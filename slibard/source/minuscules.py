# Les minuscules de Slibard. Chaque fonction rend (tuyaux, chasse).
# La structure : le contraste Art déco (fût de gauche en filet, fût de droite gras, barres en filet).
# La signature : chaque lettre a un geste à elle, pris aux emblèmes chromés des années 50.
from tuyaux import Tuyau as T
from dessin import D, fut, barre, point, JOINT as J


def _signe(t):
    """Une signature : elle ne compte pas dans la largeur de la lettre."""
    t.hors = True
    return t


def _rond(d, W=None, L=None):
    """Les repères d'une lettre ronde de la hauteur d'x : largeur, gauche, droite, haut, bas, rayon."""
    W = (468 + d.g * 0.8) if W is None else W
    xl, xr = d.gd(W, d.Lr if L is None else L)
    return W, xl, xr, d.haut(d.x, True), d.bas(True), d.R(xr - xl)


def a(d):
    W, xl, xr, top, bas, R = _rond(d, 468 + d.g * 1.25)      # le fût gras est à droite : la panse garde de la place
    return [fut(xr, 0, d.x),
            T([(xr - d.Fd / 2 + J, top), (xl, top), (xl, bas), (xr - d.Fd / 2 + J, bas)], r=R)], d.Lr + W + d.L


def b(d, h=None):
    W, xl, xr, top, bas, R = _rond(d, L=d.L)
    h = d.asc if h is None else h
    return [fut(xl, 0, h),
            T([(xl + d.Fg / 2 - J, top), (xr, top), (xr, bas), (xl + d.Fg / 2 - J, bas)], r=R)], d.L + W + d.Lr


def c(d):
    W, xl, xr, top, bas, R = _rond(d, 440 + d.g * 0.7)
    xe = d.Lr + W
    return [T([(xe, top), (xl, top), (xl, bas), (xe, bas)], r=R, debut='v', fin='v')], d.Lr + W + d.Lr * 0.6


def dd(d):
    W, xl, xr, top, bas, R = _rond(d, 468 + d.g * 1.25)      # le fût gras est à droite : la panse garde de la place
    return [fut(xr, 0, d.asc),
            T([(xr - d.Fd / 2 + J, top), (xl, top), (xl, bas), (xr - d.Fd / 2 + J, bas)], r=R)], d.Lr + W + d.L


def e(d):
    W, xl, xr, top, bas, R = _rond(d)
    ym = d.x * 0.50
    return [T([(xr, ym - d.B / 2), (xr, top), (xl, top), (xl, bas), (d.Lr + W - 6, bas)], r=[min(R, top - ym - 2), R, R], debut='h', fin='v'),
            barre(xl + d.Fg / 2 - J, xr, ym)], d.Lr + W + d.Lr * 0.8


def f(d):
    W = max(300 + d.g * 0.45, d.Fm + 190); xs = d.Lr + 70 + d.Fm / 2; xr = d.Lr + W; yb = d.haut(d.x)
    t = T([(xr, d.haut(d.asc, True)), (xs, d.haut(d.asc, True)), (xs, 0)], r=min(d.R(2 * (xr - xs)), xr - xs - 6), debut='v', ep=(d.Fm, d.B))
    return [t, barre(d.Lr, xs - d.Fm / 2 + J, yb, k=[1.5, 1.5]),
            barre(xs + d.Fm / 2 - J, xr - 6, yb, k=[1.5, 1.5])], d.Lr + W + 4


def g(d):
    W, xl, xr, top, bas, R = _rond(d, 468 + d.g * 1.25)      # le fût gras est à droite : la panse garde de la place
    yd = d.bas(True, d.desc)
    return [T([(xr, d.x), (xr, yd), (xl + 20, yd)], r=min(R, (0 - d.desc) * 0.62), fin='v'),
            T([(xr - d.Fd / 2 + J, top), (xl, top), (xl, bas), (xr - d.Fd / 2 + J, bas)], r=R)], d.Lr + W + d.L


def h(d):
    W = 456 + d.g * 0.8; xl, xr = d.gd(W); top = d.haut(d.x, True)
    return [fut(xl, 0, d.asc),
            T([(xl + d.Fg / 2 - J, top), (xr, top), (xr, 0)], r=d.R(2 * (xr - xl) - d.F))], d.L + W + d.L


def _i(d, pt=True):
    xs = d.L + 30 + d.Fm / 2
    t = [fut(xs, 0, d.x)]
    if pt:
        t.append(point(xs, d.x + 70 + min(d.Fm, 230) * 0.4, min(d.Fm * 0.9, 215)))
    return t, 2 * d.L + d.Fm + 30


