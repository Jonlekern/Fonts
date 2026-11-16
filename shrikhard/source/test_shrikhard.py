# python3 -m pytest source/test_shrikhard.py
import os
import numpy as np
import pytest
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.boundsPen import BoundsPen

FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'fonts')
VARS = {'Regular': 'Shrikhard[HAUT].ttf', 'Italic': 'Shrikhard-Italic[HAUT].ttf'}
FIXES = {'Regular': 'Shrikhard-Regular.ttf', 'Italic': 'Shrikhard-Italic.ttf'}


def var(style):
    return TTFont(os.path.join(FONTS, 'variable', VARS[style]))


def fixe(style):
    return TTFont(os.path.join(FONTS, 'ttf', FIXES[style]))


def bornes(f, g):
    gs = f.getGlyphSet(); b = BoundsPen(gs); gs[g].draw(b); return b.bounds


def coupe(f, g, y):
    """Les largeurs d'encre d'un glyphe le long d'une ligne horizontale."""
    from fontTools.pens.recordingPen import DecomposingRecordingPen
    from fontTools.pens.basePen import decomposeQuadraticSegment
    gs = f.getGlyphSet(); rp = DecomposingRecordingPen(gs); gs[g].draw(rp)
    xs, cur = [], None
    def seg(p0, p1):
        if (p0[1] - y) * (p1[1] - y) < 0:
            xs.append(p0[0] + (y - p0[1]) * (p1[0] - p0[0]) / (p1[1] - p0[1]))
    start = None
    for op, a in rp.value:
        if op == 'moveTo':
            cur = start = a[0]
        elif op == 'lineTo':
            seg(cur, a[0]); cur = a[0]
        elif op == 'qCurveTo':
            if a[-1] is None:
                a = a[:-1]; st = ((a[-1][0] + a[0][0]) / 2, (a[-1][1] + a[0][1]) / 2); cur = start = st; a = a + (st,)
            for c, p in decomposeQuadraticSegment(a):
                for t in np.linspace(0.05, 1, 20):
                    q = ((1-t)**2*cur[0]+2*t*(1-t)*c[0]+t*t*p[0], (1-t)**2*cur[1]+2*t*(1-t)*c[1]+t*t*p[1])
                    seg(cur, q); cur = q
        elif op in ('closePath', 'endPath'):
            seg(cur, start)
    xs.sort()
    return [xs[i + 1] - xs[i] for i in range(0, len(xs) - 1, 2)]


@pytest.mark.parametrize('style', ['Regular', 'Italic'])
def test_latin_seulement(style):
    cm = fixe(style).getBestCmap()
    assert not [c for c in cm if 0x0900 <= c <= 0x0DFF]
    assert all(chr(c) in ''.join(map(chr, cm)) for c in map(ord, 'AZaz09ÀÿŒœßĽľďť€„‚'))


@pytest.mark.parametrize('style', ['Regular', 'Italic'])
def test_le_curseur(style):
    f = var(style)
    axes = {a.axisTag: (a.minValue, a.defaultValue, a.maxValue) for a in f['fvar'].axes}
    assert axes['HAUT'] == (-100, 0, 20)
    assert [i.coordinates['HAUT'] for i in f['fvar'].instances] == [20, 0, -20, -40, -60, -80, -100]


def test_elargie_sans_deformer():
    """Le fût du n garde l'épaisseur de Shrikhand (251) ; un étirement brut donnerait 324."""
    f = fixe('Regular')
    w = coupe(f, 'n', 250)
    assert all(abs(x - 251) < 35 for x in w)        # 251 à 5 % près ; brut, ce serait 324
    orig = TTFont(os.path.join(FONTS, '..', 'original', 'Shrikhand-Regular.ttf'))
    assert f['hmtx']['n'][0] == round(orig['hmtx']['n'][0] * 1.29)


def test_la_variable_a_zero_est_la_fixe():
    f = instantiateVariableFont(var('Regular'), {'HAUT': 0, 'wght': 400})
    g = fixe('Regular')
    for n in ('a', 'H', 'g', 'eacute', 'Lcaron'):
        assert bornes(f, n) == bornes(g, n)


@pytest.mark.parametrize('style', ['Regular', 'Italic'])
def test_au_bout_un_trait(style):
    """À -100, chaque lettre n'est plus qu'un trait de 120 unités qui remplit sa chasse."""
    f = instantiateVariableFont(var(style), {'HAUT': -100, 'wght': 400})
    for n in 'ABHOabgnoy':
        x0, y0, x1, y1 = bornes(f, n)
        assert y0 >= -1 and y1 <= 121


def test_guillemet_bas_double():
    f = fixe('Regular')
    assert f['glyf']['quotedblbase'].numberOfContours == 2
    assert f['hmtx']['quotesinglbase'][0] == f['hmtx']['comma'][0]
