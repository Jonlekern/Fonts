# Les lettres de la police de lecture. Chaque lettre : lettre(c, poids, ovs) -> (contour, chasse).
from functools import lru_cache
import math
from mesures import mesures
from pieces import (inter as op_inter, rect, poly, union, moins, coupe, transforme, decale, miroir, superellipse, bornes)

GRAND = 5000
ESSAI_MIN = 'abcdefghijklmnopqrstuvwxyz'
ESSAI_CAP = 'ACEGHIKLMOQRSTW'

MIN = {}
CAPS = {}


def minuscule(*cars):
    def enr(fn):
        for c in cars:
            MIN[c] = fn
        return fn
    return enr


def capitale(*cars):
    def enr(fn):
        for c in cars:
            CAPS[c] = fn
        return fn
    return enr


@lru_cache(None)
def lettre(c, poids, ovs=False):
    if c in MIN:
        return MIN[c](M(poids))
    return CAPS[c](M(poids), ovs)


class M(dict):
    """Les mesures d'une graisse, avec les raccourcis du dessin."""
    def __init__(self, poids):
        super().__init__(mesures(poids))
        self.poids = poids
        self.f = self['fut_min']; self.h = self['barre_min']; self.e = self['expo']
        self.X = self['x']; self.D = self['depasse']; self.a = self['approche_min']
        self.ar = self.a - 10                       # les rondes s'approchent plus près
        self.fj = round(0.62 * self.f)              # trait aminci où la courbe rejoint le fût
        self.ASC = self['asc']; self.DESC = self['desc']
        self.cn = self['contre_n']

    def __hash__(self):
        return self.poids


# ---------- pièces de dessin ----------

def bol(x0, x1, y0, y1, ep_g, ep_d, ep_h, e, ep_b=None, e_ref=None):
    """Une ronde dans la boîte, avec ses épaisseurs : gauche, droite, haut (et bas).
    e_ref : quand la ronde est plus carrée que le texte (version de début de phrase), la contre-forme
    prend un exposant un peu plus bas, pour que le trait dans les coins reste aussi épais qu'avec e_ref."""
    ep_b = ep_h if ep_b is None else ep_b
    rx = (x1 - x0) / 2
    ext = superellipse((x0 + x1) / 2, (y0 + y1) / 2, rx, (y1 - y0) / 2, e)
    ix0, ix1, iy0, iy1 = x0 + ep_g, x1 - ep_d, y0 + ep_b, y1 - ep_h
    ei = e
    if e_ref is not None and e_ref != e:
        # sur la diagonale : rx·s(e) − rxi·s(ei) = ep·s(e_ref), avec s(n) = 2^(−1/n)
        s = lambda n: 2 ** (-1 / n)
        rxi = (ix1 - ix0) / 2; ep = (ep_g + ep_d) / 2
        si = (rx * s(e) - ep * s(e_ref)) / rxi
        ei = -1 / math.log2(si)
    inn = superellipse((ix0 + ix1) / 2, (iy0 + iy1) / 2, (ix1 - ix0) / 2, (iy1 - iy0) / 2, ei)
    return moins(ext, inn)


def arche(m, x0, x1, ep_g, ep_d, ry=None, haut=None):
    """L'épaule du n : le haut d'une ronde, puis la jambe droite qui descend à la ligne."""
    haut = m.X + m.D if haut is None else haut
    ry = ry or round(0.58 * m.X)
    cy = haut - ry
    r = bol(x0, x1, cy - ry, haut, ep_g, ep_d, m.h, m.e)
    return union(coupe(r, -GRAND, cy, GRAND, GRAND), rect(x1 - ep_d, 0, x1, cy + 1))


def pied(xd, larg, haut):
    """Le petit pied d'Overshoot : le fût s'évase vers la droite en touchant la ligne."""
    return moins(rect(xd - 1, 0, xd + larg, haut), superellipse(xd + larg, haut, larg, haut, 2))


def trait(x0, y0, x1, y1, larg):
    """Un trait droit de (x0,y0) à (x1,y1), bouts coupés à l'horizontale, larg = largeur horizontale."""
    return poly((x0 - larg / 2, y0), (x0 + larg / 2, y0), (x1 + larg / 2, y1), (x1 - larg / 2, y1))


def larg_oblique(ep, dx, dy):
    """Largeur horizontale d'un trait oblique pour qu'il fasse ep d'épaisseur."""
    return ep * math.hypot(dx, dy) / abs(dy)


def cote_de(p0, p1, gauche=True):
    """Le demi-plan à gauche (ou à droite) de la ligne p0 -> p1, comme une grande forme."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    a = (p0[0] - 20 * dx, p0[1] - 20 * dy); b = (p0[0] + 20 * dx, p0[1] + 20 * dy)
    s = -GRAND if gauche else GRAND
    return poly(a, b, (b[0] + s, b[1]), (a[0] + s, a[1]))


def jambe_k(a, F, x1, ya, haut, ep, fin):
    """Le bras et la jambe du k et du K, sans marche à la jonction."""
    w = larg_oblique(ep, x1 - (a + F), haut - ya)
    dx, dy = x1 - w / 2 - (a + F / 2), haut - ya          # le bras part du fond du fût : pas de petit bout plat qui dépasse
    bras = coupe(trait(a + F / 2 - 0.3 * dx, ya - 0.3 * dy, x1 - w / 2, haut, w), a + F / 2, 0, GRAND, GRAND)
    t = 0.40; xm = a + F / 2 + t * (x1 - w / 2 - a - F / 2); ym = ya + t * (haut - ya)
    wl = larg_oblique(ep, fin - xm, ym)
    xb = fin - wl / 2; k = 0.6                     # on prolonge la jambe vers le haut, puis on la coupe au bord haut du bras
    jambe = trait(xm - k * (xb - xm), ym + k * ym, xb, 0, wl)
    jambe = moins(jambe, cote_de((a + F / 2 + w / 2, ya), (x1, haut), gauche=True))
    return union(bras, jambe)


def point_i(m, x):
    """Le point carré du i et du j : jamais plus haut que les montantes."""
    t = round(1.05 * m.f)
    bas = min(m.X + max(70, round(0.85 * m.f)), m.ASC - t)
    return rect(x, bas, x + m.f, bas + t)


# ---------- les minuscules ----------

def fut_epaule(m, a, ar):
    """Le fût d'une lettre à épaule (n m r) : il s'arrête pile à la hauteur de l'épaule, sans petite marche."""
    yj = coupe(ar, a + m.f - 0.5, -GRAND, a + m.f, GRAND).bounds[3]
    return rect(a, 0, a + m.f, min(m.X, yj))


