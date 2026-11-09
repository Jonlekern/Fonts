# Serif de lecture : squelette de plume vintage (axes penchés, têtes en biais à gauche, lettres asymétriques)
# + peau du futur (contraste faible, empattements en coin coupés net). Pensée pour lire avec une dyslexie :
# aucune lettre n'est le miroir d'une autre, contreformes ouvertes et constantes, espacement large.
# Chaque graisse est fabriquée dans son propre processus : la graisse est lue dans l'environnement (W) à l'import.
import math, os
import pathops
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.recordingPen import RecordingPen

FAMILY = 'ANISOTROPE'
PSFAM = 'ANISOTROPE'
SLUG = 'anisotrope'
UPM = 1000
XH, CAP, ASC, DESC = 500, 700, 750, -230
OV = 10

# graisses : (usWeightClass, nom provisoire, épaisseur du fût)
WEIGHTS = [(300, '030', 60), (400, '040', 84), (500, '050', 106), (700, '070', 136), (900, '090', 172)]
ST = int(os.environ.get('W', '84'))          # fût vertical
TH = round(0.68 * ST + 2)                    # partie fine (contraste faible)
W = round(26 + 0.24 * ST)                    # avancée d'un empattement
SH = round(34 + 0.31 * ST)                   # hauteur d'un empattement en coin
NW = round(290 + 1.55 * ST)                  # largeur d'un n : la contreforme se serre un peu en gras, sans fondre
BR = round(165 + 0.85 * ST)                  # demi-largeur d'un o
S_STEM = 72 + ST / 6                         # approche d'un fût nu
ROT = 14                                     # axe penché des ronds (plume)
K_ = 0.5523

# ---------- géométrie ----------
def P(): return pathops.Path()

def poly(pts):
    p = P(); pen = p.getPen(); pen.moveTo(pts[0])
    for q in pts[1:]: pen.lineTo(q)
    pen.closePath(); return p

def rect(x0, y0, x1, y1): return poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])

def ellipse(cx, cy, rx, ry, rot=0.0):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    T = lambda x, y: (cx + x * c - y * s, cy + x * s + y * c)
    p = P(); pen = p.getPen(); pen.moveTo(T(rx, 0))
    pen.curveTo(T(rx, K_ * ry), T(K_ * rx, ry), T(0, ry))
    pen.curveTo(T(-K_ * rx, ry), T(-rx, K_ * ry), T(-rx, 0))
    pen.curveTo(T(-rx, -K_ * ry), T(-K_ * rx, -ry), T(0, -ry))
    pen.curveTo(T(K_ * rx, -ry), T(rx, -K_ * ry), T(rx, 0))
    pen.closePath(); return p

def U(*ps):
    out = P()
    for p in ps:
        if p is not None: out = pathops.op(out, p, pathops.PathOp.UNION)
    return out
def D(a, *bs):
    for b in bs: a = pathops.op(a, b, pathops.PathOp.DIFFERENCE)
    return a
def I(a, b): return pathops.op(a, b, pathops.PathOp.INTERSECTION)

def xf(p, m):
    out = P(); p.draw(TransformPen(out.getPen(), m)); return out
def mv(p, dx, dy=0): return xf(p, (1, 0, 0, 1, dx, dy))
def flipx(p, ax):  return xf(p, (-1, 0, 0, 1, 2 * ax, 0))
def flipy(p, ay):  return xf(p, (1, 0, 0, -1, 0, 2 * ay))
def rot(p, deg, cx, cy):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return xf(p, (c, s, -s, c, cx - c * cx + s * cy, cy - s * cx - c * cy))

