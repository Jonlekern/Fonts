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
