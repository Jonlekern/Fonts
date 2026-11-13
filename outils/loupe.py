# La loupe : chaque lettre de la police, en très grand, sur des planches.
#
#   python3 outils/loupe.py police.otf dossier_sortie [glyphes...]
#
# Sans liste, toutes les lettres de la police y passent. Avec une liste : des noms de glyphes ou les lettres elles-mêmes.
# Chaque case montre une lettre en noir, entourée de sa chasse (traits gris) et de la ligne de base.
# Les contours sont remplis en pair-impair : un recouvrement oublié sort en blanc, il saute aux yeux.
import sys, os, math
from PIL import Image, ImageDraw, ImageFont, ImageChops
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.basePen import decomposeQuadraticSegment

police, sortie = sys.argv[1], sys.argv[2]
t = TTFont(police); gs = t.getGlyphSet(); upm = t['head'].unitsPerEm
cm = t.getBestCmap()
# on peut donner des noms de glyphes ou des lettres tapées : « a é ß Q »
noms = []
for a in sys.argv[3:]:
    if a in gs: noms.append(a)
    elif len(a) == 1 and ord(a) in cm: noms.append(cm[ord(a)])
    else: print('pas dans la police :', a)
noms = noms or [g for g in t.getGlyphOrder() if g not in ('.notdef', 'space', 'nbspace')]
CASE, COLS, LIGNES, SUR = 560, 3, 2, 3          # case de 560 px, 6 lettres par planche, dessin 3x plus fin puis réduit
ECH = CASE * 0.62 / upm                          # 1 em = 62 % de la case : environ 0,35 px par unité
os.makedirs(sortie, exist_ok=True)
try:
    LAB = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
except OSError:
    LAB = ImageFont.load_default()
asc = t['OS/2'].sTypoAscender; desc = t['OS/2'].sTypoDescender

def contours(g):
    rp0 = DecomposingRecordingPen(gs); gs[g].draw(rp0)          # les lettres composées (accents) sont dépliées
    rp = rp0
    out = []; cur = []
    for op, a in rp.value:
        if op == 'moveTo': cur = [a[0]]
        elif op == 'lineTo': cur.append(a[0])
        elif op in ('curveTo', 'qCurveTo'):
            # TrueType : une courbe peut porter plusieurs points de contrôle, on la découpe en morceaux simples
            if op == 'qCurveTo' and a[-1] is None:                # contour fait seulement de points hors courbe
                dep = tuple((a[-2][i] + a[0][i]) / 2 for i in (0, 1)); cur = [dep]; a = a[:-1] + (dep,)
            morceaux = decomposeQuadraticSegment(a) if op == 'qCurveTo' else [a]
            for mc in morceaux:
                p0 = cur[-1]
                if op == 'qCurveTo':
                    q1, p3 = mc; p1 = tuple(p0[i] + 2 / 3 * (q1[i] - p0[i]) for i in (0, 1)); p2 = tuple(p3[i] + 2 / 3 * (q1[i] - p3[i]) for i in (0, 1))
                else:
                    p1, p2, p3 = mc
                for k in range(1, 41):
                    s = k / 40; m = 1 - s
                    cur.append(tuple(m**3*p0[i] + 3*m*m*s*p1[i] + 3*m*s*s*p2[i] + s**3*p3[i] for i in (0, 1)))
        elif op in ('closePath', 'endPath'):
            if len(cur) > 2: out.append(cur)
            cur = []
    return out

def case(g):
    adv = gs[g].width; x0 = (CASE / ECH - adv) / 2; yb = CASE * 0.24   # ligne de base à 24 % du bas
    P = lambda p: (((p[0] + x0) * ECH) * SUR, (CASE - yb - p[1] * ECH) * SUR)
    m = Image.new('1', (CASE * SUR, CASE * SUR), 0)
    for c in contours(g):
        mm = Image.new('1', m.size, 0); ImageDraw.Draw(mm).polygon([P(p) for p in c], fill=1)
        m = ImageChops.logical_xor(m, mm)
    m = m.convert('L').resize((CASE, CASE), Image.LANCZOS)
    im = Image.new('RGB', (CASE, CASE), (250, 248, 244)); d = ImageDraw.Draw(im)
    for y in (0, asc, desc):
        yy = CASE - yb - y * ECH; d.line([(0, yy), (CASE, yy)], fill=(222, 216, 206))
    for x in (0, adv):
        xx = (x + x0) * ECH; d.line([(xx, 0), (xx, CASE)], fill=(222, 216, 206))
    im.paste((18, 18, 18), mask=m)
    u = t.getBestCmap(); cp = [k for k, v in u.items() if v == g]
    d.text((10, CASE - 24), g + (f'  U+{cp[0]:04X}' if cp else ''), font=LAB, fill=(90, 90, 90))
    d.rectangle([0, 0, CASE - 1, CASE - 1], outline=(205, 198, 188))
    return im

par = COLS * LIGNES
for n in range(0, len(noms), par):
    pl = Image.new('RGB', (CASE * COLS, CASE * LIGNES), (244, 241, 236))
    for i, g in enumerate(noms[n:n + par]):
        pl.paste(case(g), ((i % COLS) * CASE, (i // COLS) * CASE))
    pl.save(os.path.join(sortie, f'loupe-{n // par + 1:03d}.png'))
print(len(noms), 'lettres,', math.ceil(len(noms) / par), 'planches dans', sortie)
