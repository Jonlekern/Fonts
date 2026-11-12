# SHEARLINE : capitales A–Z (trompes, croix pattées sur les fûts, croix dans le contre des rondes) et lettrines
from shr_core import *
from shr_lower import Cross

def caps(w, mode='mix'):
    s, k, yb, yc, pen = w.s, w.k, w.yb, w.yc, w.pen
    S = 1.35 * s; st = pen.stroke; cx = Cross(w, mode); G = {}
    xs = 0.05 * S
    trunk = [(-0.32 * S, yc - 0.38 * S), (-0.16 * S, yc), (xs, yc - 0.12 * S), (xs, yb + 0.45 * S), (-0.12 * S, yb), (-0.36 * S, yb + 0.14 * S)]
    pat = lambda x=xs, y=0.47 * CAP, wd=0.95 * S: cx('pattee', x, y, wd)
    def inner(x0, x1):
        """croix dans le contre des rondes : un filet debout et une barre"""
        if mode == 'none': return None
        m = 0.5 * (x0 + x1); f = max(1.6 * w.t, 0.18 * w.W)
        return U(rect(m - f / 2, 0.26 * CAP, m + f / 2, 0.76 * CAP), cx('latin', m, 0.60 * CAP, 0.34 * (x1 - x0) + 0.2 * S))
    tail = lambda x: [(x, 0.10 * S), (x - 0.15 * S, 0.45 * DESC), (x - 0.6 * S, 0.75 * DESC)]
    head = lambda x, top=yc: [(x - k, top), (x, top - 1.2 * k)]
    T = st(trunk)
    G['A'] = U(T, st([(xs, yc - 0.55 * S), (0.55 * S, yc), (S, yc - 1.2 * k), (S, yb + k), (S + k, yb)]), rect(xs, 0.40 * CAP, S, 0.40 * CAP + 2 * w.t), pat())
    G['B'] = U(T, st([(xs, yc - 0.5 * S), (0.5 * S, yc), (0.85 * S, yc - 1.2 * k), (0.85 * S, 0.60 * CAP), (xs, 0.52 * CAP)]),
               st([(xs, 0.52 * CAP), (S, 0.45 * CAP), (S, yb + 0.35 * S), (0.6 * S, yb), (xs, yb + 0.12 * S)]), pat(xs, 0.33 * CAP, 0.85 * S))
    Cp = [(0.95 * S, yc - 0.25 * S), (0.75 * S, yc), (0.35 * S, yc - 0.05 * S), (0, yc - 0.45 * S), (0, yb + 0.4 * S), (0.35 * S, yb), (0.95 * S, yb + 0.3 * S)]
    G['C'] = U(st(Cp), inner(0.15 * S, 0.85 * S))
    G['D'] = U(T, st([(xs, yc - 0.55 * S), (0.55 * S, yc), (S, yc - 0.45 * S), (S, yb + 0.4 * S), (0.55 * S, yb), (xs, yb + 0.12 * S)]), pat())
    G['E'] = U(st(Cp), st([(0.3 * S, 0.5 * CAP), (0.8 * S, 0.56 * CAP)]), inner(0.15 * S, 0.7 * S) if mode == 'none' else None)
    top = [(-0.05 * S, yc - 0.18 * S), (0.35 * S, yc), (0.75 * S, yc - 0.1 * S), (1.1 * S, yc)]
    G['F'] = U(st(top), st([(0.35 * S, yc - 0.1 * S), (0.35 * S, yb + 0.4 * S), (0.1 * S, yb), (-0.15 * S, yb + 0.12 * S)]),
               st([(0.1 * S, 0.5 * CAP), (0.8 * S, 0.56 * CAP)]), pat(0.35 * S, 0.33 * CAP, 0.8 * S))
    G['G'] = U(st(Cp[:-1] + [(0.95 * S, yb + 0.3 * S), (0.95 * S, 0.52 * CAP), (0.55 * S, 0.52 * CAP)]), inner(0.15 * S, 0.8 * S))
    G['H'] = U(T, st([(xs, yc - 0.6 * S), (0.55 * S, yc - 0.05 * S), (S, yc - 0.3 * S)] + tail(S)), pat())
    G['I'] = U(st([(0, yc - 0.25 * S), (0.25 * S, yc), (0.5 * S, yc - 0.15 * S), (0.5 * S, yb + 0.4 * S), (0.3 * S, yb), (0, yb + 0.15 * S)]), pat(0.5 * S, 0.5 * CAP, 0.8 * S))
    G['J'] = U(st([(0, yc - 0.25 * S), (0.25 * S, yc), (0.5 * S, yc - 0.15 * S)] + tail(0.5 * S)), pat(0.5 * S, 0.5 * CAP, 0.8 * S))
    G['K'] = U(T, st([(xs, 0.42 * CAP), (0.6 * S, yc - 0.05 * S), (0.85 * S, yc - 0.22 * S)]),
               st([(0.3 * S, 0.5 * CAP), (0.85 * S, 0.32 * CAP), (0.85 * S, yb + k), (0.85 * S + k, yb)]), pat())
    G['L'] = U(st([(-0.32 * S, yc - 0.38 * S), (-0.16 * S, yc), (xs, yc - 0.12 * S), (xs, yb + 0.35 * S), (0.3 * S, yb), (0.6 * S, yb + 0.1 * S), (0.95 * S, yb)]),
               pat())
    G['M'] = U(T, st([(xs, yc - 0.6 * S), (0.45 * S, yc), (0.85 * S, yc - 1.2 * k), (0.85 * S, yb + k), (0.85 * S + k, yb)]),
               st([(0.85 * S, yc - 0.6 * S), (1.25 * S, yc), (1.65 * S, yc - 1.2 * k), (1.65 * S, yb + k), (1.65 * S + k, yb)]), pat())
    G['N'] = U(T, st([(xs, yc - 0.6 * S), (0.62 * S, yc), (S, yc - 1.2 * k), (S, yb + k), (S + k, yb)]), pat())
    Op = [(0.5 * S, yc), (0, yc - 0.45 * S), (0, yb + 0.45 * S), (0.5 * S, yb), (S, yb + 0.45 * S), (S, yc - 0.45 * S), (0.5 * S, yc)]
    G['O'] = U(st(Op), inner(0.15 * S, 0.85 * S))
    Pb = [(xs, yc - 0.55 * S), (0.55 * S, yc), (S, yc - 0.3 * S), (S, 0.52 * CAP), (0.55 * S, 0.38 * CAP), (xs, 0.42 * CAP)]
    G['P'] = U(T, st(Pb), pat(xs, 0.25 * CAP, 0.85 * S))
    G['Q'] = U(st(Op), st([(0.5 * S, yb), (1.15 * S, -0.14 * S)]), inner(0.15 * S, 0.85 * S))
    G['R'] = U(T, st(Pb), st([(0.55 * S, 0.38 * CAP), (0.95 * S, 0.26 * CAP), (0.95 * S, yb + k), (0.95 * S + k, yb)]), pat(xs, 0.25 * CAP, 0.85 * S))
    G['S'] = U(st([(0.95 * S, yc - 0.2 * S), (0.65 * S, yc), (0.15 * S, yc - 0.25 * S), (0.15 * S, 0.56 * CAP), (0.85 * S, 0.44 * CAP), (0.95 * S, yb + 0.35 * S),
                   (0.5 * S, yb), (0, yb + 0.2 * S)]))
    G['T'] = U(st(top), st([(0.45 * S, yc - 0.05 * S), (0.15 * S, 0.62 * CAP), (0.15 * S, yb + 0.4 * S), (0.5 * S, yb), (0.95 * S, yb + 0.3 * S)]), inner(0.3 * S, 0.95 * S))
    G['U'] = U(T, st([(xs, yb + 0.4 * S), (0.5 * S, yb), (S, yb + 0.35 * S)]), st(head(S) + [(S, yb + k), (S + k, yb)]), pat())
    G['V'] = U(T, st([(xs, yb + 0.4 * S), (0.5 * S, yb), (S, yb + 0.4 * S), (S, yc - 0.3 * S), (0.75 * S, yc), (0.5 * S, yc - 0.12 * S)]), pat())
    G['W'] = U(T, st([(xs, yb + 0.4 * S), (0.45 * S, yb), (0.85 * S, yb + 0.35 * S)]), st(head(0.85 * S) + [(0.85 * S, yb + 0.35 * S), (1.3 * S, yb), (1.7 * S, yb + 0.4 * S),
                                                                                                   (1.7 * S, yc - 0.3 * S), (1.4 * S, yc)]), pat())
    G['X'] = U(st([(0.0, yc - 0.2 * S), (0.25 * S, yc), (0.5 * S, yc - 0.35 * S), (0.5 * S, yb + 0.35 * S), (0.25 * S, yb), (0.0, yb + 0.2 * S)]),
               st([(1.0 * S, yc - 0.2 * S), (0.75 * S, yc), (0.5 * S, yc - 0.35 * S)]), st([(0.5 * S, yb + 0.35 * S), (0.75 * S, yb), (1.0 * S, yb + 0.2 * S)]))
    G['Y'] = U(T, st([(xs, yb + 0.4 * S), (0.5 * S, yb), (S, yb + 0.4 * S)]), st([(0.7 * S, yc), (S, yc - 0.3 * S)] + tail(S)), pat())
    G['Z'] = st([(0.05 * S, yc - 0.05 * S), (0.9 * S, yc), (0.3 * S, 0.45 * CAP), (0.85 * S, 0.32 * CAP), (0.85 * S, 0.2 * DESC), (0.55 * S, 0.6 * DESC), (0.1 * S, 0.75 * DESC)])
    G['Thorn'] = U(T, st([(xs, 0.76 * CAP), (0.55 * S, 0.80 * CAP), (S, 0.66 * CAP), (S, 0.36 * CAP), (0.55 * S, 0.20 * CAP), (xs, 0.24 * CAP)]))
    G['uni1E9E'] = U(st([(0.0, yc - 0.55 * S), (0.0, yb + k), (k, yb)]), st([(0.0, yc - 0.6 * S), (0.3 * S, yc), (0.85 * S, yc - 0.12 * S), (0.4 * S, 0.55 * CAP),
                                                                     (0.95 * S, 0.42 * CAP), (0.95 * S, yb + 0.35 * S), (0.55 * S, yb), (0.2 * S, yb + 0.15 * S)]))
    return G

