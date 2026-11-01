"""Falsard: builds the 10 static fonts (XXXS 200 -> XXXXL 1100) from Orbitron (SIL OFL 1.1).

Recipe, per weight W:
  1. Vertical bands (red construction lines). Capitals, figures and signs:
       0-157 x1.2 (bottom thickened) | 157-439 x1.0 | 439-720 x0.5 (top compressed)
     lowercase and small caps use the same bands set on the lowercase s: 0-153 | 153-367 | 367-580.
  2. Widened to 110 % without deforming: the x coordinates come from a lighter weight so the
     stretched vertical strokes keep exactly the thickness of weight W.
  3. S, s (and S caron, s caron, small cap s, $): head and tail removed.
  4. Weights outside Orbitron's 400-900 axis are extrapolated: below 400 with the 500->400 step,
     above 900 with twice the 800->900 step (1000: strokes 173, 1100: strokes 193).
  5. Added: (c) (R) (tm) drawn with Falsard's own O, C, R, T, M.

usage: build_falsard.py Orbitron-VF.ttf out_dir
"""
import sys, os, io, functools, unicodedata
import pathops
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.recordingPen import DecomposingRecordingPen, RecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.pointInsidePen import PointInsidePen
from fontTools.pens.areaPen import AreaPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen

VF = sys.argv[1] if len(sys.argv) > 1 else "Orbitron-VF.ttf"
OUT = sys.argv[2] if len(sys.argv) > 2 else "out"
WIDEN = 1.1
STYLES = [(200, "XXXS"), (300, "XXS"), (400, "XS"), (500, "S"), (600, "M"),
          (700, "L"), (800, "XL"), (900, "XXL"), (1000, "XXXL"), (1100, "XXXXL")]

# ---------------------------------------------------------------- instances (with extrapolation)
@functools.lru_cache(None)
def inst(w):
    """static Orbitron at weight w; outside 400-900 extrapolated, keeping straight what is straight"""
    if 400 <= w <= 900:
        f = instantiateVariableFont(TTFont(VF), {"wght": w}); b = io.BytesIO(); f.save(b); d = b.getvalue()
        return TTFont(io.BytesIO(d)), d
    if w > 900: t = 2 * (w - 900) / 100; ea, eb = 900, 800
    else:       t = (400 - w) / 100;     ea, eb = 400, 500
    a, _ = inst(ea); b, _ = inst(eb); f = TTFont(io.BytesIO(inst(ea)[1]))
    for n in f.getGlyphOrder():
        ga, gb, g = a["glyf"][n], b["glyf"][n], f["glyf"][n]
        if g.isComposite():
            for c, ca, cb in zip(g.components, ga.components, gb.components):
                c.x = round(ca.x + t * (ca.x - cb.x)); c.y = round(ca.y + t * (ca.y - cb.y))
        elif g.numberOfContours > 0:
            ca, cb = ga.coordinates, gb.coordinates
            pts = [[ca[i][0] + t * (ca[i][0] - cb[i][0]), ca[i][1] + t * (ca[i][1] - cb[i][1])] for i in range(len(ca))]
            start = 0
            for end in ga.endPtsOfContours:          # straight edges of the master stay straight
                idx = list(range(start, end + 1)); start = end + 1
                for ax in (0, 1):
                    groups, cur = [], [idx[0]]
                    for i in idx[1:]:
                        if ca[i][ax] == ca[cur[-1]][ax]: cur.append(i)
                        else: groups.append(cur); cur = [i]
                    groups.append(cur)
                    if len(groups) > 1 and ca[groups[0][0]][ax] == ca[groups[-1][-1]][ax]: groups[0] += groups.pop()
                    for gr in groups:
                        v = sum(pts[i][ax] for i in gr) / len(gr)
                        for i in gr: pts[i][ax] = v
            for i in range(len(pts)):                # never through the baseline or the cap height
                if ca[i][1] >= 0 and cb[i][1] >= 0 and pts[i][1] < 0: pts[i][1] = 0
                if ca[i][1] <= 720 and cb[i][1] <= 720 and pts[i][1] > 720: pts[i][1] = 720
            if n == "one" and w < 400 and len(pts) == 8:      # the flag joins the side of the stem
                st_w = pts[7][0] - pts[0][0]
                if pts[2][1] > 720 - 0.5 * st_w: pts[2][1] = 720 - 1.1 * st_w
            if n == "zero" and w < 400 and len(ga.endPtsOfContours) == 3:   # slash counters stay in the ring
                e = ga.endPtsOfContours; lo_c = list(range(e[0] + 1, e[1] + 1)); up_c = list(range(e[1] + 1, e[2] + 1))
                if min(pts[i][1] for i in lo_c) > min(pts[i][1] for i in up_c): lo_c, up_c = up_c, lo_c
                bx0 = min(pts[i][0] for i in up_c); by0 = min(pts[i][1] for i in lo_c)
                bx1 = max(pts[i][0] for i in lo_c); by1 = max(pts[i][1] for i in up_c)
                for i in lo_c + up_c: pts[i] = [min(max(pts[i][0], bx0), bx1), min(max(pts[i][1], by0), by1)]
            for i in range(len(pts)): g.coordinates[i] = (round(pts[i][0]), round(pts[i][1]))
        aa, ab = a["hmtx"][n][0], b["hmtx"][n][0]; f["hmtx"][n] = (round(aa + t * (aa - ab)), f["hmtx"][n][1])
    bb = io.BytesIO(); f.save(bb); d = bb.getvalue(); return TTFont(io.BytesIO(d)), d

