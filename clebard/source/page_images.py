"""Images de la page Clebard (étapes de fabrication), tirées du même code que les polices.
Utilisation : python page_images.py  (à lancer à côté de build_clebard.py ; écrit des SVG dans clebard-images/)"""
import sys, os, pathops
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

HEROS = 'dl-heros/tex-gyre/opentype/texgyreheros-bold.otf'
CAL = sys.argv[1] if len(sys.argv) > 1 else 'Calebard-ExtremeBlack.ttf'
VENTI_RAW, VENTI_SP, TRENTA_RAW = 'famille2/raw-Venti.otf', 'famille2/sp-Venti.otf', 'famille2/raw-Trenta.otf'
OUTD = 'clebard-images'; os.makedirs(OUTD, exist_ok=True)
INK = "#141414"; BG = "#f4f1ec"; MUTED = "#8a8379"

def recipe(wt, src=HEROS):
    ns = {}; sys.argv = ['x', src, '/dev/null', '1.4', str(wt)]
    exec(open('build_clebard.py').read().split("def holes_area")[0], ns); return ns

def tr(p, m):
    q = pathops.Path(); p.draw(TransformPen(q.getPen(), m)); return q

def glyph(path, n):
    f = TTFont(path); g = f.getGlyphSet(); p = pathops.Path(); g[n].draw(p.getPen(glyphSet=g)); return p

def union(a, b):
    return pathops.op(a, b, pathops.PathOp.UNION, fix_winding=True, keep_starting_points=False)

def word(text, font_path, getter=None, sx=1.0, extra=0.0, scale=1.0):
    """mot mis en page par HarfBuzz avec la chasse et le crénage du fichier (x sx, + extra par lettre)"""
    f = TTFont(font_path); order = f.getGlyphOrder(); g = f.getGlyphSet()
    font = hb.Font(hb.Face(open(font_path, 'rb').read())); buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
    hb.shape(font, buf, {'kern': True})
    out = pathops.Path(); x = 0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        n = order[info.codepoint]
        if getter: p = getter(n)
        else: p = pathops.Path(); g[n].draw(p.getPen(glyphSet=g))
        out = union(out, tr(p, (scale, 0, 0, scale, x * scale, 0))); x += pos.x_advance * sx + extra
    return out

def sheet(fn, rows, width=2000, pad=100):
    maxw = max(p.bounds[2] - min(0, p.bounds[0]) for _, p in rows)
    scale = (width - 2 * pad) / maxw
    tops = max(p.bounds[3] for _, p in rows); bots = min(min(p.bounds[1], 0) for _, p in rows)
    parts = []; y = 0
    for i, (lab, p) in enumerate(rows):
        rowh = (tops - bots) * scale + 170
        sp = SVGPathPen(None); p.draw(TransformPen(sp, (scale, 0, 0, -scale, 0, tops * scale)))
        g = f'<g transform="translate({pad - min(0, p.bounds[0]) * scale},{y + 115})"><path d="{sp.getCommands()}" fill="{INK}"/></g>'
        lab_el = f'<text x="{pad}" y="{y + 72}" font-family="Helvetica, Arial, sans-serif" font-size="26" letter-spacing="2.5" fill="{MUTED}">{lab.upper()}</text>'
        sep = f'<line x1="0" x2="{width}" y1="{y + rowh}" y2="{y + rowh}" stroke="#d9d2c6" stroke-width="2"/>' if i < len(rows) - 1 else ""
        parts.append(lab_el + g + sep); y += rowh
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{y + 20}" viewBox="0 0 {width} {y + 20}"><rect width="100%" height="100%" fill="{BG}"/>{"".join(parts)}</svg>'
    open(os.path.join(OUTD, fn.replace('.png', '.svg')), 'w').write(svg); print(fn, width, y + 20)

# 1. élargir sans déformer (fûts du Bold : 150 ; étirés : 210)
r7 = recipe(700)
def thin700(n):
    """Bold étiré à 140 %, fûts ramenés à 150 (amincissement en 4 petites passes, plus précis)"""
    p = tr(r7['build'].__globals__['gs'][n] and pathops.Path(), (1, 0, 0, 1, 0, 0))
    p = pathops.Path(); r7['gs'][n].draw(TransformPen(p.getPen(glyphSet=r7['gs']), (1.4, 0, 0, 1, 0, 0))); p.simplify(fix_winding=True)
    for _ in range(4): p = r7['offset'](p, r7['GX'] / 4, r7['GY'] / 4)
    return tr(p, (1, 0, 0, r7['K'], 0, r7['GY'] * r7['K']))
sheet('elargir.png', [
    ('TeX Gyre Heros Bold · la base libre', word('CLEBARD', HEROS)),
    ('Étiré brut à 140 % · fûts à 210', tr(word('CLEBARD', HEROS), (1.4, 0, 0, 1, 0, 0))),
    ('Élargi sans déformer · fûts à 150, comme à l’origine',
     word('CLEBARD', HEROS, getter=lambda n: thin700(n), sx=1.4)),
])

# 2. garder les ouvertures en 1200
r12 = recipe(1200)
full12 = lambda n: tr(r12['build'](n, 1.0, 1.0), (1, 0, 0, r12['K'], r12['GX'], r12['GY'] * r12['K']))
sheet('ouvertures.png', [
    ('1200 sans correction · les blancs se bouchent', word('seag3', VENTI_RAW, getter=full12)),
    ('1200 corrigée · traits horizontaux affinés là où il faut', word('seag3', VENTI_RAW)),
])

# 3. la 1400 trichée
r14 = recipe(1400)
full14 = lambda n: tr(r14['build'](n, 1.0, 1.0), (1, 0, 0, r14['K'], r14['GX'], r14['GY'] * r14['K']))
sheet('triche.png', [
    ('1400 pure · ça casse', word('sea€5', TRENTA_RAW, getter=full14)),
    ('1400 trichée · fûts de la 1400, ouvertures de la 1200', word('sea€5', TRENTA_RAW)),
])

# 4. espacement de Calebard (même hauteur de capitales)
cal = TTFont(CAL); cg = cal.getGlyphSet()
from fontTools.pens.boundsPen import BoundsPen
bp = BoundsPen(cg); cg['H'].draw(bp); S = 729 / bp.bounds[3]
sheet('espacement.png', [
    ('Calebard Extreme Black · la référence', word('LAFLEURSTUDIO', CAL, scale=S)),
    ('Clebard Venti · espacement d’origine', word('LAFLEURSTUDIO', VENTI_RAW)),
    ('Clebard Venti · espacement de Calebard', word('LAFLEURSTUDIO', VENTI_SP)),
])
