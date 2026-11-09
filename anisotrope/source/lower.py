# Minuscules. Le fût de gauche est posé en x = 0 ; l'approche est donnée par out().
from core import *

HA = round(0.46 * XH)          # hauteur d'une arche

def n_body(top_left=XH):
    x1 = NW
    return U(stem(0, 0, top_left - 70), head(0, ST, top_left, arch_y(0, x1, XH, ST) if top_left == XH else None), arch(0, x1, XH),
             stem(x1 - ST, 0, XH - HA), foot(0, ST), foot(x1 - ST, x1))

@reg('n', 'n')
def g_n(): return out(n_body())

@reg('h', 'h')
def g_h(): return out(n_body(ASC))

@reg('m', 'm')
def g_m():
    mw = round(NW * 0.86); xm = mw - ST; x1 = xm + mw
    return out(U(stem(0, 0, XH - 70), head(0, ST, XH, arch_y(0, mw, XH, ST)), arch(0, mw, XH), arch(xm, x1, XH),
                 stem(xm, 0, XH - HA), stem(x1 - ST, 0, XH - HA),
                 foot(0, ST), foot(xm, xm + ST), foot(x1 - ST, x1)))

@reg('u', 'u')
def g_u():
    x1 = NW
    return out(U(stem(0, HA, XH - 70), head(0, ST, XH), cup(0, x1),
                 stem(x1 - ST, 0, XH - 70), head(x1 - ST, x1, XH), kick(x1 - ST, x1),
                 bracket(x1 / 2, round(0.46 * XH), x1 / 2, round(0.46 * XH) + OV, x1 - ST, 0, -1)), 'S', 'K')

@reg('r', 'r')
def g_r():
    xe = round(0.70 * NW + 0.4 * ST); h = round(0.40 * XH)
    cx = ST / 2 + (xe - ST / 2) / 2 + 30; rx = cx; cy = XH - h; ry = h + OV
    a = I(D(ellipse(cx, cy, rx, ry), ellipse(cx, cy, rx - ST, ry - TH)), rect(ST * 0.5, cy, 2 * rx + 10, XH + OV + 5))
    a = D(a, rcut(cx, cy, rx, ry, ST, TH, 0, 32, 1, -5))
    jy = cy + ry * math.sqrt(max(0.0, 1 - ((ST - cx) / rx) ** 2))
    return out(U(stem(0, 0, XH - 70), head(0, ST, XH, jy), a, foot(0, ST)), 'S', 'T')

@reg('o', 'o')
def g_o(): return out(bowl(BR), 'O', 'O')

@reg('b', 'b')
def g_b():
    return out(U(stem(0, 0, ASC - 70), head(0, ST, ASC), bowl(BR - 4 + 6), spur(0, ST),
                 bracket(BR + 2, XH / 2, BR, XH / 2 + OV, ST, 0, 1)), 'S', 'O')

@reg('d', 'd')
def g_d():
    x0 = 2 * BR - ST
    return out(U(bowl(BR), stem(x0, 0, ASC - 70), head(x0, x0 + ST, ASC), kick(x0, x0 + ST),
                 bracket(BR, XH / 2, BR, XH / 2 + OV, x0, 0, -1)), 'O', 'K')

@reg('p', 'p')
def g_p():
    jy = XH / 2 + (XH / 2 + OV) * math.sqrt(max(0.0, 1 - ((ST - BR - 2) / BR) ** 2))      # haut du rond au bord droit du fût
    return out(U(stem(0, DESC, XH - 70), head(0, ST, XH, jy), bowl(BR + 2), foot(0, ST, y=DESC)), 'S', 'O')

@reg('q', 'q')
def g_q():
    x0 = 2 * BR - ST; e3 = max(12, round(ST * 0.18))
    cut = poly([(x0, DESC + 60), (x0 + ST - e3, DESC), (x0 + ST, DESC), (x0 + ST, DESC + 90), (x0, DESC + 120)])
    jy = XH / 2 + (XH / 2 + OV) * math.sqrt(max(0.0, 1 - ((x0 - BR) / BR) ** 2))
    return out(U(bowl(BR), stem(x0, DESC + 60, XH - 60), cut, ear(x0, XH, jy)), 'O', 'T')

