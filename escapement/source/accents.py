# Les accents et les lettres accentuées de la police de lecture.
#   accent(nom, poids, cap)            -> le dessin de l'accent, centré sur x = 0, posé sur y = 0
#   accentuee(c, poids, ovs=False)     -> (contour, chasse) d'une lettre accentuée
#   marque(c, poids)                   -> (contour, chasse) d'un accent seul (espaçant ou combinant)
import math, unicodedata
from functools import lru_cache
from lettres import M, lettre, bol, trait, larg_oblique, superellipse, GRAND, CAPS
from pieces import rect, poly, union, moins, coupe, decale, transforme, bornes
from signes import signe

COMBINANT = {'̀': 'grave', '́': 'acute', '̂': 'circumflex', '̃': 'tilde', '̄': 'macron',
             '̆': 'breve', '̇': 'dotaccent', '̈': 'dieresis', '̊': 'ring', '̋': 'hungarumlaut',
             '̌': 'caron', '̦': 'commaaccent', '̧': 'cedilla', '̨': 'ogonek'}
DESSOUS = {'commaaccent', 'cedilla', 'ogonek'}
# en letton, la cédille s'écrit comme une virgule ; le ģ la porte au-dessus ; ď ľ ť ont une apostrophe
VIRGULE_DESSOUS = set('ĶķĻļŅņŖŗĢ')
APOSTROPHE = set('ďľĽť')

ESPACANTS = {'`': 'grave', '´': 'acute', 'ˆ': 'circumflex', 'ˇ': 'caron', '¨': 'dieresis',
             '˙': 'dotaccent', '˚': 'ring', '˜': 'tilde', '¯': 'macron', '˘': 'breve',
             '˝': 'hungarumlaut', '¸': 'cedilla', '˛': 'ogonek'}
COMBINANTS = dict((c, n) for c, n in COMBINANT.items())


def _pt(m):
    return round(1.08 * m.f)


def _haut(m, cap):
    return round((0.20 if cap else 0.26) * m.X)


