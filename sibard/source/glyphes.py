# Tous les glyphes de Sibard : nom -> (fonction de dessin, code Unicode ou None).
import math
from functools import lru_cache
from fontTools.agl import UV2AGL
from tuyaux import penche
from mesures import mesures, PENTE, CAP
from dessin import D, lettre, decale
from minuscules import MINUSCULES
from capitales import CAPITALES
from chiffres import CHIFFRES
from signes import SIGNES
from accents import ACCENTUEES, ESPACANTS, NOMS as MARQUES, accent, espacant, DESSOUS
from formes import chemin

ESSAI_MIN = 'abcdefghijklmnopqrstuvwxyz'
PLUS_MIN = 'ıȷßæœøðþłđħ'
CAPS_TOUTES = 'ABCDEFGHIJKLMNOPQRSTUVWXYZÆŒØÐÞŁĐĦẞ'
CAPS_ACC = [c for c in ACCENTUEES if c.isupper()]
NOMS_CHIFFRES = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
COMBINANTS = dict(MARQUES)


def nom(c):
    """Le nom de glyphe d'un caractère (noms AGL, sinon uniXXXX)."""
    if len(c) == 1:
        return UV2AGL.get(ord(c), 'uni%04X' % ord(c))
    return c


def _combinant(n):
    def f(d):
        return accent(n, d, -130, d.x + 56 if n not in DESSOUS else 0), 0
    return f


CARONS = {'dcaron': 'd', 'lcaron': 'l', 'tcaron': 't', 'Lcaron': 'L'}       # ď ľ ť Ľ : la lettre + le caron vertical


def _caron_vertical(d):
    from signes import P, eg
    return [P([(44, 0), (0, -190)], d, eg(d) * 0.8, k=[1, 0], debut='h')], 0


def place_caron(n, poids, vitesse=0.0):
    """Où poser le caron vertical d'un ď ľ ť Ľ (dans la variable, c'est une pièce à part)."""
    base = CARONS[n]
    m = mesures(poids, vitesse=vitesse); d = D(m)
    tuy, ch = table()[base][0](d)
    xs = [p[0] for t in tuy if not getattr(t, 'hors', False) for p in t.pts]
    h = d.cap if base == 'L' else d.asc
    x = max(xs) + (d.Fd / 2 if base != 'L' else -60) + 34 + m['air']
    return x + math.tan(math.radians(PENTE)) * vitesse * (h - CAP / 2), h, ch + (60 if base in 'dt' else 0) + m['air']


@lru_cache(None)
def table():
    t = {}
    for c, f in {**MINUSCULES, **CAPITALES, **CHIFFRES, **SIGNES, **ACCENTUEES}.items():
        t[nom(c)] = (f, ord(c))
    t['uni00A0'] = (SIGNES[' '], 0xA0)
    for c, n in ESPACANTS.items():
        t[nom(c)] = ((lambda d, n=n: espacant(n, d)), ord(c))
    for c, n in COMBINANTS.items():
        t[nom(c)] = (_combinant(n), ord(c))
    t['caron.alt'] = (_caron_vertical, None)
    return t


def dessine(n, poids, vitesse=0.0, signatures=True):
    """Les contours d'un glyphe et sa chasse, à une graisse et une vitesse (0 à 1)."""
    m = mesures(poids, vitesse=vitesse)
    tuy, ch = table()[n][0](D(m))
    lettre(tuy, m)
    if not signatures:
        tuy = [t for t in tuy if not getattr(t, 'hors', False)]
    cs = [c for t in tuy for c in t.contours(m)]
    if m['air']:
        cs = [[(s[0],) + tuple((p[0] + m['air'], p[1]) for p in s[1:]) for s in c] for c in cs]
    y0 = CAP / 2 if n != 'caron.alt' else 0          # la pièce du caron penche autour de son point d'attache
    if m['air'] and n == 'caron.alt':
        cs = [[(s[0],) + tuple((p[0] - m['air'], p[1]) for p in s[1:]) for s in c] for c in cs]
    cs = penche(cs, math.tan(math.radians(PENTE)) * vitesse, y0)
    return cs, ch + (m['air'] if ch else 0)


@lru_cache(None)
def tous(poids, vitesse=0.0):
    """nom -> (tracé fusionné, chasse, code)."""
    out = {}
    for n, (_, code) in table().items():
        cs, ch = dessine(n, poids, vitesse)
        out[n] = (chemin(cs), ch, code)
    return out


@lru_cache(None)
def corps(poids):
    """Comme tous(), sans les signatures : le crénage se règle sur le corps des lettres."""
    out = {}
    for n, (_, code) in table().items():
        cs, ch = dessine(n, poids, 0.0, signatures=False)
        out[n] = (chemin(cs), ch, code)
    return out
