# Malabard : Righteous allongée (parties verticales +540) puis graisse par offset anisotrope + élargissement
import sys, json, os
sys.path.insert(0, '.')
from stretchlib import *
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.areaPen import AreaPen

src, out, T, S = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
STEM = 287.0
GY = (T - STEM) / 2            # traits horizontaux
GX = (T / S - STEM) / 2        # traits verticaux avant élargissement S

def P(cs): return to_path(cs)
def area(p):
    a = AreaPen(); p.draw(a); return abs(a.value)
def ncont(p):
    rp = RecordingPen(); p.draw(rp); return sum(1 for op, _ in rp.value if op in ('closePath', 'endPath'))
def grow(p, gx, gy):
    if abs(gx) < 0.01 and abs(gy) < 0.01: return pathops.Path(p)
    r = max(abs(gx), abs(gy)); sx, sy = r / max(abs(gx), 0.01), r / max(abs(gy), 0.01)
    q = pathops.Path(); p.draw(TransformPen(q.getPen(), (sx, 0, 0, sy, 0, 0))); q.simplify(fix_winding=True)
    st = pathops.Path(q); st.stroke(2 * r, pathops.LineCap.BUTT_CAP, pathops.LineJoin.MITER_JOIN, 4)
    st.convertConicsToQuads()
    q = pathops.op(q, st, pathops.PathOp.UNION if gx > 0 else pathops.PathOp.DIFFERENCE, fix_winding=True, keep_starting_points=False)
    o = pathops.Path(); q.draw(TransformPen(o.getPen(), (1 / sx, 0, 0, 1 / sy, 0, 0))); return o
def offset_safe(p, gx, gy):
    neg = gx <= 0 and gy <= 0
    cands = []
    for k in (1, 2, 3, 4):
        try:
            q = pathops.Path(p)
            for _ in range(k): q = grow(q, gx / k, gy / k)
            bad = area(pathops.op(q, p, pathops.PathOp.DIFFERENCE)) > 20 if neg else area(pathops.op(p, q, pathops.PathOp.DIFFERENCE)) > 20
        except pathops.PathOpsError: continue
        if bad: continue
        cands.append(q)
        if len(cands) >= 2:
            a1, a2 = area(cands[-2]), area(cands[-1])
            if abs(a1 - a2) <= 0.03 * max(a1, a2): return cands[-2]
    return cands[-1] if cands else grow(p, gx, gy)

import numpy as np
from scipy.ndimage import distance_transform_edt
from PIL import Image, ImageDraw, ImageChops
from fontTools.pens.basePen import BasePen
class Flat(BasePen):
    def __init__(s): super().__init__(None); s.polys=[]; s.cur=[]
    def _moveTo(s,p): s.cur=[p]
    def _lineTo(s,p): s.cur.append(p)
    def _curveToOne(s,a,b,c):
        p0=s.cur[-1]
        for i in range(1,9):
            t=i/8; s.cur.append(tuple((1-t)**3*p0[k]+3*t*(1-t)**2*a[k]+3*t*t*(1-t)*b[k]+t**3*c[k] for k in (0,1)))
    def _qCurveToOne(s,a,b):
        p0=s.cur[-1]
        for i in range(1,9):
            t=i/8; s.cur.append(tuple((1-t)**2*p0[k]+2*t*(1-t)*a[k]+t*t*b[k] for k in (0,1)))
    def _closePath(s): s.polys.append(s.cur); s.cur=[]
def thickness(cs, sc=0.25):
    fp=Flat(); draw(cs, fp)
    x0,y0,x1,y1=bbox(cs); W=int((x1-x0)*sc)+6; H=int((y1-y0)*sc)+6
    acc=Image.new('1',(W,H),0)
    for poly in fp.polys:
        m=Image.new('1',(W,H),0)
        ImageDraw.Draw(m).polygon([((x-x0)*sc+3,(y1-y)*sc+3) for x,y in poly],fill=1)
        acc=ImageChops.logical_xor(acc,m)
    a=np.array(acc,dtype=bool)
    return 2*float(distance_transform_edt(a).max())/sc
