"""Fonctions OpenType de DIHEDRON-008 : crénage (kern) et placement des accents combinants (mark).
Remplace kern_dihedron.py : les deux fonctions sont compilées ensemble.
usage : feat_dihedron.py police.ttf sortie.ttf"""
import sys, unicodedata
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
import kern_dihedron as K

SPECIAL = {'Ø': 'O', 'ø': 'o', 'Ł': 'L', 'ł': 'l', 'Đ': 'D', 'Ð': 'D', 'đ': 'd', 'Ħ': 'H', 'ħ': 'h', 'Þ': 'P', 'þ': 'p', 'ȷ': 'j'}
TOP = ['̀', '́', '̂', '̃', '̄', '̆', '̇', '̈', '̊', '̋', '̌']
BOT = ['̦', '̧']
OGO = ['̨']
XH, CAPTOP = 490, 690               # le haut des minuscules, et des capitales (là où se posent les accents)

def groups(f, names):
    rev = {v: k for k, v in f.getBestCmap().items()}; g = {ch: [n] for ch, n in names.items()}
    for n in f.getGlyphOrder():
        u = rev.get(n)
        if not u: continue
        ch = chr(u); base = SPECIAL.get(ch) or unicodedata.normalize('NFD', ch)[0]
        if base in g and ch != base and n not in g[base]: g[base].append(n)
    return g

def mark_fea(f):
    cm = f.getBestCmap(); gs = f.getGlyphSet(); glyf = f['glyf']
    gname = lambda ch: cm[ord(ch)]
    out = []
    for cls, lst in (('TOP', TOP), ('BOT', BOT), ('OGO', OGO)):
        y = XH if cls == 'TOP' else 0
        for ch in lst:
            if ord(ch) in cm: out.append(f'markClass {gname(ch)} <anchor 0 {y}> @{cls};')
    bases = []
    for u, n in sorted(cm.items()):
        ch = chr(u)
        if not (ch.isalpha() and unicodedata.category(ch) in ('Lu', 'Ll')): continue
        if unicodedata.category(ch) == 'Ll' and len(unicodedata.normalize('NFD', ch)) > 1: continue   # déjà accentuée
        b = BoundsPen(gs); gs[n].draw(b)
        if not b.bounds: continue
        x0, y0, x1, y1 = b.bounds; cx = round((x0 + x1) / 2)
        tall = y1 > XH + 120
        ty = CAPTOP if tall else XH
        # pied droit pour l'ogonek : le point le plus à droite en bas
        g = glyf[n]; coords = g.getCoordinates(glyf)[0]
        lows = [x for x, y in coords if y < 40]
        ox = round(max(lows) - 60) if lows else cx
        bases.append(f'  pos base {n} <anchor {cx} {ty}> mark @TOP <anchor {cx} 0> mark @BOT <anchor {ox} 0> mark @OGO;')
    out.append('feature mark {'); out += bases; out.append('} mark;')
    return '\n'.join(out)

def kern_fea(f):
    pairs, names = K.kerning(f); gr = groups(f, names)
    fea = []
    for ch, gl in gr.items():
        fea.append(f'@L_{ord(ch)} = [{" ".join(gl)}];'); fea.append(f'@R_{ord(ch)} = [{" ".join(gl)}];')
    fea.append('feature kern {')
    for (a, b), k in sorted(pairs.items()): fea.append(f'  pos @L_{ord(a)} @R_{ord(b)} {k};')
    fea.append('} kern;')
    return '\n'.join(fea), len(pairs)

if __name__ == '__main__':
    f = TTFont(sys.argv[1]); kf, n = kern_fea(f); mf = mark_fea(f)
    addOpenTypeFeaturesFromString(f, mf + '\n' + kf); f.save(sys.argv[2])
    print(sys.argv[1].split('/')[-1], n, 'paires de crénage')
