# KARKAS (КАРКАС)

Vyaz latine de LaFleurStudio, **dessinée à neuf**. La vyaz (вязь) est l'écriture russe entrelacée des titres de manuscrits : des lettres très hautes, serrées, qui partagent leurs traits pour faire de la ligne une bande continue. KARKAS reprend ses gestes en lettres latines, avec un dessin géométrique et brutaliste : tout est droit, pas une courbe.

Le nom : « каркас », c'est l'ossature en béton d'un bâtiment. Le mot russe vient du français « carcasse ». Dans la vyaz, les lettres partagent leurs fûts comme une ossature partage ses poteaux.

KARKAS est la version **Modern** d'un projet en trois temps. Deux autres sont prévues avec la même liste de liaisons : Classic (dessin à la plume) et Display (expérimentale). Le plan complet est dans [`source/PLAN.md`](source/PLAN.md).

## La recette

- **Capitales seulement.** La vyaz n'a qu'une casse. Les minuscules donnent les mêmes capitales.
- **Tout est fût.** Les fûts montent sur toute la hauteur (800 unités pour 160 à 220 de large). Ce qui distingue la lettre (barre, boucle, oblique) est serré dans une zone, avec une taille haute à 68 %.
- **Même trait partout**, coins vifs, obliques courtes, aucune courbe.
- **Les liaisons** (feature `liga`, active par défaut), un dessin par groupe de lettres :
  - **fût partagé** : le fût droit d'une lettre est le fût gauche de la suivante (HE, AN, OU, UR…). En gras, l'épaule du A devient carrée au joint pour ne pas laisser de fente ; dans les graisses fines, le coin reste ouvert. Le D et le V ne partagent pas leur fût : leurs coins coupés et leur pointe disparaîtraient ;
  - **lettre logée** : une lettre rétrécie dans le creux d'une grande, après L, C, F et P ;
  - **sous la barre du T** : une lettre de chaque côté du T (TA, AT, ATE, STE, NTR…) ;
  - **lettres doubles** : empilées sur deux étages (EE, LL, SS, TT…) ;
  - **groupes de trois** : chaînes de fûts partagés (AND, OUR, QUE, HOM…).
- **948 ligatures** par graisse : 578 pour le latin (dont 109 avec une lettre accentuée : HÉ, NÉ, MÈ, UÇ…) et 370 pour le russe.
- **ss01** : les lettres doubles qui ont deux fûts en partagent un au lieu de s'empiler (AA, HH, MM, NN, OO, QQ, UU, WW).
- **ss02** : un losange dans le creux des lettres restées seules (L, T, F, P, J, Y), comme les bouche-trous des scribes.
- **Chiffres tabulaires.** Le 0 a les quatre coins coupés, pour ne pas le confondre avec le O.
- **Crénage** automatique par profils : les lettres ouvertes s'emboîtent (L et T, T et la virgule…). Les chiffres ne se crénent jamais.
- **Le cyrillique, en bonus** : А–Я et Ё dans le même dessin, avec fûts partagés, lettres logées sous le Г et autour du Т, lettres doubles empilées. Le Й garde sa brève et ne se lie pas.

## Pour couper les liaisons

- **Word :** Police, Paramètres avancés, Ligatures : Aucune.
- **InDesign, Illustrator, Photoshop, Affinity, Figma :** décoche « Ligatures ».
- **Sur un site :** `font-variant-ligatures: none`.

## Les graisses

Les marques du béton russe : plus le chiffre est haut, plus il résiste.

| Poids | Nom | Fût | Fichier |
| --- | --- | --- | --- |
| 300 | M150 | 24 | `KARKAS-M150.otf` |
| 500 | M300 | 44 | `KARKAS-M300.otf` |
| 800 | M500 | 68 | `KARKAS-M500.otf` |

## Caractères

Latin de base, accents d'Europe (ouest, centre, est, turc), chiffres, ponctuation, signes, monnaies, fractions, et l'alphabet russe. 1223 glyphes par fichier.

## La fabrique

Tout se refait avec une commande :

```
python3 source/build_all.py
```

- `kar_core.py` : outils de dessin (rectangles, obliques, unions) et les trois graisses.
- `kar_letters.py` : les lettres latines et russes. Chaque lettre se dessine pour une hauteur donnée : une lettre logée est la même lettre, moins haute, avec le même trait.
- `kar_liga.py` : les règles de liaison et la liste des groupes.
- `kar_signs.py` : chiffres, ponctuation, signes, accents, lettres en plus.
- `kar_fab.py` : assemble une graisse (contours, noms, OpenType, crénage, STAT).
- `build_all.py` : les 3 OTF, les 3 WOFF2 et le zip.
- `apercu.py` : un aperçu rapide d'un mot sans fabriquer la police.

Il faut Python 3 avec fontTools et skia-pathops.

## Les contrôles

- fontbakery `check-universal` : 0 erreur, 0 avertissement sur les 3 fichiers.
- `outils/defauts.py` : il signale les angles aigus des obliques (pointe d'encre, pointe de blanc) et le décrochement voulu du B. Ils font partie du dessin : pas d'écharde, de fente ni de marche accidentelle.

## Licence

Usage personnel gratuit. Usage commercial sur autorisation écrite de LaFleurStudio : info@lafleurstudio.ch. Voir [`LICENCE.txt`](LICENCE.txt).
