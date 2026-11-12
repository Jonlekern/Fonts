# SHEARLINE

Fraktur de LaFleurStudio, **dessinée à neuf** à la plume large. Le gothique sombre et religieux des bréviaires, des pierres tombales et des cathédrales la nuit : rondes cassées, têtes et pieds en losange, capitales à trompe. Et des **croix** dans les lettres.

Le nom : la *shear line*, c'est la ligne de cisaillement, là où la matière casse. C'est le sens même de « Fraktur ».

## La recette

- **À la plume.** Chaque trait est le passage d'une plume large tenue à 40°. Les pleins et les déliés viennent de l'angle de la plume, rien n'est dessiné à part.
- **Les croix.** Par défaut, chaque lettre a la sienne : croix patriarcale (deux barres) sur les hampes du b, du h et du k, croix latine sur le l, le t et le f, petite croix à la place du point du i et du j, croix pattée sur le fût des capitales, croix fine dans le contre du C, du G, du O, du Q et du T.
- **Options de croix.** ss01 : que des croix latines. ss02 : que des patriarcales. ss03 : que des pattées. ss04 : sans croix, la Fraktur pure.
- **Lettrines.** En italique, les capitales deviennent des lettrines : un bloc noir, la lettre en réserve, un filet blanc et des croix aux coins. Les minuscules ne changent pas. ss05 donne les mêmes lettrines dans le Regular.
- **Le ſ long.** Il se place tout seul : ſ au début et au milieu du mot, s rond à la fin, comme dans les vieux livres. ss06 remet le s moderne partout.
- **Ligatures** toujours actives : ch, ck, tz, ſt, ſſ.
- **Signes liturgiques** : † ‡ ✝ ☦ ✠ ☩ ℣ ℟ ⁂, avec § et ¶.
- **Le trait d'union** est double et penché, comme en Fraktur.
- **Chiffres** de la même chasse, tracés à la même plume.
- **Crénage** automatique par familles : une lettre et ses accents partagent les mêmes paires.

## Comment avoir les lettrines

Chaque graisse est une petite famille à deux styles : **Regular** (la Fraktur) et **Italic** (les capitales en lettrines).

- **Word, PowerPoint, Pages, Keynote, Canva, LibreOffice :** sélectionne la première lettre et appuie sur Italique (Ctrl+I ou ⌘I).
- **InDesign, Illustrator, Figma, Photoshop :** choisis le style « Italic » dans le menu des styles, ou active l'option ss05. N'utilise pas le faux italique de Photoshop.
- **Sur un site :** `font-style: italic` ou `<em>`, ou `font-feature-settings: "ss05"`.

Le ſ long et les ligatures demandent un logiciel qui gère les alternates contextuelles (calt) et les ligatures : navigateurs, InDesign, Illustrator, Figma, Affinity, Pages, Keynote, Word récent.

## Les graisses

| Poids | Nom | Plume | Fichiers |
| --- | --- | --- | --- |
| 300 | Épreuve | 60 | `SHEARLINE-Epreuve.otf` · `SHEARLINE-EpreuveItalic.otf` |
| 600 | Tirage | 92 | `SHEARLINE-Tirage.otf` · `SHEARLINE-TirageItalic.otf` |
| 900 | Aplat | 128 | `SHEARLINE-Aplat.otf` · `SHEARLINE-AplatItalic.otf` |

Des noms d'atelier d'impression : l'épreuve, légère, le tirage, et l'aplat, le noir plein.

## Caractères

Majuscules, minuscules, ſ long, chiffres, ponctuation, signes, signes liturgiques et accents des langues d'Europe en alphabet latin, plus les ligatures et les options.

## Fichiers

- `fonts/otf/` : les 6 fichiers à installer (3 graisses × Regular, Italic)
- `fonts/woff2/` : les 6 fichiers pour le web
- `SHEARLINE.zip` : les 6 fichiers (OTF) + la licence + « À LIRE »
- `LICENCE.txt` : la licence
- `source/` : les scripts Python de fabrication (`python3 source/build_all.py`)

## Licence

Usage personnel gratuit. Usage commercial sur autorisation écrite de LaFleurStudio : info@lafleurstudio.ch. Voir `LICENCE.txt`.

© 2026 LaFleurStudio · Jonathan Kern
