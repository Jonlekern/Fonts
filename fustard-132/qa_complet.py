# Contrôle automatique des 9 fichiers Fûstard 132
import sys, os, json, unicodedata
from fontTools.ttLib import TTFont
from fontTools.pens.areaPen import AreaPen
import uharfbuzz as hb
ICI = os.path.dirname(os.path.abspath(__file__))
CORE = json.load(open(os.path.join(ICI, 'gf_core.json')))
CORE = sorted(set(CORE) | {0xB1, 0xAC, 0xAD, 0xA6, 0xA4, 0xB9, 0xB2, 0xB3, 0xBC, 0xBD, 0xBE, 0xB5, 0x192, 0x2020, 0x2021, 0x2030})
ordre = ['Hairline', 'Thin', 'Light', 'Regular', 'Medium', 'Bold', 'ExtraBold', 'SuperBold', 'Black']
dossier = sys.argv[1]
F = {s: TTFont(os.path.join(dossier, f'Fustard132-{s}.ttf')) for s in ordre}
pb = []
for s, t in F.items():
    cmap = t.getBestCmap()
    manque = [hex(c) for c in CORE if c not in cmap]
    if manque: pb.append((s, 'caractères manquants', manque))
    gl = t['glyf']; gs = t.getGlyphSet()
    for n in t.getGlyphOrder():
        g = gl[n]
        if n not in ('space', 'uni00A0', 'nbspace') and g.numberOfContours == 0:
            pb.append((s, 'glyphe vide', n))
        if g.numberOfContours:
            p = AreaPen(gs); gs[n].draw(p)
            if p.value > 0: pb.append((s, 'sens des contours', n))
    o = t['OS/2']; hh = t['hhea']
    if not (o.fsSelection & 0x80): pb.append((s, 'USE_TYPO_METRICS absent'))
    if (o.sTypoAscender, o.sTypoDescender) != (hh.ascent, hh.descent): pb.append((s, 'typo != hhea'))
    ymax = max((gl[n].yMax for n in t.getGlyphOrder() if gl[n].numberOfContours), default=0)
    ymin = min((gl[n].yMin for n in t.getGlyphOrder() if gl[n].numberOfContours), default=0)
    if ymax > o.usWinAscent or -ymin > o.usWinDescent: pb.append((s, 'win trop petit'))
    if t['OS/2'].usWeightClass != (ordre.index(s) + 1) * 100: pb.append((s, 'poids', o.usWeightClass))
# mêmes hauteurs de ligne partout
m = {(t['hhea'].ascent, t['hhea'].descent) for t in F.values()}
if len(m) != 1: pb.append(('famille', 'hauteurs de ligne différentes', m))
ps = [t['name'].getDebugName(6) for t in F.values()]
if len(set(ps)) != 9: pb.append(('famille', 'noms PostScript en double'))
# trous perdus en grossissant : on compte les contours intérieurs (sens trigo en TrueType)
def trous(t, n):
    gl = t['glyf']; g = gl[n]
    if not g.numberOfContours: return 0
    co, ends, _ = g.getCoordinates(gl); st = 0; k = 0
    for e in ends:
        P = co[st:e + 1]; st = e + 1
        a = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(P, list(P[1:]) + [P[0]]))
        if a > 0: k += 1
    return k
H = F['Hairline']
for n in H.getGlyphOrder():
    c = [trous(F[s], n) for s in ordre]
    if min(c[1:]) < c[0] and n not in ('.notdef',):
        pb.append(('famille', 'trou perdu', n, c))
# mise en forme (HarfBuzz)
for s in ('Hairline', 'Black'):
    face = hb.Face(hb.Blob.from_file_path(os.path.join(dossier, f'Fustard132-{s}.ttf'))); font = hb.Font(face)
    def forme(t, lang=None, feats=None):
        b = hb.Buffer(); b.add_str(t); b.guess_segment_properties()
        if lang: b.language = lang
        hb.shape(font, b, feats or {}); return [font.glyph_to_string(i.codepoint) for i in b.glyph_infos], b.glyph_positions
    g, _ = forme('ĩ');  ok1 = g[0] == 'dotlessi'
    g, pos = forme('n̈'); ok2 = g == ['n', 'dieresiscomb'] and pos[1].y_offset != 0 or pos[1].x_offset != 0
    g, _ = forme('ş', 'ro'); ok3 = g == ['uni0219']
    g, _ = forme('0', feats={'onum': True}); ok4 = g == ['zero.onum']
    for nom, ok in (('i + tilde -> ı', ok1), ('n + tréma placé', ok2), ('ş roumain', ok3), ('onum', ok4)):
        if not ok: pb.append((s, 'mise en forme', nom))
print('problèmes :', len(pb))
for p in pb[:40]: print(' ', p)
print({s: os.path.getsize(os.path.join(dossier, f'Fustard132-{s}.ttf')) // 1024 for s in ordre}, 'Ko')
