# Une graisse : python3 fabrique.py <fût> <nom> <poids> <sortie.otf>
import os, sys
os.environ['W'] = sys.argv[1]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core as K
import lower, caps, digits, signs, marks
name, weight, outf = sys.argv[2], int(sys.argv[3]), sys.argv[4]
gl = []
for n, fn in K.GLYPHS.items():
    if '.' in n and n.split('.')[1] in ('a', 'b', 'c'): continue        # variantes d'essai
    p, l, r = fn(); gl.append((n, K.clean(p), l, r))
MATH = {'plus', 'uni2212', 'equal', 'multiply', 'divide', 'less', 'greater'}
mw = max(l + (p.bounds[2] - p.bounds[0]) + r for n, p, l, r in gl if n in MATH)
for i, (n, p, l, r) in enumerate(gl):
    if n in MATH:
        w = p.bounds[2] - p.bounds[0]; extra = mw - (l + w + r); gl[i] = (n, p, l + extra / 2, r + extra / 2)
K.build(outf, name, weight, gl, {n: K.UNI[n] for n, *_ in gl if n in K.UNI})
import kern
n = kern.kern_font(outf)
print(f'{len(gl)} glyphes, {n} paires')
