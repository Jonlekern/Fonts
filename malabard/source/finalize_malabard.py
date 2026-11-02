# Malabard : ligatures fi/fl, italique (12°), crénage de l'italique, noms, métriques, licence OFL
import sys, math, json
import numpy as np
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphComponent
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.basePen import BasePen
from PIL import Image, ImageDraw, ImageChops

src, out_ttf, style, weight, italic = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5] == '1'
metrics = json.load(open(sys.argv[6])) if len(sys.argv) > 6 else None
ANGLE = 12.0
f = TTFont(src); glyf = f['glyf']; hmtx = f['hmtx']

def kern_dict(f):
    d = {}
    if 'kern' in f:
        for st in f['kern'].kernTables: d.update(st.kernTable)
    return d

# ligatures fi / fl = f + i / f + l
K = kern_dict(f)
for lig, b in (('fi', 'i'), ('fl', 'l')):
    if lig not in glyf.glyphs: continue
    g = Glyph(); g.numberOfContours = -1; g.components = []
    for name, x in (('f', 0), (b, hmtx['f'][0] + K.get(('f', b), 0))):
        c = GlyphComponent(); c.glyphName = name; c.x = x; c.y = 0; c.flags = 0x204 if name == 'f' else 0x4; g.components.append(c)
    glyf[lig] = g
    hmtx[lig] = (hmtx['f'][0] + K.get(('f', b), 0) + hmtx[b][0], 0)

if italic:
    t = math.tan(math.radians(ANGLE)); y0 = f['OS/2'].sxHeight / 2
    for gn in f.getGlyphOrder():
        g = glyf[gn]
        if g.numberOfContours > 0:
            pen = TTGlyphPen(None); g.draw(TransformPen(pen, (1, 0, t, 1, -t * y0, 0)), glyf); glyf[gn] = pen.glyph()
    for gn in f.getGlyphOrder():
        g = glyf[gn]
        if g.isComposite():
            for c in g.components: c.x = int(round(c.x + t * c.y))
    f['post'].italicAngle = -ANGLE
    f['hhea'].caretSlopeRise = 2048; f['hhea'].caretSlopeRun = int(round(2048 * t))

