# Malabard

Display de course allongée : on a rallongé les droites, les courbes n'ont pas bougé. **7 graisses** de l'**ExtraLight** à l'**ExtraBold**, plus une **Medium Italic**, par **LaFleurStudio**.

Page : **https://jonlekern.github.io/Fonts/malabard/**

## Graisses

| Style | Poids | Fichier |
| --- | --- | --- |
| ExtraLight | 200 | `Malabard-ExtraLight` |
| Light | 300 | `Malabard-Light` |
| Regular | 400 | `Malabard-Regular` |
| Medium | 500 | `Malabard-Medium` |
| Medium Italic | 500 | `Malabard-MediumItalic` |
| SemiBold | 600 | `Malabard-SemiBold` |
| Bold | 700 | `Malabard-Bold` |
| ExtraBold | 800 | `Malabard-ExtraBold` |

## La recette

1. Base libre : Righteous, d'Astigmatic.
2. Seules les parties verticales sont allongées, de 50 % de la hauteur des minuscules : les arrondis et les traits horizontaux gardent leur forme et leur épaisseur.
3. Les lettres à diagonales (K, N, V, X, Z…) sont étirées d'un bloc, pour que leurs diagonales restent parallèles.
4. Sept graisses, traits amincis ou épaissis à partir de la Medium. En gras, les lettres s'élargissent un peu (jusqu'à 114 %).
5. Points, accents et blancs gardés en gras ; jonctions gardées en fin.
6. Medium Italic penchée à 12°, avec un crénage qui empêche les lettres de se toucher.

## Fichiers

| Chemin | Contenu |
| --- | --- |
| `Malabard.zip` | Les 8 styles en TTF + licence |
| `fonts/ttf/` | Polices à installer (Mac, Windows, logiciels) |
| `fonts/woff2/` | Polices pour le web |
| `images/` | Images de la page |
| `source/` | Scripts Python de fabrication |

## Sur le web

```css
@font-face { font-family: "Malabard"; font-weight: 500; src: url(Malabard-Medium.woff2) format("woff2"); }
@font-face { font-family: "Malabard"; font-weight: 500; font-style: italic; src: url(Malabard-MediumItalic.woff2) format("woff2"); }
/* … une règle par graisse : ExtraLight 200, Light 300, Regular 400, Medium 500, SemiBold 600, Bold 700, ExtraBold 800 */
```

## Licence

Malabard est une version modifiée de [Righteous](https://github.com/google/fonts/tree/main/ofl/righteous) (Brian J. Bonislawsky, Astigmatic), distribuée sous **SIL Open Font License 1.1** (voir [`OFL.txt`](OFL.txt)).
Utilisation libre, y compris commerciale. La police ne peut pas être vendue seule, et la licence doit l'accompagner.
