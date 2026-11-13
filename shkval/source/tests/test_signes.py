# №, ₽ et l'accent tonique (aigu combinant posé sur les voyelles russes)
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import pytest
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from mesures import GRAISSES, NOMS, mesures
from cyrillique import lettre

SORTIE = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', 'fonts', 'otf'))
VOYELLES = 'аеёиоуыэюяАЕЁИОУЫЭЮЯ'


def bornes(f, nom):
    p = BoundsPen(f.getGlyphSet()); f.getGlyphSet()[nom].draw(p); return p.bounds


def test_numero_et_rouble_dessines():
    for g in ('Calm', 'Storm'):
        m = mesures(g)
        p, w = lettre('№', g); x0, y0, x1, y1 = p.bounds
        assert y0 >= -1 and y1 <= 737 and x1 <= w
        p, w = lettre('₽', g); x0, y0, x1, y1 = p.bounds
        stem = m['approche_cap']
        assert y0 >= -1 and y1 <= 737 and x1 <= w
        assert x0 < (w - lettre('Р', g)[1]) + stem         # les barres dépassent à gauche du fût


@pytest.mark.parametrize('nom,it', [(n, it) for n in NOMS for it in (False, True)])
def test_dans_les_fichiers(nom, it):
    f = TTFont(os.path.join(SORTIE, f'SHKVAL-{nom}{"Italic" if it else ""}.otf'))
    cm = f.getBestCmap()
    assert 0x2116 in cm and 0x20BD in cm and 0x0301 in cm
    acc = cm[0x0301]
    assert f['hmtx'][acc][0] == 0
    assert f['GDEF'].table.GlyphClassDef.classDefs[acc] == 3
    gp = f['GPOS'].table
    marks = [i for i, r in enumerate(gp.FeatureList.FeatureRecord) if r.FeatureTag == 'mark']
    assert marks
    look = gp.LookupList.Lookup[gp.FeatureList.FeatureRecord[marks[0]].Feature.LookupListIndex[0]]
    st = look.SubTable[0]
    bases = st.BaseCoverage.glyphs
    for v in VOYELLES:
        assert cm[ord(v)] in bases, v
    # l'accent se pose centré sur le а : le milieu de son bas tombe au milieu de la lettre (à la pente près)
    a = cm[ord('а')]; ia = bases.index(a)
    ba = st.BaseArray.BaseRecord[ia].BaseAnchor[0]
    ma = st.MarkArray.MarkRecord[0].MarkAnchor
    w = f['hmtx'][a][0]
    assert abs(ba.XCoordinate - (w / 2 + (0.2135 * ba.YCoordinate - 64 if it else 0))) <= 3
    assert ba.YCoordinate > 600 and ma.YCoordinate > 600
