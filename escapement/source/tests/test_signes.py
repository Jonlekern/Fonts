import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import pytest
from mesures import GRAISSES
from pieces import bornes, union, egaux
from signes import signe, SIGNES
from outils_test import sans_recouvrement

TOUS = [(c, p) for p in GRAISSES for c in SIGNES if c not in '  ']


@pytest.mark.parametrize('c,p', TOUS)
def test_propre(c, p):
    f, ch = signe(c, p)
    assert ch > 0 and len(list(f.contours)) > 0
    assert egaux(f, union(f)) and sans_recouvrement(f)


@pytest.mark.parametrize('c,p', TOUS)
def test_dans_la_chasse(c, p):
    """L'encre ne déborde pas trop de sa case (sauf les tirets longs, qui la remplissent)."""
    f, ch = signe(c, p)
    x0, _, x1, _ = bornes(f)
    assert x0 >= -5 and x1 <= ch + 5, (c, x0, x1, ch)


def test_espaces():
    for p in GRAISSES:
        assert signe(' ', p)[1] == signe(' ', p)[1] == 250
