# LAMINAR : les 26 lettres, dessinées pour une hauteur donnée (capitales ou petites capitales)
from lam_core import *

def rcorner(p, x, y, r, q):
    """arrondit le coin extérieur (x, y) ; q = 'bl' 'tl' 'br' 'tr'"""
    sx = 1 if q[1] == 'l' else -1; sy = 1 if q[0] == 'b' else -1
    sq = rect(x, y, x + sx * r, y + sy * r); cc = circ(x + sx * r, y + sy * r, r)
    return U(D(p, sq), I(I(p, sq), cc))

def letters(c):
    H, S, h, CT, W, Bm, ov = c.H, c.S, c.h, c.CT, c.W, c.BAR, c.ov
    dS = round(0.93 * S); SO = round(1.06 * S); rr = round(0.85 * S)
    G = {}
    top = lambda x0, x1: rect(x0, H - h, x1, H)
    bot = lambda x0, x1: rect(x0, 0, x1, h)
    bar = lambda x0, x1, yc: rect(x0, yc - h / 2, x1, yc + h / 2)
    stem = lambda x0, t=S: rect(x0, 0, x0 + t, H)

    # I H
    G['I'] = Gl(stem(0), sides='SS')
    G['H'] = Gl(U(stem(0), stem(W - S), bar(S - 1, W - S + 1, Bm)), sides='SS')
    # E F L T
    Ew = S + round(0.64 * CT); Em = S + round(0.54 * CT)
    e = U(stem(0), top(0, Ew), bot(0, Ew), bar(0, Em, Bm))
    G['E'] = Gl(rcorner(rcorner(e, 0, 0, rr, 'bl'), 0, H, rr, 'tl'), sides='SO')
    f = U(stem(0), top(0, Ew), bar(0, Em, Bm))
    G['F'] = Gl(rcorner(f, 0, H, rr, 'tl'), sides='SO')
    Lw = S + round(0.58 * CT)
    G['L'] = Gl(rcorner(U(stem(0), bot(0, Lw)), 0, 0, rr, 'bl'), sides='SO')
    Tw = W + round(0.04 * H)
    G['T'] = Gl(U(stem((Tw - S) / 2), top(0, Tw)), sides='OO')

    # A (délié à gauche, plein à droite, barre haute) ; V = A tourné
    def aframe(Aw):
        wR = dS
        for _ in range(8): wR = hw(dS, (Aw - wR) / 2, H)
        xap = (Aw - wR) / 2; wL = hw(h, xap, H)
        right = diag(Aw - wR, xap, wR, 0, H); left = diag(0, xap, wL, 0, H)
        hull = poly([(0, 0), (Aw, 0), (xap + wR, H), (xap, H)])
        return U(right, left), hull, wR, wL
    Aw = W + round(0.08 * H)
    fr, hull, wR, wL = aframe(Aw)
    ya = round(0.60 * H) if not c.sc else round(0.58 * H)
    G['A'] = Gl(U(fr, I(bar(0, Aw, ya), hull)), 0, Aw, sides='DD')
    G['V'] = Gl(rot(fr, 180, Aw / 2, H / 2), 0, Aw, sides='DD')
    Vn = round(0.80 * Aw); frn, _, wRn, wLn = aframe(Vn); vn = rot(frn, 180, Vn / 2, H / 2)
    sh = Vn - wLn
    G['W'] = Gl(U(vn, mv(vn, sh)), 0, Vn + sh, sides='DD')

    # M : fût délié, oblique pleine, oblique déliée, fût plein
    Mw = W + round(0.24 * H)
    xv = (Mw - S) / 2 - S / 2
    wD = dS
    for _ in range(8):
        xv = Mw / 2 - wD / 2; wD = hw(dS, xv, H)
    wt = h
    for _ in range(8): wt = hw(h, Mw - S - xv - wD, H)
    m = U(stem(0, h), diag(xv, 0, wD, 0, H), diag(xv + wD - wt, Mw - S - wt, wt, 0, H), stem(Mw - S))
    G['M'] = Gl(m, 0, Mw, sides='SS')
    # N : fûts déliés, oblique pleine
    Nw = W + round(0.04 * H); wN = dS
    for _ in range(8): wN = hw(dS, Nw - wN, H)
    G['N'] = Gl(U(stem(0, h), stem(Nw - h, h), diag(Nw - wN, 0, wN, 0, H)), 0, Nw, sides='SS')
    # X
    Xw = Aw; wX = dS
    for _ in range(8): wX = hw(dS, Xw - wX, H)
    wx = hw(h, Xw - h, H)
    G['X'] = Gl(U(diag(Xw - wX, 0, wX, 0, H), diag(0, Xw - wx, wx, 0, H)), 0, Xw, sides='DD')
    # Y : bras plein à gauche, délié à droite, fût
    Yw = Aw; cx = Yw / 2; yj = round(0.42 * H)
    wY = hw(dS, cx - S / 2, H - yj); wy = hw(h, Yw - cx - S / 2, H - yj)
    armL = diag(cx - S / 2, 0, wY, yj, H); armR = diag(cx + S / 2 - wy, Yw - wy, wy, yj, H)
    armL = I(armL, half((cx + S / 2, yj), (Yw, H), 1))
    G['Y'] = Gl(U(armL, armR, rect(cx - S / 2, 0, cx + S / 2, yj + 1)), 0, Yw, sides='DD')
    # Z : barres déliées, oblique pleine
    Zw = round(0.94 * W); wZ = dS
    for _ in range(8): wZ = hw(dS, Zw - wZ, H)
    G['Z'] = Gl(U(top(0, Zw), bot(0, Zw), diag(0, Zw - wZ, wZ, 0, H)), 0, Zw, sides='OO')
    # K : fût, bras délié, jambe pleine posée sur le bras
    Kw = round(0.96 * W + 0.03 * H); ya_ = round(0.30 * H)
    wa = h
    for _ in range(8): wa = hw(h, Kw - wa - (S - wa), H - ya_)
    xa0 = S - wa; armK = diag(xa0, Kw - wa, wa, ya_, H)
    f_ = 0.42; qx = xa0 + wa / 2 + f_ * (Kw - wa - xa0); qy = ya_ + f_ * (H - ya_)
    wl = dS
    for _ in range(8): wl = hw(dS, (Kw - wl / 2) - qx, qy)
    # axe de la jambe : de (Kw - wl/2, 0) à (qx, qy), prolongé jusqu'en haut puis coupé sous le bras
    slope = ((Kw - wl / 2) - qx) / qy; xt = (Kw - wl / 2) - slope * H - wl / 2
    leg = I(diag(Kw - wl, xt, wl, 0, H), half((xa0, ya_), (Kw - wa, H), -1))
    G['K'] = Gl(U(stem(0), armK, leg), 0, Kw, sides='SD')

    # ronds au compas : plein à gauche
    R = H / 2 + ov; cy = H / 2
    O = ring_off(R, cy, R, SO, h, -1)
    G['O'] = Gl(O, 0, 2 * R, sides='OO')
    xq = R + 0.20 * R; wq = hw(dS, 0.42 * R, 0.24 * H + 0.10 * H)
    tail = diag(xq + 0.30 * R, xq, wq, round(-0.12 * H), round(0.20 * H))
    tail = D(tail, D(circ(R, cy, R), O))            # la queue part de l'anneau, pas de la contre-forme
    G['Q'] = Gl(U(O, tail), 0, 2 * R, sides='OO')
    ac = 40                                          # bouts du C coupés dans l'axe du compas (angle droit, pas de pointe)
    Cc = D(O, sector(R, cy, -ac, ac))
    G['C'] = Gl(Cc, 0, bounds(Cc)[2], sides='OO')
    gb = D(O, sector(R, cy, 0, ac))
    spur = I(rect(2 * R - S, -100, 2 * R, cy), circ(R, cy, R))
    gbar = rect(R + 0.10 * R, cy - h, 2 * R - 1, cy)
    G['G'] = Gl(U(gb, spur, gbar), 0, 2 * R, sides='OO')

    # demi-anneaux à droite (D B P R) : plein à droite, déliés en haut et en bas
    def bowl(xc, y0, y1, t=S):
        r = (y1 - y0) / 2; yc = (y0 + y1) / 2
        return I(D(circ(xc, yc, r), ell(xc, yc, r - t, r - h)), rect(xc, y0 - 50, xc + r + 50, y1 + 50))
    # D
    rD = H / 2; xd = S + round(0.36 * CT)
    d = U(stem(0), top(0, xd + 1), bot(0, xd + 1), bowl(xd, 0, H, round(0.64 * S + 0.3 * h)))
    G['D'] = Gl(rcorner(rcorner(d, 0, 0, rr, 'bl'), 0, H, rr, 'tl'), 0, xd + rD, sides='SO')
    # B : panse haute plus petite
    ym = round(0.57 * H); Bw = round(0.98 * W)
    rL = (ym + h / 2) / 2; xl = Bw - rL
    rU = (H - (ym - h / 2)) / 2; xu = Bw - round(0.05 * H) - rU
    b = U(stem(0), top(0, xu + 1), bar(0, max(xu, xl) + 1, ym), bot(0, xl + 1), bowl(xu, ym - h / 2, H), bowl(xl, 0, ym + h / 2))
    G['B'] = Gl(rcorner(rcorner(b, 0, 0, rr, 'bl'), 0, H, rr, 'tl'), 0, Bw, sides='SO')
    # P
    yp = round(0.40 * H); Pw = round(0.96 * W); rP = (H - yp) / 2; xp = Pw - rP
    p = U(stem(0), top(0, xp + 1), rect(0, yp, xp + 1, yp + h), bowl(xp, yp, H))
    G['P'] = Gl(rcorner(p, 0, H, rr, 'tl'), 0, Pw, sides='SO')
    # R : panse haute, jambe pleine
    yr = Bm - h / 2; rR = (H - yr) / 2; Rw = round(0.98 * W); xr = Rw - rR - round(0.03 * H)
    wl = dS
    for _ in range(8): wl = hw(dS, Rw - xr, yr + h)
    leg = diag(Rw - wl, xr - wl, wl, 0, yr + h)
    r_ = U(stem(0), top(0, xr + 1), rect(0, yr, xr + 1, yr + h), bowl(xr, yr, H), leg)
    G['R'] = Gl(rcorner(r_, 0, H, rr, 'tl'), 0, Rw, sides='SD')

    # U : fût plein, fût délié, cuvette au compas
    Uw = W + round(0.03 * H); ru = Uw / 2; cu = ru - ov
    cup = I(ring_off(ru, cu, ru, S, h, -1), rect(-50, -200, Uw + 50, cu))
    G['U'] = Gl(U(rect(0, cu - 1, S, H), rect(Uw - h, cu - 1, Uw, H), cup), 0, Uw, sides='SS')
    # J : fût plein, crochet au compas
    Jw = round(0.78 * W); rj = Jw / 2; cj = rj - ov
    hook = I(ring_off(rj, cj, rj, S, h, 1), rect(-50, -200, Jw + 50, cj))
    G['J'] = Gl(U(rect(Jw - S, cj - 1, Jw, H), hook), 0, Jw, sides='OS')

    # S : panse haute à gauche, panse basse à droite, filets
    Sw = round(0.96 * W); tot = (H + h) / 2; r1 = round(0.46 * tot); r2 = tot - r1
    cxu, cyu = r1, H - r1; cxl, cyl = Sw - r2, r2
    up = I(D(circ(cxu, cyu, r1), ell(cxu, cyu, r1 - SO, r1 - h)), rect(-50, -50, cxu, H + 50))
    lo = I(D(circ(cxl, cyl, r2), ell(cxl, cyl, r2 - SO, r2 - h)), rect(cxl, -50, Sw + 50, H + 50))
    mid = rect(cxu - 1, H - 2 * r1, cxl + 1, H - 2 * r1 + h)
    xt_ = cxl + round(0.62 * r2); xb_ = cxu - round(0.62 * r1)
    tt = round(0.88 * S); th_ = round(0.42 * r1)
    s = U(up, lo, mid, top(cxu - 1, xt_), bot(xb_, cxl + 1), rect(xt_ - tt, H - th_, xt_, H), rect(xb_, 0, xb_ + tt, th_))
    G['S'] = Gl(s, 0, Sw, sides='OO')
    return G
