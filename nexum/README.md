# Nexum

Police techno gothique de LaFleurStudio : géométrie stricte, croisements partout, bouts en pointe. Travail en cours.

**Racine** : Nexum est né de **Jalousia**, police d'après des dessins de chiffres romains néo-gothiques (branche `jalousia`). Les traits de départ de Jalousia sont copiés dans `jalousia.py`, pour que ce dossier se suffise à lui-même.

**Polices** (version 0.304, dossier `fonts/`, TTF et `fonts/woff2/`) : 9 graisses aux normes.

- **335 caractères** : tout le jeu GF Latin Core (langues d'Europe en alphabet latin) et le reste du jeu Windows (± ¹ ² ³ ¼ ½ ¾ µ † ‡ ‰ ƒ…).
- **Accents** dans la recette : traits en pointe, circonflexe croisé comme le haut du A, tréma et point en petites croix, rond en petite ogive ; plus fins que les lettres en gras, au-dessus des pointes sur les capitales.
- **Accents combinants** placés automatiquement (`mark`, `mkmk`), i et j sans point sous un accent (`ccmp`), ș ț roumains (`locl`), chiffres minuscules par défaut, chiffres romains avec `lnum`.
- **Crénage par familles** : chaque lettre accentuée suit sa lettre de base.
- **Mêmes hauteurs de ligne** dans les 9 graisses (1180 / −400, `USE_TYPO_METRICS`).
- Guillemets « » ‹ › posés sur la ligne de base.
- **Licence** (`LICENCE.txt`, aussi inscrite dans les fichiers) : usage personnel gratuit ; usage commercial sur autorisation écrite de LaFleurStudio, gratuite ou payante selon le projet. Contact : info@lafleurstudio.ch. Revente, partage des fichiers et modification interdits sans accord.

| Poids | Nom | Fichier |
| --- | --- | --- |
| 100 | Hairline | `Nexum-Hairline.ttf` |
| 200 | Thin | `Nexum-Thin.ttf` |
| 300 | Light | `Nexum-Light.ttf` |
| 400 | Regular | `Nexum-Regular.ttf` |
| 500 | Medium | `Nexum-Medium.ttf` |
| 600 | Bold | `Nexum-Bold.ttf` |
| 700 | Extra Bold | `Nexum-ExtraBold.ttf` |
| 800 | Super Bold | `Nexum-SuperBold.ttf` |
| 900 | Black | `Nexum-Black.ttf` |

## La recette

- **Géométrie stricte** : verticales à 90°, barres à 0°, diagonales à 67,5° et 45°.
- **Croisements partout** : à chaque coin, les deux traits se croisent et dépassent de 210 (hauteur des capitales : 1000).
- **Bouts en pointe.**
- **Arrondis réguliers** sur U, R, S et D, à rayon constant.
- **O en ogive** : deux arcs de cercle qui se croisent en pointe en haut et en bas.
- **A** : celui de la version sharp, gardé tel quel.
- **Q** : l'arc de gauche du O continue en longue queue courbe, barrée d'une petite croix.
- **Trait** : 32 d'épaisseur.
- **Gabarit** : toutes les capitales montent à 1210 et descendent à −210 (fûts, croix, A et U compris). Seuls le O et le Q gardent leurs pointes courbes, un peu en dessous.
- **Minuscules** : hauteur 600, montantes 1000, descendantes −380 ; croisements à la même exagération, en proportion (126).
  Point du i et du j en croix, queues de g, j, y sur la croix du J, e arrondi en haut avec un coin vif en bas à gauche.
- **Ponctuation** : points en croix, apostrophes en dagues, « » en chevrons croisés à la pointe, & en « Et », * à 8 branches, @ en fenêtre de cathédrale avec le a de Nexum dedans.
- **Chiffres** : deux jeux. Minuscules (par défaut) : arrondis, croix en bout de barre, 0 en ogive barrée. Romains (`lnum`) : N I II III IV V VI VII VIII IX, chaque chiffre d'un seul tenant entre deux barres continues ; le 0 devient N, pour *nulla*.

## Les graisses, de 100 à 900

Même squelette que la Hairline. Le trait passe de 32 (100) à 220 (900), les croisements de 210 à 320, et les règles de triche montent en douceur jusqu'à la 900 :

1. **Contraste** : horizontales jusqu'à 70 % de l'épaisseur des verticales, diagonales entre les deux.
2. **Pièges à encre** : aux croisements francs (plus de 45°), les traits s'amincissent (80 % en 900) sur une demi-épaisseur.
3. **Détails** : petites croix (E, F, S, Z, R, P, J, Q…) jusqu'à 55 %.
4. **Pointes** : de 3 à 1,5 demi-épaisseur (fers de lance en 900).
5. **Largeur** : lettres élargies jusqu'à 18 %.
6. **Croisements en biais** (moins de 40°), à partir de 500 : le trait qui traverse un autre en plein milieu s'arrête dedans (diagonale du U). Un X dont les deux traits dépassent (haut du A) reste un X.
7. **À partir de 700** : U, panse ronde et fût qui descend sous la ligne en la traversant ; u, fond plat qui traverse le fût (croix en bas à droite).
8. **A à partir de 600** : Ā, les deux traits s'arrêtent sous la barre du haut ; le A est étiré pour que sa barre arrive au niveau des pointes des autres lettres.
9. **E et F à partir de 700** : la croix au bout de la barre du haut est plus courte et plus fine.

`python3 triche.py graisses graisses.png` → `graisses.png` (LAFLEURSTUDIO dans les 9 graisses) ; `python3 triche.py nexum-900.png` → la 900.

## Étapes

| Étape | Script | Image |
| --- | --- | --- |
| 1. Étude des angles de l'essai Jalousia : 8 angles (0°, 4°, 8°, 15°, 40°, 67°, 77°, 88°) | `etude.py`, `etude_img.py` | `etude.png` |
| 2. Traits droits aux 8 angles, coins vifs, bouts en pointe | `droit.py` | `sharp.png` |
| 3. Arrondis sur les lettres rondes, O en ogive | `arrondi.py` | `arrondis.png` |
| 4. Techno gothique : géométrie stricte, croisements | `nexum.py` | `nexum.png` |
| Choix de la longueur des croisements (avant, ×2, ×3 retenu) | | `croisements.png` |
| 5. Alphabet A–Z (V, X, M, C d'après les dessins) | `nexum.py` | `alphabet.png` |
| 6. Minuscules a–z | `nexum.py` | `minuscules.png` |
| 7. Chiffres minuscules et majuscules | `nexum.py` | `chiffres.png` |
| 8. Ponctuation | `nexum.py` | `ponctuation.png` |
| 9. Premier fichier Hairline (0.100) | `build_font.py` | `police-essai.png` |
| 10. Les 9 graisses en fichiers (0.200) : un contour par trait, union, crénage calculé sur les profils, `onum` | `build_family.py` | `famille-essai.png` |
| 11. Style des accents | `accents.py` | — |
| 12. Jeu complet aux normes (0.301, licence en 0.302, chiffres minuscules par défaut et chiffres romains en 0.303) : accents, lettres et signes en plus, fonctions OpenType, crénage par familles | `complet.py`, `build_complet.py` | `complet-100.png`, `complet-900.png`, `langues.png` |
| Contrôle automatique des 9 fichiers | `qa_complet.py` | — |

## Refaire les images

```sh
python3 etude_img.py etude.png
python3 droit.py LAFLEURSTUDIO sharp.png
python3 arrondi.py LAFLEURSTUDIO arrondis.png
python3 nexum.py LAFLEURSTUDIO nexum.png
python3 nexum.py alphabet alphabet.png
python3 nexum.py minuscules minuscules.png
python3 nexum.py chiffres chiffres.png
python3 nexum.py ponctuation ponctuation.png
python3 build_complet.py fonts          # les 9 graisses complètes
python3 qa_complet.py fonts             # contrôle
python3 essai_langues.py fonts langues.png
python3 planche_complet.py 100 900      # planches des caractères ajoutés
```

Il faut fontTools, skia-pathops, uharfbuzz et brotli (`pip install fonttools skia-pathops uharfbuzz brotli`). `gf_core.json` contient la liste du jeu GF Latin Core.

Les scripts lisent les traits de départ de Jalousia dans `jalousia.py`.