def ink(f, name):
    gs = f.getGlyphSet(); bp = BoundsPen(gs); gs[name].draw(bp); return bp.bounds
@functools.lru_cache(None)
def stem(w):
    b = ink(inst(w)[0], "I"); return b[2] - b[0]
@functools.lru_cache(None)
def width(w):
    _, d = inst(w); font = hb.Font(hb.Face(d)); b = hb.Buffer(); b.add_str("FALSARD"); b.guess_segment_properties(); hb.shape(font, b)
    return sum(p.x_advance for p in b.glyph_positions)
def solve(W, s=WIDEN):
    """weight wx and scale k: k * width(wx) = s * width(W) and k * stem(wx) = stem(W)"""
    target = s * width(W); lo, hi = 150.0, 1600.0
    for _ in range(18):
        m = (lo + hi) / 2
        if stem(round(m, 1)) * target / width(round(m, 1)) > stem(W): hi = m
        else: lo = m
    wx = round((lo + hi) / 2, 1); return wx, target / width(wx)

# ---------------------------------------------------------------- bands
class Bands:
    def __init__(self, lim, sc=(1.2, 1.0, 0.5)):
        self.lim, self.sc = lim, sc; self.tops = [0]
        for i, s in enumerate(sc): self.tops.append(self.tops[-1] + (lim[i + 1] - lim[i]) * s)
    def __call__(self, y):
        if y <= 0: return y
        for i in range(3):
            if y <= self.lim[i + 1] or i == 2: return self.tops[i] + (y - self.lim[i]) * self.sc[i]
CAPS = Bands([0, 157, 439, 720])     # set on the S
LOWER = Bands([0, 153, 367, 580])    # set on the s

class MapPen:
    def __init__(s, pen, f, dx=0): s.p, s.f, s.dx = pen, f, dx
    def _m(s, pts): return [(x + s.dx, s.f(y)) for x, y in pts]
    def moveTo(s, pt): s.p.moveTo(*s._m([pt]))
    def lineTo(s, pt): s.p.lineTo(*s._m([pt]))
    def qCurveTo(s, *pts): s.p.qCurveTo(*s._m(pts))
    def curveTo(s, *pts): s.p.curveTo(*s._m(pts))
    def closePath(s): s.p.closePath()
    def endPath(s): s.p.endPath()

# ---------------------------------------------------------------- path helpers
def clean(gp, amin=150):
    gp.simplify(clockwise=True); out = pathops.Path(); pen = out.getPen()
    for c in gp.contours:
        ap = AreaPen(); c.draw(ap)
        if abs(ap.value) >= amin: c.draw(pen)
    out.simplify(clockwise=True); return out
