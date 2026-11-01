# Sources

Scripts Python (fontTools, uharfbuzz, skia-pathops) utilisés pour fabriquer Clebard à partir de TeX Gyre Heros (`texgyreheros-regular.otf` et `texgyreheros-bold.otf`, CTAN, GUST Font License) et de l'espacement de Calebard.

| Script | Rôle |
| --- | --- |
| `build_clebard.py` | Une graisse : étirement à 140 %, contours poussés ou rentrés jusqu'aux épaisseurs visées, ouvertures gardées, points et accents décalés, contrôle de chaque caractère |
| `cheat1400b.py` | Trenta : là où la 1400 casse, la Venti épaissie seulement à l'horizontale |
| `respace.py` | Approches et crénage de Calebard, à la taille de Clebard |
| `finalize_clebard.py` | TrueType, noms, métriques, licence, WOFF2 |
| `page_images.py` | Images de la page |

Ordre, pour chaque taille (source, largeur, graisse) :

```
python build_clebard.py texgyreheros-regular.otf raw-Demi.otf 1.4 400
python respace.py raw-Demi.otf Calebard-Regular.ttf sp-Demi.otf
python finalize_clebard.py sp-Demi.otf Clebard-Demi.ttf Demi 400
```

Short : Regular, 600, Calebard-Bold. Tall : Bold, 800, Calebard-SuperBold. Grande : Bold, 1000, Calebard-ExtraBlack. Venti : Bold, 1200, Calebard-ExtremeBlack.
Trenta : `build_clebard.py` en 1400, puis `cheat1400b.py texgyreheros-bold.otf raw-1400.otf log-1400.txt raw-Venti.otf raw-Trenta.otf`, puis `respace.py` avec Calebard-ExtremeBlack.
