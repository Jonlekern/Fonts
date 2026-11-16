# La ponctuation et les signes de la police de lecture, sur la recette d'Overshoot.
# Chaque signe : signe(c, poids) -> (contour, chasse).
import math
from functools import lru_cache
from pathops import Path
from lettres import (M, lettre, bol, trait, larg_oblique, cote_de, superellipse, forme_s, SIGNES as SIGNES_ESSAI,
                     GRAND, _chevron)
from pieces import rect, poly, union, moins, coupe, decale, transforme, bornes, inter

SIGNES = {}


def signe_def(*cars):
    def enr(fn):
        for c in cars:
            SIGNES[c] = fn
        return fn
    return enr


def pt(m):
    return round(1.08 * m.f)


def mx(m):
    """L'axe des signes mathématiques et des tirets."""
    return round(0.40 * m['cap'])


def ep(m):
    return round(1.02 * m.h)


def tourne(p, deg, cx, cy):
    a = math.radians(deg); c, s = math.cos(a), math.sin(a)
    return transforme(p, (c, s, -s, c, cx - c * cx + s * cy, cy - s * cx - c * cy))


def sup(c, poids, echelle, x, y):
    """Une lettre en petit (ª º ™ © ®), prise dans une graisse plus grasse pour garder un trait solide."""
    plus = {300: 500, 400: 600, 500: 700, 600: 700, 700: 700}[poids]
    p, ch = lettre(c, plus)
    x0 = bornes(p)[0]
    return transforme(p, (echelle, 0, 0, echelle, x - x0 * echelle, y)), (bornes(p)[2] - x0) * echelle


# ---------- reprises de l'essai : . , ! « » ----------
for _c in '.,!«»':
    SIGNES[_c] = SIGNES_ESSAI[_c]


@signe_def(' ', ' ')
def _espace(m):
    return Path(), 250


@signe_def(':')
def _deux_points(m):
    t = pt(m); a = m.a - 5
    return union(rect(a, 0, a + t, t), rect(a, m.X - t, a + t, m.X)), 2 * a + t


@signe_def(';')
def _point_virgule(m):
    p, ch = SIGNES[','](m); t = pt(m); a = m.a - 5
    return union(p, rect(a, m.X - t, a + t, m.X)), ch


@signe_def('?')
def _quest(m):
    C, D = m['cap'], m.D; t = pt(m); a = m.ar; larg = round(2 * m.f + 0.62 * m.cn)
    x0, x1 = a, a + larg; cx = (x0 + x1) / 2
    ry = round(0.26 * C); haut = C + D; yb = haut - 2 * ry
    r = bol(x0, x1, yb, haut, m.f, m.f, m.h, m.e)
    r = moins(r, rect(-GRAND, -GRAND, cx, haut - ry))                # en bas à gauche : ouvert
    r = moins(r, rect(-GRAND, haut - ry - 1, x0 + m.f + 1, round(haut - 0.80 * ry)))  # le bout gauche coupé à plat
    tige = rect(cx - m.f / 2, t + round(0.9 * t), cx + m.f / 2, yb + m.h)
    return union(r, tige, rect(cx - t / 2, 0, cx + t / 2, t)), x1 + a - 10


def _retourne(m, p, ch):
    """¡ ¿ : le signe tête en bas, le point posé juste sous la hauteur d'x."""
    q = transforme(p, (-1, 0, 0, -1, ch, m['cap']))
    _, y0, _, y1 = bornes(q)
    return decale(q, 0, m.X - y1), ch


@signe_def('¡')
def _excl_inv(m):
    return _retourne(m, *SIGNES['!'](m))


@signe_def('¿')
def _quest_inv(m):
    return _retourne(m, *_quest(m))


# ---------- apostrophes et guillemets ----------

def _virgule_haut(m, x, y_haut):
    """La virgule de la police, posée avec son haut à y_haut."""
    p, _ = SIGNES[','](m)
    x0, y0, x1, y1 = bornes(p)
    return decale(p, x - x0, y_haut - y1)


