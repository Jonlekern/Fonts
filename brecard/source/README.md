# Sources

Scripts Python (fontTools, uharfbuzz, skia-pathops, Pillow) utilisés pour dessiner et fabriquer Brécard.

| Script | Rôle |
| --- | --- |
| `fl.py` | Le dessin de toutes les lettres, en segments droits, pour n'importe quelle graisse (`set_weight`), y compris les caractères du jeu GF Latin Core (`build_ext`) |
| `build_brecard.py` | Les 18 fichiers : 9 graisses, chacune en droit et en italique à 16°, noms, métriques, WOFF2 |
| `feat_brecard.py` | Fonctions OpenType : crénage (avec `kern_brecard.py`) et placement des accents combinants (`mark`), compilés ensemble |
| `kern_brecard.py` | Crénage : le blanc entre chaque paire de lettres est mesuré ligne par ligne et les paires trop ouvertes (AV, LT, To, P.…) sont rapprochées, avec un écart minimal ; les lettres accentuées suivent leur lettre de base |
| `set_version.py` | Numéro de version dans les fichiers |
| `page_images.py` | Images de la page (SVG) |
| `svg2png.js` | Conversion des SVG en PNG avec Chromium (Playwright) |

Utilisation :

```
python build_brecard.py out          # écrit out/ttf et out/woff2
for f in out/ttf/*.ttf; do python feat_brecard.py $f $f; done
python set_version.py 1.201 out/ttf/*.ttf   # puis refaire les WOFF2
python page_images.py out/ttf images
node svg2png.js images
```

Les graisses sont réglées dans `fl.WEIGHTS` : nom en klingon (*vatlh* = cent), poids, épaisseur (1 = chorghvatlh, 800) et élargissement (Hutvatlh, 900 : 112 %).
