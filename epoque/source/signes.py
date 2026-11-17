# La ponctuation et les signes d'Époque. Chaque fonction rend (tuyaux, chasse).
# Les signes sont pleins : un trait fin (ef) et un trait gras (eg), sans la règle gauche/droite des lettres.
import math
from tuyaux import Tuyau as T
from dessin import D, fut, barre, point, reduit, decale, JOINT as J
from minuscules import _signe, MINUSCULES
from capitales import CAPITALES
from chiffres import CHIFFRES


def ef(d):
    return d.B * 1.35


def eg(d):
    return d.Fm * 0.92


def _pt(d):
    return d.Fm * 1.02


def P(pts, d, e=None, **k):
    """Un trait plein d'épaisseur fixe."""
    return T(pts, plein=True, ep=ef(d) if e is None else e, **k)


def espace(d):
    return [], 230 + d.g * 0.3


def point_(d, y=None):
    s = _pt(d)
    return [point(d.L + s / 2, s / 2 if y is None else y, s)], 2 * d.L + s


def virgule(d, y=0.0):
    s = _pt(d); cx = d.L + s / 2 + 10
    return [point(cx, y + s / 2, s), P([(cx + s * 0.28, y + s * 0.42), (cx - s * 0.42, y - 120)], d, s * 0.5, k=[1, 0])], 2 * d.L + s + 10


def deux_points(d):
    s = _pt(d)
    return [point(d.L + s / 2, s / 2, s), point(d.L + s / 2, d.x - s / 2, s)], 2 * d.L + s


def point_virgule(d):
    t, ch = virgule(d)
    s = _pt(d)
    return t + [point(d.L + s / 2 + 10, d.x - s / 2, s)], ch


def exclam(d, inv=False):
    s = _pt(d); cx = d.L + s / 2
    if inv:
        return [point(cx, d.x - s / 2, s), P([(cx, d.x - s - 50), (cx, d.x - d.cap)], d, eg(d), k=[0.25, 1])], 2 * d.L + s
    return [point(cx, s / 2, s), P([(cx, s + 50), (cx, d.cap)], d, eg(d), k=[0.25, 1])], 2 * d.L + s


def question(d, inv=False):
    s = _pt(d); W = 400 + d.g * 0.6; xl = d.Lr + 20; xr = d.Lr + W - eg(d) / 2; xc = (xl + xr) / 2 + 10
    top = d.haut(d.cap, True); ym = d.cap * 0.44; R = d.R(xr - xl, d.cap, 0.3)
    t = [T([(xl, top - R - 10), (xl, top), (xr, top), (xr, ym), (xc, ym), (xc, s + 60)], r=[R, R, min(R, (top - ym) / 2 - 1), d.c * 0.5],
           ep=(eg(d), ef(d)), plein=True, debut='h', k=[0.3, 1, 1, 1, 1, 0.5]),
         point(xc, s / 2, s)]
    if inv:
        for u in t:
            u.pts = [__import__('numpy').array([2 * (d.Lr + W / 2) - p[0], d.x - p[1]]) for p in u.pts]
    return t, 2 * d.Lr + W


def points(d):
    s = _pt(d); pas = s + 70
    return [point(d.L + s / 2 + i * pas, s / 2, s) for i in range(3)], 2 * d.L + s + 2 * pas


def point_median(d):
    return point_(d, d.x * 0.5)


def puce(d):
    s = _pt(d) * 1.5
    return [point(d.L + s / 2, d.x * 0.5, s)], 2 * d.L + s


def _apos(d, x, monte):
    """Une virgule haute : une goutte effilée."""
    e = eg(d) * 0.9; y1 = d.cap; y0 = d.cap - 200
    if monte:
        return P([(x + 50, y1), (x, y0)], d, e, k=[0, 1], fin='h')
    return P([(x + 50, y1), (x, y0)], d, e, k=[1, 0], debut='h')


def quoteright(d):
    return [_apos(d, d.L + 10, False)], 2 * d.L + 80