def _largeur_virgule(m):
    x0, _, x1, _ = bornes(SIGNES[','](m)[0]); return x1 - x0


@signe_def('’')
def _apos_d(m):
    a = m.a - 5
    return _virgule_haut(m, a, m['cap']), 2 * a + _largeur_virgule(m)


@signe_def('‘')
def _apos_g(m):
    p, ch = _apos_d(m)
    x0, y0, x1, y1 = bornes(p)
    return transforme(p, (-1, 0, 0, -1, x0 + x1, y0 + y1)), ch


@signe_def('‚')
def _apos_bas(m):
    return SIGNES[','](m)


def _double(m, f):
    p, ch = f(m); w = _largeur_virgule(m); gap = round(0.55 * w) + 20
    return union(p, decale(p, w + gap)), ch + w + gap


@signe_def('”')
def _guil_d(m):
    return _double(m, _apos_d)


@signe_def('“')
def _guil_g(m):
    return _double(m, _apos_g)


@signe_def('„')
def _guil_bas(m):
    return _double(m, _apos_bas)


@signe_def("'")
def _apos_droit(m):
    a = m.a; w = round(0.95 * m.f)
    return rect(a, m['cap'] - round(0.30 * m['cap']), a + w, m['cap']), 2 * a + w


@signe_def('"')
def _guil_droit(m):
    a = m.a; w = round(0.95 * m.f); g = round(0.75 * w) + 20; h = round(0.30 * m['cap'])
    return union(rect(a, m['cap'] - h, a + w, m['cap']), rect(a + w + g, m['cap'] - h, a + 2 * w + g, m['cap'])), 2 * a + 2 * w + g


@signe_def('‹')
def _sguil_g(m):
    p = _chevron(m, m.a - 20, True)
    return p, bornes(p)[2] + m.a - 20


@signe_def('›')
def _sguil_d(m):
    p = _chevron(m, m.a - 20, False)
    return p, bornes(p)[2] + m.a - 20


# ---------- tirets et barres ----------

@signe_def('-')
def _trait_union(m):
    a = m.a - 10; L = round(0.42 * m['chasse_n'])
    y = round(0.45 * m.X - ep(m) / 2)
    return rect(a, y, a + L, y + ep(m)), 2 * a + L


@signe_def('–')
def _demi_cadratin(m):
    y = round(0.45 * m.X - ep(m) / 2)
    return rect(0, y, 500, y + ep(m)), 500


@signe_def('—')
def _cadratin(m):
    y = round(0.45 * m.X - ep(m) / 2)
    return rect(0, y, 1000, y + ep(m)), 1000


@signe_def('_')
def _souligne(m):
    return rect(0, -150, 500, -150 + ep(m)), 500


@signe_def('/')
def _barre(m):
    a = m.a - 30; L = round(0.42 * m['cap']); w = larg_oblique(round(0.9 * m.f), L, m['cap'] + 160)
    return trait(a + w / 2, -140, a + L - w / 2, m['cap'] + 20, w), 2 * a + L


@signe_def('\\')
def _barre_inv(m):
    p, ch = _barre(m)
    return transforme(p, (-1, 0, 0, 1, ch, 0)), ch


@signe_def('|')
def _barre_v(m):
    a = m.a + 20
    return rect(a, -200, a + round(0.9 * m.f), m.ASC + 40), 2 * a + round(0.9 * m.f)


# ---------- parenthèses, crochets, accolades ----------

def _paren(m):
    a = m.a; w = round(0.55 * m['cap']); haut = m.ASC + 30; bas = -190
    r = bol(a, a + 2 * w, bas, haut, round(0.92 * m.f), round(0.92 * m.f), round(0.8 * m.h), m.e)
    return coupe(r, -GRAND, -GRAND, a + 0.62 * w, GRAND), round(a + 0.62 * w + 0.8 * a)


@signe_def('(')
def _par_o(m):
    return _paren(m)


@signe_def(')')
def _par_f(m):
    p, ch = _paren(m)
    return transforme(p, (-1, 0, 0, 1, ch, 0)), ch


