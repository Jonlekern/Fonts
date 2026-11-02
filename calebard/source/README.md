# Sources

Scripts Python (fontTools, uharfbuzz, skia-pathops, numpy, scipy, Pillow) utilisés pour fabriquer Calebard à partir d'Anybody (`Anybody[wdth,wght].ttf`, Google Fonts, OFL).

| Script | Rôle |
| --- | --- |
| `logo130.py` + `kern_la.py` | Version 1.0 : logo LAFLEURSTUDIO, Black étiré à 130 %, épaisseurs rééquilibrées, espacement L–A optique |
| `build_family.py` | Les 9 graisses de Hairline à Black (largeur 150, étirement `STRETCH`, 1,209 par défaut, correction des traits) |
| `build_xw.py` | Graisses au-delà du Black par prolongement (`XT=1.0` → Extra Black, `XT=2.0` → Extreme Black) |
| `check_1000.py`, `check_all.py` | Mesure des fentes et des trous de chaque caractère, comparaison avec la graisse voisine |
| `solve_many_x.py`, `solve_topo.py` | Calcul, lettre par lettre, de l'affinage des horizontales pour rouvrir les trous |
| `overrides-1000.json`, `overrides-1100.json` | Corrections de l'Extra Black et de l'Extreme Black (version 1.0, à 130 %) |
| `overrides-1000-120.json`, `overrides-1100-120.json` | Les mêmes, complétées pour la version 1.0.1 (120,9 %) |
| `five_black.py` | Retouche du coin du 5 dans le Black |
| `fix_five.py`, `scan_corners.py`, `fix_corners.py` | Arrondi des coins où une fente débouche dans un trou (5, S, 2, 3, 6, 9, ?, C) |
| `nudge.py` | Version 1.0.1 : enlève les contours vides et écarte les accents trop collés (Extra Black, Extreme Black) |
| `uj.py` | Version 1.0.1 : U moins large, queue du J plus courte, accents et ancres suivis |
| `spacing.py` + `espaces-logo.json` | Version 1.0.1 : espacement des capitales en 6 règles, le reste en proportion, 12 paires de LAFLEURSTUDIO réglées sur le logo |
| `build_goofy.py` | Goofy : lettres penchées à 12° en alternance (variantes contextuelles) |
| `build_extra_goofy.py` | Extra Goofy : lettres tournées à 4°, 7° et 10° en alternance |
| `liga_off.py` | Ligatures coupées dans Goofy |
| `flower_lib.py`, `add_flower.py` | Fleur LaFleurStudio : ❀ (U+2740), ✿ bold 1 (U+273F), ❁ bold 2 (U+2741), ✾ bold 3 (U+273E) |
| `rename_style.py` | Noms des graisses |

## Refaire la version 1.0.1

```sh
STRETCH=1.209 OVR1000=overrides-1000-120.json OVR1100=overrides-1100-120.json ./pipeline.sh out
./post.sh out
```

- `pipeline.sh` : `build_family.py` → `build_xw.py` (avec les overrides) → `rename_style.py` → `five_black.py` → `fix_corners.py` sur Super Bold, Black, Extra Black, Extreme Black → `nudge.py`.
- `post.sh` : `uj.py` → `spacing.py` → `finish.sh` (Goofy, Extra Goofy, `liga_off.py`, puis la fleur dans les 13 fichiers).

Variables : `PY` (Python à utiliser), `VF` (chemin d'Anybody). La fleur lit `logo-fleur.svg` (dépôt lafleurstudio : `images/logo-fleur.svg`). Le numéro de version se pose à la fin : `set_version.py 1.001 out/ttf/*.ttf`.

Avec `STRETCH=1.30` et les overrides d'origine, `pipeline.sh` puis `finish.sh` redonnent la version 1.0.