def quoteleft(d):
    return [_apos(d, d.L + 10, True)], 2 * d.L + 80


def quotedblright(d):
    return [_apos(d, d.L + 10, False), _apos(d, d.L + 10 + 150, False)], 2 * d.L + 230


def quotedblleft(d):
    return [_apos(d, d.L + 10, True), _apos(d, d.L + 10 + 150, True)], 2 * d.L + 230


def quotesinglbase(d):
    return decale([_apos(d, d.L + 10, False)], 0, -(d.cap - 80)), 2 * d.L + 80


def quotedblbase(d):
    return decale([_apos(d, d.L + 10, False), _apos(d, d.L + 10 + 150, False)], 0, -(d.cap - 80)), 2 * d.L + 230


def quotesingle(d):
    x = d.L + eg(d) / 2
    return [P([(x, d.cap), (x, d.cap - 220)], d, eg(d) * 0.9, k=[1, 0.25])], 2 * d.L + eg(d)


def quotedbl(d):
    x = d.L + eg(d) / 2
    return [P([(x + i * 150, d.cap), (x + i * 150, d.cap - 220)], d, eg(d) * 0.9, k=[1, 0.25]) for i in range(2)], 2 * d.L + eg(d) + 150


def _chevron(d, x, sens, gras=True):
    h = 150; a = 120; y = d.x * 0.5
    pts = [(x + a, y + h), (x, y), (x + a, y - h)] if sens < 0 else [(x, y + h), (x + a, y), (x, y - h)]
    return P(pts, d, (eg(d) * 0.8, ef(d)) if gras else ef(d), r=d.c * 0.3, debut='h', fin='h')


def guilsinglleft(d):
    return [_chevron(d, d.L + 20, -1)], 2 * d.L + 170


def guilsinglright(d):
    return [_chevron(d, d.L + 20, 1)], 2 * d.L + 170


def guillemotleft(d):
    return [_chevron(d, d.L + 20, -1, False), _chevron(d, d.L + 20 + 150, -1)], 2 * d.L + 320


def guillemotright(d):
    return [_chevron(d, d.L + 20, 1), _chevron(d, d.L + 20 + 150, 1, False)], 2 * d.L + 320


def _tiret(d, W, y=None):
    y = d.x * 0.5 if y is None else y
    return [P([(d.L, y), (d.L + W, y)], d, ef(d) * 1.3)], 2 * d.L + W


def hyphen(d):
    return _tiret(d, 260)


def endash(d):
    return _tiret(d, 480)


def emdash(d):
    return _tiret(d, 860)


def underscore(d):
    return [P([(0, -90), (560, -90)], d, ef(d) * 1.3)], 560


def slash(d):
    return [P([(d.L, d.desc * 0.5), (d.L + 300, d.asc)], d, ef(d) * 1.2, debut='h', fin='h')], 2 * d.L + 300


def backslash(d):
    return [P([(d.L, d.asc), (d.L + 300, d.desc * 0.5)], d, ef(d) * 1.2, debut='h', fin='h')], 2 * d.L + 300


def bar(d):
    x = d.L + 20
    return [P([(x, d.desc), (x, d.asc)], d, ef(d) * 1.2)], 2 * d.L + 40


def _crochet(d, ouvre, r):
    W = 200; x0 = d.L + ef(d); x1 = d.L + W; y0 = d.desc * 0.6; y1 = d.asc
    pts = [(x1, y1), (x0, y1), (x0, y0), (x1, y0)]
    if not ouvre:
        pts = [(2 * d.L + W + ef(d) - p[0], p[1]) for p in pts]
    return [P(pts, d, (eg(d) * 0.75, ef(d)), r=r)], 2 * d.L + W + ef(d)


def parenleft(d):
    return _crochet(d, True, 190)


def parenright(d):
    return _crochet(d, False, 190)


def bracketleft(d):
    return _crochet(d, True, 0)


def bracketright(d):
    return _crochet(d, False, 0)


