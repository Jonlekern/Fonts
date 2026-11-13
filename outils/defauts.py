# Chasse aux défauts de contour, glyphe par glyphe :
#  - écharde : morceau d'encre plus fin que 2r (ouverture morphologique)
#  - fente   : blanc plus étroit que 2r qui entre dans l'encre (fermeture morphologique)
#  - marche  : petit segment droit entre deux bords parallèles (zigzag)
# python3 defauts.py police.otf [r] [sortie.json] [glyphes...]   (sans liste : tous les glyphes)
import sys, math, json
import numpy as np
from scipy import ndimage as ndi
from PIL import Image, ImageDraw, ImageChops
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.basePen import decomposeQuadraticSegment

path = sys.argv[1]; R = float(sys.argv[2]) if len(sys.argv) > 2 else 5.0
OUT = sys.argv[3] if len(sys.argv) > 3 else None
t = TTFont(path); gs = t.getGlyphSet()
PAD = 40

def contours(g):
    rp = DecomposingRecordingPen(gs); gs[g].draw(rp); cs = []; cur = []; segs = []; cs_segs = []
    for op, a in rp.value:
        if op == 'moveTo':
            cur = [a[0]]; segs = []
        elif op == 'lineTo':
            segs.append(('L', cur[-1], a[0])); cur.append(a[0])
        elif op in ('curveTo', 'qCurveTo'):
            # TrueType : courbes à plusieurs points de contrôle, et contours sans point sur la courbe
            if op == 'qCurveTo' and a[-1] is None:
                dep = tuple((a[-2][j] + a[0][j]) / 2 for j in (0, 1)); cur = [dep]; segs = []; a = a[:-1] + (dep,)
            morceaux = decomposeQuadraticSegment(a) if op == 'qCurveTo' else [a]
            for mc in morceaux:
                p0 = cur[-1]
                if op == 'qCurveTo':
                    q1, p3 = mc; p1 = tuple(p0[j] + 2 / 3 * (q1[j] - p0[j]) for j in (0, 1)); p2 = tuple(p3[j] + 2 / 3 * (q1[j] - p3[j]) for j in (0, 1))
                else:
                    p1, p2, p3 = mc
                segs.append(('C', p0, p1, p2, p3))
                for i in range(1, 25):
                    s = i / 24; m = 1 - s
                    cur.append(tuple(m**3*p0[j] + 3*m*m*s*p1[j] + 3*m*s*s*p2[j] + s**3*p3[j] for j in (0, 1)))
        elif op in ('closePath', 'endPath'):
            if len(cur) > 2:
                if math.dist(cur[-1], cur[0]) > 1e-6: segs.append(('L', cur[-1], cur[0]))
                cs.append(cur); cs_segs.append(segs)
            cur = []
    return cs, cs_segs

def raster(cs, bb):
    x0, y0, x1, y1 = bb; W = int(x1 - x0) + 2 * PAD; H = int(y1 - y0) + 2 * PAD
    img = Image.new('1', (W, H), 0)
    for c in cs:
        m = Image.new('1', (W, H), 0)
        ImageDraw.Draw(m).polygon([(p[0] - x0 + PAD, y1 - p[1] + PAD) for p in c], fill=1)
        img = ImageChops.logical_xor(img, m)
    return np.array(img, dtype=bool)

def disk(r):
    n = int(math.ceil(r)); y, x = np.mgrid[-n:n + 1, -n:n + 1]; return x * x + y * y <= r * r + 0.5

def blobs(mask, minarea):
    lab, n = ndi.label(mask); out = []
    for i, sl in enumerate(ndi.find_objects(lab), 1):
        a = int((lab[sl] == i).sum())
        if a >= minarea: out.append((a, sl))
    return out

def tangent(seg, at_end):
    if seg[0] == 'L': p, q = seg[1], seg[2]
    else:
        p0, p1, p2, p3 = seg[1:]
        if at_end: p, q = (p2 if math.dist(p2, p3) > 1e-6 else p1), p3
        else: p, q = p0, (p1 if math.dist(p0, p1) > 1e-6 else p2)
    d = (q[0] - p[0], q[1] - p[1]); L = math.hypot(*d) or 1
    return (d[0] / L, d[1] / L)

def jogs(cs_segs, maxlen=34):
    found = []
    for segs in cs_segs:
        n = len(segs)
        for i, s in enumerate(segs):
            if s[0] != 'L': continue
            L = math.dist(s[1], s[2])
            if L < 0.5 or L > maxlen: continue
            prev, nxt = segs[i - 1], segs[(i + 1) % n]
            a = tangent(prev, True); b = tangent(nxt, False)
            par = a[0] * b[0] + a[1] * b[1]
            if par > 0.94:                       # les voisins vont dans le même sens : zigzag = marche
                lp = math.dist(prev[1], prev[-1]); ln = math.dist(nxt[1], nxt[-1])
                if lp > L and ln > L:
                    found.append(((s[1][0] + s[2][0]) / 2, (s[1][1] + s[2][1]) / 2, round(L, 1)))
    return found

res = {}
SEULS = set(sys.argv[4:])
for g in t.getGlyphOrder():
    if SEULS and g.split('.')[0] not in SEULS: continue
    if g in ('.notdef', 'space', 'uni00A0'): continue
    cs, cs_segs = contours(g)
    if not cs: continue
    xs = [p[0] for c in cs for p in c]; ys = [p[1] for c in cs for p in c]
    bb = (math.floor(min(xs)), math.floor(min(ys)), math.ceil(max(xs)), math.ceil(max(ys)))
    ink = raster(cs, bb); D = disk(R)
    opened = ndi.binary_opening(ink, D); closed = ndi.binary_closing(ink, D)
    sl = blobs(ink & ~opened, 14); fe = blobs(closed & ~ink, 14)
    def pos(s):
        yy, xx = s; cx = (xx.start + xx.stop) / 2 - PAD + bb[0]; cy = bb[3] - ((yy.start + yy.stop) / 2 - PAD)
        return round(cx), round(cy)
    items = [('echarde', *pos(s), a) for a, s in sl] + [('fente', *pos(s), a) for a, s in fe] + \
            [('marche', round(x), round(y), L) for x, y, L in jogs(cs_segs)]
    if items: res[g] = items
if OUT: json.dump(res, open(OUT, 'w'), indent=0)
tot = {k: sum(1 for v in res.values() for i in v if i[0] == k) for k in ('echarde', 'fente', 'marche')}
print(path.split('/')[-1], 'glyphes touchés:', len(res), tot)