@reg('g', 'g')
def g_g():
    x0 = 2 * BR - ST; h = max(150, TH + 50); hr = round(0.72 * BR); dc = min(40, (h + OV - TH) * 0.5)
    ho = ellipse(x0 + ST - hr, DESC + h, hr, h + OV); hi = ellipse(x0 + ST - hr, DESC + h, hr - ST, h + OV - TH)
    hook = I(D(ho, hi), rect(x0 - 2 * hr, DESC - OV - 5, x0 + ST + 5, DESC + h))
    hook = D(hook, rect(x0 - 2 * hr - 10, DESC + h - dc, x0 + ST - hr, DESC + h + 10))
    jy = XH / 2 + (XH / 2 + OV) * math.sqrt(max(0.0, 1 - ((x0 - BR) / BR) ** 2))
    return out(U(bowl(BR), stem(x0, DESC + h, XH - 60), hook, ear(x0, XH, jy)), 'O', 'T')

@reg('c', 'c')
def g_c():
    # bouts coupés de l'extérieur vers l'intérieur du trait : deux coins francs
    rx = BR - 16; cx = rx; cy = XH / 2; ry = XH / 2 + OV; sx, sy = ST * 0.98, TH
    return out(D(ring(cx, cy, rx, ry), rcut(cx, cy, rx, ry, sx, sy, ROT, 38, 1, 0), rcut(cx, cy, rx, ry, sx, sy, ROT, -38, -1, 0)), 'O', 'T')

@reg('e', 'e')
def g_e():
    # le rond, ouvert en bas à droite (bout coupé dans l'axe), la barre suit le bord du rond
    rx = BR - 16; cx = rx; cy = XH / 2; ry = XH / 2 + OV
    yb = cy - 10 + round(0.2 * (ST - 84))
    r = D(ring(cx, cy, rx, ry), rcut(cx, cy, rx, ry, ST * 0.98, TH, ROT, -36, -1, 8))
    barre = I(rect(ST * 0.3, yb, cx + rx + 20, yb + TH), ellipse(cx, cy, rx, ry))
    return out(U(r, barre), 'O', 'T')

@reg('a', 'a')
def g_a():
    x1 = NW - 10; xs = x1 - ST
    by = round(0.30 * XH + 0.12 * ST); brx = round(0.47 * x1)
    bo = ellipse(brx, by, brx, by + OV)
    bi = ellipse(brx + 10, by + 2, brx - ST * 0.95, by + OV - TH, 12)
    bw = I(D(bo, bi), rect(-20, -OV - 5, xs + ST * 0.5, 2 * by))
    h = round(0.34 * XH); xl = round(0.10 * x1)
    cx = (xl + x1) / 2; rx = (x1 - xl) / 2
    ao = ellipse(cx, XH - h, rx, h + OV); ai = ellipse(cx, XH - h, rx - ST, h + OV - TH)
    zone = poly([(xl - 10, XH - 150), (xl - 10, XH - h - 2), (x1 + 5, XH - h - 2), (x1 + 5, XH + OV + 5),
                 (xl + 110, XH + OV + 5)])
    top = I(D(ao, ai), zone)
    return out(U(stem(xs, 0, XH - h + 10), bw, top, kick(xs, x1), bracket(brx, by, brx, by + OV, xs, 0, -1)), 'O', 'K')

@reg('i', 'i')
def g_i(): return out(U(stem(0, 0, XH - 70), head(0, ST, XH), foot(0, ST), dot(ST / 2 - 4, XH + 150 + ST * 0.3)))

@reg('dotlessi', 'ı')
def g_dotlessi(): return out(U(stem(0, 0, XH - 70), head(0, ST, XH), foot(0, ST)))

def j_body():
    h = max(120, TH + 40); r = round(max(0.55 * ST + 50, ST + 44)); dc = min(30, (h + OV - TH) * 0.5)
    o = ellipse(-r + ST, DESC + h, r, h + OV); i = ellipse(-r + ST, DESC + h, r - ST, h + OV - TH)
    hook = I(D(o, i), rect(-2 * r - 10, DESC - OV - 5, ST, DESC + h))
    hook = D(hook, rect(-2 * r - 20, DESC + h - dc, -r + ST, DESC + h + 10))
    return U(stem(0, DESC + h, XH - 70), head(0, ST, XH), hook)

