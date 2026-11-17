# Époque — cahier des charges

Une création LaFleurStudio, dessinée de zéro. Pas une police modifiée : le nom ne finit pas en « -ard », la licence porte le certificat Lafleur.

## 1. L'idée

Le lettrage de course des années 30, signé comme un emblème chromé des années 50.

- **Ce qui constitue (années 30)** : le contraste Art déco. Le fût de droite est très gras, le fût de gauche et toutes les barres sont des filets. Dans chaque lettre, la gauche est légère et la droite lourde.
- **Ce qui signe (années 50)** : chaque lettre porte **une signature à elle**, légère, jamais répétée : une aile, une pointe effilée, un bras détaché, une queue qui file.

Deux curseurs :

| Curseur | Tag | Plage | Ce que ça fait |
| --- | --- | --- | --- |
| Graisse | `wght` | 300–900 | Le fût de droite grossit, les filets restent fins. 7 arrêts : les sections du circuit du Bremgarten. |
| Vitesse | `VITE` | 0–100 | La lettre penche vers l'avant, jusqu'à 14°, et prend un peu d'air. À 100 : le style Course. |

## 2. Ce qu'on ne fait pas

- On ne copie aucune police. Les sources sont les objets d'époque et leurs principes.
- Pas de motif répété d'une lettre à l'autre : une signature par lettre.
- Pas de photo ni de scan. Pas de mention d'outil. Adresse publique : info@lafleurstudio.ch.

## 3. Le dessin

- **Grille** : 1000 unités. Capitales 700, hauteur d'x 480, ascendantes 740, descendantes −190.
- **Construction** : chaque lettre est une liste de **tuyaux** (un tracé de droites et de virages, avec une épaisseur). Rien n'est découpé après coup : toutes les versions d'une lettre ont les mêmes points, la police glisse d'une graisse et d'une pente à l'autre.
- **Épaisseur** : elle dépend de la direction du trait (vertical = fût, horizontal = filet) et de sa place dans la lettre (à gauche léger, à droite lourd). Un fût seul (I, l) est entre le moyen et le gras.
- **Traits effilés** : un tuyau peut finir en pointe. C'est l'outil des signatures.
- **Virages** : superelliptiques. Le bord d'un virage ne mange jamais plus que la moitié de son tronçon : pas de bec dans les gras.
- **Signatures** : la liste est dans la première ligne de chaque lettre (`source/capitales.py`, `source/minuscules.py`).

| Arrêt | Poids | Section du Bremgarten |
| --- | --- | --- |
| Forsthaus | 300 | |
| Bethlehem | 400 | Regular |
| Eichholz | 500 | |
| Eymatt | 600 | |
| Wohlenrampe | 700 | Bold |
| Jordenrampe | 800 | |
| Glasbrunnen | 900 | |

## 4. Les caractères

- Minuscules a–z + ı ȷ ß æ œ ø ð þ ł đ ħ ; capitales A–Z + Æ Œ Ø Ð Þ Ł Đ Ħ ẞ.
- Chiffres de chasse fixe, ponctuation, signes, monnaies, mathématiques.
- 145 lettres accentuées (jeu GF Latin Core). 319 glyphes.
- Crénage par familles, calculé sur le corps des lettres. Dans les maigres, les signatures passent chez la voisine ; plus la lettre est grasse, moins elles entrent.

## 5. Les fichiers

- `fonts/variable/Epoque[VITE,wght].ttf` : la variable, 2 axes.
- `fonts/otf/`, `fonts/woff2/` : 7 graisses × Regular et Course (Italic).
- `Epoque.zip`, `LICENCE.txt`, `README.md`, `index.html`, `source/`.

## 6. La qualité

1. fontbakery `check-universal` : 0 erreur, 0 avertissement, sur chaque fichier.
2. Loupe sur chaque lettre, aux graisses 300, 400, 900, droite et Course. Le détecteur de défauts ne sert pas ici : il prend chaque pointe voulue pour un défaut.
3. Tests automatiques (`pytest source/tests`) : jeu de caractères, axes, mêmes points à toutes les positions.
4. Page : rien ne déborde à 1280 et à 390 px ; testeur à deux curseurs, texte par défaut « LAFLEURSTUDIO création graphique ».

## 7. Le thème suisse (MOTS.md)

Le Grand Prix de Suisse au Bremgarten (Berne, 1934–1939), la Flèche rouge des CFF, le Klausenrennen, la Landi 39.
