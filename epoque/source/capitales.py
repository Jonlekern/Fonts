# Les capitales d'Époque. Chaque fonction rend (tuyaux, chasse).
from tuyaux import Tuyau as T
from dessin import D, fut, barre, JOINT as J
from minuscules import _k, _v, _w, _x, _z, s as _s


def _rep(d, W, rond=False):
    """Gauche, droite (axes des fûts), haut, bas (axes des barres)."""
    L = d.Lr if rond else d.L
    return L + d.F / 2, L + W - d.F / 2, d.haut(d.cap, rond), d.bas(rond)


def A(d):
    W = 640 + d.g; L = d.Lr * 0.4
    xl = L + d.F * 0.52; xr = L + W - d.F * 0.52; xc = (xl + xr) / 2; yh = d.cap - d.B * 0.42 + d.d
    ym = d.taille() * 0.92
    k = ym / yh
    a0, a1, a2 = (xl, 0), (xc, yh), (xr, 0)
    return [T([a0, a1, a2], r=d.c * 0.5, debut='h', fin='h'),
            T([(xl + (xc - xl) * k, ym), (xr - (xr - xc) * k, ym)], debut=d.contre(a0, a1, -1), fin=d.contre(a1, a2, -1))], L + W + L


def B(d):
    W = 540 + d.g * 0.9; xs, xb, top, bas = _rep(d, W)
    yj = d.taille() + (d.cap * 0.5 - d.taille()) * 0.55        # la taille du B, un peu plus haute : deux panses qui tiennent
    xa = xs + d.c + 6                                          # où finit le coude du dos
    xb1 = xb - (W - d.F) * 0.07
    r1 = max(min((top - yj) / 2 - 1, xb1 - xa - 2), 1); r2 = max(min((yj - bas) / 2 - 1, xb - xa - 2), 1)
    return [T([(xa + 4, top), (xs, top), (xs, bas), (xa + 4, bas)], r=d.c),
            T([(xa, top), (xb1, top), (xb1, yj), (xs + d.F / 2 - J, yj)], r=r1),
            T([(xa, bas), (xb, bas), (xb, yj), (xb1 - r1, yj)], r=r2)], d.L + W + d.Lr


def C(d):
    W = 620 + d.g; xl, xr, top, bas = _rep(d, W, True)
    xe = d.Lr + W - 8
    return [T([(xe, top), (xl, top), (xl, bas), (xe, bas)], r=d.R(2 * (xe - xl) - 60, d.cap, 0.40))], d.Lr + W + d.Lr * 0.6


def Dd(d):
    W = 640 + d.g; xs, xb, top, bas = _rep(d, W)
    R = d.R(2 * (xb - xs) - d.c * 2 - 40, d.cap, 0.42)
    return [T([(xs, bas), (xs, top), (xb, top), (xb, bas)], r=[d.c, d.c, R, R], ferme=True)], d.L + W + d.Lr


def E(d, barre_mi=True):
    W = 500 + d.g * 0.8; xs, _, top, bas = _rep(d, W); xr = d.L + W
    t = [T([(xr, top), (xs, top), (xs, bas), (xr, bas)], r=d.c)]
    if barre_mi:
        t.append(barre(xs + d.F / 2 - J, xr - 54, d.taille()))
    return t, d.L + W + d.Lr * 0.7


def F(d):
    W = 480 + d.g * 0.8; xs, _, top, bas = _rep(d, W); xr = d.L + W
    return [T([(xr, top), (xs, top), (xs, 0)], r=d.c),
            barre(xs + d.F / 2 - J, xr - 54, d.taille())], d.L + W + d.Lr * 0.5


def G(d):
    W = 660 + d.g; xl, xr, top, bas = _rep(d, W, True)
    xe = d.Lr + W - 14; ym = max(d.taille(), bas + 1.9 * d.B)
    R = d.R(xr - xl, d.cap, 0.40)
    return [T([(xe, top), (xl, top), (xl, bas), (xr, bas), (xr, ym), (xr - (xr - xl) * 0.42, ym)],
              r=[R, R, min(R, (ym - bas) - d.c * 0.5 - 2), d.c * 0.5])], d.Lr + W + d.Lr * 0.9


def H(d):
    W = 620 + d.g; xl, xr, top, bas = _rep(d, W)
    return [fut(xl, 0, d.cap), fut(xr, 0, d.cap), barre(xl + d.F / 2 - J, xr - d.F / 2 + J, d.taille())], d.L + W + d.L


def I(d):
    return [fut(d.L + d.F / 2, 0, d.cap)], 2 * d.L + d.F


