# Sources de Jalousia (Net et Craie)

| Fichier | Contenu |
| --- | --- |
| `dessins/` | Les chiffres romains dessinés à la main : I V X, L C, D, M |
| `essai.py` | Tracé des 26 capitales et rendu d'un mot (image) |
| `minuscules.py` | Les minuscules, avec les pièces des capitales |
| `italique.py` | Minuscules de l'italique et pente de 12° |
| `signes.py` | Chiffres, ponctuation, signes, lettres en plus, accents |
| `build.py` | Fabrication des fichiers de police |
| `gf_core.json` | Liste des caractères GF Latin Core |

I, L, D, M, V et X viennent des dessins (le C dessiné a été remplacé par un C rond). Les autres lettres sont faites avec leurs morceaux.

## Refaire les polices

```sh
python3 build.py                    # les 8 droits (Net et Craie)
python3 build.py italique           # les 8 italiques
python3 build.py net 400            # un style, une graisse
```

Les fichiers vont dans `jalousia/fonts/`.

## Refaire une image d'essai

```sh
python3 essai.py LAFLEURSTUDIO essai-craie.png
python3 essai.py LAFLEURSTUDIO essai-net.png net
```
