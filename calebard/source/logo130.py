"""Build LAFLEURSTUDIO wordmark: Anybody Black 900, extended to 130 %,
with stroke contrast rebalanced via anisotropic interpolation
(x coordinates from a lighter weight, y coordinates from Black 900)."""
import copy, io, sys, json
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates
import uharfbuzz as hb
import pathops

VF_PATH, OUT_DIR = sys.argv[1], sys.argv[2]
TEXT = "LAFLEURSTUDIO"
STRETCH = 1.30
WDTH = 150


def instance(wght):
    vf = TTFont(VF_PATH)
    f = instantiateVariableFont(vf, {"wght": wght, "wdth": WDTH})
    buf = io.BytesIO(); f.save(buf)
    data = buf.getvalue()
    return TTFont(io.BytesIO(data)), data


def shape(data):
    face = hb.Face(data); font = hb.Font(face)
    b = hb.Buffer(); b.add_str(TEXT); b.guess_segment_properties()
    hb.shape(font, b, {"kern": True, "liga": False})
    return [(i.codepoint, p.x_advance, p.x_offset, p.y_offset)
            for i, p in zip(b.glyph_infos, b.glyph_positions)]


def stem(font):  # vertical stem thickness = width of the "I" glyph ink
    bp = BoundsPen(font.getGlyphSet()); font.getGlyphSet()["I"].draw(bp)
    return bp.bounds[2] - bp.bounds[0]


def run_width(run):
    return sum(r[1] for r in run)


B, B_data = instance(900)           # source of y coordinates (horizontal strokes)
B_run = shape(B_data)
S900 = stem(B)
target_w = STRETCH * run_width(B_run)


def x_source(wx):
    A, A_data = instance(wx)
    run = shape(A_data)
    scale = target_w / run_width(run)
    return A, run, scale, stem(A) * scale


# Bisection: lighter x-source weight so that stretched stems == Black 900 stems
lo, hi = 100.0, 900.0
for _ in range(18):
    mid = (lo + hi) / 2
    _, _, _, s = x_source(mid)
    if s > S900: hi = mid
    else: lo = mid
wx = round((lo + hi) / 2, 1)
A, A_run, scale, stretched_stem = x_source(wx)


def build(xfont, yfont, run, sx):
    """Union of all glyphs into one pathops.Path, x from xfont scaled by sx, y from yfont."""
    order = xfont.getGlyphOrder()
    glyf_x, glyf_y = xfont["glyf"], yfont["glyf"]
    path = pathops.Path()
    pen_x = 0
    for gid, adv, xoff, yoff in run:
        name = order[gid]
        gx, gy = glyf_x[name], glyf_y[name]
        if gx.numberOfContours > 0:
            assert len(gx.coordinates) == len(gy.coordinates), name
            g = copy.deepcopy(gx)
            g.coordinates = GlyphCoordinates(
                [(cx, cy) for (cx, _), (_, cy) in zip(gx.coordinates, gy.coordinates)])
            tp = TransformPen(path.getPen(), (sx, 0, 0, 1, (pen_x + xoff) * sx, yoff))
            g.draw(tp, glyf_x)
        elif gx.numberOfContours < 0:
            raise SystemExit(f"composite glyph not handled: {name}")
        pen_x += adv
    path.simplify()  # remove overlaps -> clean single outline
    return path


def to_svg(path, fill, label):
    xmin, ymin, xmax, ymax = path.bounds
    w, h = xmax - xmin, ymax - ymin
    sp = SVGPathPen(None, ntos=lambda v: ("%.2f" % v).rstrip("0").rstrip("."))
    path.draw(TransformPen(sp, (1, 0, 0, -1, -xmin, ymax)))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" '
            f'width="{w:.0f}" height="{h:.0f}" role="img" aria-label="{label}">'
            f'<path fill="{fill}" d="{sp.getCommands()}"/></svg>\n'), (w, h)


def ink_stem(path_font_x, sx):
    return stem(path_font_x) * sx


corrected = build(A, B, A_run, scale)
naive = build(B, B, B_run, STRETCH)
original = build(B, B, B_run, 1.0)

files = {}
for key, p, fill in [("lafleurstudio-130-noir", corrected, "#000000"),
                     ("lafleurstudio-130-blanc", corrected, "#FFFFFF"),
                     ("_naive", naive, "#141414"),
                     ("_original", original, "#141414"),
                     ("_corrected", corrected, "#141414")]:
    svg, size = to_svg(p, fill, "LaFleurStudio")
    open(f"{OUT_DIR}/{key}.svg", "w").write(svg)
    files[key] = size

# Horizontal stroke check: thickness of the top bar of "E"/"T" is unchanged since y comes from Black 900.
report = {
    "x_source_weight": wx,
    "x_scale": round(scale, 4),
    "stem_black900_original": S900,
    "stem_naive_130": round(S900 * STRETCH, 1),
    "stem_corrected_130": round(stretched_stem, 1),
    "width_original": round(files["_original"][0]),
    "width_naive": round(files["_naive"][0]),
    "width_corrected": round(files["_corrected"][0]),
    "height": round(files["_corrected"][1]),
}
print(json.dumps(report, indent=1))