def rect(xa, xb, ya, yb):
    r = pathops.Path(); pn = r.getPen(); pn.moveTo((xa, ya)); pn.lineTo((xb, ya)); pn.lineTo((xb, yb)); pn.lineTo((xa, yb)); pn.closePath(); return r
def xform(p, a, b, c, d, e, f):
    out = pathops.Path(); p.draw(TransformPen(out.getPen(), (a, b, c, d, e, f))); return out
def union(*ps):
    r = pathops.Path()
    for p in ps: r = pathops.op(r, p, pathops.PathOp.UNION, clockwise=True)
    return r
def runs_at(path, y, x0, x1):
    out, st = [], None
    for x in range(int(x0) - 5, int(x1) + 6, 2):
        p = PointInsidePen(None, (x, y)); path.draw(p); ins = p.getResult()
        if ins and st is None: st = x
        if not ins and st is not None: out.append((st, x - 2)); st = None
    return out
def keep_counters_inside(src, margin):
    """counters may not break through the outline (extrapolated light weights)"""
    rec = RecordingPen(); src.draw(rec); conts, cur = [], []
    for op, a in rec.value:
        cur.append((op, a))
        if op in ("closePath", "endPath"): conts.append(cur); cur = []
    outer, holes = pathops.Path(), pathops.Path()
    for c in conts:
        ap = AreaPen(); q = pathops.Path(); pn = q.getPen()
        for op, a in c: getattr(ap, op)(*a); getattr(pn, op)(*a)
        q.simplify(clockwise=True)
        if ap.value < 0: outer = pathops.op(outer, q, pathops.PathOp.UNION, clockwise=True)
        else: holes = pathops.op(holes, q, pathops.PathOp.UNION, clockwise=True)
    if not list(holes.contours): return src
    ring = pathops.Path(outer); ring.stroke(2 * margin, pathops.LineCap.BUTT_CAP, pathops.LineJoin.ROUND_JOIN, 4); ring.convertConicsToQuads()
    inset = pathops.op(outer, ring, pathops.PathOp.DIFFERENCE, clockwise=True)
    holes = pathops.op(holes, inset, pathops.PathOp.INTERSECTION, clockwise=True)
    return pathops.op(outer, holes, pathops.PathOp.DIFFERENCE, clockwise=True)

# ---------------------------------------------------------------- S without head nor tail
CUT = {"S": ("S", .5), "Scaron": ("S", .5), "s": ("s", .5), "scaron": ("s", .5), "s.sc": ("s.sc", .5), "dollar": ("dollar", .3)}
def s_bars(W, g, fx):
    f, _ = inst(W); gs = f.getGlyphSet(); x0, _, x1, _ = ink(f, g); cx = x0 + fx * (x1 - x0)
    def ins(y):
        p = PointInsidePen(gs, (cx, y)); gs[g].draw(p); return p.getResult()
    runs, st = [], None
    for y in range(-120, 840):
        i = ins(y)
        if i and st is None: st = y
        if not i and st is not None: runs.append((st, y - 1)); st = None
    runs = [r for r in runs if r[1] - r[0] > 20 and r[0] < 700]     # the three bars (not a caron above)
    b, m, t = runs[0], runs[1], runs[2]
    lo, hi = b[1] - 1, b[1] + 2                 # exact top of the bottom bar
    for _ in range(40):
        md = (lo + hi) / 2
        if ins(md): lo = md
        else: hi = md
    yb = round(lo)
    lo, hi = t[0] - 2, t[0] + 1                 # exact underside of the top bar
    for _ in range(40):
        md = (lo + hi) / 2
        if ins(md): hi = md
        else: lo = md
    return yb, round(hi), m
def cut_s(gp, W, base, fx, bands):
    x0, _, x1, _ = gp.bounds
    yb, yt, m = s_bars(W, base, fx)
    head_lo, head_hi = bands(m[1] + 1) + 1, bands(yt)
    tail_lo, tail_hi = bands(yb), bands(m[0]) - 1
    r = runs_at(gp, head_hi - 6, x0, x1); xa = (r[-2][1] + r[-1][0]) / 2 if len(r) >= 2 else (x0 + x1) / 2
    gp = pathops.op(gp, rect(xa, x1 + 50, head_lo, head_hi), pathops.PathOp.DIFFERENCE, clockwise=True)
    r = runs_at(gp, tail_lo + 6, x0, x1); xb = (r[0][1] + r[1][0]) / 2 if len(r) >= 2 else (x0 + x1) / 2
    return pathops.op(gp, rect(x0 - 50, xb, tail_lo, tail_hi), pathops.PathOp.DIFFERENCE, clockwise=True)

