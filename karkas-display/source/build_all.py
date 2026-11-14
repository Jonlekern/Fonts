# KARKAS DISPLAY : fabrique les 12 fichiers (3 graisses × Tournant, Bande, Bloc, Bloc Bande), leurs WOFF2 et le zip.
#   python3 source/build_all.py
import os, subprocess, sys, zipfile
from concurrent.futures import ThreadPoolExecutor
from fontTools.ttLib import TTFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..'); OTF = os.path.join(ROOT, 'fonts', 'otf'); WOFF = os.path.join(ROOT, 'fonts', 'woff2')
def run(n):
    r = subprocess.run([sys.executable, os.path.join(HERE, 'disp_fab.py'), n, OTF], capture_output=True, text=True); return r.stdout.strip() + r.stderr.strip()[-2000:]
with ThreadPoolExecutor(3) as ex:
    for r in ex.map(run, ('M150', 'M300', 'M500')): print(r)
os.makedirs(WOFF, exist_ok=True)
for f in sorted(os.listdir(OTF)):
    t = TTFont(os.path.join(OTF, f)); t.flavor = 'woff2'; t.save(os.path.join(WOFF, f[:-4] + '.woff2'))
if os.path.exists(os.path.join(ROOT, 'LICENCE.txt')):
    with zipfile.ZipFile(os.path.join(ROOT, 'KARKASDisplay.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
        for f in sorted(os.listdir(OTF)): z.write(os.path.join(OTF, f), f'KARKAS Display/{f}')
        z.write(os.path.join(ROOT, 'LICENCE.txt'), 'KARKAS Display/LICENCE.txt')
        z.write(os.path.join(HERE, 'A_LIRE.txt'), 'KARKAS Display/À LIRE.txt')