@lru_cache(None)
def accent(nom, poids, cap=False):
    m = M(poids); h = _haut(m, cap); e = round(0.88 * m.f); t = _pt(m); eh = round(0.85 * m.h)
    k = 1.15 if cap else 1.0                                  # les accents des capitales : plus plats, un peu plus larges
    if nom in ('acute', 'grave'):
        dx = round(0.75 * h * k); w = larg_oblique(e, dx, h)
        p = trait(-dx / 2, 0, dx / 2, h, w)
        return p if nom == 'acute' else transforme(p, (-1, 0, 0, 1, 0, 0))
    if nom in ('circumflex', 'caron'):
        d = round(0.95 * h * k); s = round(0.85 * e); w = larg_oblique(e, d - s / 2, h)
        g = poly((-d, 0), (-d + w, 0), (s / 2, h), (-s / 2, h))
        p = coupe(union(g, transforme(g, (-1, 0, 0, 1, 0, 0))), -GRAND, 0, GRAND, h)
        return p if nom == 'circumflex' else transforme(p, (1, 0, 0, -1, 0, h))
    if nom == 'dieresis':
        g = round(0.85 * t)
        return union(rect(-g / 2 - t, 0, -g / 2, t), rect(g / 2, 0, g / 2 + t, t))
    if nom == 'dotaccent':
        return rect(-t / 2, 0, t / 2, t)
    if nom == 'ring':
        r = round(0.62 * h) if not cap else round(0.75 * h)
        return bol(-r, r, 0, round(1.7 * r), round(0.82 * m.f), round(0.82 * m.f), eh, m.e)
    if nom == 'macron':
        L = round(1.25 * h * k + t)
        return rect(-L / 2, 0, L / 2, eh)
    if nom == 'tilde':
        L = round(1.2 * h * k + t); amp = round(0.22 * h); hh, bb = [], []
        for i in range(41):
            u = i / 40; x = -L / 2 + L * u
            v = amp * (1 - math.sin((u - 0.25) * 2 * math.pi))          # une vague : monte, descend
            hh.append((x, v + eh)); bb.append((x, v))
        return poly(*(hh + bb[::-1]))
    if nom == 'breve':
        L = round(1.15 * h * k + t); hb = round(0.70 * h)
        r = bol(-L / 2, L / 2, 0, 2 * hb, round(0.82 * m.f), round(0.82 * m.f), eh, m.e)
        return coupe(r, -GRAND, -GRAND, GRAND, hb)
    if nom == 'hungarumlaut':
        a = accent('acute', poids, cap); x0, _, x1, _ = bornes(a); g = round(0.25 * (x1 - x0)) + 20
        d = (x1 - x0 + g) / 2
        return union(decale(a, -d), decale(a, d))
    if nom == 'commaaccent':                 # la virgule de la police, en plus petit, sous la ligne
        p, _ = signe(',', poids); x0, y0, x1, y1 = bornes(p)
        q = transforme(p, (0.72, 0, 0, 0.72, 0, 0)); x0, y0, x1, y1 = bornes(q)
        return decale(q, -(x0 + x1) / 2, -y1)
    if nom == 'commaabove':                  # le ģ : la virgule retournée, au-dessus
        p = accent('commaaccent', poids)
        x0, y0, x1, y1 = bornes(p)
        q = transforme(p, (-1, 0, 0, -1, 0, 0))
        return decale(q, 0, -bornes(q)[1])
    if nom == 'apostrophe':                  # ď ľ ť
        p, _ = signe('’', poids); x0, y0, x1, y1 = bornes(p)
        q = transforme(p, (0.85, 0, 0, 0.85, 0, 0)); x0, y0, x1, y1 = bornes(q)
        return decale(q, -x0, -y0)
    if nom == 'cedilla':                     # comme Overshoot : un bout de fût, puis une virgule en biais
        w = round(0.70 * m.f + 6); y1 = -round(0.05 * m.X); y2 = -round(0.27 * m.X)
        queue = poly((-w / 2, y1), (w / 2 + 0.35 * w, y1), (-0.15 * w, y2), (-w / 2 - 0.95 * w, y2))
        return union(rect(-w / 2, y1 - 1, w / 2, 20), queue)
    if nom == 'ogonek':                      # comme Overshoot : le fût descend et tourne à droite, bout coupé à plat
        w = round(0.55 * m.f + 12); hb = round(0.62 * m.h)    # x = 0 : bord gauche du crochet
        larg = round(2.8 * w + 0.06 * m.X); bas = -round(0.22 * m.X); ry = max(round(0.13 * m.X), round(1.7 * hb))
        ring = bol(0, larg, bas, bas + 2 * ry, w, w, hb, m.e)
        ring = coupe(ring, -GRAND, -GRAND, GRAND, bas + ry)
        ring = moins(ring, rect(round(0.78 * larg), -GRAND, GRAND, GRAND))     # le bout coupé net, comme Overshoot
        return union(ring, rect(0, bas + ry - 1, w, 30))
    raise KeyError(nom)


def _base(c):
    """La lettre de base et la liste des accents d'une lettre accentuée."""
    d = unicodedata.normalize('NFD', c)
    base, marks = d[0], [COMBINANT[x] for x in d[1:]]
    if c in VIRGULE_DESSOUS:
        marks = ['commaaccent']
    if c == 'ģ':
        marks = ['commaabove']
    if c in APOSTROPHE:
        marks = ['apostrophe']
    if base == 'i' and any(n not in DESSOUS for n in marks):
        base = 'ı'
    if base == 'j' and any(n not in DESSOUS for n in marks):
        base = 'ȷ'
    return base, marks


def lettres_accentuees():
    """Les lettres accentuées du jeu d'Overshoot (hors ª º, faits dans signes.py)."""
    from fontTools.ttLib import TTFont
    import os
    ici = os.path.dirname(os.path.abspath(__file__))
    f = TTFont(os.path.join(ici, '..', '..', 'overshoot', 'fonts', 'otf', 'Overshoot-GentleBreeze.otf'))
    out = []
    for u in sorted(f.getBestCmap()):
        c = chr(u)
        if unicodedata.category(c).startswith('L') and unicodedata.decomposition(c) and c not in 'ªº':
            out.append(c)
    return ''.join(out)


