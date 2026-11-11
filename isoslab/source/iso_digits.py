# ISOSLAB : chiffres (piste A, gouttes). Étroits, tous de la même chasse ; 1 et 4 posés sur un empattement.
import math
from iso_core import *

OVD = 10

def build_digits(w, style='drop'):
    ST, TH, W, CW, SL, SX, R = w.ST, w.TH, w.W, w.CW, w.SL, w.SX, w.R
    TH = round(min(TH, 0.62 * ST + 14))                                      # horizontales un peu plus fines : des blancs qui respirent en gras
    fw = round(0.92 * W + 10)
    rb = round(max(0.55 * ST, 0.45 * ST + 20))
    G = {}
    def ell(cx, cy, a, b): return superell(cx, cy, a, b, 2.6)
    def ringb(x0, y0, x1, y1):
        a, b = (x1 - x0) / 2, (y1 - y0) / 2; cx, cy = x0 + a, y0 + b
        return D(ell(cx, cy, a, b), ell(cx, cy, a - ST, b - TH)), (cx, cy, a, b)
    def drop(cx, cy, r=None): r = r or rb; return superell(cx, cy, r, r, 2.0)
    def tdrop(cx, cy, a, b, yt, side=-1):
        """goutte au bout d'un mur coupé à la hauteur yt : elle affleure le bord extérieur et couvre toute la coupe"""
        xo = se_x(a, b, yt - cy, 2.6); xi = se_x(a - ST, b - TH, yt - cy, 2.6) if abs(yt - cy) < b - TH else 0
        cut = xo - xi; r = max(rb, round(0.52 * cut))
        x = cx + side * (xo - r)
        return I(superell(x, yt, r, r, 2.0), ell(cx, cy, a, b))                  # la goutte ne dépasse jamais du rond
    def wall_x(cx, a, b, y, cy, inner=False):
        aa, bb = (a - ST, b - TH) if inner else (a, b)
        return se_x(aa, bb, y - cy, 2.6)
    def foot(x0, x1):
        return U(rect(x0 - SX, 0, x1 + SX, SL), wedge((x0, SL), (0, 1), (-1, 0), R), wedge((x1, SL), (0, 1), (1, 0), R))
    def beak_down(x0, y, side=1):
        bw = round(SL * 0.80); h = round(0.13 * CAP); x1 = x0 + side * bw; xi = x1
        return U(rect(min(x0, x1), y - h, max(x0, x1), y + 1), wedge((xi, y), (0, -1), (side, 0), R))
    # 0
    G['zero'], _ = ringb(0, -OVD, fw, CAP + OVD)
    # 1 : fût, drapeau en biais, pied à empattement
    xs = round(fw / 2 - ST / 2 + 0.06 * fw)
    flag = I(pbar((xs + ST * 0.5, CAP - ST * 0.3), (xs - 0.34 * fw, CAP - 0.30 * CAP), ST * 0.80), rect(-500, 0, xs + ST, CAP))
    G['one'] = U(rect(xs, 0, xs + ST, CAP), flag, foot(xs, xs + ST))
    # 2 : bol du haut ouvert en bas, goutte à gauche, diagonale qui part du mur droit, base
    yl2 = round(0.36 * CAP); bowl2, (cx2, cy2, a2, b2) = ringb(0, yl2, fw, CAP + OVD)
    yt2 = cy2 + 0.10 * b2
    top2 = D(bowl2, rect(-10, yl2 - 10, fw + 10, cy2), rect(-10, cy2 - 1, cx2, yt2))
    xin = cx2 - wall_x(cx2, a2, b2, yt2, cy2, True); xo = cx2 - wall_x(cx2, a2, b2, yt2, cy2)
    d2 = I(pbar((fw - ST * 0.55, cy2 + 60), (ST * 0.55, TH * 0.5), ST * 1.0), rect(-50, TH - 1, fw, cy2 + 1))
    G['two'] = U(top2, d2, rect(0, 0, fw + 10, TH), tdrop(cx2, cy2, a2, b2, yt2))
    # 3 : deux bols ouverts à gauche, gouttes en haut et en bas
    ym3 = round(0.55 * CAP); xm3 = round(0.36 * fw)
    up3, (cxu, cyu, au, bu) = ringb(0.06 * fw, ym3 - TH, fw, CAP + OVD)
    lo3, (cxl, cyl, al, bl) = ringb(0, -OVD, fw, ym3)
    gapd = 0.06 * CAP                                                      # jour entre une goutte et le milieu
    ytu = max(cyu + 0.10 * bu, ym3 + gapd + rb); ytl = max(min(cyl - 0.10 * bl, ym3 - TH - gapd - rb), cyl - 0.55 * (bl - TH))
    up3 = D(up3, rect(-10, ym3 - TH - 10, xm3, ytu))
    lo3 = D(lo3, rect(-10, ytl, xm3, ym3 + 10))
    xou = cxu - wall_x(cxu, au, bu, ytu, cyu); xol = cxl - wall_x(cxl, al, bl, ytl, cyl)
    G['three'] = U(up3, lo3, tdrop(cxu, cyu, au, bu, ytu), tdrop(cxl, cyl, al, bl, ytl))
    # 4 : fermé, pied à empattement
    xs4 = round(0.62 * fw); yb4 = round(0.26 * CAP)
    d4 = I(pbar((xs4 + ST * 0.4, CAP), (ST * 0.25, yb4 + TH * 0.5), ST * 0.9), rect(0, yb4, xs4 + ST, CAP))
    G['four'] = U(rect(xs4, 0, xs4 + ST, CAP), d4, rect(0, yb4, fw + 10, yb4 + TH), foot(xs4, xs4 + ST))
    # 5 : drapeau à goutte, fût posé sur le haut de la panse, panse ouverte à gauche
    yt5 = round(0.60 * CAP); x5 = round(0.08 * fw)
    lo5, (c5x, c5y, a5, b5) = ringb(0, -OVD, fw, yt5)
    ytl5 = max(min(c5y - 0.10 * b5, yt5 - TH - 0.06 * CAP - rb), c5y - 0.55 * (b5 - TH))      # la coupe reste au niveau du blanc
    lo5 = D(lo5, rect(-10, ytl5, 0.42 * fw, yt5 - TH), rect(-10, yt5 - TH, x5, yt5 + 10))   # ouverture à gauche ; le haut de la panse part du fût
    xo5 = c5x - wall_x(c5x, a5, b5, ytl5, c5y)
    G['five'] = U(lo5, rect(x5, yt5 - TH, x5 + ST, CAP), rect(x5, CAP - TH, fw - rb * 0.6, CAP), drop(fw - rb, CAP - rb * 0.95),
                  tdrop(c5x, c5y, a5, b5, ytl5))
    # 6 : le 0 ouvert en haut à droite, avec un bol fermé en bas ; 9 = 6 retourné
    ym6 = round(0.60 * CAP); zero, (cz, czy, az, bz) = ringb(0, -OVD, fw, CAP + OVD)
    yt6 = czy + 0.62 * bz
    bowl6, (cb6x, cb6y, ab6, bb6) = ringb(0, -OVD, fw, ym6)                 # bol rond en bas
    upper = I(D(zero, rect(fw / 2, cb6y - 1, fw + 10, yt6)), rect(-10, cb6y, fw + 10, 2000))
    six = D(U(upper, rect(0, cb6y, ST, czy), bowl6), ell(cb6x, cb6y, ab6 - ST, bb6 - TH))   # le blanc du bol reste net
    six = U(six, tdrop(cz, czy, az, bz, yt6, side=1))
    G['six'] = six
    b = six.bounds; G['nine'] = tr_rot(six, (b[0] + b[2]) / 2, (b[1] + b[3]) / 2)
    # 7 : barre, bec à gauche vers le bas, diagonale
    xb7 = round(0.30 * fw)
    d7 = I(pbar((fw - ST * 0.45, CAP - TH * 0.5), (xb7, -50), ST * 1.0), rect(-100, 0, fw + 10, CAP - TH + 1))
    G['seven'] = U(rect(0, CAP - TH, fw, CAP), d7, beak_down(0, CAP - TH, side=1))
    # 8 : deux anneaux
    ym8 = round(0.54 * CAP)
    up8, _ = ringb(0.06 * fw, ym8 - TH, 0.94 * fw, CAP + OVD); lo8, _ = ringb(0, -OVD, fw, ym8)
    G['eight'] = U(up8, lo8)
    return G, fw

