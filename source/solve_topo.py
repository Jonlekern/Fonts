"""Max y-extrapolation T keeping the reference contour count and gap >= 80 % (+10) of the reference."""
import sys, json, copy, os
fam = open(sys.argv[3]).read(); exec(fam[:fam.index("report = {}")])
chk = open(sys.argv[4]).read(); exec(chk[:chk.index("ref, new = TTFont")])
import pathops
todo, WX, K, out, TMAX = json.load(open(sys.argv[5])), float(sys.argv[6]), float(sys.argv[7]), sys.argv[8], float(sys.argv[9])
A, f9, f8 = XSource(WX), inst(900), inst(800)
def measure(glyph, T):
    g9, g8 = f9["glyf"][glyph], f8["glyf"][glyph]; g = copy.deepcopy(g9)
    g.coordinates = GlyphCoordinates([(round(xa * K), round(y9 + T * (y9 - y8)))
        for xa, (_, y9), (_, y8) in zip(A.coords(glyph), g9.coordinates, g8.coordinates)])
    p = pathops.Path(); g.draw(p.getPen(), f9["glyf"]); p.simplify()
    ncont = sum(1 for _ in p.contours)
    class G:
        def __getitem__(s, n): return s
        def draw(s, pen): p.draw(pen)
    ink, _ = raster(G(), glyph); return ncont, channels(ink)
res = {}
for glyph, ref_gap, ref_cont in todo:
    ok = lambda T: (lambda m: m[0] == ref_cont and (m[1] or 1e9) >= 0.8 * ref_gap + 10)(measure(glyph, T))
    if not ok(0.0): res[glyph] = {"fail": measure(glyph, 0.0)}; print(glyph, res[glyph]); continue
    lo, hi = 0.0, TMAX
    for _ in range(12):
        m = (lo + hi) / 2
        if ok(m): lo = m
        else: hi = m
    res[glyph] = {"T": round(lo, 3), "m": measure(glyph, lo)}; print(glyph, res[glyph], flush=True)
json.dump(res, open(out, "w"), indent=1)
