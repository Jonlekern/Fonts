# Clebard : une graisse à partir de TeX Gyre Heros (Regular ou Bold) — usage : build_clebard.py source.otf sortie.otf largeur graisse [glyphes]
import sys, pathops
from fontTools.ttLib import TTFont
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.areaPen import AreaPen
from fontTools.pens.pointInsidePen import PointInsidePen

src, out, W, WT = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
ONLY = sys.argv[5].split(',') if len(sys.argv) > 5 else None
STEM = 150 + 19 * (WT - 700) / 100            # fût vertical visé   (400:93, 700:150)
BAR = 125 + 43 / 3 * (WT - 700) / 100         # trait horizontal visé (400:82, 700:125)
_w = TTFont(src)['OS/2'].usWeightClass
S0, B0 = (150, 125) if _w >= 700 else (93, 82)   # fût et trait de la source (Bold ou Regular)
GX = (STEM - S0 * W) / 2
GY = (BAR - B0) * 729 / (2 * (729 - BAR))
CAP = 729
K = CAP / (CAP + 2 * GY)
ZONES = [(-25, 8), (525, 565), (712, 765), (-230, -195)]   # ligne de base, x, capitales/ascendantes, descendantes
MINGAP = 0.45
import os
CLOSE = float(os.environ.get('CLOSE', '0.5'))
import os
CAPS_ON = os.environ.get("CAPS", "0") == "1"

f = TTFont(src); gs = f.getGlyphSet()
cs = f['CFF '].cff.topDictIndex[0].CharStrings

def P_from(rec):
    p = pathops.Path(); pen = p.getPen()
    for op, a in rec: getattr(pen, op)(*a)
    return p

def contours(p):
    r = RecordingPen(); p.draw(r); cs_, cur = [], []
    for op, a in r.value:
        cur.append((op, a))
        if op in ('closePath', 'endPath'): cs_.append(cur); cur = []
    return cs_

def area(rec):
    ap = AreaPen()
    for op, a in rec: getattr(ap, op)(*a)
    return ap.value

def bounds(p):
    b = p.bounds
    return None if b == (0, 0, 0, 0) else b

def grow(p, gx, gy):
    if abs(gx) < 0.01 and abs(gy) < 0.01: return pathops.Path(p)
    r = max(abs(gx), abs(gy)); sx, sy = r / max(abs(gx), 0.01), r / max(abs(gy), 0.01)
    q = pathops.Path(); p.draw(TransformPen(q.getPen(), (sx, 0, 0, sy, 0, 0))); q.simplify(fix_winding=True)
    st = pathops.Path(q); st.stroke(2 * r, pathops.LineCap.BUTT_CAP, pathops.LineJoin.MITER_JOIN, 4)
    st.convertConicsToQuads()
    q = pathops.op(q, st, pathops.PathOp.UNION if gx > 0 else pathops.PathOp.DIFFERENCE,
                   fix_winding=True, keep_starting_points=False)
    o = pathops.Path(); q.draw(TransformPen(o.getPen(), (1 / sx, 0, 0, 1 / sy, 0, 0)))
    return o

def offset(p, gx, gy):
    """épaissit (+) ou amincit (-) de gx à l'horizontale et gy à la verticale"""
    if abs(gx) < 0.3 and abs(gy) < 0.3: return pathops.Path(p)
    if gx * gy >= 0:
        sg = 1 if (gx + gy) > 0 else -1
        return grow(p, gx if abs(gx) >= 0.3 else 0.3 * sg, gy if abs(gy) >= 0.3 else 0.3 * sg)
    a = (gx - gy / 4) / (15 / 16); b = (gy - gx / 4) / (15 / 16)   # passe horizontale a, verticale b
    first, second = ((a, a / 4), (b / 4, b)) if a < 0 else ((b / 4, b), (a, a / 4))
    return grow(grow(p, *first), *second)

def _A(p):
    return abs(sum(area(c) for c in contours(p))) if bounds(p) else 0