# ---------------------------------------------------------------- glyphs
def bands_for(name, uni):
    base = name.split(".")[0]
    if name.endswith(".sc"): return LOWER
    ch = uni.get(name) or uni.get(base)
    if ch is None: return CAPS
    cat = unicodedata.category(chr(ch))
    return LOWER if cat in ("Ll", "Mn", "Sk") else CAPS

def topo(p, amin=150):
    """(outer contours, counters), ignoring slivers smaller than amin"""
    q = pathops.Path(p); q.simplify(clockwise=True); o = h = 0
    for c in q.contours:
        ap = AreaPen(); c.draw(ap)
        if abs(ap.value) < amin: continue
        if ap.value < 0: o += 1
        else: h += 1
    return o, h
def amin_for(W): return max(150, 0.3 * stem(W) ** 2) if W < 400 else 150
@functools.lru_cache(None)
def topo_ref(name, W):
    f, _ = inst(min(max(W, 400), 900)); gs = f.getGlyphSet()
    p = pathops.Path(); gs[name].draw(p.getPen(glyphSet=gs)); return topo(p, amin_for(W))
def closing(src, r):
    """bridge hairline gaps (dilate then erode by r): nothing is thinned"""
    q = pathops.Path(src); q.simplify(clockwise=True)
    band = pathops.Path(q); band.stroke(2 * r, pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 4); band.convertConicsToQuads()
    dil = pathops.op(q, band, pathops.PathOp.UNION, clockwise=True)
    band = pathops.Path(dil); band.stroke(2 * r, pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 4); band.convertConicsToQuads()
    return pathops.op(dil, band, pathops.PathOp.DIFFERENCE, clockwise=True)

_UNI = {}
def is_mark(name):
    if not _UNI:
        for c, n in TTFont(VF).getBestCmap().items(): _UNI.setdefault(n, c)
    c = _UNI.get(name); return c is not None and unicodedata.category(chr(c)) in ("Mn", "Sk")

def src_simple(name, wy, wx, k):
    fW, _ = inst(wy); fX, _ = inst(wx)
    ry = RecordingPen(); fW.getGlyphSet()[name].draw(ry)
    rx = RecordingPen(); fX.getGlyphSet()[name].draw(rx)
    src = pathops.Path(); pen = src.getPen()
    for (op, ax), (_, ay) in zip(rx.value, ry.value):
        getattr(pen, op)(*[None if pa is None else (pa[0] * k, pb[1]) for pa, pb in zip(ax, ay)])
    return src

def light_from_400(name, W):
    """light weight drawn from the 400: strokes thinned evenly (outline eroded), then put back
    on the 400 outer box (letters) or centred (accents)"""
    wx4, k4 = solve(400); base = src_simple(name, 400, wx4, k4); base.simplify(clockwise=True)
    d = (stem(400) - stem(W)) / 2
    band = pathops.Path(base); band.stroke(2 * d, pathops.LineCap.BUTT_CAP, pathops.LineJoin.MITER_JOIN, 8); band.convertConicsToQuads()
    er = pathops.op(base, band, pathops.PathOp.DIFFERENCE, clockwise=True)
    if not list(er.contours): return base
    b, e = base.bounds, er.bounds
    if is_mark(name):
        return xform(er, 1, 0, 0, 1, (b[0] + b[2] - e[0] - e[2]) / 2, (b[1] + b[3] - e[1] - e[3]) / 2)
    fy = (b[3] - b[1]) / (e[3] - e[1]); fx = min((b[2] - b[0]) / (e[2] - e[0]), 1.1)
    cxb, cxe = (b[0] + b[2]) / 2, (e[0] + e[2]) / 2
    return xform(er, fx, 0, 0, fy, cxb - cxe * fx, b[1] - e[1] * fy)

