# Fabrique les 5 graisses : python3 build_all.py [dossier_sortie]
import os, sys, subprocess, time
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'out', 'w')
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, HERE)
import core
for weight, name, st in core.WEIGHTS:
    t0 = time.time()
    f = os.path.join(OUT, f'{core.PSFAM}-{name}.otf')
    r = subprocess.run([sys.executable, os.path.join(HERE, 'fabrique.py'), str(st), name, str(weight), f], capture_output=True, text=True)
    print(name, r.stdout.strip().splitlines()[-1] if r.stdout.strip() else '', r.stderr.strip()[-300:] if r.returncode else '', f'{time.time() - t0:.0f} s', flush=True)