def _accolade(d, ouvre):
    t, ch = _crochet(d, ouvre, 60)
    ym = (d.desc * 0.6 + d.asc) / 2
    x0 = d.L + ef(d) if ouvre else ch - d.L - ef(d)
    t.append(P([(x0 - (70 if ouvre else -70), ym), (x0, ym)], d, ef(d) * 1.4, k=[0, 1.4]))
    return t, ch + 40 if ouvre else ch + 40


def braceleft(d):
    t, ch = _accolade(d, True)
    return decale(t, 40, 0), ch


def braceright(d):
    return _accolade(d, False)


def _math(d):
    return 560, d.cap * 0.5


def plus(d):
    W, y = _math(d); c = d.Lr + W / 2
    return [P([(d.Lr + 60, y), (d.Lr + W - 60, y)], d, ef(d) * 1.3), P([(c, y - 220), (c, y + 220)], d, ef(d) * 1.3)], 2 * d.Lr + W


def minus(d):
    W, y = _math(d)
    return [P([(d.Lr + 60, y), (d.Lr + W - 60, y)], d, ef(d) * 1.3)], 2 * d.Lr + W


def equal(d):
    W, y = _math(d)
    return [P([(d.Lr + 60, y + 80), (d.Lr + W - 60, y + 80)], d, ef(d) * 1.3), P([(d.Lr + 60, y - 80), (d.Lr + W - 60, y - 80)], d, ef(d) * 1.3)], 2 * d.Lr + W


def multiply(d):
    W, y = _math(d); c = d.Lr + W / 2; a = 170
    return [P([(c - a, y - a), (c + a, y + a)], d, ef(d) * 1.3), P([(c - a, y + a), (c + a, y - a)], d, ef(d) * 1.3)], 2 * d.Lr + W


def divide(d):
    W, y = _math(d); c = d.Lr + W / 2; s = _pt(d) * 0.85
    return [P([(d.Lr + 60, y), (d.Lr + W - 60, y)], d, ef(d) * 1.3), point(c, y + 170, s), point(c, y - 170, s)], 2 * d.Lr + W


def less(d):
    W, y = _math(d)
    return [P([(d.Lr + W - 70, y + 190), (d.Lr + 70, y), (d.Lr + W - 70, y - 190)], d, ef(d) * 1.3, r=d.c * 0.3)], 2 * d.Lr + W


def greater(d):
    W, y = _math(d)
    return [P([(d.Lr + 70, y + 190), (d.Lr + W - 70, y), (d.Lr + 70, y - 190)], d, ef(d) * 1.3, r=d.c * 0.3)], 2 * d.Lr + W


def asciitilde(d):
    W, y = _math(d); x = d.Lr + 60; w = W - 120
    return [P([(x, y - 40), (x + w * 0.3, y + 60), (x + w * 0.7, y - 60), (x + w, y + 40)], d, ef(d) * 1.3, r=70)], 2 * d.Lr + W


def asciicircum(d):
    W = 420; c = d.Lr + W / 2
    return [P([(d.Lr + 30, d.cap - 280), (c, d.cap), (d.Lr + W - 30, d.cap - 280)], d, ef(d) * 1.3, r=d.c * 0.3)], 2 * d.Lr + W


def numbersign(d):
    W = 600; x = d.Lr; y0 = d.cap * 0.32; y1 = d.cap * 0.68
    return [P([(x + 150, 0), (x + 230, d.cap)], d, ef(d) * 1.3, debut='h', fin='h'), P([(x + 370, 0), (x + 450, d.cap)], d, eg(d) * 0.8, debut='h', fin='h'),
            P([(x + 20, y0), (x + W - 30, y0)], d, ef(d) * 1.3), P([(x + 50, y1), (x + W, y1)], d, ef(d) * 1.3)], 2 * d.Lr + W


def asterisk(d):
    c = d.Lr + 180; y = d.cap - 170; a = 150; t = []
    for ang in (90, 30, 150):
        dx = a * math.cos(math.radians(ang)); dy = a * math.sin(math.radians(ang))
        t.append(P([(c - dx, y - dy), (c + dx, y + dy)], d, ef(d) * 1.4))
    return t, 2 * d.Lr + 360


