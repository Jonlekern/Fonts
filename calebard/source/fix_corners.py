"""Apply the 5's rounding (option 2) to every detected slit corner of a font.
usage: fix_corners.py in.ttf out.ttf report.json"""
import sys, json
from fontTools.ttLib import TTFont
exec(open(__file__.replace("fix_corners.py", "scan_corners.py")).read().split("out = {}")[0])
F1, F2 = 68 / 487, 228 / 487

src, dst, rep = sys.argv[1:4]
f = TTFont(src); glyf = f["glyf"]; changed = {}
for name in f.getGlyphOrder():
    found = corners(f, name)
    if not found: continue
    g = glyf[name]; c = g.coordinates; fl = g.flags; ends = g.endPtsOfContours
    done = []
    for cr in found:
        i = cr["pt"]
        start = 0
        for e in ends:
            if i <= e: break
            start = e + 1
        idx = list(range(start, e + 1)); n = len(idx); k = idx.index(i)
        nxt = lambda s: idx[(k + s) % n]
        # which side is the curve? (the off-curve neighbour that leaves vertically)
        for step in (1, -1):
            a = nxt(step)
            if not fl[a] & 1 and abs(c[a][0] - c[i][0]) <= 0.25 * abs(c[a][1] - c[i][1]): break
        else:
            continue
        b, after = nxt(2 * step), nxt(3 * step)
        if fl[b] & 1: continue                                   # need two off-curves (like the 5)
        end = c[after] if fl[after] & 1 else ((c[b][0] + c[after][0]) / 2, (c[b][1] + c[after][1]) / 2)
        if abs(end[1] - c[b][1]) > 1: continue                   # extremum must be horizontal
        xj, yj = c[i]; span = end[0] - xj
        if abs(span) < 60: continue
        c[a] = (round(xj + F1 * span), yj)
        c[b] = (round(xj + F2 * span), c[b][1])
        done.append(cr["xy"])
    if done:
        g.recalcBounds(glyf); changed[name] = done
f.save(dst)
json.dump(changed, open(rep, "w"))
print(src.split("/")[-1], len(changed), "glyphs:", " ".join(changed))
