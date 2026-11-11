# Sans géométrique : minuscules a–z
import math
from geo_core import *

def vee(cx, w, y0, y1, half, f, T):
    """deux obliques qui se rejoignent en (cx, y0) sur un plat f ; écartées de half de chaque côté à y1.
    renvoie (trait gauche, trait droit, hauteur du creux intérieur)"""
    sgn = 1 if y1 > y0 else -1; H = abs(y1 - y0)
    dx = half - f / 2; h = hwidth(T, dx, H)
    if sgn > 0:
        L = para(cx - f / 2, cx - half, h, y0, y1); Rr = para(cx + f / 2 - h, cx + half - h, h, y0, y1)
    else:
        L = para(cx - half, cx - f / 2, h, y1, y0); Rr = para(cx + half - h, cx + f / 2 - h, h, y1, y0)
    # creux : les bords intérieurs se croisent au centre
    yi = y0 + sgn * (h - f / 2) * H / dx if dx else y0
    return L, Rr, yi, h

def build_lower(w):
    ST, R, Wd, J, TD = w.ST, w.R, w.W, w.J, w.TD
    cy = XH / 2; G = {}
    bowl = ring(R, cy, R, ST)
    # o a b d p q
    G['o'] = Gl(bowl, [], [(R, cy, R)], 'OO')
    G['a'] = Gl(U(bowl, rect(Wd - ST, 0, Wd, XH)), [rect(Wd - ST - J, -30, Wd - ST, XH + 30)], [(R, cy, R)], 'OS')
    G['d'] = Gl(U(bowl, rect(Wd - ST, 0, Wd, ASC)), [rect(Wd - ST - J, -30, Wd - ST, XH + 30)], [(R, cy, R)], 'OS')
    G['q'] = Gl(U(bowl, rect(Wd - ST, DESC, Wd, XH)), [rect(Wd - ST - J, -30, Wd - ST, XH + 30)], [(R, cy, R)], 'OS')
    G['b'] = Gl(U(bowl, rect(0, 0, ST, ASC)), [rect(ST, -30, ST + J, XH + 30)], [(R, cy, R)], 'SO')
    G['p'] = Gl(U(bowl, rect(0, DESC, ST, XH)), [rect(ST, -30, ST + J, XH + 30)], [(R, cy, R)], 'SO')
    # c e : coupes au rayon
    G['c'] = Gl(arc(R, cy, R, ST, 42, 318), [], [(R, cy, R)], 'OO')
    opening = I(sector(R, cy, -42, 20), rect(-10, -100, Wd + 10, cy - ST / 2))
    ering_ = D(bowl, opening)
    e = U(ering_, rect(ST / 2, cy - ST / 2, Wd - ST / 2, cy + ST / 2))
    e_c = U(ering_, I(rect(ST / 2, cy - ST / 2, R + 1, cy + ST / 2), circ(R, cy, R - ST - J)), rect(R, cy - ST / 2, Wd - ST / 2, cy + ST / 2))
    G['e'] = Gl(e, [rect(R, cy + ST / 2, Wd + 10, cy + ST / 2 + J)], [(R, cy, R)], 'OO', alt=e_c)
    # n h m u r : arches
    arch = arc(R, cy, R, ST, 0, 180)
    nj = rect(ST, cy - 1, ST + J, XH + 60)
    G['n'] = Gl(U(rect(0, 0, ST, XH), arch, rect(Wd - ST, 0, Wd, cy + 1)), [nj], [(R, cy, R)], 'SS')
    G['h'] = Gl(U(rect(0, 0, ST, ASC), arch, rect(Wd - ST, 0, Wd, cy + 1)), [nj], [(R, cy, R)], 'SS')
    G['u'] = Gl(U(rect(0, cy - 1, ST, XH), arc(R, cy, R, ST, 180, 360), rect(Wd - ST, 0, Wd, XH)),
                [rect(Wd - ST - J, -60, Wd - ST, cy + 1)], [(R, cy, R)], 'SS')
    ra = round(0.39 * Wd + ST / 4); ca = XH + OV - ra
    m = U(rect(0, 0, ST, XH), arc(ra, ca, ra, ST, 0, 180), rect(2 * ra - ST, 0, 2 * ra, ca + 1),
          arc(3 * ra - ST, ca, ra, ST, 0, 180), rect(4 * ra - 2 * ST, 0, 4 * ra - ST, ca + 1))
    G['m'] = Gl(m, [rect(ST, ca - 1, ST + J, XH + 60), rect(2 * ra, ca - 1, 2 * ra + J, XH + 60)],
                [(ra, ca, ra), (3 * ra - ST, ca, ra)], 'SS')
    G['r'] = Gl(U(rect(0, 0, ST, XH), arc(R, cy, R, ST, 62, 180)), [nj], [(R, cy, R)], 'SD')
    # g
    cg = DESC + R - OV
    hook = arc(R, cg, R, ST, 198, 360)
    G['g'] = Gl(U(bowl, rect(Wd - ST, cg, Wd, XH), hook),
                [rect(Wd - ST - J, cg + 20, Wd - ST, XH + 30), rect(Wd - ST - 10, cg - J, Wd + 10, cg)],
                [(R, cy, R), (R, cg, R)], 'OS')
    # i j l : point rond
    dd = round(1.16 * ST); dy = XH + round(0.35 * ST + 44) + dd / 2
    dot = lambda x: circ(x, dy, dd / 2)
    G['i'] = Gl(U(rect(0, 0, ST, XH), dot(ST / 2)), [], [], 'SS', 0, ST)
    G['l'] = Gl(rect(0, 0, ST, ASC), [], [], 'SS')
    rj = round(0.42 * R + 0.8 * ST); cj = DESC - OV + rj
    G['j'] = Gl(U(rect(0, cj, ST, XH), arc(ST - rj, cj, rj, ST, 232, 360), dot(ST / 2)),
                [rect(-10, cj, ST + 10, cj + J)], [(ST - rj, cj, rj)], 'SS', 0, ST)
    # t f
    e_ = round(0.33 * R + 0.1 * ST); tt = XH + round(0.6 * (ASC - XH))
    G['t'] = Gl(U(rect(e_, 0, e_ + ST, tt), rect(0, XH - ST, 2 * e_ + ST, XH)),
                [rect(e_ - 10, XH - ST - J, e_ + ST + 10, XH - ST)], [], 'SS')
    rf = round(0.42 * R + 0.8 * ST); cf = ASC + OV - rf
    G['f'] = Gl(U(rect(e_, 0, e_ + ST, cf), arc(e_ + rf, cf, rf, ST, 44, 180), rect(0, XH - ST, 2 * e_ + ST, XH)),
                [rect(e_ - 10, XH - ST - J, e_ + ST + 10, XH - ST), (rect(e_ - 10, cf - J, e_ + ST + 10, cf) if cf - J - XH >= 40 else rect(e_ - 10, XH, e_ + ST + 10, XH + J))],
                [(e_ + rf, cf, rf)], 'SD', 0, 2 * e_ + ST)
    # k : bras et jambe partent du fût en « < »
    kw = round(0.80 * Wd); yj = round(0.40 * XH); fa = round(0.3 * TD)
    yA, yL = yj + fa / 2, yj - fa / 2
    hA = hwidth(TD, kw - ST, XH - yA)
    for _ in range(6): hA = hwidth(TD, kw - hA - ST, XH - yA)
    hL = hwidth(TD, kw - ST, yL)
    for _ in range(6): hL = hwidth(TD, kw - hL - ST, yL)
    sA = (kw - hA - ST) / (XH - yA); sL = (kw - hL - ST) / yL
    arm_l = ((ST, yA), (kw - hA, XH)); leg_l = ((kw - hL, 0), (ST, yL))
    arm = poly(para2(ST - sA * (yA + 300), kw - hA, hA, -300, XH))
    leg = poly(para2(kw - hL, ST - sL * (XH + 300 - yL), hL, 0, XH + 300))
    arm = I(arm, half(leg_l[0], leg_l[1], -1)); leg = I(leg, half(arm_l[0], arm_l[1], -1))
    clipk = rect(ST - 1, 0, kw, XH)
    G['k'] = Gl(U(rect(0, 0, ST, ASC), I(arm, clipk), I(leg, clipk)), [rect(ST, -10, ST + J, XH + 10)], [], 'SD', 0, kw)
    # v w y x z
    vw = round(0.90 * Wd); f = round(0.30 * TD)
    hv = hwidth(TD, vw / 2 - f / 2, XH)
    pL = para2(vw / 2 - f / 2, 0, hv, 0, XH); pR = para2(vw / 2 + f / 2 - hv, vw - hv, hv, 0, XH)
    def gap_along(stroke_pts, side):
        """bande de jour de largeur J le long du bord gauche (side=-1) ou droit (side=1) d'un trait oblique"""
        (xb, y0), (xb2, _), (xt2, y1), (xt, _) = stroke_pts; e = 1.15 * J
        if side < 0: return poly([(xb - e, y0 - 300), (xb, y0 - 300), (xt, y1 + 300), (xt - e, y1 + 300)]) if False else poly(para2(xb - e, xt - e, e, y0, y1))
        return poly(para2(xb2, xt2, e, y0, y1))
    def ext(pts, d=300):
        """prolonge un trait oblique au-delà de ses deux bouts"""
        (xb, y0), (xb2, _), (xt2, y1), (xt, _) = pts; sx = (xt - xb) / (y1 - y0)
        return [(xb - sx * d, y0 - d), (xb2 - sx * d, y0 - d), (xt2 + sx * d, y1 + d), (xt + sx * d, y1 + d)]
    def vpair(pL, pR):
        """trait gauche coupé par le bord droit du trait droit, et inversement"""
        lL, rL = pedges(pL); lR, rR = pedges(pR)
        return I(poly(pL), half(rR[0], rR[1], 1)), I(poly(pR), half(lL[0], lL[1], -1))
    L, Rr = vpair(pL, pR)
    G['v'] = Gl(U(L, Rr), [I(L, poly(ext(para2(pR[0][0] - 1.15 * J, pR[3][0] - 1.15 * J, 1.15 * J, 0, XH))))], [], 'DD', 0, vw)
    ww = round(1.42 * Wd); q = ww / 4
    hA = hwidth(TD, q - f / 2, XH)
    hB = hA
    for _ in range(6): hB = hwidth(TD, q - f + hB, XH)
    pA = para2(q - f / 2, 0, hA, 0, XH); pD = para2(3 * q + f / 2 - hA, ww - hA, hA, 0, XH)
    pB = para2(q + f / 2 - hB, 2 * q - f / 2, hB, 0, XH); pC = para2(3 * q - f / 2, 2 * q + f / 2 - hB, hB, 0, XH)
    (lA, rA), (lB, rB), (lC, rC), (lD, rD) = map(pedges, (pA, pB, pC, pD))
    A = I(poly(pA), half(rB[0], rB[1], 1))
    B = I(I(poly(pB), half(lA[0], lA[1], -1)), half(rC[0], rC[1], 1))
    C = I(I(poly(pC), half(lB[0], lB[1], -1)), half(rD[0], rD[1], 1))
    Dd = I(poly(pD), half(lC[0], lC[1], -1))
    e = 1.15 * J
    gB_l = poly(ext(para2(pB[0][0] - e, pB[3][0] - e, e, 0, XH))); gB_r = poly(ext(para2(pB[1][0], pB[2][0], e, 0, XH)))
    gC_r = poly(ext(para2(pC[1][0], pC[2][0], e, 0, XH)))
    G['w'] = Gl(U(A, B, C, Dd), [I(A, gB_l), I(C, gB_r), I(Dd, gC_r)], [], 'DD', 0, ww)
    yw = vw; hy = hv; slope = (yw / 2 - f / 2) / XH
    pLy = para2(yw / 2 - f / 2, 0, hy, 0, XH)
    pRy = para2(yw / 2 + f / 2 - hy + DESC * slope, yw - hy, hy, DESC, XH)
    lRy, rRy = pedges(pRy)
    Ly = I(poly(pLy), half(rRy[0], rRy[1], 1)); Rlong = poly(pRy)
    wide = poly(para2(pRy[0][0] - 1.1 * J, pRy[3][0] - 1.1 * J, hy + 1.1 * J, DESC - 10 * 0, XH))
    G['y'] = Gl(U(Ly, Rlong), [I(Ly, D(wide, Rlong))], [], 'DD', 0, yw)
    xw = round(0.84 * Wd); hx = hwidth(TD, xw, XH)
    for _ in range(4): hx = hwidth(TD, xw - hx, XH)
    A = para(xw - hx, 0, hx, 0, XH); B = para(0, xw - hx, hx, 0, XH)
    Bw = para(-J * 1.15, xw - hx - J * 1.15, hx + 2.3 * J, 0, XH)
    G['x'] = Gl(U(A, B), [I(A, D(Bw, B))], [], 'DD', 0, xw)
    zw = round(0.78 * Wd); hz = hwidth(TD, zw, XH)
    for _ in range(4): hz = hwidth(TD, zw - hz, XH)
    zd = para(0, zw - hz, hz, 0, XH)
    G['z'] = Gl(U(rect(0, XH - ST, zw, XH), rect(0, 0, zw, ST), zd),
                [rect(-10, ST, zw + 10, ST + J), rect(-10, XH - ST - J, zw + 10, XH - ST)], [], 'DD', 0, zw)
    # s : deux arcs au compas empilés, l'axe du milieu partagé
    tv = round(0.78 * ST); ry = (XH + 2 * OV + tv) / 4; rx = ry + 0.6 * ST
    c1 = XH + OV - ry; c2 = ry - OV
    s = U(sbout(rx, c1, rx, ry, ST, tv, 270, 24), sbout(rx, c2, rx, ry, ST, tv, 90, -156))
    G['s'] = Gl(s, [rect(rx - J / 2, c2 + ry - tv - 2, rx + J / 2, c1 - ry + tv + 2)], [(rx, c1, rx, ry, 'point', tv), (rx, c2, rx, ry, 'point', tv)], 'OO')
    return G