def offset_safe(p, gx, gy):
    """offset vérifié : un calcul raté (morceau perdu ou ajouté) est refait en plusieurs passes"""
    def bad_contain(r):
        try:
            if gx <= 0 and gy <= 0: return _A(diff(r, p)) > 20          # amincir : rester dans la forme
            if gx >= 0 and gy >= 0: return _A(diff(p, r)) > 20          # épaissir : contenir la forme
        except pathops.PathOpsError: return True
        return False
    cands = []
    for k in (1, 2, 3, 4):
        try:
            r = pathops.Path(p)
            for _ in range(k): r = offset(r, gx / k, gy / k)
        except pathops.PathOpsError: continue
        if bad_contain(r): continue
        cands.append(r)
        if len(cands) >= 2:
            a1, a2 = _A(cands[-2]), _A(cands[-1])
            if abs(a1 - a2) <= 0.03 * max(a1, a2): return cands[-2]
    return cands[-1] if cands else offset(p, gx, gy)

def rect(x0, y0, x1, y1):
    p = pathops.Path(); p.moveTo(x0, y0); p.lineTo(x1, y0); p.lineTo(x1, y1); p.lineTo(x0, y1); p.close(); return p

def union(paths):
    r = pathops.Path()
    for q in paths:
        if bounds(q): r = pathops.op(r, q, pathops.PathOp.UNION, fix_winding=True, keep_starting_points=False) if bounds(r) else pathops.Path(q)
    return r

def inter(a, b):
    try: return pathops.op(a, b, pathops.PathOp.INTERSECTION, fix_winding=True, keep_starting_points=False)
    except pathops.PathOpsError: return pathops.Path()

def diff(a, b):
    return pathops.op(a, b, pathops.PathOp.DIFFERENCE, fix_winding=True, keep_starting_points=False)

def inside(p, x, y):
    pp = PointInsidePen(None, (x, y)); p.draw(pp); return pp.getResult()

def in_zone(y): return any(a <= y <= b for a, b in ZONES)

def components(p):
    cl = contours(p)
    info = [(c, area(c), bounds(P_from(c))) for c in cl]
    info = [i for i in info if abs(i[1]) > 1]
    if not info: return []
    sgn = 1 if max(info, key=lambda i: abs(i[1]))[1] > 0 else -1
    outers = [i for i in info if i[1] * sgn > 0]; holes = [i for i in info if i[1] * sgn < 0]
    comps = [[o] for o in outers]
    for h in holes:
        x, y = h[0][0][1][0]
        best = None
        for k_, o in enumerate(outers):
            if inside(P_from(o[0]), x, y) and (best is None or abs(o[1]) < abs(outers[best][1])): best = k_
        if best is not None: comps[best].append(h)
    return [P_from([seg for c in comp for seg in c[0]]) for comp in comps]

def faces(p, axis):
    """terminaisons droites horizontales (axis=1) ou verticales (axis=0) : (a0, a1, pos, côté extérieur ±1)"""
    res = []
    for c in contours(p):
        segs = []; cur = None; start = None
        for op, a in c:
            if op == 'moveTo': cur = start = a[0]
            elif op in ('lineTo', 'curveTo', 'qCurveTo'):
                pts = [cur] + list(a); segs.append(pts); cur = a[-1]
            elif op == 'closePath':
                if cur != start: segs.append([cur, start])
        n = len(segs)
        for i, sg in enumerate(segs):
            if len(sg) != 2: continue
            p0, p1 = sg
            d_par = abs(p1[1 - axis] - p0[1 - axis]); d_perp = abs(p1[axis] - p0[axis])
            if d_par < 8 or d_perp > 0.03 * d_par: continue
            pos = (p0[axis] + p1[axis]) / 2
            a0, a1 = sorted((p0[1 - axis], p1[1 - axis])); m = (a0 + a1) / 2
            pt = lambda s_: (m, pos + s_) if axis == 1 else (pos + s_, m)
            if inside(p, *pt(-2)) and not inside(p, *pt(2)): out_ = 1
            elif inside(p, *pt(2)) and not inside(p, *pt(-2)): out_ = -1
            else: continue
            prv = segs[(i - 1) % n]; nxt = segs[(i + 1) % n]
            def away(q_from, q_to):
                v = (q_to[0] - q_from[0], q_to[1] - q_from[1]); L = (v[0] ** 2 + v[1] ** 2) ** .5 or 1
                return -out_ * v[axis] / L
            # direction en quittant la face : vers l'arrière pour le précédent, vers l'avant pour le suivant
            back = prv[-2] if len(prv) > 1 else prv[0]
            fwd = nxt[1]
            if away(p0, back) > 0.6 and away(p1, fwd) > 0.6:
                res.append((a0, a1, pos, out_))
    return res