@reg('j', 'j')
def g_j(): return out(U(j_body(), dot(ST / 2 - 4, XH + 150 + ST * 0.3)), 'T', 'P')

@reg('uni0237', 'ȷ')
def g_dotlessj(): return out(j_body(), 'T', 'P')

@reg('l', 'l')
def g_l():
    h = 110; reach = round(36 + 0.3 * ST)
    return out(U(stem(0, h, ASC - 70), head(0, ST, ASC), hook_r(0, 0, h, reach)), 'S', 'T')

@reg('t', 't')
def g_t():
    h = 100; reach = round(40 + 0.3 * ST); top = XH + 120
    s = U(stem(0, h, top - 30), poly([(0, top - 30), (ST, top + 10), (ST, top - 60), (0, top - 80)]))
    barre = rect(-round(W * 1.3), XH - TH, ST + round(W * 2.4), XH)
    return out(U(s, barre, hook_r(0, 0, h, reach)), 'T', 'T')

@reg('f', 'f')
def g_f():
    top = ASC; h = 120; reach = round(110 + 0.4 * ST)
    cxo = ST + reach - 40; cyo = top - h
    o = ellipse(cxo, cyo, reach + ST - 40, h + OV)
    i = ellipse(cxo, cyo - 4, reach - 40, h + OV - TH)
    crook = I(D(o, i), rect(-50, cyo, cxo + 0.3 * (reach - 40), top + OV + 5))   # bout coupé à la verticale, au-dessus du blanc
    barre = rect(-round(W * 1.3), XH - TH, ST + round(W * 2.2), XH)
    return out(U(stem(0, 0, top - h + 2), crook, barre, foot(0, ST, right=True)), 'T', 'T')

@reg('k', 'k')
def g_k():
    x1 = round(0.84 * NW); t = round(ST * 0.92)
    ax0, ay0, ax1, ay1 = ST + 10, round(0.30 * XH), x1 - 20, XH
    arm = bar(ax0, ay0, ax1, ay1, t)
    yj = round(0.42 * XH); xj = ax0 + (yj - ay0) / (ay1 - ay0) * (ax1 - ax0)
    tl = t * 1.05; ux, uy = (x1 + 10 - xj), -yj; ul = math.hypot(ux, uy); e_ = tl * 0.7
    leg = bar(xj - ux / ul * e_, yj - uy / ul * e_, x1 + 10, 0, tl)
    leg = D(leg, halfplane((ax1 - t / 2, XH), (ax0 - t / 2, ay0)))          # rien au-dessus du bras
    leg = I(leg, rect(ST - 20, 0, x1 + 200, XH))
    top = dserif(ax1, XH, ax0, ay0, t)
    arm = I(arm, rect(ST - 30, 0, x1 + 200, XH))
    arm = D(arm, I(halfplane((xj - tl / 2, yj), (x1 + 10 - tl / 2, 0)), rect(ST - 40, -100, x1 + 400, yj)))   # rien dans le creux
    return out(U(stem(0, 0, ASC - 70), head(0, ST, ASC), foot(0, ST), arm, leg, top,
                 dserif(x1 + 10, 0, xj, yj, t * 1.05, left=False)), 'S', 'D')

@reg('v', 'v')
def g_v():
    x1 = round(0.92 * NW); m = x1 / 2; t1 = ST * 1.05; t2 = ST * 0.78
    a = bar(0, XH, m - 4, 0, t1); b = bar(x1, XH, m + 4, 0, t2)
    a = D(a, halfplane((m + 4 + t2 / 2, 0), (x1 + t2 / 2, XH)))
    v = I(U(a, b), rect(-200, 0, x1 + 200, XH))
    return out(U(v, dserif(0, XH, m - 4, 0, t1), dserif(x1, XH, m + 4, 0, t2)), 'D', 'D')

