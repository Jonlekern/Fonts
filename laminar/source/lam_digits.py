# LAMINAR : chiffres (tabulaires, hauteur des capitales)
from lam_core import *
from lam_letters import rcorner

DN = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']

def tangent_pt(cx, cy, r, P, right=True):
    dx, dy = P[0] - cx, P[1] - cy; d = math.hypot(dx, dy); a = math.atan2(dy, dx); b = math.acos(r / d)
    t1 = (cx + r * math.cos(a + b), cy + r * math.sin(a + b)); t2 = (cx + r * math.cos(a - b), cy + r * math.sin(a - b))
    return max(t1, t2) if right else min(t1, t2)

def strip(p0, d, w, y0, y1):
    """bande oblique : bord gauche passe par p0, direction d (dx, dy) ; largeur horizontale w ; entre y0 et y1"""
    k = d[0] / d[1]; xa = p0[0] + k * (y0 - p0[1]); xb = p0[0] + k * (y1 - p0[1])
    return poly([(xa, y0), (xa + w, y0), (xb + w, y1), (xb, y1)])

def hbowl(xc, y0, y1, t, h, side=1):
    r = (y1 - y0) / 2; yc = (y0 + y1) / 2
    ring = D(circ(xc, yc, r), ell(xc, yc, r - t, r - h))
    return I(ring, rect(xc, y0 - 50, xc + side * (r + 50), y1 + 50))

def digits(c):
    H, S, h, ov = c.H, c.S, c.h, c.ov
    SO = round(1.06 * S); dS = round(0.93 * S); tv = round((S + h) / 2)
    DW = round(0.36 * H + 1.25 * S); G = {}
    tt = round(0.88 * S); th = round(0.14 * H)
    # 0 : stade, plein à gauche
    r0 = DW / 2; ri = (DW - SO - h) / 2
    out = U(rect(0, r0 - ov, DW, H + ov - r0), circ(r0, r0 - ov, r0), circ(r0, H + ov - r0, r0))
    inn = U(rect(SO, tv - ov + ri, DW - h, H + ov - tv - ri), circ(SO + ri, tv - ov + ri, ri), circ(SO + ri, H + ov - tv - ri, ri))
    G['zero'] = D(out, inn)
    # 1 : fût, drapeau délié
    xs = round(DW / 2 - S / 2 + 0.06 * DW); fw = round(0.30 * DW); fh = round(0.20 * H); hv = hw(h, fh, fw)
    flag = poly([(xs - fw, H - fh - hv), (xs + 1, H - hv), (xs + 1, H), (xs - fw, H - fh)])
    G['one'] = U(rect(xs, 0, xs + S, H), flag)
    # 2 : panse au compas, oblique pleine tangente, base déliée
    r2 = DW / 2; cx, cy = r2, H + ov - r2
    ring = ring_off(cx, cy, r2, SO, h, 1)
    wd = dS
    for _ in range(8):
        T = tangent_pt(cx, cy, r2, (wd, h)); wd = hw(dS, T[0] - wd, T[1] - h)
    T = tangent_pt(cx, cy, r2, (wd, h)); dvec = (T[0] - wd, T[1] - h)
    st = strip((0, h), dvec, wd, -10, cy + r2)
    st = I(st, U(circ(cx, cy, r2), rect(-1000, -10, 3000, T[1])))
    st = I(st, rect(0, 0, DW, H + 100))
    arc = I(ring, U(rect(-1000, cy, 3000, 3000), rect(cx, T[1] - 1, 3000, cy + 1)))
    G['two'] = U(arc, st, rect(0, 0, DW, h))
    # 3 : deux demi-panses à droite, bras déliés, éperons
    ym = round(0.56 * H); rL = (ym + h / 2) / 2; xl = DW - rL; rU = (H - (ym - h / 2)) / 2; xu = DW - round(0.05 * H) - rU
    xa = round(0.06 * DW)
    G['three'] = U(hbowl(xu, ym - h / 2, H, SO, h), hbowl(xl, 0, ym + h / 2, SO, h), rect(xa, H - h, xu + 1, H), rect(round(0.34 * DW), ym - h / 2, max(xu, xl) + 1, ym + h / 2),
                   rect(xa, 0, xl + 1, h), rect(xa, H - th, xa + tt, H), rect(xa, 0, xa + tt, th))
    # 4 : fût, oblique déliée, barre
    xs4 = DW - S - round(0.08 * DW); yb = round(0.28 * H); w4 = hw(h, xs4, H - yb)
    d4 = I(strip((0, yb), (xs4, H - yb), w4, yb, H), rect(0, yb, DW, H))
    G['four'] = U(rect(xs4, 0, xs4 + S, H), d4, rect(0, yb, DW, yb + h))
    # 5 : fût en haut à gauche, barre de tête, panse basse
    yb5 = round(0.58 * H); r5 = yb5 / 2; xl5 = DW - r5; x5 = round(0.04 * DW)
    G['five'] = U(rect(x5, yb5 - h, x5 + S, H), rect(x5, H - h, DW - round(0.04 * DW), H), rect(x5, yb5 - h, xl5 + 1, yb5), hbowl(xl5, 0, yb5, SO, h),
                  rect(xa, 0, xl5 + 1, h), rect(xa, 0, xa + tt, th))
    G['five'] = rcorner(G['five'], x5, H, round(0.85 * S), 'tl')
    # 6 : rond en bas, flanc gauche droit, arc de tête ; 9 = 6 retourné
    r6 = DW / 2; cyb = r6 - ov; cyt = H + ov - r6
    low = ring_off(r6, cyb, r6, SO, h, -1)
    topa = D(I(ring_off(r6, cyt, r6, SO, h, -1), rect(-100, cyt, 3000, 3000)), sector(r6, cyt, -10, 38))
    six = U(low, topa, rect(0, cyb, SO, cyt))
    G['six'] = six; G['nine'] = rot(six, 180, DW / 2, H / 2)
    # 7 : barre de tête déliée, oblique pleine
    x7 = round(0.16 * DW); w7 = dS
    for _ in range(8): w7 = hw(dS, DW - w7 - x7, H)
    G['seven'] = U(rect(0, H - h, DW, H), I(diag(x7, DW - w7, w7, 0, H), rect(-10, 0, DW + 10, H)))
    # 8 : deux anneaux ovales empilés, plein à gauche
    def oring(cx, cy, rx, ry):
        return D(ell(cx, cy, rx, ry), ell(cx + (SO - h) / 2, cy, rx - (SO + h) / 2, ry - tv))
    tot = H + 2 * ov + tv; rb = 0.53 * tot / 2; rt = tot / 2 - rb
    G['eight'] = U(oring(DW / 2, -ov + rb, DW / 2, rb), oring(DW / 2, H + ov - rt, 0.90 * DW / 2, rt))
    return G, DW
