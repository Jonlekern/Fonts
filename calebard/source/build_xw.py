"""Step 1: automatic weight 1000 for Calebard.
y data = Anybody extrapolated past 900 (linear, from the 800->900 segment),
x data = a real lighter instance, scaled, so stretched stems match the 1000 stems."""
import sys, io, copy, os
src = open(sys.argv[3]).read()
exec(src[:src.index("report = {}")])          # reuse the family build helpers

T = float(os.environ.get("XT", "1.0"))  # 1000 = 900 + 1.0 * (900 - 800); 1100 -> 2.0
import json, os
OVR = json.load(open(sys.argv[4])) if len(sys.argv) > 4 and os.path.exists(sys.argv[4]) else {}

def extrapolated_1000():
    a, b = inst(900), inst(800)
    ga, gb = a["glyf"], b["glyf"]
    for n in a.getGlyphOrder():
        g, h = ga[n], gb[n]
        if g.numberOfContours > 0:
            Tg = OVR.get(n, T)   # per-glyph override: thinner horizontals only (y)
            g.coordinates = GlyphCoordinates([(round(x9 + T * (x9 - x8)), round(y9 + Tg * (y9 - y8)))
                                              for (x9, y9), (x8, y8) in zip(g.coordinates, h.coordinates)])
        elif g.numberOfContours < 0:
            dys = OVR.get("_comp", {}).get(n, {})   # per-glyph component nudges (font units, y)
            for i, (c9, c8) in enumerate(zip(g.components, h.components)):
                c9.x, c9.y = round(c9.x + T * (c9.x - c8.x)), round(c9.y + T * (c9.y - c8.y)) + int(dys.get(str(i), 0))
        a["hmtx"][n] = (round(a["hmtx"][n][0] + T * (a["hmtx"][n][0] - b["hmtx"][n][0])), a["hmtx"][n][1])
    buf = io.BytesIO(); a.save(buf); return buf.getvalue()

_orig_comp_x = XSource.comp_x
def _comp_x(self, n):   # per-glyph component nudges (font units, x, final scale)
    d = OVR.get("_compx", {}).get(n, {})
    return [x + d.get(str(i), 0) / k for i, x in enumerate(_orig_comp_x(self, n))]
XSource.comp_x = _comp_x
Y_BYTES = extrapolated_1000()
Y = TTFont(io.BytesIO(Y_BYTES))
stem_1000, width_1000 = stem_of(Y), run_width(Y_BYTES)

# solve x-source weight
target_w = STRETCH * width_1000
lo, hi = 100.0, 900.0
for _ in range(20):
    m = (lo + hi) / 2; s = XSource(m)
    if s.stem() * target_w / s.width() > stem_1000: hi = m
    else: lo = m
wx = round((lo + hi) / 2, 1); k = target_w / XSource(wx).width()

# same build as the family, with the extrapolated font as y source
inst_orig = inst
inst = lambda w: TTFont(io.BytesIO(Y_BYTES)) if w == 1000 else inst_orig(w)
F = make(1000, wx, k)
stem_after = stem_of(F)
la = optical_la(F, k); add_la(F, la); set_names(F, 1000, "W1000")
F["OS/2"].usWeightClass = 1000
# hand edits on final outlines: {glyph: {point: [old_x, old_y, new_x, new_y]}}
for gname, pts in OVR.get("_final_pts", {}).items():
    gl = F["glyf"][gname]
    for i, (ox, oy, nx, ny) in pts.items():
        assert tuple(gl.coordinates[int(i)]) == (ox, oy), (gname, i, gl.coordinates[int(i)])
        gl.coordinates[int(i)] = (nx, ny)
    gl.recalcBounds(F["glyf"])
F.save(f"{sys.argv[2]}/Calebard-{os.environ.get('XNAME', 'W1000')}.ttf")
print({"stem_900": stem(900), "stem_1000_target": stem_1000, "stem_result": stem_after,
       "x_source": wx, "x_scale": round(k, 4), "LA": la})