def mean_thickness(p):
    """2 * area / perimeter: average stroke thickness of a thin shape"""
    A = 0; P = 0
    for c in p.contours:
        ap = AreaPen(); c.draw(ap); A += abs(ap.value)
        rec = RecordingPen(); c.draw(rec); pts = []
        for op, a in rec.value: pts += [q for q in a if q is not None]
        if pts: pts.append(pts[0])
        P += sum(((x1 - x0) ** 2 + (y1 - y0) ** 2) ** .5 for (x0, y0), (x1, y1) in zip(pts, pts[1:]))
    return 2 * A / P if P else 0
def light_mark(name, W):
    """light accent: the 400 accent thinned in proportion to its own stroke (stays whole)"""
    wx4, k4 = solve(400); base = src_simple(name, 400, wx4, k4); base.simplify(clockwise=True)
    d = mean_thickness(base) * (1 - stem(W) / stem(400)) / 2
    band = pathops.Path(base); band.stroke(2 * d, pathops.LineCap.BUTT_CAP, pathops.LineJoin.MITER_JOIN, 8); band.convertConicsToQuads()
    er = pathops.op(base, band, pathops.PathOp.DIFFERENCE, clockwise=True)
    if not list(er.contours): return base
    b, e = base.bounds, er.bounds
    return xform(er, 1, 0, 0, 1, (b[0] + b[2] - e[0] - e[2]) / 2, (b[1] + b[3] - e[1] - e[3]) / 2)

LIGHT_LOG = []
@functools.lru_cache(None)
def src_of(name, wy, wx, k):
    """glyph in source space (x already widened, y not yet banded); components built one by one"""
    fW, _ = inst(wy); fX, _ = inst(wx); gW, gX = fW["glyf"][name], fX["glyf"][name]
    if gW.isComposite():
        out = pathops.Path()
        for cW, cX in zip(gW.components, gX.components):
            p = src_of(cW.glyphName, wy, wx, k)
            out = union(out, xform(p, 1, 0, 0, 1, cX.x * k, cW.y))
        return out
    src = src_simple(name, wy, wx, k)
    if wy < 400:
        am, ref = amin_for(wy), topo_ref(name, wy)
        src = closing(keep_counters_inside(src, 0.4 * stem(wy)), 0.15 * stem(wy))
        if topo(src, am) != ref or (is_mark(name) and mean_thickness(src) < 0.5 * mean_thickness(light_mark(name, wy))):
            if is_mark(name):
                tries = [("thinned 400 accent", lambda: light_mark(name, wy))]
                if wy < 300:
                    w3, k3 = solve(300); tries.append(("accent of 300", lambda: src_of(name, 300, w3, k3)))
            else:
                tries = [("from 400", lambda: closing(light_from_400(name, wy), 0.15 * stem(wy)))]
                for wb in (250, 300, 350, 400):    # last resort: that glyph from a slightly heavier weight
                    if wb > wy:
                        wbx, kb = solve(wb); tries.append((f"drawn from {wb}", lambda wb=wb, wbx=wbx, kb=kb: src_of(name, wb, wbx, kb)))
            for lab, fn in tries:
                alt = fn()
                if topo(alt, am) == ref: LIGHT_LOG.append(f"{name}@{wy}: {lab}"); return alt
            LIGHT_LOG.append(f"{name}@{wy}: STILL {topo(src, am)} vs {ref}")
    return src

def build_glyph(name, W, wx, k, bands, wy=None):
    wy = wy or W
    src = src_of(name, wy, wx, k)
    gp = pathops.Path(); src.draw(MapPen(gp.getPen(), bands))
    gp = clean(gp)
    if name in CUT: gp = cut_s(gp, wy, CUT[name][0], CUT[name][1], bands)
    return gp

