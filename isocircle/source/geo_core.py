# Sans géométrique : moteur (ronds au compas, fûts droits, jonctions, filets de construction)
import math
import pathops

XH, ASC, DESC, CAP, OV, OVC = 500, 740, -220, 700, 8, 10

def P(): return pathops.Path()
def poly(pts):
    p = P(); pen = p.getPen(); pen.moveTo(pts[0])
    for q in pts[1:]: pen.lineTo(q)
    pen.closePath(); return p
def rect(x0, y0, x1, y1): return poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
def U(*ps):
    out = P()
    for p in ps:
        if p is not None: out = pathops.op(out, p, pathops.PathOp.UNION)
    return out
def D(a, *bs):
    for b in bs:
        if b is not None: a = pathops.op(a, b, pathops.PathOp.DIFFERENCE)
    return a
def I(a, b): return pathops.op(a, b, pathops.PathOp.INTERSECTION)

K = 0.5522847498
def ell(cx, cy, a, b):
    """ellipse (cercle si a == b) en 4 vraies courbes"""
    p = P(); pen = p.getPen(); pen.moveTo((cx + a, cy))
    pen.curveTo((cx + a, cy + K * b), (cx + K * a, cy + b), (cx, cy + b))
    pen.curveTo((cx - K * a, cy + b), (cx - a, cy + K * b), (cx - a, cy))
    pen.curveTo((cx - a, cy - K * b), (cx - K * a, cy - b), (cx, cy - b))
    pen.curveTo((cx + K * a, cy - b), (cx + a, cy - K * b), (cx + a, cy))
    pen.closePath(); return p
def circ(cx, cy, r): return ell(cx, cy, r, r)
def ring(cx, cy, r, t, tv=None):
    """anneau : rayon extérieur r, épaisseur t (tv : épaisseur haut/bas si différente)"""
    if tv is None: return D(circ(cx, cy, r), circ(cx, cy, r - t))
    return D(circ(cx, cy, r), ell(cx, cy, r - t, r - tv))
