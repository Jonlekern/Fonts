# Clebard

Néo-grotesque suisse en extra-large : un chien de race qui a pris du coffre. **6 graisses** en tailles de café, du **Demi** au **Trenta**, par **LaFleurStudio**.

Page : **https://jonlekern.github.io/Fonts/clebard/**

## Graisses

| Taille | Graisse | Déclarée | Fichier |
| --- | --- | --- | --- |
| Demi | 400 | 400 | `Clebard-Demi` |
| Short | 600 | 600 | `Clebard-Short` |
| Tall | 800 | 800 | `Clebard-Tall` |
| Grande | 1000 | 900 | `Clebard-Grande` |
| Venti | 1200 | 950 | `Clebard-Venti` |
| Trenta | 1400 | 1000 | `Clebard-Trenta` |

Le format s'arrête à 1000 : Grande, Venti et Trenta sont déclarées entre 900 et 1000, toutes dans la même famille « Clebard ».

## La recette

1. Base libre : TeX Gyre Heros, version libre du classique suisse (d'après Nimbus Sans L d'URW++).
2. Élargie à 140 % sans déformer : les fûts gardent leur épaisseur visée.
3. Six graisses, contours poussés vers l'extérieur ou rentrés, de 400 à 1400.
4. Au-delà de 1000, traits horizontaux affinés là où les blancs se bouchent (e, s, a, g, 3, 5, 6, 9, €).
5. Trenta trichée : là où la 1400 casse, la Venti épaissie seulement à l'horizontale.
6. Espacement et crénage de Calebard.

## Fichiers

| Chemin | Contenu |
| --- | --- |
| `Clebard.zip` | Les 6 tailles en TTF et WOFF2, la licence et les sources (toute l’œuvre listée dans `MANIFEST-Clebard.txt`) |
| `fonts/ttf/` | Polices à installer (Mac, Windows, logiciels) |
| `fonts/woff2/` | Polices pour le web |
| `images/` | Images de la page |
| `source/` | Scripts Python de fabrication |

## Sur le web

```css
@font-face { font-family: "Clebard"; font-weight: 400; src: url(Clebard-Demi.woff2) format("woff2"); }
/* … une règle par taille : Demi 400, Short 600, Tall 800, Grande 900, Venti 950, Trenta 1000 */
```

## Licence

Clebard est une version modifiée de TeX Gyre Heros (B. Jackowski et J. M. Nowacki, GUST e-foundry), elle-même d'après Nimbus Sans L d'URW++. Elle est distribuée sous **GUST Font License** (GFL), une variante de la LaTeX Project Public License 1.3c : voir [`LICENCE.txt`](LICENCE.txt), [`GUST-FONT-LICENSE.txt`](GUST-FONT-LICENSE.txt) et [`lppl.txt`](lppl.txt).
Utilisation libre, y compris commerciale. Les fichiers de licence doivent accompagner la police.