def make_glyph(name, W, wx, k, bands, log):
    """build, and if the topology broke (counter closed, part detached), retry with a lighter
    vertical source (heavy weights) - like adjusting that letter by hand"""
    gp = build_glyph(name, W, wx, k, bands); ref = topo_ref(name, W); am = amin_for(W)
    if topo(gp, am) == ref: return gp
    if W >= 900:
        for wy in range(W - 25, 599, -25):
            g2 = build_glyph(name, W, wx, k, bands, wy=wy)
            if topo(g2, am) == ref: log.append(f"{name}: y from {wy}"); return g2
    if W < 400:   # rare glyphs that will not thin cleanly: drawn from the nearest weight that holds
        for wb in range(W + 25, 401, 25):
            wbx, kb = solve(wb); g2 = build_glyph(name, wb, wbx, kb, bands)
            if topo(g2, am) == ref: log.append(f"{name}: drawn from {wb}"); return g2
    log.append(f"{name}: UNRESOLVED {topo(gp, am)} vs {ref}")
    return gp

def hole_bounds(p):
    best = None
    for c in p.contours:
        ap = AreaPen(); c.draw(ap)
        if ap.value > 0:
            b = c.bounds
            if best is None or (b[2] - b[0]) * (b[3] - b[1]) > (best[2] - best[0]) * (best[3] - best[1]): best = b
    return best
def circled(ring, letter, fill=0.62):
    """(c) and (R): Falsard O of the same weight, the letter scaled into its counter"""
    hx0, hy0, hx1, hy1 = hole_bounds(ring); l = letter.bounds
    s = fill * (hy1 - hy0) / (l[3] - l[1])
    if (l[2] - l[0]) * s > 0.8 * (hx1 - hx0): s = 0.8 * (hx1 - hx0) / (l[2] - l[0])
    w, h = (l[2] - l[0]) * s, (l[3] - l[1]) * s; cx, cy = (hx0 + hx1) / 2, (hy0 + hy1) / 2
    return union(ring, xform(letter, s, 0, 0, s, cx - w / 2 - l[0] * s, cy - h / 2 - l[1] * s))
def trademark(T, M, cap, scale=0.42, gap=0.05, sb=60):
    t, m = T.bounds, M.bounds
    Ts = xform(T, scale, 0, 0, scale, sb - t[0] * scale, cap - t[3] * scale)
    xoff = sb + (t[2] - t[0]) * scale + gap * cap
    Ms = xform(M, scale, 0, 0, scale, xoff - m[0] * scale, cap - m[3] * scale)
    p = union(Ts, Ms); return p, p.bounds[2] + sb

def to_tt(p):
    tt = TTGlyphPen(None); p.draw(Cu2QuPen(tt, max_err=0.5, reverse_direction=False)); return tt.glyph()

# ---------------------------------------------------------------- font
def scale_gpos(f, k, bands_of):
    gpos = f["GPOS"].table
    for lk in gpos.LookupList.Lookup:
        for st in lk.SubTable:
            if lk.LookupType == 2:
                recs = []
                if st.Format == 1:
                    for ps in st.PairSet: recs += [r.Value1 for r in ps.PairValueRecord] + [r.Value2 for r in ps.PairValueRecord]
                else:
                    for c1 in st.Class1Record: recs += [c2.Value1 for c2 in c1.Class2Record] + [c2.Value2 for c2 in c1.Class2Record]
                for v in recs:
                    if v is None: continue
                    for a in ("XAdvance", "XPlacement"):
                        if hasattr(v, a): setattr(v, a, round(getattr(v, a) * k))
                    for a in ("XAdvDevice", "XPlaDevice"):
                        if hasattr(v, a): setattr(v, a, None)
            elif lk.LookupType == 4:
                for g, mr in zip(st.MarkCoverage.glyphs, st.MarkArray.MarkRecord):
                    a = mr.MarkAnchor; a.XCoordinate = round(a.XCoordinate * k); a.YCoordinate = round(bands_of(g)(a.YCoordinate))
                for g, br in zip(st.BaseCoverage.glyphs, st.BaseArray.BaseRecord):
                    for a in br.BaseAnchor:
                        if a is None: continue
                        a.XCoordinate = round(a.XCoordinate * k); a.YCoordinate = round(bands_of(g)(a.YCoordinate))

