# Allongement « seulement les parties verticales » de Righteous, glyphe par glyphe
import sys, unicodedata
sys.path.insert(0, '.')
from plan import *
import pathops
from fontTools.pens.recordingPen import RecordingPen
XH = 1077; CAP = 1434; D500 = 540

def bbox(cs):
    xs = [p[0] for c in cs for p in c]; ys = [p[1] for c in cs for p in c]
    return min(xs), min(ys), max(xs), max(ys)
def to_path(cs):
    p = pathops.Path(); draw(cs, p.getPen()); return p
def from_path(p):
    rp = RecordingPen(); p.draw(rp); return parse(rp.value)
def clip(cs, x0, x1):
    r = pathops.Path(); pen = r.getPen()
    pen.moveTo((x0, -3000)); pen.lineTo((x1, -3000)); pen.lineTo((x1, 5000)); pen.lineTo((x0, 5000)); pen.closePath()
    return from_path(pathops.op(to_path(cs), r, pathops.PathOp.INTERSECTION))
def tr(cs, dx, dy): return [[(p[0] + dx, p[1] + dy, p[2]) for p in c] for c in cs]
def shift_at(cuts, y, d): return sum(d for c in cuts if min(c) < y)

def split_plan(cs, h, D):
    x0, y0, x1, y1 = bbox(cs); best = None
    for s in range(int(x0) + 40, int(x1) - 40, 8):
        L = clip(cs, x0 - 10, s); R = clip(cs, s, x1 + 10)
        if not L or not R: continue
        pl = plan(L, h); pr = plan(R, h)
        if pl is None or pr is None: continue
        dl = D / len(pl); dr = D / len(pr)
        ys = xs_at([[(p[1], p[0], p[2]) for p in c] for c in cs], s)
        if all(abs(shift_at(pl, y, dl) - shift_at(pr, y, dr)) < 0.5 for y in ys):
            sc = sum(abs(sum(c) / len(c) - 0.5 * h) for c in pl + pr) / len(pl + pr)
            if best is None or sc < best[0]: best = (sc, (L, pl, R, pr))
    return best and best[1]

NO_BAND = {'exclam', 'exclamdown', 'onehalf', 'onequarter'}
SPECIAL = {'Eth': 'D'}   # lettre = base + barre : on allonge la base, la barre monte au milieu

def kind(f0, gn, cs):
    rev = {}
    for u, g in f0.getBestCmap().items(): rev.setdefault(g, u)
    u = rev.get(gn); cat = unicodedata.category(chr(u)) if u else ''
    x0, y0, x1, y1 = bbox(cs)
    if gn == '.notdef': return ('cut', CAP)
    if cat in ('Ll', 'Lo'): return ('cut', XH)
    if cat in ('Pi', 'Pf'): return ('shiftc',)
    if cat == 'Sc' and y1 - y0 < 0.7 * XH: return ('shiftc',)
    if cat in ('Lu', 'Lt', 'Nd', 'Sc'): return ('cut', CAP)
    if cat == 'Sm': return ('cut', CAP) if y1 - y0 >= 1.2 * XH else ('shiftc',)
    if y1 - y0 >= 0.7 * XH and y0 < 0.35 * XH and y1 > 0.65 * XH:
        return ('cut', CAP if y1 > 1.15 * XH else XH)
    return ('shift',)

def stretched(f0, gn, D):
    """renvoie (contours, type) ; les signes « shift » montent de D500*cy/XH (position de la Medium)"""
    cs = contours_of(f0, gn); k = kind(f0, gn, cs)
    if gn in SPECIAL:
        bs = contours_of(f0, SPECIAL[gn]); dx = bbox(cs)[2] - bbox(bs)[2]; bs = tr(bs, dx, 0)
        extra = from_path(pathops.op(to_path(cs), to_path(bs), pathops.PathOp.DIFFERENCE))
        ex = bbox(extra); s = D * min(max(((ex[1] + ex[3]) / 2) / CAP, 0), 1)
        new = from_path(pathops.op(to_path(stretch_glyph(bs, plan(bs, CAP), D)), to_path(tr(extra, 0, s)), pathops.PathOp.UNION))
        return new, 'cut'
    if k[0] == 'cut' and gn not in NO_BAND:
        bd = band_of(cs, k[1])
        if bd is not None: return band_stretch(cs, D, bd), 'diag'
    if k[0] == 'cut':
        p = plan(cs, k[1])
        if p is not None: return stretch_glyph(cs, p, D), 'cut'
        sp = split_plan(cs, k[1], D)
        if sp is None: raise Exception('pas de plan pour ' + gn)
        L, pl, R, pr = sp
        a = to_path(stretch_glyph(L, pl, D)); b = to_path(stretch_glyph(R, pr, D))
        return from_path(pathops.op(a, b, pathops.PathOp.UNION)), 'cut'
    x0, y0, x1, y1 = bbox(cs); cy = (y0 + y1) / 2
    s = 0 if (y0 <= 30 and k[0] == 'shift') else D500 * min(max(cy / XH, 0), 1)
    return tr(cs, 0, s), ('base' if (y0 <= 30 and k[0] == 'shift') else 'center')

# --- lettres à diagonales droites : étirement affine dans une bande (les diagonales restent parallèles)
def segs_all(cs):
    out = []
    for c in cs: out += segments(c)
    return out
def band_of(cs, h):
    segs = segs_all(cs)
    x0, y0, x1, y1 = bbox(cs)
    levels = {round(y0, 1), round(y1, 1)}
    for s in segs:
        if s[0] == 'L' and abs(s[1][1] - s[2][1]) < 0.5 and abs(s[1][0] - s[2][0]) > 0.5: levels.add(round(s[1][1], 1))
    levels = sorted(levels); best = None
    for a, b in zip(levels, levels[1:]):
        if b - a < 0.25 * h: continue
        if a > 0.6 * h or b < 0.4 * h: continue          # la bande doit couvrir le milieu de la zone
        curvy = False; diag = False
        for s in segs:
            ys = [p[1] for p in s[1:]]
            if max(ys) <= a + 0.5 or min(ys) >= b - 0.5: continue
            if s[0] == 'Q': curvy = True; break
            if abs(s[1][0] - s[2][0]) > 2 and abs(s[1][1] - s[2][1]) > 2: diag = True
        if curvy or not diag: continue
        if best is None or b - a > best[1] - best[0]: best = (a, b)
    return best
def band_stretch(cs, D, band):
    a, b = band
    def m(y): return y + D * min(max((y - a) / (b - a), 0), 1)
    return [[(p[0], m(p[1]), p[2]) for p in c] for c in cs]
