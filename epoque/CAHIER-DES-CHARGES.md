# Époque — cahier des charges

Une création LaFleurStudio, dessinée de zéro. Pas une police modifiée : le nom ne finit pas en « -ard », la licence porte le certificat Lafleur.

## 1. L'idée

Le lettrage profilé des années 30 : les carrosseries des Flèches d'argent, les autorails rouges, les affiches de Grand Prix. Des lettres larges, basses, aux coins ronds, faites de **tuyaux cintrés** comme un pare-chocs chromé.

**La sauce Lafleur : trois curseurs.**

| Curseur | Tag | Plage | Ce que ça fait |
| --- | --- | --- | --- |
| Graisse | `wght` | 300–900 | Du tube fin au tube lourd. 7 arrêts, les sections du circuit du Bremgarten. |
| Vitesse | `VITE` | 0–100 | La lettre penche vers l'avant, jusqu'à 14°, et **le sillage** sort : la barre du milieu de A, B, E, F, H, P, R, e, f, t file derrière la lettre, à gauche. Chaque lettre prend aussi un peu d'air. En Chrome, le sillage fait trois filets. |
| Chrome | `CHRM` | 0–100 | Chaque trait s'ouvre en trois bandes qui suivent la courbe. **La gauche est légère, la droite lourde** : deux filets fins à gauche, la bande pleine à droite, comme la lumière sur un jonc chromé. |

Les trois se combinent librement. À 0 partout, c'est une capitale Art déco pleine et posée.

## 2. Ce qu'on ne fait pas

