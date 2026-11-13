import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from mesures import mesures, police, GRAISSES
from pieces import glyphe, bornes, egaux, union
from cyrillique import LETTRES, lettre

CAPS = [chr(c) for c in range(0x0410, 0x0430)] + ['Ё']
LATIN = {'А': 'A', 'В': 'B', 'Е': 'E', 'К': 'K', 'М': 'M', 'Н': 'H', 'О': 'O', 'Р': 'P', 'С': 'C', 'Т': 'T', 'Х': 'X', 'Ё': 'uni00CB', 'З': 'three'}


def test_les_33():
    assert len(CAPS) == 33
    for c in CAPS:
        assert c in LETTRES, c


def test_comme_le_latin():
    for g in GRAISSES:
        f = police(g)
        for c, n in LATIN.items():
            p, w = lettre(c, g)
            assert egaux(p, glyphe(f, n)) and w == f['hmtx'][n][0], (g, c)


def test_hauteurs_et_jambages():
    for g in GRAISSES:
        dj = mesures(g)['jambage']
        for c in CAPS:
            x0, y0, x1, y1 = bornes(lettre(c, g)[0])
            if c in 'ДЦЩ':
                assert y0 == -dj, (g, c)
            else:
                assert y0 >= -7, (g, c, y0)
            if c in 'ЁЙ':
                assert y1 > 760, (g, c)
            else:
                assert y1 <= 737, (g, c, y1)


def test_pas_de_recouvrement_ni_de_debord():
    for g in GRAISSES:
        for c in CAPS:
            p, w = lettre(c, g)
            assert egaux(p, union(p)), (g, c)          # contour déjà propre
            x0, y0, x1, y1 = bornes(p)
            assert x0 >= 0 and x1 <= w, (g, c, x0, x1, w)


def test_jambages_coupes_a_l_horizontale():
    from pieces import courses
    for g in ('Calm', 'Storm'):
        dj = mesures(g)['jambage']; S = mesures(g)['fut_cap']
        for c in 'ДЦЩ':
            runs = courses(lettre(c, g)[0], -dj + 1)
            assert runs and all(abs((b - a) - S) <= 2 for a, b in runs), (g, c, runs)
