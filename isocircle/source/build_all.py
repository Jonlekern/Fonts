# Fabrique les 20 fichiers (droites et italiques) et le bonus Compass (050, 070, 090) : python3 build_all.py dossier
import os, sys, subprocess
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'fonts', 'otf')
BONUS = os.path.join(OUT, '..', 'bonus')          # le bonus Compass (050, 070, 090) : il va dans le zip, pas sur le site
def one(job):
    num, it = job
    r = subprocess.run([sys.executable, os.path.join(HERE, 'fabrique.py'), num, BONUS if it == 'compas' else OUT] + ([it] if it else []), capture_output=True, text=True)
    return r.stdout.strip() + r.stderr.strip()[-2000:]
with ThreadPoolExecutor(5) as ex:
    jobs = [(n, it) for it in ('', 'italic') for n in ('030', '040', '050', '070', '090')] + [(n, 'compas') for n in ('050', '070', '090')]
    for res in ex.map(one, jobs): print(res)
