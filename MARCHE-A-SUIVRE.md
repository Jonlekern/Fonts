# Marche à suivre

Comment on fait une police LaFleurStudio, de l'idée à la mise en ligne. Chaque étape se montre à Johnny avant de passer à la suivante.

## 1. L'idée

- On choisit ensemble la famille (sans, serif, display, écrite à la main, machine à écrire, expérimental), le caractère et ce qui la rend unique : la « sauce Lafleur ».
- Le nom : **les noms en -ard sont réservés aux polices modifiées**. Une création ne finit pas en -ard.
- Les noms des graisses racontent quelque chose (le vent pour Overshoot, les heures de la nuit pour Small Hours…).
- Pas de photo ni de scan d'ardoise.

## 2. L'image d'essai

**Avant toute police complète : une image d'essai.** Quelques lettres dans les graisses prévues, pour valider la forme. On ne dessine rien de plus tant qu'elle n'est pas validée.

## 3. Le dessin, dans l'ordre

1. Les minuscules a–z (avec ı ȷ ß æ œ ø ð þ ł…), puis image d'essai.
2. Les capitales A–Z (avec Æ Œ Ø Ð Þ Ł ẞ…), puis image d'essai.
3. **Stop aux chiffres : on montre tout à Johnny et on attend.**
4. Les chiffres, la ponctuation, les signes, les accents et les lettres en plus (tout le jeu GF Latin Core).
5. Les variantes et les fonctionnalités (italique, ss01…, ligatures).

À chaque étape : **image d'essai + loupe sur chaque lettre** (voir plus bas).

## 4. La fabrique

- Les scripts de fabrication vont dans `source/` de la police : on doit pouvoir tout refaire avec une seule commande.
- On sort les OTF (ou TTF) et les WOFF2, toutes les graisses, l'italique, l'espacement, le crénage, les fonctionnalités OpenType, les noms et la table STAT.
- Les contours sont fusionnés : pas de recouvrement, pas de contour en trop.

## 5. Les contrôles

Tous, sur chaque fichier, avant de montrer et avant de publier :

