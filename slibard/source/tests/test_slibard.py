# Les contrôles de Slibard : jeu de caractères, axes, mêmes points partout.
import os, sys, glob
import pytest
from fontTools.ttLib import TTFont

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(ICI))
RACINE = os.path.dirname(os.path.dirname(ICI))
VAR = os.path.join(RACINE, 'fonts', 'variable', 'Slibard[VITE,wght].ttf')
FIXES = sorted(glob.glob(os.path.join(RACINE, 'fonts', 'otf', '*.otf')))


def test_quatorze_fixes():
    assert len(FIXES) == 16


def test_axes():
    axes = {a.axisTag: (a.minValue, a.defaultValue, a.maxValue) for a in TTFont(VAR)['fvar'].axes}
    assert axes == {'wght': (300, 400, 1000), 'VITE': (0, 0, 100)}


@pytest.mark.parametrize('chemin', FIXES + [VAR])
def test_jeu(chemin):
    cmap = TTFont(chemin).getBestCmap()
    voulu = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789éèêëàâçùûüîïôœæÉÈÀÇŒÆßäöüÄÖÜñ.,:;!?«»“”’-–—()&@€£$%§'
    assert not [c for c in voulu if ord(c) not in cmap]


def test_memes_points():
    from glyphes import table, dessine
    for n in table():
        formes = set()
        for poids in (300, 400, 650, 900, 1000):
            for vitesse in (0.0, 1.0):
                cs, _ = dessine(n, poids, vitesse)
                formes.add(tuple(tuple(s[0] for s in c) for c in cs))
        assert len(formes) == 1, n


def test_chiffres_chasse_fixe():
    for chemin in FIXES:
        h = TTFont(chemin)['hmtx']
        assert len({h[g][0] for g in ('zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine')}) == 1