# épaisseur de chaque glyphe (diamètre du plus gros cercle inscrit), mesurée sur la Medium
f0 = TTFont(src)
TH = {}
cache = 'thickness.json'
if os.path.exists(cache): TH = json.load(open(cache))
order = f0.getGlyphOrder()
med = {}
for gn in order:
    g = f0['glyf'][gn]
    if g.numberOfContours <= 0: continue
    cs, typ = stretched(f0, gn, D500); med[gn] = (cs, typ)
    if gn not in TH: TH[gn] = thickness(cs)
json.dump(TH, open(cache, 'w'))
THS = TH['l']

f = TTFont(src); glyf = f['glyf']; hmtx = f['hmtx']
from fontTools.pens.pointInsidePen import PointInsidePen
def signed_area(c):
    return sum((c[i-1][0]*c[i][1]-c[i][0]*c[i-1][1]) for i in range(len(c)))/2
def split_components(cs):
    """liste de composantes = contour extérieur + ses trous"""
    if not cs: return []
    big = max(cs, key=lambda c: abs(signed_area(c))); sg = 1 if signed_area(big) > 0 else -1
    outers = [c for c in cs if signed_area(c) * sg > 0]; holes = [c for c in cs if signed_area(c) * sg <= 0]
    comps = [[o] for o in outers]
    for h in holes:
        x, y = h[0][0], h[0][1]; best = None
        for k, o in enumerate(outers):
            pp = PointInsidePen(None, (x, y)); draw([o], pp)
            if pp.getResult():
                a = abs(signed_area(o))
                if best is None or a < best[0]: best = (a, k)
        if best is not None: comps[best[1]].append(h)
    return comps
def topo(p):
    cs = from_path(p) if p.bounds != (0, 0, 0, 0) else []
    comps = split_components(cs); return (len(comps), sum(len(c) - 1 for c in comps))
def fill_new_holes(q, t0, orig=None):
    cs = from_path(q); comps = split_components(cs)
    if len(comps) != t0[0]: return None
    oh = [h for c in split_components(from_path(orig)) for h in c[1:]] if orig is not None else []
    keep = []; removed = 0
    for c in comps:
        kc = [c[0]]
        for h in c[1:]:
            new = True
            for o in oh:
                try:
                    if area(pathops.op(P([h]), P([o]), pathops.PathOp.INTERSECTION, fix_winding=True)) > 1: new = False; break
                except pathops.PathOpsError: new = False
            if new and abs(signed_area(h)) < 0.08 * abs(signed_area(c[0])): removed += 1
            else: kc.append(h)
        keep.append(kc)
    if removed == 0: return None
    if sum(len(c) - 1 for c in keep) != t0[1]: return None
    return P([ct for c in keep for ct in c])
def opening(p, r):
    try: return grow(grow(p, -r, -r), r, r)
    except pathops.PathOpsError: return pathops.Path()
def union2(a, b):
    if a.bounds == (0, 0, 0, 0): return b
    if b.bounds == (0, 0, 0, 0): return a
    return pathops.op(a, b, pathops.PathOp.UNION, fix_winding=True, keep_starting_points=False)
def keep_white(p, q, k):
    """garde ouverts les blancs d'origine (amincis de k de chaque côté)"""
    x0, y0, x1, y1 = p.bounds; r = pathops.Path(); pen = r.getPen()
    pen.moveTo((x0 - 400, y0 - 400)); pen.lineTo((x1 + 400, y0 - 400)); pen.lineTo((x1 + 400, y1 + 400)); pen.lineTo((x0 - 400, y1 + 400)); pen.closePath()
    white = pathops.op(r, p, pathops.PathOp.DIFFERENCE, fix_winding=True, keep_starting_points=False)
    return pathops.op(q, grow(white, -k, -k), pathops.PathOp.DIFFERENCE, fix_winding=True, keep_starting_points=False)