1. **fontbakery** `check-universal` : 0 erreur, 0 avertissement.
2. **Le détecteur** : `python3 outils/defauts.py police.otf 5 defauts.json` cherche les échardes (encre trop fine), les fentes (blanc trop étroit qui entre dans l'encre) et les marches (petit zigzag dans un contour). Puis `python3 outils/zooms.py police.otf defauts.json planche` fait un gros plan de chaque endroit touché.
3. **La loupe sur chaque lettre** : `python3 outils/loupe.py police.otf dossier`. Voir la section suivante : c'est la plus importante.
4. **Le vrai texte** : la police sur sa page, sur ordi et sur téléphone (390 px), en mode clair et sombre.

## 6. La loupe sur chaque lettre : indispensable

**Aucune police ne part sans être passée à la loupe, lettre par lettre, graisse par graisse.** Pas un échantillon : toutes les lettres.

### Pourquoi

- En taille texte, on ne voit rien. Mais une police, on la zoome : sur une affiche, un écran agrandi, une découpe vinyle, une gravure, un grand format. Là, chaque défaut saute aux yeux. Et Johnny zoome sur chaque lettre : si on ne l'a pas fait avant, c'est lui qui le trouve.
- Le détecteur ne trouve que ce qui se mesure. Il rate une courbe cassée, une bosse, une jonction molle, un trait qui dépasse proprement, un accent mal posé ou qui touche la lettre. Seul l'œil voit ça.
- Une correction peut casser une autre lettre : un changement dans la fabrique touche souvent toutes les lettres qui partagent une pièce (un fût, une boule, un accent). Donc après chaque correction, on repasse la loupe.
- Les lettres composées (accents, ligatures, variantes, italique) sont fabriquées automatiquement : c'est là que les défauts se cachent le plus.

### Ce qu'on cherche

- **Les traits qui dépassent** : un bout de trait qui sort d'une jonction, d'un empattement, d'un angle.
- **Les pointes** : un angle qui part en pique alors qu'il devrait être net ou arrondi.
- **Les crans** : une petite marche ou un zigzag dans un contour, souvent aux jonctions (a, g, q, B, Q…).
- **Les fils blancs** : un trait blanc très fin entre deux morceaux qui devraient se toucher.
- **Les échardes et les recouvrements** : un éclat d'encre, ou deux contours l'un sur l'autre (la loupe les montre en blanc).
- **Les courbes** : bosses, plats, cassures.
- **Les accents** : bien placés, la même hauteur partout, rien qui touche.
- **L'espacement** : la lettre bien posée dans sa chasse (les traits gris de la case).

### Comment

1. `python3 outils/loupe.py police.otf dossier` : toutes les lettres en grand, 6 par planche. Pour quelques lettres seulement : `python3 outils/loupe.py police.otf dossier a g Q é ß`.
2. On regarde **chaque case** : les bords, les jonctions, les bouts, les blancs intérieurs, les accents.
3. On le fait pour **chaque graisse et chaque style**, surtout la plus fine et la plus grasse.
4. Sur chaque défaut, on zoome encore avec `outils/zooms.py`, on corrige dans `source/`, on refabrique, et **on repasse la loupe sur toute la police**.
5. On ne montre une police que quand la loupe ne trouve plus rien.

## Les polices russes

Pour une police faite pour écrire le russe (comme ШКВАЛ) :

- **Les lettres** : le russe complet (А–Я, а–я, Ё ё), le latin de base (A–Z, a–z), les chiffres, la ponctuation et les signes. **Pas d'accents latins** : on écrit du russe, pas du suédois.
- **La page est entièrement en russe** : menus, titres, textes, testeur, téléchargement, pied de page. Les noms des graisses restent en lettres latines (ils s'affichent comme ça dans les menus des logiciels).
- **Le testeur** démarre sur **« LAFLEURSTUDIO графический дизайн »** (au lieu de « LAFLEURSTUDIO création graphique »).
- **Les mots d'exemple** sont des lieux russes, pas un canton suisse (voir `MOTS.md`).
- **La carte de l'accueil** : sous-titre technique en français, écrit seulement avec des lettres que la police a (sans accents), puisqu'il s'affiche dans la police.
- **Le filtre de l'accueil** : une police russe est **seulement** dans le filtre « Кириллица » (`data-fam="cyrillique"`), dans aucune autre famille. On met à jour le compteur de « Кириллица » (et de « Tout »).

## 7. La publication

- Le dossier de la police (en minuscules) : `fonts/otf/` (ou `fonts/ttf/`), `fonts/woff2/`, `source/`, `README.md`, `LICENCE.txt` (avec « Lafleur Certificat »), le zip.
- La page `index.html` (spécimen commun `shared/specimen.js`) :
  - le testeur sans boutons, avec « LAFLEURSTUDIO création graphique » par défaut (« LAFLEURSTUDIO графический дизайн » pour une police russe) ;
  - les mots d'exemple pris dans **`MOTS.md`** : un canton suisse par police, Bienne pour les polices biennoises, le même mot dans chaque boîte qui compare des graisses, jamais un mot déjà pris ;
  - les sous-titres ne changent pas une fois validés.
- La carte sur l'accueil `index.html` : le nom, l'exemple, la famille pour le filtre (`data-fam`), à sa place dans l'ordre.
- Une ligne dans le tableau du `README.md`.
- Rien ne déborde : on mesure sur ordi (1280 px) et sur téléphone (390 px). Si un mot ne rentre pas, on baisse la taille, on ne coupe pas le mot.
- Pas d'emoji style Apple sur le site. Adresse publique : info@lafleurstudio.ch.

## 8. La mise en ligne

- Commits au nom de **Jonlekern**.
- **On pousse seulement quand Johnny dit « Pousse »** : d'abord `git push origin page-fusard:main`, puis `git push origin page-fusard`.
- **Ne jamais supprimer la branche `fusard-132`.**