@minuscule('n')
def _n(m):
    ch = m['chasse_n']; a, f = m.a, m.f
    ar = arche(m, a + f - m.fj, ch - a, m.fj, f)
    return union(fut_epaule(m, a, ar), ar), ch


@minuscule('h')
def _h(m):
    ch = m['chasse_n']; a, f = m.a, m.f
    return union(rect(a, 0, a + f, m.ASC), arche(m, a + f - m.fj, ch - a, m.fj, f)), ch


@minuscule('m')
def _m(m):
    a, f = m.a, m.f; cm = round(0.80 * m.cn); ch = 3 * f + 2 * cm + 2 * a
    x2 = a + 2 * f + cm
    ar1 = arche(m, a + f - m.fj, x2, m.fj, f, ry=round(0.52 * m.X))
    return union(fut_epaule(m, a, ar1), ar1,
                 arche(m, x2 - m.fj, ch - a, m.fj, f, ry=round(0.52 * m.X))), ch


@minuscule('u')
def _u(m):
    p, ch = _n(m)
    return transforme(p, (-1, 0, 0, -1, ch, m.X)), ch


@minuscule('r')
def _r(m):
    a, f = m.a, m.f; x1 = a + f + round(0.62 * m.cn) + f
    ar = arche(m, a + f - m.fj, x1, m.fj, round(0.9 * f))
    cx = (a + f - m.fj + x1) / 2
    ar = moins(ar, rect(cx, -GRAND, GRAND, round(0.64 * m.X)))     # le bout coupé à plat
    return union(fut_epaule(m, a, ar), ar), x1 + a - 25


def _o_boite(m):
    larg = 2 * m.f + m.cn + 34
    return m.ar, m.ar + larg


@minuscule('o')
def _o(m):
    x0, x1 = _o_boite(m)
    return bol(x0, x1, -m.D, m.X + m.D, m.f, m.f, m.h, m.e), x1 + m.ar


def _panse(m, cote):
    """b d p q : le fût et sa panse ; cote = côté du fût."""
    a, f = m.a, m.f; larg = f + m.cn + 34 + f
    x0, x1 = a + f - m.fj, a + larg
    p = bol(x0, x1, -m.D, m.X + m.D, m.fj, f, m.h, m.e)
    ch = x1 + m.ar
    return p, ch


def _b(m):
    p, ch = _panse(m, 'g')
    return union(p, rect(m.a, 0, m.a + m.f, m.ASC)), ch


def _p(m):
    p, ch = _panse(m, 'g')
    return union(p, rect(m.a, m.DESC, m.a + m.f, m.X)), ch


MIN['b'] = _b
MIN['p'] = _p
MIN['d'] = lambda m: (lambda pc: (miroir(pc[0], pc[1]), pc[1]))(_b(m))
MIN['q'] = lambda m: (lambda pc: (miroir(pc[0], pc[1]), pc[1]))(_p(m))


@minuscule('c')
def _c(m):
    x0, x1 = _o_boite(m)
    o = bol(x0, x1, -m.D, m.X + m.D, m.f, m.f, m.h, m.e)
    cx = (x0 + x1) / 2
    return moins(o, rect(cx + 0.18 * (x1 - x0), round(0.30 * m.X), GRAND, round(0.70 * m.X))), x1 + m.ar - 22


@minuscule('e')
def _e(m):
    x0, x1 = _o_boite(m)
    ext = superellipse((x0 + x1) / 2, m.X / 2, (x1 - x0) / 2, m.X / 2 + m.D, m.e)
    o = bol(x0, x1, -m.D, m.X + m.D, m.f, m.f, m.h, m.e)
    yb = round(0.46 * m.X - 0.3 * (m.f - 88))
    barre = coupe(ext, x0 + m.f / 2, yb, x1, yb + m.h)
    cx = (x0 + x1) / 2
    return moins(union(o, barre), rect(cx + 0.18 * (x1 - x0), round(0.26 * m.X), GRAND, yb)), x1 + m.ar - 8


def forme_s(x0, x1, haut, bas, f, h, hs, e, e_ref=None):
    """Le s : deux ronds empilés, l'un ouvert à droite en bas, l'autre à gauche en haut, bouts plats."""
    r = (haut - bas + hs) / 4; cx = (x0 + x1) / 2
    cyh = haut - r; cyb = bas + r
    rh = bol(x0 + 0.02 * (x1 - x0), x1 - 0.02 * (x1 - x0), cyh - r, haut, f, f, h, e, ep_b=hs, e_ref=e_ref)
    rb = bol(x0, x1, bas, cyb + r, f, f, hs, e, ep_b=h, e_ref=e_ref)
    rh = moins(rh, rect(cx, -GRAND, GRAND, cyh + 0.28 * r))
    rb = moins(rb, rect(-GRAND, cyb - 0.28 * r, cx, GRAND))
    return union(rh, rb)


@minuscule('s')
def _s(m):
    a = m.ar + 4; larg = round(0.80 * (2 * m.f + m.cn + 34))
    return forme_s(a, a + larg, m.X + m.D, -m.D, round(0.94 * m.f), m.h, round(1.05 * m.h), m.e), a + larg + m.ar + 4


@minuscule('l')
def _l(m):
    return rect(m.a, 0, m.a + m.f, m.ASC), 2 * m.a + m.f


@minuscule('i')
def _i(m):
    return union(rect(m.a, 0, m.a + m.f, m.X), point_i(m, m.a)), 2 * m.a + m.f


def _crochet_bas(m, xd, larg, cote):
    """Le crochet du j : le fût tourne à gauche sous la ligne, bas aplati comme Overshoot,
    bout coupé en biais « / » qui file sous la lettre d'avant."""
    y0 = m.DESC - 4; ry = round(1.35 * m.f); x0 = xd - larg
    r = bol(x0, xd, y0, y0 + 2 * ry, m.f, m.f, m.h, m.e)
    r = coupe(r, -GRAND, -GRAND, GRAND, y0 + ry)
    cy = y0 + ry
    biais = cote_de((x0 + 0.02 * larg, y0), (x0 + 0.30 * larg, cy), gauche=True)
    return moins(r, biais), cy


