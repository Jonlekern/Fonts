# Shrikhard

[Shrikhand](https://fonts.google.com/specimen/Shrikhand) (Jonny Pinhorn) **élargie à 129 % sans être déformée**, en latin. Un style droit, un italique, et un **curseur Hauteur** qui l'étire vers le haut ou l'écrase jusqu'à ce qu'il ne reste qu'un trait. Par **LaFleurStudio**.

Page : **https://jonlekern.github.io/Fonts/shrikhard/**

## Le curseur Hauteur

| Axe | Tag | Plage | Ce que ça fait |
| --- | --- | --- | --- |
| Hauteur | `HAUT` | −100 à 20 | Vers le haut, les lettres s'étirent et gardent leurs traits. Vers le bas, elles s'aplatissent, et leurs traits horizontaux s'affinent un peu pour que les blancs restent ouverts. De −40 à −100, elles s'écrasent et s'élargissent jusqu'à se toucher : à −100, chaque lettre n'est plus qu'un trait de l'épaisseur du _. |

Les arrêts portent les noms de la piste du Lauberhorn, à Wengen :

| Arrêt | Hauteur |
| --- | --- |
| Start | 20 |
| Regular | 0 |
| Hundschopf | −20 |
| Kernen-S | −40 |
| Haneggschuss | −60 |
| Ziel-S | −80 |
| Ziel | −100 |

Il y a deux polices variables : la droite et l'italique (penchée de 14°, comme Shrikhand). La graisse est déclarée comme un axe fixe (400) pour que les logiciels y retrouvent leur « Regular ».

## Ce qu'on a changé dans Shrikhand

- **Le gujarati est retiré** : seul le latin reste (accents d'Europe centrale compris).
- **Élargie à 129 % sans déformer.** La lettre est redressée de 14° (autour de la mi-hauteur des minuscules), étirée, puis chaque trait retrouve son épaisseur : les points glissent à l'horizontale, de ce que l'étirement a ajouté. Le fût du n reste autour de 251 unités au lieu de 324. Les bouts arrondis, les boutons et les pointes s'étirent sans être creusés.
- **Un style droit** : le dessin redressé. **L'italique** : le même, repenché de 14°.
- **Le curseur Hauteur**, fait de 5 versions qui ont toutes les mêmes points (+20, 0, −20, −40, −100).
- **Réparations** : „ n'avait qu'une virgule (il en a deux), ‚ avait la chasse d'un tiret (il a celle de la virgule), le caron de Ľ ľ ď ť est une pièce à part, les signes mathématiques ont tous la même chasse, l'espace insécable a la chasse de l'espace.
- Les approches et le crénage d'origine sont gardés, élargis avec la lettre.

## Les fichiers

- `fonts/variable/Shrikhard[HAUT].ttf`, `fonts/variable/Shrikhard-Italic[HAUT].ttf` : les polices variables.
- `fonts/ttf/Shrikhard-Regular.ttf`, `fonts/ttf/Shrikhard-Italic.ttf` : les styles fixes (Hauteur 0), pour les logiciels sans variable.
- `fonts/woff2/` : les mêmes, pour les sites.
- `Shrikhard.zip` : les variables, les styles fixes et la licence.
- `original/` : Shrikhand d'origine, pas modifiée, avec sa licence : la fabrique part de là, et la page s'en sert pour la comparaison.
- `images/` : les images de la page.

## Sur le web

```css
@font-face { font-family: "Shrikhard"; src: url("Shrikhard[HAUT].woff2") format("woff2"); }
@font-face { font-family: "Shrikhard Italic"; src: url("Shrikhard-Italic[HAUT].woff2") format("woff2"); }
h1 { font-family: "Shrikhard"; font-variation-settings: "HAUT" -40; }
```

## La fabrique

```
python3 source/build_all.py
python3 source/page_images.py
python3 -m pytest source/test_shrikhard.py
```

- `shrikhard.py` : le latin seul, le redressement, l'élargissement sans déformer, l'aplatissement, le trait final.
- `fabrique.py` : les réparations, une version fixe, la police variable.
- `build_all.py` : les variables, les fixes, les WOFF2, les noms, la table STAT, le zip.
- `page_images.py` : l'image « élargir sans déformer » de la page.
- `test_shrikhard.py` : les contrôles.

Il faut Python 3 avec fontTools, skia-pathops et numpy.

## Licence

Shrikhard est une version modifiée de Shrikhand (Jonny Pinhorn), distribuée sous **SIL Open Font License 1.1** (voir [`OFL.txt`](OFL.txt)).
Utilisation libre, y compris commerciale. La police ne peut pas être vendue seule, et la licence doit l'accompagner.
