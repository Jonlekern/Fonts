# KARKAS : fabrique les 3 graisses et leurs WOFF2.  python3 source/build_all.py
import os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from fontTools.ttLib import TTFont
HERE = os.path.dirname(os.path.abspath(__file__)); OTF = os.path.join(HERE, '..', 'fonts', 'otf'); WOFF = os.path.join(HERE, '..', 'fonts', 'woff2')
def run(n):
    r = subprocess.run([sys.executable, os.path.join(HERE, 'kar_fab.py'), n, OTF], capture_output=True, text=True); return r.stdout.strip() + r.stderr.strip()[-2000:]
with ThreadPoolExecutor(3) as ex:
    for r in ex.map(run, ('M150', 'M300', 'M500')): print(r)
os.makedirs(WOFF, exist_ok=True)
for f in sorted(os.listdir(OTF)):
    t = TTFont(os.path.join(OTF, f)); t.flavor = 'woff2'; t.save(os.path.join(WOFF, f[:-4] + '.woff2'))
# le zip : les 3 OTF, la licence, À LIRE
import zipfile
ROOT = os.path.join(HERE, '..')
with zipfile.ZipFile(os.path.join(ROOT, 'KARKAS.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
    for f in sorted(os.listdir(OTF)): z.write(os.path.join(OTF, f), f'KARKAS/{f}')
    z.write(os.path.join(ROOT, 'LICENCE.txt'), 'KARKAS/LICENCE.txt')
    z.write(os.path.join(HERE, 'A_LIRE.txt'), 'KARKAS/À LIRE.txt')
