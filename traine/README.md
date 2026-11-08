# Traîne

Serif de lecture de LaFleurStudio, **dessinée à neuf**, lourde en bas. Une plume ovale grossit en descendant : têtes fines, pieds lourds, le bas des ronds plus gras que le haut. À la fin de chaque mot, la dernière lettre part en traîne.

## La traîne

- Chaque lettre a une version à traîne (`.q`). La fonction `calt` la met toute seule quand la lettre n'est pas suivie d'une lettre : espace, ponctuation, fin de ligne.
- Pas de traîne au milieu d'un mot, ni avant une apostrophe, un trait d'union ou une barre oblique (l’ami, Biel/Bienne).
- La traîne plonge sous la ligne et remonte en s'effilant. Le I la porte en haut, sinon on le lirait L.
- Pour la couper : `font-feature-settings: "calt" 0`.

## Les graisses

Des tissus, du plus léger au plus lourd.

| Poids | Nom | Fichier |
| --- | --- | --- |
| 200 | Voile | `Traine-Voile.otf` |
| 300 | Tulle | `Traine-Tulle.otf` |
| 400 | Satin | `Traine-Satin.otf` |
| 600 | Velours | `Traine-Velours.otf` |
| 800 | Brocart | `Traine-Brocart.otf` |

## Caractères

Tout le jeu GF Latin Core : majuscules, minuscules, chiffres, ponctuation, signes et accents d'Europe en alphabet latin.

## Fichiers

- `fonts/otf/` : les 5 graisses à installer
- `fonts/woff2/` : les 5 graisses pour le web
- `Traine.zip` : les 5 graisses (OTF) + la licence
- `LICENCE.txt` : la licence

## Licence

Usage personnel gratuit. Usage commercial sur autorisation écrite de LaFleurStudio : info@lafleurstudio.ch. Voir `LICENCE.txt`.

© 2026 LaFleurStudio · Jonathan Kern
