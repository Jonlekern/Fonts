# Sans Rire

Comic sans de LaFleurStudio, **entièrement dessinée à neuf**, écrite au feutre. Chaque lettre est une suite de gestes ; un feutre rond glisse le long de chaque geste. Il bave un peu quand il se pose, gonfle un peu quand il se lève, et la main tremble à peine. Majuscules et minuscules.

Le nom : *sans rire*, c'est une police comique. Et c'est une sans.

## La recette

- **Le feutre** : une pointe ronde, un petit pâté d'encre au départ de chaque trait, un léger tremblé de la main.
- **Les formes** : des bols en « squircle », ni ronds ni carrés ; une grande hauteur d'x ; un a et un g à un seul étage ; un l et un t qui finissent par une petite virgule.
- **Trois prises par lettre** : chaque lettre et chaque chiffre est tracé trois fois. Dans le texte, les trois versions tournent (fonction `calt`, active par défaut) : les lettres penchent, sautillent et changent un peu de taille. Deux lettres pareilles côte à côte ne sont jamais identiques.
- **Hauteurs** : minuscules à 520, capitales à 712, montantes à 770, descendantes à −235.
- **Espacement** : crénage par familles (une lettre, ses accents et ses trois prises), vérifié pour que deux lettres qui penchent l'une vers l'autre ne se touchent jamais.

## Pas sérieux

| Fonction | Ce qu'elle fait | En CSS |
| --- | --- | --- |
| `calt` | Les 3 prises tournent : le texte danse (actif par défaut) | `font-feature-settings: "calt" 0` pour l'arrêter |
| `ss01` Zinzin | Les lettres sautent beaucoup plus haut et plus bas | `font-feature-settings: "ss01"` |
| `ss02` Cœurs | Des cœurs à la place des points sur les i et les j | `font-feature-settings: "ss02"` |
| `liga` | `?!` et `!?` en un seul signe, `!!` → ‼, `<3` → ♥, `wtf` avec des traits de surprise | actif par défaut |

## Les graisses

Les graisses vont du petit rire au fou rire, de **Lol** à **Jpp** (« j'en peux plus »). Le dessin ne change pas, seul le feutre s'épaissit.

| Poids | Nom | Feutre | Fichier |
| --- | --- | --- | --- |
| 300 | Lol | 40 | `SansRire-Lol.otf` |
| 400 | Mdr | 62 | `SansRire-Mdr.otf` |
| 600 | Ptdr | 88 | `SansRire-Ptdr.otf` |
| 800 | Xptdr | 116 | `SansRire-Xptdr.otf` |
| 900 | Jpp | 146 | `SansRire-Jpp.otf` |

## Caractères

Tout le jeu GF Latin Core : majuscules, minuscules, chiffres, ponctuation, signes et accents des langues d'Europe en alphabet latin. En plus : ‽ ‼ ♥.

## Fichiers

- `fonts/otf/` : les 5 graisses à installer (OpenType)
- `fonts/woff2/` : les 5 graisses pour le web
- `SansRire.zip` : les 5 graisses (OTF) + la licence
- `LICENCE.txt` : la licence

## Licence

Usage personnel gratuit. Usage commercial sur autorisation écrite de LaFleurStudio : info@lafleurstudio.ch. Voir `LICENCE.txt`.

© 2026 LaFleurStudio · Jonathan Kern
