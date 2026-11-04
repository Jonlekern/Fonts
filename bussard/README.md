# Bussard

Une police à points lumineux, inspirée des transports et des affichages LED. Chaque lettre est dessinée point par point sur une grille. **6 graisses**, de **Thin** à **Black**, chacune avec son **italique glitch** penchée à 12°, par **LaFleurStudio**.

Page : **https://jonlekern.github.io/Fonts/bussard/**

## Graisses

| Style | Poids | Trait | Point | Fichiers |
| --- | --- | --- | --- | --- |
| Thin | 100 | 1 point | petits points (rayon 13) | `Bussard-Thin`, `Bussard-ThinItalic` |
| Light | 300 | 1 point | rayon 20 | `Bussard-Light`, `Bussard-LightItalic` |
| Regular | 400 | 2 points | rayon 20 | `Bussard-Regular`, `Bussard-Italic` |
| Medium | 500 | 2 points | gros points (rayon 23) | `Bussard-Medium`, `Bussard-MediumItalic` |
| Bold | 700 | 3 points | rayon 20 | `Bussard-Bold`, `Bussard-BoldItalic` |
| Black | 900 | 3 points | gros points (rayon 23,5) | `Bussard-Black`, `Bussard-BlackItalic` |

Les italiques penchent à 12° et glitchent : la moitié basse des lettres décroche d'un point vers le bas et d'un point vers la gauche.

Grille : 14 points de haut pour les majuscules, 10 pour les minuscules, un point tous les 50 unités, dans toutes les graisses.

## Détails

- Jeu de caractères GF Latin Core complet (319 caractères), accents combinants compris.
- `🚌` (U+1F68C) dessine le petit bus des tableaux.
- Tous les chiffres ont la même largeur : les horaires restent alignés.
- Crénage en points entiers (50 unités), pour que les points restent sur la grille. Les chiffres ne sont pas crénés.
- Article Google Fonts : [`article/ARTICLE.en_us.html`](article/ARTICLE.en_us.html).
- Jeu de caractères et placement des accents contrôlés avec Fontbakery (profil Google Fonts).

## Fichiers

| Chemin | Contenu |
| --- | --- |
| `Bussard.zip` | Les 12 styles en TTF + licence |
| `fonts/ttf/` | Polices à installer (Mac, Windows, logiciels) |
| `fonts/woff2/` | Polices pour le web |

## Sur le web

```css
@font-face { font-family: "Bussard"; font-weight: 400; font-style: normal; src: url(Bussard-Regular.woff2) format("woff2"); }
@font-face { font-family: "Bussard"; font-weight: 400; font-style: italic; src: url(Bussard-Italic.woff2) format("woff2"); }
/* … une règle par style : Thin 100, Light 300, Regular 400, Medium 500, Bold 700, Black 900, et leurs italiques */
```

## Licence

Copyright 2026 **Jonathan Kern**, **LaFleurStudio**, avec le nom réservé **« Bussard »** (Reserved Font Name).

Bussard est distribuée sous **SIL Open Font License 1.1** (voir [`OFL.txt`](OFL.txt)).
Libre et gratuite, y compris pour un usage commercial. La police ne peut pas être vendue seule, et la licence doit l'accompagner.
Une version modifiée par quelqu'un d'autre ne peut pas s'appeler « Bussard ».
