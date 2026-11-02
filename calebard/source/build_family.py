"""Calebard family (Thin..Black): Anybody (OFL) at width 150, extended to 130 %,
stroke contrast rebalanced per weight (x from a lighter weight, y from the target
weight), optical L–A spacing. Black keeps the exact validated parameters."""
import io, sys, copy, functools, statistics, json
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates
from fontTools.ttLib.tables import ttProgram
from fontTools.otlLib.builder import buildPairPosGlyphsSubtable, buildLookup, buildValue
from fontTools.ttLib.removeOverlaps import removeOverlaps
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.basePen import BasePen
import uharfbuzz as hb

VF, OUT = sys.argv[1], sys.argv[2]
import os
FAMILY, TEXT, STRETCH = "Calebard", "LAFLEURSTUDIO", float(os.environ.get("STRETCH", "1.209"))
WEIGHTS = {100: "Thin", 200: "ExtraLight", 300: "Light", 400: "Regular", 500: "Medium",
           600: "SemiBold", 700: "Bold", 800: "ExtraBold", 900: "Black"}
FIXED = {900: (704.7, 1.3342, -172.6)} if STRETCH == 1.30 else {}   # validated logo parameters (130 %)


@functools.lru_cache(None)
def inst_bytes(w):
    f = instantiateVariableFont(TTFont(VF), {"wght": w, "wdth": 150})
    b = io.BytesIO(); f.save(b); return b.getvalue()

def inst(w): return TTFont(io.BytesIO(inst_bytes(w)))


def run_width(data):
    font = hb.Font(hb.Face(data)); b = hb.Buffer(); b.add_str(TEXT); b.guess_segment_properties()
    hb.shape(font, b, {"kern": True}); return sum(p.x_advance for p in b.glyph_positions)

def stem_of(font):
    bp = BoundsPen(font.getGlyphSet()); font.getGlyphSet()["I"].draw(bp); return bp.bounds[2] - bp.bounds[0]

@functools.lru_cache(None)
def stem(w): return stem_of(inst(w))
@functools.lru_cache(None)
def width(w): return run_width(inst_bytes(w))


class XSource:
    """x data at weight wx; below the axis minimum (100) it is linearly extrapolated from 100 and 200."""
    def __init__(self, wx):
        self.wx = wx
        if wx >= 100:
            self.f = inst(wx); self.g = None; self.t = 0
        else:
            self.f = inst(100); self.g = inst(200); self.t = (100 - wx) / 100
    def _ex(self, a, b): return a + self.t * (a - b)
    def coords(self, n):
        ca = self.f["glyf"][n].coordinates
        if not self.g: return [x for x, _ in ca]
        return [self._ex(xa, xb) for (xa, _), (xb, _) in zip(ca, self.g["glyf"][n].coordinates)]
    def comp_x(self, n):
        ca = self.f["glyf"][n].components
        if not self.g: return [c.x for c in ca]
        return [self._ex(a.x, b.x) for a, b in zip(ca, self.g["glyf"][n].components)]
    def adv(self, n):
        a = self.f["hmtx"][n][0]
        return a if not self.g else self._ex(a, self.g["hmtx"][n][0])
    def stem(self):
        return stem(self.wx) if not self.g else self._ex(stem(100), stem(200))
    def width(self):
        return width(self.wx) if not self.g else self._ex(width(100), width(200))
    def gpos(self): return copy.deepcopy(self.f["GPOS"])


def solve(W):
    target_w = STRETCH * width(W)
    eff = lambda wx: (lambda s: s.stem() * target_w / s.width())(XSource(wx))
    lo, hi = 50.0, float(W)
    for _ in range(20):
        m = (lo + hi) / 2
        if eff(m) > stem(W): hi = m
        else: lo = m
    wx = round((lo + hi) / 2, 1); s = XSource(wx)
    return wx, target_w / s.width()


def scale_x(o, k, seen):
    if o is None or isinstance(o, (int, float, str, bytes)) or id(o) in seen: return
    seen.add(id(o))
    if isinstance(o, (list, tuple)):
        for i in o: scale_x(i, k, seen)
        return
    if isinstance(o, dict):
        for i in o.values(): scale_x(i, k, seen)
        return
    for a, v in list(getattr(o, "__dict__", {}).items()):
        if a in ("XAdvance", "XPlacement", "XCoordinate") and isinstance(v, (int, float)):
            setattr(o, a, round(v * k))
        else:
            scale_x(v, k, seen)


def make(W, wx, k):
    X, F = XSource(wx), inst(W)
    gf = F["glyf"]; order = F.getGlyphOrder()
    for n in order:
        f = gf[n]
        if f.numberOfContours > 0:
            xs = X.coords(n); assert len(xs) == len(f.coordinates), n
            f.coordinates = GlyphCoordinates([(round(x * k), y) for x, (_, y) in zip(xs, f.coordinates)])
        elif f.numberOfContours < 0:
            for c, x in zip(f.components, X.comp_x(n)): c.x = round(x * k)
        if hasattr(f, "program"):
            f.program = ttProgram.Program(); f.program.fromBytecode(b"")
    for n in order:
        g = gf[n]; g.recalcBounds(gf)
        F["hmtx"][n] = (round(X.adv(n) * k), getattr(g, "xMin", 0) if g.numberOfContours else 0)
    F["GPOS"] = X.gpos(); scale_x(F["GPOS"].table, k, set())
    for t in ("fpgm", "prep", "cvt ", "hdmx", "LTSH", "VDMX", "kern", "STAT"):
        if t in F: del F[t]
    removeOverlaps(F)
    return F


