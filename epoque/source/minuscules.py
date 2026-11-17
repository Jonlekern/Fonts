# Les minuscules d'Époque. Chaque fonction rend (tuyaux, chasse).
from tuyaux import Tuyau as T
from dessin import D, fut, barre, point, JOINT as J


def _rond(d, W=None):
    """Les repères d'une lettre ronde de la hauteur d'x : gauche, droite, haut, bas, rayon."""
    W = (468 + d.g * 0.8) if W is None else W
    xl = d.Lr + d.F / 2; xr = d.Lr + W - d.F / 2
    return W, xl, xr, d.haut(d.x, True), d.bas(True), d.R(xr - xl)


def a(d):
    W, xl, xr, top, bas, R = _rond(d)
    return [fut(xr, 0, d.x),
            T([(xr - d.F / 2 + J, top), (xl, top), (xl, bas), (xr - d.F / 2 + J, bas)], r=R)], d.Lr + W + d.L


def b(d, h=None):
    W, xl, xr, top, bas, R = _rond(d)
    dx = d.L - d.Lr; xl += dx; xr += dx
    return [fut(xl, 0, d.asc if h is None else h),
            T([(xl + d.F / 2 - J, top), (xr, top), (xr, bas), (xl + d.F / 2 - J, bas)], r=R)], d.L + W + d.Lr


def c(d):
    W, xl, xr, top, bas, R = _rond(d, 440 + d.g * 0.7)
    xe = d.Lr + W
    return [T([(xe, top), (xl, top), (xl, bas), (xe, bas)], r=R)], d.Lr + W + d.Lr * 0.6


def dd(d):
    W, xl, xr, top, bas, R = _rond(d)
    return [fut(xr, 0, d.asc),
            T([(xr - d.F / 2 + J, top), (xl, top), (xl, bas), (xr - d.F / 2 + J, bas)], r=R)], d.Lr + W + d.L


def e(d):
    W, xl, xr, top, bas, R = _rond(d)
    ym = max(d.x * 0.47, 2.0 * d.B)
    r2 = max(min(R, (top - ym) / 2 - 1), 1)
    return [T([(xl + d.F / 2 - J, ym), (xr, ym), (xr, top), (xl, top), (xl, bas), (d.Lr + W - 8, bas)],
              r=[min(d.c * 0.6, r2), min(R, 2 * r2 - min(d.c * 0.6, r2)), R, R], fin='v'),
            d.sillage(xl, ym)], d.Lr + W + d.Lr * 0.7


def f(d):
    W = 300 + d.g * 0.45; xs = d.Lr + 62 + d.F / 2; xr = d.Lr + W; yb = d.haut(d.x)
    return [T([(xr, d.haut(d.asc, True)), (xs, d.haut(d.asc, True)), (xs, 0)], r=min(d.R(2 * (xr - xs)), xr - xs - 6), debut='v'),
            barre(d.Lr - d.m['sillage'], xs - d.F / 2 + J, yb), barre(xs + d.F / 2 - J, xr - 6, yb)], d.Lr + W + 4


def g(d):
    W, xl, xr, top, bas, R = _rond(d)
    yd = d.bas(True, d.desc)
    return [T([(xr, d.x), (xr, yd), (xl - d.F / 2 + 26, yd)], r=min(R, (0 - d.desc) * 0.62), fin='v'),
            T([(xr - d.F / 2 + J, top), (xl, top), (xl, bas), (xr - d.F / 2 + J, bas)], r=R)], d.Lr + W + d.L


def h(d):
    W = 456 + d.g * 0.8; xl = d.L + d.F / 2; xr = d.L + W - d.F / 2; top = d.haut(d.x, True)
    return [fut(xl, 0, d.asc), T([(xl + d.F / 2 - J, top), (xr, top), (xr, 0)], r=d.R(2 * (xr - xl) - d.F))], d.L + W + d.L


def _i(d, pt=True):
    xs = d.L + d.F / 2
    t = [fut(xs, 0, d.x)]
    if pt:
        t.append(point(xs, d.x + 60 + d.F * 0.62, d.F * 1.16))
    return t, 2 * d.L + d.F


def i(d):
    return _i(d)


def dotlessi(d):
    return _i(d, False)


