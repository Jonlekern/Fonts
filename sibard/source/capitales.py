# Les capitales de Sibard. Chaque fonction rend (tuyaux, chasse).
# La structure : le contraste Art déco (fût de gauche en filet, fût de droite gras, barres en filet).
# La signature : chaque lettre a un geste à elle, pris aux emblèmes chromés des années 50.
from tuyaux import Tuyau as T
from dessin import D, fut, barre, JOINT as J
from minuscules import _signe, _k, _v, _w, _x, _z, _s


def _rep(d, W, rond=False):
    """Axe du fût gauche, axe du fût droit, axe de la barre du haut, axe de la barre du bas."""
    xl, xr = d.gd(W, d.Lr if rond else d.L)
    return xl, xr, d.haut(d.cap, rond), d.bas(rond)


def A(d):
    W = 640 + d.g; L = d.Lr * 0.5
    xl, xr = d.gd(W, L); xc = (xl + xr) / 2 - d.F * 0.2; yh = d.cap + d.d - d.F * 0.5
    ym = d.taille() * 0.92; k = ym / yh
    a0, a1, a2 = (xl, 0), (xc, yh), (xr, 0)
    return [T([a0, a1, a2], r=d.c * 0.4, debut='h', fin='h'),
            T([(xl + (xc - xl) * k, ym), (xr - (xr - xc) * k, ym)], debut=d.contre(a0, a1, -1), fin=d.contre(a1, a2, -1))], L + W + L


def B(d):
    W = 540 + d.g * 0.9; xs, xb, top, bas = _rep(d, W)
    yj = d.taille() + (d.cap * 0.5 - d.taille()) * 0.6
    xb1 = xb - (W - d.F) * 0.08
    r1 = max((top - yj) / 2 - 1, 1); r2 = max((yj - bas) / 2 - 1, 1)
    return [T([(xs, d.cap), (xs, bas), (xb, bas), (xb, yj), (xs + d.Fg / 2 - J, yj)], r=[d.c, r2, r2]),
            T([(xs + d.Fg / 2 - J, top), (xb1, top), (xb1, yj), (xb1 - r1 - 2, yj)], r=r1)], d.L + W + d.Lr


def C(d):
    W = 620 + d.g; xl, xr, top, bas = _rep(d, W, True)
    xe = d.Lr + W - 6
    return [T([(xe, top), (xl, top), (xl, bas), (xe, bas)], r=d.R(2 * (xe - xl) - 60, d.cap, 0.42), debut='v', fin='v')], d.Lr + W + d.Lr * 0.5


def Dd(d):
    W = 640 + d.g; xs, xb, top, bas = _rep(d, W)
    R = d.R(2 * (xb - xs) - 60, d.cap, 0.44)
    return [T([(xs, bas), (xs, top), (xb, top), (xb, bas)], r=[d.c, d.c, R, R], ferme=True)], d.L + W + d.Lr


def E(d):
    W = 480 + d.g * 0.8; xs, _, top, bas = _rep(d, W); xr = d.L + W
    return [T([(xr, top), (xs, top), (xs, bas), (xr, bas)], r=d.c),
            barre(xs + d.Fg / 2 - J, xr - 40, d.taille())], d.L + W + d.Lr * 0.8


def F(d):
    """Le seul geste de Sibard : la barre du milieu s'élargit un peu vers la droite."""
    W = 460 + d.g * 0.8; xs, _, top, bas = _rep(d, W); xr = d.L + W
    return [T([(xr, top), (xs, top), (xs, 0)], r=d.c),
            T([(xs, d.taille()), (xr - 50, d.taille())], k=[0.5, 1], ep=d.B * 1.5 + d.F * 0.09, plein=True, fin='v')], d.L + W + d.Lr * 0.5


def G(d):
    W = 660 + d.g; xl, xr, top, bas = _rep(d, W, True)
    xe = d.Lr + W - 10; ym = max(d.taille() * 1.1, bas + 120)
    R = d.R(xr - xl, d.cap, 0.42)
    return [T([(xe, top), (xl, top), (xl, bas), (xr, bas), (xr, ym + d.B / 2)], r=[R, R, min(R, ym - bas - 4)], debut='v', fin='h'),
            T([(xr - (xr - xl) * 0.42, ym), (xr, ym)], debut='v', fin='v')], d.Lr + W + d.Lr * 0.9


def H(d):
    W = 620 + d.g; xl, xr, top, bas = _rep(d, W)
    return [fut(xl, 0, d.cap), fut(xr, 0, d.cap),
            barre(xl + d.Fg / 2 - J, xr - d.Fd / 2 + J, d.taille())], d.L + W + d.L


def I(d):
    xs = d.L + 40 + d.Fm / 2
    return [fut(xs, 0, d.cap)], d.L + 40 + d.Fm + d.L