KEEP_WHITE = {'at'}
def offset_comp(c, fac0, gname=''):
    """offset d'une composante ; rattrape les cassures (amincir) ou réduit l'effet (trou bouché)"""
    p = P(c); t0 = topo(p); fac = fac0
    if gname in KEEP_WHITE and GY > 0:
        q = keep_white(p, offset_safe(p, GX * fac, GY * fac), 20)
        if topo(q)[0] == t0[0]: return q, fac, 'blancs gardés'
    q = offset_safe(p, GX * fac, GY * fac) if abs(GX * fac) > 0.3 or abs(GY * fac) > 0.3 else p
    if topo(q) == t0: return q, fac, ''
    if GY > 0:
        q2 = fill_new_holes(q, t0, p)
        if q2 is not None: return q2, fac, 'bouché'
    if GY < 0 and topo(q)[0] > t0[0]:
        # cassure : on recolle avec un morceau de la version moins amincie, pris autour de la cassure
        for lf in (0.6, 0.45, 0.3):
            ql = offset_safe(p, GX * fac * lf, GY * fac * lf)
            if topo(ql) != t0: continue
            qq = pathops.Path(q)
            for _ in range(4):
                pieces = [P(c) for c in split_components(from_path(qq))]
                if len(pieces) <= t0[0]: break
                pieces.sort(key=lambda z: -area(z))
                A = pieces[0]
                for B in pieces[1:]:
                    m, d = nearest(A, B)
                    R = d / 2 + (STEM + 2 * GY * fac) * 0.35
                    import math
                    disc = pathops.Path(); pen = disc.getPen(); cx, cy = m
                    pts = [(cx + R * math.cos(2 * math.pi * t / 32), cy + R * math.sin(2 * math.pi * t / 32)) for t in range(32)]
                    pen.moveTo(pts[0])
                    for pt in pts[1:]: pen.lineTo(pt)
                    pen.closePath()
                    patch = pathops.op(disc, ql, pathops.PathOp.INTERSECTION, fix_winding=True, keep_starting_points=False)
                    qq = union2(qq, patch)
            if topo(qq) == t0: return qq, fac, 'rattrapé'
    while fac > 0.25:
        fac *= 0.85
        q = offset_safe(p, GX * fac, GY * fac)
        if topo(q) == t0: return q, fac, 'réduit'
        if GY > 0:
            q2 = fill_new_holes(q, t0, p)
            if q2 is not None: return q2, fac, 'réduit+bouché'
    return q, fac, 'échec'
def raster(p, x0, y1, W, H, sc):
    fp = Flat(); p.draw(fp); acc = Image.new('1', (W, H), 0)
    for poly in fp.polys:
        m = Image.new('1', (W, H), 0); ImageDraw.Draw(m).polygon([((x - x0) * sc, (y1 - y) * sc) for x, y in poly], fill=1); acc = ImageChops.logical_xor(acc, m)
    return np.array(acc, dtype=bool)
def dist(a, b, sc=0.2):
    ba, bb = a.bounds, b.bounds
    x0 = min(ba[0], bb[0]) - 50; y0 = min(ba[1], bb[1]) - 50; x1 = max(ba[2], bb[2]) + 50; y1 = max(ba[3], bb[3]) + 50
    W = int((x1 - x0) * sc) + 2; H = int((y1 - y0) * sc) + 2
    A = raster(a, x0, y1, W, H, sc); B = raster(b, x0, y1, W, H, sc)
    if (A & B).any(): return -1.0
    return float(distance_transform_edt(~A)[B].min()) / sc
def nearest(a, b, sc=0.2):
    ba, bb = a.bounds, b.bounds
    x0 = min(ba[0], bb[0]) - 50; y0 = min(ba[1], bb[1]) - 50; x1 = max(ba[2], bb[2]) + 50; y1 = max(ba[3], bb[3]) + 50
    W = int((x1 - x0) * sc) + 2; H = int((y1 - y0) * sc) + 2
    A = raster(a, x0, y1, W, H, sc); B = raster(b, x0, y1, W, H, sc)
    dt, ind = distance_transform_edt(~A, return_indices=True)
    dB = np.where(B, dt, np.inf); r, c = np.unravel_index(np.argmin(dB), dB.shape)
    ra, ca = ind[0][r, c], ind[1][r, c]
    mx = ((c + ca) / 2) / sc + x0; my = y1 - ((r + ra) / 2) / sc
    return (mx, my), float(dB[r, c]) / sc
