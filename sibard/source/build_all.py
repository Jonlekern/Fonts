# Fabrique toute la famille Sibard, en une commande :
#   python3 source/build_all.py
# Sortie : fonts/otf (7 graisses + 7 italiques), fonts/variable (Graisse + Vitesse), fonts/woff2.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mesures import GRAISSES, NOMS
import crenage, fabrique

ICI = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(ICI, '..', 'fonts')


def main(quoi=('fixes', 'variable')):
    if 'fixes' in quoi:
        for p in GRAISSES:
            fea = fabrique.code_kern([crenage.table(p)[0]])[0]
            for it in (False, True):
                print(os.path.basename(fabrique.fixe(p, it, SORTIE, fea)))
        print('hauteurs Windows', fabrique.hauteurs_windows(SORTIE))
    if 'variable' in quoi:
        feas = fabrique.code_kern([crenage.table(p)[0] for p in fabrique.MAITRES])
        print(os.path.basename(fabrique.variable(SORTIE, feas)))


if __name__ == '__main__':
    main(sys.argv[1:] or ('fixes', 'variable'))
