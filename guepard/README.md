# GUÉPARD

Capitale sport années 70 et **première police variable** de LaFleurStudio. C'est une version modifiée de [Danfo](https://github.com/Afrotype/danfo) (Afrotype), une capitale inspirée des lettres peintes des bus de Lagos.

Page : **https://jonlekern.github.io/Fonts/guepard/**

## Les deux axes

| Axe | Tag | Plage | Ce que ça fait |
| --- | --- | --- | --- |
| Vitesse | `VITE` | 0–100 | Les lettres penchent (jusqu'à 12°) et s'étirent (jusqu'à +15 %) vers l'avant. Les chasses et le crénage suivent. |
| Bandes | `BAND` | 0–100 | De 0 à 50 : trois bandes de course s'ouvrent dans le bas noir des lettres. De 50 à 100 : les tranches du bas glissent à gauche et à droite, ça glitche. Le haut ne bouge jamais. |

Les deux axes se combinent librement.

## Les styles fixes

Pour les logiciels qui ne gèrent pas les polices variables : 6 fichiers TTF dans `fonts/ttf/`.

| Style | Vitesse | Bandes |
| --- | --- | --- |
| Regular | 0 | 0 |
| Course | 100 | 0 |
| Bandes | 0 | 50 |
| Course Bandes | 100 | 50 |
| Glitch | 0 | 100 |
| Course Glitch | 100 | 100 |

## Ce qu'on a changé dans Danfo

- **L'axe d'origine est retiré.** Danfo est figée à ELSH 0, sa forme lisse.
- **Le bas noir est coupé en tranches** à 110, 220 et 330 unités. Fermées, les tranches se chevauchent de 4 unités. Ouvertes, elles laissent des bandes de 18 unités. Au glitch, elles glissent de 60 unités en alternance.
- **La vitesse** est une pente (tan 12°) et un étirement horizontal de 15 %, appliqués aux contours, aux chasses, au crénage et aux ancres des accents.
- Toutes les versions viennent du même découpage. Elles ont donc exactement les mêmes points, et l'interpolation est propre partout.
- Le deux-points modificateur (U+A789), qui avait une chasse nulle dans Danfo, prend celle du deux-points.

Danfo n'a que des capitales : les minuscules tapées donnent les capitales.

## Les fichiers

- `fonts/variable/Guepard[VITE,BAND].ttf` : la police variable.
- `fonts/woff2/Guepard[VITE,BAND].woff2` : la même, pour les sites.
- `fonts/ttf/` : les 6 styles fixes.
- `Guepard.zip` : la variable, les styles fixes et la licence.

## La fabrique

```
python3 source/build_all.py
python3 -m pytest source/test_guepard.py
```

- `gp_base.py` : charge Danfo et la fige à ELSH 0.
- `gp_tranches.py` : coupe chaque glyphe en tranches.
- `gp_masters.py` : ouvre les bandes, fait glisser les tranches, applique la vitesse.
- `gp_fab.py` : assemble les 6 masters en police variable (fontTools varLib), avec STAT et noms.
- `build_all.py` : la variable, le WOFF2, les styles fixes, le zip.
- `PLAN.md` : le projet ; `PLAN-FAB.md` : le plan de fabrication.

Il faut Python 3 avec fontTools, skia-pathops et uharfbuzz.

## Les contrôles

- fontbakery `check-universal` : 0 échec sur les 6 styles fixes. Sur la variable, il reste 1 échec, qui ne s'applique pas ici : le contrôle « instance Regular » ne regarde que les axes standard (`wght`, `wdth`…), et Guépard n'a que des axes maison.

## Licence

SIL Open Font License 1.1, libre même en commercial. Copyright 2023 The Danfo Project Authors, 2026 LaFleurStudio. Voir [`OFL.txt`](OFL.txt).
