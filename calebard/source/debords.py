"""Débords de chasse : la corne de Ơ Ư, le caron de Ľ et les ogoneks (Ą ą Į į Ų ų…) ne sortent plus à droite.

Règle (les 11 graisses) : si le dessin sort à droite de la chasse, la chasse s'allonge pour que le bout
de la corne, de l'accent ou de l'ogonek garde à droite la moitié de l'approche droite de la lettre de base
(O pour Ơ, U pour Ư, L pour Ľ, A pour Ą…). Les variantes (.ss01…) suivent leur lettre de base.
Goofy et Extra Goofy (faites depuis le Black) prennent le même allongement que le Black, variante par variante.
Seule la chasse change (et la largeur moyenne xAvgCharWidth) : les contours, les accents et le crénage ne bougent pas.
On peut le relancer : ce qui est déjà fait ne bouge plus.

usage : python3 debords.py dossier-ttf
"""
import os, sys, unicodedata
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen

D = sys.argv[1]
GRAISSES = ['Hairline', 'Thin', 'Light', 'Regular', 'Medium', 'Bold', 'ExtraBold', 'SuperBold', 'Black', 'ExtraBlack', 'ExtremeBlack']


def cibles(f):
    """{glyphe: lettre de base} pour les lettres à corne, à ogonek, et Ľ, variantes comprises."""
    cm = f.getBestCmap(); base = {}
    for c, g in cm.items():
        d = unicodedata.normalize('NFD', chr(c))
        if unicodedata.category(chr(c))[0] != 'L': continue
        if '̛' in d or '̨' in d or chr(c) == 'Ľ':
            base[g] = cm[ord(d[0])]
    for g in f.getGlyphOrder():                      # variantes : aogonek.ss01 → a.ss01
        if '.' in g and g.split('.')[0] in base:
            b = base[g.split('.')[0]] + '.' + g.split('.', 1)[1]
            base[g] = b if b in f.getGlyphOrder() else base[g.split('.')[0]]
    return base


def droite(gs, g):
    p = BoundsPen(gs); gs[g].draw(p); return p.bounds[2] if p.bounds else None


allonge_black = {}
for w in GRAISSES:
    chemin = os.path.join(D, f'Calebard-{w}.ttf'); f = TTFont(chemin); gs = f.getGlyphSet(); hm = f['hmtx'].metrics
    faits = []
    for g, b in cibles(f).items():
        xmax = droite(gs, g); xb = droite(gs, b)
        if xmax is None or xb is None: continue
        approche = hm[b][0] - xb
        voulu = round(xmax + max(approche, 0) / 2)
        if voulu > hm[g][0]:
            faits.append((g, voulu - hm[g][0])); hm[g] = (voulu, hm[g][1])
            if w == 'Black': allonge_black[g] = faits[-1][1]
    f['OS/2'].recalcAvgCharWidth(f)
    f.save(chemin)
    print(w, len(faits), 'chasses allongées', ' '.join(f'{g}+{d}' for g, d in faits))

for nom in ('Goofy', 'ExtraGoofy'):
    chemin = os.path.join(D, f'Calebard-{nom}.ttf'); f = TTFont(chemin); hm = f['hmtx'].metrics; n = 0
    for g in f.getGlyphOrder():
        racine = g[:-len('.goofy')] if g.endswith('.goofy') else (g.rsplit('.', 1)[0] if g.rsplit('.', 1)[-1][:2] == 'eg' else g)
        if racine in allonge_black:
            hm[g] = (hm[g][0] + allonge_black[racine], hm[g][1]); n += 1
    f['OS/2'].recalcAvgCharWidth(f)
    f.save(chemin)
    print(nom, n, 'chasses allongées (comme le Black)')