def build_figure_signs(w, Dg, fw, C, sc, mv, pbar_):
    """% ‰ ¹ ² ³ ¼ ½ ¾ № à partir des chiffres"""
    from iso_core import Wt
    ST = w.ST; G = {}
    small, _ = build_digits(Wt(round(ST * 0.80)), 'drop')                   # petits chiffres un peu plus légers : même noirceur à l'œil
    k = 0.55
    def sm(n, top=None, base=None):
        p = sc(small[n], k); b = p.bounds
        if top is not None: return mv(p, -b[0], top - b[3])
        return mv(p, -b[0], base - b[1])
    for n, sup in (('one', 'onesuperior'), ('two', 'twosuperior'), ('three', 'threesuperior')):
        G[sup] = sm(n, top=CAP)
    z = sc(small['zero'], 0.50); bz = z.bounds; zw = bz[2] - bz[0]
    z1 = mv(z, -bz[0], CAP - bz[3]); z2 = mv(z, -bz[0] + zw * 1.25, -bz[1])
    sl = pbar_((zw * 0.15, -10), (zw * 2.1, CAP + 10), ST * 0.55 + 8)
    G['percent'] = U(z1, z2, sl)
    G['perthousand'] = U(z1, z2, mv(z, -bz[0] + zw * 2.35, -bz[1]), sl)
    def frac(a, b):
        na = sm(a, top=CAP); wa = na.bounds[2]
        db = sm(b, base=0); wb = db.bounds[2] - db.bounds[0]
        x0 = wa + 30
        return U(na, pbar_((x0 - 60, -10), (x0 + 180, CAP + 10), ST * 0.50 + 8), mv(db, x0 + 70))
    G['onequarter'] = frac('one', 'four'); G['onehalf'] = frac('one', 'two'); G['threequarters'] = frac('three', 'four')
    N = C['N']; bN = N.bounds
    o = sc(small['zero'], 0.42); bo = o.bounds; ow = bo[2] - bo[0]
    o = mv(o, bN[2] + 40 - bo[0], CAP - bo[3])
    G['uni2116'] = U(N, o, rect(bN[2] + 40, CAP * 0.36, bN[2] + 40 + ow, CAP * 0.36 + w.TH * 0.75))
    return G

def tr_rot(p, cx, cy):
    from iso_signs import rot180
    return rot180(p, cx, cy)
