# Brécard

Display en pointes et en losanges : tout en angles, avec le poids en haut. **9 graisses** de 100 à 900, nommées en **klingon** (de *wa'vatlh* à *Hutvatlh*), chacune avec son **italique**, par **LaFleurStudio**.

Page : **https://jonlekern.github.io/Fonts/brecard/**

## Graisses

Les graisses sont comptées en klingon : *vatlh* veut dire « cent ». Les fichiers s'écrivent sans apostrophe.

| Style | Veut dire | Poids | Fichier |
| --- | --- | --- | --- |
| wa'vatlh | cent | 100 | `Brecard-wavatlh` |
| wa'vatlh Italic | | 100 | `Brecard-wavatlhItalic` |
| cha'vatlh | deux cents | 200 | `Brecard-chavatlh` |
| cha'vatlh Italic | | 200 | `Brecard-chavatlhItalic` |
| wejvatlh | trois cents | 300 | `Brecard-wejvatlh` |
| wejvatlh Italic | | 300 | `Brecard-wejvatlhItalic` |
| loSvatlh | quatre cents | 400 | `Brecard-loSvatlh` |
| loSvatlh Italic | | 400 | `Brecard-loSvatlhItalic` |
| vaghvatlh | cinq cents | 500 | `Brecard-vaghvatlh` |
| vaghvatlh Italic | | 500 | `Brecard-vaghvatlhItalic` |
| javvatlh | six cents | 600 | `Brecard-javvatlh` |
| javvatlh Italic | | 600 | `Brecard-javvatlhItalic` |
| Sochvatlh | sept cents | 700 | `Brecard-Sochvatlh` |
| Sochvatlh Italic | | 700 | `Brecard-SochvatlhItalic` |
| chorghvatlh | huit cents | 800 | `Brecard-chorghvatlh` |
| chorghvatlh Italic | | 800 | `Brecard-chorghvatlhItalic` |
| Hutvatlh | neuf cents | 900 | `Brecard-Hutvatlh` |
| Hutvatlh Italic | | 900 | `Brecard-HutvatlhItalic` |

## La recette

1. Dessinée de zéro à partir d'un A en pointe de flèche : sans barre, pieds coupés en biais vers l'intérieur. Que des segments droits, aucune courbe.
2. Les ronds en losange, les bouts des barres coupés en biais vers l'intérieur, les traits qui finissent seuls en coin (larges en haut, pointus en bas).
3. Le poids en haut : milieux plus bas que le centre, barres du haut plus épaisses que celles du bas.
4. Neuf graisses tirées d'un seul réglage d'épaisseur, nommées en klingon. Hutvatlh (900) est élargie de 12 %.
5. Minuscules aux verticales en coin, comme le i, et aux barres deux fois plus fines.
6. Une italique pour chaque graisse, penchée à 16°.

## Caractères

Majuscules, minuscules, chiffres, accents du français, de l'allemand et de l'espagnol (À Â Ä Á Ç É È Ê Ë Í Î Ï Ñ Ó Ô Ö Ú Ù Û Ü Ÿ Œ Æ ẞ et leurs minuscules, ß), ponctuation et symboles (« » „ “ ” ‘ ’ ¡ ¿ … – — & @ # % € $ £ © ® ™ °…).

## Fichiers

| Chemin | Contenu |
| --- | --- |
| `Brecard.zip` | Les 18 styles en TTF + licence |
| `fonts/ttf/` | Polices à installer (Mac, Windows, logiciels) |
| `fonts/woff2/` | Polices pour le web |
| `images/` | Images de la page |
| `source/` | Scripts Python de fabrication |

## Sur le web

```css
@font-face { font-family: "Brécard"; font-weight: 800; src: url(Brecard-chorghvatlh.woff2) format("woff2"); }
@font-face { font-family: "Brécard"; font-weight: 800; font-style: italic; src: url(Brecard-chorghvatlhItalic.woff2) format("woff2"); }
/* … une règle par style : wa'vatlh 100, cha'vatlh 200, wejvatlh 300, loSvatlh 400, vaghvatlh 500, javvatlh 600, Sochvatlh 700, chorghvatlh 800, Hutvatlh 900, et la même chose en italique */
```

## Licence

Brécard est distribuée sous **SIL Open Font License 1.1** (voir [`OFL.txt`](OFL.txt)), avec le nom réservé « Brécard ».
Utilisation libre, y compris commerciale. La police ne peut pas être vendue seule, et la licence doit l'accompagner. Une version modifiée doit porter un autre nom.