def Jj(d):
    W = 400 + d.g * 0.6; xr = d.Lr * 0.6 + W - d.F / 2; bas = d.bas(True)
    return [T([(xr, d.cap), (xr, bas), (d.Lr * 0.6, bas)], r=d.R(2 * (W - d.F) - 30, d.cap, 0.40), fin='v')], d.Lr * 0.6 + W + d.L


def K(d):
    return _k(d, d.cap, d.cap)


def Ll(d):
    W = 460 + d.g * 0.7; xs, _, top, bas = _rep(d, W); xr = d.L + W
    return [T([(xs, d.cap), (xs, bas), (xr, bas)], r=d.c)], d.L + W + d.Lr * 0.4


def M(d):
    W = 760 + d.g * 1.3; xl, xr, top, bas = _rep(d, W); xc = (xl + xr) / 2
    yh = d.cap - d.B * 0.42
    return [T([(xl, 0), (xl, yh), (xc, d.cap * 0.22), (xr, yh), (xr, 0)], r=d.c * 0.45)], d.L + W + d.L


def N(d):
    W = 640 + d.g; xl, xr, top, bas = _rep(d, W)
    return [T([(xl, 0), (xl, d.cap - d.B * 0.42), (xr, d.B * 0.42), (xr, d.cap)], r=d.c * 0.45)], d.L + W + d.L


def O(d):
    W = 700 + d.g * 1.1; xl, xr, top, bas = _rep(d, W, True)
    return [T([(xl, bas), (xl, top), (xr, top), (xr, bas)], r=d.R(xr - xl, d.cap, 0.41), ferme=True)], d.Lr + W + d.Lr


def P(d):
    W = 540 + d.g * 0.9; xs, xb, top, bas = _rep(d, W)
    yj = d.taille(); R = max(min((top - yj) / 2 - 1, xb - xs - d.c - 4), 1)
    return [T([(xs, 0), (xs, top), (xb, top), (xb, yj), (xs + d.F / 2 - J, yj)], r=[d.c, R, R])], d.L + W + d.Lr * 0.6


def Q(d):
    t, ch = O(d)
    W = ch - 2 * d.Lr; cx = d.Lr + W * 0.60
    t.append(T([(cx, d.bas(True) - d.B / 2 + J), (cx + 150, -150)], debut='h', fin='h'))
    return t, ch


def R(d):
    t, ch = P(d)
    W = 540 + d.g * 0.9; xs, xb, top, bas = _rep(d, W)
    yj = d.taille(); x0 = xs + (xb - xs) * 0.42
    t.append(T([(x0, yj - d.B / 2 + J), (d.L + W - d.F * 0.5, 0)], debut='h', fin='h'))
    return t, d.L + W + d.Lr * 0.5


def S(d):
    return _s(d, d.cap, 540 + d.g * 0.9)


def Tt(d):
    W = 560 + d.g * 0.8; L = d.Lr * 0.6; xc = L + W / 2; top = d.haut(d.cap)
    return [barre(L, L + W, top), fut(xc, 0, top - d.B / 2 + J)], L + W + L


def U(d):
    W = 620 + d.g; xl, xr, top, bas = _rep(d, W)
    bas = d.bas(True)
    return [T([(xl, d.cap), (xl, bas), (xr, bas), (xr, d.cap)], r=d.R(xr - xl, d.cap, 0.40))], d.L + W + d.L


def V(d):
    return _v(d, d.cap, 620 + d.g, d.Lr * 0.4)


def W(d):
    return _w(d, d.cap, 900 + d.g * 1.6, d.Lr * 0.4)


def X(d):
    return _x(d, d.cap, 600 + d.g, d.Lr * 0.5)


def Y(d):
    W = 600 + d.g; L = d.Lr * 0.4; xl = L + d.F * 0.52; xr = L + W - d.F * 0.52; xc = (xl + xr) / 2
    ym = d.cap * 0.40
    a0, a1 = (xl, d.cap), (xc, ym)
    return [T([a0, a1, (xc, 0)], r=d.c * 0.5, debut='h'),
            T([(xr, d.cap), (xc, ym)], debut='h', fin=d.contre(a0, a1, -1))], L + W + L


def Z(d):
    return _z(d, d.cap, 560 + d.g * 0.9, d.Lr * 0.8)


CAPITALES = {'A': A, 'B': B, 'C': C, 'D': Dd, 'E': E, 'F': F, 'G': G, 'H': H, 'I': I, 'J': Jj, 'K': K, 'L': Ll,
             'M': M, 'N': N, 'O': O, 'P': P, 'Q': Q, 'R': R, 'S': S, 'T': Tt, 'U': U, 'V': V, 'W': W, 'X': X,
             'Y': Y, 'Z': Z}