def lettrine(w, g):
    """lettrine : bloc noir, la capitale en réserve, filet blanc intérieur, croix pattées aux coins"""
    b = bounds(g)
    m = 0.28 * w.s + 40; y0, y1 = DESC * 0.55, CAP + 0.10 * CAP
    bw = max(b[2] - b[0] + 2 * m, 0.82 * (y1 - y0)); xm = 0.5 * (b[0] + b[2]); x0, x1 = xm - bw / 2, xm + bw / 2
    blk = rect(x0, y0, x1, y1)
    f = max(2.2 * w.t, 14); e = 0.32 * m
    frame = D(rect(x0 + e, y0 + e, x1 - e, y1 - e), rect(x0 + e + f, y0 + e + f, x1 - e - f, y1 - e - f))
    cs = 0.95 * m
    def cr(cx_, cy_):
        a = bar_pattee(cx_, cy_, cs, 0.30 * cs, 2.4)
        return U(a, xf(bar_pattee(0, 0, cs, 0.30 * cs, 2.4), (0, 1, -1, 0, cx_, cy_)))
    q = e + f + 0.62 * cs
    corners = U(cr(x0 + q, y0 + q), cr(x1 - q, y0 + q), cr(x0 + q, y1 - q), cr(x1 - q, y1 - q))
    gm = mv(g, 0, 0.5 * ((y0 + y1) - (b[1] + b[3])))
    gm = I(gm, rect(x0 + e + f, y0 + e + f, x1 - e - f, y1 - e - f))
    return D(blk, frame, corners, gm)
