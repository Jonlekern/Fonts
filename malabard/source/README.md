# Sources

Scripts Python (fontTools, uharfbuzz, skia-pathops, numpy, scipy, Pillow) utilisés pour fabriquer Malabard à partir de Righteous (`Righteous-Regular.ttf`, Astigmatic, Google Fonts, OFL).

| Script | Rôle |
| --- | --- |
| `stretch.py` | Lecture des contours, coupe horizontale là où le contour est vertical, insertion de la hauteur |
| `plan.py` | Choix des coupes de chaque lettre (une ou deux, tolérance par contour) |
| `stretchlib.py` | Allongement de chaque glyphe : coupe, bande étirée d'un bloc pour les diagonales, signes remontés |
| `build_malabard.py` | Une graisse : allongement puis traits amincis ou épaissis, élargissement en gras, jonctions, points et accents |
| `finalize_malabard.py` | Ligatures fi/fl, italiques à 12°, crénage des collisions, noms, métriques, WOFF2 |
| `page_images.py` | Images de la page |

Utilisation (fût visé et élargissement, en unités de 2048 par em) :

```
python build_malabard.py Righteous-Regular.ttf raw-200.ttf 120 1.0
python build_malabard.py Righteous-Regular.ttf raw-300.ttf 180 1.0
python build_malabard.py Righteous-Regular.ttf raw-400.ttf 235 1.0
python build_malabard.py Righteous-Regular.ttf raw-500.ttf 287 1.0
python build_malabard.py Righteous-Regular.ttf raw-600.ttf 345 1.03
python build_malabard.py Righteous-Regular.ttf raw-700.ttf 405 1.08
python build_malabard.py Righteous-Regular.ttf raw-800.ttf 465 1.14
python finalize_malabard.py raw-700.ttf ttf/Malabard-Bold.ttf Bold 700 0 metrics.json raw-500.ttf
python finalize_malabard.py raw-500.ttf ttf/Malabard-MediumItalic.ttf "Medium Italic" 500 1 metrics.json raw-500.ttf
```

`metrics.json` contient les métriques verticales communes à la famille (`asc`, `desc`, `winasc`, `windesc`).
