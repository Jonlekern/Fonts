# Planche : LAFLEURSTUDIO de l'essai, chaque trait découpé en segments droits colorés par famille d'angle.
import sys, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
_ICI = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [_ICI, os.path.join(_ICI, '..', 'jalousia')]
import essai
from etude import study

def police(t, gras=False):
    try:
        return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf' % ('-Bold' if gras else ''), t)
    except OSError:
        return ImageFont.load_default()

FAM = [('barre', 0, 2.5, (90, 170, 255), 'barres 0°'),
       ('main', 2.5, 6, (70, 220, 230), 'à la main ~4°'),
       ('pied', 6, 10, (80, 220, 140), 'pieds ~8°'),
       ('attaque', 10, 28, (255, 210, 60), 'attaques ~15°'),
       ('oblique', 28, 52, (255, 140, 60), 'obliques ~40°'),
       ('diag', 52, 72, (255, 70, 70), 'diagonales ~67°'),
       ('penche', 72, 85, (180, 120, 255), 'fûts penchés ~77°'),
       ('droit', 85, 90.1, (240, 240, 240), 'fûts ~88°')]

def fam(a):
    A = abs(a)
    for f in FAM:
        if f[1] <= A < f[2]:
            return f
    return FAM[-1]

res = study()
k = 0.42
rows = ['LAFLEUR', 'STUDIO']
F = police(19, True)
imgs = []
for word in rows:
    xs, end = essai.layout(word)
    top, bot = 1250, -320
    W = int((end + 400) * k); H = int((top - bot) * k)
    im = Image.new('RGB', (W, H), (0, 0, 0))
    d = ImageDraw.Draw(im)
    T = lambda x, y, ox: ((x + ox + 200) * k, (top - y) * k)
    for ch, ox in zip(word, xs):
        for s in essai.G[ch]:
            P = [T(x, y, ox) for x, y in essai.cr(s)]
            d.line(P, fill=(70, 70, 70), width=9)
    labels = []
    for ch, ox in zip(word, xs):
        for sg in res[ch]:
            if sg['short']: continue
            f = fam(sg['angle'])
            p = T(*sg['p'], ox); q = T(*sg['q'], ox)
            d.line([p, q], fill=f[3], width=4)
            if sg['length'] > 180:
                a = abs(sg['angle'])
                labels.append(((p[0] + q[0]) / 2, (p[1] + q[1]) / 2, f"{a:.0f}°", f[3]))
    for x, y, t, c in labels:
        tw = d.textlength(t, font=F)
        d.rectangle([x + 6, y - 11, x + 10 + tw, y + 12], fill=(0, 0, 0))
        d.text((x + 8, y - 11), t, font=F, fill=c)
    imgs.append(im)

W = max(i.width for i in imgs) + 40
H = sum(i.height for i in imgs) + 150
sheet = Image.new('RGB', (W, H), (0, 0, 0))
y = 10
for i in imgs:
    sheet.paste(i, (20, y)); y += i.height
d = ImageDraw.Draw(sheet)
F2 = police(24)
x, y = 30, y + 20
for f in FAM:
    d.rectangle([x, y + 7, x + 28, y + 19], fill=f[3])
    d.text((x + 36, y), f[4], font=F2, fill=(230, 230, 230))
    x += 60 + d.textlength(f[4], font=F2)
    if x > W - 300:
        x, y = 30, y + 44
sheet.save(sys.argv[1] if len(sys.argv) > 1 else 'etude.png')
print(sheet.size)
