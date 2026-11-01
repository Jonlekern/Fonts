# Sources

Scripts Python (fontTools, uharfbuzz, skia-pathops, numpy, scipy, Pillow) utilisés pour fabriquer Calebard à partir d'Anybody (`Anybody[wdth,wght].ttf`, Google Fonts, OFL).

| Script | Rôle |
| --- | --- |
| `logo130.py` + `kern_la.py` | Logo LAFLEURSTUDIO : Black étiré à 130 %, épaisseurs rééquilibrées, espacement L–A optique |
| `build_family.py` | Les 9 graisses de Hairline à Black (largeur 150, étirement 130 %, correction des traits, L–A) |
| `build_xw.py` | Graisses au-delà du Black par prolongement (`XT=1.0` → Extra Black, `XT=2.0` → Extreme Black) |
| `check_1000.py`, `check_all.py` | Mesure des fentes et des trous de chaque caractère, comparaison avec la graisse voisine |
| `solve_many_x.py`, `solve_topo.py` | Calcul, lettre par lettre, de l'affinage des horizontales pour rouvrir les trous |
| `overrides-1000.json`, `overrides-1100.json` | Corrections retenues pour l'Extra Black et l'Extreme Black |
| `fix_five.py`, `scan_corners.py`, `fix_corners.py` | Arrondi des coins où une fente débouche dans un trou (5, S, 2, 3, 6, 9, ?, C) |
| `build_goofy.py` | Goofy : lettres penchées à 12° en alternance (variantes contextuelles) |
| `build_extra_goofy.py` | Extra Goofy : lettres tournées à 4°, 7° et 10° en alternance |
| `flower_lib.py`, `add_flower.py` | Fleur LaFleurStudio : ❀ (U+2740), ✿ bold 1 (U+273F), ❁ bold 2 (U+2741), ✾ bold 3 (U+273E) |
| `rename_style.py` | Noms des graisses |

Ordre : `build_family.py` → `build_xw.py` (avec les overrides) → `fix_five.py` / `fix_corners.py` sur Super Bold, Black, Extra Black, Extreme Black → `rename_style.py`.
