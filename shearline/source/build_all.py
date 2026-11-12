# SHEARLINE : fabrique les 6 fichiers (3 graisses × regular, italic (lettrines)) et leurs WOFF2.  python3 source/build_all.py
import os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from fontTools.ttLib import TTFont
HERE = os.path.dirname(os.path.abspath(__file__)); OTF = os.path.join(HERE, '..', 'fonts', 'otf'); WOFF = os.path.join(HERE, '..', 'fonts', 'woff2')
jobs = [(n, s) for n in ('Epreuve', 'Tirage', 'Aplat') for s in ('', 'italic')]
def run(j):
    return subprocess.run([sys.executable, os.path.join(HERE, 'shr_fab.py'), j[0], OTF] + ([j[1]] if j[1] else []), capture_output=True, text=True).stdout.strip()
with ThreadPoolExecutor(6) as ex:
    for r in ex.map(run, jobs): print(r)
os.makedirs(WOFF, exist_ok=True)
for f in sorted(os.listdir(OTF)):
    t = TTFont(os.path.join(OTF, f)); t.flavor = 'woff2'; t.save(os.path.join(WOFF, f[:-4] + '.woff2'))
