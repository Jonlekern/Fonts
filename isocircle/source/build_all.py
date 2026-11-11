# Fabrique les 10 fichiers : python3 build_all.py dossier
import os, sys, subprocess
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'fonts', 'otf')
def one(num):
    r = subprocess.run([sys.executable, os.path.join(HERE, 'fabrique.py'), num, OUT], capture_output=True, text=True)
    return r.stdout.strip() + r.stderr.strip()[-2000:]
with ThreadPoolExecutor(5) as ex:
    for res in ex.map(one, ['030', '040', '050', '070', '090']): print(res)
