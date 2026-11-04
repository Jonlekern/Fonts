"""Calebard 1.0.2, étape 2 : R à la largeur du logo LAFLEURSTUDIO (t-shirt).
Tout ce qui est à droite du montant est resserré à 90 % (rond, trou, jambe) ; le montant ne bouge pas.
Les accents des composites (Ŕ Ř Ŗ Ȑ Ȓ Ṛ Ṟ) et les ancres suivent.
usage : r102.py <ttf> [<ttf> ...]   (modifie les fichiers)"""
import sys
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
K = 0.900

def process(path):
    f = TTFont(path); glyf, hmtx = f['glyf'], f['hmtx']
    g = glyf['R']; c = list(g.coordinates)
    x0 = min(x for x, _ in c); xmax = max(x for x, _ in c)
    sr = min(x for x, y in c if y == 0 and x > x0)          # bord droit du montant
    fx = lambda x: sr + (x - sr)*K if x > sr else x
    for i, (x, y) in enumerate(c): g.coordinates[i] = (round(fx(x)), y)
    g.recalcBounds(glyf)
    d = round(xmax - fx(xmax))
    hmtx['R'] = (hmtx['R'][0] - d, hmtx['R'][1])
    touche = ['R']; gs = f.getGlyphSet()
    for n in f.getGlyphOrder():
        gg = glyf[n]
        if not gg.isComposite() or gg.components[0].glyphName != 'R': continue
        for k in gg.components[1:]:
            bp = BoundsPen(gs); gs[k.glyphName].draw(bp)
            if not bp.bounds: continue
            mx = (bp.bounds[0] + bp.bounds[2])/2 + k.x
            k.x = round(k.x + fx(mx) - mx)
        hmtx[n] = (hmtx[n][0] - d, hmtx[n][1]); gg.recalcBounds(glyf); touche.append(n)
    for lk in f['GPOS'].table.LookupList.Lookup:
        if lk.LookupType != 4: continue
        for st in lk.SubTable:
            bc = st.BaseCoverage.glyphs
            for n in touche:
                if n not in bc: continue
                for a in st.BaseArray.BaseRecord[bc.index(n)].BaseAnchor:
                    if a is not None: a.XCoordinate = round(fx(a.XCoordinate))
    f['OS/2'].recalcAvgCharWidth(f)
    f.save(path)
    return sr, d, len(touche)

if __name__ == '__main__':
    for p in sys.argv[1:]: print(p.split('/')[-1], 'montant jusqu\'à %d, %d unités en moins, %d glyphes' % process(p))
