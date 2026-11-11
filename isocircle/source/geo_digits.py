# Sans géométrique : chiffres (tous la même chasse)
import math
from geo_core import *

DN = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']

def build_digits(w, piste='M'):
    """piste M (choisie) : le 3 de B (tête plate), le 6 et le 9 de A (hampe au compas)"""
    p3 = 'B' if piste in ('B', 'M') else 'A'; p6 = 'A' if piste in ('A', 'M') else 'B'
    S, T, J = w.STC, w.TDC, w.J; e = 1.15 * J
    fw = round(0.56 * CAP + 0.5 * S); cx = fw / 2; G = {}
    bar_ = rbar
    def tangent(C, rm, B, side):
        """point où la droite issue de B touche le cercle (C, rm), calculé sur la lettre penchée ;
        renvoie le point (en dessin) et l'angle de dessin du rayon (le secteur sera penché avec la lettre)"""
        Cr, Br = to_real(C), to_real(B)
        dx, dy = Br[0] - Cr[0], Br[1] - Cr[1]; d = math.hypot(dx, dy); a = math.atan2(dy, dx); ph = math.acos(rm / d)
        th = a + side * ph; P_ = (Cr[0] + rm * math.cos(th), Cr[1] + rm * math.sin(th))
        thd = math.degrees(math.atan2(math.sin(th), math.cos(th) - SL[0] * math.sin(th)))   # angle qui, penché, donne th
        return to_design(P_), thd
    # deux cercles empilés (3, 8) : la taille du bas fixe celle du haut
    rb = min(fw / 2, (CAP + 2 * OVC + S) / 2 / 1.87); rt = (CAP + 2 * OVC + S) / 2 - rb
    cb = rb - OVC; ct = CAP + OVC - rt
    # 0 : ovale
    tv = round(0.9 * S)
    G['zero'] = Gl(ering(cx, CAP / 2, fw / 2, CAP / 2 + OVC, S, tv), [], [(cx, CAP / 2, fw / 2, CAP / 2 + OVC, 'point', tv)], 'NN', 0, fw)
    # 1 : fût + drapeau
    xs = cx - S / 2 + 0.08 * fw
    st1 = rect(xs, 0, xs + S, CAP)
    fl = I(bar_((xs + S * 0.5, CAP + 0.4 * S), (xs - 0.30 * fw, CAP - 0.30 * CAP), T), rect(-500, -10, xs + S, CAP))
    G['one'] = Gl(U(st1, fl), [D(I(fl, D(rect(xs - J, -10, xs + S + 10, CAP + 10), st1)), st1)], [], 'NN', 0, fw)
    # 2 : arc au compas, tangente à la règle, socle
    r2 = 0.97 * fw / 2; c2 = (cx, CAP + OVC - r2); rm = r2 - S / 2
    hb = hwidth(T, 1, 1)
    B = (T * 0.75, S)
    for _ in range(4):
        tp, th = tangent(c2, rm, B, 1)
        hb = T * math.hypot(tp[0] - B[0], tp[1] - B[1]) / abs(tp[1] - B[1]); B = (hb / 2, S)
    tp, th = tangent(c2, rm, B, 1)
    d_ = (B[0] - tp[0], B[1] - tp[1]); Ld = math.hypot(*d_)
    diag2 = I(bar_(tp, (B[0] + d_[0] / Ld * 200, B[1] + d_[1] / Ld * 200), S), rect(0, S / 2, fw, CAP))
    two = U(arc(c2[0], c2[1], r2, S, th, 160), diag2, rect(0, 0, fw, S))
    G['two'] = Gl(two, [I(diag2, rect(-10, S, fw, S + J))], [(c2[0], c2[1], r2)], 'NN', 0, fw)
    # 3 : deux arcs au compas, la langue du milieu part à gauche
    if p3 == 'A':
        three = U(arc(cx, ct, rt, S, -122, 150), arc(cx, cb, rb, S, -150, 90))
        G['three'] = Gl(three, [rect(cx - J / 2, cb + rb - S - 2, cx + J / 2, ct - rt + S + 2)], [(cx, ct, rt), (cx, cb, rb)], 'NN', 0, fw)
    else:                                                    # tête plate, oblique, panse
        yj = 2 * rb - OVC
        h3 = fit_h(T, fw - (cx - 0.05 * fw), CAP - S - (yj - S / 2))
        d3 = poly(para2(cx - 0.05 * fw - h3 / 2, fw - h3, h3, yj - S, CAP))
        three = U(rect(0.06 * fw, CAP - S, fw, CAP), d3, tbar(cx - 0.05 * fw - h3 / 2, yj - S, cx, yj, cx, cb, rb), arc(cx, cb, rb, S, -150, 0), I(arc(cx, cb, rb, S, 0, 120), vreal(cx, cb, -1)))
        G['three'] = Gl(three, [rect(-10, CAP - S - J, fw + 10, CAP - S)], [(cx, cb, rb)], 'NN', 0, fw)
    # 4
    x4 = fw - S - 0.06 * fw; yb4 = round(0.25 * CAP); hd = fit_h(T, x4 + S, CAP - yb4)
    d4 = poly(para2(0, x4 + S - hd, hd, yb4, CAP)); st4 = rect(x4, 0, x4 + S, CAP); bar4 = rect(0, yb4, x4 + S, yb4 + round(0.9 * S))
    G['four'] = Gl(U(d4, st4, bar4), [D(I(bar4, rect(x4 - J, -10, x4, CAP)), st4), I(d4, rect(-10, yb4 + 0.9 * S, fw, yb4 + 0.9 * S + J))], [], 'NN', 0, fw)
    # 5 : drapeau, fût, panse
    ytop = 2 * rb - OVC; xs5 = round(0.08 * fw)
    five = U(rect(xs5, CAP - S, fw - 0.02 * fw, CAP), rect(xs5, ytop - S, xs5 + S, CAP), tbar(xs5, ytop - S, cx, ytop, cx, cb, rb), arc(cx, cb, rb, S, -150, 0), I(arc(cx, cb, rb, S, 0, 120), vreal(cx, cb, -1)))
    G['five'] = Gl(five, [rect(xs5 - 10, CAP - S - J, xs5 + S + 10, CAP - S)], [(cx, cb, rb)], 'NN', 0, fw)
    # 6 9 : panse ronde + hampe
    if p6 == 'A':
        R6 = (CAP + OVC - cb) / math.sin(math.radians(100)); c6x = cx - rb + R6
        hamp = D(arc(c6x, cb, R6, S, 100, 180), circ(cx, cb, rb - S))
    else:
        top = (fw - 0.16 * fw, CAP + 40)
        tp6, th6 = tangent((cx, cb), rb - S / 2, top, 1)
        hamp = D(I(bar_(tp6, top, S), rect(-100, -100, fw + 100, CAP)), circ(cx, cb, rb - S))
    six = U(ring(cx, cb, rb, S), hamp)
    G['six'] = Gl(six, [], [(cx, cb, rb)], 'NN', 0, fw)
    nine = rot(six, 180, cx, CAP / 2)
    G['nine'] = Gl(nine, [], [(cx, CAP - cb, rb)], 'NN', 0, fw)
    # 7
    h7 = fit_h(T, fw - 0.16 * fw, CAP - S / 2)
    d7 = poly(para2(0.16 * fw, fw - h7, h7, 0, CAP - S / 2))
    G['seven'] = Gl(U(rect(0, CAP - S, fw, CAP), d7), [I(d7, rect(-10, CAP - S - J, fw + 10, CAP - S))], [], 'NN', 0, fw)
    # 8 : deux anneaux empilés
    G['eight'] = Gl(U(ring(cx, ct, rt, S), ring(cx, cb, rb, S)), [rect(cx - J / 2, cb + rb - S - 2, cx + J / 2, ct - rt + S + 2)], [(cx, ct, rt), (cx, cb, rb)], 'NN', 0, fw)
    for g in G.values(): g.tab = fw
    return G

