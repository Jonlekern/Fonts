# python3 ep_planche.py sortie.png "texte|texte2" [poids,chrome,vitesse ...]
import sys, math; sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageChops
from tuyaux import aplatis, penche
from mesures import mesures
from dessin import D, lettre
import importlib
G = {}
for mod, nom in (('minuscules', 'MINUSCULES'), ('capitales', 'CAPITALES'), ('chiffres', 'CHIFFRES'), ('signes', 'SIGNES')):
    try:
        G.update(getattr(importlib.import_module(mod), nom))
    except ModuleNotFoundError:
        pass

import os, json
SURCHARGE = json.loads(os.environ.get('M', '{}'))

def ligne(img, texte, m, chrome, pente, x0, ybase, s):
    m.update(SURCHARGE)
    if 'fut' in SURCHARGE: m['barre'] = m['fut'] * SURCHARGE.get('rapport', 0.8); m['coude'] = SURCHARGE.get('coude', m['coude'])
    x = x0; d = D(m)
    for ch in texte:
        if ch == ' ':
            x += (240 + m['air']) * s; continue
        tuy, ch_w = G[ch](d); lettre(tuy, m)
        for tu in tuy:
            cs = penche(tu.contours(m, chrome), pente, 350)
            if tu.ferme and not tu.disque:
                for i in range(0, len(cs), 2):
                    ma = Image.new('1', img.size, 0); mb = Image.new('1', img.size, 0)
                    ImageDraw.Draw(ma).polygon([(x + px * s, ybase - py * s) for px, py in aplatis(cs[i])], fill=1)
                    ImageDraw.Draw(mb).polygon([(x + px * s, ybase - py * s) for px, py in aplatis(cs[i + 1])], fill=1)
                    img.paste(0, mask=ImageChops.logical_xor(ma, mb))
            else:
                dr = ImageDraw.Draw(img)
                for c in cs:
                    dr.polygon([(x + px * s, ybase - py * s) for px, py in aplatis(c)], fill=0)
        ImageDraw.Draw(img).line([(x, ybase + 8), (x, ybase + 22)], fill=150)
        x += ((ch_w - 2 * m['app']) * m.get('serre', 1) + 2 * m['app'] + m['air']) * s

sortie = sys.argv[1]; textes = sys.argv[2].split('|')
reglages = [tuple(float(v) for v in a.split(',')) for a in sys.argv[3:]] or [(500, 0, 0)]
s = float(__import__('os').environ.get('ECH', 0.26)); H = int(1150 * s)
img = Image.new('L', (2600, H * len(textes) * len(reglages) + 30), 255)
k = 0
for p, c, v in reglages:
    for t in textes:
        ligne(img, t, mesures(int(p), vitesse=v), c, math.tan(math.radians(14)) * v, 30, int(H * k + 830 * s), s); k += 1
img.save(sortie)
