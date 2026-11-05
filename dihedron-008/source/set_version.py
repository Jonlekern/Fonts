"""Pose le numéro de version dans les fichiers. usage : set_version.py 1.001 fichier.ttf [...]"""
import sys
from fontTools.ttLib import TTFont
v = sys.argv[1]
for p in sys.argv[2:]:
    f = TTFont(p)
    for r in f['name'].names:
        if r.nameID == 5: r.string = f'Version {v}'
        if r.nameID == 3: r.string = v + ';' + r.toUnicode().split(';', 1)[1]
    f['head'].fontRevision = float(v); f.save(p)
