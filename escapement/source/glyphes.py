# Tous les glyphes d'Escapement pour une graisse : nom -> (contour, chasse, code ou None).
import unicodedata
from functools import lru_cache
from fontTools.agl import UV2AGL
from lettres import lettre, ESSAI_MIN, PLUS_MIN, CAPS_TOUTES
from chiffres import chiffre, CHIFFRES
from signes import signe, SIGNES
from accents import accentuee, marque, ACCENTUEES, ESPACANTS, COMBINANTS

NOMS_CHIFFRES = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
CAPS_ACC = [c for c in ACCENTUEES if c.isupper()]
TOUTES_CAPS = list(CAPS_TOUTES) + CAPS_ACC           # celles qui ont une version de début de phrase


def nom(c):
    """Le nom de glyphe d'un caractère (noms AGL, sinon uniXXXX)."""
    if c.endswith('.ovs') or c.endswith('.tf'):
        base, suf = c.rsplit('.', 1)
        return nom(base) + '.' + suf
    if len(c) == 1:
        return UV2AGL.get(ord(c), 'uni%04X' % ord(c))
    return c


@lru_cache(None)
def tous(poids):
    out = {}
    for c in ESSAI_MIN + PLUS_MIN + CAPS_TOUTES:
        p, ch = lettre(c, poids); out[nom(c)] = (p, ch, ord(c))
    for c in CAPS_TOUTES:
        p, ch = lettre(c, poids, True); out[nom(c) + '.ovs'] = (p, ch, None)
    for c, n in zip(CHIFFRES, NOMS_CHIFFRES):
        p, ch = chiffre(c, poids); out[n] = (p, ch, ord(c))
        p, ch = chiffre(c, poids, True); out[n + '.tf'] = (p, ch, None)
    for c in SIGNES:
        p, ch = signe(c, poids); out[nom(c)] = (p, ch, ord(c))
    for c in ACCENTUEES:
        p, ch = accentuee(c, poids); out[nom(c)] = (p, ch, ord(c))
    for c in CAPS_ACC:
        p, ch = accentuee(c, poids, True); out[nom(c) + '.ovs'] = (p, ch, None)
    for c in list(ESPACANTS) + list(COMBINANTS):
        p, ch = marque(c, poids); out[nom(c)] = (p, ch, ord(c))
    return out


def base_de(c):
    """La lettre de base d'un caractère accentué (pour le crénage par familles)."""
    d = unicodedata.normalize('NFD', c)
    return d[0] if d else c
