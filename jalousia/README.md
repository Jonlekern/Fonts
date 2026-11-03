# Jalousia

Police inspirée des chiffres romains néo-gothiques, capitales et minuscules.
Deux styles : **Craie** (trait à la craie) et **Net** (trait net), chacun en 4 graisses aux noms latins. Jeu de caractères GF Latin Core.

| Graisse | Nom |
| --- | --- |
| 100 | Centum |
| 200 | Ducenti |
| 300 | Trecenti |
| 400 | Quadringenti |

| Chemin | Contenu |
| --- | --- |
| `fonts/ttf/` | Jalousia-CraieCentum.ttf … Jalousia-NetQuadringenti.ttf (8 fichiers) |
| `fonts/woff2/` | Les mêmes pour le web |
| `dessins/` | Les lettres romaines dessinées à la main : I V X, L C, D, M |
| `essai.py` | Tracé des 26 lettres et rendu d'un mot |
| `minuscules.py` | Les minuscules, avec les pièces des capitales |
| `signes.py` | Chiffres, ponctuation, signes, lettres en plus, accents |
| `build.py` | Fabrication des fichiers de police |
| `gf_core.json` | Liste des caractères GF Latin Core |

I, L, D, M, V et X viennent des dessins. Les autres lettres sont faites avec leurs morceaux.
Espacement : les lettres se glissent les unes sous les autres tant que les traits restent à bonne distance ; les barres de V et W peuvent toucher la lettre d'à côté.
Ponctuation : tirets, guillemets et points médians sont placés pour les minuscules ; la fonction OpenType `case` les remonte pour les capitales.

## Refaire les polices

```sh
python3 build.py fonts              # les 8 fichiers
python3 build.py fonts net 400      # un style, une graisse
```

## Refaire les images

```sh
python3 essai.py LAFLEURSTUDIO essai-craie.png
python3 essai.py LAFLEURSTUDIO essai-net.png net
```

## Descendance

**Fûstard 132**, police techno gothique, est née de Jalousia. Elle a sa propre branche : `fustard-132`.
