# Clebard : CFF -> TrueType, noms, métriques, licence GUST (TeX Gyre Heros modifiée)
import sys
from fontTools.ttLib import TTFont, newTable
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib.tables._g_l_y_f import Glyph

src, out_ttf, style, weight = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
f = TTFont(src)
gs = f.getGlyphSet(); order = f.getGlyphOrder()

glyf = newTable('glyf'); glyf.glyphs = {}; glyf.glyphOrder = order
for n in order:
    pen = TTGlyphPen(None)
    gs[n].draw(Cu2QuPen(pen, max_err=0.5, reverse_direction=True))
    glyf.glyphs[n] = pen.glyph()
f['glyf'] = glyf
f['loca'] = newTable('loca')
del f['CFF ']
if 'VORG' in f: del f['VORG']
maxp = f['maxp']; maxp.tableVersion = 0x00010000
for a in ('maxZones', 'maxTwilightPoints', 'maxStorage', 'maxFunctionDefs', 'maxInstructionDefs',
          'maxStackElements', 'maxSizeOfInstructions', 'maxComponentElements', 'maxComponentDepth'):
    setattr(maxp, a, 0)
maxp.maxZones = 1
f['head'].glyphDataFormat = 0
f['post'].formatType = 2.0; f['post'].extraNames = []; f['post'].mapping = {}
f.sfntVersion = '\x00\x01\x00\x00'

# chasse/approche gauche = boîte réelle
for n in order:
    g = glyf[n]; g.recalcBounds(glyf)
    adv = f['hmtx'][n][0]
    f['hmtx'][n] = (adv, g.xMin if g.numberOfContours else 0)

# métriques verticales
ymax = max(glyf[n].yMax for n in order if glyf[n].numberOfContours)
ymin = min(glyf[n].yMin for n in order if glyf[n].numberOfContours)
cm = f.getBestCmap()
lat = [cm[c] for c in cm if c < 0x250 and glyf[cm[c]].numberOfContours]
la_max = max(glyf[n].yMax for n in lat); la_min = min(glyf[n].yMin for n in lat)
os2 = f['OS/2']; hh = f['hhea']
os2.version = max(os2.version, 4)
hh.ascent, hh.descent, hh.lineGap = la_max, la_min, 0
os2.sTypoAscender, os2.sTypoDescender, os2.sTypoLineGap = la_max, la_min, 0
os2.usWinAscent, os2.usWinDescent = ymax, -ymin
os2.fsSelection = (os2.fsSelection | (1 << 7)) & ~((1 << 0) | (1 << 5)) | (1 << 6)   # USE_TYPO_METRICS, Regular
os2.usWeightClass = weight
os2.sCapHeight = glyf['H'].yMax; os2.sxHeight = glyf['x'].yMax
os2.achVendID = 'LFST'
os2.fsType = 0                       # installation et intégration libres
f['head'].macStyle = 0

fam = 'Clebard'; full = f'{fam} {style}'; ps = f'{fam}-{style}'
COPY = ('Copyright 2007-2009 B. Jackowski and J.M. Nowacki (TeX Gyre Heros, based on URW Nimbus Sans L released by URW++ under the GUST Font License). '
        'Modifications (Clebard) 2026 LaFleurStudio.')
names = {0: COPY, 1: full, 2: 'Regular', 3: f'1.000;LFST;{ps}', 4: full, 5: 'Version 1.000', 6: ps,
         8: 'LaFleurStudio', 9: 'LaFleurStudio',
         10: 'Clebard is a modified version of TeX Gyre Heros, released under the GUST Font License.',
         13: 'This font is released under the GUST Font License (GFL), an instance of the LaTeX Project Public License (LPPL) 1.3c or later.',
         14: 'http://www.gust.org.pl/fonts/licenses/GUST-FONT-LICENSE.txt', 16: fam, 17: style}
name = f['name']; name.names = []
for i, s in names.items():
    name.setName(s, i, 3, 1, 0x409)
    name.setName(s, i, 1, 0, 0)
f.save(out_ttf)
f2 = TTFont(out_ttf); f2.flavor = 'woff2'; f2.save(out_ttf.replace('.ttf', '.woff2').replace('/ttf/', '/woff2/'))
print('ok', out_ttf, 'asc', la_max, 'desc', la_min, 'win', ymax, ymin)
