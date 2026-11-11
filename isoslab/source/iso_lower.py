# ISOSLAB : minuscules. Même famille que les capitales : fûts presque monolignes, empattements carrés raccordés,
# panses en "D" côté fût (aucune dent à la jonction), gouttes au bout du a c r f j g.
import math
from iso_core import *

XH, ASC, DESC, OVL = 500, 760, -210, 10

def rrect(x0, y0, x1, y1, tl=0, tr=0, br=0, bl=0, n=2.5, N=None):
    """rectangle aux coins arrondis en quart de superellipse, chaque coin en une vraie courbe (rayon 0 = coin vif)"""
    m = min(x1 - x0, y1 - y0) / 2
    tl, tr, br, bl = (min(r, m) for r in (tl, tr, br, bl))
    k = se_k(n); p = P(); pen = p.getPen(); started = [False]
    def go(pt):
        if not started[0]: pen.moveTo(pt); started[0] = True
        else: pen.lineTo(pt)
    def corner(cx, cy, r, a0):
        if r <= 0: return
        t0 = math.radians(a0); t1 = math.radians(a0 + 90)
        s0 = (cx + r * math.cos(t0), cy + r * math.sin(t0)); e = (cx + r * math.cos(t1), cy + r * math.sin(t1))
        d0 = (-math.sin(t0), math.cos(t0)); d1 = (-math.sin(t1), math.cos(t1))
        go(s0); pen.curveTo((s0[0] + k * r * d0[0], s0[1] + k * r * d0[1]), (e[0] - k * r * d1[0], e[1] - k * r * d1[1]), e)
    if bl > 0: corner(x0 + bl, y0 + bl, bl, 180)
    else: go((x0, y0))
    if br > 0: corner(x1 - br, y0 + br, br, 270)
    else: go((x1, y0))
    if tr > 0: corner(x1 - tr, y1 - tr, tr, 0)
    else: go((x1, y1))
    if tl > 0: corner(x0 + tl, y1 - tl, tl, 90)
    else: go((x0, y1))
    pen.closePath(); return p