@minuscule('j')
def _j(m):
    a, f = m.a, m.f; xs = a + 60
    cr, cy = _crochet_bas(m, xs + f, round(3.4 * f + 40), 'g')
    return union(rect(xs, cy - 1, xs + f, m.X), cr, point_i(m, xs)), xs + f + a


@minuscule('f')
def _f(m):
    a, f = m.a, m.f; xs = a + round(0.25 * f)
    larg = round(2.7 * f) + 40; ry = round(1.35 * f)
    haut = m.ASC + m.D
    r = bol(xs, xs + larg, haut - 2 * ry, haut, f, f, m.h, m.e)
    cy = haut - ry
    r = coupe(r, xs - 1, cy, GRAND, GRAND)
    r = moins(r, rect(xs + larg / 2, -GRAND, GRAND, cy + 0.35 * ry))
    barre = rect(a - round(0.15 * f), m.X - m.h, xs + f + round(1.3 * f), m.X)
    return union(rect(xs, 0, xs + f, cy + 1), r, barre), xs + larg - 15 + round(0.3 * a)


@minuscule('t')
def _t(m):
    a, f = m.a, m.f; xs = a + round(0.25 * f)
    larg = round(2.3 * f) + 60; ry = round(0.30 * m.X)
    r = bol(xs, xs + larg, -m.D, -m.D + 2 * ry, f, round(0.9 * f), m.h, m.e)
    cy = -m.D + ry
    r = coupe(r, xs - 1, -GRAND, GRAND, cy)
    r = moins(r, rect(xs + larg / 2, round(-m.D + 0.80 * ry), GRAND, GRAND))     # le bout coupé à plat
    barre = rect(a - round(0.15 * f), m.X - m.h, xs + f + round(1.3 * f), m.X)
    return union(rect(xs, cy - 1, xs + f, round(m.X + 0.27 * (m.ASC - m.X))), r, barre), xs + larg - 10 + round(0.3 * a)


def _a_sans_pied(m):
    p, ch = _a_corps(m)
    return p, ch


@minuscule('a')
def _a(m):
    p, xd = _a_corps(m)
    return union(p, pied(xd, m['pied'], 3 * m['pied'])), xd + m['pied'] + m.a - 6


def _a_corps(m):
    a, f = m.ar + 4, m.f
    larg = 2 * f + round(0.92 * m.cn) + 20
    x0, xd = a, a + larg
    ry = round(0.36 * m.X)
    haut = bol(x0 + 8, xd, m.X + m.D - 2 * ry, m.X + m.D, f, f, m.h, m.e)
    cy = m.X + m.D - ry
    haut = coupe(haut, -GRAND, cy, GRAND, GRAND)
    haut = moins(haut, rect(-GRAND, -GRAND, (x0 + xd) / 2, round(0.70 * m.X)))
    yb = round(0.55 * m.X + 0.7 * (f - 88))
    panse = bol(x0, xd - f + m.fj, -m.D, yb, f, m.fj, m.h, m.e)
    return union(haut, rect(xd - f, 0, xd, cy + 1), panse), xd


@minuscule('g')
def _g(m):
    a, f = m.ar, m.f; larg = f + m.cn + 34 + f
    x0, x1 = a, a + larg
    panse = bol(x0, x1 - f + m.fj, -m.D + 40, m.X + m.D, f, m.fj, m.h, m.e)
    y0 = m.DESC - 4; ry = round(0.40 * (m.X))
    cr = bol(x0 + 10, x1, y0, y0 + 2 * ry, f, f, m.h, m.e)
    cy = y0 + ry
    cr = coupe(cr, -GRAND, -GRAND, GRAND, cy)
    cr = moins(cr, rect(-GRAND, y0 + round(0.55 * ry), (x0 + x1) / 2, GRAND))
    return union(panse, cr, rect(x1 - f, cy - 1, x1, m.X)), x1 + m.a


def _v_traits(m, x0, x1, haut, bas_larg, ep):
    """Le v : deux traits qui se rejoignent en bas sur un plat."""
    cx = (x0 + x1) / 2
    dx = cx - bas_larg / 2 - x0; w = larg_oblique(ep, dx, haut)
    g = poly((x0, haut), (x0 + w, haut), (cx - bas_larg / 2 + w, 0), (cx - bas_larg / 2, 0))
    d = poly((x1 - w, haut), (x1, haut), (cx + bas_larg / 2, 0), (cx + bas_larg / 2 - w, 0))
    # en bas, chaque trait s'arrête au bord extérieur de l'autre : pas de petit bout qui dépasse
    g = moins(g, cote_de((x1, haut), (cx + bas_larg / 2, 0), gauche=False))
    d = moins(d, cote_de((x0, haut), (cx - bas_larg / 2, 0), gauche=True))
    return union(g, d), w


@minuscule('v')
def _v(m):
    larg = round(0.98 * (2 * m.f + m.cn)) + 30; x0 = m.a - 25
    p, _ = _v_traits(m, x0, x0 + larg, m.X, round(1.0 * m.f), round(0.92 * m.f))
    return p, x0 + larg + m.a - 25


@minuscule('w')
def _w(m):
    lv = round(0.80 * (2 * m.f + m.cn)) + 20; x0 = m.a - 30
    ep = round(0.86 * m.f); bl = round(0.95 * m.f)
    g, w = _v_traits(m, x0, x0 + lv, m.X, bl, ep)
    d, _ = _v_traits(m, x0 + lv - w, x0 + 2 * lv - w, m.X, bl, ep)
    return union(g, d), x0 + 2 * lv - w + m.a - 30


@minuscule('y')
def _y(m):
    larg = round(0.98 * (2 * m.f + m.cn)) + 30; x0 = m.a - 25; x1 = x0 + larg
    ep = round(0.92 * m.f); yb = m.DESC
    # comme Overshoot : le trait de droite file tout droit sous la ligne, bout coupé à plat
    xb = x0 + round(0.30 * larg)
    w = larg_oblique(ep, x1 - xb, m.X - yb)
    droite = trait(x1 - w / 2, m.X, xb, yb, w)
    xr0 = (x1 - w / 2) + (xb - (x1 - w / 2)) * m.X / (m.X - yb)
    wg = larg_oblique(ep, xr0 - x0, m.X)
    gauche = trait(x0 + wg / 2, m.X, xr0 - w / 2 + wg / 2, 0, wg)
    gauche = moins(gauche, cote_de((x1 - w, m.X), (xb - w / 2, yb), gauche=False))
    return union(droite, gauche), x1 + m.a - 25