def build_variants(w, G):
    """variantes en option : zéro barré, a et g à deux étages"""
    ST, S, J, Wd = w.ST, w.STC, w.J, w.W; e = 1.15 * J; V = {}
    z = G['zero']; fw = z.x1; cx = fw / 2; tv = round(0.9 * S)
    ia, ib = fw / 2 - S, CAP / 2 + OVC - tv                      # contreforme du 0
    bar_ = rbar
    sl = bar_((cx - ia, CAP / 2 - ib), (cx + ia, CAP / 2 + ib), round(0.72 * S))
    V['zero.zero'] = Gl(U(z.ink, I(sl, ell(cx, CAP / 2, ia + 2, ib + 2))), [], z.centers, 'NN', 0, fw,
                        alt=U(z.ink, I(sl, ell(cx, CAP / 2, ia - J, ib - J))))
    # a à deux étages : arc de tête au compas, fût, panse ovale
    wa = round(0.86 * Wd); rt = wa / 2; ct = XH + OV - rt
    ry = round(0.30 * XH + 0.12 * ST); cb = ry - OV; tvb = round(0.9 * ST)
    bowl = ering(wa / 2, cb, wa / 2, ry, ST, tvb)
    a2 = U(arc(wa / 2, ct, rt, ST, 0, 152), rect(wa - ST, 0, wa, ct + 1), I(bowl, half((wa, 0), (wa, 1000), 1)))
    V['a.ss01'] = Gl(a2, [D(rect(wa - ST - J, -20, wa - ST, 2 * ry), rect(wa - ST, -30, wa, XH), arc(wa / 2, ct, rt, ST, 0, 152))], [(wa / 2, ct, rt), (wa / 2, cb, wa / 2, ry, 'point', tvb)], 'OS', 0, wa)
    # g à deux étages : petit rond, attache, boucle ovale, oreille
    rg = round(0.33 * XH + 0.1 * ST); cg = XH + OV - rg; gx = round(0.48 * Wd)
    lx = round(0.47 * Wd); ly0 = round(0.10 * XH); lyb = DESC - OV; lry = (ly0 - lyb) / 2; lcy = (ly0 + lyb) / 2
    loop = ering(gx, lcy, lx, lry, ST, tvb)
    link = rect(gx - ST / 2, ly0 - tvb, gx + ST / 2, cg - rg + ST)
    ear = rect(gx + rg - ST, XH - round(0.85 * ST), gx + rg + round(0.20 * Wd), XH)
    g2 = U(ring(gx, cg, rg, ST), link, loop, ear)
    b = ubounds(g2)
    V['g.ss02'] = Gl(g2, [rect(gx - ST, ly0 - J * 0 + 1, gx + ST, ly0 + J) if False else rect(gx - ST, lcy + lry * math.sqrt(1 - (ST / 2 / lx) ** 2) - 0.5, gx + ST, lcy + lry * math.sqrt(1 - (ST / 2 / lx) ** 2) + J),
                          D(rect(gx + rg - ST - J, XH - ST - 10, gx + rg - ST, XH + 10), ring(gx, cg, rg, ST))],
                     [(gx, cg, rg), (gx, lcy, lx, lry, 'point', tvb)], 'OO', b[0], b[2])
    V['a.ss01'].is_alt = True; V['g.ss02'].is_alt = True
    return V

