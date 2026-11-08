# Falsard

Display géométrique d'inspiration techno, au centre de gravité bas : haut compressé, bas épaissi, largeur généreuse. **10 graisses** en tailles de t-shirt, du **XXXS** au **XXXXL**, par **LaFleurStudio**.

Page : **https://jonlekern.github.io/Fonts/falsard/**

## Graisses

| Taille | Poids | Fichier |
| --- | --- | --- |
| XXXS | 200 | `Falsard-XXXS` |
| XXS | 300 | `Falsard-XXS` |
| XS | 400 | `Falsard-XS` |
| S | 500 | `Falsard-S` |
| M | 600 | `Falsard-M` |
| L | 700 | `Falsard-L` |
| XL | 800 | `Falsard-XL` |
| XXL | 900 | `Falsard-XXL` |
| XXXL | 1000 | `Falsard-XXXL` |
| XXXXL | 1100 (déclarée en 1000, le maximum du format) | `Falsard-XXXXL` |

## La recette

1. Lignes de construction calées sur le S : le haut des lettres est compressé de 50 %, le bas épaissi de 20 %.
2. Élargie à 110 % sans déformer : les traits verticaux gardent leur épaisseur d'origine.
3. Le S (et s, Š, š, $) sans tête ni queue, et les têtes et queues du 2, du 3 et du 5 coupées aussi.
4. Les minuscules suivent la même recette, avec des lignes calées sur le petit s.
5. Prolongée sous 400 (XXXS, XXS) et au-dessus de 900 (XXXL, XXXXL).
6. © ® ™ dessinés avec les lettres de Falsard.

## Versions

- **1.0.1** : guillemets « » ‹ ›, petits et posés en bas, et point médian ·. LaFleurStudio noté comme fabricant, les auteurs d'Orbitron restent crédités.
- **1.0** : première version.

## Italiques

Chaque graisse a son italique, penchée de 12° : même dessin, mêmes chasses, même crénage. Les fichiers finissent par « Italic » (`Falsard-LItalic.ttf`…). Sur le web : une famille « Falsard Italic » avec les mêmes graisses.

## Fichiers

| Chemin | Contenu |
| --- | --- |
| `Falsard.zip` | Les 10 graisses et leurs italiques en TTF + licence |
| `fonts/ttf/` | Polices à installer (Mac, Windows, logiciels) |
| `fonts/woff2/` | Polices pour le web |
| `images/` | Images de la page |
| `original/` | Orbitron d'origine, pas modifiée, avec sa licence OFL : sert juste à la comparaison sur la page |
| `source/` | Scripts Python de fabrication |

## Sur le web

```css
@font-face { font-family: "Falsard"; font-weight: 900; src: url(Falsard-XXL.woff2) format("woff2"); }
/* … une règle par taille, de 200 (XXXS) à 1000 (XXXL) */
@font-face { font-family: "Falsard XXXXL"; font-weight: 1000; src: url(Falsard-XXXXL.woff2) format("woff2"); }
```

## Licence

Falsard est une version modifiée d'[Orbitron](https://github.com/theleagueof/orbitron) (Matt McInerney, The League of Moveable Type), distribuée sous **SIL Open Font License 1.1** (voir [`OFL.txt`](OFL.txt)).
Utilisation libre, y compris commerciale. La police ne peut pas être vendue seule, et la licence doit l'accompagner.
