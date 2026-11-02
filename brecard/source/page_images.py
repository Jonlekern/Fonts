"""Images de la page Brécard, tirées des fichiers de la police (et de fl.py pour la version « avant »).
Utilisation : python page_images.py <dossier ttf> <dossier sortie>   (écrit des SVG puis des PNG)"""
import sys, os, pathops
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
import fl

TTF = sys.argv[1] if len(sys.argv) > 1 else 'out/ttf'
OUTD = sys.argv[2] if len(sys.argv) > 2 else 'brecard-images'
os.makedirs(OUTD, exist_ok=True)
INK = "#141414"; BG = "#f4f1ec"; MUTED = "#8a8379"

def tr(p, m):
    q = pathops.Path(); p.draw(TransformPen(q.getPen(), m)); return q
def union(a, b): return pathops.op(a, b, pathops.PathOp.UNION, fix_winding=True)

def word(parts):
    """parts : liste de (texte, style) mis bout à bout."""
    out = pathops.Path(); x = 0
    for text, style in parts:
        path = f'{TTF}/Brecard-{style}.ttf'
        f = TTFont(path); order = f.getGlyphOrder(); g = f.getGlyphSet()
        font = hb.Font(hb.Face(open(path, 'rb').read())); buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
        hb.shape(font, buf)
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            p = pathops.Path(); g[order[info.codepoint]].draw(p.getPen(glyphSet=g))
            out = union(out, tr(p, (1, 0, 0, 1, x + pos.x_offset, 0))); x += pos.x_advance
    return out

def word_fl(text):
    """Mot dessiné directement avec fl.G (pour la version « avant »)."""
    out = pathops.Path(); x = 0
    for ch in text:
        p, w, l, r = fl.G[ch]; out = union(out, tr(p, (1, 0, 0, 1, x + l, 0))); x += l + w + r
    return out

def svgpath(p, m):
    sp = SVGPathPen(None); p.draw(TransformPen(sp, m)); return sp.getCommands()

def sheet(fn, rows, width=2000, pad=100, maxscale=0.2):
    maxw = max(p.bounds[2] - min(0, p.bounds[0]) for _, p in rows)
    scale = min((width - 2*pad)/maxw, maxscale)
    tops = max(p.bounds[3] for _, p in rows); bots = min(min(p.bounds[1], 0) for _, p in rows)
    parts = []; y = 0
    for i, (lab, p) in enumerate(rows):
        rowh = (tops - bots)*scale + 170
        d = svgpath(p, (scale, 0, 0, -scale, 0, tops*scale))
        g = f'<g transform="translate({pad - min(0, p.bounds[0])*scale},{y + 115})"><path d="{d}" fill="{INK}"/></g>'
        lab_el = f'<text x="{pad}" y="{y + 72}" font-family="Helvetica, Arial, sans-serif" font-size="26" letter-spacing="2.5" fill="{MUTED}">{lab.upper()}</text>'
        sep = f'<line x1="0" x2="{width}" y1="{y + rowh}" y2="{y + rowh}" stroke="#d9d2c6" stroke-width="2"/>' if i < len(rows) - 1 else ""
        parts.append(lab_el + g + sep); y += rowh
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{y + 20}" viewBox="0 0 {width} {y + 20}"><rect width="100%" height="100%" fill="{BG}"/>{"".join(parts)}</svg>'
    open(os.path.join(OUTD, fn.replace('.png', '.svg')), 'w').write(svg); print(fn, width, y + 20)

# 1. le A en pointe de flèche, de 100 à 900
sheet('fleche.png', [
    ('Le A en pointe de flèche · 100, 400, 800, 900',
     word([('A ', 'wavatlh'), ('A ', 'loSvatlh'), ('A ', 'chorghvatlh'), ('A', 'Hutvatlh')])),
], maxscale=0.32)

# 2. les règles
sheet('regles.png', [
    ('Les ronds en losange', word([('OCGQ08', 'chorghvatlh')])),
    ('Les bouts coupés en biais vers l’intérieur', word([('HUFKN', 'chorghvatlh')])),
    ('Les traits qui finissent seuls, en coin', word([('IT147R', 'chorghvatlh')])),
])

# 3. le poids en haut : avant / après
fl.set_weight(1.0)
fl.MID = 0.5; fl.BT = fl.BB = fl.TM = 135.0; fl.TT = fl.TB = 140.0
fl.G.clear(); fl.ORDER.clear(); fl.build_letters()
avant = word_fl('LAFLEURSTUDIO')
fl.MID = 0.42; fl.set_weight(1.0)
sheet('poids.png', [
    ('Avant · le milieu au centre, les barres égales', avant),
    ('Brécard · milieux plus bas, barres du haut plus épaisses', word([('LAFLEURSTUDIO', 'chorghvatlh')])),
])

# 4. les minuscules
sheet('minuscules.png', [
    ('Les verticales en coin, comme le i', word([('abcdefghijklm', 'chorghvatlh')])),
    ('', word([('nopqrstuvwxyz', 'chorghvatlh')])),
    ('Avec les capitales', word([('LaFleurStudio', 'chorghvatlh')])),
])

# Les PNG sont faits ensuite avec svg2png.js (Chromium) : node svg2png.js <dossier>
