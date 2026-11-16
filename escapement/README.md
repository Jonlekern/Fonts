# Escapement

Grotesque de lecture de LaFleurStudio, **dessinée à neuf**. C'est la petite sœur d'[Overshoot](../overshoot/) : la même recette, mais faite pour lire des articles, des livrets et des catalogues, de 9 à 14 points.

Le nom vient de l'horlogerie suisse : l'*escapement*, c'est l'échappement, la pièce qui donne à une montre son tic-tac régulier. Une bonne lecture, c'est la même chose : un rythme régulier.

## La recette

- **Les rondes** : des superellipses, comme dans Overshoot, mais plus près de l'ovale pour la lecture.
- **Les bouts** : coupés à l'horizontale (c, e, s, C, G, S, J, 2, 3, 5, 6, 9…).
- **Les proportions** : bien plus étroite qu'Overshoot, minuscules à 72 % des capitales, espacement aéré, contraste faible.
- **Les lettres rares portent la signature d'Overshoot** :
  - **G** : l'éperon en coin net ;
  - **Q** : la panse coupée à l'horizontale et la queue en dalle posée au sol ;
  - **R** et **a** : le petit pied qui botte vers la droite ;
  - **j** : le crochet coupé en biais, qui se glisse sous la lettre d'avant ;
  - **7** : la jambe un peu creusée ;
  - **« »** : des guillemets lourds à la pointe.

## La lettre de début de phrase

Au début d'une phrase, la capitale passe toute seule en **version Overshoot** : plus large, avec les rondes plus carrées. Elle garde la même hauteur et la même épaisseur que le texte.

- **Elle se déclenche** au début d'un paragraphe et après `. ! ? …` suivi d'une espace, même après un guillemet ouvrant (« Bonjour »).
- **Elle ne se déclenche pas** :
  - en plein milieu d'une phrase ;
  - après une abréviation courante en français, allemand, anglais et italien (M., Mme, z. B., Nr., Mr., Sig.…) ;
  - après une initiale (C. F. Ramuz) ;
  - après un ordinal (am 1. August) ;
  - dans les mots tout en capitales (UNESCO, ZÜRICH).
- **ss01** met toutes les capitales en version Overshoot, partout (pour les titres, et pour Word).
- Il faut un logiciel qui gère les alternates contextuelles (`calt`) : InDesign, Illustrator, Figma, Affinity, Pages et les navigateurs. On peut couper la règle en désactivant les alternates contextuelles.
- Sur le web, une balise au milieu d'une phrase (`<em>`, `<a>`) peut faire croire à un début de paragraphe.

## Les graisses

Les graisses portent les noms de lignes de train suisses, de la moins raide à la plus raide.

| Poids | Nom | La ligne | Fichier |
| --- | --- | --- | --- |
| 300 | Gotthard | 27 ‰ | `Escapement-Gotthard.otf` |
| 400 | Albula | 35 ‰ | `Escapement-Albula.otf` |
| 500 | Bernina | 70 ‰ | `Escapement-Bernina.otf` |
| 600 | Rigi | 250 ‰ | `Escapement-Rigi.otf` |
| 700 | Pilatus | 480 ‰ | `Escapement-Pilatus.otf` |

## Italiques

Chaque graisse a son italique, penchée de 10° : même dessin, mêmes chasses, même crénage. Les fichiers finissent par « Italic » (`Escapement-AlbulaItalic.otf`…). Sur le web : une famille « Escapement Italic » avec les mêmes graisses.

## Chiffres

Alignés et proportionnels par défaut. Les chiffres tabulaires (`tnum`) sont là pour les prix et les tableaux : les colonnes tombent juste.

## Caractères

Le même jeu qu'Overshoot : majuscules, minuscules, chiffres, ponctuation, signes et accents des langues d'Europe en alphabet latin.

## Fichiers

- `fonts/otf/` : les 5 graisses et leurs italiques à installer (OpenType)
- `fonts/woff2/` : les 5 graisses et leurs italiques pour le web
- `Escapement.zip` : les 5 graisses et leurs italiques (OTF) + la licence
- `source/` : la fabrique (`python3 source/build_all.py` refait les 10 fichiers)
- `LICENCE.txt` : la licence

## Licence

Usage personnel gratuit. Usage commercial sur autorisation écrite de LaFleurStudio : info@lafleurstudio.ch. Voir `LICENCE.txt`.

© 2026 LaFleurStudio · Jonathan Kern
