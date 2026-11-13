# Refait les 18 fichiers de SHKVAL : python3 source/build_all.py
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mesures import GRAISSES
from fabrique import construit

SORTIE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'fonts'))
for g in GRAISSES:
    for it in (False, True):
        print(construit(g, it, SORTIE))