class FlattenPen(BasePen):
    def __init__(self): super().__init__(None); self.contours = []; self.cur = []
    def _moveTo(self, p): self.cur = [p]
    def _lineTo(self, p): self.cur.append(p)
    def _qCurveToOne(self, p1, p2):
        p0 = self.cur[-1]
        for i in range(1, 17):
            t = i / 16; self.cur.append(((1-t)**2*p0[0]+2*(1-t)*t*p1[0]+t*t*p2[0], (1-t)**2*p0[1]+2*(1-t)*t*p1[1]+t*t*p2[1]))
    def _curveToOne(self, p1, p2, p3):
        p0 = self.cur[-1]
        for i in range(1, 17):
            t = i / 16; m = 1 - t
            self.cur.append(tuple(m**3*p0[j]+3*m*m*t*p1[j]+3*m*t*t*p2[j]+t**3*p3[j] for j in (0, 1)))
    def _closePath(self):
        if self.cur: self.contours.append(self.cur); self.cur = []
    _endPath = _closePath


def optical_la(F, k):
    b = io.BytesIO(); F.save(b); data = b.getvalue(); F2 = TTFont(io.BytesIO(data))
    font = hb.Font(hb.Face(data)); buf = hb.Buffer(); buf.add_str(TEXT); buf.guess_segment_properties()
    hb.shape(font, buf, {"kern": True})
    gs, order = F2.getGlyphSet(), F2.getGlyphOrder()
    cap = (lambda bp: (gs["I"].draw(bp), bp.bounds[3])[1])(BoundsPen(gs))
    rows = [y + 2 for y in range(0, int(cap), 4)]; depth = 0.15 * cap * k
    profs, x = [], 0
    for i, p in zip(buf.glyph_infos, buf.glyph_positions):
        fp = FlattenPen(); gs[order[i.codepoint]].draw(TransformPen(fp, (1, 0, 0, 1, x + p.x_offset, 0)))
        edges = [(c[j], c[(j+1) % len(c)]) for c in fp.contours for j in range(len(c))]
        prof = []
        for y in rows:
            xs = [x0+(y-y0)*(x1-x0)/(y1-y0) for (x0, y0), (x1, y1) in edges if (y0 <= y < y1) or (y1 <= y < y0)]
            prof.append((min(xs), max(xs)) if xs else None)
        profs.append(prof); x += p.x_advance
    def gaps(i):
        L, R = profs[i], profs[i+1]
        rmax = max(q[1] for q in L if q); lmin = min(q[0] for q in R if q)
        return [min(b_[0], lmin+depth) - max(a[1], rmax-depth) for a, b_ in zip(L, R) if a and b_]
    areas = [sum(gaps(i)) for i in range(len(profs)-1)]
    mins = [min(gaps(i)) for i in range(len(profs)-1)]
    delta = (areas[0] - statistics.median(areas[1:])) / len(gaps(0))
    delta = max(0, min(delta, mins[0] - 0.4 * statistics.median(mins[1:])))
    return -round(delta, 1)


def add_la(F, shift):
    gpos = F["GPOS"].table
    st = buildPairPosGlyphsSubtable({("L", "A"): (buildValue({"XAdvance": round(shift)}), None)}, F.getReverseGlyphMap())
    gpos.LookupList.Lookup.append(buildLookup([st])); gpos.LookupList.LookupCount = len(gpos.LookupList.Lookup)
    idx = gpos.LookupList.LookupCount - 1; n = 0
    for fr in gpos.FeatureList.FeatureRecord:
        if fr.FeatureTag == "kern": fr.Feature.LookupListIndex.append(idx); fr.Feature.LookupCount += 1; n += 1
    assert n


def set_names(F, W, style):
    nm = F["name"]; cp = TTFont(VF)["name"].getDebugName(0)
    ribbi = style in ("Regular", "Bold")
    fam1 = FAMILY if ribbi else f"{FAMILY} {style}"
    vals = {0: cp + ". Modifications (Calebard) 2026 LaFleurStudio.",
            1: fam1, 2: style if ribbi else "Regular", 3: f"1.000;{FAMILY}-{style}",
            4: f"{FAMILY} {style}", 6: f"{FAMILY}-{style}", 16: FAMILY, 17: style,
            10: "Calebard is a modified version of Anybody (SIL Open Font License 1.1).",
            8: "LaFleurStudio", 9: "LaFleurStudio, based on Anybody by Tyler Finck (Etcetera Type Co.)", 11: "https://jonlekern.github.io/Fonts/"}
    nm.names = [r for r in nm.names if r.nameID not in (1, 2, 3, 4, 6, 8, 9, 11, 12, 16, 17, 25)]
    for i, v in vals.items():
        nm.setName(v, i, 3, 1, 0x409); nm.setName(v, i, 1, 0, 0)
    os2 = F["OS/2"]
    os2.usWeightClass, os2.usWidthClass = W, 9
    os2.achVendID = 'LFST'
    os2.fsSelection &= ~((1 << 0) | (1 << 5) | (1 << 6))
    os2.fsSelection |= (1 << 5) if style == "Bold" else (1 << 6)
    F["head"].macStyle = 1 if style == "Bold" else 0
    os2.recalcAvgCharWidth(F)


report = {}
for W, style in WEIGHTS.items():
    if W in FIXED: wx, k, la = FIXED[W]
    else: (wx, k), la = solve(W), None
    F = make(W, wx, k)
    stem_after = stem_of(F)
    if la is None: la = optical_la(F, k)
    add_la(F, la); set_names(F, W, style)
    F.save(f"{OUT}/{FAMILY}-{style}.ttf")
    report[style] = {"x_source": wx, "x_scale": round(k, 4), "stem_target": stem(W),
                     "stem_naive": round(stem(W) * STRETCH), "stem_result": stem_after, "LA": la}
    print(style, report[style], flush=True)
