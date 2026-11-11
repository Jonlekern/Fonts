# Sans géométrique : ponctuation et signes (sans chiffres)
import math
from geo_core import *

def build_signs(w, G):
    ST, S, T, J, Rl = w.ST, w.STC, w.TDC, w.J, w.R
    e = 1.15 * J; dd = round(1.16 * ST); rr = dd / 2; H = {}
    ma = round(0.52 * XH)                                  # axe des signes de calcul
    tb = round(0.86 * ST)                                  # trait des signes
    dot = lambda x, y: circ(x, y, rr)
    # . , : ; …
    H['period'] = Gl(dot(rr, rr), [], [], 'OO')
    comma = drop(rr, rr, rr, (rr - 0.30 * dd, -0.85 * dd))
    H['comma'] = Gl(comma, [], [], 'OO', 0, dd)
    H['colon'] = Gl(U(dot(rr, rr), dot(rr, XH - rr)), [], [], 'OO')
    H['semicolon'] = Gl(U(comma, dot(rr, XH - rr)), [], [], 'OO', 0, dd)
    g3 = round(0.62 * dd + 0.5 * w.SBO)
    H['ellipsis'] = Gl(U(dot(rr, rr), dot(rr + dd + g3, rr), dot(rr + 2 * (dd + g3), rr)), [], [], 'OO')
    H['periodcentered'] = Gl(dot(rr, ma), [], [], 'OO')
    rb = round(0.75 * dd); H['bullet'] = Gl(circ(rb, ma, rb), [], [], 'OO')
    # quotes : la virgule en haut
    up = CAP - dd
    q_r = xf(comma, (1, 0, 0, 1, 0, up))
    q_l = rot(q_r, 180, rr, up + rr - 0.15 * dd)
    gq = dd + round(0.5 * dd)
    H['quoteright'] = Gl(q_r, [], [], 'OO', 0, dd); H['quoteleft'] = Gl(q_l, [], [], 'OO', 0, dd)
    H['quotesinglbase'] = Gl(comma, [], [], 'OO', 0, dd)
    sh = lambda p, dx: xf(p, (1, 0, 0, 1, dx, 0))
    H['quotedblright'] = Gl(U(q_r, sh(q_r, gq)), [], [], 'OO', 0, dd + gq)
    H['quotedblleft'] = Gl(U(q_l, sh(q_l, gq)), [], [], 'OO', 0, dd + gq)
    H['quotedblbase'] = Gl(U(comma, sh(comma, gq)), [], [], 'OO', 0, dd + gq)
    qs = rect(0, CAP - round(0.30 * CAP), round(0.8 * ST), CAP)
    H['quotesingle'] = Gl(qs, [], [], 'SS')
    H['quotedbl'] = Gl(U(qs, sh(qs, round(0.8 * ST) + round(0.6 * dd))), [], [], 'SS')
    # ! ¡ ? ¿
    xs = (dd - ST) / 2; ys = round(1.42 * dd)
    H['exclam'] = Gl(U(rect(xs, ys, xs + ST, CAP), dot(rr, rr)), [], [], 'SS', 0, dd)
    rq = round(0.21 * CAP + 0.25 * ST); cq = CAP + OVC - rq; xq = rq            # ? : arc au compas + fût à la règle
    arcq = arc(xq, cq, rq, ST, -90, 158)
    stq = rect(xq - ST, ys, xq, cq - rq + ST)
    qd = dot(xq - ST / 2, rr)
    H['question'] = Gl(U(arcq, stq, qd), [rect(xq - ST - 10, cq - rq - J, xq + 10, cq - rq)], [(xq, cq, rq)], 'OO')
    def flip(g, dy):
        """signe renversé (¡ ¿) : tourné d'un demi-tour, la pointe en bas, le point à hauteur d'x"""
        b = g.ink.bounds; cx_ = (b[0] + b[2]) / 2
        m = lambda p: xf(rot(p, 180, cx_, 0), (1, 0, 0, 1, 0, dy))
        return Gl(m(g.ink), [m(c) for c in g.cuts], [(2 * cx_ - c[0], -c[1] + dy) + tuple(c[2:]) for c in g.centers], g.sides[::-1], 2 * cx_ - g.x1, 2 * cx_ - g.x0)
    H['exclamdown'] = flip(H['exclam'], XH)
    H['questiondown'] = flip(H['question'], XH)
    # ( ) [ ] { }
    yb, yt = round(-0.20 * CAP), round(1.10 * CAP); hc = (yt - yb) / 2; ym = (yt + yb) / 2
    rp = round(0.95 * CAP); hal = math.degrees(math.asin(hc / rp))
    xc = rp; par = arc(xc, ym, rp, ST, 180 - hal, 180 + hal)
    b = par.bounds
    H['parenleft'] = Gl(par, [], [], 'SO', b[0], b[2])
    H['parenright'] = Gl(mirror(par, (b[0] + b[2]) / 2), [], [], 'OS', b[0], b[2])
    bw = round(0.24 * CAP + 0.3 * ST)
    brk = U(rect(0, yb, S, yt), rect(0, yb, bw, yb + ST), rect(0, yt - ST, bw, yt))
    bcut = [rect(S, yb + ST, S + J, yt - ST) and rect(S, yb - 10, S + J, yb + ST + 10), rect(S, yt - ST - 10, S + J, yt + 10)]
    H['bracketleft'] = Gl(brk, bcut, [], 'SO')
    H['bracketright'] = Gl(mirror(brk, bw / 2), [mirror(c, bw / 2) for c in bcut], [], 'OS')
    t = ST; rbr = round(0.10 * CAP + 0.8 * ST); a = rbr - t / 2 + 4
    mid = ym
    br = U(arc(a + rbr, yt - rbr, rbr, t, 90, 180), rect(a, mid + rbr, a + t, yt - rbr),
           arc(a + t - rbr, mid + rbr, rbr, t, 270, 360), arc(a + t - rbr, mid - rbr, rbr, t, 0, 90),
           rect(a, yb + rbr, a + t, mid - rbr), arc(a + rbr, yb + rbr, rbr, t, 180, 270))
    b = br.bounds
    H['braceleft'] = Gl(br, [], [], 'OO', b[0], b[2])
    H['braceright'] = Gl(mirror(br, (b[0] + b[2]) / 2), [], [], 'OO', b[0], b[2])
    # / \ |
    sw = round(0.42 * CAP + 0.3 * ST); hs = fit_h(T, sw, yt - yb)
    sl = poly(para2(0, sw - hs, hs, yb, yt))
    H['slash'] = Gl(sl, [], [], 'DD', 0, sw); H['backslash'] = Gl(mirror(sl, sw / 2), [], [], 'DD', 0, sw)
    H['bar'] = Gl(rect(0, round(1.15 * DESC), ST, ASC), [], [], 'SS')
    # tirets
    hy = round(0.30 * CAP + 0.4 * ST)
    H['hyphen'] = Gl(rect(0, ma - tb / 2, hy, ma + tb / 2), [], [], 'DD')
    en = 500 - 2 * w.SBD; em = 1000 - 2 * w.SBD
    H['endash'] = Gl(rect(0, ma - tb / 2, en, ma + tb / 2), [], [], 'NN')
    H['emdash'] = Gl(rect(0, ma - tb / 2, em, ma + tb / 2), [], [], 'NN')
    H['endash'].x1 = en + 2 * w.SBD; H['emdash'].x1 = em + 2 * w.SBD
    H['endash'].ink = xf(H['endash'].ink, (1, 0, 0, 1, w.SBD, 0)); H['emdash'].ink = xf(H['emdash'].ink, (1, 0, 0, 1, w.SBD, 0))
    H['underscore'] = Gl(rect(0, round(-0.20 * CAP), round(0.62 * CAP), round(-0.20 * CAP) + tb), [], [], 'NN')
    # calcul : + − × ÷ = < > ~ ^
    mw = round(0.52 * CAP + 0.2 * ST); hmw = mw / 2
    hbar = rect(0, ma - tb / 2, mw, ma + tb / 2); vbar = rect(hmw - tb / 2, ma - hmw, hmw + tb / 2, ma + hmw)
    H['plus'] = Gl(U(hbar, vbar), [rect(hmw - tb / 2 - J, ma - tb, hmw - tb / 2, ma + tb), rect(hmw + tb / 2, ma - tb, hmw + tb / 2 + J, ma + tb)], [], 'SS', 0, mw)
    H['uni2212'] = Gl(hbar, [], [], 'SS', 0, mw)
    xb = rot(hbar, 45, hmw, ma); xv = rot(vbar, 45, hmw, ma)
    cutx = [D(rot(rect(hmw - tb / 2 - J, ma - tb, hmw + tb / 2 + J, ma + tb), 45, hmw, ma), xv)]
    mx = I(U(xb, xv), circ(hmw, ma, hmw * 0.92))
    H['multiply'] = Gl(mx, [I(c, xb) for c in cutx], [], 'OO', 0, mw)
    gd = round(0.55 * dd) + tb / 2 + rr
    H['divide'] = Gl(U(hbar, dot(hmw, ma + gd), dot(hmw, ma - gd)), [], [], 'SS', 0, mw)
    ge = round(0.5 * tb + 0.22 * CAP * 0.5 + 0.2 * ST)
    H['equal'] = Gl(U(rect(0, ma + ge - tb / 2, mw, ma + ge + tb / 2), rect(0, ma - ge - tb / 2, mw, ma - ge + tb / 2)), [], [], 'SS', 0, mw)
    f = round(0.30 * tb)
    pL, pR, hv = vpair_pts(hmw, ma - hmw * 0.92, ma + hmw * 0.92, hmw * 0.92, f, tb)
    # chevron couché : on dessine un V de hauteur mw puis on le tourne
    vh = 0.80 * mw
    pL, pR, hv = vpair_pts(0, 0, mw, vh / 2, f, tb); L_, R_ = clip_pair(pL, pR)
    chev = U(L_, R_); chev_cut = I(L_, band(pR, -1, e))
    lt = rot(chev, -90, 0, 0); ltc = rot(chev_cut, -90, 0, 0)
    bl = lt.bounds; dx_, dy_ = -bl[0], ma - (bl[1] + bl[3]) / 2
    mv = lambda p: xf(p, (1, 0, 0, 1, dx_, dy_))
    H['less'] = Gl(mv(lt), [mv(ltc)], [], 'DD', 0, bl[2] - bl[0])
    H['greater'] = Gl(mirror(mv(lt), (bl[2] - bl[0]) / 2), [mirror(mv(ltc), (bl[2] - bl[0]) / 2)], [], 'DD', 0, bl[2] - bl[0])
    rt = round(0.15 * CAP + 0.3 * ST)
    til = U(arc(rt, ma, rt, tb, 0, 180), arc(3 * rt - tb, ma, rt, tb, 180, 360))
    H['asciitilde'] = Gl(til, [], [], 'OO', 0, 4 * rt - tb)
    cw_ = round(0.40 * CAP + 0.2 * ST)
    pL, pR, hc_ = vpair_pts(cw_ / 2, CAP, round(0.55 * CAP), cw_ / 2, f, tb); L_, R_ = clip_pair(pL, pR)
    H['asciicircum'] = Gl(U(L_, R_), [I(L_, band(pR, -1, e))], [], 'DD', 0, cw_)
    # guillemets : petits chevrons à hauteur d'x
    gw = round(0.40 * XH + 0.3 * ST); gh = round(0.21 * XH + 0.25 * ST); gt = round(0.66 * tb)
    pL, pR, hg = vpair_pts(0, 0, gw, gh, round(0.3 * gt), gt); L_, R_ = clip_pair(pL, pR)
    gch = rot(U(L_, R_), -90, 0, 0); gcc = rot(I(L_, band(pR, -1, e)), -90, 0, 0); bg = gch.bounds
    mvg = lambda p, dx=0: xf(p, (1, 0, 0, 1, -bg[0] + dx, XH / 2 - (bg[1] + bg[3]) / 2))
    gwid = bg[2] - bg[0]; gstep = round(0.62 * gwid + 0.6 * ST)
    H['guilsinglleft'] = Gl(mvg(gch), [mvg(gcc)], [], 'DD', 0, gwid)
    H['guilsinglright'] = Gl(mirror(mvg(gch), gwid / 2), [mirror(mvg(gcc), gwid / 2)], [], 'DD', 0, gwid)
    H['guillemotleft'] = Gl(U(mvg(gch), mvg(gch, gstep)), [mvg(gcc), mvg(gcc, gstep)], [], 'DD', 0, gwid + gstep)
    H['guillemotright'] = Gl(mirror(U(mvg(gch), mvg(gch, gstep)), (gwid + gstep) / 2), [mirror(mvg(gcc), (gwid + gstep) / 2), mirror(mvg(gcc, gstep), (gwid + gstep) / 2)], [], 'DD', 0, gwid + gstep)
    # * #
    ra = round(0.17 * CAP + 0.2 * ST); ca = CAP - ra; sp = rect(ra - tb / 2 * 0.9, ca, ra + tb / 2 * 0.9, ca + ra)
    ast = U(circ(ra, ca, 0.8 * tb), *[rot(sp, k * 60, ra, ca) for k in range(6)])
    H['asterisk'] = Gl(ast, [], [(ra, ca, ra * 0 + tb)] if False else [], 'OO', 0, 2 * ra)
    hw_ = round(0.58 * CAP + 0.9 * tb); hh = round(0.62 * CAP); y0h = 0
    v1 = rect(hw_ * 0.30 - tb / 2, y0h, hw_ * 0.30 + tb / 2, hh); v2 = rect(hw_ * 0.70 - tb / 2, y0h, hw_ * 0.70 + tb / 2, hh)
    h1 = rect(0, hh * 0.33 - tb / 2, hw_, hh * 0.33 + tb / 2); h2 = rect(0, hh * 0.67 - tb / 2, hw_, hh * 0.67 + tb / 2)
    hcut = [D(rect(xv - tb / 2 - J, -10, xv + tb / 2 + J, hh + 10), rect(xv - tb / 2, -20, xv + tb / 2, hh + 20)) for xv in (hw_ * 0.30, hw_ * 0.70)]
    H['numbersign'] = Gl(U(v1, v2, h1, h2), [I(U(h1, h2), c) for c in hcut], [], 'SS', 0, hw_)
    # @ : un a dans un rond ouvert
    ta = round(0.78 * ST); ro = round(0.42 * CAP + 0.4 * ST); ri = round(0.46 * ro); cyat = round(0.42 * CAP)
    inner = U(ring(ro, cyat, ri, ta), rect(ro + ri - ta, cyat - ri + OV, ro + ri, cyat + ri - OV))
    outer = arc(ro, cyat, ro, ta, 0, 300)
    H['at'] = Gl(U(inner, outer), [rect(ro + ri - ta - J, cyat - ri - 10, ro + ri - ta, cyat + ri + 10)], [(ro, cyat, ri), (ro, cyat, ro)], 'OO')
    # & : boucle au compas, panse ouverte, jambe à la règle
    S = round(0.85 * w.STC); r1 = round(0.16 * CAP + 0.45 * S); r2 = round(0.27 * CAP + 0.4 * S)
    c2 = (r2, r2 - OVC); c1 = (r2 - 0.06 * CAP, CAP + OVC - r1)
    loop = ring(c1[0], c1[1], r1, S)
    amw = round(2 * r2 + 0.10 * CAP)
    p0 = (c1[0], c1[1])
    xb_ = amw - 0.5 * T
    for _ in range(6):                                   # le bas de la jambe affleure la chasse
        dxl, dyl = xb_ - p0[0], -p0[1]; hb = T * math.hypot(dxl, dyl) / abs(dyl); xb_ = amw - hb / 2
    p1 = (xb_, 0.0)
    d_ = (p1[0] - p0[0], p1[1] - p0[1]); Ld = math.hypot(*d_)
    def bar_(p, q, tt):
        dx, dy = q[0] - p[0], q[1] - p[1]; L = math.hypot(dx, dy); nx, ny = -dy / L * tt / 2, dx / L * tt / 2
        return poly([(p[0] + nx, p[1] + ny), (q[0] + nx, q[1] + ny), (q[0] - nx, q[1] - ny), (p[0] - nx, p[1] - ny)])
    far = (p1[0] + d_[0] / Ld * 300, p1[1] + d_[1] / Ld * 300)
    rm_ = r2 - S / 2
    def cross(k0, k1):
        """angle où le cercle moyen de la panse croise l'axe de la jambe"""
        best = None
        for k in range(k0 * 10, k1 * 10):
            th = math.radians(k / 10); px, py = c2[0] + rm_ * math.cos(th), c2[1] + rm_ * math.sin(th)
            dist = abs((px - p0[0]) * d_[1] - (py - p0[1]) * d_[0]) / Ld
            if best is None or dist < best[0]: best = (dist, k / 10)
        return best[1]
    bowl = arc(c2[0], c2[1], r2, S, cross(0, 180), cross(220, 360))
    T = round(0.85 * w.TDC)
    leg = D(I(bar_(p0, far, T), rect(-100, 0, amw + 300, CAP + 100)), circ(c1[0], c1[1], r1 - S))
    legw = D(I(bar_(p0, far, T + 2 * e), rect(-100, -10, amw + 300, CAP + 100)), circ(c1[0], c1[1], r1 - S))
    H['ampersand'] = Gl(U(loop, bowl, leg), [I(bowl, D(legw, leg)), I(loop, D(legw, leg))], [(c1[0], c1[1], r1), (c2[0], c2[1], r2)], 'OD', 0, amw)
    # $ ¢ € £ ¥
    S = w.STC
    Sg = G['S']; rxS, c1S, c2S, ryS, tvS = Sg.geo; cxs = rxS; bwid = round(0.6 * S); hb_ = bwid / 2
    yin = lambda c, sg: c + sg * (ryS - tvS) * math.sqrt(1 - (hb_ / (rxS - S)) ** 2)     # bord intérieur au droit de la barre
    yout = lambda c, sg: c + sg * ryS * math.sqrt(1 - (hb_ / rxS) ** 2)                  # bord extérieur au droit de la barre
    top_ = rect(cxs - hb_, c1S + ryS - tvS + 1, cxs + hb_, CAP + round(0.13 * CAP)); bot_ = rect(cxs - hb_, -round(0.13 * CAP), cxs + hb_, c2S - ryS + tvS - 1)
    H['dollar'] = Gl(U(Sg.ink, top_, bot_), Sg.cuts + [rect(cxs - S, yout(c1S, 1) - 0.5, cxs + S, yout(c1S, 1) + J), rect(cxs - S, yout(c2S, -1) - J, cxs + S, yout(c2S, -1) + 0.5)], Sg.centers, 'OO')
    H['dollar'].sbk = 1.3
    cg = G['c']; cxc = Rl; hb2 = bwid / 2 if bwid / 2 < ST else ST / 2; bw2 = 2 * hb2
    yi_ = math.sqrt((Rl - ST) ** 2 - hb2 ** 2); yo_ = math.sqrt(Rl ** 2 - hb2 ** 2)
    H['cent'] = Gl(U(cg.ink, rect(cxc - hb2, XH / 2 + Rl - ST + 1, cxc + hb2, XH + round(0.16 * CAP)), rect(cxc - hb2, -round(0.16 * CAP), cxc + hb2, XH / 2 - Rl + ST - 1)),
                   [rect(cxc - ST, XH / 2 + yo_ - 0.5, cxc + ST, XH / 2 + yo_ + J), rect(cxc - ST, XH / 2 - yo_ - J, cxc + ST, XH / 2 - yo_ + 0.5)], cg.centers, 'OO')
    Cg = G['C']; R_ = w.RC; eb = round(0.13 * CAP); ext_ = round(0.16 * CAP)
    eur = xf(Cg.ink, (1, 0, 0, 1, ext_, 0))
    cxE = R_ + ext_
    def ebar(y0, y1, x0):
        """barre du € : son bout droit se cache dans l'épaisseur du C"""
        ya_, yb2 = sorted((abs(y0 - CAP / 2), abs(y1 - CAP / 2)))
        xo = cxE - math.sqrt(R_ ** 2 - yb2 ** 2); xi = cxE - math.sqrt((R_ - S) ** 2 - ya_ ** 2)
        return rect(x0, y0, cxE - 0.30 * R_, y1)          # la barre entre franchement dans le rond
    ebars = [ebar(CAP / 2 + 0.07 * CAP, CAP / 2 + 0.07 * CAP + 0.8 * S, 0), ebar(CAP / 2 - 0.07 * CAP - 0.8 * S, CAP / 2 - 0.07 * CAP, 0.04 * CAP)]
    H['Euro'] = Gl(U(eur, *ebars), [D(I(U(*ebars), D(circ(R_ + ext_, CAP / 2, R_ + J), circ(R_ + ext_, CAP / 2, R_ - S / 2))), eur)], [(R_ + ext_, CAP / 2, R_)], 'OO')
    H['Euro'].sbk = 1.3
    rl = round(0.18 * CAP + 0.4 * S); xsL = round(0.12 * CAP); cl = CAP + OVC - rl; lw = round(0.50 * CAP + 0.3 * S)
    ster = U(rect(xsL, S, xsL + S, cl), arc(xsL + rl, cl, rl, S, 30, 180), rect(0, 0, lw, S), rect(0, 0.42 * CAP, xsL + S + round(0.18 * CAP), 0.42 * CAP + 0.85 * S))
    H['sterling'] = Gl(ster, [rect(xsL - 10, S, xsL + S + 10, S + J), rect(xsL - 10, cl - J, xsL + S + 10, cl)], [(xsL + rl, cl, rl)], 'SD')
    H['sterling'].sbk = 1.3
    Yg = G['Y']; yb_ = Yg.ink.bounds; ycx = (yb_[0] + yb_[2]) / 2; yl = round(0.30 * CAP)
    tb2 = round(0.5 * S); yc1 = round(0.12 * CAP); yc2 = yc1 + tb2 + max(0.6 * tb2, 40)
    ybars = [rect(ycx - 0.30 * CAP, yc - tb2 / 2, ycx + 0.30 * CAP, yc + tb2 / 2) for yc in (yc1, yc2)]
    H['yen'] = Gl(U(Yg.ink, *ybars), Yg.cuts + [D(rect(ycx - S / 2 - J, 0, ycx + S / 2 + J, 0.42 * CAP - J), rect(ycx - S / 2, -10, ycx + S / 2, CAP)) and I(U(*ybars), D(rect(ycx - S / 2 - J, -10, ycx + S / 2 + J, CAP), rect(ycx - S / 2, -20, ycx + S / 2, CAP + 10)))], [], 'DD', yb_[0], yb_[2])
    H['yen'].sbk = 1.3
    # © ® ™
    rc = round(0.46 * CAP); tc = round(0.55 * ST); cyc = CAP / 2; ric = round(0.46 * rc)
    H['copyright'] = Gl(U(ring(rc, cyc, rc, tc), arc(rc, cyc, ric, round(0.75 * ST), 44, 316)), [], [(rc, cyc, rc), (rc, cyc, ric)], 'OO')
    sR = round(0.75 * ST); rr_ = round(0.20 * rc); xR = rc - 0.42 * rc + 0
    yR0, yR1 = cyc - 0.48 * rc, cyc + 0.48 * rc; ybR = cyc - 0.06 * rc
    rR = (yR1 - ybR) / 2; xcR = xR + 0.40 * rc
    Rin = U(rect(xR, yR0, xR + sR, yR1), rect(xR, yR1 - sR, xcR, yR1), rect(xR, ybR, xcR, ybR + sR), arc(xcR, ybR + rR, rR, sR, -90, 90),
            I(poly(para2(xcR + 0.42 * rc - fit_h(sR, 0.42 * rc + 0.0, ybR + sR / 2 - yR0), xcR - fit_h(sR, 0.42 * rc, ybR + sR / 2 - yR0) / 2, fit_h(sR, 0.42 * rc, ybR + sR / 2 - yR0), yR0, ybR + sR / 2)), rect(0, yR0, 2 * rc, ybR + sR)))
    H['registered'] = Gl(U(ring(rc, cyc, rc, tc), Rin), [], [(rc, cyc, rc)], 'OO')
    th = round(0.36 * CAP); ts = round(0.62 * ST); ty0 = CAP - th; tW = round(0.36 * CAP)
    Tt = U(rect(0, CAP - ts, tW, CAP), rect(tW / 2 - ts / 2, ty0, tW / 2 + ts / 2, CAP))
    mx0 = tW + round(0.10 * CAP); mW = round(0.44 * CAP)
    pL, pR, hm = vpair_pts(mx0 + mW / 2, ty0, CAP, mW / 2, round(0.3 * ts), ts); L_, R_ = clip_pair(pL, pR)
    Mt = U(rect(mx0, ty0, mx0 + ts, CAP), rect(mx0 + mW - ts, ty0, mx0 + mW, CAP), L_, R_)
    H['trademark'] = Gl(U(Tt, Mt), [rect(tW / 2 - ts / 2 - 10, CAP - ts - J, tW / 2 + ts / 2 + 10, CAP - ts), I(L_, band(pR, -1, e))], [], 'SS', 0, mx0 + mW)
    # § ¶ °
    ts_ = round(0.85 * ST); ty = round(0.70 * ST); rys = round(0.26 * CAP); rxs = round(0.21 * CAP + 0.35 * ST)
    y2 = CAP / 2 - 0.08 * CAP
    sec = U(sbout(rxs, y2 + rys, rxs, rys, ts_, ty, 200, 28), ering(rxs, y2, rxs, rys, ts_, ty), sbout(rxs, y2 - rys, rxs, rys, ts_, ty, 20, -152))
    H['section'] = Gl(sec, [], [(rxs, y2, rxs, rys, 'point', ty)], 'OO')
    pw_ = round(0.50 * CAP + 0.2 * ST); rpb = round(0.24 * CAP); x1p = pw_ - 2.2 * ST - round(0.06 * CAP)
    para_ = U(rect(x1p, DESC * 0.5, x1p + ST, CAP), rect(pw_ - ST, DESC * 0.5, pw_, CAP), rect(x1p, CAP - ST, pw_, CAP),
              I(circ(x1p, CAP - rpb, rpb), rect(x1p - rpb - 5, 0, x1p + 1, CAP + 5)))
    H['paragraph'] = Gl(para_, [rect(x1p + ST, CAP - ST - J, pw_ - ST, CAP - ST) and rect(pw_ - ST - 10, CAP - ST - J, pw_ + 10, CAP - ST)], [], 'OS', x1p - rpb, pw_)
    rdg = round(0.13 * CAP + 0.2 * ST)
    H['degree'] = Gl(ring(rdg, CAP - rdg, rdg, round(0.62 * ST)), [], [], 'OO')
    # espace
    for n_, a_ in (('space', round(0.26 * 1000)), ('uni00A0', round(0.26 * 1000))):
        H[n_] = Gl(P(), [], [], 'NN', 0, a_)
    return H
