# Calebard

Sans-serif super étendue en **11 graisses**, du Hairline à l'Extreme Black, plus deux styles bonus **Goofy** et **Extra Goofy**, par **LaFleurStudio**.

Page : **https://jonlekern.github.io/Fonts/calebard/**

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
| ✿ | U+273F | Fleur bold |

À taper par copier-coller ou depuis le visualiseur de caractères.

## Fichiers

| Chemin | Contenu |
| --- | --- |
| `Calebard.zip` | Les 11 graisses, Goofy et Extra Goofy en TTF + licence |
| `fonts/ttf/` | Polices à installer (Mac, Windows, logiciels) |
| `fonts/woff2/` | Polices pour le web |
| `images/` | Images de la page et logo LAFLEURSTUDIO (SVG) |
| `source/` | Scripts Python de fabrication |

## Sur le web

```css
@font-face { font-family: "Calebard"; font-weight: 400; src: url(Calebard-Regular.woff2) format("woff2"); }
/* … une règle par graisse, de 100 (Hairline) à 1000 (Extra Black) */
@font-face { font-family: "Calebard Extreme"; font-weight: 1000; src: url(Calebard-ExtremeBlack.woff2) format("woff2"); }
```

## Licence

Calebard est une version modifiée d'[Anybody](https://github.com/Etcetera-Type-Co/Anybody) (Etcetera Type Co.), distribuée sous **SIL Open Font License 1.1** (voir [`OFL.txt`](OFL.txt)).
Utilisation libre, y compris commerciale. La police ne peut pas être vendue seule, et la licence doit l'accompagner.