def set_names(f, style, weight):
    fam = "Falsard"; ps = style
    nm = f["name"]; nm.names = [r for r in nm.names if r.nameID < 256 and r.nameID != 25]
    vals = {0: 'Copyright 2018 The Orbitron Project Authors (https://github.com/theleagueof/orbitron), with Reserved Font Name: "Orbitron". Modifications (Falsard) 2026 LaFleurStudio.',
            1: f"{fam} {style}", 2: "Regular", 3: f"1.000;{fam}-{ps}", 4: f"{fam} {style}", 5: "Version 1.000",
            6: f"{fam}-{ps}", 10: "Falsard is a modified version of Orbitron (SIL Open Font License 1.1).",
            16: fam, 17: style}
    nm.names = [r for r in nm.names if r.nameID not in vals]
    for i, v in vals.items():
        nm.setName(v, i, 3, 1, 0x409); nm.setName(v, i, 1, 0, 0)
    os2 = f["OS/2"]; os2.usWeightClass = weight
    os2.fsSelection &= ~((1 << 0) | (1 << 5)); os2.fsSelection |= (1 << 6)
    f["head"].macStyle = 0; f["head"].fontRevision = 1.0

def build(W, style):
    wx, k = solve(W)
    f = TTFont(io.BytesIO(inst(wx)[1]))
    for t in ("DSIG", "STAT"):
        if t in f: del f[t]
    order = f.getGlyphOrder(); cmap = f.getBestCmap()
    uni = {}
    for c, n in cmap.items(): uni.setdefault(n, c)
    bands_of = lambda n: bands_for(n, uni)
    glyf, hmtx = f["glyf"], f["hmtx"]
    paths = {}
    log = []
    for n in order:
        paths[n] = make_glyph(n, W, wx, k, bands_of(n), log)
    if log: print(style, "|", "; ".join(log), flush=True)
    if LIGHT_LOG: print(style, "| light:", "; ".join(LIGHT_LOG), flush=True); LIGHT_LOG.clear()
    advs = {n: hmtx[n][0] * k for n in order}
    # (c) (R) (tm)
    O = paths["O"]; cap = CAPS(720)
    extra = {"copyright": (0xA9, circled(O, paths["C"]), advs["O"]),
             "registered": (0xAE, circled(O, paths["R"]), advs["O"])}
    tmp, tadv = trademark(paths["T"], paths["M"], cap)
    extra["trademark"] = (0x2122, tmp, tadv)
    f.setGlyphOrder(order + list(extra))
    for n, (cp, p, adv) in extra.items():
        paths[n] = p; advs[n] = adv
        for t in f["cmap"].tables:
            if t.isUnicode(): t.cmap[cp] = n
    gdef = f["GDEF"].table
    for n in extra: gdef.GlyphClassDef.classDefs[n] = 1
    for n in order + list(extra):
        g = to_tt(paths[n]); glyf[n] = g; g.recalcBounds(glyf)
        hmtx[n] = (round(advs[n]), g.xMin if g.numberOfContours else 0)
    scale_gpos(f, k, bands_of)
    # vertical metrics: the em is mapped like the letters
    os2, hh = f["OS/2"], f["hhea"]
    asc = round(CAPS(1011)); os2.sTypoAscender = hh.ascent = asc; os2.sTypoDescender = hh.descent = -243; os2.sTypoLineGap = hh.lineGap = 0
    ymax = max(getattr(glyf[n], "yMax", 0) for n in f.getGlyphOrder()); ymin = min(getattr(glyf[n], "yMin", 0) for n in f.getGlyphOrder())
    os2.usWinAscent = max(asc, ymax); os2.usWinDescent = max(243, -ymin)
    os2.sCapHeight = round(CAPS(720)); os2.sxHeight = round(LOWER(580))
    os2.recalcAvgCharWidth(f)
    set_names(f, style, min(W, 1000))
    os.makedirs(OUT, exist_ok=True)
    fn = os.path.join(OUT, f"Falsard-{style}.ttf"); f.save(fn)
    print(style, W, "wx", wx, "k", round(k, 4), "stem", round(stem(wx) * k, 1), "/", stem(W), "| glyphs", len(f.getGlyphOrder()), "->", fn, flush=True)
    return fn

if __name__ == "__main__":
    only = os.environ.get("ONLY")
    for W, style in STYLES:
        if only and style not in only.split(","): continue
        build(W, style)