def poly(pts):
    p = pathops.Path(); p.moveTo(*pts[0])
    for q in pts[1:]: p.lineTo(*q)
    p.close(); return p

def terminal_caps(P, gx, gy):
    """ce que la croissance ajouterait au-delà des terminaisons qui regardent un autre trait.
    On le retire dans un cône à 45° partant des coins de la terminaison : pas de marche."""
    out = []
    for a0, a1, pos, s_ in faces(P, 1):
        if in_zone(pos): continue
        reach = 2 * gy + 40
        lo, hi = (pos + 0.5, pos + reach) if s_ > 0 else (pos - reach, pos - 0.5)
        if not bounds(inter(P, rect(a0 + 1, lo, a1 - 1, hi))): continue
        band = rect(a0 - gy, pos - 1.5 * gy, a1 + gy, pos) if s_ > 0 else rect(a0 - gy, pos, a1 + gy, pos + 1.5 * gy)
        pieces = components(inter(P, band))
        mx, my = (a0 + a1) / 2, pos - 2 * s_
        T = [c for c in pieces if inside(c, mx, my)]
        if not T: continue
        GT = grow(T[0], gx, gy) if gx > 0 else grow(T[0], 1, gy)
        h = gy + 2
        e = 1.3 * max(gx, 0) + 2
        cone = poly([(a0 - e, pos), (a1 + e, pos), (a1 + e + h, pos + s_ * h), (a0 - e - h, pos + s_ * h)])
        X = inter(GT, cone)
        if bounds(X): out.append(X)
    return out

def prune(g, c):
    keep = []
    for comp in components(g):
        if bounds(inter(comp, c)): keep.append(comp)
    return union(keep)

def translate(p, dx, dy):
    q = pathops.Path(); p.draw(TransformPen(q.getPen(), (1, 0, 0, 1, dx, dy))); return q

def touches(a, b, gap):
    """a et b à moins de gap verticalement ?"""
    return bool(bounds(inter(grow(a, 0.5, gap / 2) if gap > 0 else a, grow(b, 0.5, gap / 2) if gap > 0 else b)))

def vclear(a, b):
    """distance verticale libre entre a (au-dessus) et b (en dessous), par dichotomie"""
    lo, hi = 0.0, 400.0
    if bounds(inter(a, b)): return 0.0
    for _ in range(12):
        m = (lo + hi) / 2
        if bounds(inter(translate(a, 0, -m), b)): hi = m
        else: lo = m
    return lo

def topo(p):
    cl = [area(c) for c in contours(p)]
    cl = [a for a in cl if abs(a) >= 150]
    if not cl: return (0, 0)
    sg = 1 if max(cl, key=abs) > 0 else -1
    return (sum(1 for a in cl if a * sg > 0), sum(1 for a in cl if a * sg < 0))

from fontTools.pens.perimeterPen import PerimeterPen
def thickness(p):
    ap = AreaPen(); pp = PerimeterPen(); p.draw(ap); p.draw(pp)
    return 2 * abs(ap.value) / pp.value if pp.value else 0
_href = pathops.Path(); gs['H'].draw(TransformPen(_href.getPen(glyphSet=gs), (W, 0, 0, 1, 0, 0)))
T_REF = thickness(_href)

