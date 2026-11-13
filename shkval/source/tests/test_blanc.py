# Le blanc entre deux lettres posées côte à côte (chasse + crénage), mesuré ligne par ligne :
# aucune paire russe fréquente ne doit se toucher.
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from functools import lru_cache
import pytest
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from mesures import GRAISSES, NOMS

SORTIE = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', 'fonts', 'otf'))
PAIRES = ['ст', 'ет', 'то', 'от', 'те', 'тс', 'тб', 'тэ', 'ну', 'пу', 'му', 'ду', 'лу', 'цу', 'ша', 'ня',
          'АЯ', 'ЕЯ', 'КЯ', 'ХЯ', 'Ая', 'Кя', 'Ея', 'ся', 'Тб', 'Уб', 'Кб', 'Жб', 'Гб', 'кб', 'нТ', 'иТ',
          'ко', 'но', 'ен', 'ов', 'ни', 'ра', 'во', 'ал', 'ре', 'ла', 'ли', 'ти', 'ос', 'ка', 'ер', 'ог',
          'сл', 'ло', 'ля', 'ол', 'ГЭ', 'ТА', 'ГА', 'УА', 'ЛА', 'ДА', 'ЯТ', 'ЬТ', 'ТЬ', 'ГО', 'ТО', 'ЧТ', 'Ст', 'Та', 'Го']
BLANC_MIN = 15
BANDES = range(-240, 1000, 6)


@lru_cache(None)
def police(fichier):
    return TTFont(fichier)


@lru_cache(None)
def profil(fichier, nom):
    """Pour chaque hauteur : (x le plus à gauche, x le plus à droite) de l'encre."""
    rp = RecordingPen(); police(fichier).getGlyphSet()[nom].draw(rp)
    polys = []; cur = []
    for op, a in rp.value:
        if op == 'moveTo': cur = [a[0]]
        elif op == 'lineTo': cur.append(a[0])
        elif op == 'curveTo':
            p0 = cur[-1]; p1, p2, p3 = a
            for k in range(1, 17):
                s = k / 16; m = 1 - s
                cur.append(tuple(m**3*p0[i] + 3*m*m*s*p1[i] + 3*m*s*s*p2[i] + s**3*p3[i] for i in (0, 1)))
        else:
            if len(cur) > 2: polys.append(cur)
            cur = []
    out = {}
    for y in BANDES:
        xs = []
        for poly in polys:
            for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
        if xs:
            out[y] = (min(xs), max(xs))
    return out


def kern(f, L, R):
    for st in f['GPOS'].table.LookupList.Lookup[0].SubTable:
        if L not in st.Coverage.glyphs:
            continue
        v = st.Class1Record[st.ClassDef1.classDefs.get(L, 0)].Class2Record[st.ClassDef2.classDefs.get(R, 0)].Value1
        return getattr(v, 'XAdvance', 0) if v else 0
    return 0


def blanc(fichier, a, b):
    f = police(fichier); cm = f.getBestCmap(); L, R = cm[ord(a)], cm[ord(b)]
    dx = f['hmtx'][L][0] + kern(f, L, R)
    pa, pb = profil(fichier, L), profil(fichier, R)
    return min(pb[y][0] + dx - pa[y][1] for y in pa if y in pb)


@pytest.mark.parametrize('nom,it', [(n, it) for n in NOMS for it in (False, True)])
def test_les_paires_ne_se_touchent_pas(nom, it):
    fichier = os.path.join(SORTIE, f'SHKVAL-{nom}{"Italic" if it else ""}.otf')
    serrees = [(p, round(blanc(fichier, *p))) for p in PAIRES if blanc(fichier, *p) < BLANC_MIN]
    assert not serrees, serrees
