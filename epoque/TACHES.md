# Époque — où on en est

## VALIDÉ PAR JOHNNY : le contraste Art déco (« Voilà ! »)
- Fût de droite très gras, fût de gauche et barres en filet : `mesures.py` (barre = fût × 0,20, écart = 0,74, coude = 30).
- La base, ce sont `capitales.py` et `minuscules.py` (pas `blocs.py`, essai abandonné).
- Ensuite : des signatures, une différente par lettre, discrètes (gestes d'emblèmes chromés des années 50).
  Posées pour l'instant : A (aile à gauche), E (flèche), Q (queue qui file), R (jambe détachée), T (barre en pointe à gauche),
  K k (bras détachés), f (aile), t (flèche), g (queue qui file à gauche). Les autres lettres restent à signer.
- À régler : espacement (trop serré), fûts seuls (I l i), m, et tout passer à la loupe.

## LA RÈGLE (Johnny) : « mes réf signent, tes réf constituent, chaque lettre a un truc unique »
- La structure vient des années 30 : blocs carénés, noirs, vides en fente (`source/blocs.py`, essai sur EPOQUE SKYLARK).
- La signature vient des emblèmes chromés des années 50 (logodesignlove.com/vintage-vehicle-logotypes) : aile, pointe
  effilée, bras détaché, queue qui file. **Une signature différente par lettre**, jamais un motif répété.
- Le moteur sait effiler un trait : `Tuyau(..., k=[1, 0])` (épaisseur à chaque point, 0 = en pointe).
- Essai : `BLOCS=1 M='{"fut":150,"rapport":0.58,"coude":18,"ecart":0.14,"app":46,"appr":46,"tension":1.25}' python3 source/planche.py …`
- Les fichiers `minuscules.py` et `capitales.py` sont le premier jet (tuyaux années 70) : à remplacer.

## CHANGEMENT DE CAP (Johnny : « tu es passé à côté, tu n'as pas analysé son essence »)
Le premier jet (tuyaux aux grandes rondes, chasses moyennes) fait police techno des années 70. En regardant les vraies
images du lettrage profilé, l'essence est ailleurs :
- des lettres en **blocs carénés** : coins doux à petit rayon, côtés et dessus droits (un rectangle adouci, pas un stade) ;
- **le noir domine** : fûts lourds, barres fines, vides réduits à des fentes ;
- une **grande amplitude de largeur** : du très étroit, haut et élégant, au très large et massif ;
- des **arches** à la place des pointes (A, M, N en arches), une hauteur d'x très haute, un air de capitales partout.
Vu sur les pièces de 1930 (couverture de Marinetti en Motor, réclames en Kabel noir) : des capitales géométriques
très noires, et **chaque lettre signée légèrement** par un petit éclat (quelques traits blancs courts, un reflet de chrome).
Notre version, à valider par Johnny : **la griffe** — trois petites entailles horizontales dans le flanc gauche de chaque
lettre, à la taille ; quand la Vitesse monte, elles sortent et deviennent le sillage. Maquette : `GRIFFE=1 python3 source/planche.py …`
(les entailles y sont peintes sur l'image, pas encore dans le moteur).
À faire : redessiner les lettres sur cette base, avec le même moteur (il sait déjà le faire : petits rayons, traits
lourds, axes resserrés). Ajouter un curseur Largeur. Garder la gauche légère/droite lourde, le Chrome et le sillage
seulement s'ils servent cette essence. Premier pas : une image d'essai propre, étroit / normal / large.

## Fait (session 1)
- Recherche, cahier des charges, plan.
- Moteur à tuyaux (`source/tuyaux.py`) : mêmes points à toute graisse, tout chrome, toute pente.
- Mesures (`source/mesures.py`), outils (`source/dessin.py`).
- Minuscules a–z + ı ȷ ß æ œ ø ð þ ł đ ħ (`source/minuscules.py`), premier jet réglé en gras.
- Capitales A–Z (`source/capitales.py`), premier jet réglé en gras.

## Demandé par Johnny (fait)
- La gauche plus légère que la droite, en Chrome (filets à gauche, bande pleine à droite) et dans la lettre pleine (fût gauche fin, fût droit gras). `dessin.lettre()` doit être appelée sur chaque lettre.

- La sauce : le sillage (`D.sillage`), lié au curseur Vitesse. `mesures(p, vitesse=…)` ; la chasse prend `m['air']`.

## À reprendre dans le dessin
- Chrome sur les fûts fins de gauche : filets très fins en 600–900, à régler.
- ð (le trait du haut), ß (le creux du milieu), æ œ en gras (œil du e), e en gras (œil petit).
- B : les deux panses en gras ; Q : la queue ; R : départ de la jambe ; M en gras (noir au milieu).
- f, t : les barres en Chrome (deux moignons) ; k, K : jonction bras/jambe.
- Capitales en plus : Æ Œ Ø Ð Þ Ł Đ Ħ ẞ.
- Vérifier chaque lettre à la loupe aux 3 graisses dessinées (300, 500, 900), Chrome 0 et 100.

## À faire (sessions 2 et 3) : voir PLAN.md, étapes 7 à 18
- Chiffres, ponctuation, signes, accents, variantes (ss01, ss02, ss03).
- Espacement, crénage.
- Fabrique : 12 masters, variable 3 axes, fixes, contrôles.
- Loupe, page, publication, push (seulement quand tout est fini).

## Outil d'essai
`python3 source/planche.py sortie.png "texte|texte" 500,0,0 900,1,1` (graisse, chrome 0–1, vitesse 0–1 ; `ECH=0.2` pour réduire).