def Jj(d):
    W = max(380 + d.g * 0.6, d.Fm + 170); L = d.Lr * 0.6; xr = L + W - d.Fm / 2; bas = d.bas(True)
    return [T([(xr, d.cap), (xr, bas), (L, bas)], r=d.R(2 * (W - d.Fm) - 30, d.cap, 0.42), fin='v', ep=(d.Fm, d.B))], L + W + d.L


def K(d):
    return _k(d, d.cap, d.cap)


def Ll(d):
    W = 440 + d.g * 0.7; xs = d.L + d.Fg / 2; xr = d.L + W
    return [T([(xs, d.cap), (xs, d.bas()), (xr, d.bas())], r=d.c, fin='v')], d.L + W + d.Lr * 0.5


def M(d):
    W = 780 + d.g * 1.3; xl, xr, top, bas = _rep(d, W); xc = (xl + xr) / 2 - d.F * 0.15
    return [T([(xl, 0), (xl, d.cap - d.B * 0.42), (xc, d.cap * 0.20), (xr, d.cap - d.Fd * 0.40 + 4), (xr, 0)], r=[d.c * 0.4, d.c * 0.6, d.c * 0.4])], d.L + W + d.L


def N(d):
    W = 640 + d.g; xl, xr, top, bas = _rep(d, W)
    return [fut(xl, 0, d.cap), fut(xr, 0, d.cap),
            T([(xl, d.cap), (xr - d.Fd * 0.2, d.B * 0.5)], k=[0.3, 1], ep=(d.F * 1.25, d.B), debut='h', fin='h')], d.L + W + d.L


def O(d):
    W = 700 + d.g * 1.1; xl, xr, top, bas = _rep(d, W, True)
    R = d.R(xr - xl, d.cap, 0.43)
    return [T([(xl, bas), (xl, top), (xr, top), (xr, bas)], r=R, ferme=True)], d.Lr + W + d.Lr


def P(d):
    W = 540 + d.g * 0.9; xs, xb, top, bas = _rep(d, W)
    yj = d.taille(); R = max((top - yj) / 2 - 1, 1)
    return [T([(xs, 0), (xs, top), (xb, top), (xb, yj), (xs + d.Fg / 2 - J, yj)], r=[d.c, R, R])], d.L + W + d.Lr * 0.6


def Q(d):
    W = 700 + d.g * 1.1; xl, xr, top, bas = _rep(d, W, True)
    R = d.R(xr - xl, d.cap, 0.43); e = d.F * 0.34; yq = bas - d.B / 2 - e / 2 + J
    return [T([(xl, bas), (xl, top), (xr, top), (xr, bas)], r=R, ferme=True),
            _signe(T([((xl + xr) / 2 + 20, yq), (d.Lr + W, yq)], ep=e, debut='v', fin='v'))], d.Lr + W + d.Lr


def R(d):
    W = 540 + d.g * 0.9; xs, xb, top, bas = _rep(d, W)
    yj = d.taille(); Rr = max((top - yj) / 2 - 1, 1)
    return [T([(xs, 0), (xs, top), (xb, top), (xb, yj), (xs + d.Fg / 2 - J, yj)], r=[d.c, Rr, Rr]),
            T([(xs + (xb - xs) * 0.45, yj), (d.L + W, 0)], debut='h', fin='h', ep=(d.F * 1.3, d.B))], d.L + W + d.Lr * 0.6


def S(d):
    return _s(d, d.cap, 540 + d.g * 0.9)


def Tt(d):
    W = 540 + d.g * 0.8; L = d.Lr * 0.6; xc = L + W / 2; top = d.haut(d.cap)
    return [barre(L, L + W, top), fut(xc, 0, top - d.B / 2 + J)], L + W + L


def U(d):
    W = 620 + d.g; xl, xr, top, bas = _rep(d, W)
    bas = d.bas(True)
    return [T([(xl, d.cap), (xl, bas), (xr, bas), (xr, d.cap)], r=d.R(xr - xl, d.cap, 0.42))], d.L + W + d.L


def V(d):
    return _v(d, d.cap, 620 + d.g, d.Lr * 0.4)


def W(d):
    return _w(d, d.cap, 900 + d.g * 1.6, d.Lr * 0.4)


def X(d):
    return _x(d, d.cap, 600 + d.g, d.Lr * 0.5)


def Y(d):
    W = 600 + d.g; L = d.Lr * 0.4; xl, xr = d.gd(W, L); xc = (xl + xr) / 2 + d.F * 0.2
    ym = d.cap * 0.42
    a0, a1 = (xr, d.cap), (xc, ym)
    return [T([a0, a1, (xc, 0)], r=d.c * 0.5, debut='h', fin='h', ep=(d.Fd, d.B)),
            T([(xl, d.cap), (xc - d.F * 0.3, ym + 30)], debut='h', fin=d.contre(a0, a1, 1), ep=(d.Fg, d.B))], L + W + L


