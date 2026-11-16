import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import pytest
from mesures import GRAISSES
from pieces import bornes, union, egaux
from chiffres import chiffre, CHIFFRES
from outils_test import sans_recouvrement

RONDS_HAUT = '023689'      # dépassent en haut
RONDS_BAS = '035689'       # dépassent en bas
CONTOURS = {'0': 2, '1': 1, '2': 1, '3': 1, '4': 2, '5': 1, '6': 2, '7': 1, '8': 3, '9': 2}


@pytest.mark.parametrize('c,p,t', [(c, p, t) for p in GRAISSES for c in CHIFFRES for t in (False, True)])
def test_hauteurs(c, p, t):
    _, y0, _, y1 = bornes(chiffre(c, p, t)[0])
    assert y1 == (712 if c in RONDS_HAUT else 700), (c, y1)
    assert y0 == (-12 if c in RONDS_BAS else 0), (c, y0)


@pytest.mark.parametrize('c,p', [(c, p) for p in GRAISSES for c in CHIFFRES])
def test_propres(c, p):
    f = chiffre(c, p)[0]
    assert egaux(f, union(f)) and sans_recouvrement(f)
    assert len(list(f.contours)) == CONTOURS[c], (c, len(list(f.contours)))


@pytest.mark.parametrize('p', GRAISSES)
def test_tabulaires(p):
    ch = {chiffre(c, p, True)[1] for c in CHIFFRES}
    assert len(ch) == 1
    w = ch.pop()
    for c in CHIFFRES:
        x0, _, x1, _ = bornes(chiffre(c, p, True)[0])
        assert x0 >= 0 and x1 <= w and abs((x0 + x1) / 2 - w / 2) <= 1, c
