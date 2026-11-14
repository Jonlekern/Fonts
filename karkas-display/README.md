# KARKAS DISPLAY

La version expérimentale de [KARKAS](../karkas/), la vyaz en lettres latines de LaFleurStudio. Mêmes lettres, mêmes liaisons, et trois expériences en plus :

- **Le Tournant** : chaque liaison a un second dessin, en étages (les deux lettres l'une sur l'autre). Une liaison sur deux tourne.
- **La Bande** : la ligne devient un bandeau noir, les lettres y sont creusées en blanc, comme la trace d'un coffrage.
- **Le Bloc** : les lettres se rangent par colonnes de trois étages. Un mot court devient un pavé.

C'est la troisième version du projet décrit dans [`../karkas/source/PLAN.md`](../karkas/source/PLAN.md) (Modern, Classic, Display). La Classic n'existe pas encore.

## Les styles

Chaque graisse est une petite famille à quatre styles.

| Style | Nom | Ce que ça fait |
| --- | --- | --- |
| Regular | Tournant | Les liaisons de KARKAS ; une sur deux passe en étages |
| Italic | Bande | Le Tournant, creusé en blanc dans un bandeau noir |
| Bold | Bloc | Colonnes de trois étages |
| Bold Italic | Bloc Bande | Le Bloc dans la bande |

| Poids | Graisse | Fichiers |
| --- | --- | --- |
| 300 | M150 | `KARKASDisplay-M150.otf` · `…Italic` · `…Bold` · `…BoldItalic` |
| 500 | M300 | `KARKASDisplay-M300.otf` · `…Italic` · `…Bold` · `…BoldItalic` |
| 800 | M500 | `KARKASDisplay-M500.otf` · `…Italic` · `…Bold` · `…BoldItalic` |

## Comment avoir la bande et le bloc

- **Word, PowerPoint, Pages, Keynote, Canva, LibreOffice :** Italique (Ctrl+I ou ⌘I) pour la bande, Gras (Ctrl+B ou ⌘B) pour le bloc.
- **InDesign, Illustrator, Figma, Photoshop :** choisis « Italic », « Bold » ou « Bold Italic » dans le menu des styles. N'utilise pas le faux gras ni le faux italique de Photoshop.
- **Sur un site :** `font-style: italic` et `font-weight: 700`.

Le tournant et le bloc demandent un logiciel qui gère les alternates contextuelles (`calt`) : navigateurs, InDesign, Illustrator, Figma, Affinity, Pages, Keynote, Word récent. Ailleurs, tu obtiens les liaisons de KARKAS (Regular) ou des lettres normales (Bold).

## Le détail

### Le Tournant (Regular)

- 948 liaisons, les mêmes que KARKAS, plus un second dessin pour 839 d'entre elles (les liaisons avec une lettre accentuée n'en ont pas).
- Une paire devient deux lettres empilées. Un groupe de trois devient une lettre entière suivie de deux lettres empilées. Une lettre double, empilée dans KARKAS, se met côte à côte.
- L'alternance : après une liaison normale, la suivante tourne, même six signes plus loin. Un mot qui a un nombre impair de liaisons change donc d'allure quand on le répète ; un mot qui en a un nombre pair reste le même.
- `ss03` : toutes les liaisons en étages. `ss01` et `ss02` : comme dans KARKAS.

### La Bande (Italic)

- Le bandeau va de −190 à 990 : presque toute la hauteur de ligne. Avec un interligne de 1,2, deux lignes laissent un joint de 20 unités.
- L'espace reste vide : chaque mot est sa propre dalle. Le tiret bas `_` est un morceau de bandeau plein, pour relier deux mots.
- Pas de crénage : le bandeau reste régulier.

### Le Bloc (Bold)

- Les lettres A–Z existent en tiers de hauteur (haut, milieu, bas) et en moitiés. Toutes ont la largeur de la colonne ; le I prend des empattements pour la remplir.
- La police range les lettres d'un mot : haut, milieu, bas, puis colonne suivante. S'il reste deux lettres, elles se partagent la hauteur. S'il en reste une, elle garde toute la hauteur.
- Les lettres accentuées, les chiffres, la ponctuation et le russe gardent toute la hauteur et coupent les colonnes.
- Le trait est plus fin que dans les autres styles (62 % du fût), pour que les lettres tiennent sur un tiers de hauteur.
- Pas de liaisons ni de crénage dans ce style.

## La fabrique

```
python3 source/build_all.py
```

- `disp_fab.py` : fabrique une graisse en quatre styles. Les lettres et les règles de liaison viennent de `../karkas/source` (`kar_*.py`).
- `build_all.py` : les 12 OTF, les 12 WOFF2 et le zip.

Il faut Python 3 avec fontTools et skia-pathops.

## Les contrôles

- fontbakery `check-universal`, graisse par graisse (chaque graisse est une famille) : 0 erreur, 0 avertissement.

## Licence

Usage personnel gratuit. Usage commercial sur autorisation écrite de LaFleurStudio : info@lafleurstudio.ch. Voir [`LICENCE.txt`](LICENCE.txt).
