"""Solve the y-extrapolation factor for many glyphs (gap >= 80 % of the Black's)."""
import sys, json, io, copy
fam = open(sys.argv[3]).read(); exec(fam[:fam.index("report = {}")])
chk = open(sys.argv[4]).read(); exec(chk[:chk.index("ref, new = TTFont")])
import pathops, os
TMAX = float(os.environ.get("TMAX", "1.0"))
todo, WX, K, out = json.load(open(sys.argv[5])), float(sys.argv[6]), float(sys.argv[7]), sys.argv[8]
A, f9, f8 = XSource(WX), inst(900), inst(800)

def gap_for(glyph, T):
    g9, g8 = f9["glyf"][glyph], f8["glyf"][glyph]
    g = copy.deepcopy(g9)
    g.coordinates = GlyphCoordinates([(round(xa * K), round(y9 + T * (y9 - y8)))
        for xa, (_, y9), (_, y8) in zip(A.coords(glyph), g9.coordinates, g8.coordinates)])
    p = pathops.Path(); g.draw(p.getPen(), f9["glyf"]); p.simplify()
    class G:
        def __getitem__(s, n): return s
        def draw(s, pen): p.draw(pen)
    ink, _ = raster(G(), glyph)
    return channels(ink)

res = {}
for glyph, ref in todo:
    g9 = f9["glyf"][glyph]
    if g9.numberOfContours <= 0:
        res[glyph] = {"skip": "composite"}; continue
    target = 0.8 * ref
    if gap_for(glyph, TMAX) >= target: res[glyph] = {"T": TMAX}; continue
    lo, hi = 0.0, TMAX
    for _ in range(12):
        m = (lo + hi) / 2
        if gap_for(glyph, m) >= target: lo = m
        else: hi = m
    res[glyph] = {"T": round(lo, 3), "before": gap_for(glyph, TMAX), "after": gap_for(glyph, lo), "target": round(target)}
    print(glyph, res[glyph], flush=True)
json.dump(res, open(out, "w"), indent=1)