REF = sys.argv[7] if len(sys.argv) > 7 else None
if italic or REF:
    upright = TTFont(REF) if REF else TTFont(src)
    # crénage : on garde au moins un petit jour entre les lettres (italique, graisses extrêmes)
    class Flat(BasePen):
        def __init__(s, gs): super().__init__(gs); s.polys = []; s.cur = []
        def _moveTo(s, p): s.cur = [p]
        def _lineTo(s, p): s.cur.append(p)
        def _qCurveToOne(s, a, b):
            p0 = s.cur[-1]
            for i in range(1, 7):
                u = i / 6; s.cur.append(tuple((1 - u) ** 2 * p0[k] + 2 * u * (1 - u) * a[k] + u * u * b[k] for k in (0, 1)))
        def _curveToOne(s, a, b, c):
            p0 = s.cur[-1]
            for i in range(1, 7):
                u = i / 6; s.cur.append(tuple((1 - u) ** 3 * p0[k] + 3 * u * (1 - u) ** 2 * a[k] + 3 * u * u * (1 - u) * b[k] + u ** 3 * c[k] for k in (0, 1)))
        def _closePath(s): s.polys.append(s.cur); s.cur = []
    SC = 0.1; YLO, YHI = -800, 3000; H = int((YHI - YLO) * SC)
    def profile(font, gn):
        gs = font.getGlyphSet(); fp = Flat(gs); gs[gn].draw(fp)
        if not fp.polys: return None
        xs = [x for p in fp.polys for x, _ in p]; x0 = min(xs) - 10; W = int((max(xs) - x0) * SC) + 4
        acc = Image.new('1', (W, H), 0)
        for poly in fp.polys:
            m = Image.new('1', (W, H), 0); ImageDraw.Draw(m).polygon([((x - x0) * SC, (YHI - y) * SC) for x, y in poly], fill=1); acc = ImageChops.logical_xor(acc, m)
        a = np.array(acc, dtype=bool); has = a.any(axis=1)
        left = np.where(has, a.argmax(axis=1) / SC + x0, np.inf)
        right = np.where(has, (W - 1 - a[:, ::-1].argmax(axis=1)) / SC + x0, -np.inf)
        return left, right
    cmap = f.getBestCmap()
    chars = [c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,:;!?'\"()[]{}-/&@$%*+=<>«»" if ord(c) in cmap]
    names = [cmap[ord(c)] for c in chars]
    Pu = {n: profile(upright, n) for n in names}; Pi = {n: profile(f, n) for n in names}
    Ku = kern_dict(upright); added = {}
    for a in names:
        for b in names:
            if Pu[a] is None or Pu[b] is None: continue
            k = Ku.get((a, b), 0)
            gu = np.min(upright['hmtx'][a][0] + k + Pu[b][0] - Pu[a][1])
            gi = np.min(hmtx[a][0] + k + Pi[b][0] - Pi[a][1])
            target = min(gu, 70)
            if gi < target - 10: added[(a, b)] = k + int(round(target - gi))
    for st in f['kern'].kernTables: st.kernTable.update(added)
    print('paires de crénage ajoutées :', len(added))

# approche gauche = boîte réelle
for n in f.getGlyphOrder():
    g = glyf[n]; g.recalcBounds(glyf)
    hmtx[n] = (hmtx[n][0], g.xMin if g.numberOfContours else 0)

os2 = f['OS/2']; hh = f['hhea']
if metrics:
    hh.ascent, hh.descent, hh.lineGap = metrics['asc'], metrics['desc'], 0
    os2.sTypoAscender, os2.sTypoDescender, os2.sTypoLineGap = metrics['asc'], metrics['desc'], 0
    os2.usWinAscent, os2.usWinDescent = metrics['winasc'], metrics['windesc']
os2.version = max(os2.version, 4)
fs = os2.fsSelection & ~((1 << 0) | (1 << 5) | (1 << 6)) | (1 << 7)
if italic: fs |= 1
if weight == 700: fs |= (1 << 5)
if weight == 400 and not italic: fs |= (1 << 6)
os2.fsSelection = fs
os2.usWeightClass = weight
os2.sCapHeight = glyf['H'].yMax; os2.sxHeight = glyf['x'].yMax
os2.achVendID = 'LFST'
f['head'].macStyle = (1 if weight == 700 else 0) | (2 if italic else 0)
f['head'].fontRevision = 1.0

fam = 'Malabard'; full = f'{fam} {style}'; ps = f'{fam}-{style.replace(" ", "")}'
if style in ('Regular', 'Bold', 'Italic', 'Bold Italic'): n1, n2 = fam, style
elif italic: n1, n2 = f'{fam} {style.replace(" Italic", "")}', 'Italic'
else: n1, n2 = f'{fam} {style}', 'Regular'
COPY = ('Copyright (c) 2011 by Brian J. Bonislawsky DBA Astigmatic (AOETI) (astigma@astigmatic.com), with Reserved Font Name "Righteous". '
        'Modifications (Malabard) copyright (c) 2026 LaFleurStudio.')
names = {0: COPY, 1: n1, 2: n2, 3: f'1.000;LFST;{ps}', 4: full, 5: 'Version 1.000', 6: ps,
         8: 'LaFleurStudio', 9: 'LaFleurStudio',
         10: 'Malabard is a modified version of Righteous by Astigmatic, released under the SIL Open Font License 1.1.',
         13: 'This Font Software is licensed under the SIL Open Font License, Version 1.1. This license is available with a FAQ at: https://openfontlicense.org',
         14: 'https://openfontlicense.org', 16: fam, 17: style}
name = f['name']; name.names = []
for i, s in names.items():
    name.setName(s, i, 3, 1, 0x409); name.setName(s, i, 1, 0, 0)
f.save(out_ttf)
f2 = TTFont(out_ttf); f2.flavor = 'woff2'; f2.save(out_ttf.replace('.ttf', '.woff2').replace('/ttf/', '/woff2/'))
print('ok', out_ttf)
