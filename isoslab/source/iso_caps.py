# ISOSLAB : capitales et étoile
import math
from iso_core import *

def build(w):
    ST, TH, SL, SX, R, CW, BK, W = w.ST, w.TH, w.SL, w.SX, w.R, w.CW, w.BK, w.W
    G = {}

    # ---------- briques ----------
    def slab(sx0, sx1, top=False, left=True, right=True):
        y0, y1 = (CAP - SL, CAP) if top else (0, SL)
        p = rect(sx0 - (SX if left else 0), y0, sx1 + (SX if right else 0), y1)
        yq = y0 if top else y1; up = (0, -1) if top else (0, 1)
        if left: p = U(p, wedge((sx0, yq), up, (-1, 0), R))
        if right: p = U(p, wedge((sx1, yq), up, (1, 0), R))
        return p
    def stem(x0, w_=None, y0=0, y1=CAP): return rect(x0, y0, x0 + (w_ or ST), y1)
    def beak(xe, y, down, h=BK, side=-1):
        """bec vertical au bout d'un bras ; y = bord du bras côté bec ; side=-1 : le bec est à gauche de xe"""
        bw = round(SL * 0.85)
        x0, x1 = (xe - bw, xe) if side < 0 else (xe, xe + bw)
        xi = x0 if side < 0 else x1
        if down: return U(rect(x0, y - h, x1, y + 1), wedge((xi, y), (0, -1), (side, 0), R))
        return U(rect(x0, y - 1, x1, y + h), wedge((xi, y), (0, 1), (side, 0), R))
    class Diag:
        """trait oblique de largeur w (perpendiculaire), axe de (xb, y0) à (xt, y1), bouts horizontaux"""
        def __init__(d, xb, xt, w_, y0=0, y1=CAP):
            d.xb, d.xt, d.y0, d.y1 = xb, xt, y0, y1
            L = math.hypot(xt - xb, y1 - y0); d.hw = w_ * L / (y1 - y0); d.u = unit((xt - xb, y1 - y0))
            d.path = I(pbar((xb - (xt - xb) * 0.2, y0 - (y1 - y0) * 0.2), (xt + (xt - xb) * 0.2, y1 + (y1 - y0) * 0.2), w_),
                       rect(-2000, y0, 4000, y1))
        def x(d, y): return d.xb + (d.xt - d.xb) * (y - d.y0) / (d.y1 - d.y0)
        def slab(d, top=False, left=True, right=True, k=0.8):
            y = d.y1 if top else d.y0; sx = SX * k
            yy0, yy1 = (y - SL, y) if top else (y, y + SL)
            yq_ = yy1 if not top else yy0; yo_ = yy0 if not top else yy1      # face qui touche le trait / face extérieure
            lean = d.x(yq_) - d.x(yo_)                                         # >0 : le trait penche vers la droite
            xl = min(d.x(yq_) - d.hw / 2 - (sx * 0.45 if lean < 0 else sx), d.x(yo_) - d.hw / 2 - 0.45 * sx)
            xr = max(d.x(yq_) + d.hw / 2 + (sx * 0.45 if lean > 0 else sx), d.x(yo_) + d.hw / 2 + 0.45 * sx)
            if not left: xl = min(d.x(yq_), d.x(yo_)) - d.hw / 2
            if not right: xr = max(d.x(yq_), d.x(yo_)) + d.hw / 2
            p = rect(xl, yy0, xr, yy1)
            yq = yy0 if top else yy1; u = (-d.u[0], -d.u[1]) if top else d.u
            xq = d.x(yq)
            # congé seulement du côté ouvert : du côté aigu, il ferait une bulle
            if left and u[0] > -0.05: p = U(p, wedge((xq - d.hw / 2, yq), u, (-1, 0), R))
            if right and u[0] < 0.05: p = U(p, wedge((xq + d.hw / 2, yq), u, (1, 0), R))
            return p
        def edge(d, side):
            """bord gauche (side=-1) ou droit (+1) : deux points"""
            return ((d.x(d.y0) + side * d.hw / 2, d.y0), (d.x(d.y1) + side * d.hw / 2, d.y1))
    GMIN = round(0.30 * CW)
    def sep(p1, p2):
        """deux empattements voisins (p1 à gauche, p2 à droite) : jamais moins de GMIN de jour entre eux"""
        b1, b2 = p1.bounds, p2.bounds
        if b2[0] - b1[2] >= GMIN: return p1, p2
        mid = (b1[2] + b2[0]) / 2
        return I(p1, rect(-3000, -3000, mid - GMIN / 2, 3000)), I(p2, rect(mid + GMIN / 2, -3000, 6000, 3000))
    def bowl(x0, x1, y0, y1):
        h = (y1 - y0) / 2; r = min(h * 0.95, (x1 - x0 - ST) * 0.9); xm_ = x1 - r
        out = U(rect(x0, y0, xm_ + 1, y1), I(superell(xm_, y0 + h, r, h, 2.6), rect(xm_, y0 - 1, x1 + 1, y1 + 1)))
        ins = U(rect(x0 + ST, y0 + TH, xm_ + 1, y1 - TH), I(superell(xm_, y0 + h, r - ST, h - TH, 2.6), rect(xm_, y0, x1, y1)))
        return D(out, ins)

    def grave(cx, base):
        """accent grave : trait penché, assez long pour ne jamais tourner au losange"""
        L = 150 + 0.55 * ST; t = ST * 0.72; d = unit((-0.55, 1.0))
        p0 = (cx + 0.30 * L * 0.55 + 10, base + 70); p1 = (p0[0] + d[0] * L, p0[1] + d[1] * L)
        return pbar(p0, p1, t)
    G['_grave'] = grave
    # ---------- droites ----------
    G['I'] = U(stem(0), slab(0, ST), slab(0, ST, top=True))
    G['H'] = U(stem(0), stem(W - ST), rect(0, CAP * 0.5 - TH / 2, W, CAP * 0.5 + TH / 2),
               slab(0, ST), slab(0, ST, top=True), slab(W - ST, W), slab(W - ST, W, top=True))
    Tw = W + 2 * SX; xs = Tw / 2 - ST / 2
    G['T'] = U(rect(0, CAP - TH, Tw, CAP), beak(Tw, CAP - TH, True), beak(0, CAP - TH, True, side=1),
               stem(xs), slab(xs, xs + ST))
    xe = W - 10; ym = CAP * 0.5
    # place libre entre un bras du haut (ou du bas) et la barre du milieu : un bec est franc ou absent, jamais un moignon
    room = CAP / 2 - 1.5 * TH - 0.35 * CW
    BKE = BK if room >= BK else (round(room) if room >= 0.45 * BK else 0)
    emid = round(0.18 * TH + 12) if room - BKE >= round(0.18 * TH + 12) + 10 else 0
    def mid_arm(xa):
        p = rect(0, ym - TH / 2, xa, ym + TH / 2)
        if emid: p = U(p, rect(xa - round(SL * 0.42), ym - TH / 2 - emid, xa, ym + TH / 2 + emid))
        return p
    def beakE(xe, y, down):
        return beak(xe, y, down, h=BKE) if BKE else None
    G['E'] = U(stem(0), slab(0, ST, right=False), slab(0, ST, top=True, right=False),
               rect(0, CAP - TH, xe, CAP), beakE(xe, CAP - TH, True), rect(0, 0, xe + 12, TH), beakE(xe + 12, TH, False),
               mid_arm(xe - 45))
    G['F'] = U(stem(0), slab(0, ST), slab(0, ST, top=True, right=False),
               rect(0, CAP - TH, xe, CAP), beakE(xe, CAP - TH, True), mid_arm(xe - 55))
    G['L'] = U(stem(0), slab(0, ST, top=True), slab(0, ST, right=False), rect(0, 0, xe, TH), beak(xe, TH, False, h=BK * 1.1))
    # ---------- ronds ----------
    a, b = W / 2 + 10, CAP / 2 + OV
    ring = D(superell(a, CAP / 2, a, b), superell(a, CAP / 2, a - ST, b - TH))
    G['O'] = ring
    yt = min(0.56 * b, 0.86 * (b - TH))                 # hauteur des bouts coupés (C, G)
    xcut = min(a + se_x(a - ST, b - TH, yt), 2 * a - ST) - 0.5
    G['C'] = D(ring, rect(xcut, CAP / 2 - yt, 2 * a + 10, CAP / 2 + yt))
    yg = CAP / 2 - 0.04 * b
    G['G'] = U(D(ring, rect(xcut, yg, 2 * a + 10, CAP / 2 + yt)), rect(a + 0.10 * a, yg - TH, 2 * a + SX * 0.4, yg))
    tail = I(pbar((a * 0.62, 220), (2 * a + 0.02 * a, -165), ST * 0.95), rect(-10, -165, 2 * a + 0.02 * a, 2 * TH))   # la queue reste sous la lettre
    G['Q'] = U(ring, D(tail, superell(a, CAP / 2, a - ST, b - TH)))     # la queue ne mord pas dans le blanc
    Dw = W + 20
    G['D'] = U(bowl(0, Dw, 0, CAP), slab(0, ST, right=False), slab(0, ST, top=True, right=False))
    yb = round(CAP * 0.53)
    G['B'] = U(bowl(0, Dw - 28, yb - TH, CAP), bowl(0, Dw, 0, yb), slab(0, ST, right=False), slab(0, ST, top=True, right=False))
    yp = round(CAP * 0.42)
    G['P'] = U(stem(0), bowl(0, Dw - 10, yp - TH, CAP), slab(0, ST), slab(0, ST, top=True, right=False))
    yr = round(CAP * 0.47); xr1 = Dw - 20; xf = xr1 + 25 - ST * 0.5
    leg = I(pbar((ST + (xr1 - ST) * 0.42, yr - TH * 0.5), (xf, SL * 0.5), ST * 1.0), rect(ST, 0, Dw + 60, yr))
    G['R'] = U(bowl(0, xr1, yr - TH, CAP), stem(0), leg, slab(0, ST), slab(0, ST, top=True, right=False),
               rect(xf - ST * 0.5 - SX * 0.55, 0, xf + ST * 0.5 + SX * 0.65, SL))
    # U : deux fûts et une cuvette
    Uw = W; yu = round(0.36 * CAP); ua, ub = Uw / 2, yu + OV
    cupo = I(superell(ua, yu, ua, ub, 2.6), rect(-1, -OV - 1, Uw + 1, yu))
    cupi = I(superell(ua, yu, ua - ST, ub - TH, 2.6), rect(ST, -OV, Uw - ST, yu + 1))
    G['U'] = U(D(U(cupo, stem(0, y0=yu - 1), stem(Uw - ST, y0=yu - 1)), cupi),
               slab(0, ST, top=True), slab(Uw - ST, Uw, top=True))
    # J : fût à droite, crochet coupé à plat à gauche
    Jw = round(W * 0.82); ja = Jw / 2; yj = round(0.34 * CAP); jb = yj + OV
    hooko = I(superell(ja, yj, ja, jb, 2.6), rect(-1, -OV - 1, Jw + 1, yj))
    hooki = I(superell(ja, yj, ja - ST, jb - TH, 2.6), rect(ST, -OV, Jw - ST, yj + 1))
    hook = D(U(hooko, stem(Jw - ST, y0=yj - 1)), hooki)
    ycj = yj - 0.10 * jb
    hook = D(hook, rect(-10, ycj, ja, CAP + 10))          # bout gauche coupé à plat
    G['J'] = U(hook, slab(Jw - ST, Jw, top=True, right=True))
    # S : deux ronds superposés qui partagent l'épine
    Ht = CAP + 2 * OV + TH; bu = 0.47 * Ht / 2; bl = Ht / 2 - bu
    cu = CAP + OV - bu; cl = -OV + bl
    sa = a - 4
    ru = D(superell(sa, cu, sa - 6, bu), superell(sa, cu, sa - 6 - ST, bu - TH))
    rl = D(superell(sa, cl, sa, bl), superell(sa, cl, sa - ST, bl - TH))
    ytu = min(0.30 * bu, 0.5 * (bu - TH)); ytl = min(0.30 * bl, 0.5 * (bl - TH))
    xcu = min(sa + se_x(sa - 6 - ST, bu - TH, ytu), 2 * sa - 6 - ST) - 0.5
    xcl = max(sa - se_x(sa - ST, bl - TH, ytl), ST) + 0.5
    ru = D(ru, rect(sa, -100, 3 * sa, cu), rect(xcu, cu - 1, 3 * sa, cu + ytu))
    rl = D(rl, rect(-100, cl, sa, CAP + 100), rect(-100, cl - ytl, xcl, cl + 1))
    G['S'] = U(ru, rl)
    # ---------- obliques ----------
    def apex_pair(width, tw, wl, wr, inverted=False):
        """deux jambes : pointe aplatie de largeur tw en haut (A) ou en bas (V)"""
        cx = width / 2; m = SX * 0.8
        hl, hr = wl, wr
        for _ in range(3):
            if not inverted:
                L_ = Diag(m + hl / 2, cx - tw / 2 + hl / 2, wl); Rr = Diag(width - m - hr / 2, cx + tw / 2 - hr / 2, wr)
            else:
                L_ = Diag(cx - tw / 2 + hl / 2, m + hl / 2, wl); Rr = Diag(cx + tw / 2 - hr / 2, width - m - hr / 2, wr)
            hl, hr = L_.hw, Rr.hw
        return L_, Rr
    Aw = W + 2 * SX + round(0.9 * CW + 0.9 * ST)
    L_, Rr = apex_pair(Aw, ST * 0.7, ST * 0.80, ST * 1.0)
    yc = round(CAP * 0.25)
    il = lambda y: L_.x(y) + L_.hw / 2 - 3; ir = lambda y: Rr.x(y) - Rr.hw / 2 + 3      # bords intérieurs (+ recouvrement)
    bar = poly([(il(yc), yc), (ir(yc), yc), (ir(yc + TH), yc + TH), (il(yc + TH), yc + TH)])
    (pl0, pl1), (pr0, pr1) = L_.edge(-1), Rr.edge(1)
    outer = poly([pl0, pl1, pr1, pr0])
    A = U(I(U(L_.path, Rr.path, rect(pl1[0], CAP - 2, pr1[0], CAP)), outer),
          bar, L_.slab(), Rr.slab())
    G['A'] = A
    G['Agrave'] = U(A, grave(Aw / 2, CAP))
    Vw = W + 2 * SX + round(0.6 * CW)
    L_, Rr = apex_pair(Vw, ST * 0.6, ST * 1.0, ST * 0.80, inverted=True)
    (pl0, pl1), (pr0, pr1) = L_.edge(-1), Rr.edge(1)
    G['V'] = U(I(U(L_.path, Rr.path, rect(pl0[0], 0, pr0[0], 2)), poly([pl0, pl1, pr1, pr0])),
               *sep(L_.slab(top=True), Rr.slab(top=True)))
    # W : deux V serrés, pointe du milieu à pleine hauteur
    Ww = round(1.55 * W + 2 * SX); m = SX * 0.8; bw = ST * 0.5
    x1b = Ww * 0.30; x2b = Ww * 0.70; xm = Ww / 2
    s1 = Diag(x1b - bw / 2, m + ST * 0.55, ST * 0.95); s2 = Diag(x1b + bw / 2, xm - ST * 0.2, ST * 0.72)
    s3 = Diag(x2b - bw / 2, xm + ST * 0.2, ST * 0.95); s4 = Diag(x2b + bw / 2, Ww - m - ST * 0.42, ST * 0.72)
    G['W'] = U(s1.path, s2.path, s3.path, s4.path, s1.slab(top=True), s4.slab(top=True))
    # X
    Xw = W + 2 * SX + round(0.4 * CW + 0.2 * ST); m = SX * 0.8
    d1 = Diag(Xw - m - ST * 0.6, m + ST * 0.6, ST * 1.0)      # du bas droit au haut gauche (plein)
    d2 = Diag(m + ST * 0.45, Xw - m - ST * 0.45, ST * 0.78)    # du bas gauche au haut droit (fin)
    tl, tr = sep(d1.slab(top=True), d2.slab(top=True)); bl_, br_ = sep(d2.slab(), d1.slab())
    G['X'] = U(d1.path, d2.path, tl, tr, bl_, br_)
    # Y
    Yw = W + 2 * SX + round(0.45 * CW); yy = round(CAP * 0.44); cx = Yw / 2; m = SX * 0.8
    ya = Diag(cx, m + ST * 0.55, ST * 1.0, y0=yy); yb_ = Diag(cx, Yw - m - ST * 0.42, ST * 0.78, y0=yy)
    for _ in range(3):
        ya = Diag(cx - ST / 2 + ya.hw / 2, m + ST * 0.55, ST * 1.0, y0=yy)
        yb_ = Diag(cx + ST / 2 - yb_.hw / 2, Yw - m - ST * 0.42, ST * 0.78, y0=yy)
    (q0, q1), (r0, r1) = ya.edge(-1), yb_.edge(1)
    arms = I(U(ya.path, yb_.path), poly([(cx - ST / 2, yy), q1, r1, (cx + ST / 2, yy)]))   # rien ne dépasse du fût
    G['Y'] = U(arms, stem(cx - ST / 2, y1=yy + 1), slab(cx - ST / 2, cx + ST / 2),
               *sep(ya.slab(top=True), yb_.slab(top=True)))
    # K
    Kw = W + SX + round(0.4 * ST); yk = round(CAP * 0.36)
    xt_ = Kw - ST * 0.42; yj = round(0.30 * CAP); hwa = ST * 0.78
    for _ in range(4):        # le bord bas du bras touche le fût à la hauteur yj
        xc_ = ST - hwa / 2; t_ = (CAP - yj) / (xt_ - xc_)
        arm = Diag(xc_ - (yj - 10) / t_ * 0 - 10 / t_, xt_, ST * 0.78, y0=yj - 10); hwa = arm.hw
    legk = Diag(Kw - ST * 0.55, ST + (Kw - ST) * 0.28, ST * 1.0, y1=yk + 200)
    a0, a1 = arm.edge(-1)                               # bord haut-gauche du bras
    under = poly([a0, a1, (a1[0] + 3000, a1[1]), (a0[0] + 3000, a0[1] - 3000)])
    st_b, lg_b = sep(slab(0, ST), legk.slab()); st_t, ar_t = sep(slab(0, ST, top=True), arm.slab(top=True))
    G['K'] = U(stem(0), I(arm.path, rect(ST - 5, 0, Kw + 200, CAP)), I(I(legk.path, under), rect(ST - 5, 0, Kw + 200, CAP)),
               st_b, lg_b, st_t, ar_t)
    # N, M
    Nw = W + 10; tn = round(ST * 0.78)
    diag = I(poly([(0, CAP), (ST * 1.15, CAP), (Nw, 0), (Nw - ST * 1.15, 0)]), rect(0, 0, Nw, CAP))
    G['N'] = U(stem(0, tn), stem(Nw - tn, tn), diag, slab(0, tn), slab(0, tn, top=True, right=False), slab(Nw - tn, Nw, top=True))
    Mw = W + CW * 0.55 + ST * 0.6; tm = round(ST * 0.80); mc = Mw / 2
    v1 = poly([(0, CAP), (ST * 1.05, CAP), (mc + ST * 0.5, 0), (mc - ST * 0.55, 0)])
    v2 = poly([(Mw, CAP), (Mw - ST * 0.85, CAP), (mc - ST * 0.40, 0), (mc + ST * 0.45, 0)])
    vout = poly([(0, CAP), (mc - ST * 0.55, 0), (mc + ST * 0.45, 0), (Mw, CAP)])          # contour net : rien ne dépasse au pied du V
    G['M'] = U(stem(0, tm), stem(Mw - tm, tm), I(I(U(v1, v2), rect(0, 0, Mw, CAP)), vout), slab(0, tm), slab(Mw - tm, Mw),
               slab(0, tm, top=True, right=False), slab(Mw - tm, Mw, top=True, left=False))
    # Z
    Zw = W + SX
    zd = I(pbar((ST * 0.3, TH * 0.5), (Zw - ST * 0.3, CAP - TH * 0.5), ST * 1.0), rect(0, TH - 2, Zw, CAP - TH + 2))
    zd = I(poly([(0, TH), (Zw - ST * 1.25, TH), (Zw, CAP - TH), (ST * 1.25, CAP - TH)]), rect(0, 0, Zw, CAP))
    zd = I(poly([(0, TH), (ST * 1.25, TH), (Zw, CAP - TH), (Zw - ST * 1.25, CAP - TH)]), rect(0, 0, Zw, CAP))
    G['Z'] = U(rect(10, CAP - TH, Zw, CAP), beak(10, CAP - TH, True, side=1), zd,
               rect(0, 0, Zw - 10, TH), beak(Zw - 10, TH, False))
    # ★ : pointes vives, creux arrondis (comme le raccord d'un empattement)
    Ro = 375; cy = CAP / 2 - 45; k = 0.40 + 0.0004 * ST; pts = []
    for i in range(10):
        an = math.radians(90 + 36 * i); r = Ro if i % 2 == 0 else Ro * k
        pts.append((r * math.cos(an), cy + r * math.sin(an)))
    st_ = poly(pts); rr = round(0.55 * ST + 14)
    for i in range(1, 10, 2):
        Q = pts[i]; A_ = pts[i - 1]; B_ = pts[(i + 1) % 10]
        st_ = U(st_, wedge(Q, (A_[0] - Q[0], A_[1] - Q[1]), (B_[0] - Q[0], B_[1] - Q[1]), rr))
    G['star'] = st_
    return G
