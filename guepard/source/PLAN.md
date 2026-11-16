# GUÉPARD — le projet

## L'intention

Johnny veut une **première police variable** pour LaFleurStudio. Elle est faite à partir d'une police libre retravaillée « à notre sauce », d'où un nom en -ard. Le style est **sport années 70**.

Après deux planches d'essai (30 polices « course », puis 32 polices « sport 70s »), Johnny a choisi **Danfo** (Afrotype, OFL, Google Fonts). C'est une capitale de lettrage peint des bus de Lagos, au gros bas noir.

## Les décisions de Johnny

- Le départ est **Danfo**. On **efface ses effets** : on garde la forme lisse (ELSH 0) et on retire l'axe ELSH.
- **Axe A, vitesse** : les lettres penchent vers l'avant et s'étirent, comme un numéro de course.
- **Axe C, bandes** : des bandes de course **seulement dans le bas** des lettres. **Quand on va loin, ça glitche.**
- Nom : **GUÉPARD** (fichiers : `Guepard`).

## Les buts

- Une police variable à 2 axes qui fonctionne dans les navigateurs, Illustrator, InDesign, Figma et macOS.
- Les deux axes se combinent librement.
- Le jeu de signes de Danfo est gardé (≈1160 glyphes), avec toutes ses features (case, frac, ss01–03…).
- Une page sur le site, avec deux curseurs.

## Les non-buts

- Pas d'axe de graisse.
- Pas de bas-de-casse nouvelle : Danfo n'a que des capitales, on garde ça.

## Les anti-buts (ce qui serait raté même si ça marche)

- Des bandes qui touchent le haut fin des lettres.
- Des contours qui se croisent ou qui sautent pendant l'interpolation : les lettres doivent bouger en douceur d'un bout à l'autre des axes.
- Une vitesse qui ressemble à un faux italique mou (des courbes tordues, des O en œuf penché).

## Les axes

| Axe | Tag | Plage | Défaut | Ce qui se passe |
| --- | --- | --- | --- | --- |
| Vitesse | `VITE` | 0–100 | 0 | 0 : droit. 100 : pente d'environ 12° et lettres étirées d'environ 15 % vers l'avant. Les chasses suivent. |
| Bandes | `BAND` | 0–100 | 0 | 0 : rien. 0→50 : 3 bandes horizontales s'ouvrent dans le bas noir. 50→100 : glitch, les tranches du bas glissent latéralement en alternance (gauche, droite…), de plus en plus loin. Le haut ne bouge pas. |

Les tags sont en capitales parce que ce sont des axes maison (pas des axes enregistrés comme `wght` ou `slnt`).

## Les approches envisagées

1. **Les masters géométriques** (retenue). Les lettres sont découpées en tranches horizontales, en contours séparés qui se superposent légèrement à BAND 0. Les bandes, c'est l'écart entre les tranches. Le glitch, c'est un décalage horizontal des tranches. La vitesse, c'est une transformation affine (pente + étirement) suivie de corrections. Tous les masters viennent du même découpage, ils sont donc compatibles point par point par construction.
2. **Les booléens par master** : chaque master serait calculé par soustraction de bandes. C'est rejeté : la topologie change d'un master à l'autre, et l'interpolation devient impossible.
3. **Dessiner à la main.** C'est rejeté : 1160 glyphes, ce serait trop long, et le découpage géométrique est plus régulier.

## Le comment, côté technique

- La source est `Danfo[ELSH].ttf` (Google Fonts), instanciée à ELSH 0. La police est en TrueType (glyf), 1000 UPM, capitales 716, et le bas noir va de 0 à ≈334.
- **Découpage** : la zone basse (≈0–320) est coupée en 4 tranches, ce qui laisse 3 joints. Le haut reste un contour à part. À BAND 0, chaque tranche déborde de quelques unités sur la voisine : pas de joint visible. Le drapeau OVERLAP_SIMPLE est mis pour macOS.
- **Masters BAND** : 0 (fermé), 50 (bandes ouvertes, ≈18 unités chacune), 100 (bandes ouvertes et tranches décalées en alternance, ≈±60 unités). C'est un master intermédiaire sur le même axe.
- **Masters VITE** : chaque master BAND est dupliqué à VITE 100 (pente + étirement). Cela fait 6 masters en tout. Les O, C, S et les autres courbes sont corrigés pour ne pas paraître tordus.
- Les chasses et le crénage (GPOS) sont adaptés pour VITE. Le crénage de Danfo est gardé et mis à l'échelle de l'étirement.
- Une table **STAT** et des **instances nommées** : Droite, Course, Bandes, Course Bandes, Glitch, Course Glitch.
- Les instances fixes sont exportées en OTF/TTF pour les logiciels sans variable.
- Les fichiers : `Guepard[VITE,BAND].ttf` + WOFF2, les fixes, le zip, `OFL.txt` (copyright Danfo Project Authors + LaFleurStudio), le README et la page `guepard/index.html` avec les curseurs, sur le modèle des autres pages (`shared/specimen.js`).
- La carte d'accueil est ajoutée, puis `outils/accueil.py` est relancé.
- Contrôles : fontbakery `check-universal`, et un rendu en grille (VITE × BAND) pour vérifier qu'aucune lettre ne casse.

## Ce qui reste au fabricant

- Les valeurs exactes de pente, d'étirement, d'épaisseur et de décalage des bandes : les régler à l'œil sur les rendus.
- La liste des glyphes à corriger à la main pour la vitesse.
- Les signes sans bas noir (ponctuation, petits signes) : les tranches ne touchent que ce qui se trouve dans la zone basse.