@signe_def('[')
def _cro_o(m):
    a = m.a + 10; w = round(0.92 * m.f); L = round(0.30 * m['cap']); haut = m.ASC + 30; bas = -190
    return union(rect(a, bas, a + w, haut), rect(a, haut - m.h, a + L, haut), rect(a, bas, a + L, bas + m.h)), a + L + m.a - 20


@signe_def(']')
def _cro_f(m):
    p, ch = _cro_o(m)
    return transforme(p, (-1, 0, 0, 1, ch, 0)), ch


@signe_def('{')
def _acc_o(m):
    a = m.a; w = round(0.90 * m.f); L = round(0.30 * m['cap']); haut = m.ASC + 30; bas = -190
    xs = a + round(0.12 * m['cap']); ym = (haut + bas) / 2
    nez = poly((a, ym + m.h / 2), (xs + 1, ym + m.h / 2 + 50), (xs + 1, ym - m.h / 2 - 50), (a, ym - m.h / 2))
    corps = union(rect(xs, bas, xs + w, haut), rect(xs, haut - m.h, xs + L, haut), rect(xs, bas, xs + L, bas + m.h), nez)
    return corps, xs + L + m.a - 20


@signe_def('}')
def _acc_f(m):
    p, ch = _acc_o(m)
    return transforme(p, (-1, 0, 0, 1, ch, 0)), ch


# ---------- signes mathématiques ----------

def _math(m):
    return 560, round(0.50 * 560 - 40)        # chasse, demi-longueur des traits


@signe_def('+')
def _plus(m):
    ch, d = _math(m); c = ch / 2; y = mx(m); e = ep(m)
    return union(rect(c - d, y - e / 2, c + d, y + e / 2), rect(c - e / 2, y - d, c + e / 2, y + d)), ch


@signe_def('−')
def _moins(m):
    ch, d = _math(m); c = ch / 2; y = mx(m); e = ep(m)
    return rect(c - d, y - e / 2, c + d, y + e / 2), ch


@signe_def('=')
def _egal(m):
    ch, d = _math(m); c = ch / 2; y = mx(m); e = ep(m); g = round(0.75 * e) + 30
    return union(rect(c - d, y + g / 2, c + d, y + g / 2 + e), rect(c - d, y - g / 2 - e, c + d, y - g / 2)), ch


@signe_def('×')
def _fois(m):
    ch, d = _math(m); c = ch / 2; y = mx(m); e = ep(m); d = round(0.80 * d)
    p = union(rect(c - d, y - e / 2, c + d, y + e / 2), rect(c - e / 2, y - d, c + e / 2, y + d))
    return tourne(p, 45, c, y), ch


@signe_def('÷')
def _divise(m):
    ch, d = _math(m); c = ch / 2; y = mx(m); e = ep(m); t = round(0.95 * pt(m)); g = e / 2 + 40
    return union(rect(c - d, y - e / 2, c + d, y + e / 2), rect(c - t / 2, y + g, c + t / 2, y + g + t),
                 rect(c - t / 2, y - g - t, c + t / 2, y - g)), ch


def _angle(m, vers_gauche):
    ch, d = _math(m); c = ch / 2; y = mx(m); e = round(0.95 * ep(m)); h = round(0.75 * d)
    x0, x1 = c - d, c + d
    w = e * math.hypot(x1 - x0, h) / (x1 - x0)          # épaisseur mesurée à la verticale
    haut = poly((x0, y - w / 2), (x1, y + h - w), (x1, y + h), (x0, y + w / 2))
    bas = transforme(haut, (1, 0, 0, -1, 0, 2 * y))
    p = coupe(union(haut, bas), x0 + 0.25 * e, -GRAND, GRAND, GRAND)
    if vers_gauche:
        return p, ch
    return transforme(p, (-1, 0, 0, 1, ch, 0)), ch


@signe_def('<')
def _inf(m):
    return _angle(m, True)


@signe_def('>')
def _sup(m):
    return _angle(m, False)


