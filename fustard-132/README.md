# Fûstard 132 (brouillon)

Version techno gothique de Jalousia (dossier `jalousia/`). Travail en cours.

**Fichier de police d'essai** : `fonts/Fustard132-Hairline.ttf` (Hairline, poids 100, version 0.100) : A–Z, a–z, chiffres, ponctuation. Chiffres majuscules par défaut ; chiffres minuscules avec l'option « chiffres elzéviriens » (`onum`). Pas encore d'accents.

## La recette

- **Géométrie stricte** : verticales à 90°, barres à 0°, diagonales à 67,5° et 45°.
- **Croisements partout** : à chaque coin, les deux traits se croisent et dépassent de 210 (hauteur des capitales : 1000).
- **Bouts en pointe.**
- **Arrondis réguliers** sur U, R, S et D, à rayon constant.
- **O en ogive** : deux arcs de cercle qui se croisent en pointe en haut et en bas.
- **A** : celui de la version sharp, gardé tel quel.
- **Q** : l'arc de gauche du O continue en longue queue courbe, barrée d'une petite croix.
- **Trait** : 32 d'épaisseur.
- **Minuscules** : hauteur 600, montantes 1000, descendantes −380 ; croisements à la même exagération, en proportion (126).
  Point du i et du j en croix, queues de g, j, y sur la croix du J, e arrondi en haut avec un coin vif en bas à gauche.
- **Ponctuation** : points en croix, apostrophes en dagues, « » en chevrons croisés à la pointe, & en « Et », * à 8 branches, @ en fenêtre de cathédrale avec le a de Fûstard dedans.
- **Chiffres** : deux jeux. Minuscules : arrondis, croix en bout de barre, 0 en ogive barrée. Majuscules : coins vifs, chaque coin en croix, 0 en cadre barré, 8 en grille.

## La 900 (essai)

Même squelette que la Hairline, trait de 220 (22 % des capitales), croisements rallongés à 320. Pour que ça tienne en gras, on triche :

1. **Contraste** : horizontales à 70 % de l'épaisseur des verticales, diagonales entre les deux.
2. **Pièges à encre** : aux croisements francs (plus de 45°), les traits s'amincissent à 80 % sur une demi-épaisseur.
3. **Détails** : petites croix (E, F, S, Z, R, P, J, Q…) à 55 %.
4. **Pointes** : longues de 1,5 demi-épaisseur (fers de lance).
5. **Largeur** : lettres élargies de 18 %.
6. **Croisements en biais** (moins de 40°) : le trait s'arrête dans l'autre, sans dépasser.
7. **À partir de 700** : U, panse ronde et fût qui descend sous la ligne en la traversant ; u, fond plat qui traverse le fût (croix en bas à droite).

`python3 triche.py fustard-132-900.png` → `fustard-132-900.png`

## Étapes

| Étape | Script | Image |
| --- | --- | --- |
| 1. Étude des angles de l'essai Jalousia : 8 angles (0°, 4°, 8°, 15°, 40°, 67°, 77°, 88°) | `etude.py`, `etude_img.py` | `etude.png` |
| 2. Traits droits aux 8 angles, coins vifs, bouts en pointe | `droit.py` | `sharp.png` |
| 3. Arrondis sur les lettres rondes, O en ogive | `arrondi.py` | `arrondis.png` |
| 4. Techno gothique : géométrie stricte, croisements | `fustard.py` | `fustard-132.png` |
| Choix de la longueur des croisements (avant, ×2, ×3 retenu) | | `croisements.png` |
| 5. Alphabet A–Z (V, X, M, C d'après les dessins) | `fustard.py` | `alphabet.png` |
| 6. Minuscules a–z | `fustard.py` | `minuscules.png` |
| 7. Chiffres minuscules et majuscules | `fustard.py` | `chiffres.png` |
| 8. Ponctuation | `fustard.py` | `ponctuation.png` |
| 9. Fichier de police (crénage calculé sur les profils, `onum`) | `build_font.py` | `police-essai.png` |

## Refaire les images

```sh
python3 etude_img.py etude.png
python3 droit.py LAFLEURSTUDIO sharp.png
python3 arrondi.py LAFLEURSTUDIO arrondis.png
python3 fustard.py LAFLEURSTUDIO fustard-132.png
python3 fustard.py alphabet alphabet.png
python3 fustard.py minuscules minuscules.png
python3 fustard.py chiffres chiffres.png
python3 fustard.py ponctuation ponctuation.png
python3 build_font.py fonts/Fustard132-Hairline.ttf police-essai.png
```

`build_font.py` demande fontTools et skia-pathops (`pip install fonttools skia-pathops`).

Les scripts lisent les lettres de départ dans `../jalousia/essai.py`.