ACCENTUEES = lettres_accentuees()


def _centre(base, p, m):
    """Le centre optique de la lettre, là où on pose l'accent."""
    x0, _, x1, _ = bornes(p)
    if base in ('a',):                      # le pied du a ne compte pas
        x1 -= m['pied']
    if base == 'R':
        x1 -= round(m['pied'] * 700 / 504)
    if base in 'ıiȷj':
        return x0 + m.f / 2
    return (x0 + x1) / 2


@lru_cache(None)
def accentuee(c, poids, ovs=False):
    m = M(poids)
    base, marks = _base(c)
    cap = base in CAPS
    p, ch = lettre(base, poids, ovs) if cap else lettre(base, poids)
    x0, y0, x1, y1 = bornes(p)
    cx = _centre(base, p, m)
    formes = [p]
    if cap:
        y = m['cap'] + round(0.10 * m['cap'])
    elif base in 'bdfhklł':
        y = m.ASC + round(0.08 * m.X)
    else:
        y = m.X + round(0.17 * m.X)
    for nom in marks:
        if nom == 'apostrophe':
            a = accent('apostrophe', poids)
            if base == 't':
                xs = x0 + round(0.25 * m.f) + m.f + round(0.35 * m.f) + 20
                formes.append(decale(a, xs, m.ASC + 10 - bornes(a)[3]))
            elif base == 'L':
                formes.append(decale(a, x0 + m['fut_cap'] + 50, m['cap'] - bornes(a)[3]))
            else:                           # ď ľ : à droite du fût
                formes.append(decale(a, x1 + 50, m.ASC - bornes(a)[3]))
            continue
        if nom in DESSOUS:
            if nom == 'ogonek':
                w = round(0.55 * m.f + 12)
                if base in 'aAuUiI':               # le fût du crochet sous le fût (ou la jambe) de droite
                    xr = x1 - (m['pied'] if base == 'a' else 0) - (round(0.08 * (x1 - x0)) if base == 'A' else 0)
                    xo = xr - (m['fut_cap'] if cap else m.f) * 0.5 - w / 2
                else:                              # e E : sous le bas de la courbe, un peu à droite du milieu
                    xo = x0 + 0.55 * (x1 - x0)
                formes.append(decale(accent('ogonek', poids), xo, 0))
            elif nom == 'cedilla':
                formes.append(decale(accent('cedilla', poids), cx, 0))
            else:
                formes.append(decale(accent(nom, poids), cx, -round(0.06 * m.X)))
            continue
        a = accent(nom, poids, cap or base in 'bdfhklł')
        formes.append(decale(a, cx, y))
        y += bornes(a)[3] - bornes(a)[1] + round(0.06 * m.X)
    q = union(*formes)
    # la chasse : celle de la base, élargie si l'accent dépasse (ď ľ ť)
    ch2 = max(ch, round(bornes(q)[2] + 0.6 * m.a)) if marks and marks[0] == 'apostrophe' else ch
    return q, ch2


@lru_cache(None)
def marque(c, poids):
    """Les accents seuls : espaçants (avec leur chasse) ou combinants (chasse 0, dessinés sur la lettre d'avant)."""
    m = M(poids)
    if c in ESPACANTS:
        a = accent(ESPACANTS[c], poids)
        x0, _, x1, _ = bornes(a)
        y = 0 if ESPACANTS[c] in DESSOUS else m.X + round(0.17 * m.X)
        if ESPACANTS[c] == 'ogonek':
            return decale(a, -x0 + m.a, 0), round(x1 - x0 + 2 * m.a)
        return decale(a, -x0 + m.a, y), round(x1 - x0 + 2 * m.a)
    nom = COMBINANTS[c]
    a = accent(nom, poids)
    y = (-round(0.07 * m.X) if nom == 'commaaccent' else 0) if nom in DESSOUS else m.X + round(0.17 * m.X)
    return decale(a, -round(0.5 * m['chasse_n']), y), 0
