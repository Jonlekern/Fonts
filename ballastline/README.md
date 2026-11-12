# BALLASTLINE

Serif de lecture de LaFleurStudio. Le centre de gravité est en bas : même trait partout, têtes fines, et le poids tombe dans le bas des courbes. Et derrière l'italique et le gras, **la ligne de flottaison et le lest**.

Le nom : la *ballast line*, la ligne de lest. Ce qui met le poids en bas d'un bateau et le tient droit. L'ancien nom de la police était BARYCENTRE-032.

## La recette

- **Le poids en bas des courbes.** Là où une courbe tourne pour finir sur la ligne, le trait gonfle en douceur. Le blanc de la lettre reste rond.
- **Italique = la ligne de flottaison.** Une bande noire passe au bas de chaque mot, comme la coque d'un bateau sous l'eau. Les lettres y passent en blanc, et la bande file d'une lettre à l'autre. Les espaces restent hors de l'eau : chaque mot a sa coque.
- **Gras = le lest.** Sous chaque lettre pend un fil et un plomb en goutte, accroché à son pied principal.
- **Gras italique = les deux.** La flottaison, avec les plombs qui pendent sous la coque.
- **ss01 : points en plomb.** Les points du i et du j, le point, la virgule, les deux-points, le point-virgule et les points de ! ? ¡ ¿ deviennent des plombs.
- **Crénage** d'origine en normal et en gras. En flottaison, pas de crénage entre les lettres : la bande resterait coupée.

## Comment avoir la flottaison et le lest

Chaque graisse est une petite famille à quatre styles : **Regular** (normal), **Italic** (flottaison), **Bold** (lest) et **Bold Italic** (les deux).

- **Word, PowerPoint, Pages, Keynote, Canva, LibreOffice :** Italique (Ctrl+I ou ⌘I) pour la flottaison, Gras (Ctrl+B ou ⌘B) pour le lest, les deux ensemble pour les deux.
- **InDesign, Illustrator, Figma, Photoshop :** choisis le style « Italic », « Bold » ou « Bold Italic ». N'utilise pas le faux gras ni le faux italique de Photoshop.
- **Sur un site :** `font-style: italic` ou `<em>`, `font-weight: bold` ou `<strong>`. Attention, les titres sont souvent en gras automatiquement : ils sortiront avec leurs plombs.

## Les graisses

| Poids | Nom | Fichiers |
| --- | --- | --- |
| 200 | 020 | `BALLASTLINE-020.otf` · `BALLASTLINE-020Italic.otf` · `BALLASTLINE-020Bold.otf` · `BALLASTLINE-020BoldItalic.otf` |
| 300 | 030 | `BALLASTLINE-030.otf` · `BALLASTLINE-030Italic.otf` · `BALLASTLINE-030Bold.otf` · `BALLASTLINE-030BoldItalic.otf` |
| 400 | 040 | `BALLASTLINE-040.otf` · `BALLASTLINE-040Italic.otf` · `BALLASTLINE-040Bold.otf` · `BALLASTLINE-040BoldItalic.otf` |
| 600 | 060 | `BALLASTLINE-060.otf` · `BALLASTLINE-060Italic.otf` · `BALLASTLINE-060Bold.otf` · `BALLASTLINE-060BoldItalic.otf` |
| 800 | 080 | `BALLASTLINE-080.otf` · `BALLASTLINE-080Italic.otf` · `BALLASTLINE-080Bold.otf` · `BALLASTLINE-080BoldItalic.otf` |

## Caractères

Tout le jeu GF Latin Core : majuscules, minuscules, chiffres, ponctuation, signes et accents d'Europe en alphabet latin, plus les points en plomb.

## Fichiers

- `fonts/otf/` : les 20 fichiers à installer (5 graisses × normal, flottaison, lest, les deux)
- `fonts/woff2/` : les 20 fichiers pour le web
- `BALLASTLINE.zip` : les 20 fichiers (OTF) + la licence + « À LIRE »
- `LICENCE.txt` : la licence
- `source/` : les dessins d'origine (`dessins/`) et les scripts Python qui en tirent les 4 styles (`python3 source/build_all.py`)

## Licence

Usage personnel gratuit. Usage commercial sur autorisation écrite de LaFleurStudio : info@lafleurstudio.ch. Voir `LICENCE.txt`.

© 2026 LaFleurStudio · Jonathan Kern
