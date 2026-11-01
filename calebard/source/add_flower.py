"""Add the LaFleurStudio flower to Calebard fonts.
U+2740 ❀ -> 'flower' (logo as drawn) ; U+273F ✿ -> 'flower.bold' (stroke thickened, "Bold 1").
Both scaled to cap height (1350 units), sitting on the baseline.
usage: add_flower.py font.ttf [font.ttf ...]   (edits in place)"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from flower_lib import flower
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.reverseContourPen import ReverseContourPen
from fontTools.pens.areaPen import AreaPen

CAP, SB = 1350, 100
K = 1350 / 1619
SHAPES = {"flower": (0x2740, flower(0)), "flower.bold": (0x273F, flower(150 / K - 57))}

def glyph_for(path):
    x0, y0, x1, y1 = path.bounds; s = CAP / (y1 - y0)
    tr = (s, 0, 0, s, SB - x0 * s, -y0 * s)
    ap = AreaPen(); path.draw(TransformPen(ap, tr))
    tt = TTGlyphPen(None)
    target = ReverseContourPen(tt) if ap.value > 0 else tt      # TrueType: outer contours clockwise
    path.draw(TransformPen(Cu2QuPen(target, max_err=1.0), tr))
    return tt.glyph(), round((x1 - x0) * s + 2 * SB)

built = {n: glyph_for(p) for n, (_, p) in SHAPES.items()}
for fp in sys.argv[1:]:
    f = TTFont(fp); order = f.getGlyphOrder()
    new = [n for n in SHAPES if n not in order]
    if new: f.setGlyphOrder(order + new)
    for n, (cp, _) in SHAPES.items():
        g, adv = built[n]
        f["glyf"][n] = g; g.recalcBounds(f["glyf"]); f["hmtx"][n] = (adv, g.xMin)
        for t in f["cmap"].tables:
            if t.isUnicode(): t.cmap[cp] = n
    f.save(fp)
    print(os.path.basename(fp), "ok", {n: f["hmtx"][n] for n in SHAPES})
