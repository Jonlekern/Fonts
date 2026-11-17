# python3 ep_planche.py sortie.png "texte|texte2" [poids,chrome,vitesse ...]
import os, sys, math; sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageChops
from tuyaux import aplatis, penche
from mesures import mesures
from dessin import D, lettre
import importlib
G = {}
for mod, nom in ((('minuscules', 'MINUSCULES'), ('capitales', 'CAPITALES'), ('chiffres', 'CHIFFRES'), ('signes', 'SIGNES')) if not os.environ.get('BLOCS') else (('blocs', 'BLOCS'),)):
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
        if os.environ.get('GRIFFE') and ch != ' ':
            # maquette de la griffe : trois petites entailles dans le flanc gauche, à la taille
            px = img.load(); F = m['fut']; pas = F * 0.20; prof = F * 0.50; haut = max(2, int(F * 0.075 * s))
            ym = m['cap'] * 0.36 if ch.isupper() else m['x'] * 0.42
            for k in (-1, 0, 1):
                yy = int(ybase - (ym + k * pas) * s)
                x0 = None
                for xx in range(int(x), int(x + ch_w * s)):
                    if px[xx + int(pente * (ym + k * pas - 350) * s), yy] < 128:
                        x0 = xx + int(pente * (ym + k * pas - 350) * s); break
                if x0 is not None:
                    ImageDraw.Draw(img).rectangle([x0 - 2, yy - haut // 2, x0 + int(prof * s) + k * int(prof * s * 0.25), yy + haut // 2], fill=255)
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