def _j(d, pt=True):
    W = 250 + d.g * 0.4; xs = d.Lr + W - d.F / 2; yd = d.bas(True, d.desc)
    t = [T([(xs, d.x), (xs, yd), (d.Lr - 30, yd)], r=min(d.R(2 * (W - d.F)), (0 - d.desc) * 0.62), fin='v')]
    if pt:
        t.append(point(xs, d.x + 60 + d.F * 0.62, d.F * 1.16))
    return t, d.Lr + W + d.L


def j(d):
    return _j(d)


def dotlessj(d):
    return _j(d, False)


def _k(d, h, xh):
    """Le k et le K : un fût, un bras qui bute contre lui, une jambe qui bute sous le bras."""
    W = (430 if xh == d.x else 560) + d.g * 0.8; xl = d.L + d.F / 2; xr = d.L + W
    ym = xh * 0.40 if xh == d.x else d.taille()
    a0 = (xl + d.F / 2 - J, ym); a1 = (xr - d.F * 0.55, xh)
    ep = d.ep(a0, a1)
    # la jambe part du bras, à un tiers de sa longueur
    k = 0.30
    p = (a0[0] + (a1[0] - a0[0]) * k, a0[1] + (a1[1] - a0[1]) * k)
    return [fut(xl, 0, h),
            T([a0, a1], debut='v', fin='h'),
            T([p, (xr - d.F * 0.5, 0)], debut=d.contre(a0, a1, -1), fin='h')], d.L + W + d.Lr * 0.3


def k(d):
    return _k(d, d.asc, d.x)


def l(d):
    return [fut(d.L + d.F / 2, 0, d.asc)], 2 * d.L + d.F


def m(d):
    W = 720 + d.g * 1.45; xl = d.L + d.F / 2; xr = d.L + W - d.F / 2; xm = (xl + xr) / 2; top = d.haut(d.x, True)
    R = d.R(xm - xl)
    return [T([(xl, 0), (xl, top), (xm, top), (xm, 0)], r=R),
            T([(xm + d.F / 2 - J, top), (xr, top), (xr, 0)], r=R)], d.L + W + d.L


def n(d):
    W = 456 + d.g * 0.8; xl = d.L + d.F / 2; xr = d.L + W - d.F / 2; top = d.haut(d.x, True)
    return [T([(xl, 0), (xl, top), (xr, top), (xr, 0)], r=d.R(xr - xl))], d.L + W + d.L


def o(d):
    W, xl, xr, top, bas, R = _rond(d, 480 + d.g * 0.85)
    return [T([(xl, bas), (xl, top), (xr, top), (xr, bas)], r=R, ferme=True)], d.Lr + W + d.Lr


def p(d):
    W, xl, xr, top, bas, R = _rond(d)
    dx = d.L - d.Lr; xl += dx; xr += dx
    return [fut(xl, d.desc, d.x),
            T([(xl + d.F / 2 - J, top), (xr, top), (xr, bas), (xl + d.F / 2 - J, bas)], r=R)], d.L + W + d.Lr


def q(d):
    W, xl, xr, top, bas, R = _rond(d)
    return [fut(xr, d.desc, d.x),
            T([(xr - d.F / 2 + J, top), (xl, top), (xl, bas), (xr - d.F / 2 + J, bas)], r=R)], d.Lr + W + d.L


def r(d):
    W = 300 + d.g * 0.5; xl = d.L + d.F / 2; xr = d.L + W; top = d.haut(d.x, True)
    return [T([(xl, 0), (xl, top), (xr, top)], r=min(d.R(2 * (xr - xl)), xr - xl - 8), fin='v')], d.L + W + 8


def s(d, h=None, W=None):
    h = d.x if h is None else h
    W = (410 + d.g * 0.75) if W is None else W
    xl = d.Lr + d.F / 2; xr = d.Lr + W - d.F / 2; top = d.haut(h, True); bas = d.bas(True)
    mid = (top + bas) / 2 + h * 0.012
    ra = (top - mid) / 2; rb = (mid - bas) / 2
    return [T([(d.Lr + W - 10, top), (xl, top), (xl, mid), (xr, mid), (xr, bas), (d.Lr + 6, bas)],
              r=[ra, ra, rb, rb], debut='v', fin='v')], d.Lr + W + d.Lr


