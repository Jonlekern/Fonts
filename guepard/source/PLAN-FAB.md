# GUÉPARD — plan de fabrication

> Pour l'exécutant : suivre tâche par tâche (superpowers:executing-plans). Cases à cocher.

**But :** une police variable à 2 axes (VITE, BAND), tirée de Danfo à ELSH 0, avec ses fixes, sa page et sa carte.
**Architecture :** un découpage en tranches horizontales, fait une seule fois. Tous les masters en sont dérivés par des transformations, donc ils sont compatibles par construction. Assemblage avec fontTools `varLib.build` à partir de masters TTF et d'un designspace.
**Outils :** Python 3, fontTools (instancer, varLib, ttGlyphPen), skia-pathops (intersections), uharfbuzz (tests), Playwright (rendus).
**Spec :** `guepard/source/PLAN.md`

## Contraintes globales

- Nom : GUÉPARD, nom de famille `Guepard`, PostScript `Guepard-…`. Licence OFL : copyright Danfo Project Authors + 2026 LaFleurStudio. Pas de nom réservé.
- Axes : `VITE` 0–100 (défaut 0), `BAND` 0–100 (défaut 0).
- Bandes : uniquement dans la zone 0–320 ; le haut (> 334) ne bouge jamais.
- Commits : `git -c user.name=Jonlekern -c user.email=Jonlekern@users.noreply.github.com commit`. On ne pousse que sur « Pousse ».
- Les rendus pour Johnny sont des PNG dans le scratchpad, à envoyer avec SendUserFile.

## Points de vigilance

1. Les glyphes composites (accents) : il faut les décomposer avant le découpage. Sinon, l'accent n'est pas penché et les bandes manquent → test sur `É`.
2. Un glyphe sans rien dans la zone basse (`-`, `'`, `^`) : il doit sortir intact. Il ne doit pas y avoir de tranche vide qui casse la compatibilité → test.
3. Les combinaisons du coin (VITE 100 + BAND 100) : aucun contour ne doit s'inverser → test d'aire signée.
4. Le crénage sur VITE 100 : les paires ne doivent pas se percuter → contrôle visuel sur une grille de mots.
5. macOS et le chevauchement : le flag OVERLAP_SIMPLE doit être sur tous les glyphes découpés → test.

---

### Tâche 1 : la base Danfo lisse

**Fichiers :** créer `guepard/source/gp_base.py`, `guepard/source/test_guepard.py` ; télécharger `guepard/source/danfo/Danfo[ELSH].ttf` et `OFL.txt` (google/fonts, `ofl/danfo/`).

**Interfaces :** produit `charger_base() -> TTFont`. Il renvoie Danfo instanciée à ELSH 0, sans fvar, avec les composites décomposés.

