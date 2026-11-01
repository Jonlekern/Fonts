"""Compare every glyph (encoded or not) of the 1000 with the Black; list gaps below the rule:
gap_1000 < 0.8 * gap_black and gap_1000 < 120 units, or contour-count change."""
import sys, json
chk = open(sys.argv[4]).read(); exec(chk[:chk.index("ref, new = TTFont")])
ref, new, src = TTFont(sys.argv[1]), TTFont(sys.argv[2]), TTFont(sys.argv[5])
gr, gn = ref.getGlyphSet(), new.getGlyphSet()
cmap = {v: chr(k) for k, v in new.getBestCmap().items()}
out = []
for g in new.getGlyphOrder():
    a, ca = raster(gr, g); b, cb = raster(gn, g)
    if a is None or b is None: continue
    wa, wb = channels(a), channels(b)
    bad = (ca != cb) or (wa and wb and wb < 0.8 * wa and wb < 120)
    if bad:
        out.append({"g": g, "char": cmap.get(g, ""), "ref": wa, "new": wb, "contours": [ca, cb],
                    "simple": src["glyf"][g].numberOfContours > 0})
json.dump(out, open(sys.argv[3], "w"), indent=1)
print(len(out), "flagged:", " ".join(f'{o["g"]}{"" if o["simple"] else "*"}' for o in out))
