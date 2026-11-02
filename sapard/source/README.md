# Sources

Scripts Python (fontTools, uharfbuzz, skia-pathops, Pillow) utilisés pour dessiner et fabriquer Sapard.

| Script | Rôle |
| --- | --- |
| `fl.py` | Le dessin de toutes les lettres, en segments droits, pour n'importe quelle graisse (`set_weight`) |
| `build_sapard.py` | Les 18 fichiers : 9 graisses, chacune en droit et en italique à 16°, noms, métriques, WOFF2 |
| `page_images.py` | Images de la page (SVG) |
| `svg2png.js` | Conversion des SVG en PNG avec Chromium (Playwright) |

Utilisation :

```
python build_sapard.py out          # écrit out/ttf et out/woff2
python page_images.py out/ttf images
node svg2png.js images
```

Les graisses sont réglées dans `fl.WEIGHTS` : nom, poids, épaisseur (1 = ExtraBold) et élargissement (Black : 112 %).
