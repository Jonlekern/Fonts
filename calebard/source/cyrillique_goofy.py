"""Le cyrillique dans Goofy et Extra Goofy, sans refaire les lettres latines (qui restent en 1.0.1).
Les lettres russes du Black (déjà passé par cyrillique.py) sont penchées ou tournées comme les autres,
avec leurs variantes, ajoutées aux variantes contextuelles (calt) et au crénage.
usage : cyrillique_goofy.py Calebard-Goofy.ttf Calebard-Black-avec-cyrillique.ttf"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cyrillique import JUMELLES, crenage, cyrl, Graisse
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.boundsPen import BoundsPen

dst, src = sys.argv[1], sys.argv[2]
f = TTFont(dst); B = TTFont(src); bgs = B.getGlyphSet(); bcm = B.getBestCmap()
cyr = {c: n for c, n in bcm.items() if 0x400 <= c <= 0x4FF}
order = f.getGlyphOrder()
if 'A.goofy' in order:                      # Goofy : penchée à droite, variante penchée à gauche
    T = math.tan(math.radians(12.0))
    def mat(x0, y0, x1, y1, s): cy = (y0 + y1) / 2; return (1, 0, s, 1, -s * cy, 0)
    pas = {'': T, '.goofy': -T}
else:                                       # Extra Goofy : tournée, cycle +7 -4 +10 -7 +4 -10
    CYCLE = [7, -4, 10, -7, 4, -10]
    def mat(x0, y0, x1, y1, deg):
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; a = math.radians(deg); c, s = math.cos(a), math.sin(a)
        return (c, s, -s, c, cx - cx * c + cy * s, cy - cx * s - cy * c)
    pas = {('' if k == 0 else f'.eg{k}'): CYCLE[k] for k in range(6)}

# Л et Д penchés ou tournés vers la gauche : leur jambe se redresserait et ils ressembleraient à un П.
# On les redessine avec une jambe plus penchée de la même quantité.
JAMBES = {'uni041B', 'uni043B', 'uni0414', 'uni0434'}
redessins = {}
def jambe(n, v):
    pente = abs(v) if 'A.goofy' in order else math.tan(math.radians(abs(v)))
    if pente not in redessins:
        g = Graisse(src, pente); g.dessine(); redessins[pente] = g.neufs
    return redessins[pente][n][1]

def glyphe(n, v):
    if n in JAMBES and v < 0:
        p = jambe(n, v); rec = DecomposingRecordingPen(None); p.draw(rec); b = p.bounds
    else:
        rec = DecomposingRecordingPen(bgs); bgs[n].draw(rec)
        bp = BoundsPen(bgs); bgs[n].draw(bp); b = bp.bounds
    tt = TTGlyphPen(None); rec.replay(TransformPen(tt, mat(*b, v)))
    return tt.glyph()

glyf, hmtx = f['glyf'], f['hmtx']
noms = sorted(set(cyr.values()))
neufs = [n + suf for suf in pas for n in noms]
f.setGlyphOrder(order + [n for n in neufs if n not in order])
for n in noms:
    for suf, v in pas.items():
        g = glyphe(n, v); glyf[n + suf] = g; g.recalcBounds(glyf)
        hmtx[n + suf] = (B['hmtx'][n][0], g.xMin if g.numberOfContours else 0)
for t in f['cmap'].tables:
    if t.isUnicode():
        for c, n in cyr.items(): t.cmap[c] = n
f['maxp'].numGlyphs = len(f.getGlyphOrder())

# variantes contextuelles : on ajoute les lettres russes partout où se trouve le A et ses variantes
gsub = f['GSUB'].table
for lk in gsub.LookupList.Lookup:
    for st in lk.SubTable:
        if lk.LookupType == 6 and st.Format == 3:
            for cv in st.InputCoverage + st.BacktrackCoverage:
                for suf in pas:
                    if 'A' + suf in cv.glyphs: cv.glyphs = cv.glyphs + [n + suf for n in noms if n + suf not in cv.glyphs]
        if lk.LookupType == 1 and st.mapping.get('A', '').startswith('A.'):
            suf = st.mapping['A'][1:]
            for n in noms: st.mapping[n] = n + suf
gid = f.getReverseGlyphMap(rebuild=True)
for lk in gsub.LookupList.Lookup:
    for st in lk.SubTable:
        if lk.LookupType == 6 and st.Format == 3:
            for cv in st.InputCoverage + st.BacktrackCoverage + st.LookAheadCoverage: cv.glyphs = sorted(set(cv.glyphs), key=gid.get)

cyrl(f, neufs)
code = {n: c for c, n in cyr.items()}
crenage(f, {n + suf: tuple(JUMELLES[code[n]]) for n in noms for suf in pas})
os2 = f['OS/2']
ymax = max(getattr(glyf[n], 'yMax', 0) for n in f.getGlyphOrder()); ymin = min(getattr(glyf[n], 'yMin', 0) for n in f.getGlyphOrder())
if 'A.eg1' in order: os2.usWinAscent = max(os2.usWinAscent, ymax); os2.usWinDescent = max(os2.usWinDescent, -ymin)
os2.recalcAvgCharWidth(f)
f.save(dst)
print(os.path.basename(dst), len(noms), 'lettres russes,', len(neufs), 'glyphes ajoutés')
