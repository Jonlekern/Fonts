# Finitions : le crénage déclaré par alphabet, et pas de bord presque plat (cran d'une unité) dans les lettres construites
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import pytest
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from mesures import NOMS
from cyrillique import copies

SORTIE = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', 'fonts', 'otf'))
CAS = [(n, it) for n in NOMS for it in (False, True)]


def fichier(n, it):
    return os.path.join(SORTIE, f'SHKVAL-{n}{"Italic" if it else ""}.otf')


@pytest.mark.parametrize('n,it', CAS)
def test_crenage_par_alphabet(n, it):
    gp = TTFont(fichier(n, it))['GPOS'].table
    tags = {sr.ScriptTag: sr for sr in gp.ScriptList.ScriptRecord}
    assert {'DFLT', 'cyrl', 'latn'} <= set(tags)
    for t in ('DFLT', 'cyrl', 'latn'):
        feats = {gp.FeatureList.FeatureRecord[i].FeatureTag for i in tags[t].Script.DefaultLangSys.FeatureIndex}
        assert feats == {'kern', 'mark'}, (t, feats)


@pytest.mark.parametrize('n,it', CAS)
def test_pas_de_bord_presque_plat(n, it):
    f = TTFont(fichier(n, it)); gs = f.getGlyphSet(); cm = f.getBestCmap()
    cop = copies()
    mauvais = []
    for u in list(range(0x0410, 0x0450)) + [0x0401, 0x0451, 0x2116, 0x20BD]:
        c = chr(u)
        if c in cop:
            continue                                   # les lettres reprises restent identiques au latin
        rp = RecordingPen(); gs[cm[u]].draw(rp); cur = None
        for op, a in rp.value:
            if op == 'moveTo':
                cur = a[0]
            elif op == 'lineTo':
                (x0, y0), (x1, y1) = cur, a[0]; dx, dy = abs(x1 - x0), abs(y1 - y0)
                if 0 < dy <= 2 and dx >= 10:
                    mauvais.append((c, cur, a[0]))
                if not it and 0 < dx <= 2 and dy >= 10:
                    mauvais.append((c, cur, a[0]))
                cur = a[0]
            elif op == 'curveTo':
                cur = a[-1]
    assert not mauvais, mauvais[:8]
