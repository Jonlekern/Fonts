# BALLASTLINE : fabrique les 20 fichiers (5 graisses × normal, flottaison, lest, les deux) et leurs WOFF2.  python3 source/build_all.py
import os, subprocess, sys
from fontTools.ttLib import TTFont
HERE = os.path.dirname(os.path.abspath(__file__)); OTF = os.path.join(HERE, '..', 'fonts', 'otf'); WOFF = os.path.join(HERE, '..', 'fonts', 'woff2')
for n in ('020', '030', '040', '060', '080'):
    subprocess.run([sys.executable, os.path.join(HERE, 'ball_fab.py'), os.path.join(HERE, 'dessins', f'dessin-{n}.otf'), n, OTF], check=True)
os.makedirs(WOFF, exist_ok=True)
for f in sorted(os.listdir(OTF)):
    t = TTFont(os.path.join(OTF, f)); t.flavor = 'woff2'; t.save(os.path.join(WOFF, f[:-4] + '.woff2'))
