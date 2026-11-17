# Époque, deuxième jet : des blocs carénés (la structure, années 30), chaque lettre signée d'un geste
# d'emblème chromé (années 50). Essai sur quelques capitales.
from tuyaux import Tuyau as T
from dessin import D, fut, barre, JOINT as J


def _rep(d, W):
    return d.L + d.F / 2, d.L + W - d.F / 2, d.haut(d.cap), d.bas()


def E(d):
    """Signature : la barre du milieu part en flèche."""
    W = 330; xs, _, top, bas = _rep(d, W); xr = d.L + W; ym = d.cap * 0.42
    return [T([(xr, top), (xs, top), (xs, bas), (xr, bas)], r=d.c),
            T([(xs + d.F / 2 - J, ym), (xr + 36, ym)], k=[1, 0])], d.L + W + d.L


def P(d, aile=True):
    """Signature : la barre de taille sort à gauche, en aile."""
    W = 400; xs, xb, top, bas = _rep(d, W); yj = d.cap * 0.40
    R = max((top - yj) / 2 - 1, 1)
    t = [T([(xs, 0), (xs, top), (xb, top), (xb, yj), (xs + d.F / 2 - J, yj)], r=[d.c, R, R])]
    if aile:
        t.append(T([(xs - d.F / 2 - 84, yj), (xs - d.F / 2 + J, yj)], k=[0, 1])); t[-1].hors = True
    return t, d.L + W + d.L * 0.8


def O(d):
    """Signature : le vide est une fente, décalée vers la gauche."""
    W = 430; xl, xr, top, bas = _rep(d, W)
    return [T([(xl, bas), (xl, top), (xr, top), (xr, bas)], r=min(120, (xr - xl) / 2 - 2), ferme=True)], d.L + W + d.L


def Q(d):
    """Signature : la queue file à l'horizontale, loin à droite."""
    t, ch = O(d)
    W = 430; xl, xr, top, bas = _rep(d, W); e = d.B * 0.8
    t.append(T([(xl + 60, bas - d.B / 2 - e / 2 + J), (xr + 210, bas - d.B / 2 - e / 2 + J)], ep=e, k=[1, 0], debut='v')); t[-1].hors = True
    return t, ch


def U(d):
    """Signature : le bras gauche est plus court, coupé en biais."""
    W = 420; xl, xr, top, bas = _rep(d, W)
    return [T([(xl, d.cap - 70), (xl, bas), (xr, bas), (xr, d.cap)], r=min(120, (xr - xl) / 2 - 2),
              debut=((xl, d.cap - 70), (1, 0.5)))], d.L + W + d.L


def S(d):
    """Signature : les deux bouts tranchés en biais."""
    W = 380; xl, xr, top, bas = _rep(d, W)
    mid = (top + bas) / 2 + 8; ra = (top - mid) / 2; rb = (mid - bas) / 2
    return [T([(d.L + W - 6, top), (xl, top), (xl, mid), (xr, mid), (xr, bas), (d.L + 6, bas)], r=[ra, ra, rb, rb],
              debut=((d.L + W - 6, top), (0.5, 1)), fin=((d.L + 6, bas), (0.5, 1)))], d.L + W + d.L


def K(d):
    """Signature : les bras ne touchent pas le fût."""
    W = 430; xs = d.L + d.F / 2; xr = d.L + W; ym = d.cap * 0.42; jour = 18
    a0 = (xs + d.F / 2 + jour, ym); a1 = (xr - d.F * 0.5, d.cap)
    p = (a0[0] + (a1[0] - a0[0]) * 0.22, a0[1] + (a1[1] - a0[1]) * 0.22)
    return [fut(xs, 0, d.cap),
            T([a0, a1], debut='v', fin='h'),
            T([p, (xr - d.F * 0.45, 0)], debut=d.contre(a0, a1, -1), fin='h')], d.L + W + d.L * 0.5


def Y(d):
    """Signature : la fourche est basse et la branche droite monte plus haut, en pointe."""
    W = 420; xl = d.L + d.F / 2; xr = d.L + W - d.F * 0.4; xc = d.L + W * 0.46; ym = d.cap * 0.34
    a0, a1 = (xl, d.cap), (xc, ym)
    return [T([a0, a1, (xc, 0)], r=d.c, debut='h'),
            T([(xr, d.cap + 46), (xc + d.F * 0.2, ym + 40)], k=[0.25, 1], debut='h', fin=d.contre(a0, a1, 1))], d.L + W + d.L * 0.5


def Ll(d):
    """Signature : le pied s'effile vers la droite."""
    W = 330; xs = d.L + d.F / 2; xr = d.L + W
    return [T([(xs, d.cap), (xs, d.bas()), (xr + 60, d.bas())], r=d.c, k=[1, 1, 0.12], fin='v')], d.L + W + d.L * 0.9


def A(d):
    """Signature : une arche, et la barre très basse sort à gauche en aile."""
    W = 420; xl, xr, top, bas = _rep(d, W); yb = d.cap * 0.27
    t = [T([(xl, 0), (xl, top), (xr, top), (xr, 0)], r=min(130, (xr - xl) / 2 - 2)),
         T([(xl - d.F / 2 - 80, yb), (xr - d.F / 2 + J, yb)], k=[0, 1])]
    t[-1].hors = True
    return t, d.L + W + d.L


def R(d):
    """Signature : la jambe est détachée et part en ruade."""
    t, ch = P(d, aile=False)
    W = 400; xs, xb, top, bas = _rep(d, W); yj = d.cap * 0.40
    t.append(T([(xs + d.F * 0.9, yj - d.B / 2 - 18), (d.L + W + 26, 0)], debut='h', fin='h', k=[0.72, 1.05]))
    return t, d.L + W + d.L


BLOCS = {'A': A, 'E': E, 'K': K, 'L': Ll, 'O': O, 'P': P, 'Q': Q, 'R': R, 'S': S, 'U': U, 'Y': Y}