def trim_bottom(p, y):
    r = pathops.Path(); pen = r.getPen()
    pen.moveTo((-3000, y)); pen.lineTo((6000, y)); pen.lineTo((6000, 6000)); pen.lineTo((-3000, 6000)); pen.closePath()
    return pathops.op(p, r, pathops.PathOp.INTERSECTION, fix_winding=True, keep_starting_points=False)
def move(p, dx, dy):
    q = pathops.Path(); p.draw(TransformPen(q.getPen(), (1, 0, 0, 1, dx, dy))); return q
MINGAP = 0.45
report = []; gxs = {}
for gn in order:
    g = glyf[gn]; w, lsb = hmtx[gn]
    if g.numberOfContours == 0:
        if not g.isComposite(): hmtx[gn] = (int(round(w * S)), 0)
        continue
    if g.isComposite(): continue
    _, typ = med[gn]
    fac_g = min(1.0, TH[gn] / THS)
    gy_g = GY * fac_g; gx_g = GX * fac_g
    if typ == 'diag':
        cs0 = contours_of(f0, gn); h = kind(f0, gn, cs0)[1]
        q0 = pathops.Path(); notes = []
        for c in split_components(cs0):
            qq, fr, note = offset_comp(c, fac_g); q0 = union2(q0, qq)
            if note: notes.append(note + ' %.2f' % fr)
        cs1 = from_path(q0); bd = band_of(cs1, h + 2 * gy_g)
        if bd is None:
            a_, b_ = band_of(cs0, h); bd = (a_ - gy_g, b_ + gy_g)
            notes.append('bande d’origine')
        q = P(band_stretch(cs1, D500 - 2 * gy_g, bd)); dy = gy_g
        if notes: report.append((gn, notes))
        gxs[gn] = gx_g
        pen = TTGlyphPen(None)
        q.draw(TransformPen(Cu2QuPen(pen, 1.0, reverse_direction=False), (S, 0, 0, 1, gx_g * S, dy)))
        glyf[gn] = pen.glyph(); hmtx[gn] = (int(round((w + 2 * gx_g) * S)), 0)
        continue
    if typ == 'cut': cs, _ = stretched(f0, gn, D500 - 2 * gy_g); dy = gy_g
    else:
        cs, _ = stretched(f0, gn, D500); dy = gy_g if typ == 'base' else 0
        if typ == 'center' and bbox(cs)[1] > 0.8 * (XH + D500): dy = gy_g     # signes en l'air (accents…) : le bas ne bouge pas
        if typ == 'base' and bbox(cs)[3] < 30: dy = -gy_g                      # virgule sous la lettre : le haut ne bouge pas
    comps = split_components(cs)
    outs = []; notes = []
    for c in comps:
        fc = min(1.0, thickness(c) / THS) if len(comps) > 1 else fac_g
        q, fr, note = offset_comp(c, fc, gn)
        outs.append([P(c), q, fr])
        if note: notes.append(note + ' %.2f' % fr)
    def ub(lst):
        bs = [o[1].bounds for o in lst if o[1].bounds != (0, 0, 0, 0)]
        return min(x[0] for x in bs), max(x[2] for x in bs)
    before = ub(outs)
    # écarts entre composantes : on garde au moins MINGAP de l'écart d'origine
    if len(outs) > 1 and abs(GY) > 0.3 and GY > 0:
        for _ in range(3):
            changed = False
            for i in range(len(outs)):
                for j in range(i + 1, len(outs)):
                    a0, a, _fa = outs[i]; b0, b, _fb = outs[j]
                    d0 = dist(a0, b0)
                    if d0 <= 0: continue
                    target = MINGAP * d0
                    if dist(a, b) >= target - 2: continue
                    ba, bb = a0.bounds, b0.bounds
                    # option horizontale : écarter les deux de part et d'autre
                    l, r = (i, j) if (ba[0] + ba[2]) < (bb[0] + bb[2]) else (j, i)
                    def okh(t): return dist(move(outs[l][1], -t / 2, 0), move(outs[r][1], t / 2, 0)) >= target - 2
                    # option verticale : petit élément au-dessus -> monte ; point posé sur la ligne de base -> on raccourcit le corps
                    up, lo_ = (j, i) if (bb[1] + bb[3]) > (ba[1] + ba[3]) else (i, j)
                    small_up = area(outs[up][0]) <= area(outs[lo_][0])
                    def okv(t):
                        if small_up: return dist(move(outs[up][1], 0, t), outs[lo_][1]) >= target - 2
                        lo_b = outs[lo_][1].bounds
                        if lo_b[1] > 10: return dist(outs[up][1], move(outs[lo_][1], 0, -t)) >= target - 2
                        return dist(trim_bottom(outs[up][1], outs[lo_][1].bounds[3] + t), outs[lo_][1]) >= target - 2
                    def search(ok):
                        if not ok(400): return None
                        lo2, hi2 = 0.0, 400.0
                        for _ in range(9):
                            m = (lo2 + hi2) / 2
                            lo2, hi2 = (lo2, m) if ok(m) else (m, hi2)
                        return hi2
                    ox = min(ba[2], bb[2]) - max(ba[0], bb[0])
                    oy = min(ba[3], bb[3]) - max(ba[1], bb[1])
                    vert_ok = ox >= 0.5 * min(ba[2] - ba[0], bb[2] - bb[0]) and oy < 0
                    th = search(okh); tv = search(okv) if vert_ok else None
                    if th is not None and (tv is None or th < tv):
                        outs[l][1] = move(outs[l][1], -th / 2, 0); outs[r][1] = move(outs[r][1], th / 2, 0); notes.append('écarté %d' % th)
                    elif tv is not None:
                        if small_up: outs[up][1] = move(outs[up][1], 0, tv); notes.append('monté %d' % tv)
                        elif outs[lo_][1].bounds[1] > 10: outs[lo_][1] = move(outs[lo_][1], 0, -tv); notes.append('descendu %d' % tv)
                        else: outs[up][1] = trim_bottom(outs[up][1], outs[lo_][1].bounds[3] + tv); notes.append('raccourci %d' % tv)
                    else:
                        sm = i if area(outs[i][0]) < area(outs[j][0]) else j; ot = j if sm == i else i
                        fr = outs[sm][2]
                        while fr > 0.15 and dist(outs[sm][1], outs[ot][1]) < target - 2:
                            fr *= 0.85; outs[sm][1] = offset_safe(outs[sm][0], GX * fr, GY * fr)
                        outs[sm][2] = fr; notes.append('allégé %.2f' % fr)
                    changed = True
            if not changed: break
    after = ub(outs); extra_w = 0.0
    if after != before:
        sh = before[0] - after[0]
        for o in outs: o[1] = move(o[1], sh, 0)
        extra_w = (after[1] - after[0]) - (before[1] - before[0])
    q = pathops.Path()
    for o in outs: q = union2(q, o[1])
    if notes: report.append((gn, notes))
    gxs[gn] = gx_g
    pen = TTGlyphPen(None)
    q.draw(TransformPen(Cu2QuPen(pen, 1.0, reverse_direction=False), (S, 0, 0, 1, gx_g * S, dy)))
    glyf[gn] = pen.glyph()
    hmtx[gn] = (int(round((w + 2 * gx_g + extra_w) * S)), 0)
