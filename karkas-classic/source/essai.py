# image d'essai : python3 essai.py sortie.png "MOT" "-MOT sans liaisons" ...
import sys
from PIL import Image, ImageDraw
from fontTools.pens.recordingPen import RecordingPen
import cla_letters as cl
from kar_core import *
import kar_liga
kar_liga.letter = cl.letter; kar_liga.LM = cl.LM; kar_liga.RM = cl.RM; kar_liga.wedge = lambda *a: None
def contours(p, n=12):
    rp = RecordingPen(); p.draw(rp); cs = []; cur = []
    for op, a in rp.value:
        if op == 'moveTo': cur = [a[0]]
        elif op == 'lineTo': cur.append(a[0])
        elif op == 'curveTo':
            p0 = cur[-1]
            for i in range(1, n + 1):
                t = i / n; m = 1 - t; cur.append(tuple(m**3 * p0[j] + 3 * m * m * t * a[0][j] + 3 * m * t * t * a[1][j] + t**3 * a[2][j] for j in (0, 1)))
        elif op == 'closePath': cs.append(cur)
    return cs
def area(c): return sum(c[i][0] * c[(i + 1) % len(c)][1] - c[(i + 1) % len(c)][0] * c[i][1] for i in range(len(c))) / 2
def line(w, text, G, liga=True):
    x = 0; out = []
    for wi, word in enumerate(text.split(' ')):
        if wi: x += round(1.6 * w.W)
        for seg in (kar_liga.segment(word, G) if liga else list(word)):
            g = kar_liga.draw(w, *G[seg]) if len(seg) > 1 else cl.letter(seg, w)
            out.append(mv(g.ink, x)); x += g.w + w.G
    return out, x
if __name__ == '__main__':
    outp = sys.argv[1]; G = {k: v for k, v in kar_liga.groups().items() if all(c in kar_liga.AZ for c in k)}; sc = 0.34; pad = 40; rows = []
    for text in sys.argv[2:]:
        for nom, w in cl.WEIGHTS.items(): rows.append((w, text))
    lines = [line(w, t.lstrip('-'), G, not t.startswith('-')) for w, t in rows]
    Wd = int(max(x for _, x in lines) * sc) + 2 * pad; Hh = int(1040 * sc)
    im = Image.new('L', (Wd * 2, Hh * len(rows) * 2 + 2 * pad), 255); d = ImageDraw.Draw(im)
    for r, (inks, x) in enumerate(lines):
        base = pad + (r * Hh + int(900 * sc)) * 2
        for p in inks:
            q = U(p); q.simplify(fix_winding=True, clockwise=False)
            for c in sorted(contours(q), key=lambda c: -abs(area(c))):
                d.polygon([(2 * (pad + v[0] * sc), base - 2 * v[1] * sc) for v in c], fill=0 if area(c) > 0 else 255)
    im.resize((Wd, im.size[1] // 2), Image.LANCZOS).save(outp)
