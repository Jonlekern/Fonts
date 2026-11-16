# Calebard

Sans-serif super étendue en **11 graisses**, du Hairline à l'Extreme Black, plus deux styles bonus **Goofy** et **Extra Goofy**, par **LaFleurStudio**.

Page : **https://jonlekern.github.io/Fonts/calebard/**

En russe, Calebard a une police sœur : **TRENIKI (ТРЕНИКИ)**, dans `treniki/`.

## Graisses

| Nom | Poids | Fichier |
| --- | --- | --- |
| Hairline | 100 | `Calebard-Hairline` |
| Thin | 200 | `Calebard-Thin` |
| Light | 300 | `Calebard-Light` |
| Regular | 400 | `Calebard-Regular` |
| Medium | 500 | `Calebard-Medium` |
| Bold | 600 | `Calebard-Bold` |
| Extra Bold | 700 | `Calebard-ExtraBold` |
| Super Bold | 800 | `Calebard-SuperBold` |
| Black | 900 | `Calebard-Black` |
| Extra Black | 1000 | `Calebard-ExtraBlack` |
| Extreme Black | 1100 (déclarée en 1000, le maximum du format) | `Calebard-ExtremeBlack` |

### Styles bonus (base Black)

| Nom | Effet | Fichier |
| --- | --- | --- |
| Goofy | Lettres penchées à 12°, une fois à droite, une fois à gauche | `Calebard-Goofy` |
| Extra Goofy | Lettres tournées à 4°, 7° et 10°, dans un sens puis dans l'autre | `Calebard-ExtraGoofy` |

L'alternance passe par les variantes contextuelles (`calt`) : actives d'office dans les navigateurs, Figma, Adobe et les apps Mac. Dans Word : Police → Avancé → « Utiliser les variantes contextuelles ».

## La fleur LaFleurStudio

Le logo fleur du studio est inclus dans toutes les polices :

| Caractère | Code | Version |
| --- | --- | --- |
| ❀ | U+2740 | Fleur normale |
| ✿ | U+273F | Fleur bold 1 |
| ❁ | U+2741 | Fleur bold 2 |
| ✾ | U+273E | Fleur bold 3 |

À taper par copier-coller ou depuis le visualiseur de caractères.

## Fichiers

| Chemin | Contenu |
| --- | --- |
| `Calebard.zip` | Les 11 graisses, Goofy et Extra Goofy en TTF + licence |
| `fonts/ttf/` | Polices à installer (Mac, Windows, logiciels) |
| `fonts/woff2/` | Polices pour le web |
| `images/` | Images de la page et logo LAFLEURSTUDIO (SVG) |
| `original/` | Anybody d'origine, pas modifiée, avec sa licence OFL : sert juste à la comparaison sur la page |
| `source/` | Scripts Python de fabrication |

## Sur le web

```css
@font-face { font-family: "Calebard"; font-weight: 400; src: url(Calebard-Regular.woff2) format("woff2"); }
/* … une règle par graisse, de 100 (Hairline) à 1000 (Extra Black) */
@font-face { font-family: "Calebard Extreme"; font-weight: 1000; src: url(Calebard-ExtremeBlack.woff2) format("woff2"); }
```

## Versions

- **1.0.2** : réglée sur le vrai logo LAFLEURSTUDIO (celui du t-shirt). L, U, R et F à la largeur du logo ; C, G, J, O, Q, S, U dépassent de la ligne comme dans le logo ; espacement recalculé sur les espaces du logo (A et T plus aérés) ; Ų, Ư, Ứ, Ừ, Ử, Ữ, Ự ont le même U que le U ; bout du crochet du j coupé en biais. Goofy et Extra Goofy restent en 1.0.1.
- **1.0.1** : largeur 120 % (LAFLEURSTUDIO tapé en Black a la largeur du logo du studio), espacement des capitales en 6 règles, U moins large, queue du J plus courte.
- **1.0** : première version, étirée à 130 %.

## Licence

Calebard est une version modifiée d'[Anybody](https://github.com/Etcetera-Type-Co/Anybody) (Etcetera Type Co.), distribuée sous **SIL Open Font License 1.1** (voir [`OFL.txt`](OFL.txt)).
Utilisation libre, y compris commerciale. La police ne peut pas être vendue seule, et la licence doit l'accompagner.
