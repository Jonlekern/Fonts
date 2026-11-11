# Fabrique les 3 graisses d'ISOSLAB : python3 source/build_all.py [dossier_sortie]
import os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'fonts', 'otf'); os.makedirs(OUT, exist_ok=True)
for st, name, wt in ((92, '050', 500), (136, '070', 700), (184, '090', 900)):
    r = subprocess.run([sys.executable, os.path.join(HERE, 'fabrique.py'), str(st), name, str(wt), os.path.join(OUT, f'ISOSLAB-{name}.otf')], capture_output=True, text=True)
    print(r.stdout.strip(), r.stderr.strip()[-1500:])