def i(d):
    return _i(d)


def dotlessi(d):
    return _i(d, False)


def _j(d, pt=True):
    W = max(250 + d.g * 0.4, d.Fm + 130); xs = d.Lr + W - d.Fm / 2; yd = d.bas(True, d.desc)
    t = [T([(xs, d.x), (xs, yd), (d.Lr - 10, yd)], r=min(d.R(2 * (W - d.Fm)), (0 - d.desc) * 0.62), fin='v', ep=(d.Fm, d.B))]
    if pt:
        t.append(point(xs, d.x + 70 + min(d.Fm, 230) * 0.4, min(d.Fm * 0.9, 215)))
    return t, d.Lr + W + d.L


def j(d):
    return _j(d)


def dotlessj(d):
    return _j(d, False)


def _k(d, h, xh):
    """Le k et le K : un fût, un bras qui part du fût, une jambe qui part du bras."""
    W = (430 if xh == d.x else 560) + d.g * 0.8; xl = d.L + d.Fg / 2; xr = d.L + W
    ym = xh * 0.42 if xh == d.x else d.taille() * 1.1
    a0 = (xl + d.Fg / 2 - J, ym); a1 = (xr - d.F * 0.5, xh)
    p = (a0[0] + (a1[0] - a0[0]) * 0.24, a0[1] + (a1[1] - a0[1]) * 0.24)
    return [fut(xl, 0, h),
            T([a0, a1], debut='v', fin='h', ep=(d.Fg * 1.2, d.B)),
            T([p, (xr - d.F * 0.6, 0)], debut=d.contre(a0, a1, -1), fin='h', ep=(d.Fd, d.B))], d.L + W + d.Lr * 0.3


def k(d):
    return _k(d, d.asc, d.x)


def l(d):
    xs = d.L + d.Fm / 2
    return [fut(xs, 0, d.asc)], 2 * d.L + d.Fm


def m(d):
    W = 720 + d.g * 1.45; xl, xr = d.gd(W); xm = (xl + xr) / 2 - d.F * 0.2; top = d.haut(d.x, True)
    R = d.R(xm - xl)
    return [T([(xl, 0), (xl, top), (xm, top), (xm, 0)], r=R),
            T([(xm + d.F / 2 - J, top), (xr, top), (xr, 0)], r=R)], d.L + W + d.L


def n(d):
    W = 456 + d.g * 0.8; xl, xr = d.gd(W); top = d.haut(d.x, True)
    return [T([(xl, 0), (xl, top), (xr, top), (xr, 0)], r=d.R(xr - xl))], d.L + W + d.L


def o(d):
    W, xl, xr, top, bas, R = _rond(d, 480 + d.g * 0.85)
    return [T([(xl, bas), (xl, top), (xr, top), (xr, bas)], r=R, ferme=True)], d.Lr + W + d.Lr


def p(d):
    W, xl, xr, top, bas, R = _rond(d, L=d.L)
    return [fut(xl, d.desc, d.x),
            T([(xl + d.Fg / 2 - J, top), (xr, top), (xr, bas), (xl + d.Fg / 2 - J, bas)], r=R)], d.L + W + d.Lr


def q(d):
    W, xl, xr, top, bas, R = _rond(d, 468 + d.g * 1.25)      # le fût gras est à droite : la panse garde de la place
    return [fut(xr, d.desc, d.x),
            T([(xr - d.Fd / 2 + J, top), (xl, top), (xl, bas), (xr - d.Fd / 2 + J, bas)], r=R)], d.Lr + W + d.L


def r(d):
    W = max(300 + d.g * 0.5, d.Fm + 150); xl = d.L + d.Fm / 2; xr = d.L + W; top = d.haut(d.x, True)
    return [T([(xl, 0), (xl, top), (xr, top)], r=min(d.R(2 * (xr - xl)), xr - xl - 8), fin='v', ep=(d.Fm, d.B))], d.L + W + 8


def _s(d, h=None, W=None):
    """Le s et le S : les bouts coupés droit, le milieu gras."""
    h = d.x if h is None else h
    W = (410 + d.g * 0.75) if W is None else W
    xl, xr = d.gd(W, d.Lr); top = d.haut(h, True); bas = d.bas(True)
    xl += (d.F - d.Fg) * 0.25
    mid = (top + bas) / 2 + h * 0.012
    ra = (top - mid) / 2; rb = (mid - bas) / 2
    return [T([(d.Lr + W - 6, top), (xl, top), (xl, mid), (xr, mid), (xr, bas), (d.Lr + 4, bas)],
              r=[ra, ra, rb, rb], debut='v', fin='v')], d.Lr + W + d.Lr


