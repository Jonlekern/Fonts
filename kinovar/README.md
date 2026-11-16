# КИНОВАРЬ (KINOVAR)

Police russe de LaFleurStudio, **dessinée à neuf** d'après l'oustav (устав), la première écriture des livres russes. C'est l'écriture de l'Évangile d'Ostromir (1056–1057), le plus ancien livre russe daté : droite, large, lente, tracée à la plume large tenue à plat.

Le nom : la « киноварь » (cinabre) est le rouge des scribes. Ils s'en servaient pour les titres et les lettrines, pour séparer l'important du reste.

## La recette

- **La plume large tenue à plat.** Les fûts sont épais, avec une petite attaque en coin en haut à gauche et une sortie en bas à droite. Les traits horizontaux sont fins et finissent en goutte (Т, Г, Д, Б).
- **Les rondes** (О, С, Е, Ф, Э, Ю) ont les flancs épais et le haut et le bas fins. Le Е est rond, avec une langue au milieu.
- **Des lettres larges**, à peu près aussi larges que hautes, bien séparées.
- **Les lettres anciennes, par défaut** (décision de Johnny) : le И a une barre droite, le Н une barre oblique, le Ч est une coupe sur un pied. Un lecteur d'aujourd'hui peut lire le И comme un Н.
- **ss01** : le И, le Й, le Н et le Ч comme on les écrit aujourd'hui.
- **Les descendantes** : le Р, le У et le Ф passent sous la ligne ; le Д, le Ц et le Щ ont de petites gouttes.
- **Les minuscules sont des petites capitales** : l'oustav n'a qu'une casse. Mêmes formes, moins hautes (546 pour 700).
- **Le latin d'accompagnement** est une onciale tracée avec la même plume. L'oustav et l'onciale sont cousins : les deux viennent de l'écriture grecque. A, B, C, E, H, K, M, O, P, T, X et Y reprennent le dessin de la lettre russe jumelle.
- **Chiffres tabulaires.** Le point est un losange, comme la trace de la plume.
- **Crénage** automatique par profils. Les chiffres ne se crénent jamais.
- **L'accent tonique** (U+0301) se pose sur toutes les lettres.

## Caractères

Le russe complet (А–Я, а–я, Ё ё), le latin de base (A–Z, a–z), les chiffres, la ponctuation et les signes (№ ₽ € « » — …). Pas d'accents latins : c'est une police pour écrire le russe. 204 glyphes par fichier.

## Les graisses

Les trois parties d'une page de manuscrit.

| Poids | Nom | Fût | Trait fin | Fichier |
| --- | --- | --- | --- | --- |
| 300 | Stroka (строка, la ligne de texte) | 46 | 15 | `KINOVAR-Stroka.otf` |
| 500 | Zaglavie (заглавие, le titre) | 80 | 22 | `KINOVAR-Zaglavie.otf` |
| 800 | Bukvitsa (буквица, la lettrine) | 122 | 30 | `KINOVAR-Bukvitsa.otf` |

## La fabrique

```
python3 source/build_all.py
```

- `kin_letters.py` : les lettres russes et latines, et les trois graisses.
- `kin_signs.py` : chiffres, ponctuation, signes.
- `kin_fab.py` : assemble une graisse (contours, noms, OpenType, crénage, STAT). Le nettoyage des contours et le crénage viennent de `../karkas/source/kar_fab.py`.
- `build_all.py` : les 3 OTF, les 3 WOFF2 et le zip.

Il faut Python 3 avec fontTools et skia-pathops.

## Les contrôles

- fontbakery `check-universal` : 0 erreur, 0 avertissement sur les 3 fichiers.

## Licence

Usage personnel gratuit. Usage commercial sur autorisation écrite de LaFleurStudio : info@lafleurstudio.ch. Voir [`LICENCE.txt`](LICENCE.txt).
