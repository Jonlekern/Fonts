# aperçu rapide : python3 apercu.py sortie.png "MOT" "MOT"...   (avant la fabrique : dessine les mots avec les mêmes règles)
import sys
from PIL import Image, ImageDraw
from fontTools.pens.recordingPen import RecordingPen
from kar_core import *
from kar_letters import letter
from kar_liga import groups, draw, segment
def contours(p):
    rp = RecordingPen(); p.draw(rp); cs = []; cur = []
    for op, a in rp.value:
        if op == 'moveTo': cur = [a[0]]
        elif op == 'lineTo': cur.append(a[0])
        elif op == 'closePath': cs.append(cur)
    return cs
def area(c): return sum(c[i][0] * c[(i + 1) % len(c)][1] - c[(i + 1) % len(c)][0] * c[i][1] for i in range(len(c))) / 2
def line(w, text, G, liga=True):
    x = 0; out = []
    for wi, word in enumerate(text.split(' ')):
        if wi: x += round(0.9 * w.W)
        for seg in (segment(word, G) if liga else list(word)):
            g = draw(w, *G[seg]) if len(seg) > 1 else letter(seg, w)
            out.append(mv(g.ink, x)); x += g.w + w.G
    return out, x
if __name__ == '__main__':
    outp = sys.argv[1]; words = sys.argv[2:]; G = groups(); sc = 0.36; pad = 40; rows = []
    for text in words:
        for nom, w in WEIGHTS.items(): rows.append((w, text))
    lines = [line(w, t.lstrip('-'), G, not t.startswith('-')) for w, t in rows]
    Wd = int(max(x for _, x in lines) * sc) + 2 * pad; Hh = int(1000 * sc)
    im = Image.new('L', (Wd * 2, Hh * len(rows) * 2 + 2 * pad), 255); d = ImageDraw.Draw(im)
    for r, (inks, x) in enumerate(lines):
        base = pad + (r * Hh + int(880 * sc)) * 2
        for p in inks:
            cs = sorted(contours(p), key=lambda c: -abs(area(c)))
            for c in cs:
                d.polygon([(2 * (pad + q[0] * sc), base - 2 * q[1] * sc) for q in c], fill=0 if area(c) > 0 else 255)
    im.resize((Wd, im.size[1] // 2), Image.LANCZOS).save(outp)