def s(d):
    return _s(d)


def t(d):
    W = max(300 + d.g * 0.45, d.Fm + 190); xs = d.Lr + 62 + d.Fm / 2; xr = d.Lr + W; bas = d.bas(True); yb = d.haut(d.x)
    return [T([(xs, d.x + 150), (xs, bas), (xr, bas)], r=min(d.R(2 * (xr - xs)), xr - xs - 6), fin='v', ep=(d.Fm, d.B)),
            barre(d.Lr, xs - d.Fm / 2 + J, yb, k=[1.5, 1.5]),
            barre(xs + d.Fm / 2 - J, xr, yb, k=[1.5, 1.5])], d.Lr + W + 6


def u(d):
    W = 456 + d.g * 0.8; xl, xr = d.gd(W); bas = d.bas(True)
    return [T([(xl, d.x), (xl, bas), (xr, bas), (xr, d.x)], r=d.R(xr - xl))], d.L + W + d.L


def _v(d, h, W, L):
    xl, xr = d.gd(W, L); xc = (xl + xr) / 2 + d.F * 0.2
    return [T([(xl, h), (xc, d.Fd * 0.29 - 20), (xr, h)], r=d.c * 0.4, debut='h', fin='h')], L + W + L


def v(d):
    return _v(d, d.x, 450 + d.g * 0.75, d.Lr * 0.5)


def _w(d, h, W, L):
    xl, xr = d.gd(W, L); q = (xr - xl) / 4; y0 = d.Fd * 0.32 - 18; cx = (xl + xr) / 2
    return [T([(xl, h), (xl + q, y0), (cx, h)], r=d.c * 0.4, debut='h', fin='h'),
            T([(cx, h), (xl + 3 * q, y0), (xr, h)], r=d.c * 0.4, debut='h', fin='h')], L + W + L


def w(d):
    return _w(d, d.x, 700 + d.g * 1.3, d.Lr * 0.5)


def _x(d, h, W, L):
    xl, xr = d.gd(W, L); xl += d.F * 0.3
    return [T([(xl, h), (xr, 0)], debut='h', fin='h', ep=(d.Fd * 0.9, d.B)),
            T([(L + d.F * 0.2, 0), (xr - d.F * 0.2, h)], debut='h', fin='h', ep=(d.Fg * 1.3, d.B))], L + W + L


def x(d):
    return _x(d, d.x, 440 + d.g * 0.75, d.Lr * 0.55)


def y(d):
    W = 456 + d.g * 0.8; xl, xr = d.gd(W); bas = d.bas(True); yd = d.bas(True, d.desc)
    R = d.R(xr - xl)
    return [T([(xr, d.x), (xr, yd), (xr - d.Fd / 2 - 110, yd)], r=min(R * 0.7, (0 - d.desc) * 0.5), fin='v'),
            T([(xl, d.x), (xl, bas), (xr - d.Fd / 2 + J, bas)], r=R)], d.L + W + d.L


def _z(d, h, W, L):
    xl = L + d.F * 0.3; xr = L + W - d.F * 0.3
    return [T([(L, d.haut(h)), (xr, d.haut(h)), (xl, d.bas()), (L + W, d.bas())], r=d.c * 0.4, ep=(d.Fd * 0.8, d.B))], L + W + L


def z(d):
    return _z(d, d.x, 410 + d.g * 0.7, d.Lr * 0.8)


# --- les lettres en plus

def germandbls(d):
    W = 480 + d.g * 0.85; xl, xr = d.gd(W); xa = xl + (xr - xl) * 0.60
    top = d.haut(d.asc, True); bas = d.bas(True); ym = d.x * 0.84
    ra = d.R(xa - xl, d.asc); rj = 24; rl = max((ym - bas) / 2 - 1, 1)
    return [T([(xl, 0), (xl, top), (xa, top), (xa, ym), (xr, ym), (xr, bas), (xl + d.Fg / 2 + 40, bas)],
              r=[ra, ra, rj, rl, rl], fin='v')], d.L + W + d.Lr


def ae(d):
    W = 740 + d.g * 1.4; xl, xr = d.gd(W, d.Lr); xc = (xl + xr) / 2
    top = d.haut(d.x, True); bas = d.bas(True); R = d.R(xc - xl); ym = d.x * 0.50
    return [fut(xc, 0, d.x),
            T([(xc - d.F / 2 + J, top), (xl, top), (xl, bas), (xc - d.F / 2 + J, bas)], r=R),
            T([(xr, ym - d.B / 2), (xr, top), (xc + d.F / 2 - J, top)], r=min(R, top - ym - 2), debut='h'),
            barre(xc + d.F / 2 - J, d.Lr + W - 6, d.bas()),
            barre(xc + d.F / 2 - J, xr, ym)], d.Lr + W + d.Lr * 0.8


