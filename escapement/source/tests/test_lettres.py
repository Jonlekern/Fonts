import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import pytest
from mesures import mesures, GRAISSES
from pieces import bornes, courses, union, egaux
from lettres import lettre, ESSAI_MIN, PLUS_MIN
from outils_test import sans_recouvrement

TOUTES = [(c, p) for p in GRAISSES for c in ESSAI_MIN + PLUS_MIN]
CONTOURS = {**{c: 1 for c in 'lnhmurfktvwxyzcs'}, **{c: 2 for c in 'ijobdpqeg'}, 'a': 2, **{c: 1 for c in 'ıȷßłħ'}, **{c: 2 for c in 'ðþđ'}, **{c: 3 for c in 'æœø'}}


@pytest.mark.parametrize('c,p', TOUTES)
def test_existe(c, p):
    forme, ch = lettre(c, p)
    assert ch > 0 and len(list(forme.contours)) > 0


@pytest.mark.parametrize('p', GRAISSES)
def test_depassement(p):
    X, D = 504, 12
    for c in 'oces':
        _, y0, _, y1 = bornes(lettre(c, p)[0])
        assert abs(y0 + D) <= 1 and abs(y1 - X - D) <= 1, (c, y0, y1)
    for c in 'nmr':
        assert abs(bornes(lettre(c, p)[0])[3] - X - D) <= 1, c
    assert abs(bornes(lettre('u', p)[0])[1] + D) <= 1
    for c in 'xzvw':
        _, y0, _, y1 = bornes(lettre(c, p)[0])
        assert (y0, y1) == (0, X), (c, y0, y1)


@pytest.mark.parametrize('p', GRAISSES)
def test_fut(p):
    f = mesures(p)['fut_min']
    for c in 'nhli':
        g0, g1 = courses(lettre(c, p)[0], 150)[0]
        assert abs((g1 - g0) - f) <= 1, (c, g1 - g0, f)


@pytest.mark.parametrize('p', GRAISSES)
def test_pied_a(p):
    forme, _ = lettre('a', p)
    morceaux = courses(forme, 0)
    pd = mesures(p)['pied']
    # au ras de la ligne, la jambe du a dépasse son fût de la longueur du pied
    f = mesures(p)['fut_min']
    g0, g1 = morceaux[-1]
    assert abs((g1 - g0) - (f + pd)) <= 3, (g1 - g0, f + pd)


@pytest.mark.parametrize('c,p', TOUTES)
def test_contours_propres(c, p):
    forme, _ = lettre(c, p)
    assert egaux(forme, union(forme)) and sans_recouvrement(forme)
    assert len(list(forme.contours)) == CONTOURS[c], (c, len(list(forme.contours)))


def test_chasse_n():
    assert lettre('n', 400)[1] == mesures(400)['chasse_n']


def test_detecte_recouvrement():
    from pieces import rect
    from pathops import Path
    p = Path(); rect(0, 0, 100, 100).draw(p.getPen()); rect(50, 50, 150, 150).draw(p.getPen())
    assert not sans_recouvrement(p)


@pytest.mark.parametrize('p', GRAISSES)
def test_descendantes_et_montantes(p):
    m = mesures(p)
    for c in 'gjyȷ':
        assert bornes(lettre(c, p)[0])[1] <= m['desc'], c          # les crochets passent la ligne du bas
    assert bornes(lettre('f', p)[0])[3] == m['asc'] + m['depasse']   # le haut rond du f dépasse
    for c in 'ij':
        assert bornes(lettre(c, p)[0])[3] <= m['asc'], c            # le point ne monte pas plus haut que les montantes
