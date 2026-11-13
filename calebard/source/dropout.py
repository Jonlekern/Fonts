"""Smart dropout : les traits fins ne disparaissent plus en très petite taille (TTF non hintés).

Ajoute la table prep (PUSHW 511, SCANCTRL, PUSHB 4, SCANTYPE) et règle gasp et maxp en conséquence.
Les contours ne changent pas.

usage : python3 dropout.py police.ttf [police.ttf ...]
"""
import sys
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables import ttProgram

for chemin in sys.argv[1:]:
    f = TTFont(chemin)
    prep = newTable('prep'); prep.program = ttProgram.Program()
    prep.program.fromAssembly(['PUSHW[]', '511', 'SCANCTRL[]', 'PUSHB[]', '4', 'SCANTYPE[]'])
    f['prep'] = prep
    if 'gasp' not in f:
        f['gasp'] = newTable('gasp'); f['gasp'].version = 1
    f['gasp'].gaspRange = {0xFFFF: 0x000F}
    m = f['maxp']
    m.maxZones = max(m.maxZones, 1)
    m.maxStackElements = max(m.maxStackElements, 1)
    f.save(chemin)
    print(chemin, 'smart dropout ok')
