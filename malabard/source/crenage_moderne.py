# Le crénage moderne de Malabard, en GPOS (kern) : le même crénage, sorti de la vieille table « kern »
# que beaucoup de logiciels ignorent (Affinity, Canva, certains logiciels Adobe…).
#   python3 source/crenage_moderne.py fonts/ttf/Malabard-Regular.ttf [...]
# Le fichier TTF est réécrit, le WOFF2 refait à côté (fonts/woff2/).
import os, sys
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.otlLib.builder import buildStatTable

def crenage(font):
    """Le crénage de Malabard tel qu'il est (celui de Righteous, plus les collisions de l'italique réglées par
    finalize_malabard.py), sorti de la vieille table « kern »."""
    table = {}
    if 'kern' in font:
        for st in font['kern'].kernTables:
            table.update(st.kernTable)
    return {k: v for k, v in table.items() if v}, None


def fea(table, familles, font):
    L = ['languagesystem DFLT dflt;', 'languagesystem latn dflt;', 'feature kern {']
    ordre = set(font.getGlyphOrder())
    for (a, b), v in sorted(table.items()):
        if a in ordre and b in ordre:
            L.append(f'  pos {a} {b} {v};')
    L.append('} kern;')
    return '\n'.join(L)


def finitions(f):
    """Ce que fontbakery demande : pas de noms Mac, une table STAT, un .notdef dessiné, la bonne largeur moyenne."""
    f['name'].names = [n for n in f['name'].names if n.platformID != 1]
    upm = f['head'].unitsPerEm
    if not f['glyf']['.notdef'].numberOfContours:
        pen = TTGlyphPen(None); w = round(0.5 * upm); h = f['OS/2'].sCapHeight; e = round(0.05 * upm)
        for pts in ([(e, 0), (e, h), (w - e, h), (w - e, 0)], [(2 * e, e), (w - 2 * e, e), (w - 2 * e, h - e), (2 * e, h - e)]):
            pen.moveTo(pts[0]); [pen.lineTo(p) for p in pts[1:]]; pen.closePath()
        f['glyf']['.notdef'] = pen.glyph(); f['hmtx']['.notdef'] = (w, e)
    f['OS/2'].recalcAvgCharWidth(f)
    os2 = f['OS/2']
    if not os2.fsSelection & 0b100001:                 # ni italique ni gras : c'est le « Regular » de sa famille
        os2.fsSelection |= 1 << 6
    if 'prep' not in f:                                # le contrôle des pertes de pixels (smart dropout), comme partout
        from fontTools.ttLib import newTable
        from fontTools.ttLib.tables import ttProgram
        prep = newTable('prep'); prep.program = ttProgram.Program()
        prep.program.fromAssembly(['PUSHW[ ]', '511', 'SCANCTRL[ ]', 'PUSHB[ ]', '4', 'SCANTYPE[ ]'])
        f['prep'] = prep
    poids = f['OS/2'].usWeightClass
    italique = bool(f['OS/2'].fsSelection & 1)
    style = f['name'].getDebugName(17) or f['name'].getDebugName(2)
    nom_poids = style.replace(' Italic', '').replace('Italic', 'Regular') if style else 'Regular'
    ital = {'value': 1, 'name': 'Italic'} if italique else {'value': 0, 'name': 'Roman', 'flags': 2, 'linkedValue': 1}
    buildStatTable(f, [{'tag': 'wght', 'name': 'Weight', 'values': [{'value': poids, 'name': nom_poids}]},
                       {'tag': 'ital', 'name': 'Italic', 'values': [ital]}], elidedFallbackName=2, macNames=False)


def traite(chemin):
    f = TTFont(chemin)
    table, familles = crenage(f)
    if 'kern' in f:
        del f['kern']
    addOpenTypeFeaturesFromString(f, fea(table, familles, f))
    finitions(f)
    f.save(chemin)
    w = TTFont(chemin); w.flavor = 'woff2'
    sortie = os.path.join(os.path.dirname(os.path.dirname(chemin)), 'woff2', os.path.basename(chemin)[:-4] + '.woff2')
    w.save(sortie)
    return len(table)


if __name__ == '__main__':
    for c in sys.argv[1:]:
        print(os.path.basename(c), traite(c), 'paires')
