import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import pytest
from mesures import mesures, GRAISSES
from pieces import bornes, courses, union, egaux
from lettres import lettre, CAPS_TOUTES as ESSAI_CAP
from outils_test import sans_recouvrement, trait_max

TOUTES = [(c, p, o) for p in GRAISSES for c in ESSAI_CAP for o in (False, True)]
RONDES = 'OCGQSŒ'
RONDES_BAS = 'UJẞ'
CONTOURS = {**{c: 1 for c in 'CEGHIKLMSTWFJNUVXYZŁẞ'}, **{c: 2 for c in 'AORDPÆŒÐÞĐĦ'}, 'Q': 1, 'B': 3, 'Ø': 3}


@pytest.mark.parametrize('c,p,o', TOUTES)
def test_hauteur_cap(c, p, o):
    _, y0, _, y1 = bornes(lettre(c, p, o)[0])
    if c in RONDES:
        assert abs(y1 - 712) <= 1 and abs(y0 + 12) <= 1, (y0, y1)
    elif c in RONDES_BAS:
        assert y1 == 700 and abs(y0 + 12) <= 1, (y0, y1)
    elif c == 'Ø':
        assert y0 <= -12 and y1 >= 712
    else:
        assert (y0, y1) == (0, 700), (y0, y1)


@pytest.mark.parametrize('p', GRAISSES)
def test_ovs_meme_trait(p):
    for c in 'HIKLMRTE':
        n = courses(lettre(c, p)[0], 172)
        v = courses(lettre(c, p, True)[0], 172)
        fn = [b - a for a, b in n]; fv = [b - a for a, b in v]
        # le fût de gauche (ou le seul) garde exactement la même épaisseur
        assert abs(fn[0] - fv[0]) <= 1, (c, fn, fv)


@pytest.mark.parametrize('c,p', [(c, p) for p in GRAISSES for c in ESSAI_CAP])
def test_ovs_plus_large(c, p):
    r = lettre(c, p, True)[1] / lettre(c, p)[1]
    assert 1.20 <= r <= 1.25, r


@pytest.mark.parametrize('p', GRAISSES)
def test_m_w_au_sol(p):
    for c in 'MW':
        for o in (False, True):
            forme = lettre(c, p, o)[0]
            assert len(courses(forme, 2)) == (3 if c == 'M' else 2), (c, courses(forme, 2))
            assert bornes(forme)[3] == 700


@pytest.mark.parametrize('c,p,o', TOUTES)
def test_contours_propres(c, p, o):
    forme = lettre(c, p, o)[0]
    assert egaux(forme, union(forme)) and sans_recouvrement(forme)
    assert len(list(forme.contours)) == CONTOURS[c], (c, len(list(forme.contours)))


# le G n'y est pas : son trait le plus épais est le coin carré de l'éperon, pas la ronde
@pytest.mark.parametrize('c,p', [(c, p) for p in (300, 400, 700) for c in 'OCQS'])
def test_ovs_coins_pas_plus_gras(c, p):
    n, v = trait_max(lettre(c, p)[0]), trait_max(lettre(c, p, True)[0])
    assert abs(n - v) <= 3, (c, n, v)      # 3 unités : moins de 2 % du trait


@pytest.mark.parametrize('c,p', [(c, p) for p in GRAISSES for c in ESSAI_CAP])
def test_encre_ovs_plus_large(c, p):
    """Une union ratée perd un morceau de lettre : la version de début de phrase doit avoir plus d'encre en largeur."""
    if c == 'I':
        return
    n = bornes(lettre(c, p)[0]); v = bornes(lettre(c, p, True)[0])
    assert v[2] - v[0] > n[2] - n[0], (c, n, v)
