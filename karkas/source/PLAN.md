# KARKAS (КАРКАС) : le plan

Décidé avec Johnny le 14 novembre 2026.

## L'idée

Réinterpréter la **vyaz** (вязь), l'écriture russe entrelacée des titres de manuscrits, **en lettres latines**, dans un dessin géométrique et brutaliste. Le nom : « каркас », l'ossature en béton d'un bâtiment ; le mot russe vient du français « carcasse ». Dans la vyaz, les lettres partagent leurs fûts comme une ossature partage ses poteaux.

Trois versions sont prévues, avec la même liste de liaisons : **Modern** (celle-ci, la première), puis Classic (dessin à la plume) et Display (expérimentale). Ce plan couvre la Modern.

## Ce que la vraie vyaz nous donne

- Une ligne qui devient une bande continue, comme un code-barres.
- Des lettres très hautes (jusqu'à 10 fois leur largeur aux XVe–XVIe siècles), une seule casse.
- Les gestes des scribes : fût partagé, lettre rétrécie logée dans un creux, petites lettres empilées, bouche-trous décoratifs.
- Le style géométrique était celui de Moscou.

## Les décisions de Johnny

- Latin prioritaire, cyrillique « pour le délire » (bonus).
- Capitales seulement.
- Modern en premier, avec OpenType.
- **Approche A** : chaque liaison est une ligature, un dessin par groupe de lettres.
- Nom : KARKAS.
- Production complète sans validation intermédiaire ; rien n'est poussé avant « Pousse ».

## Mes choix (à corriger au besoin)

### Le dessin

- 1000 unités, capitales à 800, environ 4 à 5 fois plus hautes que larges.
- Tout est droit : fûts, barres, obliques courtes. Même épaisseur partout. Coins vifs. Aucune courbe.
- Les fûts montent sur toute la hauteur ; l'événement de la lettre (barre, boucle, oblique) est serré dans une zone, taille haute à 68 % de la hauteur. C'est le principe de la vyaz.
- Les touches minuscules donnent les mêmes capitales (même glyphe).
- Jeu de caractères : celui de LAMINAR (latin de base, accents d'Europe, chiffres, ponctuation, signes).

### Les graisses : les marques de béton

En Russie, le béton se classe par marque : plus le chiffre est haut, plus il résiste.

| Graisse | Fût | Poids |
| --- | --- | --- |
| M150 | fin | 300 |
| M300 | moyen | 500 |
| M500 | gras | 800 |

### Les liaisons (feature `liga`, active par défaut)

Toutes fabriquées par script à partir des pièces des lettres, un glyphe par groupe.

1. **Fût partagé** : le fût droit de la première lettre est le fût gauche de la seconde (HE, NE, UR, AN, OU…).
2. **Lettre logée** : une lettre rétrécie se loge dans le creux d'une grande. Après L (sur le pied), après T et avant T (sous la barre), après F et P (sous le bras, sous la boucle), dans C (dans la bouche).
3. **Lettres empilées** : une lettre double s'écrit en deux étages (EE, LL, SS, TT…).
4. **Groupes de trois** : une lettre sous chaque bras du T (ATA, ITE, STE…) et des chaînes de fûts partagés (AND, ONE, UNE…).

Une paire sans ligature reste serrée côte à côte.

### Les options

- `ss01` : les lettres doubles partagent un fût au lieu de s'empiler (HH, NN, MM, OO…).
- `ss02` : des losanges bouchent les creux des lettres restées seules (L, T, F, P…).
- Couper les ligatures : option standard « ligatures » du logiciel ou `font-variant-ligatures: none`.

### Le cyrillique (bonus, après le latin)

Capitales russes А–Я et Ё dans le même dessin, minuscules sur les mêmes glyphes, liaisons par fût partagé et lettres doubles empilées.

## La fabrique

`python3 source/build_all.py` refait tout : 3 OTF, 3 WOFF2.

- `kar_core.py` : outils de dessin (rectangles, obliques, unions).
- `kar_letters.py` : les lettres, dessinées pour une hauteur donnée (une lettre logée est la même lettre, moins haute, même trait).
- `kar_liga.py` : les règles de liaison et la liste des groupes.
- `kar_signs.py` : chiffres, ponctuation, signes, accents.
- `kar_cyr.py` : le cyrillique.
- `kar_fab.py` : assemble une graisse (contours, noms, OpenType, crénage, STAT).

## Les contrôles

- fontbakery `check-universal` sur chaque fichier.
- `outils/defauts.py` puis `outils/zooms.py`.
- La loupe sur toutes les lettres et toutes les ligatures, dans les 3 graisses.
- La page à 1280 px et 390 px, clair et sombre.

## La publication

- Dossier `karkas/` : fonts, source, README, LICENCE (usage personnel gratuit, commercial sur autorisation), zip.
- Page en français sur le modèle des autres créations ; testeur « LAFLEURSTUDIO création graphique ».
- Mots d'exemple : le béton suisse (barrages et bâtiments brutalistes), à noter dans `MOTS.md`.
- Carte sur l'accueil, ligne dans le README.
- Commits au nom de Jonlekern. Pas de push avant « Pousse ».