@minuscule('x')
def _x(m):
    larg = round(0.95 * (2 * m.f + m.cn)) + 20; x0 = m.a - 25; x1 = x0 + larg
    ep = round(0.92 * m.f); w = larg_oblique(ep, x1 - x0, m.X)
    return union(poly((x0, m.X), (x0 + w, m.X), (x1, 0), (x1 - w, 0)),
                 poly((x1 - w, m.X), (x1, m.X), (x0 + w, 0), (x0, 0))), x1 + m.a - 25


@minuscule('z')
def _z(m):
    larg = round(0.88 * (2 * m.f + m.cn)); x0 = m.a - 10; x1 = x0 + larg
    hz = round(1.0 * m.h); w = larg_oblique(round(0.86 * m.f), x1 - x0, m.X - 2 * hz)
    return union(rect(x0 + 8, m.X - hz, x1, m.X), rect(x0, 0, x1 + 4, hz),
                 poly((x1 - w, m.X - hz), (x1, m.X - hz), (x0 + w, hz), (x0, hz))), x1 + m.a - 10


@minuscule('k')
def _k(m):
    a, f = m.a, m.f; larg = round(0.90 * (2 * f + m.cn))
    x1 = a + larg
    return union(rect(a, 0, a + f, m.ASC), jambe_k(a, f, x1, round(0.30 * m.X), m.X, round(0.92 * f), x1 + 10)), x1 + 10 + m.a - 22


# ---------- les capitales et leur version de début de phrase ----------
# Chaque capitale se dessine pour une largeur d'encre L. La version de début de phrase (ovs) garde
# la hauteur et les traits, prend les rondes d'Overshoot (expo_ovs) et assez de largeur en plus
# pour que sa chasse fasse large_ovs fois la chasse normale.

LARGEURS = {'A': 600, 'C': 560, 'E': 460, 'G': 600, 'H': 560, 'I': 0, 'K': 540, 'L': 430, 'M': 680,
            'O': 620, 'Q': 620, 'R': 530, 'S': 500, 'T': 560, 'W': 880,
            'B': 520, 'D': 580, 'F': 440, 'J': 420, 'N': 580, 'P': 510, 'U': 560, 'V': 600, 'X': 580,
            'Y': 580, 'Z': 520, 'Æ': 820, 'Œ': 880, 'Ø': 620, 'Ð': 580, 'Þ': 500, 'Ł': 430, 'Đ': 580,
            'Ħ': 560, 'ẞ': 540}
CAPS_TOUTES = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' + 'ÆŒØÐÞŁĐĦẞ'
DESSINS = {}


def dessin(c):
    def enr(fn):
        DESSINS[c] = fn; CAPS[c] = _cap(c)
        return fn
    return enr


def _cap(c):
    def fn(m, ovs):
        L0 = (LARGEURS[c] + 0.9 * (m['fut_cap'] - 117)) if c != 'I' else m['fut_cap']
        p, ch = DESSINS[c](m, L0, m.e, 0)
        if not ovs:
            return p, ch
        plus = (m['large_ovs'] - 1) * ch
        if c == 'I':      # le I ne s'élargit pas : il prend de l'air
            return decale(p, plus / 2), ch + plus
        p2, ch2 = DESSINS[c](m, L0 + plus, m['expo_ovs'], 0)
        # la chasse dessinée, tenue entre 1,20 et 1,25 fois la normale (le Q garde la place de sa dalle)
        return p2, min(max(round(ch2), round(ch * 1.20)), round(ch * 1.25))
    return fn


def demi_bol(xg, xd, y0, y1, F, ep_d, ep_h, e):
    """La panse du D, du P, du R : plate à gauche (contre le fût), ronde à droite."""
    ry = (y1 - y0) / 2; rx = min((xd - xg) * 0.6, ry * 1.15); cx = xd - rx; cy = (y0 + y1) / 2
    ext = union(rect(xg, y0, cx + 1, y1), coupe(superellipse(cx, cy, rx, ry, e), cx, -GRAND, GRAND, GRAND))
    inn = union(rect(xg + F, y0 + ep_h, cx + 1, y1 - ep_h),
                coupe(superellipse(cx, cy, rx - ep_d, ry - ep_h, e), cx, -GRAND, GRAND, GRAND))
    return moins(ext, inn)


def _ac(m):
    return m['approche_cap']


@dessin('H')
def _H(m, L, e, _):
    a, F, B, C = _ac(m), m['fut_cap'], m['barre_cap'], m['cap']
    yb = round(0.49 * C - B / 2)
    return union(rect(a, 0, a + F, C), rect(a + L - F, 0, a + L, C), rect(a, yb, a + L, yb + B)), round(2 * a + L)


@dessin('I')
def _I(m, L, e, _):
    a, F = _ac(m), m['fut_cap']
    return rect(a, 0, a + F, m['cap']), 2 * a + F


@dessin('L')
def _L(m, L, e, _):
    a, F, B, C = _ac(m), m['fut_cap'], m['barre_cap'], m['cap']
    return union(rect(a, 0, a + F, C), rect(a, 0, a + L, B)), round(a + L + a - 25)


@dessin('E')
def _E(m, L, e, _):
    a, F, B, C = _ac(m), m['fut_cap'], m['barre_cap'], m['cap']
    yb = round(0.49 * C - B / 2)
    return union(rect(a, 0, a + F, C), rect(a, 0, a + L, B), rect(a, C - B, a + L - 8, C),
                 rect(a, yb, a + L - 0.10 * L, yb + B)), round(a + L + a - 20)


@dessin('T')
def _T(m, L, e, _):
    a, F, B, C = _ac(m) - 30, m['fut_cap'], m['barre_cap'], m['cap']
    cx = a + L / 2
    return union(rect(a, C - B, a + L, C), rect(cx - F / 2, 0, cx + F / 2, C)), round(2 * a + L)


def _O_forme(m, L, e):
    a, F, B, C, D = _ac(m) - 14, m['fut_cap'], m['barre_cap'], m['cap'], m['depasse']
    return bol(a, a + L, -D, C + D, round(1.04 * F), round(1.04 * F), B, e, e_ref=m.e), a, a + L


@dessin('O')
def _O(m, L, e, _):
    p, x0, x1 = _O_forme(m, L, e)
    return p, round(x1 + x0)


