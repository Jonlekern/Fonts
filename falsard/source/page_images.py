"""images for the Falsard page (process steps), drawn from the build pipeline itself"""
import sys, os
sys.argv = ["x", "dl-orbitron/Orbitron-VF.ttf", "/dev/null"]
exec(open("build_falsard.py").read().split('if __name__ == "__main__":')[0])
from fontTools.pens.svgPathPen import SVGPathPen
OUTD = "falsard-images"
RED = "#e5262b"; INK = "#141414"; BG = "#f4f1ec"; MUTED = "#8a8379"

def word(text, mode, W=900, bands=CAPS):
    """mode: orbitron (raw), bands (bands only), brut (bands + raw x110%), final (Falsard), final_nocut"""
    f, d = inst(W); font = hb.Font(hb.Face(d)); buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties(); hb.shape(font, buf)
    order = f.getGlyphOrder(); out = pathops.Path(); x = 0
    if mode.startswith("final"):
        wx, k = solve(W); fx, dx = inst(wx); fb = hb.Font(hb.Face(dx)); bb = hb.Buffer(); bb.add_str(text); bb.guess_segment_properties(); hb.shape(fb, bb)
        for info, pos in zip(bb.glyph_infos, bb.glyph_positions):
            n = fx.getGlyphOrder()[info.codepoint]
            src = src_of(n, W, wx, k); gp = pathops.Path(); src.draw(MapPen(gp.getPen(), bands, x * k)); gp = clean(gp)
            if mode == "final" and n in CUT: gp = cut_s(gp, W, CUT[n][0], CUT[n][1], bands)
            out = union(out, gp); x += pos.x_advance
        return out
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        n = order[info.codepoint]; src = src_simple(n, W, W, 1.0)
        gp = pathops.Path()
        if mode == "orbitron": src.draw(TransformPen(gp.getPen(), (1, 0, 0, 1, x, 0)))
        else: src.draw(MapPen(gp.getPen(), bands, x))
        gp.simplify(clockwise=True); out = union(out, gp); x += pos.x_advance
    if mode == "brut": out = xform(out, WIDEN, 0, 0, 1, 0, 0)
    return out

def svg_word(p, lines, scale, x0=0, top=None):
    b = p.bounds; top = top if top is not None else max(b[3], max(lines) if lines else 0)
    sp = SVGPathPen(None); p.draw(TransformPen(sp, (scale, 0, 0, -scale, x0, top * scale)))
    return sp.getCommands(), top

def sheet(fn, rows, width=2000, pad=100, lines_ext=40):
    """rows: list of (label, path, lines) ; same scale for all rows"""
    maxw = max(p.bounds[2] - min(0, p.bounds[0]) for _, p, _ in rows)
    scale = (width - 2 * pad) / maxw
    parts = []; y = 0
    for i, (lab, p, lines) in enumerate(rows):
        b = p.bounds; top = max([b[3]] + lines); bot = min(b[1], 0)
        h = (top - bot) * scale; rowh = h + 170
        g = f'<g transform="translate({pad - b[0] * scale if b[0] < 0 else pad},{y + 115})">'
        sp = SVGPathPen(None); p.draw(TransformPen(sp, (scale, 0, 0, -scale, 0, top * scale)))
        ls = "".join(f'<line x1="{-lines_ext}" x2="{(b[2]) * scale + lines_ext}" y1="{(top - ly) * scale}" y2="{(top - ly) * scale}" stroke="{RED}" stroke-width="3"/>' for ly in lines)
        g += f'<path d="{sp.getCommands()}" fill="{INK}"/>{ls}</g>'
        lab_el = f'<text x="{pad}" y="{y + 72}" font-family="Helvetica, Arial, sans-serif" font-size="26" letter-spacing="2.5" fill="{MUTED}">{lab.upper()}</text>'
        sep = f'<line x1="0" x2="{width}" y1="{y + rowh}" y2="{y + rowh}" stroke="#d9d2c6" stroke-width="2"/>' if i < len(rows) - 1 else ""
        parts.append(lab_el + g + sep); y += rowh
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{y + 20}" viewBox="0 0 {width} {y + 20}"><rect width="100%" height="100%" fill="{BG}"/>{"".join(parts)}</svg>'
    open(os.path.join(OUTD, fn.replace(".png", ".svg")), "w").write(svg)
    print(fn, width, y + 20)

L0 = [0, 157, 439, 720]; L1 = CAPS.tops
# 1. construction lines + bands
sheet("bandes.png", [("Orbitron Black (900) · les lignes rouges sont calées sur le S", word("FALSARD", "orbitron"), L0),
                     ("Le haut compressé de 50 %, le bas épaissi de 20 %", word("FALSARD", "bands"), L1)])
# 2. widening
sheet("elargir.png", [("Étiré brut à 110 % · traits verticaux à 168", word("FALSARD", "brut"), []),
                      ("Élargi sans déformer · traits verticaux à 153, comme à l'origine", word("FALSARD", "final_nocut"), [])])
# 3. S
_a, _b = word("S", "final_nocut"), word("S", "final"); _w = _a.bounds[2] - _a.bounds[0]
sheet("s-coupe.png", [("Avant  ·  sans tête ni queue", union(_a, xform(_b, 1, 0, 0, 1, _w * 1.45, 0)), L1)], width=1400, pad=90, lines_ext=40)
# 4. lowercase
sheet("minuscules.png", [("Minuscules · lignes calées sur le petit s", word("falsard", "final", bands=LOWER), LOWER.tops + [LOWER(770)])])
