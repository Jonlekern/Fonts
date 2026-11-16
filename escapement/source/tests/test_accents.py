import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import pytest
from mesures import GRAISSES
from pieces import bornes, union, egaux, coupe
from lettres import lettre, CAPS
from accents import accentuee, marque, ACCENTUEES, ESPACANTS, COMBINANTS, _base, DESSOUS
from outils_test import sans_recouvrement

CAPS_ACC = [c for c in ACCENTUEES if c.isupper()]
TOUTES = [(c, p, o) for p in (300, 400, 700) for c in ACCENTUEES for o in (False, True) if not o or c in CAPS_ACC]


def test_145():
    assert len(ACCENTUEES) == 145


@pytest.mark.parametrize('c,p,o', TOUTES)
def test_propre(c, p, o):
    f, ch = accentuee(c, p, o)
    assert egaux(f, union(f)) and sans_recouvrement(f)
    assert bornes(f)[3] <= 960 and bornes(f)[1] >= -300, (c, bornes(f))


@pytest.mark.parametrize('c,p,o', TOUTES)
def test_accent_ne_touche_pas(c, p, o):
    """Un accent au-dessus garde au moins 40 unités de blanc avec la lettre."""
    base, marks = _base(c)
    if all(n in DESSOUS for n in marks) or marks == ['apostrophe']:
        return
    bp, _ = lettre(base, p, o) if base in CAPS else lettre(base, p)
    haut_base = bornes(bp)[3]
    f, _ = accentuee(c, p, o)
    dessus = coupe(f, -5000, haut_base + 1, 5000, 5000)
    assert bornes(dessus)[1] - haut_base >= 40, (c, bornes(dessus)[1], haut_base)


@pytest.mark.parametrize('c,p', [(c, p) for p in GRAISSES for c in list(ESPACANTS) + list(COMBINANTS)])
def test_marques(c, p):
    f, ch = marque(c, p)
    assert len(list(f.contours)) > 0 and sans_recouvrement(f)
    assert (ch == 0) == (c in COMBINANTS)
