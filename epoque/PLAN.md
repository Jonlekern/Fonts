# Époque — plan d'action

Trois sessions. À la fin de chaque session : tout est commité, `TACHES.md` dit où on en est.

## Session 1 — le moteur et les lettres

1. **Recherche** (fait) : lettrage d'époque, thème suisse, règles de métier. Résumé dans `CAHIER-DES-CHARGES.md`.
2. **Le moteur à tuyaux** (`source/tuyaux.py`)
   - un tuyau = points de passage + rayon de virage à chaque point + épaisseurs (verticale, horizontale) + coupes des deux bouts ;
   - sortie : pour chaque bande (pleine, filet 1, filet 2) un contour fermé, toujours avec le même nombre de points ;
   - paramètres : graisse, chrome (0–1), pente ; coupes de bout : d'équerre, horizontale, verticale, sur une droite donnée (chevrons) ;
   - anneaux fermés (O, o) : deux contours par bande.
   - Tests : mêmes points à toutes les positions ; épaisseur mesurée = épaisseur demandée ; pas de contour retourné.
3. **Les mesures** (`source/mesures.py`) : hauteurs, épaisseurs par graisse, rayons, taille basse/haute.
4. **Image d'essai n° 1** : `EPOQUE Bremgarten 1934` en 3 graisses × Chrome 0/100 × Vitesse 0/100. On règle : proportions, rayons, répartition des filets. Deux répartitions comparées, on garde la plus belle.
5. **Minuscules** a–z + lettres en plus → planche, loupe, corrections.
6. **Capitales** A–Z + lettres en plus → planche, loupe, corrections.

## Session 2 — le jeu complet et la fabrique

7. **Chiffres** (course : 1 à drapeau, 0 en stade), exposants, fractions.
8. **Ponctuation, signes, monnaies, mathématiques.**
9. **Accents** et lettres accentuées (GF Latin Core), en pièces à tuyaux.
10. **Variantes** : ss01 taille haute, ss02 rondes, ss03 7 barré / 0 pointé ; numéros de course ronds si le temps le permet.
11. **Espacement** (méthode H/O puis n/o) et **crénage** par familles, calculé sur les contours pleins, pour 3 graisses.
12. **La fabrique** (`source/fabrique.py`, `build_all.py`)
    - masters : 3 graisses × 2 vitesses × 2 chromes = 12, tous compatibles ;
    - variable : fontTools varLib, glyf + gvar + HVAR, drapeau de recouvrement, STAT, avar si besoin, MVAR pour la pente du curseur ;
    - fixes : contours fusionnés (pathops), OTF, noms, STAT.
13. **Contrôles** : fontbakery 0/0, `interpolatable`, détecteur, tests.

## Session 3 — la finition et la mise en ligne

14. **Loupe complète** : chaque lettre, graisses extrêmes, Chrome 0/100, Vitesse 0/100, plus les positions intermédiaires. Corrections, puis loupe à nouveau.
15. **Vrai texte** : mots du thème, phrases, capitales espacées ; réglage fin du crénage.
16. **Page** `index.html` : héros animé (le chrome s'ouvre, la lettre penche), les 7 graisses, testeur à 3 curseurs, caractères, « Comment on l'a faite » (les tuyaux, les filets, les chevrons), téléchargement.
17. **Publication** : carte d'accueil + `outils/accueil.py`, README racine, `MOTS.md`, README de la police, `LICENCE.txt` avec certificat, zip.
18. **Dernier contrôle** complet, fusion de `main`, commit, **push** (`page-fusard:main` puis `page-fusard`).

## Règles de travail

- Une image d'essai avant chaque gros morceau ; la loupe après chaque correction.
- Tout se refait avec `python3 source/build_all.py`.
- Si le temps manque, on coupe dans cet ordre : numéros ronds, ss02, styles fixes Chrome (la variable les contient), jamais dans les contrôles.
