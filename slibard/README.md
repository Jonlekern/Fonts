# Slibard

Le frère sage d'[Époque](../epoque/), de LaFleurStudio. Le même moteur et le même fût, sans les signatures, et plus gras encore.

## La recette

- **Le même fût qu'Époque** : la droite de chaque lettre est grasse, la gauche et les barres sont des filets. Jusqu'à 900, c'est exactement le fût d'Époque.
- **Sage** : plus de pointes, de queues qui filent ni de bras détachés. Les barres sont droites, les ronds sont fermés, le point du i est rond.
- **Un seul geste** : la barre du milieu du F part fine du fût et s'élargit un peu vers la droite.
- **Plus gras** : Slibard monte jusqu'à 1000. Les lettres s'élargissent pour garder leurs blancs ouverts.
- **Deux curseurs** : Graisse (`wght`, 300 à 1000) et Vitesse (`VITE`, 0 à 100 ; à 100 la lettre penche de 14°, c'est le style Course).

## Les graisses

Huit arrêts, de plus en plus froids, jusqu'à La Brévine, la Sibérie de la Suisse.

| Poids | Nom | Fichiers |
| --- | --- | --- |
| 300 | Frais | `Slibard-Frais.otf`, `Slibard-FraisItalic.otf` |
| 400 | Froid | `Slibard-Froid.otf`, `Slibard-FroidItalic.otf` |
| 500 | Gel | `Slibard-Gel.otf`, `Slibard-GelItalic.otf` |
| 600 | Givre | `Slibard-Givre.otf`, `Slibard-GivreItalic.otf` |
| 700 | Glace | `Slibard-Glace.otf`, `Slibard-GlaceItalic.otf` |
| 800 | Bise | `Slibard-Bise.otf`, `Slibard-BiseItalic.otf` |
| 900 | Banquise | `Slibard-Banquise.otf`, `Slibard-BanquiseItalic.otf` |
| 1000 | Brevine | `Slibard-Brevine.otf`, `Slibard-BrevineItalic.otf` |

Les fichiers `…Italic` sont les styles Course. La variable : `fonts/variable/Slibard[VITE,wght].ttf`.

## Les caractères

319 glyphes : capitales, minuscules, chiffres de chasse fixe, ponctuation, signes, monnaies, 145 lettres accentuées (langues d'Europe en alphabet latin). Crénage par familles.

## La fabriquer

```
python3 source/build_all.py            # tout : 16 fixes + la variable
python3 -m pytest source/tests -q      # les contrôles
```

Le moteur est dans `source/` : chaque lettre est une liste de tuyaux (`source/tuyaux.py`), un tracé avec une épaisseur. Toutes les versions d'une lettre ont les mêmes points.

## Licence

Usage personnel gratuit, usage commercial sur autorisation : [LICENCE.txt](LICENCE.txt). Contact : info@lafleurstudio.ch.