@dessin('C')
def _C(m, L, e, _):
    p, x0, x1 = _O_forme(m, L, e); C = m['cap']
    p = moins(p, rect((x0 + x1) / 2 + 0.16 * L, round(0.30 * C), GRAND, round(0.70 * C)))
    return p, round(x1 + x0 - 22)


@dessin('G')
def _G(m, L, e, _):
    p, x0, x1 = _O_forme(m, L, e); C, B, F = m['cap'], m['barre_cap'], m['fut_cap']
    yh = round(0.45 * C + B / 2)
    p = moins(p, rect((x0 + x1) / 2 + 0.16 * L, yh - B, GRAND, round(0.69 * C)))
    # l'éperon : la barre rentre, puis le fût descend en coin net
    yc = coupe(p, x1 - F - 0.01, -GRAND, x1 - F, round(0.3 * C)).bounds[1]   # où la courbe du bas croise le fût
    p = moins(p, rect(x1 - F, -GRAND, GRAND, yh))
    eperon = union(rect((x0 + x1) / 2 + 0.06 * L, yh - B, x1, yh), rect(x1 - F, yc, x1, yh))
    return union(p, eperon), round(x1 + x0)


@dessin('Q')
def _Q(m, L, e, _):
    p, x0, x1 = _O_forme(m, L, e); C, B, D = m['cap'], m['barre_cap'], m['depasse']
    cx = (x0 + x1) / 2
    p = moins(p, rect(cx + 0.08 * L, -GRAND, GRAND, round(-D + 1.75 * B)))
    p = moins(p, rect(cx, -D + B, cx + 0.08 * L + 1, round(-D + 1.75 * B)))    # le bas de la panse s'arrête pile sur la dalle
    dalle = rect(cx, -D, x1 + 0.10 * L, -D + B)
    return union(p, dalle), round(x1 + 0.10 * L + x0 - 10)


@dessin('R')
def _R(m, L, e, _):
    a, F, B, C = _ac(m), m['fut_cap'], m['barre_cap'], m['cap']
    x1 = a + L; yb = round(0.42 * C)
    panse = demi_bol(a, x1, yb, C, F, round(1.02 * F), B, e)
    jambe = rect(x1 - F, 0, x1, round((yb + C) / 2))
    pd = round(m['pied'] * 700 / 504)
    return union(rect(a, 0, a + F, C), panse, jambe, pied(x1, pd, 3 * pd)), round(x1 + pd + a - 20)


@dessin('S')
def _S(m, L, e, _):
    a, F, B, C, D = _ac(m) - 10, m['fut_cap'], m['barre_cap'], m['cap'], m['depasse']
    return forme_s(a, a + L, C + D, -D, round(0.95 * F), B, round(1.05 * B), e, e_ref=m.e), round(2 * a + L)


@dessin('K')
def _K(m, L, e, _):
    a, F, C = _ac(m), m['fut_cap'], m['cap']; x1 = a + L
    return union(rect(a, 0, a + F, C), jambe_k(a, F, x1, round(0.30 * C), C, round(0.92 * F), x1 + 10)), round(x1 + 10 + a - 25)


@dessin('A')
def _A(m, L, e, _):
    a, F, B, C = _ac(m) - 40, m['fut_cap'], m['barre_cap'], m['cap']
    x0, x1 = a, a + L; cx = (x0 + x1) / 2; ep = round(0.95 * F); haut = round(0.95 * F)
    w = larg_oblique(ep, cx - haut / 2 - x0, C)
    g = poly((x0, 0), (x0 + w, 0), (cx - haut / 2 + w, C), (cx - haut / 2, C))
    d = poly((x1 - w, 0), (x1, 0), (cx + haut / 2, C), (cx + haut / 2 - w, C))
    coque = poly((x0, 0), (cx - haut / 2, C), (cx + haut / 2, C), (x1, 0))
    yb = round(0.26 * C)
    barre = op_inter(rect(x0, yb, x1, yb + B), coque)
    return union(op_inter(union(g, d), coque), barre), round(x1 + a)


def _v_cap(m, x0, x1, haut, bas, ep):
    return _v_traits(m, x0, x1, haut, bas, ep)


@dessin('M')
def _M(m, L, e, _):
    a, F, C = _ac(m), m['fut_cap'], m['cap']
    x0, x1 = a, a + L; Fm = round(0.92 * F); ep = round(0.88 * F)
    v, w = _v_traits(m, x0, x1, C, round(0.95 * F), ep)
    return union(rect(x0, 0, x0 + Fm, C), rect(x1 - Fm, 0, x1, C), v), round(x1 + a)


@dessin('W')
def _W(m, L, e, _):
    a, F, C = _ac(m) - 45, m['fut_cap'], m['cap']
    ep = round(0.90 * F); bl = round(0.95 * F)
    lv = (L + 0) / 2
    g, w = _v_traits(m, a, a + lv + w_half(m, ep, lv, C), C, bl, ep)
    d, _ = _v_traits(m, a + lv - w_half(m, ep, lv, C), a + L, C, bl, ep)
    return union(g, d), round(a + L + a)


def w_half(m, ep, lv, C):
    return larg_oblique(ep, lv / 2, C) / 2


# ---------- la ponctuation de l'essai ----------

SIGNES = {}


def signe(*cars):
    def enr(fn):
        for c in cars:
            SIGNES[c] = fn
        return fn
    return enr


def _pt(m):
    return round(1.08 * m.f)


@signe('.')
def _point(m):
    t = _pt(m); a = m.a - 5
    return rect(a, 0, a + t, t), 2 * a + t


@signe(',')
def _virgule(m):
    """Le carré du point et sa queue en biais, d'un seul contour : pas de marche entre les deux."""
    t = _pt(m); a = m.a - 5
    return poly((a, t), (a + t, t), (a + t, 0), (a + 0.42 * t, -1.1 * t), (a - 0.06 * t, -1.1 * t), (a, 0)), 2 * a + t


@signe('!')
def _excl(m):
    t = _pt(m); a = m.a
    return union(rect(a, 0, a + t, t), rect(a + (t - m.f) / 2, t + 90, a + (t + m.f) / 2, m['cap'])), 2 * a + t