def build(name, scale=1.0, sx_=1.0):
    p = pathops.Path(); gs[name].draw(TransformPen(p.getPen(glyphSet=gs), (W, 0, 0, 1, 0, 0)))
    if not bounds(p): return p
    p.simplify(fix_winding=True)
    gx, gy = GX * sx_, GY * scale
    if GX < 0:                          # amincir : en proportion de l'épaisseur du caractère
        fthin = max(0.3, min(1.0, thickness(p) / T_REF))
        gx *= fthin; gy *= fthin
    comps = components(p)
    big = max(abs(area(contours(c)[0])) for c in comps)
    grown = []
    for c in comps:
        small = abs(area(contours(c)[0])) < 0.3 * big and len(comps) > 1
        g_ = offset_safe(c, gx, gy / 2 if small else gy)
        if gx < -5:                       # graisses fines : fermeture pour regarnir les jonctions arche-fût
            rc = min(CLOSE * STEM, abs(gx))
            try:
                h_ = offset_safe(offset_safe(g_, rc, rc), -rc, -rc)
                bg, bh = bounds(g_), bounds(h_)
                sane = bh and all(abs(a - b) <= 2 for a, b in zip(bg, bh)) and abs(sum(area(c) for c in contours(h_))) >= abs(sum(area(c) for c in contours(g_))) - 1
                if sane and topo(h_) == topo(g_): g_ = h_   # seulement si rien ne se bouche ni ne se perd
            except pathops.PathOpsError: pass
        grown.append(g_)
    rects = terminal_caps(p, gx, gy) if CAPS_ON else []
    if rects:
        Rr = union(rects)
        grown = [prune(union([diff(g, Rr), c]), c) for g, c in zip(grown, comps)]
    # écarts entre éléments séparés (points, accents) : on décale le plus petit
    if len(comps) > 1:
        order = sorted(range(len(comps)), key=lambda i: bounds(comps[i])[1])
        shift = [0.0] * len(comps)
        for _ in range(2):
            for ii, i in enumerate(order):
                for j in order[:ii]:
                    bi, bj = bounds(comps[i]), bounds(comps[j])
                    if bi[0] > bj[2] or bj[0] > bi[2]: continue      # pas l'un au-dessus de l'autre
                    if bi[1] < bj[3] - 2: continue                    # chevauchement vertical : pas un empilement
                    g0 = vclear(comps[i], comps[j])
                    target = max(MINGAP * g0, min(g0, 20))
                    gi = translate(grown[i], 0, shift[i]); gj = translate(grown[j], 0, shift[j])
                    now = vclear(gi, gj)
                    need = target - now
                    if need <= 0.5: continue
                    ai = abs(area(contours(comps[i])[0])); aj = abs(area(contours(comps[j])[0]))
                    if ai < 0.5 * aj: shift[i] += need                 # le petit du dessus monte
                    elif aj < 0.5 * ai: shift[j] -= need               # le petit du dessous descend
                    else: shift[i] += need / 2; shift[j] -= need / 2
        grown = [translate(g, 0, s) for g, s in zip(grown, shift)]
    return union(grown)

def src_topo(name):
    p = pathops.Path(); gs[name].draw(p.getPen(glyphSet=gs)); p.simplify(fix_winding=True)
    return topo(p)

def holes_area(p):
    cl = [area(c) for c in contours(p)]
    cl = [a for a in cl if abs(a) >= 150]
    if not cl: return 0
    sg = 1 if max(cl, key=abs) > 0 else -1
    return sum(abs(a) for a in cl if a * sg < 0)

