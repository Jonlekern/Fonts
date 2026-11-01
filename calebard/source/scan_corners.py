"""Find "5-like" corners: a sharp ink corner where a horizontal straight edge (one side of a
narrow slit) meets a curve leaving vertically away from the slit, into a bigger counter."""
import sys, json
from fontTools.ttLib import TTFont
from fontTools.pens.pointInsidePen import PointInsidePen

SLIT_MAX = 260   # font units: max slit height to count as a "slit"


def inside(gs, name, x, y):
    p = PointInsidePen(gs, (x, y)); gs[name].draw(p); return p.getResult()


def corners(font, name):
    gs = font.getGlyphSet(); g = font["glyf"][name]
    if g.numberOfContours <= 0: return []
    c, fl, ends = [tuple(p) for p in g.coordinates], g.flags, g.endPtsOfContours
    found, start = [], 0
    for end in ends:
        idx = list(range(start, end + 1)); n = len(idx)
        for k, i in enumerate(idx):
            if not fl[i] & 1: continue
            a, b = idx[k - 1], idx[(k + 1) % n]
            for edge, curve in ((a, b), (b, a)):
                if not (fl[edge] & 1 and c[edge][1] == c[i][1] and c[edge][0] != c[i][0]): continue
                if fl[curve] & 1: continue
                dx, dy = c[curve][0] - c[i][0], c[curve][1] - c[i][1]
                if dy == 0 or abs(dx) > 0.25 * abs(dy): continue
                x, y = c[i]; ex = 1 if c[edge][0] > x else -1          # edge lies on this side of P
                q = [inside(gs, name, x + sx * 6, y + sy * 6) for sx, sy in ((1, 1), (-1, 1), (-1, -1), (1, -1))]
                if sum(q) != 1: continue                                  # convex ink corner only
                cy = 1 if dy > 0 else -1                                  # curve leaves up (+1) or down (-1)
                wy = -cy                                                  # slit must be on the other side
                px = x + ex * 30
                if inside(gs, name, px, y + wy * 6): continue             # white side check
                d = next((s for s in range(8, SLIT_MAX + 1, 4) if inside(gs, name, px, y + wy * s)), None)
                if d is None: continue
                # the curve must lead into a counter (closed in), not to the glyph's outside
                qx, qy = x - ex * 20, y + cy * 20
                if inside(gs, name, qx, qy): continue
                if not any(inside(gs, name, qx - ex * s_, qy) for s_ in range(20, 3000, 20)): continue
                found.append({"pt": i, "xy": [x, y], "slit": d, "dir": "up" if cy > 0 else "down"})
        start = end + 1
    return found


out = {}
for path in sys.argv[2:]:
    f = TTFont(path); cmap = {v: chr(k) for k, v in f.getBestCmap().items()}
    res = {}
    for name in f.getGlyphOrder():
        cs = corners(f, name)
        if cs: res[name] = {"char": cmap.get(name, ""), "corners": cs}
    out[path.split("/")[-1]] = res
    print(path.split("/")[-1], len(res), "glyphs:", " ".join(v["char"] or k for k, v in res.items()))
json.dump(out, open(sys.argv[1], "w"), indent=1)