def _quest(m):
    t = _pt(m); a = m.ar; larg = round(2.2 * m.f + 170); C = m['cap']
    ry = round(0.25 * C); haut = C + m.D
    r = bol(a, a + larg, haut - 2 * ry, haut, m.f, m.f, m.h, m.e)
    cy = haut - ry; cx = a + larg / 2
    r = moins(r, rect(-GRAND, -GRAND, cx, round(cy - 0.2 * ry)))
    r = moins(r, rect(-GRAND, -GRAND, GRAND, cy - ry + m.h))
    pied_ = union(rect(cx - m.f / 2, t + 90, cx + m.f / 2, cy - ry + m.h + 1), rect(cx - m.f / 2, cy - ry + 1, a + larg - m.f / 2, cy - ry + m.h + 1))
    return union(r, pied_, rect(cx - t / 2, 0, cx + t / 2, t)), 2 * a + larg - 20


def _chevron(m, x, vers_gauche):
    """Un chevron : deux bras qui se croisent à la pointe, coupée à la verticale (plus lourde là)."""
    h = round(0.62 * m.X); y0 = round(0.12 * m.X); larg = round(0.42 * m.X); ep = round(0.72 * m.f)
    cy = y0 + h / 2; w = larg_oblique(ep, h / 2, larg)        # largeur verticale des bras
    haut = poly((x - 40, cy - w / 2 - 40 * h / 2 / larg), (x + larg, y0 + h - w), (x + larg, y0 + h), (x - 40, cy + w / 2 - 40 * h / 2 / larg))
    bas = transforme(haut, (1, 0, 0, -1, 0, 2 * cy))
    ch = coupe(union(haut, bas), x + round(0.30 * ep), -GRAND, GRAND, GRAND)
    if vers_gauche:
        return ch
    return transforme(ch, (-1, 0, 0, 1, 2 * x + larg + round(0.30 * ep), 0))


@signe('«')
def _guil_o(m):
    l1 = _chevron(m, m.a - 20, True); l2 = _chevron(m, m.a - 20 + round(0.26 * m.X + 0.9 * m.f), True)
    return union(l1, l2), bornes(union(l1, l2))[2] + m.a - 20


@signe('»')
def _guil_f(m):
    l1 = _chevron(m, m.a - 20, False); l2 = _chevron(m, m.a - 20 + round(0.26 * m.X + 0.9 * m.f), False)
    return union(l1, l2), bornes(union(l1, l2))[2] + m.a - 20


def tout(poids):
    """Toutes les formes de l'essai : nom de glyphe -> (contour, chasse, code ou None)."""
    out = {}
    for c in ESSAI_MIN + PLUS_MIN + CAPS_TOUTES:
        p, ch = lettre(c, poids); out[c] = (p, ch, ord(c))
    for c in CAPS_TOUTES:
        p, ch = lettre(c, poids, True); out[c + '.ovs'] = (p, ch, None)
    m = M(poids)
    for c, fn in SIGNES.items():
        p, ch = fn(m); out[c] = (p, ch, ord(c))
    return out



# ---------- les minuscules en plus ----------
PLUS_MIN = 'ıȷßæœøðþłđħ'


@minuscule('ı')
def _idotless(m):
    return rect(m.a, 0, m.a + m.f, m.X), 2 * m.a + m.f


@minuscule('ȷ')
def _jdotless(m):
    a, f = m.a, m.f; xs = a + 60
    cr, cy = _crochet_bas(m, xs + f, round(3.4 * f + 40), 'g')
    return union(rect(xs, cy - 1, xs + f, m.X), cr), xs + f + a


def _barre_oblique(m, cx, cy, larg, ep):
    """La barre en biais du ł et du ø."""
    h = 0.55 * larg; w = larg_oblique(ep, larg, h) if False else ep * 1.15
    return poly((cx - larg / 2, cy - h / 2 - w / 2), (cx + larg / 2, cy + h / 2 - w / 2),
                (cx + larg / 2, cy + h / 2 + w / 2), (cx - larg / 2, cy - h / 2 + w / 2))


@minuscule('ł')
def _lslash(m):
    a, f = m.a + 50, m.f
    barre = _barre_oblique(m, a + f / 2, round(0.55 * m.ASC), round(2.6 * f) + 40, m.h)
    return union(rect(a, 0, a + f, m.ASC), barre), 2 * a + f


@minuscule('đ')
def _dcroat(m):
    p, ch = MIN['d'](m)
    xs = ch - m.a - m.f; yb = min(round(m.X + 0.45 * (m.ASC - m.X)), m.ASC - round(1.8 * m.h))
    return union(p, rect(xs - round(1.0 * m.f), yb, xs + m.f + round(0.55 * m.f), yb + m.h)), ch + round(0.25 * m.f)


@minuscule('ħ')
def _hbar(m):
    p, ch = _h(m)
    yb = min(round(m.X + 0.45 * (m.ASC - m.X)), m.ASC - round(1.8 * m.h)); dx = round(0.45 * m.f)
    return decale(union(p, rect(m.a - dx, yb, m.a + m.f + round(1.0 * m.f), yb + m.h)), dx), ch + dx


@minuscule('ø')
def _oslash(m):
    p, ch = _o(m); x0, x1 = _o_boite(m)
    larg = (x1 - x0) * 1.08
    barre = op_inter(_barre_oblique(m, (x0 + x1) / 2, m.X / 2, larg, m.h),
                     superellipse((x0 + x1) / 2, m.X / 2, (x1 - x0) / 2, m.X / 2 + m.D, m.e))
    return union(p, barre), ch


@minuscule('þ')
def _thorn(m):
    p, ch = _panse(m, 'g')
    return union(p, rect(m.a, m.DESC, m.a + m.f, m.ASC)), ch


@minuscule('ð')
def _eth(m):
    """Comme Overshoot : le o, avec un trait qui part en biais au-dessus de son coin droit et une petite barre."""
    p, ch = _o(m); x0, x1 = _o_boite(m); w = x1 - x0
    ep = round(0.90 * m.f); haut = round(m.X + 0.70 * (m.ASC - m.X))
    xb, xh = x0 + 0.80 * w, x0 + 0.60 * w
    lw = larg_oblique(ep, xb - xh, haut - m.X)
    trait_ = coupe(trait(xb, m.X - m.h, xh, haut, lw), -GRAND, m.X - m.h, GRAND, haut)
    trait_ = moins(trait_, superellipse((x0 + x1) / 2, m.X / 2, (x1 - x0) / 2 - m.f, m.X / 2 + m.D - m.h, m.e))
    yb = round(m.X + 0.30 * (m.ASC - m.X))
    barre = rect(x0 + 0.52 * w, yb, x0 + 0.90 * w, yb + round(0.85 * m.h))
    return union(p, trait_, barre), ch


