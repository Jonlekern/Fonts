# Époque — où on en est

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
