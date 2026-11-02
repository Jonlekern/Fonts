# Sources

Scripts Python (fontTools, uharfbuzz, skia-pathops) utilisés pour fabriquer Falsard à partir d'Orbitron (`Orbitron[wght].ttf`, Google Fonts, OFL).

| Script | Rôle |
| --- | --- |
| `build_falsard.py` | Les 10 graisses de XXXS à XXXXL : lignes de construction (haut compressé, bas épaissi), élargissement à 110 % sans déformer, S sans tête ni queue, minuscules calées sur le s, prolongement sous 400 et au-dessus de 900, contrôle de chaque caractère, © ® ™, noms |
| `guillemets.py` | Guillemets « » ‹ › tirés du < et du > de Falsard, petits et posés en bas, et point médian · (à lancer sur chaque fichier après `build_falsard.py`) |
| `set_version.py` | Numéro de version dans les fichiers |
| `page_images.py` | Images de la page (lignes, élargissement, S, minuscules) |

Utilisation : `python build_falsard.py Orbitron-VF.ttf dossier_de_sortie`, puis `python guillemets.py police.ttf police.ttf 0.55 base` sur chaque fichier, et `python set_version.py 1.001 dossier/*.ttf`.
