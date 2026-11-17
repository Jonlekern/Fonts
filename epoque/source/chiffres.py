# Les chiffres d'Époque : même chasse pour tous (ils s'alignent en colonnes), contraste Art déco.
from tuyaux import Tuyau as T
from dessin import D, fut, barre, retourne, JOINT as J
from minuscules import _signe


def _rep(d):
    W = 500 + d.g * 0.8
    xl, xr = d.gd(W, d.Lr)
    return W, xl, xr, d.haut(d.cap, True), d.bas(True)


def _chasse(d):
    return 2 * d.Lr + 500 + d.g * 0.8


def zero(d):
    W, xl, xr, top, bas = _rep(d)
    return [T([(xl, bas), (xl, top), (xr, top), (xr, bas)], r=d.R(xr - xl, d.cap, 0.36), ferme=True)], _chasse(d)


def un(d):
    """Signature : un drapeau fin, comme sur les voitures de course."""
    W, xl, xr, top, bas = _rep(d)
    xs = d.Lr + W * 0.56
    return [fut(xs, 0, d.cap),
            _signe(T([(xs - d.Fm / 2 - 130, d.cap - 150), (xs - d.Fm / 2 + J + 6, d.cap - d.B * 0.6)], ep=d.B * 1.3, plein=True, fin='v'))], _chasse(d)


def deux(d):
    W, xl, xr, top, bas = _rep(d)
    ym = d.cap * 0.56; R = d.R(xr - xl, d.cap, 0.30)
    return [T([(xl, top - R - 20), (xl, top), (xr, top), (xr, ym), (xl + 10, d.bas()), (d.Lr + W + 10, d.bas())],
              r=[R, R, R * 0.9, d.c * 0.3], debut='h', k=[0.3, 1, 1, 1, 1, 1])], _chasse(d)


def trois(d):
    W, xl, xr, top, bas = _rep(d)
    ym = d.cap * 0.54; xr1 = xr - (xr - xl) * 0.08
    r1 = max((top - ym) / 2 - 1, 1); r2 = max((ym - bas) / 2 - 1, 1)
    return [T([(xl + 30, top), (xr1, top), (xr1, ym), (xl + (xr - xl) * 0.42, ym)], r=r1, debut='v'),
            T([(xr1 - r1 - 2, ym), (xr, ym), (xr, bas), (xl - 10, bas)], r=r2, k=[1, 1, 1, 0], fin='v')], _chasse(d)


def quatre(d):
    W, xl, xr, top, bas = _rep(d)
    xs = xr - (xr - xl) * 0.10; y4 = d.cap * 0.30
    return [fut(xs, 0, d.cap, ep=(d.Fd, d.B)),
            T([(xs - d.Fd / 2 + J, d.cap - 10), (xl - 10, y4), (d.Lr + W + 20, y4)], r=d.c * 0.3, debut='v', ep=(d.B * 1.4, d.B), plein=True)], _chasse(d)


def cinq(d):
    W, xl, xr, top, bas = _rep(d)
    ym = d.cap * 0.60; R = max((ym - bas) / 2 - 1, 1)
    xl2 = xl + (xr - xl) * 0.08
    return [T([(d.Lr + W - 20, d.haut(d.cap)), (xl2, d.haut(d.cap)), (xl2, ym), (xr, ym), (xr, bas), (xl - 10, bas)],
              r=[d.c * 0.3, d.c * 0.3, R, R], k=[1, 1, 1, 1, 1, 0], fin='v')], _chasse(d)


def six(d):
    W, xl, xr, top, bas = _rep(d)
    y6 = d.cap * 0.60; R6 = d.R(xr - xl, y6, 0.46); R = d.R(xr - xl, d.cap, 0.36)
    return [T([(xl, bas), (xl, y6), (xr, y6), (xr, bas)], r=R6, ferme=True),
            T([(xl, y6 / 2), (xl, top), (xr - 20, top)], r=R, k=[1, 1, 0], fin='v')], _chasse(d)


def sept(d):
    W, xl, xr, top, bas = _rep(d)
    return [T([(d.Lr, d.haut(d.cap)), (xr + d.Fd * 0.3, d.haut(d.cap)), (xl + (xr - xl) * 0.42, 0)], r=d.c * 0.3, fin='h', ep=(d.Fd, d.B))], _chasse(d)


def huit(d):
    W, xl, xr, top, bas = _rep(d)
    ym = d.cap * 0.54; dx = (xr - xl) * 0.06
    return [T([(xl, bas), (xl, ym), (xr, ym), (xr, bas)], r=max((ym - bas) / 2 - 1, 1), ferme=True),
            T([(xl + dx, ym), (xl + dx, top), (xr - dx, top), (xr - dx, ym)], r=max((top - ym) / 2 - 1, 1), ferme=True)], _chasse(d)


def neuf(d):
    t, ch = six(d)
    return retourne(t, ch / 2, d.cap / 2), ch


CHIFFRES = {'0': zero, '1': un, '2': deux, '3': trois, '4': quatre, '5': cinq, '6': six, '7': sept, '8': huit, '9': neuf}