def t(d):
    W = 300 + d.g * 0.45; xs = d.Lr + 62 + d.F / 2; xr = d.Lr + W; bas = d.bas(True); yb = d.haut(d.x)
    return [T([(xs, d.x + 150), (xs, bas), (xr, bas)], r=min(d.R(2 * (xr - xs)), xr - xs - 6), fin='v'),
            barre(d.Lr - d.m['sillage'], xs - d.F / 2 + J, yb), barre(xs + d.F / 2 - J, xr - 6, yb)], d.Lr + W + 6


def u(d):
    W = 456 + d.g * 0.8; xl = d.L + d.F / 2; xr = d.L + W - d.F / 2; bas = d.bas(True)
    return [T([(xl, d.x), (xl, bas), (xr, bas), (xr, d.x)], r=d.R(xr - xl))], d.L + W + d.L


def _v(d, h, W, L):
    xl = L + d.F * 0.52; xr = L + W - d.F * 0.52; xc = (xl + xr) / 2
    return [T([(xl, h), (xc, d.B * 0.42 - d.d), (xr, h)], r=d.c * 0.5, debut='h', fin='h')], L + W + L


def v(d):
    return _v(d, d.x, 450 + d.g * 0.75, d.Lr * 0.5)


def _w(d, h, W, L):
    xl = L + d.F * 0.52; xr = L + W - d.F * 0.52; q = (xr - xl) / 4; y0 = d.B * 0.42 - d.d
    return [T([(xl, h), (xl + q, y0), (xl + 2 * q, h * 0.80), (xl + 3 * q, y0), (xr, h)], r=d.c * 0.5, debut='h', fin='h')], L + W + L


def w(d):
    return _w(d, d.x, 700 + d.g * 1.3, d.Lr * 0.5)


def _x(d, h, W, L):
    xl = L + d.F * 0.55; xr = L + W - d.F * 0.55; c = ((xl + xr) / 2, h / 2)
    a0, a1 = (xl, h), (xr, 0)
    return [T([a0, a1], debut='h', fin='h'),
            T([(xl, 0), c], debut='h', fin=d.contre(a0, a1, -1)),
            T([c, (xr, h)], debut=d.contre(a0, a1, 1), fin='h')], L + W + L


def x(d):
    return _x(d, d.x, 440 + d.g * 0.75, d.Lr * 0.55)


def y(d):
    W = 456 + d.g * 0.8; xl = d.L + d.F / 2; xr = d.L + W - d.F / 2; bas = d.bas(True); yd = d.bas(True, d.desc)
    R = d.R(xr - xl)
    return [T([(xr, d.x), (xr, yd), (xl - d.F / 2 + 26, yd)], r=min(R, (0 - d.desc) * 0.62), fin='v'),
            T([(xl, d.x), (xl, bas), (xr - d.F / 2 + J, bas)], r=R)], d.L + W + d.L


def _z(d, h, W, L):
    xl = L + d.F * 0.3; xr = L + W - d.F * 0.3
    return [T([(L, d.haut(h)), (xr, d.haut(h)), (xl, d.bas()), (L + W, d.bas())], r=d.c * 0.45)], L + W + L


def z(d):
    return _z(d, d.x, 410 + d.g * 0.7, d.Lr * 0.8)


# --- les lettres en plus

def germandbls(d):
    W = 480 + d.g * 0.85; xl = d.L + d.F / 2; xr = d.L + W - d.F / 2; xa = xl + (xr - xl) * 0.60
    top = d.haut(d.asc, True); bas = d.bas(True); ym = max(d.x * 0.82, bas + 2.7 * d.B)
    ra = d.R(xa - xl, d.asc)
    rj = max(min(d.c * 0.8, (xr - xa) / 2 - 1), 1)
    rl = max(min((ym - bas) / 2 - 1, (xr - xa) - rj - 1), 1)
    return [T([(xl, 0), (xl, top), (xa, top), (xa, ym), (xr, ym), (xr, bas), (xl + d.F / 2 + 30, bas)],
              r=[ra, min(ra, top - ym - rj - 1), rj, rl, rl], fin='v')], d.L + W + d.Lr


