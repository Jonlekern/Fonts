# Fûstard 132 (brouillon)

Version techno gothique de Jalousia (dossier `jalousia/`). Travail en cours, pas encore de fichier de police.

## La recette

- **Géométrie stricte** : verticales à 90°, barres à 0°, diagonales à 67,5° et 45°.
- **Croisements partout** : à chaque coin, les deux traits se croisent et dépassent de 210 (hauteur des capitales : 1000).
- **Bouts en pointe.**
- **Arrondis réguliers** sur U, R, S et D, à rayon constant.
- **O en ogive** : deux arcs de cercle qui se croisent en pointe en haut et en bas.
- **A** : celui de la version sharp, gardé tel quel.
- **Q** : l'arc de gauche du O continue en longue queue courbe, barrée d'une petite croix.
- **Trait** : 32 d'épaisseur.

## Étapes

| Étape | Script | Image |
| --- | --- | --- |
| 1. Étude des angles de l'essai Jalousia : 8 angles (0°, 4°, 8°, 15°, 40°, 67°, 77°, 88°) | `etude.py`, `etude_img.py` | `etude.png` |
| 2. Traits droits aux 8 angles, coins vifs, bouts en pointe | `droit.py` | `sharp.png` |
| 3. Arrondis sur les lettres rondes, O en ogive | `arrondi.py` | `arrondis.png` |
| 4. Techno gothique : géométrie stricte, croisements | `fustard.py` | `fustard-132.png` |
| Choix de la longueur des croisements (avant, ×2, ×3 retenu) | | `croisements.png` |
| 5. Alphabet A–Z (V, X, M, C d'après les dessins) | `fustard.py` | `alphabet.png` |

## Refaire les images

```sh
python3 etude_img.py etude.png
python3 droit.py LAFLEURSTUDIO sharp.png
python3 arrondi.py LAFLEURSTUDIO arrondis.png
python3 fustard.py LAFLEURSTUDIO fustard-132.png
python3 fustard.py alphabet alphabet.png
```

Les scripts lisent les lettres de départ dans `../jalousia/essai.py`.