# composites : accents recentrés, lettres côte à côte (ĳ, Ĳ, ŉ) décalées, écarts accent/lettre gardés
import unicodedata
rev = {}
for u, gname in f0.getBestCmap().items(): rev.setdefault(gname, u)
def is_letter(gname):
    u = rev.get(gname); return u is not None and unicodedata.category(chr(u)) in ('Lu', 'Ll', 'Lt', 'Lo')
def outline(font_or_none, gname, dx, dy, medium=False):
    if medium: cs = med[gname][0] if gname in med else []
    else:
        gs = f.getGlyphSet(); rp = RecordingPen(); gs[gname].draw(rp); cs = parse(rp.value)
    return move(P(cs), dx, dy) if cs else pathops.Path()
cfix = []
for gn in order:
    g = glyf[gn]
    if not g.isComposite(): continue
    comps = g.components; base = comps[0].glyphName; gb = gxs.get(base, GX)
    w, lsb = hmtx[gn]; extra = 2 * gb
    orig = [(c.glyphName, c.x, c.y) for c in comps]
    for k, c in enumerate(comps):
        if k == 0: c.x = int(round(c.x * S)); continue
        ga = gxs.get(c.glyphName, GX)
        if is_letter(c.glyphName):
            c.x = int(round((c.x + 2 * gb) * S)); extra += 2 * ga
        else:
            c.x = int(round(c.x * S + (gb - ga) * S))
    hmtx[gn] = (int(round((w + extra) * S)), 0)
    if abs(GY) < 0.3: continue
    # écart accent / lettre
    for k, c in enumerate(comps[1:], 1):
        letter = is_letter(c.glyphName)
        A0 = outline(None, base, orig[0][1], orig[0][2], True); B0 = outline(None, c.glyphName, orig[k][1], orig[k][2], True)
        if A0.bounds == (0, 0, 0, 0) or B0.bounds == (0, 0, 0, 0): continue
        d0 = dist(A0, B0)
        if d0 <= 0: continue
        A = outline(None, base, comps[0].x, comps[0].y); B = outline(None, c.glyphName, c.x, c.y)
        target = MINGAP * d0
        if dist(A, B) >= target - 2: continue
        up = (B.bounds[1] + B.bounds[3]) > (A.bounds[1] + A.bounds[3]); right = (B.bounds[0] + B.bounds[2]) > (A.bounds[0] + A.bounds[2])
        def okv(t): return dist(A, move(B, 0, t if up else -t)) >= target - 2
        def okh(t): return dist(A, move(B, t if right else -t, 0)) >= target - 2
        def search(ok):
            if not ok(400): return None
            lo2, hi2 = 0.0, 400.0
            for _ in range(9):
                m = (lo2 + hi2) / 2
                lo2, hi2 = (lo2, m) if ok(m) else (m, hi2)
            return hi2
        tv = None if letter else search(okv); th = search(okh)
        if tv is not None and (th is None or tv <= th): c.y += int(round(tv if up else -tv)); cfix.append((gn, 'v', round(tv)))
        elif th is not None:
            c.x += int(round(th if right else -th)); cfix.append((gn, 'h', round(th)))
            if right and letter: hmtx[gn] = (int(round(hmtx[gn][0] + th)), 0)
            elif right:
                rsb = hmtx[base][0] - A.bounds[2]; newR = B.bounds[2] + th
                if newR + rsb > hmtx[gn][0]: hmtx[gn] = (int(round(newR + rsb)), 0)
        else: cfix.append((gn, 'non résolu'))
if cfix: print('composites ajustés :', cfix)
# crénage
if 'kern' in f:
    for st in f['kern'].kernTables:
        st.kernTable = {k: int(round(v * S)) for k, v in st.kernTable.items()}
d = D500
f['hhea'].ascent = 2017 + d; f['OS/2'].sTypoAscender = f0['OS/2'].sTypoAscender + d; f['OS/2'].usWinAscent = f0['OS/2'].usWinAscent + d
f['OS/2'].sxHeight = XH + d; f['OS/2'].sCapHeight = CAP + d
if 'VDMX' in f: del f['VDMX']
f.save(out)
print(out, 'GX %.1f GY %.1f S %.2f' % (GX, GY, S))
for r in report: print('  ', r)