def build_lower(w):
    ST, TH = w.ST, w.TH
    SL = round(0.78 * w.SL); SX = round(0.85 * w.SX); R = round(0.45 * SX)
    CW = round(0.80 * w.CW); nw = 2 * ST + CW
    rA = round(0.50 * nw); riA = max(round(0.30 * CW), rA - ST); rs = round(0.22 * CW)
    rb = round(0.45 * ST + 20)                      # goutte
    GMIN = round(0.30 * CW)
    G = {}

    def stem(x0, y0, y1, w_=None): return rect(x0, y0, x0 + (w_ or ST), y1)
    def slab(sx0, sx1, y=0, top=False, left=True, right=True):
        y0, y1 = (y - SL, y) if top else (y, y + SL)
        p = rect(sx0 - (SX if left else 0), y0, sx1 + (SX if right else 0), y1)
        yq = y0 if top else y1; up = (0, -1) if top else (0, 1)
        if left: p = U(p, wedge((sx0, yq), up, (-1, 0), R))
        if right: p = U(p, wedge((sx1, yq), up, (1, 0), R))
        return p
    def sep(p1, p2):
        b1, b2 = p1.bounds, p2.bounds
        if b2[0] - b1[2] >= GMIN: return p1, p2
        mid = (b1[2] + b2[0]) / 2
        return I(p1, rect(-3000, -3000, mid - GMIN / 2, 3000)), I(p2, rect(mid + GMIN / 2, -3000, 6000, 3000))
    def ball(x, y, r=None): r = r or rb; return superell(x, y, r, r, 2.0, 120)
    def beak(xe, y, up=True, h=None, side=-1):
        h = h or round(0.13 * XH); bw = round(SL * 0.80)
        x0, x1 = (xe - bw, xe) if side < 0 else (xe, xe + bw); xi = x0 if side < 0 else x1
        if up: return U(rect(x0, y - 1, x1, y + h), wedge((xi, y), (0, 1), (side, 0), R))
        return U(rect(x0, y - h, x1, y + 1), wedge((xi, y), (0, -1), (side, 0), R))
    class Diag:
        def __init__(d, xb, xt, w_, y0=0, y1=XH):
            d.xb, d.xt, d.y0, d.y1 = xb, xt, y0, y1
            L = math.hypot(xt - xb, y1 - y0); d.hw = w_ * L / (y1 - y0); d.u = unit((xt - xb, y1 - y0))
            d.path = I(pbar((xb - (xt - xb) * 0.3, y0 - (y1 - y0) * 0.3), (xt + (xt - xb) * 0.3, y1 + (y1 - y0) * 0.3), w_),
                       rect(-3000, y0, 4000, y1))
        def x(d, y): return d.xb + (d.xt - d.xb) * (y - d.y0) / (d.y1 - d.y0)
        def edge(d, side): return ((d.x(d.y0) + side * d.hw / 2, d.y0), (d.x(d.y1) + side * d.hw / 2, d.y1))
        def slab(d, top=False, left=True, right=True, k=0.8):
            sx = SX * k; y = d.y1 if top else d.y0
            yy0, yy1 = (y - SL, y) if top else (y, y + SL)
            yq_, yo_ = (yy0, yy1) if top else (yy1, yy0)
            lean = d.x(yq_) - d.x(yo_)
            xl = min(d.x(yq_) - d.hw / 2 - (sx * 0.45 if lean < 0 else sx), d.x(yo_) - d.hw / 2 - 0.45 * sx)
            xr = max(d.x(yq_) + d.hw / 2 + (sx * 0.45 if lean > 0 else sx), d.x(yo_) + d.hw / 2 + 0.45 * sx)
            if not left: xl = min(d.x(yq_), d.x(yo_)) - d.hw / 2
            if not right: xr = max(d.x(yq_), d.x(yo_)) + d.hw / 2
            p = rect(xl, yy0, xr, yy1); u = (-d.u[0], -d.u[1]) if top else d.u; xq = d.x(yq_)
            if left and u[0] > -0.05: p = U(p, wedge((xq - d.hw / 2, yq_), u, (-1, 0), R))
            if right and u[0] < 0.05: p = U(p, wedge((xq + d.hw / 2, yq_), u, (1, 0), R))
            return p
    def drop(cx, cy, r, P, pick):
        """goutte en larme : le rond + une tangente qui le raccorde au point P du bord intérieur du trait.
        pick choisit la tangente : 'minx', 'maxx' ou 'maxy'"""
        dx, dy = P[0] - cx, P[1] - cy; d = math.hypot(dx, dy)
        circ = superell(cx, cy, r, r, 2.0, 120)
        if d <= r * 1.02: return circ
        if pick in ('minx', 'maxx') and dy < 0.9 * r: return circ          # la goutte couvre déjà le trait : pas de tangente (sinon pointe)
        if pick == 'maxy' and dx < 0.9 * r: return circ
        base = math.atan2(dy, dx); a_ = math.acos(r / d)
        T = [(cx + r * math.cos(base + s_ * a_), cy + r * math.sin(base + s_ * a_)) for s_ in (1, -1)]
        k = {'minx': lambda t: t[0], 'maxx': lambda t: -t[0], 'maxy': lambda t: -t[1]}[pick]
        T = min(T, key=k)
        return U(circ, poly([P, T, (cx, cy)]))
    def dot(cx):
        dr = round(0.58 * ST + 8); yd = XH + dr + max(55, round(0.40 * ST))
        return superell(cx, yd, dr, dr, 3.0, 120)

    # ---------- n m h u ----------
    def arch(x0, x1, tl=0):
        return D(rrect(x0, 0, x1, XH, tl=tl, tr=round(0.5 * (x1 - x0))),
                 rrect(x0 + ST, -5, x1 - ST, XH - TH, tl=rs, tr=max(round(0.30 * (x1 - x0 - 2 * ST)), round(0.5 * (x1 - x0)) - ST)))
    def feet(*xs):
        ps = [slab(x, x + ST) for x in xs]
        for i in range(len(ps) - 1): ps[i], ps[i + 1] = sep(ps[i], ps[i + 1])
        return ps
    G['n'] = U(arch(0, nw), slab(0, ST, XH, top=True, right=False), *feet(0, nw - ST))
    G['h'] = U(arch(0, nw), stem(0, 0, ASC), slab(0, ST, ASC, top=True, right=False), *feet(0, nw - ST))
    CWm = round(0.86 * CW); m1 = 2 * ST + CWm; mw = 3 * ST + 2 * CWm
    G['m'] = U(arch(0, m1), arch(m1 - ST, mw, tl=round(0.18 * m1)), slab(0, ST, XH, top=True, right=False),
               *feet(0, m1 - ST, mw - ST))
    cup = D(rrect(0, 0, nw, XH, bl=rA), rrect(ST, TH, nw - ST, XH + 5, bl=riA, br=rs))
    t1, t2 = sep(slab(0, ST, XH, top=True), slab(nw - ST, nw, XH, top=True, right=False))
    G['u'] = U(cup, t1, t2, slab(nw - ST, nw, 0, left=False))
    # ---------- i j l ----------
    G['i'] = U(stem(0, 0, XH), slab(0, ST, XH, top=True, right=False), slab(0, ST), dot(ST / 2))
    G['l'] = U(stem(0, 0, ASC), slab(0, ST, ASC, top=True, right=False), slab(0, ST))
    hk = round(0.70 * (-DESC)); tht = min(TH, round(0.45 * (-DESC)))       # barre du crochet : jamais plus épaisse que le jambage ne le permet
    rbh = min(rb, round(0.40 * (-DESC)))                                      # goutte du crochet : reste sous la ligne de base
    xj0 = ST - round(0.62 * nw)
    rH = round(0.5 * (ST - xj0)); riH = max(round(0.3 * CW), rH - ST)
    hookj = D(rrect(xj0, DESC, ST, DESC + hk, br=rH), rrect(xj0 - 5, DESC + tht, 0, DESC + hk + 5, br=riH))
    G['j'] = U(stem(0, DESC + hk - 1, XH), hookj, slab(0, ST, XH, top=True, right=False),
               drop(xj0 + rbh, DESC + rbh, rbh, (xj0 + 2.4 * rbh, DESC + tht), 'maxy'), dot(ST / 2))
    # ---------- ronds ----------
    oa = nw / 2 + 2; ob = XH / 2 + OVL; cy = XH / 2
    G['o'] = D(superell(oa, cy, oa, ob), superell(oa, cy, oa - ST, ob - TH))
    ca = nw / 2 - 4; ring = D(superell(ca, cy, ca, ob), superell(ca, cy, ca - ST, ob - TH))
    yt = min(0.50 * ob, 0.80 * (ob - TH))
    xin, xo = ca + se_x(ca - ST, ob - TH, yt), ca + se_x(ca, ob, yt)
    xcut = min(xin, 2 * ca - ST) - 0.5
    rbc = min(rb, round(0.55 * (xo - xin) + 0.12 * CW))
    G['c'] = U(D(ring, rect(xcut, cy - yt, 2 * ca + 10, cy + yt)),
               I(drop(xo - rbc, cy + yt, rbc, (xin - 1, cy + yt + 1.6 * rbc), 'minx'), superell(ca, cy, ca, ob)))   # la goutte ne dépasse pas du rond
    ea = nw / 2 + 2; ring_e = D(superell(ea, cy, ea, ob), superell(ea, cy, ea - ST, ob - TH))
    ybar = cy - TH * 0.35
    xce = min(ea + se_x(ea - ST, ob - TH, yt), 2 * ea - ST) - 0.5
    G['e'] = U(D(ring_e, rect(xce, cy - yt, 2 * ea + 10, ybar)), I(rect(0, ybar, 2 * ea, ybar + TH), superell(ea, cy, ea, ob)))
    # s : deux ronds superposés (comme le S)
    Ht = XH + 2 * OVL + TH; bu = 0.47 * Ht / 2; bl_ = Ht / 2 - bu; cu = XH + OVL - bu; cl = -OVL + bl_
    sa = nw / 2 - 6
    ru = D(superell(sa, cu, sa - 5, bu), superell(sa, cu, sa - 5 - ST, bu - TH))
    rl = D(superell(sa, cl, sa, bl_), superell(sa, cl, sa - ST, bl_ - TH))
    ytu = min(0.30 * bu, 0.5 * (bu - TH)); ytl = min(0.30 * bl_, 0.5 * (bl_ - TH))
    xcu = min(sa + se_x(sa - 5 - ST, bu - TH, ytu), 2 * sa - 5 - ST) - 0.5
    xcl = max(sa - se_x(sa - ST, bl_ - TH, ytl), ST) + 0.5
    ru = D(ru, rect(sa, -100, 3 * sa, cu), rect(xcu, cu - 1, 3 * sa, cu + ytu))
    rl = D(rl, rect(-100, cl, sa, XH + 100), rect(-100, cl - ytl, xcl, cl + 1))
    G['s'] = U(ru, rl)
    # ---------- b d p q g ----------
    bw = nw + 6
    bowlR = D(rrect(0, 0, bw, XH, tr=rA, br=rA), rrect(ST, TH, bw - ST, XH - TH, tl=rs, bl=rs, tr=riA, br=riA))
    bowlL = D(rrect(0, 0, bw, XH, tl=rA, bl=rA), rrect(ST, TH, bw - ST, XH - TH, tl=riA, bl=riA, tr=rs, br=rs))
    kick = U(rect(bw - ST, 0, bw + SX, SL), wedge((bw, SL), (0, 1), (1, 0), R))
    G['b'] = U(bowlR, stem(0, 0, ASC), slab(0, ST, ASC, top=True, right=False), slab(0, ST, right=False))
    G['d'] = U(bowlL, stem(bw - ST, 0, ASC), slab(bw - ST, bw, ASC, top=True, right=False), kick)
    G['p'] = U(bowlR, stem(0, DESC, XH), slab(0, ST, XH, top=True, right=False), slab(0, ST, DESC))
    ear = slab(bw - ST, bw, XH, top=True, left=False)
    G['q'] = U(bowlL, stem(bw - ST, DESC, XH), ear, slab(bw - ST, bw, DESC))
    xg0 = round(0.16 * bw); rHg = round(0.5 * (bw - xg0)); riHg = max(round(0.3 * CW), rHg - ST)
    hookg = D(rrect(xg0, DESC, bw, DESC + hk, br=rHg), rrect(xg0 - 5, DESC + tht, bw - ST, DESC + hk + 5, br=riHg))
    G['g'] = U(bowlL, stem(bw - ST, DESC + hk - 1, XH), hookg, ear, drop(xg0 + rbh, DESC + rbh, rbh, (xg0 + 2.4 * rbh, DESC + tht), 'maxy'))
    # ---------- a ----------
    aw = nw; tha = round(0.75 * TH)
    ybw = round(max(0.50 * XH, 2 * tha + 0.10 * XH))                       # la panse garde toujours un blanc
    rba = round(max(0.32 * ST + 14, 0.55 * ST))                            # la goutte couvre tout le trait
    yta = ybw + round(0.06 * XH + 0.7 * rba)                                 # la goutte pend dans un vrai jour au-dessus de la panse
    inner_sh = rrect(ST, yta - 5, aw - ST, XH - tha, tl=riA, tr=riA) if XH - tha - yta > 0.25 * CW else None
    sh = D(rrect(0, yta, aw, XH, tl=rA, tr=rA), inner_sh)

    rBo = round(0.45 * ybw)
    bowl_a = D(rrect(0, 0, aw, ybw, tl=rBo, bl=rBo), rrect(ST, tha, aw - ST, ybw - tha, tl=max(rBo - ST, 10), bl=max(rBo - ST, 10), tr=rs, br=rs))
    cyd = min(yta + 0.3 * rba, XH - rba - 2)
    sh = D(sh, rect(-10, yta - 1, rba, cyd))                                 # le trait s'arrête au milieu de la goutte : raccord sans cran
    G["a"] = U(sh, stem(aw - ST, 0, max(XH - rA * 0.5, yta + 5)), bowl_a, U(rect(aw - ST, 0, aw + SX, SL), wedge((aw, SL), (0, 1), (1, 0), R)),
               drop(rba, cyd, rba, (ST + 1, min(yta + 2.2 * rba, XH - tha - riA - 2)), 'maxx'))
    # ---------- r f t ----------
    rw = round(0.66 * nw); ytr = round(0.52 * XH); rR = round(0.5 * rw); riR = max(round(0.3 * CW), rR - ST)
    arm_r = D(rrect(0, ytr, rw, XH, tr=rR), rrect(ST, ytr - 5, rw - ST, XH - TH, tl=rs, tr=riR))
    G['r'] = U(stem(0, 0, XH), arm_r, slab(0, ST, XH, top=True, right=False), slab(0, ST),
               drop(rw - rb, ytr, rb, (rw - ST - 1, min(ytr + 1.7 * rb, XH - TH - riR - 2)), 'minx'))
    fw = round(0.66 * nw); rF = round(0.5 * fw); riF = max(round(0.3 * CW), rF - ST)
    rbf = min(rb, round(0.27 * (ASC - XH)))
    ytf = XH + round(0.10 * XH) + rbf                                         # le bas de la goutte reste bien au-dessus de la barre
    hook_f = D(rrect(0, ytf, fw, ASC, tl=rF, tr=rF), rrect(ST, ytf - 5, fw - ST, ASC - TH, tl=riF, tr=riF) if ASC - TH - ytf > 0.25 * CW else None)
    G['f'] = U(stem(0, 0, max(ASC - rF, ytf + 5)), hook_f, drop(fw - rbf, ytf, rbf, (fw - ST - 1, max(ytf + 2, min(ytf + 1.7 * rbf, ASC - TH - riF - 2))), 'minx'),
               rect(-round(0.30 * nw), XH - TH, round(0.60 * nw), XH), slab(0, ST))
    tw = round(0.62 * nw); ttop = XH + round(0.22 * XH); hb = round(0.42 * XH); rT = round(0.48 * tw); riT = max(round(0.25 * CW), rT - ST)
    bot = D(rrect(0, 0, tw, hb, bl=rT), rrect(ST, TH, tw + 10, hb + 10, bl=riT))
    G['t'] = U(stem(0, hb - 1, ttop), bot, beak(tw, TH, up=True), rect(-round(0.28 * nw), XH - TH, tw, XH))
    # ---------- obliques ----------
    m = SX * 0.8
    # v
    vw = nw + 2 * SX + round(0.2 * CW)
    def vpair(width, wl, wr, bwid):
        cx = width / 2; hl, hr = wl, wr
        for _ in range(3):
            L_ = Diag(cx - bwid / 2 + hl / 2, m + hl / 2, wl); Rr = Diag(cx + bwid / 2 - hr / 2, width - m - hr / 2, wr)
            hl, hr = L_.hw, Rr.hw
        return L_, Rr
    L_, Rr = vpair(vw, ST, ST * 0.80, ST * 0.6)
    (pl0, pl1), (pr0, pr1) = L_.edge(-1), Rr.edge(1)
    G['v'] = U(I(U(L_.path, Rr.path, rect(pl0[0], 0, pr0[0], 2)), poly([pl0, pl1, pr1, pr0])),
               *sep(L_.slab(top=True), Rr.slab(top=True)))
    # y : le bras droit descend jusqu'au jambage
    yw = vw; xv = yw / 2
    rt = (yw - m - ST * 0.42, XH); dxdy = (rt[0] - (xv + ST * 0.15)) / XH
    ry_ = Diag(xv + ST * 0.15 + dxdy * DESC, rt[0], ST * 0.85, y0=DESC)
    ly_ = Diag(xv - ST * 0.30, m + ST * 0.55, ST * 1.0)
    (q0, q1) = ly_.edge(-1)
    G['y'] = U(ly_.path, ry_.path, *sep(ly_.slab(top=True), ry_.slab(top=True)), ry_.slab())
    # w
    ww = round(1.45 * nw + 2 * SX); bw_ = ST * 0.45; x1b, x2b, xm_ = ww * 0.30, ww * 0.70, ww / 2
    s1 = Diag(x1b - bw_ / 2, m + ST * 0.55, ST * 0.95); s2 = Diag(x1b + bw_ / 2, xm_ - ST * 0.2, ST * 0.72)
    s3 = Diag(x2b - bw_ / 2, xm_ + ST * 0.2, ST * 0.95); s4 = Diag(x2b + bw_ / 2, ww - m - ST * 0.42, ST * 0.72)
    G['w'] = U(s1.path, s2.path, s3.path, s4.path, s1.slab(top=True), s4.slab(top=True))
    # x
    xw = nw + 2 * SX + round(0.2 * CW + 0.2 * ST)
    d1 = Diag(xw - m - ST * 0.6, m + ST * 0.6, ST * 1.0); d2 = Diag(m + ST * 0.45, xw - m - ST * 0.45, ST * 0.78)
    tl_, tr_ = sep(d1.slab(top=True), d2.slab(top=True)); bl2, br2 = sep(d2.slab(), d1.slab())
    G['x'] = U(d1.path, d2.path, tl_, tr_, bl2, br2)
    # k
    kw = nw + round(0.3 * ST); yj = round(0.30 * XH); xt_ = kw - ST * 0.42; hwa = ST * 0.78
    for _ in range(4):
        xc_ = ST - hwa / 2; t_ = (XH - yj) / (xt_ - xc_)
        arm = Diag(xc_ - 10 / t_, xt_, ST * 0.78, y0=yj - 10); hwa = arm.hw
    legk = Diag(kw - ST * 0.55, ST + (kw - ST) * 0.28, ST * 1.0, y1=XH * 0.36 + 200)
    a0, a1 = arm.edge(-1); under = poly([a0, a1, (a1[0] + 3000, a1[1]), (a0[0] + 3000, a0[1] - 3000)])
    sb_, lb_ = sep(slab(0, ST), legk.slab())
    G['k'] = U(stem(0, 0, ASC), slab(0, ST, ASC, top=True, right=False), I(arm.path, rect(ST - 5, 0, kw + 200, XH)),
               I(I(legk.path, under), rect(ST - 5, 0, kw + 200, XH)), sb_, lb_, arm.slab(top=True))
    # z
    zw = round(0.92 * nw)
    zd = I(poly([(0, TH), (ST * 1.25, TH), (zw, XH - TH), (zw - ST * 1.25, XH - TH)]), rect(0, 0, zw, XH))
    G['z'] = U(rect(10, XH - TH, zw, XH), beak(10, XH - TH, up=False, side=1), zd, rect(0, 0, zw - 10, TH), beak(zw - 10, TH, up=True))
    return G