- **On ne copie aucune police.** Ni Silver Streak (on ne la regarde pas), ni Motor, Zeppelin, Prisma. Les sources sont les objets d'époque et leurs principes (voir §3).
- Pas de bandes horizontales à travers la lettre (c'est Motor, et c'est Guépard chez nous) : nos filets **suivent le trait**.
- Pas de filet épais + filet fin seulement (c'est Zeppelin) : trois bandes, dégradées.
- Pas de photo ni de scan. Pas de mention d'outil. Adresse publique : info@lafleurstudio.ch.

## 3. Ce que la recherche a donné (les principes d'époque)

Vérifié dans les sources : Motor (Sommer, 1930) a des bandes ouvertes lues comme des reflets de chrome ; Zeppelin (Koch, 1929) double le trait d'un filet ; Prisma (Koch, 1931) est faite de lignes parallèles ; Huxley Vertical et Agency Gothic ont des variantes rondes pour A, M, N, W ; les numéros des Flèches d'argent étaient peints à la main, différents à chaque course ; les autorails et les trains profilés portaient des capitales sobres, droites, très espacées.

Les traits qu'on retient :

1. Trait d'épaisseur presque constante (monoligne), horizontales un peu plus fines pour l'œil.
2. Rondes en **stade ou en superellipse**, côtés presque droits : jamais le cercle pur.
3. **Taille basse** : les barres de A, E, F, H vers 36 % de la hauteur. Variante taille haute.
4. Bouts **coupés à plat**, sans ergot. G sans éperon. R et K à jambe droite.
5. Variantes rondes d'époque : A en arche, M et N en arches, W rond.
6. Penchée de 10 à 15° sur les affiches, droite sur les trains : c'est le curseur Vitesse.
7. Capitales larges, de chasses égalisées (O, H, E proches), faites pour être espacées.
8. Chiffres de course : 1 à drapeau court, 7 barré en variante, 6 et 9 à queue ouverte, 0 en stade.

## 4. Le dessin

- **Grille** : 1000 unités. Capitales 700, hauteur d'x 500, ascendantes 730, descendantes −190. Dépassement des rondes : 10.
- **Construction** : chaque lettre est une liste de **tuyaux** (un tracé fait de droites et de virages arrondis, avec une épaisseur). Rien n'est découpé après coup : toutes les versions d'une lettre ont donc les mêmes points, et la police peut glisser d'une graisse, d'une pente ou d'un chrome à l'autre.
- **Virages** : superelliptiques (plus tendus qu'un arc de cercle), rayon extérieur = rayon de l'axe + demi-épaisseur, rayon intérieur = rayon de l'axe − demi-épaisseur.
- **La gauche légère, la droite lourde** : dans chaque lettre, un trait vertical est d'autant plus gras qu'il est à droite (fût de gauche à −24/−30 %, fût de droite à +24/+30 %). Un fût seul (I, l) garde l'épaisseur moyenne. Pareil pour les diagonales et les côtés des rondes. Avec ou sans Chrome.
- **Contraste** : horizontales à 90 % des verticales en maigre, 84 % en gras.
- **Jonctions** : un tuyau qui en rejoint un autre s'arrête contre lui (ses filets butent sur la première bande de l'autre). Aux pointes (A, V, W, M), les deux tuyaux sont coupés sur l'axe de la pointe : les filets font un chevron.
- **Chrome** : le trait est divisé dans son épaisseur en filet + blanc + filet + blanc + bande pleine, de gauche à droite. Sur un trait qui monte ou qui descend, les filets sont toujours du côté gauche de la lettre ; dans les virages et sur les barres, les trois bandes s'égalisent en douceur (elles enflent et s'affinent avec la courbe). Blancs et filets : jamais moins de 10 unités à la graisse la plus fine, 22 à la plus grasse. À Chrome 0 les bandes se recouvrent de 2 unités : aucune couture.
- **Graisses** (fût en unités) : 300 → 72, 400 → 96, 500 → 118, 600 → 140, 700 → 162, 800 → 184, 900 → 206 (à régler à l'œil).

| Arrêt | Poids | Section du Bremgarten |
| --- | --- | --- |
| Forsthaus | 300 | le virage le plus lent |
| Bethlehem | 400 | la sortie des stands (Regular) |
| Eichholz | 500 | l'entrée en forêt |
| Eymatt | 600 | la grande courbe |
| Wohlenrampe | 700 | la rampe |
| Jordenrampe | 800 | la descente |
| Glasbrunnen | 900 | la section la plus rapide |

## 5. Les caractères

- Minuscules a–z + ı ȷ ß æ œ ø ð þ ł đ ħ ; capitales A–Z + Æ Œ Ø Ð Þ Ł Đ Ħ ẞ.
- Chiffres, ponctuation, signes, monnaies, mathématiques, exposants, fractions.
- Accents : tout le jeu GF Latin Core (comme Escapement).
- **Fonctions** : `ss01` taille haute ; `ss02` variantes rondes (A M N W, a g y selon le dessin) ; `ss03` 7 barré et 0 pointé ; `cpsp` capitales espacées ; `kern` par familles ; `tnum` ; `frac` ; numéros de course dans un rond (① à ⑨, ⓪) si le temps le permet.

## 6. Les fichiers

- `fonts/variable/Epoque[CHRM,VITE,wght].ttf` : la variable, 3 axes.
- `fonts/otf/` : les fixes, 7 graisses × 4 styles (Regular, Course, Chrome, Course Chrome) si tout passe ; au minimum 7 × 2 (Regular, Course).
- `fonts/woff2/`, `Epoque.zip`, `LICENCE.txt` (usage personnel gratuit, commercial sur autorisation, certificat Lafleur), `README.md`, `index.html`, `source/`.

## 7. La qualité (critères de réception)

1. fontbakery `check-universal` : 0 erreur, 0 avertissement, sur chaque fichier.
2. Détecteur (`outils/defauts.py`) : aucune écharde, aucune marche ; les fentes sont seulement les filets voulus.
3. Loupe sur chaque lettre, aux graisses extrêmes, à Chrome 0 et 100, à Vitesse 0 et 100.
4. Interpolation : aucune lettre ne se croise ni ne se retourne entre deux arrêts (contrôle fontTools `interpolatable` + planches aux positions intermédiaires).
5. Épaisseurs mesurées : fûts égaux à ±2 unités dans toute la police, à chaque graisse.
6. Espacement : rythme régulier dans HHOHOO, nnonoo, et dans de vrais mots ; crénage des paires classiques.
7. Page : rien ne déborde à 1280 et à 390 px, clair et sombre ; testeur avec les trois curseurs, texte par défaut « LAFLEURSTUDIO création graphique ».
8. Tests automatiques (`pytest`) : jeu de caractères, axes, épaisseurs, compatibilité des versions.

## 8. Le thème suisse (MOTS.md)

Le Grand Prix de Suisse au Bremgarten (Berne, 1934–1939), la Flèche rouge des CFF (1935), le Klausenrennen, la Landi 39.
Mots : Bremgarten · Forsthaus · Glasbrunnen · Eymatt · Bethlehem · Klausen · Linthal · Urnerboden · Dübendorf · Flèche rouge · Roter Pfeil · Doppelpfeil · Landi 39 · Caracciola · Rosemeyer · 7,280 km · 2:34,5.
