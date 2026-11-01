
# ---- L–A optical spacing (appended to the logo build) ----
from fontTools.pens.basePen import BasePen
import statistics, re


class FlattenPen(BasePen):
    """Collects contours as polylines (curves sampled)."""
    def __init__(self):
        super().__init__(None); self.contours = []; self.cur = []
    def _moveTo(self, p): self.cur = [p]
    def _lineTo(self, p): self.cur.append(p)
    def _qCurveToOne(self, p1, p2):
        p0 = self.cur[-1]
        for i in range(1, 17):
            t = i / 16; a = (1 - t) ** 2; b = 2 * (1 - t) * t; c = t * t
            self.cur.append((a*p0[0]+b*p1[0]+c*p2[0], a*p0[1]+b*p1[1]+c*p2[1]))
    def _curveToOne(self, p1, p2, p3):
        p0 = self.cur[-1]
        for i in range(1, 17):
            t = i / 16; m = 1 - t
            self.cur.append((m**3*p0[0]+3*m*m*t*p1[0]+3*m*t*t*p2[0]+t**3*p3[0],
                             m**3*p0[1]+3*m*m*t*p1[1]+3*m*t*t*p2[1]+t**3*p3[1]))
    def _closePath(self):
        if self.cur: self.contours.append(self.cur); self.cur = []
    _endPath = _closePath


def profile(gpath, rows):
    fp = FlattenPen(); gpath.draw(fp)
    edges = [(c[i], c[(i+1) % len(c)]) for c in fp.contours for i in range(len(c))]
    out = []
    for y in rows:
        xs = [x0 + (y - y0) * (x1 - x0) / (y1 - y0)
              for (x0, y0), (x1, y1) in edges if (y0 <= y < y1) or (y1 <= y < y0)]
        out.append((min(xs), max(xs)) if xs else None)
    return out


bp = BoundsPen(B.getGlyphSet()); B.getGlyphSet()["I"].draw(bp)
cap = bp.bounds[3]
rows = [y + 2 for y in range(0, int(cap), 4)]
depth = 0.15 * cap * scale  # how deep an opening is allowed to count

glyphs = []
build(A, B, A_run, scale, shifts=[0] * len(A_run), per_glyph=glyphs)
profs = [profile(g, rows) for g in glyphs]


def pair_gaps(i):
    L, R = profs[i], profs[i + 1]
    rmax = max(p[1] for p in L if p); lmin = min(p[0] for p in R if p)
    gaps = []
    for a, b in zip(L, R):
        if not a or not b: continue
        right = max(a[1], rmax - depth); left = min(b[0], lmin + depth)
        gaps.append(left - right)
    return gaps


areas = [sum(pair_gaps(i)) for i in range(len(glyphs) - 1)]
min_gaps = [min(pair_gaps(i)) for i in range(len(glyphs) - 1)]
target = statistics.median(areas[1:])
delta = (areas[0] - target) / len(pair_gaps(0))
floor = 0.4 * statistics.median(min_gaps[1:])          # never let the A foot crowd the L bar
delta = min(delta, min_gaps[0] - floor)
delta = max(delta, 0)

shifts = [0] + [-delta] * (len(A_run) - 1)
final = build(A, B, A_run, scale, shifts=shifts, per_glyph=[])

for key, fill in [("lafleurstudio-130-noir", "#000000"), ("lafleurstudio-130-blanc", "#FFFFFF")]:
    svg, (w, h) = to_svg(final, fill, "LaFleurStudio")
    svg = re.sub(r'width="[\d.]+" height="[\d.]+"', f'width="2000" height="{2000*h/w:.1f}"', svg, count=1)
    open(f"{OUT_DIR}/{key}.svg", "w").write(svg)

print(json.dumps({
    "pair_areas": [round(a) for a in areas],
    "LA_area": round(areas[0]), "target_median": round(target),
    "LA_min_gap_before": round(min_gaps[0]), "median_min_gap_others": round(statistics.median(min_gaps[1:])),
    "shift_applied": round(delta, 1), "LA_min_gap_after": round(min_gaps[0] - delta),
}, indent=1))