@reg('w', 'w')
def g_w():
    s = round(0.74 * NW); t1 = ST * 1.0; t2 = ST * 0.74
    parts = []
    for k in range(2):
        x0 = k * s
        thick = D(bar(x0, XH, x0 + s / 2, 0, t1), halfplane((x0 + s / 2 + t2 / 2, 0), (x0 + s + t2 / 2, XH)))
        parts += [thick, bar(x0 + s, XH, x0 + s / 2, 0, t2)]
    w = I(U(*parts), rect(-200, 0, 2 * s + 200, XH))
    w = D(w, rect(s - t1, XH - round(SH * 0.9), s + t2, XH + 50))                  # sommet du milieu coupé droit, un peu plus bas
    return out(U(w, dserif(0, XH, s / 2, 0, t1), dserif(2 * s, XH, 1.5 * s, 0, t2)), 'D', 'D')

@reg('y', 'y')
def g_y():
    # le v, dont le bras droit continue sous la ligne dans la même pente, et finit par un pied simple
    x1 = round(0.92 * NW); m = x1 / 2; t1 = ST * 1.05; t2 = ST * 0.80
    slope = (x1 - m) / XH
    xb = x1 - slope * (XH - DESC)
    b = I(bar(x1, XH, xb, DESC, t2), rect(-400, DESC, x1 + 200, XH))          # coupé net sur la ligne des descendantes
    # le bras gauche s'arrête contre le bord gauche du bras droit : rien ne dépasse sous la jonction
    a = bar(0, XH, m + t2 * 0.35, 0, t1)                                  # le bras gauche plonge bien dans le bras droit
    a = D(a, poly([(x1 - t2 / 2 + 2, XH + 10), (xb - t2 / 2 + 2, DESC - 10), (x1 + 500, DESC - 10), (x1 + 500, XH + 10)]))
    a = I(a, rect(-200, -500, x1, XH))
    return out(U(a, b, dserif(0, XH, m + t2 * 0.35, 0, t1), dserif(x1, XH, xb, DESC, t2)), 'D', 'D')

@reg('x', 'x')
def g_x():
    x1 = round(0.86 * NW); t1 = ST * 1.0; t2 = ST * 0.76
    a = bar(0, XH, x1, 0, t1); b = bar(x1, XH, 0, 0, t2)
    x = I(U(a, b), rect(-200, 0, x1 + 200, XH))
    return out(U(x, dserif(0, XH, x1, 0, t1), dserif(x1, XH, 0, 0, t2),
                 dserif(0, 0, x1, XH, t2), dserif(x1, 0, 0, XH, t1)), 'D', 'D')

@reg('z', 'z')
def g_z():
    x1 = round(0.78 * NW); t = ST * 1.02
    d = bar(x1 - t / 2 - 6, XH - TH, t / 2 + 6, TH, t)
    z = U(rect(0, XH - TH, x1, XH), rect(0, 0, x1, TH), d)
    return out(I(z, rect(-10, 0, x1 + 10, XH)), 'T', 'T')

@reg('s', 's')
def g_s():
    # deux ronds empilés qui partagent la même bande au milieu ; bouts coupés d'équerre au bord du blanc
    rx = round(0.40 * NW + 0.2 * ST); ry = (XH + TH) / 4 + OV / 2; cx = rx; sx = ST * 0.9
    cu, cl = XH + OV - ry, -OV + ry
    up = D(I(ring(cx, cu, rx, ry, sx=sx, r=0), pie(cx, cu, -20, 270)), icut(cx, cu, rx, ry, sx, TH, 24, 1, -20))
    lo = D(I(ring(cx, cl, rx, ry, sx=sx, r=0), pie(cx, cl, 160, 450)), icut(cx, cl, rx, ry, sx, TH, 204, 1, 160))
    return out(U(up, lo), 'T', 'T')