@signe_def('~')
def _tilde_ascii(m):
    ch, d = _math(m); c = ch / 2; y = mx(m); e = ep(m); amp = round(0.30 * d)
    haut_, bas_ = [], []
    for k in range(41):
        t = k / 40; x = c - d + 2 * d * t; v = y + amp * math.sin(t * 2 * math.pi)
        haut_.append((x, v + e / 2)); bas_.append((x, v - e / 2))
    return poly(*(haut_ + bas_[::-1])), ch


@signe_def('^')
def _circ_ascii(m):
    ch, d = _math(m); c = ch / 2; C = m['cap']; e = ep(m); h = round(0.36 * C)
    w = larg_oblique(e, d, h); s = round(0.9 * e)
    g = poly((c - d, C - h), (c - d + w, C - h), (c + s / 2, C), (c - s / 2, C))
    p = union(g, transforme(g, (-1, 0, 0, 1, ch, 0)))
    return coupe(p, -GRAND, -GRAND, GRAND, C), ch


# ---------- signes ----------

@signe_def('#')
def _diese(m):
    C = m['cap']; a = m.a - 20; L = round(0.70 * C); e = ep(m); w = round(0.95 * m.f)
    x0, x1 = a, a + L
    h1, h2 = round(0.30 * C), round(0.64 * C)
    barres = union(rect(x0, h1, x1, h1 + e), rect(x0 + 0.08 * L, h2, x1 + 0.08 * L, h2 + e))
    pente = 0.16 * L
    v1 = trait(x0 + 0.32 * L - pente / 2, 0, x0 + 0.32 * L + pente / 2, C, w)
    v2 = trait(x0 + 0.70 * L - pente / 2, 0, x0 + 0.70 * L + pente / 2, C, w)
    return union(barres, v1, v2), round(x1 + 0.08 * L + a)


@signe_def('%')
def _pourcent(m):
    C, D = m['cap'], m.D; a = m.a - 10; r = round(0.20 * C); e = round(0.92 * m.f)
    o1 = bol(a, a + 2 * r, round(0.52 * C), C + D, e, e, m.h, m.e)
    L = round(0.78 * C)
    o2 = bol(a + L - 2 * r, a + L, -D, round(0.48 * C), e, e, m.h, m.e)
    w = larg_oblique(round(0.9 * m.f), L - 2 * r, C)
    barre = trait(a + 0.30 * L, 0, a + 0.70 * L, C, w)
    return union(o1, o2, barre), a + L + a


@signe_def('&')
def _et(m):
    C, D = m['cap'], m.D; f, h, e = m['fut_cap'], m['barre_cap'], m.e
    a = m.a; L = round(0.86 * C + 0.9 * (f - 117)); x0, x1 = a, a + L
    yb = round(0.62 * C)
    haut = bol(x0 + 0.10 * L, x0 + 0.62 * L, round(0.56 * C), C + D, round(0.92 * f), round(0.92 * f), h, e)
    bas = bol(x0, x0 + 0.78 * L, -D, yb, f, f, h, e)
    bas = moins(bas, rect(x0 + 0.40 * L, round(0.30 * C), GRAND, GRAND))     # ouvert en haut à droite
    ep_ = round(0.95 * f)
    w = larg_oblique(ep_, x1 - (x0 + 0.20 * L), round(0.60 * C))
    diag = trait(x0 + 0.22 * L + w / 2, round(0.60 * C), x1 - w / 2, 0, w)
    diag = coupe(diag, -GRAND, 0, GRAND, round(0.60 * C))
    bras = rect(x0 + 0.62 * L, round(0.40 * C), x1, round(0.40 * C) + h)
    return union(haut, bas, diag, bras), x1 + a - 20


