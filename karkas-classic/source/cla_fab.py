# KARKAS CLASSIC : fabrique une graisse.  python3 cla_fab.py Poluustav <dossier>
# La fabrique est celle de KARKAS (../../karkas/source/kar_fab.py) ; on lui donne les lettres du manuscrit et ses réglages.
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', '..', 'karkas', 'source'))
import cla_letters as cl
import kar_letters, kar_liga, kar_signs, kar_fab
from kar_core import rect

for m in (kar_liga, kar_signs, kar_fab):                 # les lettres et leurs fûts
    m.letter = cl.letter; m.LM = cl.LM; m.RM = cl.RM
kar_liga.wedge = lambda *a: None                         # le A ancien n'a qu'un fût : pas de coin à remplir
kar_liga.MAST = lambda x, y0, y1, S: cl.fut(x, y0, y1, S)  # dans les liaisons aussi, les fûts ont leurs bouts en coin
kar_liga.NESTS = 'LF'                                    # le C et le P sont en courbes : ils ne logent pas de lettre
kar_fab.ORN = ''                                         # pas de losanges dans les creux : les fûts portent déjà des nœuds
kar_fab.WEIGHTS = cl.WEIGHTS
kar_fab.FAMILY = 'KARKAS Classic'; kar_fab.PSFAM = 'KARKASClassic'; kar_fab.SLUG = 'karkas-classic'

if __name__ == '__main__':
    nom, outd = sys.argv[1], sys.argv[2]; os.makedirs(outd, exist_ok=True)
    print(nom, kar_fab.write(nom, os.path.join(outd, f'KARKASClassic-{nom}.otf')))
