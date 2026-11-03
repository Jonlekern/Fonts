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

321 caractères : majuscules, minuscules, chiffres, ponctuation et symboles, et tous les accents des langues d'Europe à alphabet latin (le jeu « GF Latin Core » : français, allemand, espagnol, polonais, tchèque, slovaque, hongrois, roumain, turc, letton, lituanien, langues nordiques…), avec Ø Ł Đ Ħ Þ ð ¦ †, les accents seuls et les accents combinants, placés automatiquement sur les lettres.

## Versions

- **1.2.1** : designer : Jonathan Kern.
- **1.2** : nouvelle licence : usage personnel gratuit, usage commercial sur autorisation de LaFleurStudio.
- **1.1.2** : retour au .notdef de Brécard, sans monogramme.
- **1.1.1** : ¦ †, accents seuls à hauteur de capitale.
- **1.1** : 166 caractères en plus (jeu GF Latin Core), nouveaux accents dessinés dans le style de Brécard (macron, caron, brève, point, rond, double aigu, ogonek, virgule), symboles < > [ ] { } | ~ ^ § ¶ × ÷ ¢ ¥ • ·, placement automatique des accents combinants.
- **1.0.1** : crénage, de 1 500 à 2 100 paires selon le style (AV, LT, To, P.…). Les lettres accentuées suivent leur lettre de base.
- **1.0** : première version.

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

À partir de la version 1.2 : **usage personnel gratuit, usage commercial sur autorisation** (voir [`LICENCE.txt`](LICENCE.txt)).
Pour un usage commercial (logo, client, produit vendu, pub, site d'entreprise…), écrire à info@lafleurstudio.ch : chaque projet est étudié, l'autorisation peut être gratuite ou payante.
Revente, partage des fichiers et modification interdits sans accord écrit.

Les versions jusqu'à 1.1.2 ont été publiées sous SIL Open Font License 1.1 et restent sous cette licence.
