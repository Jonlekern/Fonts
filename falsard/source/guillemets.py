"""Guillemets « » ‹ › de Falsard, faits à partir de son propre < et > (option 2 : petits, posés en bas).
Le chevron est réduit à 55 %, son trait regonflé pour garder l'épaisseur d'origine, puis posé sur la ligne de base.
usage : guillemets.py police.ttf sortie.ttf 0.55 base"""
import sys, math, pathops
from fontTools.ttLib import TTFont
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.areaPen import AreaPen
from fontTools.pens.reverseContourPen import ReverseContourPen

def path_of(gs, n, m=(1, 0, 0, 1, 0, 0)):
    p = pathops.Path(); gs[n].draw(TransformPen(p.getPen(), m)); return p

def chevron(f, base, S):
    gs = f.getGlyphSet(); p = path_of(gs, base); x0, y0, x1, y1 = p.bounds
    a = AreaPen(); p.draw(a); w, h = x1 - x0, y1 - y0
    t = abs(a.value) / (2 * math.hypot(w, h / 2))                 # épaisseur du trait du chevron
    q = path_of(gs, base, (S, 0, 0, S, -x0 * S, -y0 * S))           # réduit, coin en bas à gauche à (0,0)
    o = t * (1 - S) / 2                                             # on regonfle le trait
    if o > 0.5:
        st = pathops.Path(q); st.stroke(2 * o, pathops.LineCap.BUTT_CAP, pathops.LineJoin.MITER_JOIN, 6)
        q = pathops.op(q, st, pathops.PathOp.UNION, fix_winding=True)
    bx0, by0, bx1, by1 = q.bounds
    return q, (bx0, by0, bx1, by1), t

def add(f, S, place):
    gs = f.getGlyphSet(); cm = f.getBestCmap(); glyf, hmtx = f['glyf'], f['hmtx']
    hy = path_of(gs, cm[ord('-')]).bounds; yc = (hy[1] + hy[3]) / 2
    lsb = hmtx['less'][1]
    for name, base, n, cp in (('guilsinglleft', 'less', 1, 0x2039), ('guilsinglright', 'greater', 1, 0x203A),
                              ('guillemetleft', 'less', 2, 0x00AB), ('guillemotright', 'greater', 2, 0x00BB)):
        q, (bx0, by0, bx1, by1), t = chevron(f, base, S)
        cw = bx1 - bx0; ch = by1 - by0; gap = 0.18 * cw
        dy = (yc - (by0 + by1) / 2) if place == 'tiret' else -by0
        out = pathops.Path()
        for k in range(n):
            dx = lsb - bx0 + k * (cw + gap)
            pk = pathops.Path(); q.draw(TransformPen(pk.getPen(), (1, 0, 0, 1, dx, dy)))
            out = pathops.op(out, pk, pathops.PathOp.UNION, fix_winding=True)
        a = AreaPen(); out.draw(a); tt = TTGlyphPen(None)
        out.draw(ReverseContourPen(tt) if a.value > 0 else tt)
        g = tt.glyph(); 
        if name not in f.getGlyphOrder(): f.setGlyphOrder(f.getGlyphOrder() + [name])
        glyf[name] = g; g.recalcBounds(glyf)
        hmtx[name] = (round(lsb + n * cw + (n - 1) * gap + lsb), g.xMin)
        for tb in f['cmap'].tables:
            if tb.isUnicode(): tb.cmap[cp] = name
    return f

if __name__ == '__main__':
    src, dst, S, place = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
    f = TTFont(src); add(f, S, place); f.save(dst)
