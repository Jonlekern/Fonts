import os, sys, glob
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import pytest
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from mesures import GRAISSES, NOMS, police
from pieces import glyphe, transforme, egaux

SORTIE = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', 'fonts'))
CYR = list(range(0x0410, 0x0450)) + [0x0401, 0x0451]
POIDS = dict(zip(GRAISSES, range(100, 1000, 100)))


def fichier(nom, it):
    return os.path.join(SORTIE, 'otf', f'SHKVAL-{nom}{"Italic" if it else ""}.otf')


CAS = [(g, n, it) for g, n in zip(GRAISSES, NOMS) for it in (False, True)]


def test_les_18_fichiers():
    for g, n, it in CAS:
        assert os.path.exists(fichier(n, it)), fichier(n, it)
        assert os.path.exists(fichier(n, it).replace('/otf/', '/woff2/').replace('.otf', '.woff2'))


@pytest.mark.parametrize('g,n,it', CAS)
def test_contenu(g, n, it):
    f = TTFont(fichier(n, it)); o = police(g, it)
    cm, cmo = f.getBestCmap(), o.getBestCmap()
    import unicodedata
    for u in cm:                                                         # que du russe, de l'ASCII et des signes
        c = chr(u); cat = unicodedata.category(c)
        assert u in CYR or u < 0x7F or u == 0x0301 or not (cat.startswith('L') or cat in ('Mn', 'Sk')), hex(u)   # 0301 : accent tonique
    assert all(cm[u] == v for u, v in cmo.items() if u < 0x7F)          # l'ASCII est là, mêmes noms
    assert 0xE9 not in cm and 0x0105 not in cm and 0xC5 not in cm       # é, ą, Å : partis
    assert all(u in cm for u in CYR)                                     # les 66 russes
    gs, gso = f.getGlyphSet(), o.getGlyphSet()
    for nom in o.getGlyphOrder():                                       # latin identique
        if nom == '.notdef' or nom not in gs:
            continue
        a, b = RecordingPen(), RecordingPen(); gs[nom].draw(a); gso[nom].draw(b)
        if nom not in ('multiply', 'less', 'greater'):
            assert a.value == b.value and f['hmtx'][nom] == o['hmtx'][nom], nom
    nm = {r.nameID: r.toUnicode() for r in f['name'].names if r.platformID == 3}
    assert not [r for r in f['name'].names if r.platformID == 1]
    assert nm[16] == 'SHKVAL' and nm[17] == n + (' Italic' if it else '')
    assert nm[1] == f'SHKVAL {n}' and nm[2] == ('Italic' if it else 'Regular')
    assert nm[6] == f'SHKVAL-{n}{"Italic" if it else ""}'
    assert 'Overshoot' not in ' '.join(nm.values())
    assert f['OS/2'].usWeightClass == POIDS[g]
    assert bool(f['OS/2'].fsSelection & 1) == it and bool(f['head'].macStyle & 2) == it
    assert f['OS/2'].ulCodePageRange1 & (1 << 2)                       # page de code cyrillique (1251)
    assert f['OS/2'].ulUnicodeRange1 & (1 << 9)
    assert 'STAT' in f
    p = RecordingPen(); gs['.notdef'].draw(p); assert p.value
    assert f['hmtx']['multiply'][0] == f['hmtx']['plus'][0] == f['hmtx']['less'][0] == f['hmtx']['greater'][0]
    assert len(f['STAT'].table.AxisValueArray.AxisValue) == 2


def kern(f, L, R):
    for st in f['GPOS'].table.LookupList.Lookup[0].SubTable:
        if L not in st.Coverage.glyphs:
            continue
        v = st.Class1Record[st.ClassDef1.classDefs.get(L, 0)].Class2Record[st.ClassDef2.classDefs.get(R, 0)].Value1
        return getattr(v, 'XAdvance', 0) if v else 0
    return 0


def test_crenage():
    for n, it in (('Shtil', False), ('Shtorm', True)):
        f = TTFont(fichier(n, it)); u = lambda c: f.getBestCmap()[ord(c)]
        assert kern(f, u('Г'), u('А')) == kern(f, 'F', 'A') != 0
        assert kern(f, u('Т'), u('А')) == kern(f, 'T', 'A') != 0
        assert kern(f, u('Т'), 'A') == kern(f, 'T', 'A')                 # russe – latin
        assert kern(f, 'T', u('о')) == kern(f, 'T', 'o') != 0            # latin – russe
        g = GRAISSES[NOMS.index(n)]
        assert kern(f, 'L', 'T') == kern(police(g, it), 'L', 'T') != 0           # le latin garde son crénage


def test_italique_penche():
    from cyrillique import lettre
    f = TTFont(fichier('Shtorm', True)); gs = f.getGlyphSet()
    from pathops import Path
    p = Path(); gs[f.getBestCmap()[ord('Ш')]].draw(p.getPen())
    k, dx = 0.2137, -64.0
    assert egaux(p, transforme(lettre('Ш', 'Storm')[0], (1, 0, k, 1, dx, 0)), tol=800)
