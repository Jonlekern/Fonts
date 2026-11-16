# Refait les 10 fichiers d'Escapement : python3 source/build_all.py
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mesures import GRAISSES
import crenage
from fabrique import construit, hauteurs_windows

SORTIE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'fonts'))
for g in GRAISSES:
    k = crenage.fea(g)[0]                       # le même crénage pour le droit et l'italique
    for it in (False, True):
        print(construit(g, it, SORTIE, k))
print('hauteurs Windows', hauteurs_windows(SORTIE))