def oe(d):
    W = 780 + d.g * 1.5; xl, xr = d.gd(W, d.Lr); xc = (xl + xr) / 2
    top = d.haut(d.x, True); bas = d.bas(True); R = d.R(xc - xl); ym = d.x * 0.50
    return [T([(xl, bas), (xl, top), (xc, top), (xc, bas)], r=R, ferme=True),
            T([(xr, ym - d.B / 2), (xr, top), (xc + d.F / 2 - J, top)], r=min(R, top - ym - 2), debut='h'),
            barre(xc + d.F / 2 - J, d.Lr + W - 6, d.bas()),
            barre(xc + d.F / 2 - J, xr, ym)], d.Lr + W + d.Lr * 0.8


def oslash(d):
    W, xl, xr, top, bas, R = _rond(d, 480 + d.g * 0.85)
    return [T([(xl, bas), (xl, top), (xr, top), (xr, bas)], r=R, ferme=True),
            _signe(T([(d.Lr + 20, -40), (d.Lr + W - 20, d.x + 40)], plein=True, ep=d.B * 1.3, debut='h', fin='h'))], d.Lr + W + d.Lr


def eth(d):
    W, xl, xr, top, bas, R = _rond(d, 480 + d.g * 0.85)
    h = d.x * 0.94; top = d.haut(h, True)
    return [T([(xl, bas), (xl, top), (xr, top), (xr, bas)], r=d.R(xr - xl, h), ferme=True),
            T([(xr, h * 0.3), (xr, d.asc - 170), (xl + 60, d.asc)], r=d.c * 2, fin='h', k=[0, 1, 0.25]),
            _signe(T([(xl + 90, d.asc - 150), (xr + d.Fd * 0.5 + 20, d.asc - 60)], plein=True, ep=d.B * 1.3, debut='v', fin='v'))], d.Lr + W + d.Lr


def thorn(d):
    W, xl, xr, top, bas, R = _rond(d, L=d.L)
    return [fut(xl, d.desc, d.asc),
            T([(xl + d.Fg / 2 - J, top), (xr, top), (xr, bas), (xl + d.Fg / 2 - J, bas)], r=R)], d.L + W + d.Lr


def lslash(d):
    xs = d.L + 40 + d.Fm / 2
    return [fut(xs, 0, d.asc),
            _signe(T([(xs - d.Fm * 0.5 - 60, d.asc * 0.40), (xs + d.Fm * 0.5 + 60, d.asc * 0.60)], plein=True, ep=d.B * 1.3, debut='v', fin='v'))], 2 * d.L + d.Fm + 80


def dcroat(d):
    W, xl, xr, top, bas, R = _rond(d, 468 + d.g * 1.25)      # le fût gras est à droite : la panse garde de la place
    return [fut(xr, 0, d.asc),
            T([(xr - d.Fd / 2 + J, top), (xl, top), (xl, bas), (xr - d.Fd / 2 + J, bas)], r=R),
            _signe(barre(xr - d.Fd / 2 - 90, xr + d.Fd / 2 + 50, d.x + 132, plein=True, ep=d.B))], d.Lr + W + d.L + 30


def hbar(d):
    W = 456 + d.g * 0.8; xl, xr = d.gd(W); top = d.haut(d.x, True)
    return [fut(xl, 0, d.asc),
            T([(xl + d.Fg / 2 - J, top), (xr, top), (xr, 0)], r=d.R(2 * (xr - xl) - d.F)),
            _signe(barre(xl - d.Fg / 2 - 60, xl + d.Fg / 2 + 110, d.x + 132, plein=True, ep=d.B))], d.L + W + d.L


MINUSCULES = {'a': a, 'b': b, 'c': c, 'd': dd, 'e': e, 'f': f, 'g': g, 'h': h, 'i': i, 'j': j, 'k': k, 'l': l,
              'm': m, 'n': n, 'o': o, 'p': p, 'q': q, 'r': r, 's': s, 't': t, 'u': u, 'v': v, 'w': w, 'x': x,
              'y': y, 'z': z, 'ı': dotlessi, 'ȷ': dotlessj, 'ß': germandbls, 'æ': ae, 'œ': oe, 'ø': oslash,
              'ð': eth, 'þ': thorn, 'ł': lslash, 'đ': dcroat, 'ħ': hbar}
