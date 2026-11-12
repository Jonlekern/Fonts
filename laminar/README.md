# LAMINAR

Art déco de LaFleurStudio, **dessinée à neuf**. Le Paris de 1925 (haute, étroite, barres hautes), le contraste des affiches de Broadway et les lignes de vitesse du Streamline. Pour les cinémas, les hôtels, les bars et les trains de nuit.

Le nom : un écoulement laminaire, c'est l'air qui glisse en lignes parallèles le long d'une carrosserie profilée. C'est exactement ce que font les trois lignes de la version vitesse.

## La recette

- **Pleins et déliés.** Les fûts sont pleins, les barres sont des filets. Les obliques suivent la plume : la descendante pleine, la montante fine (A, V, M, N, X, Y, K).
- **Ronds au compas.** O, C, G et Q sont des cercles parfaits : un cercle extérieur, un cercle intérieur décalé, le plein à gauche et le délié à droite. Les bouts du C et du G sont coupés dans l'axe du compas.
- **Barres hautes.** Le A, le E, le F, le H et le R portent leur barre haut, comme sur les façades de 1925.
- **Coins profilés.** Le coin extérieur des E, F, L, B, D, P et R est arrondi, façon Streamline.
- **Capitales et petites capitales.** Les majuscules donnent les capitales, les minuscules donnent les petites capitales. Rien à activer.
- **La vitesse, derrière l'italique.** Les lettres restent droites ; trois lignes les traversent en blanc et filent en noir d'une lettre à l'autre. La première lettre d'un mot a une traîne, la dernière finit en bout rond, une lettre seule a les deux.
- **Ligatures.** Toujours actives : TT, LL, TH, LT. Sur demande (dlig) : OO, CO, CA, LA, LE, AV, VA, AW, MM, NN, AR, ER. En capitales et en petites capitales, en sobre et en vitesse.
- **Options de la vitesse.** ss01 : les lignes passent derrière les lettres. ss02 : la traîne seule, sans lignes dans le mot.
- **Chiffres tabulaires.** Tous de la même chasse. Le 0 est un stade, pour ne jamais le confondre avec le O.
- **Crénage** automatique par familles en sobre. En vitesse, les lettres ne se crénent jamais entre elles : les lignes restent continues.

## Comment avoir la vitesse

Chaque graisse est une petite famille à deux styles : **Regular** (sobre) et **Italic** (vitesse).

- **Word, PowerPoint, Pages, Keynote, Canva, LibreOffice :** sélectionne le texte et appuie sur Italique (Ctrl+I ou ⌘I).
- **InDesign, Illustrator, Figma, Photoshop :** choisis le style « Italic » dans le menu des styles. N'utilise pas le faux italique de Photoshop.
- **Sur un site :** `font-style: italic` ou `<em>`.

La traîne et le bout rond demandent un logiciel qui gère les alternates contextuelles (calt) : navigateurs, InDesign, Illustrator, Figma, Affinity, Pages, Keynote, Word récent. Sinon, les lignes traversent simplement tout le mot.

## Les graisses

| Poids | Nom | Fût | Fichiers |
| --- | --- | --- | --- |
| 300 | 030 | 58 | `LAMINAR-030.otf` · `LAMINAR-030Italic.otf` |
| 600 | 060 | 118 | `LAMINAR-060.otf` · `LAMINAR-060Italic.otf` |
| 900 | 090 | 190 | `LAMINAR-090.otf` · `LAMINAR-090Italic.otf` |

030 pour l'hôtel, 060 pour le bar, 090 pour le fronton du cinéma.

## Caractères

Capitales, petites capitales, chiffres, ponctuation, signes et accents des langues d'Europe en alphabet latin, plus les ligatures. 359 signes par fichier sobre ; la vitesse ajoute les formes de début, de fin et les options.

## Fichiers

- `fonts/otf/` : les 6 fichiers à installer (3 graisses × sobre, vitesse)
- `fonts/woff2/` : les 6 fichiers pour le web
- `LAMINAR.zip` : les 6 fichiers (OTF) + la licence + « À LIRE »
- `LICENCE.txt` : la licence
- `source/` : les scripts Python de fabrication (`python3 source/build_all.py`)

## Licence

Usage personnel gratuit. Usage commercial sur autorisation écrite de LaFleurStudio : info@lafleurstudio.ch. Voir `LICENCE.txt`.

© 2026 LaFleurStudio · Jonathan Kern
