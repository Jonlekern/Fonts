# Sans géométrique : capitales A–Z
import math
from geo_core import *

def build_caps(w):
    S, T, R, J = w.STC, w.TDC, w.RC, w.J
    e = 1.15 * J; cy = CAP / 2; f = round(0.30 * T); G = {}
    stem = lambda x, y0=0, y1=CAP: rect(x, y0, x + S, y1)
    # O C G Q
    O = ring(R, cy, R, S); W2 = 2 * R
    G['O'] = Gl(O, [], [(R, cy, R)], 'OO')
    G['C'] = Gl(arc(R, cy, R, S, 44, 316), [], [(R, cy, R)], 'OO')
    gr = arc(R, cy, R, S, 44, 360)
    G['G'] = Gl(U(gr, rect(R, cy - S, W2 - S / 2, cy)), [], [(R, cy, R)], 'OO',
                alt=U(gr, I(rect(R, cy - S, W2 - S / 2, cy), circ(R, cy, R - S - J))))
    bar_ = rbar
    u = (math.cos(math.radians(-50)), math.sin(math.radians(-50))); r0 = min(R - 1.6 * S, 0.75 * (R - S))
    p0 = (R + r0 * u[0], cy + r0 * u[1]); p1 = (R + 1.40 * R * u[0], cy + 1.40 * R * u[1])
    d = (p1[0] - p0[0], p1[1] - p0[1]); Ld = math.hypot(*d)
    tail = bar_(p0, p1, T)
    tw_ = bar_((p0[0] - d[0] / Ld * 60, p0[1] - d[1] / Ld * 60), (p1[0] + d[0] / Ld * 60, p1[1] + d[1] / Ld * 60), T + 2 * e)
    G['Q'] = Gl(U(O, tail), [I(O, D(tw_, tail))], [(R, cy, R)], 'OO', 0, W2)
    # D P B R : fût + panses en demi-cercle
    def panse(x0, xc, yb, yt):
        """panse : barres haut et bas du fût jusqu'à xc, puis demi-anneau à droite"""
        r = (yt - yb) / 2
        return U(tbar(x0, yt - S, xc, yt, xc, yb + r, r), tbar(x0, yb, xc, yb + S, xc, yb + r, r), I(ring(xc, yb + r, r, S), vreal(xc, yb + r, -1))), (xc, yb + r, r)
    sj = rect(S, -10, S + J, CAP + 10)
    dw = round(0.70 * CAP + 0.3 * S); pD, cD = panse(0, dw - CAP / 2, 0, CAP)
    G['D'] = Gl(U(stem(0), pD), [sj], [cD], 'SO')
    yb = round(0.40 * CAP); pw = round(0.54 * CAP + 0.4 * S); rp = (CAP - yb) / 2
    pP, cP = panse(0, pw - rp, yb, CAP)
    G['P'] = Gl(U(stem(0), pP), [sj], [cP], 'SO')
    ym = round(0.54 * CAP); bw = round(0.56 * CAP + 0.4 * S)
    r2 = (ym + S / 2) / 2; r1 = (CAP - ym + S / 2) / 2
    pB2, cB2 = panse(0, bw - r2, 0, ym + S / 2); pB1, cB1 = panse(0, bw - r2 - 0.04 * CAP - (r1 - r2) * 0, ym - S / 2, CAP)
    pB1, cB1 = panse(0, bw - 0.04 * CAP - r1, ym - S / 2, CAP)
    G['B'] = Gl(U(stem(0), pB1, pB2), [sj], [cB1, cB2], 'SO')
    rw = round(0.60 * CAP + 0.4 * S)
    xl = cP[0]; hl = fit_h(T, rw - xl, yb + S / 2)
    leg = poly(para2(rw - hl, xl - hl / 2 + 0, hl, 0, yb + S / 2))
    G['R'] = Gl(U(stem(0), pP, leg), [sj], [cP], 'SD', 0, rw, alt=U(stem(0), pP, I(leg, rect(-10, -10, rw + 10, yb - J))))
    # E F L T H I
    ew = round(0.42 * CAP + 0.5 * S)
    bars = lambda w_, ys: [rect(0, y, w_, y + S) for y in ys]
    G['E'] = Gl(U(stem(0), *bars(ew, (0, CAP - S)), rect(0, cy - S / 2, round(0.9 * ew), cy + S / 2)), [sj], [], 'SS')
    G['F'] = Gl(U(stem(0), rect(0, CAP - S, ew - 0.03 * CAP, CAP), rect(0, cy - S / 2 - 0.03 * CAP, round(0.88 * ew), cy + S / 2 - 0.03 * CAP)), [sj], [], 'SS')
    G['L'] = Gl(U(stem(0), rect(0, 0, ew - 0.02 * CAP, S)), [rect(S, S, S + J, CAP + 10)], [], 'SS')
    tw = round(0.56 * CAP + 0.3 * S); xs = (tw - S) / 2
    G['T'] = Gl(U(rect(0, CAP - S, tw, CAP), stem(xs)), [rect(xs - 10, CAP - S - J, xs + S + 10, CAP - S)], [], 'SS')
    hw = round(0.64 * CAP + 0.5 * S)
    G['H'] = Gl(U(stem(0), stem(hw - S), rect(0, cy - S / 2, hw, cy + S / 2)),
                [rect(S, cy - S, S + J, cy + S), rect(hw - S - J, cy - S, hw - S, cy + S)], [], 'SS')
    G['I'] = Gl(stem(0), [], [], 'SS')
    # J U
    rj = round(0.20 * CAP + 0.6 * S); jw = 2 * rj; cj = rj - OVC
    G['J'] = Gl(U(stem(jw - S, cj), arc(rj, cj, rj, S, 200, 360)), [rect(jw - S - 10, cj, jw + 10, cj + J)], [(rj, cj, rj)], 'DS', 0, jw)
    uw = round(0.64 * CAP + 0.5 * S); ru = uw / 2; cu = ru - OVC
    G['U'] = Gl(U(stem(0, cu), stem(uw - S, cu), arc(ru, cu, ru, S, 180, 360)),
                [rect(-10, cu, S + 10, cu + J), rect(uw - S - 10, cu, uw + 10, cu + J)], [(ru, cu, ru)], 'SS')
    # S
    tv = round(0.78 * S); ry = (CAP + 2 * OVC + tv) / 4; rx = ry + 0.30 * S
    c1 = CAP + OVC - ry; c2 = ry - OVC
    G['S'] = Gl(U(sbout(rx, c1, rx, ry, S, tv, 270, 28), sbout(rx, c2, rx, ry, S, tv, 90, -152)),
                [rect(rx - J / 2, c2 + ry - tv - 2, rx + J / 2, c1 - ry + tv + 2)], [(rx, c1, rx, ry, 'point', tv), (rx, c2, rx, ry, 'point', tv)], 'OO')
    G['S'].geo = (rx, c1, c2, ry, tv)
    # V A
    vw = round(0.80 * CAP + 0.6 * S)
    pL, pR, hv = vpair_pts(vw / 2, 0, CAP, vw / 2, f, T); L, Rr = clip_pair(pL, pR)
    G['V'] = Gl(U(L, Rr), [I(L, band(pR, -1, e))], [], 'DD', 0, vw)
    aw = vw
    pL, pR, ha = vpair_pts(aw / 2, CAP, 0, aw / 2, f, T); L, Rr = clip_pair(pL, pR)
    ya = round(0.17 * CAP); tb = round(0.85 * S)
    xbar = rect(0, ya, aw, ya + tb)
    barP = I(I(xbar, half(pedges(pL)[0][0], pedges(pL)[0][1], -1)), half(pedges(pR)[1][0], pedges(pR)[1][1], 1))
    lLr = pedges(pL)[1]; lRl = pedges(pR)[0]
    barC = I(I(xbar, poly(ext(para2(pL[1][0] + e, pL[2][0] + e, 3000, 0, CAP)))), poly(ext(para2(pR[0][0] - e - 3000, pR[3][0] - e - 3000, 3000, 0, CAP))))
    G['A'] = Gl(U(L, Rr, barP), [I(L, band(pR, -1, e))], [], 'DD', 0, aw, alt=U(L, Rr, barC))
    # W
    ww = round(1.24 * CAP + 0.5 * S); q = ww / 4
    hA = hwidth(T, q - f / 2, CAP); hB = fit_h(T, q - f, CAP)
    pA = para2(q - f / 2, 0, hA, 0, CAP); pDd = para2(3 * q + f / 2 - hA, ww - hA, hA, 0, CAP)
    pB = para2(q + f / 2 - hB, 2 * q - f / 2, hB, 0, CAP); pC = para2(3 * q - f / 2, 2 * q + f / 2 - hB, hB, 0, CAP)
    (lA, rA), (lB, rB), (lC, rC), (lD, rD) = map(pedges, (pA, pB, pC, pDd))
    A_ = I(poly(pA), half(rB[0], rB[1], 1)); B_ = I(I(poly(pB), half(lA[0], lA[1], -1)), half(rC[0], rC[1], 1))
    C_ = I(I(poly(pC), half(lB[0], lB[1], -1)), half(rD[0], rD[1], 1)); D_ = I(poly(pDd), half(lC[0], lC[1], -1))
    G['W'] = Gl(U(A_, B_, C_, D_), [I(A_, band(pB, -1, e)), I(C_, band(pB, 1, e)), I(D_, band(pC, 1, e))], [], 'DD', 0, ww)
    # M N : les fûts s'arrêtent sous l'oblique en construction
    mw = round(0.88 * CAP + 0.6 * S)
    hm = hwidth(T, mw / 2 - f / 2, CAP)
    pL = para2(mw / 2 - f / 2, 0, hm, 0, CAP); pR = para2(mw / 2 + f / 2 - hm, mw - hm, hm, 0, CAP); L, Rr = clip_pair(pL, pR)
    yl = edge_x(pL, -1, 0) and None
    def under(pts, side, x):
        """hauteur du bord gauche (-1) / droit (1) d'un trait oblique à l'abscisse x"""
        (xb, y0), (xb2, _), (xt2, y1), (xt, _) = pts
        a, b = (xb, xt) if side < 0 else (xb2, xt2)
        return y0 + (x - a) * (y1 - y0) / (b - a)
    def vgap(pts):
        """écart vertical qui donne un jour de J perpendiculaire au trait"""
        (xb, y0), _, _, (xt, y1) = pts; return J * math.hypot(xt - xb, y1 - y0) / abs(xt - xb)
    mL = under(pL, -1, S) - vgap(pL); mR = under(pR, 1, mw - S) - vgap(pR)
    G['M'] = Gl(U(stem(0), stem(mw - S), L, Rr), [I(L, band(pR, -1, e))], [], 'SS', 0, mw)
    nw = round(0.68 * CAP + 0.4 * S); hn = fit_h(T, nw, CAP)
    pN = para2(nw - hn, 0, hn, 0, CAP); N_ = poly(pN)
    nL = under(pN, -1, S) - vgap(pN); nR = under(pN, 1, nw - S) + vgap(pN)
    G['N'] = Gl(U(stem(0), stem(nw - S), N_), [], [], 'SS', 0, nw)
    # K
    kw = round(0.62 * CAP + 0.4 * S); yj = round(0.40 * CAP); fa = round(0.3 * T)
    yA, yL = yj + fa / 2, yj - fa / 2
    hA = fit_h(T, kw - S, CAP - yA); hL = fit_h(T, kw - S, yL)
    sA = (kw - hA - S) / (CAP - yA); sL = (kw - hL - S) / yL
    arm_l = ((S, yA), (kw - hA, CAP)); leg_l = ((kw - hL, 0), (S, yL))
    arm = poly(para2(S - sA * (yA + 300), kw - hA, hA, -300, CAP)); lg = poly(para2(kw - hL, S - sL * (CAP + 300 - yL), hL, 0, CAP + 300))
    arm = I(arm, half(leg_l[0], leg_l[1], -1)); lg = I(lg, half(arm_l[0], arm_l[1], -1)); clipk = rect(S - 1, 0, kw, CAP)
    G['K'] = Gl(U(stem(0), I(arm, clipk), I(lg, clipk)), [rect(S, -10, S + J, CAP + 10)], [], 'SD', 0, kw)
    # X Y Z
    xw = round(0.70 * CAP + 0.3 * S); hx = fit_h(T, xw, CAP)
    pXa = para2(xw - hx, 0, hx, 0, CAP); pXb = para2(0, xw - hx, hx, 0, CAP)
    Xa, Xb = poly(pXa), poly(pXb)
    G['X'] = Gl(U(Xa, Xb), [I(Xa, D(poly(ext(para2(-e, xw - hx - e, hx + 2 * e, 0, CAP))), Xb))], [], 'DD', 0, xw)
    yw = round(0.74 * CAP + 0.3 * S); yy = round(0.42 * CAP)
    pL, pR, hy = vpair_pts(yw / 2, yy, CAP, yw / 2, f, T); L, Rr = clip_pair(pL, pR)
    ys = yy + (S - f) / 2 * (CAP - yy) / (yw / 2 - f / 2)
    G['Y'] = Gl(U(L, Rr, rect(yw / 2 - S / 2, 0, yw / 2 + S / 2, ys)), [I(L, band(pR, -1, e)), rect(yw / 2 - S, yy - J, yw / 2 + S, yy)], [], 'DD', 0, yw)
    zw = round(0.60 * CAP + 0.3 * S); hz = fit_h(T, zw, CAP)
    G['Z'] = Gl(U(rect(0, CAP - S, zw, CAP), rect(0, 0, zw, S), poly(para2(0, zw - hz, hz, 0, CAP))),
                [rect(-10, S, zw + 10, S + J), rect(-10, CAP - S - J, zw + 10, CAP - S)], [], 'DD', 0, zw)
    for g in G.values(): g.sbk = 1.3        # les capitales respirent plus
    return G