def ae(d):
    W = 740 + d.g * 1.4; xl = d.Lr + d.F / 2; xr = d.Lr + W - d.F / 2; xc = (xl + xr) / 2
    top = d.haut(d.x, True); bas = d.bas(True); R = d.R(xc - xl)
    ym = max(d.x * 0.47, 2.0 * d.B); r2 = max(min(R, (top - ym) / 2 - 1), 1)
    return [fut(xc, 0, d.x),
            T([(xc - d.F / 2 + J, top), (xl, top), (xl, bas), (xc - d.F / 2 + J, bas)], r=R),
            T([(xc + d.F / 2 - J, ym), (xr, ym), (xr, top), (xc + d.F / 2 - J, top)], r=[min(d.c * 0.6, r2), min(R, 2 * r2 - min(d.c * 0.6, r2))]),
            barre(xc + d.F / 2 - J, d.Lr + W - 8, d.bas())], d.Lr + W + d.Lr * 0.7


def oe(d):
    W = 780 + d.g * 1.5; xl = d.Lr + d.F / 2; xr = d.Lr + W - d.F / 2; xc = (xl + xr) / 2
    top = d.haut(d.x, True); bas = d.bas(True); R = d.R(xc - xl)
    ym = max(d.x * 0.47, 2.0 * d.B); r2 = max(min(R, (top - ym) / 2 - 1), 1)
    return [T([(xl, bas), (xl, top), (xc, top), (xc, bas)], r=R, ferme=True),
            T([(xc + d.F / 2 - J, ym), (xr, ym), (xr, top), (xc + d.F / 2 - J - 40, top)], r=[min(d.c * 0.6, r2), min(R, 2 * r2 - min(d.c * 0.6, r2))]),
            barre(xc + d.F / 2 - J - 40, d.Lr + W - 8, d.bas())], d.Lr + W + d.Lr * 0.7


def oslash(d):
    t, ch = o(d)
    t.append(T([(d.Lr + 34, -34), (ch - d.Lr - 34, d.x + 34)], plein=True, ep=d.B * 0.55, debut='h', fin='h'))
    return t, ch


def eth(d):
    W, xl, xr, top, bas, R = _rond(d, 480 + d.g * 0.85)
    h = d.x * 0.94; top = d.haut(h, True)
    xa = xl + (xr - xl) * 0.30
    return [T([(xl, bas), (xl, top), (xr, top), (xr, bas)], r=d.R(xr - xl, h), ferme=True),
            T([(xr, h * 0.55), (xr, d.asc - 180), (xa, d.asc)], r=d.c * 1.5, fin='h'),
            T([(xa + 40, d.asc - 150), (xr + d.F * 0.35, d.asc - 62)], plein=True, ep=d.B * 0.55, debut='v', fin='v')], d.Lr + W + d.Lr


def thorn(d):
    t, ch = b(d)
    t[0] = fut(d.L + d.F / 2, d.desc, d.asc)
    return t, ch


def lslash(d):
    t, ch = l(d)
    xs = d.L + d.F / 2
    t.append(T([(xs - d.F * 0.5 - 52, d.asc * 0.40), (xs + d.F * 0.5 + 52, d.asc * 0.60)], plein=True, ep=d.B * 0.62, debut='v', fin='v'))
    return t, ch + 0


def dcroat(d):
    t, ch = dd(d)
    xr = d.Lr + (468 + d.g * 0.8) - d.F / 2
    t.append(barre(xr - d.F / 2 - 74, xr + d.F / 2 + 44, d.x + 132, plein=True, ep=d.B * 0.6))
    return t, ch + 22


def hbar(d):
    t, ch = h(d)
    xl = d.L + d.F / 2
    t.append(barre(xl - d.F / 2 - 44, xl + d.F / 2 + 84, d.x + 132, plein=True, ep=d.B * 0.6))
    return t, ch


MINUSCULES = {'a': a, 'b': b, 'c': c, 'd': dd, 'e': e, 'f': f, 'g': g, 'h': h, 'i': i, 'j': j, 'k': k, 'l': l,
              'm': m, 'n': n, 'o': o, 'p': p, 'q': q, 'r': r, 's': s, 't': t, 'u': u, 'v': v, 'w': w, 'x': x,
              'y': y, 'z': z, 'ı': dotlessi, 'ȷ': dotlessj, 'ß': germandbls, 'æ': ae, 'œ': oe, 'ø': oslash,
              'ð': eth, 'þ': thorn, 'ł': lslash, 'đ': dcroat, 'ħ': hbar}
