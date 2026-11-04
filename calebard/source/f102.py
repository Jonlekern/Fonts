"""Calebard 1.0.2, étape 5 : F à la largeur du logo LAFLEURSTUDIO (bras 6,3 % plus longs, comme le L).
usage : f102.py <ttf> [...]   (modifie les fichiers)"""
import sys
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates
from fontTools.pens.boundsPen import BoundsPen
from array import array
F_RATIO = 0.0630                     # Black : 1858 -> 1975

def pts(g): return [list(p) for p in g.coordinates], list(g.flags), list(g.endPtsOfContours)
def ecrit(g, c, fl, ends, glyf):
    g.coordinates = GlyphCoordinates([(round(x), round(y)) for x, y in c]); g.flags = array('B', fl); g.endPtsOfContours = ends
    if hasattr(g, 'program'): g.program.fromBytecode(b'')
    g.recalcBounds(glyf)

def bras_F(f):
    glyf, hmtx = f['glyf'], f['hmtx']; g = glyf['F']; c, fl, ends = pts(g)
    x0 = min(x for x, _ in c); x1 = max(x for x, _ in c)
    stem = min(x for x, y in c if y == 0 and x > x0)
    mid_arm = min(x for x, y in c if x > stem + 50)
    split = (stem + mid_arm)/2; d = round(F_RATIO*(x1 - x0))
    for p in c:
        if p[0] > split: p[0] += d
    ecrit(g, c, fl, ends, glyf)
    gs = f.getGlyphSet(); touch = ['F']
    for n in f.getGlyphOrder():
        gg = glyf[n]
        if gg.isComposite() and gg.components[0].glyphName == 'F':
            for k in gg.components[1:]:
                bp = BoundsPen(gs); gs[k.glyphName].draw(bp)
                if bp.bounds and (bp.bounds[0] + bp.bounds[2])/2 + k.x > split: k.x += round(d/2)
            gg.recalcBounds(glyf); touch.append(n)
    for n in touch: hmtx[n] = (hmtx[n][0] + d, hmtx[n][1])
    for lk in f['GPOS'].table.LookupList.Lookup:
        if lk.LookupType != 4: continue
        for st in lk.SubTable:
            bc = st.BaseCoverage.glyphs
            for n in touch:
                if n in bc:
                    for a in st.BaseArray.BaseRecord[bc.index(n)].BaseAnchor:
                        if a is not None and a.XCoordinate > split: a.XCoordinate += round(d/2)
    return d

def lsb(f):
    glyf, hmtx = f['glyf'], f['hmtx']
    for n in f.getGlyphOrder():
        g = glyf[n]
        if g.isComposite(): g.recalcBounds(glyf)
        if hasattr(g, 'xMin') and (g.isComposite() or g.numberOfContours > 0): hmtx[n] = (hmtx[n][0], g.xMin)

if __name__ == '__main__':
    for p in sys.argv[1:]:
        f = TTFont(p); d = bras_F(f); lsb(f); f['OS/2'].recalcAvgCharWidth(f); f.save(p); print(p.split('/')[-1], 'F +%d' % d)
