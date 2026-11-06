# Swift Rallye 01

Police de course de LaFleurStudio, dans l'esprit des rallyes des années 70 : large et basse, penchée vers l'avant, coins ronds, bouts coupés en biseau. Majuscules seulement (les minuscules tapées sortent en majuscules).

**Racine** : Swift Rallye 01 est née de l'étude des traits des majuscules de **Biel/Bienne WildStyle**. Les lettres du graffiti n'ont pas été déformées : leurs traits ont été mesurés, et un alphabet neuf a été dessiné avec les règles qui en sortent.

## La recette

- **8 angles seulement**, mesurés sur les 26 majuscules wildstyle : 0°, 31°, 57°, 72°, 87°, −52°, −66°, −80°.
- **Verticales à 72°** : la lettre penche vers l'avant (pente de 18°).
- **Rondes en octogone** aux coins coupés à 31° et à −52°, puis **arrondis** sur le contour.
- **Bouts en biseau**, coupés le long d'un des 8 angles (31° de préférence, le plus proche du biseau à 14° du marqueur).
- **Épaisseur du marqueur biseau** (14°) : verticales épaisses, horizontales plus fines.
- **La traînée** : le trait long de chaque lettre devient une barre qui file vers l'arrière et se glisse sous la lettre d'avant.
- **Allongée** : lettres basses et larges.

## Les graisses

| Poids | Nom | Fichier |
| --- | --- | --- |
| 100 | Reco | `SwiftRallye01-Reco.ttf` |
| 200 | Liaison | `SwiftRallye01-Liaison.ttf` |
| 300 | Pointage | `SwiftRallye01-Pointage.ttf` |
| 400 | Départ | `SwiftRallye01-Depart.ttf` |
| 500 | Spéciale | `SwiftRallye01-Speciale.ttf` |
| 600 | Chrono | `SwiftRallye01-Chrono.ttf` |
| 700 | Épingle | `SwiftRallye01-Epingle.ttf` |
| 800 | Dérapage | `SwiftRallye01-Derapage.ttf` |
| 900 | Saut | `SwiftRallye01-Saut.ttf` |
| 1000 | Turbo | `SwiftRallye01-Turbo.ttf` |
| 1100 | Groupe 4 | `SwiftRallye01-Groupe4.ttf` |
| 1200 | Groupe B | `SwiftRallye01-GroupeB.ttf` |

Un fichier de police ne connaît pas de graisse au-dessus de 1000 : Groupe 4 et Groupe B sont déclarées 1000 et se choisissent par leur nom.

**Triche des graisses extrêmes** : en Groupe 4 et Groupe B, les barres et les diagonales arrêtent de grossir, seules les verticales continuent. Dans les graisses grasses, les accents, les points et les petits signes restent plus fins que les lettres.

## Caractères

207 signes : 26 majuscules, 10 chiffres, ponctuation, signes (@ # $ % & € £ ¥ ¢ © ® ™ § ¶ ° …) et tout le jeu GF Latin Core en majuscules (langues d'Europe en alphabet latin). Crénage par familles : chaque lettre accentuée suit sa lettre de base.

## Fichiers

- `fonts/ttf/` : les 12 graisses à installer.
- `fonts/woff2/` : les 12 graisses pour le web.
- `SwiftRallye01.zip` : les 12 graisses en TTF + licence.
- `LICENCE.txt` : la licence.

## Licence

Usage personnel gratuit ; usage commercial sur autorisation écrite de LaFleurStudio, gratuite ou payante selon le projet. Contact : info@lafleurstudio.ch. Voir `LICENCE.txt`.