def ering(cx, cy, rx, ry, t, tv): return D(ell(cx, cy, rx, ry), ell(cx, cy, rx - t, ry - tv))
def sector(cx, cy, a0, a1, R=3000):
    """secteur angulaire (degrés, sens trigo de a0 à a1)"""
    n = max(2, int(abs(a1 - a0) / 8) + 1)
    pts = [(cx, cy)] + [(cx + R * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + R * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
    return poly(pts)
def arc(cx, cy, r, t, a0, a1): return I(ring(cx, cy, r, t), sector(cx, cy, a0, a1))
def earc(cx, cy, rx, ry, t, tv, a0, a1): return I(ering(cx, cy, rx, ry, t, tv), sector(cx, cy, a0, a1))
def para(xb, xt, h, y0, y1):
    """trait oblique : bas gauche en xb (à y0), haut gauche en xt (à y1), largeur horizontale h"""
    return poly([(xb, y0), (xb + h, y0), (xt + h, y1), (xt, y1)])
def hwidth(T, dx, dy):
    """largeur horizontale d'un trait d'épaisseur T qui monte de dy sur dx"""
    return T * math.hypot(dx, dy) / abs(dy)

class Wt:
    def __init__(s, st, num, wclass, filets):
        s.ST, s.num, s.wclass, s.filets = st, num, wclass, filets
        s.R = XH // 2 + OV                      # rayon extérieur du rond : tient pile dans la hauteur d'x
        s.W = 2 * s.R
        s.TD = round(0.94 * st)                 # obliques un poil plus fines que les fûts
        s.J = round(10 + 0.1 * st)              # jonction (fil de jour)
        s.HL = max(5, round(0.07 * st))         # filet de construction
        s.SBS = round(36 + 0.33 * st)            # approche d'un fût
        s.SBO = round(0.72 * s.SBS)             # approche d'un rond
        s.SBD = round(0.40 * s.SBS)             # approche d'une oblique
        s.STC = round(1.06 * st)                # fût des capitales
        s.TDC = round(0.94 * s.STC)
        s.RC = CAP // 2 + OVC                   # rayon du O

class Gl:
    """une lettre : encre pleine, coupes de jonction, centres de compas, côtés pour l'approche"""
    def __init__(s, ink, cuts=(), centers=(), sides='SS', x0=None, x1=None, alt=None):
        s.ink, s.cuts, s.centers, s.sides, s.alt = ink, list(cuts), list(centers), sides, alt
        b = ink.bounds if x0 is None or x1 is None else None
        s.x0 = x0 if x0 is not None else b[0]
        s.x1 = x1 if x1 is not None else b[2]

def finish(g, w, joints=True):
    """dessin final + chasse : jonctions coupées, filets de construction ajoutés"""
    sb = {'S': w.SBS, 'O': w.SBO, 'D': w.SBD, 'N': 0}
    k = getattr(g, 'sbk', 1.0); l, r = round(k * sb[g.sides[0]]), round(k * sb[g.sides[1]])
    ink = D(g.alt if g.alt is not None else g.ink, *g.cuts) if joints else g.ink
    adv = round(g.x1 - g.x0 + l + r); dx = l - g.x0
    from fontTools.pens.transformPen import TransformPen
    out = P(); ink.draw(TransformPen(out.getPen(), (1, 0, 0, 1, dx, 0)))
    if w.filets:
        out = U(out, construction(w, [(ce[0] + dx,) + tuple(ce[1:]) for ce in g.centers], adv))
    return out, adv

def construction(w, centers, adv):
    """filets : lignes de base, d'x, de hampe et de jambage sur toute la chasse ; cercles entiers ; croix de compas.
    centre : (cx, cy, r) ou (cx, cy, rx, ry, 'point') pour un rond sans axes (ellipse du s)"""
    h = w.HL; parts = [rect(0, y - h / 2, adv, y + h / 2) for y in (0, XH, CAP, DESC)]
    for ce in centers:
        cx, cy = ce[0], ce[1]
        if len(ce) == 3:
            rr = ce[2]; rm = rr - w.ST / 2
            parts.append(ring(cx, cy, rm + h / 2, h))
            parts.append(rect(cx - h / 2, cy - rr - 30, cx + h / 2, cy + rr + 30))
            k = 0.9 * w.ST + 20; parts.append(rect(cx - k, cy - h / 2, cx + k, cy + h / 2))
        else:
            rx, ry = ce[2], ce[3]; mx, my = rx - w.ST / 2, ry - ce[5] / 2
            parts.append(ering(cx, cy, mx + h / 2, my + h / 2, h, h))
        parts.append(ring(cx, cy, 2.4 * h, 1.2 * h))
    out = U(*parts)
    for ce in centers: out = D(out, circ(ce[0], ce[1], 1.2 * h))
    return out

def half(p, q, side=1, F=4000):
    """demi-plan à gauche (side=1) ou à droite (side=-1) de la droite p→q"""
    dx, dy = q[0] - p[0], q[1] - p[1]; L = math.hypot(dx, dy); ux, uy = dx / L, dy / L; nx, ny = -uy * side, ux * side
    a = (p[0] - ux * F, p[1] - uy * F); b = (p[0] + ux * F, p[1] + uy * F)
    return poly([a, b, (b[0] + nx * F, b[1] + ny * F), (a[0] + nx * F, a[1] + ny * F)])
def pedges(pa):
    """bords gauche et droit d'un trait oblique para : ((bas, haut), (bas, haut))"""
    (xb, y0), (xb2, _), (xt2, y1), (xt, _) = pa
    return ((xb, y0), (xt, y1)), ((xb2, y0), (xt2, y1))
def para2(xb, xt, h, y0, y1): return [(xb, y0), (xb + h, y0), (xt + h, y1), (xt, y1)]

def vpair_pts(cx, ya, yo, half_, f, T):
    """V (pointe en bas, ya < yo) ou Λ (pointe en haut) : deux traits obliques, plat f à la pointe, demi-ouverture half_ en yo"""
    h = hwidth(T, half_ - f / 2, abs(yo - ya))
    if ya < yo: return para2(cx - f / 2, cx - half_, h, ya, yo), para2(cx + f / 2 - h, cx + half_ - h, h, ya, yo), h
    return para2(cx - half_, cx - f / 2, h, yo, ya), para2(cx + half_ - h, cx + f / 2 - h, h, yo, ya), h
def clip_pair(pL, pR):
    """chaque trait coupé par le bord extérieur de l'autre : la pointe reste nette"""
    lL, rL = pedges(pL); lR, rR = pedges(pR)
    return I(poly(pL), half(rR[0], rR[1], 1)), I(poly(pR), half(lL[0], lL[1], -1))
def ext(pts, d=400):
    """prolonge un trait oblique au-delà de ses deux bouts"""
    (xb, y0), (xb2, _), (xt2, y1), (xt, _) = pts; sx = (xt - xb) / (y1 - y0)
    return [(xb - sx * d, y0 - d), (xb2 - sx * d, y0 - d), (xt2 + sx * d, y1 + d), (xt + sx * d, y1 + d)]
def band(pts, side, e):
    """bande de jour de largeur e contre le bord gauche (side=-1) ou droit (side=1) d'un trait oblique"""
    (xb, y0), (xb2, _), (xt2, y1), (xt, _) = pts
    if side < 0: return poly(ext(para2(xb - e, xt - e, e, y0, y1)))
    return poly(ext(para2(xb2, xt2, e, y0, y1)))
def edge_x(pts, side, y):
    """abscisse du bord gauche (-1) ou droit (1) d'un trait oblique à la hauteur y"""
    (xb, y0), (xb2, _), (xt2, y1), (xt, _) = pts
    a, b = (xb, xt) if side < 0 else (xb2, xt2)
    return a + (b - a) * (y - y0) / (y1 - y0)
def fit_h(T, span, H, n=6):
    """largeur horizontale h d'un trait dont le bord gauche parcourt span - h sur la hauteur H"""
    h = hwidth(T, span, H)
    for _ in range(n): h = hwidth(T, span - h, H)
    return h

def sbout(cx, cy, rx, ry, t, tv, a1, a_end):
    """arc d'ellipse de a_end à a1 (sens trigo), le bout a_end coupé selon la normale du trait (pas de pointe)"""
    body = I(ering(cx, cy, rx, ry, t, tv), sector(cx, cy, a_end - 30, a1))
    A, B = rx - t / 2, ry - tv / 2; th = math.radians(a_end)
    tt = math.atan2(math.sin(th) * A, math.cos(th) * B)
    P0 = (cx + A * math.cos(tt), cy + B * math.sin(tt)); n = (math.cos(tt) / A, math.sin(tt) / B)
    q = (P0[0] + n[0] * 100, P0[1] + n[1] * 100)
    tk = math.radians(a_end + 40); Tt = (cx + A * math.cos(tk), cy + B * math.sin(tk))
    side = 1 if (q[0] - P0[0]) * (Tt[1] - P0[1]) - (q[1] - P0[1]) * (Tt[0] - P0[0]) > 0 else -1
    return D(body, I(half(P0, q, -side), sector(cx, cy, a_end - 40, a_end + 12)))

from fontTools.pens.transformPen import TransformPen as _TP
def xf(p, m):
    """transforme un contour (a, b, c, d, dx, dy) ; un miroir est recousu par une union"""
    out = P(); p.draw(_TP(out.getPen(), m))
    return U(out) if m[0] * m[3] - m[1] * m[2] < 0 else out
def rot(p, ang, cx, cy):
    c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    return xf(p, (c, s, -s, c, cx - c * cx + s * cy, cy - s * cx - c * cy))
def mirror(p, x):
    """miroir gauche-droite autour de la verticale x"""
    return xf(p, (-1, 0, 0, 1, 2 * x, 0))
def drop(cx, cy, r, tip, flat=0.10):
    """goutte au compas et à la règle : cercle + deux tangentes jusqu'à la pointe (pointe coupée net)"""
    dx, dy = tip[0] - cx, tip[1] - cy; d = math.hypot(dx, dy); a = math.atan2(dy, dx); b = math.acos(r / d)
    t1 = (cx + r * math.cos(a + b), cy + r * math.sin(a + b)); t2 = (cx + r * math.cos(a - b), cy + r * math.sin(a - b))
    body = U(circ(cx, cy, r), poly([t1, tip, t2, (cx, cy)]))
    k = 1 - flat * 2 * r / d; c0 = (cx + dx * k, cy + dy * k)          # coupe perpendiculaire près de la pointe
    n = (-dy, dx); return D(body, half(c0, (c0[0] + n[0], c0[1] + n[1]), 1 if (dx * n[1] - dy * n[0]) < 0 else -1))
