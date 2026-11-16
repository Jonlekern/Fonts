# Les chiffres de la police de lecture, dessinés sur la recette d'Overshoot.
# Chaque chiffre : chiffre(c, poids, tab=False) -> (contour, chasse). tab=True : tous de la même chasse.
from functools import lru_cache
from pathops import Path
from lettres import M, superellipse, bol, demi_bol, trait, larg_oblique, cote_de, GRAND
from pieces import rect, poly, union, moins, coupe, decale, transforme, bornes

CHIFFRES = '0123456789'
LARG = {'0': 470, '1': 300, '2': 450, '3': 450, '4': 520 , '5': 450, '6': 470, '7': 440, '8': 470, '9': 470}
DESSIN = {}


def dessin(c):
    def enr(fn):
        DESSIN[c] = fn
        return fn
    return enr


def _mes(m, c):
    F, B, C, D = m['fut_cap'], m['barre_cap'], m['cap'], m['depasse']
    L = LARG[c] + 0.9 * (F - 117)
    return F, B, C, D, L


@dessin('0')
def _0(m, x0):
    F, B, C, D, L = _mes(m, '0')
    return bol(x0, x0 + L, -D, C + D, F, F, B, m.e), L


@dessin('1')
def _1(m, x0):
    F, B, C, D, L = _mes(m, '1')
    xs = x0 + L - F
    # le drapeau d'Overshoot : il part du haut du fût et descend en biais vers la gauche, bout coupé à la verticale
    dh = round(0.13 * C); fl = x0 + 0.05 * L
    drapeau = poly((xs + 1, C), (fl, C - dh), (fl, C - dh - round(0.95 * B)), (xs + 1, C - round(1.25 * B)))
    return union(rect(xs, 0, xs + F, C), drapeau), L


@dessin('2')
def _2(m, x0):
    F, B, C, D, L = _mes(m, '2')
    x1 = x0 + L; ry = round(0.28 * C + 0.5 * (F - 117)); cy = C + D - ry
    haut = coupe(bol(x0, x1, C + D - 2 * ry, C + D, F, F, B, m.e), -GRAND, cy, GRAND, GRAND)
    yd = round(0.50 * C)                                   # le côté droit descend tout droit jusqu'ici
    mur = rect(x1 - F, yd, x1, cy + 1)
    ep = round(0.95 * F); w = larg_oblique(ep, L - F, yd - B)
    # le bord gauche du biais part pile du bord intérieur du côté droit : pas de marche dans le blanc
    diag = trait(x1 - F + w / 2, yd, x0 + w / 2, B - 1, w)
    diag = coupe(diag, x0, -GRAND, x1, GRAND)
    return union(haut, mur, diag, rect(x0, 0, x1, B)), L


@dessin('3')
def _3(m, x0):
    F, B, C, D, L = _mes(m, '3')
    x1 = x0 + L; ym = round(0.50 * C - B / 2); cx = x0 + L / 2
    haut = bol(x0 + 0.06 * L, x1 - 0.04 * L, ym, C + D, F, F, B, m.e)
    haut = moins(haut, rect(-GRAND, ym - 1, cx, round(0.70 * C)))        # le bout du haut coupé à plat
    bas = bol(x0, x1, -D, ym + B, F, F, B, m.e)
    bas = moins(bas, rect(-GRAND, round(0.30 * C), cx, GRAND))            # le bout du bas coupé à plat
    milieu = rect(x0 + 0.30 * L, ym, cx + 1, ym + B)
    return union(haut, bas, milieu), L


@dessin('4')
def _4(m, x0):
    F, B, C, D, L = _mes(m, '4'); L += 0.9 * (F - 117)
    x1 = x0 + L; xs = x0 + round(0.70 * L) - F / 2; yb = round(0.24 * C)
    ep = round(0.92 * F); w = larg_oblique(ep, xs - x0, C - yb)
    diag = trait(xs + F - w / 2, C, x0 + w / 2, yb, w)
    diag = moins(diag, cote_de((xs + F, C), (xs + F, 0), gauche=False))
    diag = coupe(diag, x0, yb, GRAND, C)
    return union(rect(xs, 0, xs + F, C), diag, rect(x0, yb, x1, yb + B)), L