@minuscule('æ')
def _ae(m):
    pa, cha = _a_sans_pied(m)
    pa = moins(pa, rect(cha - m.f - 1, -GRAND, cha + 1, 20))
    pe, che = _e(m)
    x0e = bornes(pe)[0]; xd = cha                          # le fût du a devient le côté gauche du e
    dx = xd - m.f - x0e
    return union(pa, decale(pe, dx)), round(dx + che)


@minuscule('œ')
def _oe(m):
    po, cho = _o(m); x0, x1 = _o_boite(m)
    pe, che = _e(m)
    dx = x1 - m.f - bornes(pe)[0]
    return union(po, decale(pe, dx)), round(dx + che)


@minuscule('ß')
def _germandbls(m):
    a, f = m.a, m.f; w = round(2 * f + 0.78 * m.cn)
    x1 = a + w; haut = m.ASC + m.D
    ym = round(0.47 * m.ASC); coupe_x = a + f + round(0.45 * m.cn * 0.5)
    ryu = (haut - ym) / 2; cyu = ym + ryu
    haut_ = bol(a, x1 - round(0.10 * w), ym, haut, f, f, m.h, m.e)
    haut_ = moins(haut_, rect(-GRAND, -GRAND, coupe_x, cyu))
    bas = bol(a, x1, -m.D, ym + m.h, f, f, m.h, m.e)
    bas = moins(bas, rect(-GRAND, -GRAND, coupe_x, GRAND))
    return union(rect(a, 0, a + f, cyu), haut_, bas), x1 + m.ar



# ---------- les autres capitales ----------

def _barre_mi(m):
    C, B = m['cap'], m['barre_cap']
    return round(0.49 * C - B / 2)


@dessin('B')
def _B(m, L, e, _):
    a, F, B, C = _ac(m), m['fut_cap'], m['barre_cap'], m['cap']
    ym = round(0.52 * C - B / 2)
    haut = demi_bol(a, a + round(0.90 * L), ym, C, F, round(0.98 * F), B, e)
    bas = demi_bol(a, a + L, 0, ym + B, F, round(1.02 * F), B, e)
    return union(rect(a, 0, a + F, C), haut, bas), round(a + L + a - 20)


@dessin('D')
def _D(m, L, e, _):
    a, F, B, C = _ac(m), m['fut_cap'], m['barre_cap'], m['cap']
    return union(rect(a, 0, a + F, C), demi_bol(a, a + L, 0, C, F, round(1.04 * F), B, e)), round(a + L + a - 14)


@dessin('P')
def _P(m, L, e, _):
    a, F, B, C = _ac(m), m['fut_cap'], m['barre_cap'], m['cap']
    yb = round(0.40 * C)
    return union(rect(a, 0, a + F, C), demi_bol(a, a + L, yb, C, F, round(1.02 * F), B, e)), round(a + L + a - 20)


@dessin('F')
def _F(m, L, e, _):
    a, F, B, C = _ac(m), m['fut_cap'], m['barre_cap'], m['cap']
    yb = _barre_mi(m) - round(0.02 * C)
    return union(rect(a, 0, a + F, C), rect(a, C - B, a + L, C), rect(a, yb, a + L - 0.10 * L, yb + B)), round(a + L + a - 30)


@dessin('J')
def _J(m, L, e, _):
    a, F, B, C, D = _ac(m) - 30, m['fut_cap'], m['barre_cap'], m['cap'], m['depasse']
    x0, x1 = a, a + L; ry = round(0.30 * C)
    r = bol(x0, x1, -D, -D + 2 * ry, F, F, B, e)
    cy = -D + ry
    r = coupe(r, -GRAND, -GRAND, GRAND, cy)
    r = moins(r, rect(-GRAND, round(-D + 0.70 * ry), (x0 + x1) / 2, GRAND))     # le bout coupé à plat
    return union(r, rect(x1 - F, cy - 1, x1, C)), round(x1 + _ac(m))


@dessin('U')
def _U(m, L, e, _):
    a, F, B, C, D = _ac(m), m['fut_cap'], m['barre_cap'], m['cap'], m['depasse']
    x0, x1 = a, a + L; ry = round(0.36 * C)
    r = bol(x0, x1, -D, -D + 2 * ry, F, F, B, e)
    cy = -D + ry
    r = coupe(r, -GRAND, -GRAND, GRAND, cy)
    return union(r, rect(x0, cy - 1, x0 + F, C), rect(x1 - F, cy - 1, x1, C)), round(x1 + a)


@dessin('N')
def _N(m, L, e, _):
    a, F, C = _ac(m), m['fut_cap'], m['cap']
    x0, x1 = a, a + L; Fn = round(0.92 * F); ep = round(0.95 * F)
    wd = larg_oblique(ep, L - Fn, C)
    diag = poly((x0, C), (x0 + wd, C), (x1, 0), (x1 - wd, 0))
    return union(rect(x0, 0, x0 + Fn, C), rect(x1 - Fn, 0, x1, C), diag), round(x1 + a)


@dessin('V')
def _V(m, L, e, _):
    a, F, C = _ac(m) - 40, m['fut_cap'], m['cap']
    p, _w = _v_traits(m, a, a + L, C, round(0.95 * F), round(0.95 * F))
    return p, round(a + L + a)


@dessin('X')
def _X(m, L, e, _):
    a, F, C = _ac(m) - 35, m['fut_cap'], m['cap']; x0, x1 = a, a + L
    w = larg_oblique(round(0.95 * F), x1 - x0, C)
    return union(poly((x0, C), (x0 + w, C), (x1, 0), (x1 - w, 0)),
                 poly((x1 - w, C), (x1, C), (x0 + w, 0), (x0, 0))), round(x1 + a)


@dessin('Y')
def _Y(m, L, e, _):
    a, F, C = _ac(m) - 40, m['fut_cap'], m['cap']; x0, x1 = a, a + L
    cx = (x0 + x1) / 2; yj = round(0.42 * C); ep = round(0.95 * F)
    w = larg_oblique(ep, cx - x0, C - yj)
    # les deux bras se posent pile sur le fût : rien ne dépasse à la jonction
    g = trait(x0 + w / 2, C, cx - F / 2 + w / 2, yj, w)
    d = trait(x1 - w / 2, C, cx + F / 2 - w / 2, yj, w)
    g = moins(g, cote_de((x1, C), (cx + F / 2, yj), gauche=False))
    d = moins(d, cote_de((x0, C), (cx - F / 2, yj), gauche=True))
    return union(g, d, rect(cx - F / 2, 0, cx + F / 2, yj + 1)), round(x1 + a)