def _petit(d, c, s, dx, dy, table=None):
    table = table or {**MINUSCULES, **CAPITALES, **CHIFFRES}
    t, ch = table[c](d)
    return reduit(t, s, dx, dy), ch * s


def percent(d):
    a, cha = _petit(d, 'o', 0.62, d.Lr, d.cap - d.x * 0.62 - 4)
    b, chb = _petit(d, 'o', 0.62, d.Lr + 400, 0)
    W = 400 + chb
    return a + b + [P([(d.Lr + 130, -20), (d.Lr + W - 130, d.cap + 20)], d, ef(d) * 1.2, debut='h', fin='h')], 2 * d.Lr + W


def degree(d):
    a, ch = _petit(d, 'o', 0.5, d.Lr, d.cap - d.x * 0.5)
    return a, 2 * d.Lr + ch


def ordfeminine(d):
    a, ch = _petit(d, 'a', 0.6, d.Lr, d.cap - d.x * 0.6)
    return a, d.Lr + ch


def ordmasculine(d):
    a, ch = _petit(d, 'o', 0.6, d.Lr, d.cap - d.x * 0.6)
    return a, d.Lr + ch


def _cercle(d):
    W = 760; x0 = d.Lr + 20; x1 = d.Lr + W - 20; y0 = -30; y1 = d.cap + 30
    return P([(x0, y0), (x0, y1), (x1, y1), (x1, y0)], d, ef(d) * 1.2, r=330, ferme=True), W


def copyright(d):
    c, W = _cercle(d)
    a, ch = _petit(d, 'C', 0.5, 0, 0)
    return [c] + decale(a, d.Lr + (W - ch) / 2 + 10, d.cap * 0.25), 2 * d.Lr + W


def registered(d):
    c, W = _cercle(d)
    a, ch = _petit(d, 'R', 0.5, 0, 0)
    return [c] + decale(a, d.Lr + (W - ch) / 2 + 10, d.cap * 0.25), 2 * d.Lr + W


def trademark(d):
    a, cha = _petit(d, 'T', 0.42, d.Lr, d.cap * 0.58)
    b, chb = _petit(d, 'M', 0.42, d.Lr + cha, d.cap * 0.58)
    return a + b, d.Lr + cha + chb + d.Lr


def _avec_trait(d, c, table, y0, y1, dx=0.0):
    t, ch = table[c](d)
    xs = [p[0] for u in t if not getattr(u, 'hors', False) for p in u.pts]
    cx = (min(xs) + max(xs)) / 2 + dx
    return t + [_signe(P([(cx - 12, y0), (cx + 12, y1)], d, ef(d) * 1.2, debut='h', fin='h'))], ch


def dollar(d):
    return _avec_trait(d, 'S', CAPITALES, -80, d.cap + 80)


def cent(d):
    return _avec_trait(d, 'c', MINUSCULES, -80, d.x + 80)


def euro(d):
    t, ch = CAPITALES['C'](d)
    x = d.Lr - 50
    return t + [_signe(P([(x, d.cap * 0.58), (x + 400, d.cap * 0.58)], d, ef(d) * 1.2, k=[0, 1])),
                _signe(P([(x, d.cap * 0.42), (x + 360, d.cap * 0.42)], d, ef(d) * 1.2, k=[0, 1]))], ch


def sterling(d):
    W = 520; xs = d.Lr + 150; top = d.haut(d.cap, True); xr = d.Lr + W
    return [T([(xr - 10, top - 120), (xr - 10, top), (xs, top), (xs, d.bas())], r=[140, 140], ep=(d.Fm, d.B), debut='h', k=[0.3, 1, 1, 1]),
            P([(d.Lr, d.bas()), (xr + 20, d.bas())], d, d.B, k=[1.3, 0]),
            P([(d.Lr + 20, d.cap * 0.45), (xs + 190, d.cap * 0.45)], d, ef(d) * 1.2)], 2 * d.Lr + W