@dessin('5')
def _5(m, x0):
    F, B, C, D, L = _mes(m, '5')
    x1 = x0 + L; xs = x0 + 0.05 * L; yt = round(0.60 * C); cx = x0 + L / 2
    bas = bol(x0, x1, -D, yt, F, F, B, m.e)
    bas = moins(bas, rect(-GRAND, round(0.30 * C), cx, yt + 1))         # le bout du bas coupé à plat
    plat = rect(xs, yt - B, cx + 1, yt)                                  # le haut de la panse part à plat du fût
    return union(bas, plat, rect(xs, yt - B, xs + F, C), rect(xs, C - B, x1 - 0.02 * L, C)), L


@dessin('6')
def _6(m, x0):
    F, B, C, D, L = _mes(m, '6')
    x1 = x0 + L; yt = round(0.60 * C); ru = round(0.36 * C); cyu = C + D - ru; cx = x0 + L / 2
    bas = bol(x0, x1, -D, yt, F, F, B, m.e)
    haut = coupe(bol(x0, x1, C + D - 2 * ru, C + D, F, F, B, m.e), -GRAND, cyu, GRAND, GRAND)
    haut = moins(haut, rect(cx, -GRAND, GRAND, round(0.76 * C)))       # le bout du haut coupé à plat
    return union(bas, haut, rect(x0, (yt - D) / 2, x0 + F, cyu + 1)), L


@dessin('9')
def _9(m, x0):
    p, L = _6(m, x0)
    C = m['cap']
    return transforme(p, (-1, 0, 0, -1, 2 * x0 + L, C)), L


@dessin('7')
def _7(m, x0):
    F, B, C, D, L = _mes(m, '7')
    x1 = x0 + L; ep = round(0.95 * F); xb = x0 + round(0.22 * L)
    w = larg_oblique(ep, x1 - xb, C - B) * 0.92
    # la jambe légèrement creusée : deux bords en courbe, du haut à droite vers le bas
    p = Path(); pen = p.getPen()
    yt = C - B
    pen.moveTo((x1 - w, yt)); pen.lineTo((x1, yt))
    pen.curveTo((x1 - 0.30 * (x1 - xb), 0.55 * yt), (xb + w + 0.02 * L, 0.20 * yt), (xb + w, 0))
    pen.lineTo((xb, 0))
    pen.curveTo((xb + 0.02 * L, 0.22 * yt), (x1 - w - 0.32 * (x1 - xb), 0.58 * yt), (x1 - w, yt))
    pen.closePath()
    jambe = union(p)
    return union(rect(x0, C - B, x1, C), jambe), L


@dessin('8')
def _8(m, x0):
    F, B, C, D, L = _mes(m, '8')
    x1 = x0 + L; ym = round(0.53 * C - B / 2)
    haut = bol(x0 + 0.06 * L, x1 - 0.06 * L, ym, C + D, round(0.96 * F), round(0.96 * F), B, m.e)
    bas = bol(x0, x1, -D, ym + B, F, F, B, m.e)
    return union(haut, bas), L


@lru_cache(None)
def chiffre(c, poids, tab=False):
    m = M(poids); a = round(0.85 * m['approche_cap'])
    if not tab:
        p, L = DESSIN[c](m, a)
        if c == '1':
            return p, round(L + 2 * a + 10)
        return p, round(L + 2 * a)
    # tabulaires : la chasse du 0, chaque chiffre centré dedans
    _, L0 = DESSIN['0'](m, a); ch = round(L0 + 2 * a)
    p, L = DESSIN[c](m, a)      # jamais à x=0 : pathops s'y trompe parfois
    x0, _, x1, _ = bornes(p)
    return decale(p, (ch - (x1 - x0)) / 2 - x0), ch
