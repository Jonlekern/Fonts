import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import pytest
from fontTools.ttLib import TTFont
from gp_base import charger_base, SOURCE


@pytest.fixture(scope="module")
def base():
    return charger_base()


def test_base(base):
    assert "fvar" not in base
    glyf = base["glyf"]
    assert not any(glyf[n].isComposite() for n in base.getGlyphOrder())
    assert len(base.getGlyphOrder()) == len(TTFont(SOURCE).getGlyphOrder())
    cm = base.getBestCmap()
    for c in "AZ09É":
        assert ord(c) in cm


import pathops
from gp_tranches import decouper, COUPES


def _aire(contours):
    p = pathops.Path()
    pen = p.getPen()
    for c in contours:
        pen.moveTo(c[0][:2])
        for x, y, on in c[1:]:
            pen.lineTo((x, y))
        pen.closePath()
    return abs(p.area)


@pytest.fixture(scope="module")
def gs(base):
    return base.getGlyphSet()


def test_union_egale_glyphe(base, gs):
    from gp_tranches import _chemin
    cm = base.getBestCmap()
    for c in "AEOS":
        tr = decouper(gs, cm[ord(c)])
        union = pathops.Path()
        pen = union.getPen()
        for t in tr:
            for ct in t:
                pen.moveTo(ct[0][:2])
                for x, y, on in ct[1:]:
                    pen.lineTo((x, y))
                pen.closePath()
        union.simplify()
        ref = _chemin(gs, cm[ord(c)]); ref.simplify()
        poly = pathops.Path(); ref.draw(poly.getPen())  # même approximation polygonale ? on compare grossièrement
        assert abs(abs(union.area) - abs(ref.area)) / abs(ref.area) < 0.02, c


def test_signe_sans_bas(base, gs):
    cm = base.getBestCmap()
    tr = decouper(gs, cm[ord("'")])
    assert tr[0] == [] and tr[1] == [] and tr[2] == []
    assert tr[3]


def test_haut_intact(base, gs):
    cm = base.getBestCmap()
    tr = decouper(gs, cm[ord("E")])
    from gp_tranches import _chemin
    src = {(round(x), round(y)) for op, pts in _chemin(gs, cm[ord("E")]).segments for (x, y) in (p for p in pts if p) if y > 445}
    haut = {(round(x), round(y)) for c in tr[3] for x, y, on in c if y > 445}
    assert src == haut


import random
from gp_masters import master_band, vitesse, glyphe, BAND, OVERLAP_SIMPLE


def _signature(contours):
    return [len(c) for c in contours], [on for c in contours for x, y, on in c]


def test_compatible(base, gs):
    noms = [n for n in base.getGlyphOrder()]
    random.seed(4)
    for n in random.sample(noms, 50) + [base.getBestCmap()[ord(c)] for c in "EOÉQ'"]:
        tr = decouper(gs, n)
        sigs = {repr(_signature(vitesse(master_band(tr, *BAND[b])) if v else master_band(tr, *BAND[b]))) for b in BAND for v in (0, 1)}
        assert len(sigs) == 1, n


def test_overlap_flag(base, gs):
    tr = decouper(gs, base.getBestCmap()[ord("E")])
    g = glyphe(master_band(tr, *BAND[50]))
    assert g.flags[0] & OVERLAP_SIMPLE


def test_aire_signee(base, gs):
    def sens(c):
        return sum((x1 - x0) * (y1 + y0) for (x0, y0, _), (x1, y1, _) in zip(c, c[1:] + c[:1])) > 0
    for ch in "AEOSRG8":
        tr = decouper(gs, base.getBestCmap()[ord(ch)])
        ref = [sens(c) for c in master_band(tr, *BAND[0])]
        coin = [sens(c) for c in vitesse(master_band(tr, *BAND[100]))]
        assert ref == coin, ch