def build_figure_signs(w, G):
    """% ‰ ¹ ² ³ ¼ ½ ¾ №"""
    ST, S, T, J = w.ST, w.STC, w.TDC, w.J; e = 1.15 * J; F = {}
    fw = G['zero'].x1
    # chiffres supérieurs : dessinés plus gras puis réduits, pour garder un trait solide
    k = 0.58; st_s = 0.74 * w.ST / k
    ws = Wt(st_s, w.num, 0, w.filets); Ds = build_digits(ws)
    def small(n, dx, dy):
        g = Ds[n]; m = (k, 0, 0, k, dx, dy)
        return xf(g.ink, m), [xf(c, m) for c in g.cuts], g.x1 * k
    names = {'one': 'onesuperior', 'two': 'twosuperior', 'three': 'threesuperior'}
    for n, nm in names.items():
        ink, cu, wd = small(n, 0, CAP - k * CAP)
        F[nm] = Gl(ink, cu, [], 'OO', 0, wd)
    ink0, cu0, wd0 = small('zero', 0, 0)
    sw = round(0.30 * CAP); fracw = 2 * wd0 + sw * 0.55
    hs = fit_h(round(0.62 * T), sw, CAP)
    slash = poly(para2(wd0 - sw * 0.2, wd0 + sw * 0.75 - hs, hs, 0, CAP))
    for nm, a_, b_ in (('onequarter', 'one', 'four'), ('onehalf', 'one', 'two'), ('threequarters', 'three', 'four')):
        ia, ca, wa = small(a_, 0, CAP - k * CAP); ib, cb, wb = small(b_, wd0 + sw * 0.55, 0)
        F[nm] = Gl(U(ia, ib, slash), ca + cb, [], 'OO', 0, fracw)
    # % ‰ : petits ovales + oblique
    rx = round(0.17 * CAP); ry = round(0.20 * CAP); tp = round(0.85 * S); tv = round(0.8 * tp)
    pw = round(0.86 * CAP)
    o1 = ering(rx, CAP - ry, rx, ry, tp, tv); o2 = ering(pw - rx, ry, rx, ry, tp, tv)
    hp = fit_h(round(0.8 * T), pw - 2 * rx * 0.4, CAP)
    sl = poly(para2(rx * 0.4, pw - rx * 0.4 - hp, hp, 0, CAP))
    F['percent'] = Gl(U(o1, o2, sl), [D(I(sl, U(ell(rx, CAP - ry, rx + e, ry + e), ell(pw - rx, ry, rx + e, ry + e))), U(o1, o2))], [], 'OO', 0, pw)
    o3 = ering(pw + 2 * rx - tp + rx * 0.3, ry, rx, ry, tp, tv)
    F['perthousand'] = Gl(U(o1, o2, sl, o3), [D(I(sl, U(ell(rx, CAP - ry, rx + e, ry + e), ell(pw - rx, ry, rx + e, ry + e))), U(o1, o2))], [], 'OO', 0, pw + 2 * rx - tp + 1.3 * rx)
    # № : N + petit o souligné
    N = G['N']; nw = N.x1; ro = round(0.15 * CAP); tno = round(0.8 * S); xo = nw + round(0.07 * CAP) + ro
    no = U(N.ink, ring(xo, CAP - ro - 0.08 * CAP, ro, tno), rect(xo - ro, CAP - 2 * ro - 0.08 * CAP - 0.10 * CAP - tno * 0.8, xo + ro, CAP - 2 * ro - 0.08 * CAP - 0.10 * CAP))
    F['uni2116'] = Gl(no, N.cuts, [], 'SO', 0, xo + ro); F['uni2116'].sbk = 1.3
    return F
