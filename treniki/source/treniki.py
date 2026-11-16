"""TRENIKI : la version russe de Calebard, en police à part (comme ШКВАЛ pour Overshoot).
On part des 13 fichiers de Calebard passés par cyrillique.py et cyrillique_goofy.py, on garde le russe, le latin de base,
les chiffres, la ponctuation et les signes (pas d'accents latins), et on donne aux graisses leurs noms russes.
usage : treniki.py dossier-calebard-avec-cyrillique dossier-sortie"""
import sys, os
from fontTools.ttLib import TTFont
from fontTools import subset

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
FAMILLE = 'TRENIKI'
# Calebard -> TRENIKI : l'effort en survêtement, de la balade au champion
NOMS = [('Hairline', 'Progulka', 100), ('Thin', 'Shag', 200), ('Light', 'Trustsa', 300), ('Regular', 'Beg', 400),
        ('Medium', 'Probezhka', 500), ('Bold', 'Kross', 600), ('ExtraBold', 'Ryvok', 700), ('SuperBold', 'Sprint', 800),
        ('Black', 'Finish', 900), ('ExtraBlack', 'Rekord', 1000), ('ExtremeBlack', 'Chempion', 1000),
        ('Goofy', 'Shatun', 900), ('ExtraGoofy', 'Vrazvalku', 900)]
GARDE = (list(range(0x20, 0x7F)) + [0xA0, 0xA2, 0xA3, 0xA5, 0xA7, 0xA9, 0xAB, 0xAC, 0xAE, 0xB0, 0xB1, 0xB6, 0xB7, 0xBB, 0xD7, 0xF7]
         + [0x401, 0x451] + list(range(0x410, 0x450)) + [0x301]
         + [0x2009, 0x2010, 0x2011, 0x2013, 0x2014, 0x2018, 0x2019, 0x201A, 0x201C, 0x201D, 0x201E, 0x2022, 0x2026,
            0x202F, 0x2030, 0x2039, 0x203A, 0x20AC, 0x20BD, 0x2116, 0x2122, 0x2212, 0x2248, 0x2260, 0x2264, 0x2265]
         + list(range(0x273E, 0x2742)))

for cal, nom, poids in NOMS:
    t = TTFont(os.path.join(src, f'Calebard-{cal}.ttf'))
    o = subset.Options()
    o.layout_features = ['*']; o.layout_scripts = ['*']; o.name_IDs = ['*']; o.name_languages = ['*']; o.name_legacy = True
    o.glyph_names = True; o.notdef_glyph = True; o.notdef_outline = True; o.recalc_timestamp = False; o.hinting = True
    o.legacy_kern = True; o.drop_tables = []; o.passthrough_tables = True; o.layout_closure = True
    s = subset.Subsetter(o); s.populate(unicodes=[c for c in GARDE if c in t.getBestCmap()]); s.subset(t)
    n = t['name']
    n.names = [r for r in n.names if r.platformID != 1 and r.nameID not in (0, 1, 2, 3, 4, 5, 6, 16, 17)]
    vals = {0: 'Copyright 2020 The Anybody Project Authors (https://github.com/Etcetera-Type-Co/Anybody). '
               'Modifications (Calebard, TRENIKI) 2026 LaFleurStudio.',
            1: f'{FAMILLE} {nom}', 2: 'Regular', 3: f'1.000;LFST;{FAMILLE}-{nom}', 4: f'{FAMILLE} {nom}',
            5: 'Version 1.000', 6: f'{FAMILLE}-{nom}', 16: FAMILLE, 17: nom}
    for i, v in vals.items(): n.setName(v, i, 3, 1, 0x409)
    os2 = t['OS/2']; os2.usWeightClass = poids
    os2.fsSelection = (os2.fsSelection & ~((1 << 0) | (1 << 5) | (1 << 6))) | (1 << 6)
    t['head'].macStyle = 0; t['head'].fontRevision = 1.0
    os2.recalcAvgCharWidth(t)
    t.save(os.path.join(out, f'{FAMILLE}-{nom}.ttf'))
    print(f'{FAMILLE}-{nom}', len(t.getGlyphOrder()), 'glyphes')
