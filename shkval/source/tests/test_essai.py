import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from mesures import mesures, police, GRAISSES
from pieces import glyphe, bornes, courses, miroir, egaux
from cyrillique import LETTRES, lettre

ESSAI = ['Ш', 'К', 'В', 'А', 'Л', 'Б', 'Г', 'Д', 'Ж', 'Ю', 'Я', 'ш', 'к', 'в', 'а', 'л']


def test_lettres_presentes():
    for c in ESSAI:
        assert c in LETTRES, c


def test_fus_du_sha():
    for g in ('Calm', 'FreshBreeze', 'Storm'):
        m = mesures(g); p, w = lettre('Ш', g)
        runs = courses(p, 500)
        assert len(runs) == 3
        for x0, x1 in runs:
            assert abs((x1 - x0) - m['fut_cap']) <= 2
        assert w == m['chasse_M']
        rm = courses(lettre('ш', g)[0], 400)
        assert len(rm) == 3 and all(abs((b - a) - m['fut_min']) <= 2 for a, b in rm)


def test_hauteurs():
    for g in ('Calm', 'Storm'):
        for c in 'ШКВАЛБГЖЮЯ':
            x0, y0, x1, y1 = bornes(lettre(c, g)[0])
            assert abs(y1 - 730) <= 7 and y0 >= -7, (g, c)
        for c in 'шквал':
            x0, y0, x1, y1 = bornes(lettre(c, g)[0])
            assert abs(y1 - 599) <= 7 and y0 >= -7, (g, c)
        x0, y0, x1, y1 = bornes(lettre('Д', g)[0])
        assert y0 == -mesures(g)['jambage']


def test_comme_le_latin():
    for g in ('Calm', 'Storm'):
        f = police(g)
        for c, n in (('А', 'A'), ('В', 'B'), ('К', 'K'), ('а', 'a')):
            p, w = lettre(c, g)
            assert egaux(p, glyphe(f, n)) and w == f['hmtx'][n][0], (g, c)
        p, w = lettre('Я', g)
        from pieces import decale
        assert egaux(p, decale(miroir(glyphe(f, 'R'), f['hmtx']['R'][0]), 20)) and w == f['hmtx']['R'][0] + 20
