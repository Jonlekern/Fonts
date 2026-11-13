# Planche de gros plans : python3 zooms.py police.otf defauts.json sortie_prefixe [types] [glyphes...]
import sys, json, math
from PIL import Image, ImageDraw, ImageFont, ImageChops
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
font, js, outp = sys.argv[1:4]
kinds = set(sys.argv[4].split(',')) if len(sys.argv) > 4 else {'echarde', 'fente', 'marche'}
only = set(sys.argv[5:])
t = TTFont(font); gs = t.getGlyphSet(); d = json.load(open(js))
LAB = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
WIN, SC, CELL = 200, 1.3, 260

def polys(g):
    rp = RecordingPen(); gs[g].draw(rp); out = []; cur = []
    for op, a in rp.value:
        if op == 'moveTo': cur = [a[0]]
        elif op == 'lineTo': cur.append(a[0])
        elif op == 'curveTo':
            p0 = cur[-1]; p1, p2, p3 = a
            for i in range(1, 25):
                s = i / 24; m = 1 - s
                cur.append(tuple(m**3*p0[j] + 3*m*m*s*p1[j] + 3*m*s*s*p2[j] + s**3*p3[j] for j in (0, 1)))
        elif op in ('closePath', 'endPath'):
            if len(cur) > 2: out.append(cur)
            cur = []
    return out

items = []
for g, v in d.items():
    if only and g not in only: continue
    if not only and (g.startswith('uni') and len(g) == 7 or g in ('asciitilde', 'tilde')): continue
    for k, x, y, a in v:
        if k in kinds: items.append((g, k, x, y, a))
cols = 6; per = 36
for page in range(0, len(items), per):
    chunk = items[page:page + per]; rows = -(-len(chunk) // cols)
    im = Image.new('RGB', (cols * CELL, rows * (CELL + 24)), (244, 241, 236)); dr = ImageDraw.Draw(im)
    for i, (g, k, x, y, a) in enumerate(chunk):
        cx0 = (i % cols) * CELL; cy0 = (i // cols) * (CELL + 24)
        m = Image.new('1', (CELL, CELL), 0)
        for c in polys(g):
            mm = Image.new('1', (CELL, CELL), 0)
            ImageDraw.Draw(mm).polygon([((p[0] - x) * SC + CELL / 2, CELL / 2 - (p[1] - y) * SC) for p in c], fill=1)
            m = ImageChops.logical_xor(m, mm)
        tile = Image.new('RGB', (CELL, CELL), (250, 248, 244)); tile.paste((20, 20, 20), mask=m)
        im.paste(tile, (cx0, cy0))
        r = 26; dr.ellipse([cx0 + CELL / 2 - r, cy0 + CELL / 2 - r, cx0 + CELL / 2 + r, cy0 + CELL / 2 + r], outline=(220, 40, 30), width=2)
        dr.text((cx0 + 6, cy0 + CELL + 3), f'{page + i + 1}. {g} {k} ({x},{y})', font=LAB, fill=(60, 60, 60))
        dr.rectangle([cx0, cy0, cx0 + CELL - 1, cy0 + CELL - 1], outline=(215, 208, 198))
    im.save(f'{outp}-{page // per}.png')
print(len(items), 'gros plans,', -(-len(items) // per), 'planches')
