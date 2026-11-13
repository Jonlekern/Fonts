import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from mesures import mesures, police, GRAISSES
from pieces import glyphe, bornes, egaux, union, courses
from cyrillique import LETTRES, lettre

MINS = [chr(c) for c in range(0x0430, 0x0450)] + ['ё']
LATIN = {'а': 'a', 'е': 'e', 'о': 'o', 'р': 'p', 'с': 'c', 'у': 'y', 'х': 'x', 'ё': 'uni00EB'}


def test_les_33():
    assert len(MINS) == 33
    for c in MINS:
        assert c in LETTRES, c


def test_comme_le_latin():
    for g in GRAISSES:
        f = police(g)
        for c, n in LATIN.items():
            p, w = lettre(c, g)
            assert egaux(p, glyphe(f, n)) and w == f['hmtx'][n][0], (g, c)


def test_hauteurs():
    for g in GRAISSES:
        dj = mesures(g)['jambage']
        for c in MINS:
            x0, y0, x1, y1 = bornes(lettre(c, g)[0])
            if c in 'дцщ':
                assert y0 == -dj, (g, c, y0)
            elif c in 'руф':
                assert y0 == -219, (g, c)
            else:
                assert y0 >= -7, (g, c, y0)
            if c in 'бф':
                assert y1 == 748, (g, c, y1)
            elif c in 'йё':
                assert 650 < y1 < 900, (g, c, y1)
            else:
                assert y1 <= 606, (g, c, y1)


def test_futs_des_minuscules():
    for g in ('Calm', 'FreshBreeze', 'Storm'):
        s = mesures(g)['fut_min']
        for c in 'нпшщцгт':
            runs = courses(lettre(c, g)[0], 200)
            assert runs and all(abs((b - a) - s) <= 2 for a, b in runs), (g, c, runs)


def test_propre():
    for g in GRAISSES:
        for c in MINS:
            p, w = lettre(c, g)
            assert egaux(p, union(p)), (g, c)
            x0, y0, x1, y1 = bornes(p)
            assert x0 >= 0 and x1 <= w, (g, c, x0, x1, w)