@signe_def('@')
def _arobase(m):
    C, D = m['cap'], m.D
    pa, cha = lettre('a', m.poids)
    xa0, ya0, xa1, ya1 = bornes(pa)
    e_ = round(0.85 * m.f); h = m.h
    marge = round(0.16 * C)
    x0 = m.a - 10; x1 = x0 + (xa1 - xa0) + 2 * marge + 2 * e_
    y0, y1 = -round(0.22 * C), C + D
    anneau = bol(x0, x1, y0, y1, e_, e_, h, m.e)
    cx = (x0 + x1) / 2
    a_ = decale(pa, x0 + e_ + marge - xa0, round((y0 + y1) / 2 - (ya0 + ya1) / 2))
    _, yab, _, _ = bornes(a_)
    anneau = moins(anneau, rect(cx, yab, GRAND, round(0.52 * C)))       # ouvert en bas à droite, bouts à plat
    return union(anneau, a_), x1 + m.a - 10


@signe_def('$')
def _dollar(m):
    p, ch = lettre('S', m.poids)
    x0, _, x1, _ = bornes(p); cx = (x0 + x1) / 2; w = round(0.80 * m.h)
    return union(p, rect(cx - w / 2, -110, cx + w / 2, m['cap'] + 110)), ch


@signe_def('¢')
def _cent(m):
    p, ch = lettre('c', m.poids)
    x0, _, x1, _ = bornes(p); cx = (x0 + x1) / 2 - 10; w = round(0.80 * m.h)
    return union(p, rect(cx - w / 2, -110, cx + w / 2, m.X + 110)), ch


@signe_def('€')
def _euro(m):
    p, ch = lettre('C', m.poids)
    dx = round(0.10 * m['cap']); p = decale(p, dx)
    x0, _, x1, _ = bornes(p); C = m['cap']; e = round(0.85 * m['barre_cap'])
    b1 = rect(m.a - 30, round(0.56 * C), x0 + 0.62 * (x1 - x0), round(0.56 * C) + e)
    b2 = rect(m.a - 30, round(0.36 * C), x0 + 0.55 * (x1 - x0), round(0.36 * C) + e)
    return union(p, b1, b2), ch + dx


@signe_def('£')
def _livre(m):
    C, D = m['cap'], m.D; F, B, e = m['fut_cap'], m['barre_cap'], m.e
    a = m.a - 10; L = round(0.70 * C + 0.9 * (F - 117)); x0, x1 = a, a + L
    xs = x0 + round(0.20 * L); ry = round(0.30 * C); cy = C + D - ry
    haut = coupe(bol(xs, xs + round(0.75 * L), C + D - 2 * ry, C + D, F, F, B, e), -GRAND, cy, GRAND, GRAND)
    haut = moins(haut, rect(xs + round(0.75 * L) / 2, -GRAND, GRAND, round(0.82 * C)))
    yb = round(0.40 * C)
    return union(haut, rect(xs, B - 1, xs + F, cy + 1), rect(x0, yb, xs + F + round(0.30 * L), yb + B),
                 rect(x0, 0, x1, B)), x1 + a


@signe_def('¥')
def _yen(m):
    p, ch = lettre('Y', m.poids)
    x0, _, x1, _ = bornes(p); cx = (x0 + x1) / 2; C = m['cap']; e = round(0.85 * m['barre_cap']); d = 0.36 * (x1 - x0)
    return union(p, rect(cx - d, round(0.16 * C), cx + d, round(0.16 * C) + e),
                 rect(cx - d, round(0.36 * C), cx + d, round(0.36 * C) + e)), ch


@signe_def('§')
def _paragraphe(m):
    a = m.ar + 4; larg = round(0.80 * (2 * m.f + m.cn + 34))
    f, h = round(0.92 * m.f), m.h
    s1 = forme_s(a, a + larg, m['cap'] + m.D, round(0.20 * m['cap']), f, h, h, m.e)
    s2 = forme_s(a, a + larg, round(0.55 * m['cap']), -m.D - round(0.20 * m['cap']), f, h, h, m.e)
    return union(s1, s2), a + larg + m.ar + 4