@dessin('Z')
def _Z(m, L, e, _):
    a, F, B, C = _ac(m) - 25, m['fut_cap'], m['barre_cap'], m['cap']; x0, x1 = a, a + L
    w = larg_oblique(round(0.86 * F), x1 - x0, C - 2 * B)
    return union(rect(x0 + 10, C - B, x1, C), rect(x0, 0, x1 + 6, B),
                 poly((x1 - w, C - B), (x1, C - B), (x0 + w, B), (x0, B))), round(x1 + a)


@dessin('Ø')
def _Oslash(m, L, e, _):
    p, x0, x1 = _O_forme(m, L, e); C, B, D = m['cap'], m['barre_cap'], m['depasse']
    cx = (x0 + x1) / 2; ep = round(0.85 * B)
    w = larg_oblique(ep, (x1 - x0) * 0.9, C + 2 * D + 40)
    barre = trait(cx - 0.45 * (x1 - x0), -D - 20, cx + 0.45 * (x1 - x0), C + D + 20, w)
    return union(p, barre), round(x1 + x0)


@dessin('Œ')
def _OE(m, L, e, _):
    a, F, B, C, D = _ac(m) - 14, m['fut_cap'], m['barre_cap'], m['cap'], m['depasse']
    lo = round(0.66 * L)
    o = bol(a, a + lo, -D, C + D, round(1.04 * F), round(1.04 * F), B, e, e_ref=m.e)
    # le fût du E commence là où le bord du O redescend à la hauteur des capitales : pas de marche
    haut = coupe(o, a + lo / 2, C, GRAND, GRAND)
    xs = round(bornes(haut)[2]) if list(haut.contours) else a + lo - F
    xs = min(xs, a + lo - F)
    o = moins(o, rect(xs + F / 2, -GRAND, GRAND, GRAND))
    yb = _barre_mi(m)
    E = union(rect(xs, 0, xs + F, C), rect(xs, 0, a + L, B), rect(xs, C - B, a + L - 8, C),
              rect(xs, yb, a + L - 0.10 * (L - lo), yb + B))
    return union(o, E), round(a + L + _ac(m) - 20)


@dessin('Æ')
def _AE(m, L, e, _):
    a, F, B, C = _ac(m) - 40, m['fut_cap'], m['barre_cap'], m['cap']
    xs = a + round(0.48 * L); ep = round(0.95 * F)
    w = larg_oblique(ep, xs - a, C)
    diag = poly((a, 0), (a + w, 0), (xs + F, C), (xs + F - w, C))
    diag = coupe(diag, -GRAND, -GRAND, xs + F / 2, GRAND)
    yb = round(0.26 * C); yb2 = _barre_mi(m)
    barreA = op_inter(rect(a, yb, xs + 1, yb + B), poly((a, 0), (xs + F, C), (xs + F, 0)))
    E = union(rect(xs, 0, xs + F, C), rect(xs, 0, a + L, B), rect(xs - 10, C - B, a + L - 8, C),
              rect(xs, yb2, a + L - 0.10 * (L - xs + a), yb2 + B))
    return union(diag, barreA, E), round(a + L + _ac(m) - 20)


@dessin('Þ')
def _Thorn(m, L, e, _):
    a, F, B, C = _ac(m), m['fut_cap'], m['cap'] and m['barre_cap'], m['cap']
    y0, y1 = round(0.17 * C), round(0.80 * C)
    return union(rect(a, 0, a + F, C), demi_bol(a, a + L, y0, y1, F, round(1.02 * F), B, e)), round(a + L + a - 20)


def _barre_fut(m, x, y, avant, apres):
    return rect(x - avant, y, x + m['fut_cap'] + apres, y + round(0.85 * m['barre_cap']))


@dessin('Ð')
def _Eth(m, L, e, _):
    p, ch = _D(m, L, e, _); dx = round(0.35 * m['fut_cap'])
    a = _ac(m); yb = round(0.48 * m['cap'] - 0.42 * m['barre_cap'])
    return decale(union(p, _barre_fut(m, a, yb, dx, round(0.75 * m['fut_cap']))), dx), ch + dx


DESSINS['Đ'] = DESSINS['Ð']; CAPS['Đ'] = _cap('Đ')


@dessin('Ł')
def _Lslash(m, L, e, _):
    p, ch = _L(m, L, e, _); dx = round(0.30 * m['fut_cap']); a = _ac(m); F = m['fut_cap']
    ep = round(0.85 * m['barre_cap']); C = m['cap']
    b = trait(a + F / 2 - 0.9 * F, round(0.40 * C), a + F / 2 + 0.9 * F, round(0.40 * C) + round(1.1 * F), round(1.5 * ep))
    return decale(union(p, b), dx), ch + dx


@dessin('Ħ')
def _Hbar(m, L, e, _):
    p, ch = _H(m, L, e, _); a = _ac(m); F = m['fut_cap']; dx = round(0.30 * F)
    yb = round(0.76 * m['cap'])
    b = rect(a - dx, yb, a + L + dx, yb + round(0.85 * m['barre_cap']))
    return decale(union(p, b), dx), ch + 2 * dx


@dessin('ẞ')
def _Germandbls(m, L, e, _):
    a, F, B, C, D = _ac(m), m['fut_cap'], m['barre_cap'], m['cap'], m['depasse']
    L = L + 2.2 * (F - 117)                                    # en gras, il faut de la place pour le bas
    x1 = a + L; xt = a + round(0.78 * L); ym = round(0.50 * C)
    eg = round(0.85 * F)
    x0b = a + F + round(0.05 * L); cxl = x0b + eg + 4        # le bas s'ouvre à gauche, loin du fût
    bas = bol(x0b, x1, -D, ym + B, eg, F, B, e, e_ref=m.e)
    bas = moins(bas, rect(-GRAND, round(0.24 * C), cxl, GRAND))       # le bout du bas coupé à plat
    bas = union(bas, rect(cxl, ym, (x0b + x1) / 2, ym + B))           # le trait du haut part à plat du biais
    ep = round(0.92 * F); w = larg_oblique(ep, xt - cxl, C - ym)
    diag = coupe(trait(xt - w / 2, C, cxl + w / 2, ym, w), -GRAND, ym, GRAND, C)
    return union(rect(a, 0, a + F, C), rect(a, C - B, xt, C), diag, bas), round(x1 + a - 10)
