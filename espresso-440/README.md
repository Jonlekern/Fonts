# Espresso 4.40.-

Un projet artistique : le portrait de Bienne par son écriture. Une écriture à la main tirée des ardoises des cafés et des boulangeries biennois : les menus et les prix écrits au feutre craie, relevés lettre par lettre. **5 graisses**, du **Lungo** au **Moka**, par **LaFleurStudio**. Version 1.101.

Page : **https://jonlekern.github.io/Fonts/espresso-440/**

## Graisses

| Style | Poids | Trait | Fichier |
| --- | --- | --- | --- |
| Lungo | 300 | 64 | `Espresso440-Lungo` |
| Espresso | 400 | 100 | `Espresso440-Espresso` |
| Ristretto | 500 | 122 | `Espresso440-Ristretto` |
| Doppio | 600 | 144 | `Espresso440-Doppio` |
| Moka | 700 | 168 | `Espresso440-Moka` |

Épaisseur du trait en unités (1000 par em). Hauteur des majuscules : 720, des minuscules : 480, dans toutes les graisses.

## Détails

- Chaque lettre est relevée sur une vraie ardoise de café ou de boulangerie à Bienne, puis redessinée d'un trait rond et régulier.
- Tous les i accentués (î, ï, í, ì…) portent un petit cœur à la place de l'accent.
- Deux e : rond et ouvert au milieu d'un mot, à longue sortie en fin de mot (fonction `calt`, accents compris).
- Le f descend sous la ligne et se glisse sous la lettre d'avant ; ff s'écrit d'un seul geste (fonction `liga`).
- U+2600 (le soleil) dessine un soleil qui sourit.
- Jeu de caractères GF Latin Core complet (319 caractères), accents combinants compris.
- Crénage calculé sur la forme de chaque lettre, pour chaque graisse.

## Fichiers

| Chemin | Contenu |
| --- | --- |
| `Espresso440.zip` | Les 5 graisses en TTF + licence |
| `fonts/ttf/` | Polices à installer (Mac, Windows, logiciels) |
| `fonts/woff2/` | Polices pour le web |

## Sur le web

```css
@font-face { font-family: "Espresso 4.40.-"; font-weight: 400; src: url(Espresso440-Espresso.woff2) format("woff2"); }
/* … une règle par graisse : Lungo 300, Espresso 400, Ristretto 500, Doppio 600, Moka 700 */
```

## Licence

Espresso 4.40.- est distribuée sous **SIL Open Font License 1.1** (voir [`OFL.txt`](OFL.txt)).
Libre et gratuite, y compris pour un usage commercial. La police ne peut pas être vendue seule, et la licence doit l'accompagner.

## Merci

Merci aux mains anonymes des cafés et des boulangeries biennoises.