- [ ] Test `test_base` : pas de table `fvar` ; aucun glyphe composite ; le nombre de glyphes est égal à celui de Danfo ; la cmap couvre A–Z, 0–9 et É.
- [ ] Implémenter avec `instantiateVariableFont(f, {'ELSH': 0})`, puis décomposer (`fontTools.ttLib.scaleUpem` n'est pas utile ; on passe par `DecomposingRecordingPen` → `TTGlyphPen`).
- [ ] `pytest` passe → commit.

### Tâche 2 : le découpage en tranches

**Fichiers :** créer `guepard/source/gp_tranches.py`.

**Interfaces :** produit `decouper(contours, coupes=(80,160,240), haut=320, recouvre=4) -> list[Tranche]`. `Tranche` = `(contours: list[list[(x,y,on)]], ymin, ymax, rang)` ; le rang 0–3 correspond aux tranches basses et le rang 4 au haut. Les contours sont dans le format du pen de pathops.

Algorithme : pour chaque bande `[y0−recouvre, y1+recouvre]`, intersection pathops du glyphe avec un grand rectangle. Le haut prend `[haut−recouvre, +∞]`. Une tranche vide est gardée vide (0 contour), puisqu'elle est vide dans tous les masters → compatible.

- [ ] Tests : `test_union_egale_glyphe` (pour A, E, O, S, la surface de l'union des tranches est égale à celle du glyphe, à 0,5 % près) ; `test_signe_sans_bas` (le `-` donne des tranches basses vides et un haut égal au glyphe) ; `test_haut_intact` (les points de E au-dessus de 334 sont identiques à ceux de la source).
- [ ] Implémenter, faire passer les tests, commit.

### Tâche 3 : les masters BAND

**Fichiers :** créer `guepard/source/gp_masters.py`.

**Interfaces :** consomme `decouper`. Produit `master_band(tranches, ouverture: float, decalage: float) -> list contours`. Chaque tranche basse de rang `r` est rétrécie de `ouverture/2` à ses bords internes (les joints entre tranches). Le bord du sol (y=0) et le bord du haut (y=320) ne bougent pas pour les tranches extrêmes. Les tranches sont ensuite décalées en x de `decalage * (+1, −1, +1, −1)[r]`. Le rétrécissement est fait en déplaçant les points de coupe : les mêmes points dans tous les masters, et pas de nouvelle intersection.

Valeurs : BAND 0 → `ouverture = −2·recouvre` (les tranches se chevauchent) et `decalage = 0` ; BAND 50 → `ouverture = 18`, `decalage = 0` ; BAND 100 → `ouverture = 18`, `decalage = 60`.

- [ ] Test `test_compatible` : pour 50 glyphes au hasard, les 3 masters ont le même nombre de contours et de points, et les mêmes drapeaux on/off.
- [ ] Test `test_overlap_flag` : chaque glyphe découpé a le bit OVERLAP_SIMPLE (0x40) sur son premier point.
- [ ] Implémenter, faire passer les tests, commit.

### Tâche 4 : les masters VITE

**Fichiers :** modifier `guepard/source/gp_masters.py`.

**Interfaces :** produit `vitesse(contours, pente=0.21, etire=1.15) -> contours` (x' = etire·x + pente·y, y' = y ; 0.21 ≈ tan 12°), ainsi que la chasse ×1.15. Le dictionnaire `CORRECTIONS: dict[str, callable]` sert aux retouches à la main par glyphe (les O, C, G, Q, S, 0, 3, 6, 8, 9). Les retouches déplacent des points existants, sans jamais en ajouter.

- [ ] Test `test_vite_compatible` : les 6 masters (BAND 0/50/100 × VITE 0/100) sont compatibles.
- [ ] Test `test_aire_signee` : à VITE 100 et BAND 100, aucun contour ne change de sens par rapport au master par défaut.
- [ ] Rendu d'un PNG de la grille VITE × BAND (0, 50, 100), avec le texte « GUÉPARD 1974 RALLYE ». Il est regardé et les CORRECTIONS sont ajustées jusqu'à ce que les courbes soient propres.
- [ ] Commit.

### Tâche 5 : l'assemblage de la variable

**Fichiers :** créer `guepard/source/gp_fab.py` et `guepard/source/build_all.py`.

**Interfaces :** `fabriquer(dossier_sortie) -> Path` du TTF variable. Les étapes :
- écrire 6 masters TTF (copies de la base, avec glyf, hmtx et GPOS mis à jour) ;
- écrire un designspace (BAND 50 comme master intermédiaire) ;
- lancer `varLib.build` ;
- écrire le STAT (`fontTools.otlLib.builder.buildStatTable`) avec les noms d'axe Vitesse et Bandes ;
- ajouter les instances nommées : Droite (0,0), Course (100,0), Bandes (0,50), Course Bandes (100,50), Glitch (0,100), Course Glitch (100,100) ;
- renommer la police (table name : famille Guepard, et la licence OFL avec l'URL).

Pour le crénage : dans le master VITE 100, chaque valeur GPOS de paire est multipliée par 1.15.

- [ ] Test `test_variable` : `fvar` a 2 axes avec les plages exactes ; 6 instances nommées ; à (100,100), le shaping uharfbuzz de « GUEPARD » est plus large que celui de (0,0), d'un facteur entre 1.10 et 1.20.
- [ ] fontbakery `check-universal` donne 0 FAIL.
- [ ] Commit.

### Tâche 6 : les fixes, le WOFF2 et le zip

**Fichiers :** modifier `build_all.py`.

`build_all.py` produit :
- `guepard/Guepard[VITE,BAND].ttf` et sa version `.woff2` ;
- les 6 instances fixes `guepard/fixes/Guepard-<Nom>.ttf`, tirées des instances nommées par `instantiateVariableFont` (overlaps retirés avec `removeOverlaps`) ;
- `guepard/Guepard.zip`, qui contient la variable, les fixes et `OFL.txt`.

- [ ] Test `test_fixes` : 6 fichiers sans `fvar`, chacun avec son style dans la table name.
- [ ] Commit.

### Tâche 7 : la page, le README et la carte d'accueil

**Fichiers :** créer `guepard/index.html` (sur le modèle de `karkas/index.html`, avec `shared/specimen.js`) et `guepard/README.md` (sur le modèle de `karkas-classic/README.md`) ; modifier `index.html` (la carte), le tableau de `README.md` et `shared/accueil/` (via `python3 outils/accueil.py`).

La page a deux curseurs, Vitesse et Bandes, qui pilotent `font-variation-settings` dans le testeur et les grands titres. Elle a aussi des boutons pour les 6 instances. Le texte est en français, et les exemples sont sport 70s.

- [ ] Rendu Playwright de la page (bureau + 390 px, clair + sombre), regardé : rien ne déborde.
- [ ] `outils/accueil.py` relancé, et la carte vérifiée.
- [ ] Commit. On attend « Pousse ».
