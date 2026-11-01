"""Images de la page Malabard (étapes de fabrication), tirées des mêmes scripts que les polices.
Utilisation : python page_images.py  (à côté de stretch.py, plan.py, stretchlib.py ; écrit des SVG dans malabard-images/)"""
import sys, os, pathops
sys.path.insert(0, '.')
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from stretchlib import *

SRC = 'src/Righteous-Regular.ttf'
OUT = 'mal/out/ttf'
OLD_THIN = sys.argv[1] if len(sys.argv) > 1 else None      # ExtraLight coupée (première version)
OLD_BOLD = sys.argv[2] if len(sys.argv) > 2 else None      # 800 épaissie sans précaution
OUTD = 'malabard-images'; os.makedirs(OUTD, exist_ok=True)
INK = "#141414"; BG = "#f4f1ec"; MUTED = "#8a8379"; ACC = "#c8402e"

def tr(p, m):
    q = pathops.Path(); p.draw(TransformPen(q.getPen(), m)); return q
def union(a, b):
    return pathops.op(a, b, pathops.PathOp.UNION, fix_winding=True, keep_starting_points=False)
def word(text, font_path):
    f = TTFont(font_path); order = f.getGlyphOrder(); g = f.getGlyphSet()
    font = hb.Font(hb.Face(open(font_path, 'rb').read())); buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
    hb.shape(font, buf, {'kern': True})
    out = pathops.Path(); x = 0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        p = pathops.Path(); g[order[info.codepoint]].draw(p.getPen(glyphSet=g))
        out = union(out, tr(p, (1, 0, 0, 1, x + pos.x_offset, 0))); x += pos.x_advance
    return out
def svgpath(p, m):
    sp = SVGPathPen(None); p.draw(TransformPen(sp, m)); return sp.getCommands()
def sheet(fn, rows, width=2000, pad=100):
    maxw = max(p.bounds[2] - min(0, p.bounds[0]) for _, p in rows)
    scale = min((width - 2 * pad) / maxw, 0.22)
    tops = max(p.bounds[3] for _, p in rows); bots = min(min(p.bounds[1], 0) for _, p in rows)
    parts = []; y = 0
    for i, (lab, p) in enumerate(rows):
        rowh = (tops - bots) * scale + 170
        d = svgpath(p, (scale, 0, 0, -scale, 0, tops * scale))
        g = f'<g transform="translate({pad - min(0, p.bounds[0]) * scale},{y + 115})"><path d="{d}" fill="{INK}"/></g>'
        lab_el = f'<text x="{pad}" y="{y + 72}" font-family="Helvetica, Arial, sans-serif" font-size="26" letter-spacing="2.5" fill="{MUTED}">{lab.upper()}</text>'
        sep = f'<line x1="0" x2="{width}" y1="{y + rowh}" y2="{y + rowh}" stroke="#d9d2c6" stroke-width="2"/>' if i < len(rows) - 1 else ""
        parts.append(lab_el + g + sep); y += rowh
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{y + 20}" viewBox="0 0 {width} {y + 20}"><rect width="100%" height="100%" fill="{BG}"/>{"".join(parts)}</svg>'
    open(os.path.join(OUTD, fn.replace('.png', '.svg')), 'w').write(svg); print(fn, width, y + 20)

# 1. la base et la Medium
sheet('allonger.png', [
    ('Righteous · la base', word('LaFleurStudio', SRC)),
    ('Malabard Medium · les verticales allongées de 50 %', word('LaFleurStudio', f'{OUT}/Malabard-Medium.ttf')),
])

# 2. la coupe : là où on coupe, et ce qu'on ajoute (en rouge)
f0 = TTFont(SRC)
def rect(x0, y0, x1, y1):
    p = pathops.Path(); pen = p.getPen(); pen.moveTo((x0, y0)); pen.lineTo((x1, y0)); pen.lineTo((x1, y1)); pen.lineTo((x0, y1)); pen.closePath(); return p
letters = []
for ch in 'onS':
    gn = f0.getBestCmap()[ord(ch)]; cs = contours_of(f0, gn)
    h = XH if ch.islower() else CAP
    cuts = plan(cs, h); d = D500 / len(cuts)
    ys = sorted(max(c) for c in cuts)
    new = to_path(stretch_glyph(cs, cuts, D500))
    bands = pathops.Path()
    for k, y in enumerate(ys): bands = union(bands, rect(-500, y + k * d, 3000, y + (k + 1) * d))
    red = pathops.op(new, bands, pathops.PathOp.INTERSECTION, fix_winding=True)
    letters.append((to_path(cs), ys, new, red, f0['hmtx'][gn][0]))
W, PAD, SC = 2000, 100, 0.175
TOP = CAP + D500 + 60; H = int(TOP * SC) + 230
parts = []; x = PAD
for orig, ys, new, red, adv in letters:
    m = (SC, 0, 0, -SC, 0, TOP * SC)
    parts.append(f'<g transform="translate({x},140)"><path d="{svgpath(orig, m)}" fill="{INK}"/>' +
                 ''.join(f'<line x1="{-30}" x2="{adv * SC + 30}" y1="{(TOP - y) * SC}" y2="{(TOP - y) * SC}" stroke="{ACC}" stroke-width="4" stroke-dasharray="14 10"/>' for y in ys) + '</g>')
    x += adv * SC + 60
    parts.append(f'<g transform="translate({x},140)"><path d="{svgpath(new, m)}" fill="{INK}"/><path d="{svgpath(red, m)}" fill="{ACC}"/></g>')
    x += adv * SC + 150
lab = f'<text x="{PAD}" y="72" font-family="Helvetica, Arial, sans-serif" font-size="26" letter-spacing="2.5" fill="{MUTED}">LA COUPE (POINTILLÉS) · CE QU’ON AJOUTE (EN ROUGE)</text>'
svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="100%" height="100%" fill="{BG}"/>{lab}{"".join(parts)}</svg>'
open(os.path.join(OUTD, 'coupe.svg'), 'w').write(svg); print('coupe.png', W, H, 'largeur utilisée', x)

# 3. les diagonales en ExtraLight
if OLD_THIN:
    sheet('diagonales.png', [
        ('ExtraLight coupée · les diagonales s’épaississent', word('NVXZ vxz', OLD_THIN)),
        ('ExtraLight · amincie puis étirée d’un bloc', word('NVXZ vxz', f'{OUT}/Malabard-ExtraLight.ttf')),
    ])
# 4. les blancs en ExtraBold
if OLD_BOLD:
    sheet('blancs.png', [
        ('800 épaissie sans précaution', word('mew@?ij', OLD_BOLD)),
        ('ExtraBold · lettres élargies, blancs et points gardés', word('mew@?ij', f'{OUT}/Malabard-ExtraBold.ttf')),
    ])