@signe_def('¶')
def _pied_de_mouche(m):
    C = m['cap']; a = m.a - 10; F = round(0.92 * m.f); bw = round(0.36 * C); g = round(0.10 * C)
    bas = round(0.38 * C)
    boule = superellipse(a + bw, (bas + C) / 2, bw, (C - bas) / 2, m.e)
    boule = union(coupe(boule, -GRAND, -GRAND, a + bw, GRAND), rect(a + bw, bas, a + bw + 2, C))
    x1 = a + bw + 2
    tiges = union(rect(x1, -140, x1 + F, C), rect(x1 + F + g, -140, x1 + 2 * F + g, C), rect(x1, C - m.h, x1 + 2 * F + g, C))
    return union(boule, tiges), x1 + 2 * F + g + m.a - 10


@signe_def('*')
def _asterisque(m):
    C = m['cap']; c = 300; y = round(0.70 * C); d = round(0.24 * C); e = ep(m)
    branche = rect(c - e / 2, y, c + e / 2, y + d)
    p = union(*[tourne(branche, k * 72, c, y) for k in range(5)])
    return p, 600


@signe_def('•')
def _puce(m):
    r = round(0.20 * m.X); a = m.a
    return superellipse(a + r, round(0.45 * m.X), r, r, m.e), 2 * a + 2 * r


@signe_def('·')
def _point_median(m):
    t = pt(m); a = m.a - 5; y = round(0.45 * m.X - t / 2)
    return rect(a, y, a + t, y + t), 2 * a + t


@signe_def('…')
def _points(m):
    t = pt(m); a = m.a - 5; g = round(1.5 * t)
    return union(*[rect(a + k * (t + g), 0, a + k * (t + g) + t, t) for k in range(3)]), 2 * a + 3 * t + 2 * g


@signe_def('°')
def _degre(m):
    C, D = m['cap'], m.D; r = round(0.17 * C); a = m.a - 10; e = round(0.85 * m.f)
    return bol(a, a + 2 * r, C + D - 2 * r, C + D, e, e, round(0.9 * m.h), m.e), 2 * a + 2 * r


def _cercle(m):
    C, D = m['cap'], m.D; a = m.a - 10; r = round((C + 2 * D) / 2); e = round(0.80 * m.f)
    return bol(a, a + 2 * r, -D, C + D, e, e, round(0.9 * m.h), 2.2), a, r


@signe_def('©')
def _copyright(m):
    o, a, r = _cercle(m)
    lp, w = sup('C', m.poids, 0.52, 0, 0)
    _, y0, _, y1 = bornes(lp)
    lp = decale(lp, a + r - w / 2, m['cap'] / 2 - (y0 + y1) / 2)
    return union(o, lp), 2 * a + 2 * r


@signe_def('®')
def _registered(m):
    o, a, r = _cercle(m)
    lp, w = sup('R', m.poids, 0.50, 0, 0)
    _, y0, _, y1 = bornes(lp)
    lp = decale(lp, a + r - w / 2, m['cap'] / 2 - (y0 + y1) / 2)
    return union(o, lp), 2 * a + 2 * r


@signe_def('™')
def _trademark(m):
    C = m['cap']; a = m.a - 10; s = 0.40
    t, wt = sup('T', m.poids, s, a, C - s * C)
    mm, wm = sup('M', m.poids, s, a + wt + 40, C - s * C)
    return union(t, mm), a + wt + 40 + wm + a


@signe_def('ª')
def _ordinal_a(m):
    s = 0.58; a = m.a - 10; y = round(m['cap'] - s * (m.X + m.D))
    p, w = sup('a', m.poids, s, a, y)
    return union(p, rect(a, y - round(0.16 * m['cap']), a + w, y - round(0.16 * m['cap']) + round(0.8 * m.h))), 2 * a + w


@signe_def('º')
def _ordinal_o(m):
    s = 0.58; a = m.a - 10; y = round(m['cap'] - s * (m.X + m.D))
    p, w = sup('o', m.poids, s, a, y)
    return union(p, rect(a, y - round(0.16 * m['cap']), a + w, y - round(0.16 * m['cap']) + round(0.8 * m.h))), 2 * a + w


@lru_cache(None)
def signe(c, poids):
    return SIGNES[c](M(poids))
