"""Calebard 1.0.2, étape 4 : bout du crochet du j coupé en biais (dessin de Johnny) : le bas part plus loin
vers la gauche, sous la lettre d'avant, le haut du bout recule. Même angle dans toutes les graisses.
Black : bas du bout −59, haut du bout +112 (sur un bout de 362 de haut).
usage : j102.py <ttf> [...]"""
import sys
from fontTools.ttLib import TTFont
BAS, HAUT = -59/362, 112/362
def process(path):
    f = TTFont(path); glyf, hmtx = f['glyf'], f['hmtx']; out = []
    for n in ('j', 'uni0237'):
        g = glyf[n]; c = list(g.coordinates); fl = list(g.flags)
        x0 = min(x for x, _ in c[:g.endPtsOfContours[0] + 1])
        bout = [i for i, (x, y) in enumerate(c) if x == x0 and i <= g.endPtsOfContours[0]]
        assert len(bout) == 2, (n, bout)
        ib, ih = sorted(bout, key=lambda i: c[i][1])
        h = c[ih][1] - c[ib][1]
        c[ib] = (round(c[ib][0] + BAS*h), c[ib][1]); c[ih] = (round(c[ih][0] + HAUT*h), c[ih][1])
        for i, p in enumerate(c): g.coordinates[i] = p
        g.recalcBounds(glyf); hmtx[n] = (hmtx[n][0], g.xMin); out.append((n, h, c[ib][0], c[ih][0]))
    for n in f.getGlyphOrder():
        g = glyf[n]
        if g.isComposite() and any(k.glyphName in ('j', 'uni0237') for k in g.components):
            g.recalcBounds(glyf); hmtx[n] = (hmtx[n][0], g.xMin)
    f.save(path); return out
if __name__ == '__main__':
    for p in sys.argv[1:]: print(p.split('/')[-1], process(p)[0])