def pie(cx, cy, a0, a1, R=3000):
    """part de tarte de a0 à a1 degrés (sens direct)"""
    if a1 < a0: a1 += 360
    n = max(2, int((a1 - a0) / 10) + 1)
    pts = [(cx, cy)] + [(cx + R * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
                         cy + R * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
    return poly(pts)

def bar(x0, y0, x1, y1, t):
    """trait droit d'épaisseur t (mesurée à l'horizontale) entre deux points"""
    return poly([(x0 - t / 2, y0), (x0 + t / 2, y0), (x1 + t / 2, y1), (x1 - t / 2, y1)])

# ---------- pièces ----------
def stem(x, y0, y1, w=None): return rect(x, y0, x + (w or ST), y1)

def ring(cx, cy, rx, ry, sx=None, sy=None, r=ROT, dx=0, dy=0):
    """rond de plume : l'axe penche (vintage), contraste faible (futur)"""
    sx = ST * 0.98 if sx is None else sx; sy = TH if sy is None else sy
    return D(ellipse(cx, cy, rx, ry), ellipse(cx + dx, cy + dy, rx - sx, ry - sy, r))

def bowl(cx):
    """bol d'un o, b, d, p, q"""
    return ring(cx, XH / 2, BR, XH / 2 + OV)

def arch(x0, x1, top, h=None):
    """arche du n : rejoint le fût de droite à pleine épaisseur, naît en encoche du fût de gauche"""
    h = h or round(0.46 * XH)
    cx = (x0 + x1) / 2; rx = (x1 - x0) / 2
    a = D(ellipse(cx, top - h, rx, h + OV), ellipse(cx, top - h, rx - ST, h + OV - TH))
    return I(a, rect(x0 + ST * 0.5, top - h - 2, x1 + 5, top + OV + 5))

def cup(x0, x1, bot=0, h=None):
    """bas du u (une arche à l'envers)"""
    h = h or round(0.46 * XH)
    cx = (x0 + x1) / 2; rx = (x1 - x0) / 2
    a = D(ellipse(cx, bot + h, rx, h + OV), ellipse(cx, bot + h, rx - ST, h + OV - TH))
    return I(a, rect(x0 - 5, bot - OV - 5, x1 + 5, bot + h + 2))      # la cuvette garde tout son mur droit : il se confond avec le fût

def foot(x0, x1, left=True, right=True, y=0):
    """empattement en coin : large en bas, coupé net, rejoint le fût en biais"""
    l = W if left else 0; r = W if right else 0; e = max(10, round(SH * 0.2))
    return poly([(x0 - l, y), (x1 + r, y), (x1 + r, y + e), (x1, y + SH), (x0, y + SH), (x0 - l, y + e)])

def cap_foot(x0, x1, left=True, right=True, y=0, top=False):
    """empattement des capitales (et dessus des barres) : même coin, retournable"""
    p = foot(x0, x1, left, right, 0)
    if top: p = flipy(p, 0)
    return mv(p, 0, y)

def head(x0, x1, top):
    """tête de plume : coin en biais vers la gauche (vintage), arêtes nettes (futur)"""
    a = round(W * 0.95); d = round(SH * 1.6)
    return poly([(x0 - a - 10, top - round(SH * 0.73)), (x0 + 6, top + 8), (x1, top + 16),
                 (x1, top - d + 10), (x0, top - d), (x0 - a - 10, top - round(SH * 1.1))])

def kick(x0, x1, y=0):
    """départ vers la droite au pied (d, u, a) : la lettre avance"""
    return poly([(x0, y + round(SH * 1.15)), (x0, y), (x1 + W, y), (x1 + W, y + max(10, round(SH * 0.2))), (x1, y + SH)])

def spur(x0, x1, y=0):
    """éperon à gauche sous le fût (b) : pointe vers le bas"""
    return poly([(x0, y + round(SH * 1.35)), (x0 - round(W * 0.6), y - 8), (x1, y), (x1, y + 30)])

def ear(x0, y):
    """oreille en haut à droite (q, g) : coupe nette qui monte"""
    return poly([(x0, y - 24), (x0 + ST + round(W * 0.8), y + 24), (x0 + ST + round(W * 0.65), y - 6),
                 (x0 + ST, y - 60), (x0, y - 60)])

def dot(cx, cy, r=None):
    r = r or round(ST * 0.62 + 4)
    return ellipse(cx, cy, r, r)

def hook_r(x0, y, h, reach):
    """crochet en bas à droite (l, t) : finit coupé net"""
    o = ellipse(x0 + ST + reach, y + h, reach + ST, h + OV)
    i = ellipse(x0 + ST + reach, y + h + 4, reach, h + OV - TH)
    return I(D(o, i), rect(x0, y - OV - 5, x0 + ST + reach, y + h))

# ---------- registre ----------
GLYPHS = {}; UNI = {}
def reg(name, ch=None):
    def deco(f):
        GLYPHS[name] = f
        if ch: UNI[name] = ch
        return f
    return deco

def side(k):
    """approche selon le bord : S fût à empattement, P fût nu, O rond, D diagonale, K coup de pied, ou un nombre"""
    if isinstance(k, (int, float)): return k
    return {'S': S_STEM - W, 'P': S_STEM, 'O': S_STEM * 0.62, 'D': S_STEM * 0.28,
            'K': S_STEM - W * 0.7, 'T': S_STEM * 0.45}[k]

def out(p, l='S', r='S'): return p, round(side(l)), round(side(r))

# ---------- fabrication ----------
VERSION = '1.000'
WIN_ASC, WIN_DESC = 1060, 360          # les mêmes pour toute la famille (la 090 monte à 1047)
def build(outf, style, weight, glyphs, cmap_names, fea=None):
    from fontTools.pens.t2CharStringPen import T2CharStringPen
    from fontTools.pens.boundsPen import BoundsPen
    order = ['.notdef', 'space'] + [g[0] for g in glyphs if g[0] not in ('.notdef', 'space')]
    cs = {}; hmtx = {}
    nd = T2CharStringPen(500, None); D(rect(50, 0, 450, CAP), rect(50 + TH, TH, 450 - TH, CAP - TH)).draw(nd)
    cs['.notdef'] = nd.getCharString(); hmtx['.notdef'] = (500, 50)
    sp = round(250 + 0.4 * ST); cs['space'] = T2CharStringPen(sp, None).getCharString(); hmtx['space'] = (sp, 0)
    for name, path, lsb, rsb in glyphs:
        if name in ('.notdef', 'space'): continue
        if path is None or path.bounds is None or path.bounds == (0, 0, 0, 0):
            cs[name] = T2CharStringPen(sp, None).getCharString(); hmtx[name] = (sp, 0); continue
        b = path.bounds
        adv = round(lsb + (b[2] - b[0]) + rsb); dx = lsb - b[0]
        if name.startswith('uni03'): adv = 0; dx = 0
        pen = T2CharStringPen(adv, None)
        path.draw(TransformPen(pen, (1, 0, 0, 1, round(dx), 0)))
        cs[name] = pen.getCharString(); hmtx[name] = (adv, round(b[0] + round(dx)))
    fb = FontBuilder(UPM, isTTF=False)
    fb.setupGlyphOrder(order)
    cmap = {ord(' '): 'space'}
    for n, ch in cmap_names.items():
        if n in cs: cmap[ord(ch)] = n
    fb.setupCharacterMap(cmap)
    psn = f'{PSFAM}-{style}'; full = f'{FAMILY} {style}'
    cr = '© 2026 LaFleurStudio. All rights reserved.'
    fb.setupCFF(psn, {'FullName': full, 'FamilyName': full, 'Weight': style, 'Copyright': '(c) 2026 LaFleurStudio. All rights reserved.',
                      'Notice': f'{FAMILY} by LaFleurStudio.'}, cs, {})
    fb.setupHorizontalMetrics(hmtx)
    fb.setupHorizontalHeader(ascent=950, descent=-300)
    lic = ('Free for personal use. Commercial use requires prior written permission from LaFleurStudio '
           '(free or paid, decided case by case): info@lafleurstudio.ch. Usage personnel gratuit ; usage commercial '
           'sur autorisation écrite de LaFleurStudio.')
    fb.setupNameTable({'copyright': cr, 'familyName': full, 'styleName': 'Regular',
        'uniqueFontIdentifier': f'{VERSION};LFST;{psn}', 'fullName': full, 'version': f'Version {VERSION}', 'psName': psn,
        'manufacturer': 'LaFleurStudio', 'designer': 'Jonathan Kern', 'vendorURL': 'https://jonlekern.github.io/Fonts/',
        'licenseDescription': lic, 'licenseInfoURL': f'https://github.com/Jonlekern/Fonts/blob/main/{SLUG}/LICENCE.txt',
        'typographicFamily': FAMILY, 'typographicSubfamily': style}, mac=False)
    fb.setupOS2(sTypoAscender=950, sTypoDescender=-300, sTypoLineGap=0, usWinAscent=WIN_ASC, usWinDescent=WIN_DESC,
                sCapHeight=CAP, usWeightClass=weight, sxHeight=XH, version=4, achVendID='LFST', fsSelection=0x40 | 0x80)
    fb.setupPost()
    if fea:
        from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
        addOpenTypeFeaturesFromString(fb.font, fea)
    gs = fb.font.getGlyphSet(); ys = []
    for n_ in fb.font.getGlyphOrder():
        bp = BoundsPen(gs); gs[n_].draw(bp)
        if bp.bounds: ys += [bp.bounds[1], bp.bounds[3]]
    assert max(ys) <= WIN_ASC and -min(ys) <= WIN_DESC, ('hors des métriques win', max(ys), min(ys))
    from fontTools.ttLib.tables.O_S_2f_2 import Panose
    fb.font['OS/2'].recalcUnicodeRanges(fb.font)
    cps = set(cmap)
    cpr = 0
    if 0xE9 in cps: cpr |= 1 << 0              # Latin 1
    if 0x10D in cps and 0x171 in cps: cpr |= 1 << 1   # Latin 2
    if 0x11F in cps and 0x15F in cps: cpr |= 1 << 4   # turc
    if 0x113 in cps and 0x12B in cps: cpr |= 1 << 7   # balte
    cpr |= 1 << 29                              # Mac Roman
    fb.font['OS/2'].ulCodePageRange1 = cpr; fb.font['OS/2'].ulCodePageRange2 = 0
    fb.font['head'].macStyle = 0; fb.font['head'].fontRevision = float(VERSION)
    fb.font['OS/2'].usDefaultChar = 0; fb.font['OS/2'].usBreakChar = 32
    fb.save(outf)

def clean(p, amin=60):
    """simplifie et retire les miettes (contours d'aire < amin)"""
    p = P() if p is None else p
    try:
        p.simplify(fix_winding=True, clockwise=False)
    except Exception:
        return p
    rp = RecordingPen(); p.draw(rp); out_ = P(); pen = out_.getPen(); cur = []; keep = []
    for op, a in rp.value:
        if op == 'moveTo': cur = [(op, a)]
        elif op in ('closePath', 'endPath'):
            cur.append((op, a)); keep.append(cur); cur = []
        else: cur.append((op, a))
    def area(c):
        pts = [a[-1] for op, a in c if a]
        return abs(sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts))) / 2) if len(pts) > 2 else 0
    for c in keep:
        if area(c) < amin: continue
        for op, a in c: getattr(pen, op)(*a)
    return out_
