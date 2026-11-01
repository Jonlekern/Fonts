"""Step 2: find characters that break in the 1000 (vs the validated Black 900).
For every encoded glyph: rasterize, measure white channels (gaps between strokes:
counters, slits like E's arms, apertures like S) column by column and row by row,
take the median width of each channel, keep the narrowest one per glyph.
Also flags contour-count changes (holes closed / shapes merged)."""
import sys, json
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen

U = 4  # font units per pixel


class Poly(BasePen):
    def __init__(self, gs):
        super().__init__(gs); self.contours = []; self.cur = []
    def _moveTo(self, p): self.cur = [p]
    def _lineTo(self, p): self.cur.append(p)
    def _qCurveToOne(self, p1, p2):
        p0 = self.cur[-1]
        for i in range(1, 9):
            t = i / 8; self.cur.append(tuple((1-t)**2*p0[j]+2*(1-t)*t*p1[j]+t*t*p2[j] for j in (0, 1)))
    def _curveToOne(self, p1, p2, p3):
        p0 = self.cur[-1]
        for i in range(1, 9):
            t = i / 8; m = 1 - t
            self.cur.append(tuple(m**3*p0[j]+3*m*m*t*p1[j]+3*m*t*t*p2[j]+t**3*p3[j] for j in (0, 1)))
    def _closePath(self):
        if len(self.cur) > 2: self.contours.append(self.cur)
        self.cur = []
    _endPath = _closePath


def raster(gs, name):
    pp = Poly(gs); gs[name].draw(pp)
    if not pp.contours: return None, 0
    xs = [x for c in pp.contours for x, _ in c]; ys = [y for c in pp.contours for _, y in c]
    x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
    w, h = int((x1 - x0) / U) + 3, int((y1 - y0) / U) + 3
    acc = np.zeros((h, w), bool)
    for c in pp.contours:
        im = Image.new("1", (w, h), 0)
        ImageDraw.Draw(im).polygon([((x - x0) / U + 1, (y1 - y) / U + 1) for x, y in c], fill=1)
        acc ^= np.array(im, bool)   # even-odd (overlaps already removed)
    return acc, len(pp.contours)


def channels(ink):
    """median width (font units) of the narrowest white channel bounded by ink on both sides."""
    best = None
    for arr in (ink, ink.T):                       # columns -> vertical gaps, then rows -> horizontal gaps
        h, w = arr.shape
        gapmask = np.zeros_like(arr)
        for x in range(w):
            col = arr[:, x]; idx = np.flatnonzero(col)
            if len(idx) < 2: continue
            seg = ~col[idx[0]:idx[-1] + 1]          # white strictly between first and last ink
            gapmask[idx[0]:idx[-1] + 1, x] = seg
        lab, n = ndimage.label(gapmask)
        for i in range(1, n + 1):
            m = lab == i
            cols = np.flatnonzero(m.any(axis=0))
            if len(cols) * U < 60: continue           # ignore tiny notches
            widths = m.sum(axis=0)[cols] * U
            med = float(np.median(widths))
            if best is None or med < best: best = med
    return best


ref, new = TTFont(sys.argv[1]), TTFont(sys.argv[2])
gr, gn = ref.getGlyphSet(), new.getGlyphSet()
cmap = new.getBestCmap()
by_glyph = {}
for cp, g in sorted(cmap.items()):
    by_glyph.setdefault(g, []).append(cp)

rows = []
for g, cps in by_glyph.items():
    a, ca = raster(gr, g); b, cb = raster(gn, g)
    if a is None or b is None: continue
    wa, wb = channels(a), channels(b)
    rows.append({"g": g, "char": "".join(chr(c) for c in cps), "ref": wa, "new": wb,
                 "ratio": (wb / wa) if (wa and wb) else None, "contours": (ca, cb)})

json.dump(rows, open(sys.argv[3], "w"))
topo = [r for r in rows if r["contours"][0] != r["contours"][1]]
print("glyphs checked:", len(rows), "| contour count changed:", [(r["char"], r["contours"]) for r in topo][:40])
vals = sorted([r for r in rows if r["new"] is not None], key=lambda r: r["new"])
print("narrowest channels in 1000 (units, ref 900 -> 1000):")
for r in vals[:60]:
    print(f'  {r["char"]!r:6} {r["g"]:14} {r["ref"]:6.0f} -> {r["new"]:5.0f}  ({r["ratio"]:.2f})' if r["ref"] else f'  {r["char"]!r} {r["g"]} new {r["new"]}')