OVR = {'eth': (0.45, 0.6), 'eth.sc': (0.45, 0.6)}   # croix du ð : moins épaissie pour rester lisible
names = ONLY or f.getGlyphOrder()
results = {}
TRIES = [(s_, 1.0) for s_ in (1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2)] + [(0.4, x_) for x_ in (0.7, 0.4)]
for n in names:
    p0 = pathops.Path(); gs[n].draw(TransformPen(p0.getPen(glyphSet=gs), (W, 0, 0, 1, 0, 0))); p0.simplify(fix_winding=True)
    t0 = topo(p0); h0 = holes_area(p0)
    # ouverture de départ : jusqu'où on peut épaissir la source sans boucher (mesure relative)
    d0 = 2
    for d in (30, 25, 20, 15, 10, 5):
        if all(topo(grow(c, 6, d)) == topo(c) for c in components(p0)): d0 = d; break
    dreq = min(20, 0.5 * d0)
    if n in OVR and GX > 0:           # réglage imposé (graisses épaissies), sans contrôle automatique
        sc, sx_ = OVR[n]; results[n] = build(n, sc, sx_); print(f'  {n}: imposé vertical ×{sc} horizontal ×{sx_}'); continue
    def ok_(r):
        b0, b1 = bounds(p0), bounds(r)
        if b1 and (b1[2] < b0[2] - 1.3 * abs(GX) - 6 or b1[0] > b0[0] + 1.3 * abs(GX) + 6): return False
        return topo(r) == t0 and holes_area(r) >= 0.3 * h0 and all(topo(grow(c, 6, dreq)) == topo(c) for c in components(r))
    if GX < 0:
        r = build(n, 1.0, 1.0)
        if bounds(r) and not ok_(r):
            for fr in (0.6, 0.4, 0.2, 0.0):
                E2 = build(n, fr, fr) if fr > 0 else pathops.Path(p0)
                d = (1 - fr) * max(abs(GX), abs(GY)) + 2
                try:
                    N = diff(E2, offset(r, d, d))
                    if not bounds(N): continue
                    cand = union([r, inter(E2, offset(N, d, d))])
                except pathops.PathOpsError: continue
                if ok_(cand):
                    r = cand; print(f'  {n}: morceau fin repris (×{fr})'); break
        if bounds(r) and ok_(r):
            results[n] = r; continue
    for sc, sx_ in TRIES:
        r = build(n, sc, sx_)
        if not bounds(r): break
        if ok_(r) and holes_area(r) >= 0.3 * h0 and all(topo(grow(c, 6, dreq)) == topo(c) for c in components(r)): break
    else:
        print('  NON RÉSOLU', n)
    if (sc, sx_) != (1.0, 1.0): print(f'  {n}: vertical ×{sc} horizontal ×{sx_}')
    results[n] = r

for n in f.getGlyphOrder():
    adv = f['hmtx'][n][0]
    w = round(adv * W + (2 * GX if GX > 0 else 0)) if adv > 0 else 0
    t2 = T2CharStringPen(w, gs)
    if n in results and bounds(results[n]):
        dx = GX if (GX > 0 and adv > 0) else 0
        results[n].draw(TransformPen(t2, (1, 0, 0, K, dx, GY * K)))
    elif n not in results and adv >= 0:
        pass
    cs[n] = t2.getCharString(private=cs[n].private, globalSubrs=cs[n].globalSubrs)
    f['hmtx'][n] = (w, 0)
gs2 = f.getGlyphSet()
for n in f.getGlyphOrder():
    bp = BoundsPen(gs2); gs2[n].draw(bp)
    f['hmtx'][n] = (f['hmtx'][n][0], round(bp.bounds[0]) if bp.bounds else 0)

def scale_vr(v):
    if v is None: return
    for a_ in ('XAdvance', 'XPlacement'):
        if hasattr(v, a_): setattr(v, a_, round(getattr(v, a_) * W))
def walk(st):
    t = st.__class__.__name__
    if t == 'ExtensionPos': return walk(st.ExtSubTable)
    if t == 'PairPos':
        if st.Format == 1:
            for ps in st.PairSet:
                for r in ps.PairValueRecord: scale_vr(r.Value1); scale_vr(r.Value2)
        else:
            for c1 in st.Class1Record:
                for c2 in c1.Class2Record: scale_vr(c2.Value1); scale_vr(c2.Value2)
if 'GPOS' in f:
    for lk in f['GPOS'].table.LookupList.Lookup:
        for st in lk.SubTable: walk(st)
for rec in f['name'].names:
    if rec.nameID in (1, 4, 16): rec.string = 'Clebard Preview'
    if rec.nameID == 6: rec.string = 'Clebard-Preview'
f.save(out); print('ok', out, 'GX', round(GX, 1), 'GY', round(GY, 1), 'K', round(K, 3))
