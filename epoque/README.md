# Époque

Lettrage de course de LaFleurStudio, **dessiné à neuf**. Le corps vient des années 30, la signature des années 50.

## La recette

- **La droite grasse, la gauche en filet** : c'est le contraste Art déco des affiches de Grand Prix. Dans chaque lettre, le trait de droite porte le poids ; le trait de gauche et toutes les barres sont des filets.
- **Une signature par lettre** : comme sur un emblème chromé de carrosserie, chaque lettre a un petit geste à elle, jamais deux fois le même. A : une aile à gauche. Q : la queue file à l'horizontale. R : la jambe se détache. T : la barre finit en pointe. g : la queue part loin à gauche. i : le point est un trait de vitesse.
- **Deux curseurs** : Graisse (`wght`, 300 à 900) et Vitesse (`VITE`, 0 à 100). À Vitesse 100, la lettre penche de 14° vers l'avant : c'est le style Course.

## Les graisses

Sept arrêts, sept endroits du circuit du Bremgarten, à Berne, où se courait le Grand Prix de Suisse (1934–1939).

| Poids | Nom | Fichiers |
| --- | --- | --- |
| 300 | Forsthaus | `Epoque-Forsthaus.otf`, `Epoque-ForsthausItalic.otf` |
| 400 | Bethlehem | `Epoque-Bethlehem.otf`, `Epoque-BethlehemItalic.otf` |
| 500 | Eichholz | `Epoque-Eichholz.otf`, `Epoque-EichholzItalic.otf` |
| 600 | Eymatt | `Epoque-Eymatt.otf`, `Epoque-EymattItalic.otf` |
| 700 | Wohlenrampe | `Epoque-Wohlenrampe.otf`, `Epoque-WohlenrampeItalic.otf` |
| 800 | Jordenrampe | `Epoque-Jordenrampe.otf`, `Epoque-JordenrampeItalic.otf` |
| 900 | Glasbrunnen | `Epoque-Glasbrunnen.otf`, `Epoque-GlasbrunnenItalic.otf` |

Les fichiers `…Italic` sont les styles Course. La variable : `fonts/variable/Epoque[VITE,wght].ttf`.

## Les caractères

319 glyphes : capitales, minuscules, chiffres de chasse fixe, ponctuation, signes, monnaies, 145 lettres accentuées (langues d'Europe en alphabet latin). Crénage par familles.

## La fabriquer

```
python3 source/build_all.py            # tout : 14 fixes + la variable
python3 -m pytest source/tests -q      # les contrôles
```

Chaque lettre est une liste de tuyaux (`source/tuyaux.py`) : un tracé avec une épaisseur. Rien n'est découpé après coup, toutes les versions d'une lettre ont les mêmes points. Le détail est dans `CAHIER-DES-CHARGES.md`.

## Licence

Usage personnel gratuit, usage commercial sur autorisation : [LICENCE.txt](LICENCE.txt). Contact : info@lafleurstudio.ch.