def yen(d):
    t, ch = CAPITALES['Y'](d)
    c = ch / 2 + d.F * 0.2
    return t + [_signe(P([(c - 190, d.cap * 0.34), (c + 190, d.cap * 0.34)], d, ef(d) * 1.2)),
                _signe(P([(c - 190, d.cap * 0.18), (c + 190, d.cap * 0.18)], d, ef(d) * 1.2))], ch


def section(d):
    a, ch = _petit(d, 's', 0.9, d.Lr, d.cap - d.x * 0.9 + 6)
    b, _ = _petit(d, 's', 0.9, d.Lr, d.desc * 0.5)
    return a + b, d.Lr + ch


def paragraph(d):
    W = 520; xl, xr = d.gd(W, d.Lr); xm = xr - d.Fd / 2 - 110; top = d.haut(d.cap); ym = d.cap * 0.44
    return [fut(xr, d.desc * 0.6, d.cap), P([(xm, d.desc * 0.6), (xm, d.cap)], d, ef(d) * 1.2),
            T([(xr, top), (xl + 40, top), (xl + 40, ym), (xm, ym)], r=max((top - ym) / 2 - 1, 1), ep=(d.Fd * 1.2, d.B))], 2 * d.Lr + W


def ampersand(d):
    W = 640; xl, xr = d.gd(W, d.Lr); top = d.haut(d.cap, True); bas = d.bas(True); ym = d.cap * 0.52
    x1 = xl + (xr - xl) * 0.16; x2 = xl + (xr - xl) * 0.70
    r1 = max((top - ym) / 2 - 1, 1); r2 = max((ym - bas) / 2 - 1, 1)
    return [T([(x2, top), (x1, top), (x1, ym), (x1 + r1 + 4, ym)], r=r1, debut='v'),
            T([(xr + d.Fd / 2 + 50, ym), (xl, ym), (xl, bas), (xr, bas), (xr, ym - 2)], r=[r2, r2, r2], k=[0, 1, 1, 1, 1], fin='h')], 2 * d.Lr + W


def at(d):
    W = 840; x0 = d.Lr + 20; x1 = d.Lr + W - 20; y0 = -150; y1 = d.x + 150
    a, ch = _petit(d, 'a', 0.62, 0, 0)
    return [P([(x1 - 40, y0 + 70), (x1 - 300, y0), (x0, y0), (x0, y1), (x1, y1), (x1, y0 + 250)], d, ef(d) * 1.2, r=[40, 260, 260, 260], fin='h')] + \
        decale(a, d.Lr + (W - ch) / 2 + 20, (d.x - d.x * 0.62) / 2), 2 * d.Lr + W


SIGNES = {' ': espace, '.': point_, ',': virgule, ':': deux_points, ';': point_virgule, '!': exclam, '?': question,
          '¡': lambda d: exclam(d, True), '¿': lambda d: question(d, True), '…': points, '·': point_median, '•': puce,
          '’': quoteright, '‘': quoteleft, '”': quotedblright, '“': quotedblleft, '‚': quotesinglbase, '„': quotedblbase,
          "'": quotesingle, '"': quotedbl, '‹': guilsinglleft, '›': guilsinglright, '«': guillemotleft, '»': guillemotright,
          '-': hyphen, '–': endash, '—': emdash, '_': underscore, '/': slash, '\\': backslash, '|': bar,
          '(': parenleft, ')': parenright, '[': bracketleft, ']': bracketright, '{': braceleft, '}': braceright,
          '+': plus, '−': minus, '=': equal, '×': multiply, '÷': divide, '<': less, '>': greater, '~': asciitilde, '^': asciicircum,
          '#': numbersign, '*': asterisk, '%': percent, '°': degree, 'ª': ordfeminine, 'º': ordmasculine,
          '©': copyright, '®': registered, '™': trademark, '$': dollar, '¢': cent, '€': euro, '£': sterling, '¥': yen,
          '§': section, '¶': paragraph, '&': ampersand, '@': at}
