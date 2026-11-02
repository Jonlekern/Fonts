"""Après l'étirement à 120 % : enlève les contours vides et écarte un peu les accents trop collés.
usage : nudge.py ref.ttf font.ttf   (font modifiée sur place ; ref = graisse voisine plus fine)"""
import sys, json, copy
chk = open('check_1000.py').read(); exec(chk[:chk.index("ref, new = TTFont")])
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphCoordinates
from fontTools.pens.areaPen import AreaPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
ACCEPTED = {'tcaron.ss01', 'uni01EA', 'uni022C', 'uni022D', 'uni20A9'}       # déjà acceptés à 130 %
ref, f = TTFont(sys.argv[1]), TTFont(sys.argv[2]); glyf = f['glyf']
# 1. contours sans surface (restes de la fusion des formes)
for n in f.getGlyphOrder():
    g = glyf[n]
    if g.isComposite() or g.numberOfContours <= 1: continue
    c, fl = g.getCoordinates(glyf)[0], g.flags; s = 0; keep = []
    for e in g.endPtsOfContours:
        pts = list(c[s:e+1]); xs = [x for x, _ in pts]; ys = [y for _, y in pts]
        if max(xs) - min(xs) > 2 and max(ys) - min(ys) > 2: keep.append((s, e))
        s = e + 1
    if len(keep) < g.numberOfContours:
        pen = TTGlyphPen(None); pts_all = list(c)
        g2 = Glyph(); g2.numberOfContours = len(keep)
        coords, flags, ends = [], [], []
        for s, e in keep:
            coords += pts_all[s:e+1]; flags += list(fl[s:e+1]); ends.append(len(coords) - 1)
        g2.coordinates = GlyphCoordinates(coords); g2.flags = bytearray(flags); g2.endPtsOfContours = ends
        g2.program = g.program if hasattr(g, 'program') else None
        glyf[n] = g2; g2.recalcBounds(glyf); f['hmtx'][n] = (f['hmtx'][n][0], g2.xMin)
        print('contour vide enlevé :', n)
# 2. accents trop collés : on les écarte par petits pas
gr = ref.getGlyphSet()
def measure(n):
    gs = f.getGlyphSet(); a, ca = raster(gs, n); return ca, channels(a)
for n in f.getGlyphOrder():
    g = glyf[n]
    if not g.isComposite() or n in ACCEPTED or n not in ref.getGlyphOrder(): continue
    a, cref = raster(gr, n); wref = channels(a)
    cnew, wnew = measure(n)
    bad = lambda c, w: c != cref or (wref and w and w < 0.8 * wref and w < 120)
    if not bad(cnew, wnew): continue
    comps = g.components; base = comps[0]
    horn = [c for c in comps[1:] if c.glyphName.startswith('uni031B')]
    movers = horn if (horn and cnew != cref) else comps[1:]
    if not movers: continue
    bb = glyf[base.glyphName]; bb.recalcBounds(glyf); mid = (bb.yMin + bb.yMax) / 2 + base.y
    start = [(c.x, c.y) for c in movers]; done = False
    for step in range(1, 26):
        for c, (x0, y0) in zip(movers, start):
            if horn and cnew != cref: c.x = x0 - 4 * step                       # la corne se recolle à la lettre
            else:
                m = glyf[c.glyphName]; m.recalcBounds(glyf); cy = (m.yMin + m.yMax) / 2 + y0
                c.y = y0 + (4 * step if cy >= mid else -4 * step)            # au-dessus : on monte ; en dessous : on descend
        cn, wn = measure(n)
        if not bad(cn, wn): done = True; break
    if not done:
        for c, (x0, y0) in zip(movers, start): c.x, c.y = x0, y0
    g.recalcBounds(glyf)
    print(n, 'écarté de', 4 * step if done else 0, 'unités' if done else '(inchangé)', '| écart', wnew, '→', measure(n)[1], '(réf', wref, ')')
f.save(sys.argv[2])