# lettres de plus
@reg('germandbls', 'ß')
def g_germandbls():
    # le fût monte et tourne d'un seul trait dans l'arche ; deux bols à droite ; largeurs qui tiennent en gras
    top = ASC - 10; h = 150; x1 = round(max(0.80 * NW, 2 * ST + 150))
    rxa = x1 / 2; cyu = top - h
    arc = I(D(ellipse(rxa, cyu, rxa, h + OV), ellipse(rxa, cyu, rxa - ST, h + OV - TH)), rect(-5, cyu - 2, x1 + 5, top + OV + 5))
    rxu = round(max(0.42 * x1, ST + 60)); ryu = round(top - h - XH + 60); cxu = x1 - rxu
    upr = I(ring(cxu, cyu, rxu, ryu, sx=ST, r=0), rect(cxu - 2, cyu - ryu - OV - 5, x1 + 5, cyu + 2))
    ym = cyu - ryu
    ryl = (ym + TH + OV) / 2; cyl = ym + TH - ryl; rxl = round(max(0.52 * x1 + 0.2 * ST, ST + 120))
    low = I(ring(cxu, cyl, rxl, ryl, r=0), pie(cxu, cyl, 262, 452))
    return out(U(stem(0, 0, cyu + 2), arc, upr, low, foot(0, ST, right=False)), 'S', 'O')

@reg('ae', 'æ')
def g_ae():
    a = g_a()[0]
    a = D(a, rect(NW - 10 - ST, -50, NW + 200, 90))
    return out(U(a, mv(g_e()[0], NW - 10 - ST - 30)), 'O', 'T')

@reg('oe', 'œ')
def g_oe():
    return out(U(bowl(BR), mv(g_e()[0], 2 * BR - ST - 20)), 'O', 'T')

@reg('oslash', 'ø')
def g_oslash():
    return out(U(bowl(BR), pbar(2 * BR - 30, XH + 40, 30, -40, TH * 0.9)), 'O', 'O')

@reg('eth', 'ð')
def g_eth():
    # le o, une hampe qui part du haut du bol vers la droite en penchant, et une barre qui la croise
    x0 = 2 * BR - ST; cx = BR
    hampe = I(bar(x0 + ST * 0.5 - 3, XH * 0.5, cx + BR * 0.28, ASC - 10, ST * 0.95), rect(-50, XH * 0.5, 2 * BR + 100, ASC))
    hampe = D(hampe, ellipse(cx, XH / 2, BR - ST * 0.98, XH / 2 + OV - TH, ROT))
    ym = (XH + ASC) / 2 + 20; barre = pbar(cx - BR * 0.45, ym - 40 + TH / 2, cx + BR * 0.95, ym + 30 + TH / 2, TH)
    return out(U(bowl(BR), hampe, barre), 'O', 'T')

@reg('thorn', 'þ')
def g_thorn():
    return out(U(stem(0, DESC, ASC - 70), head(0, ST, ASC), bowl(BR + 2), foot(0, ST, y=DESC)), 'S', 'O')

@reg('lslash', 'ł')
def g_lslash():
    p = g_l()[0]
    return out(U(p, pbar(-70, 300 + TH / 2, ST + 70, 430 + TH / 2, TH)), 'T', 'T')

@reg('dcroat', 'đ')
def g_dcroat():
    x0 = 2 * BR - ST
    return out(U(g_d()[0], rect(x0 - 150, ASC - 190, x0 + ST + 50, ASC - 190 + TH)), 'O', 'K')

@reg('hbar', 'ħ')
def g_hbar():
    return out(U(n_body(ASC), rect(-(round(W * 0.95) + 10), ASC - 190, ST + 150, ASC - 190 + TH)))

@reg('ordfeminine', 'ª')
def g_ordfeminine():
    a = xf(g_a()[0], (0.58, 0, 0, 0.58, 0, CAP - 0.58 * XH + 10))
    b = bounds = a.bounds
    return out(U(a, rect(b[0], CAP - 0.58 * XH - 70, b[2], CAP - 0.58 * XH - 70 + TH * 0.8)), 'T', 'T')

@reg('ordmasculine', 'º')
def g_ordmasculine():
    o = xf(bowl(BR), (0.58, 0, 0, 0.58, 0, CAP - 0.58 * XH + 10))
    b = o.bounds
    return out(U(o, rect(b[0], CAP - 0.58 * XH - 70, b[2], CAP - 0.58 * XH - 70 + TH * 0.8)), 'T', 'T')