def Z(d):
    return _z(d, d.cap, 560 + d.g * 0.9, d.Lr * 0.8)


# --- les capitales en plus

def AE(d):
    W = 860 + d.g * 1.4; L = d.Lr * 0.5
    xl = L + d.Fg / 2; xc = L + W * 0.50; xr = L + W; top = d.haut(d.cap); bas = d.bas()
    ym = d.taille() * 0.92; k = ym / d.cap
    a0, a1 = (xl, 0), (xc, d.cap)
    return [T([a0, a1], debut='h', fin='h', ep=(d.Fg, d.B)),
            fut(xc, 0, d.cap, ep=(d.F * 1.2, d.B)),
            T([(xl + (xc - xl) * k, ym), (xc - d.F * 0.6 + J, ym)], debut=d.contre(a0, a1, -1)),
            barre(xc + d.F * 0.6 - J, xr, top), barre(xc + d.F * 0.6 - J, xr, bas),
            barre(xc + d.F * 0.6 - J, xr - 40, d.taille())], L + W + d.Lr * 0.8


def OE(d):
    W = 900 + d.g * 1.5; xl = d.Lr + d.Fg / 2; xc = d.Lr + W * 0.50; xr = d.Lr + W; top = d.haut(d.cap, True); bas = d.bas(True)
    R = d.R(xc - xl, d.cap, 0.43)
    return [T([(xl, bas), (xl, top), (xc, top), (xc, bas)], r=R, ferme=True),
            barre(xc + d.F / 2 - J, xr, d.haut(d.cap)), barre(xc + d.F / 2 - J, xr, d.bas()),
            barre(xc + d.F / 2 - J, xr - 40, d.taille())], d.Lr + W + d.Lr * 0.8


def Oslash(d):
    W = 700 + d.g * 1.1; xl, xr, top, bas = _rep(d, W, True)
    R = d.R(xr - xl, d.cap, 0.43)
    return [T([(xl, bas), (xl, top), (xr, top), (xr, bas)], r=R, ferme=True),
            _signe(T([(d.Lr + 20, -50), (d.Lr + W - 20, d.cap + 50)], plein=True, ep=d.B * 1.3, debut='h', fin='h'))], d.Lr + W + d.Lr


def Eth(d):
    t, ch = Dd(d)
    xs = d.L + d.Fg / 2
    t.append(_signe(barre(xs - d.Fg / 2 - 60, xs + 190, d.cap * 0.5, plein=True, ep=d.B * 1.3)))
    return t, ch


def Thorn(d):
    W = 520 + d.g * 0.9; xs, xb, top, bas = _rep(d, W)
    y1 = d.cap * 0.78; y0 = d.cap * 0.24; Rr = max((y1 - y0) / 2 - 1, 1)
    return [fut(xs, 0, d.cap),
            T([(xs + d.Fg / 2 - J, y1), (xb, y1), (xb, y0), (xs + d.Fg / 2 - J, y0)], r=Rr)], d.L + W + d.Lr * 0.6


def Lslash(d):
    t, ch = Ll(d)
    xs = d.L + d.Fg / 2
    t.append(_signe(T([(xs - 90, d.cap * 0.40), (xs + 150, d.cap * 0.58)], plein=True, ep=d.B * 1.3, debut='v', fin='v')))
    return t, ch


def Hbar(d):
    t, ch = H(d)
    W = 620 + d.g; xl, xr, top, bas = _rep(d, W)
    t.append(_signe(barre(xl - 50, xr + d.Fd / 2 + 30, d.cap * 0.80, plein=True, ep=d.B)))
    return t, ch


def Germandbls(d):
    W = 600 + d.g; xl, xr, top, bas = _rep(d, W); xa = xl + (xr - xl) * 0.62
    top = d.haut(d.cap, True); bas = d.bas(True); ym = d.cap * 0.56
    rj = 30; rl = max((ym - bas) / 2 - 1, 1); ra = d.R(xa - xl, d.cap, 0.3)
    return [T([(xl, 0), (xl, top), (xa, top), (xa, ym), (xr, ym), (xr, bas), (xl + d.Fg / 2 + 60, bas)],
              r=[ra, ra, rj, rl, rl], fin='v')], d.L + W + d.Lr


CAPITALES = {'A': A, 'B': B, 'C': C, 'D': Dd, 'E': E, 'F': F, 'G': G, 'H': H, 'I': I, 'J': Jj, 'K': K, 'L': Ll,
             'M': M, 'N': N, 'O': O, 'P': P, 'Q': Q, 'R': R, 'S': S, 'T': Tt, 'U': U, 'V': V, 'W': W, 'X': X,
             'Y': Y, 'Z': Z, 'Æ': AE, 'Œ': OE, 'Ø': Oslash, 'Ð': Eth, 'Þ': Thorn, 'Ł': Lslash, 'Đ': Eth,
             'Ħ': Hbar, 'ẞ': Germandbls}
