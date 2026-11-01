"""Round the two corners where the 5's slit meets its counter (option 2 chosen on the 1000).
Works on TrueType quadratic outlines with explicit or implied on-curve points."""
import sys
from fontTools.ttLib import TTFont
F1, F2 = 68 / 487, 228 / 487

def analyse(g):
    c, fl = [tuple(p) for p in g.coordinates], g.flags
    on = lambda i: fl[i] & 1; n = len(c); res = {}
    for i in range(1, n - 3):
        # top corner: horizontal edge (i-1 -> i) then off-curve going straight up
        if on(i) and on(i-1) and c[i-1][1] == c[i][1] and c[i-1][0] < c[i][0] and not on(i+1) and not on(i+2) \
           and abs(c[i+1][0] - c[i][0]) < 40 and c[i+1][1] > c[i][1]:
            end = c[i+3] if on(i+3) else ((c[i+2][0] + c[i+3][0]) / 2, (c[i+2][1] + c[i+3][1]) / 2)
            if abs(end[1] - c[i+2][1]) < 1: res["top"] = (i, end)
        # bottom corner: off-curve coming straight up into on-curve k, then horizontal edge to the left
        k = i + 2
        if k + 1 < n and on(k) and on(k+1) and c[k+1][1] == c[k][1] and c[k+1][0] < c[k][0] and not on(k-1) and not on(k-2) \
           and abs(c[k-1][0] - c[k][0]) < 40 and c[k-1][1] < c[k][1]:
            end = c[k-3] if on(k-3) else ((c[k-3][0] + c[k-2][0]) / 2, (c[k-3][1] + c[k-2][1]) / 2)
            if abs(end[1] - c[k-2][1]) < 1: res["bot"] = (k, end)
    return res

def apply(g, res):
    c = g.coordinates
    i, (ex, ey) = res["top"]; xj, yt = c[i]; span = ex - xj
    c[i+1] = (round(xj + F1 * span), yt); c[i+2] = (round(xj + F2 * span), round(ey))
    k, (ex, ey) = res["bot"]; xj, ys = c[k]; span = ex - xj
    c[k-1] = (round(xj + F1 * span), ys); c[k-2] = (round(xj + F2 * span), round(ey))

if __name__ == "__main__":
    for path in sys.argv[1:]:
        f = TTFont(path); g = f["glyf"]["five"]; res = analyse(g)
        info = {k: (tuple(g.coordinates[v[0]]), tuple(round(z) for z in v[1])) for k, v in res.items()}
        print(path.split("/")[-1], info)
