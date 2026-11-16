# KARKAS CLASSIC

La version manuscrite de [KARKAS](../karkas/), la vyaz en lettres latines de LaFleurStudio. Les lettres sont **redessinées d'après les titres des manuscrits russes**, écrits à la plume large. Les liaisons sont celles de KARKAS.

C'est la deuxième version du projet décrit dans [`../karkas/source/PLAN.md`](../karkas/source/PLAN.md) : Modern (`karkas/`), Classic (ici), Display (`karkas-display/`).

La vyaz latine n'a jamais existé : ce n'est pas la copie d'un modèle, c'est la transposition d'un geste. Direction choisie par Johnny : « le manuscrit ».

## La recette

- **Capitales seulement**, six à huit fois plus hautes que larges. Les minuscules donnent les mêmes capitales.
- **Le trait de plume.** Les fûts sont épais et s'évasent en coin en haut et en bas. Les barres et les obliques sont des traits fins, terminés par un petit coin.
- **Les formes anciennes.** Le A a un fût droit et une oblique fine, comme le А de la vyaz. Le O, le C, le D, le G et le Q sont en amande pointue. Le B, le P et le R portent de petites boucles pointues. Le Y est un fût avec une oblique fine, comme le У.
- **Les nœuds.** Un losange au milieu des longs fûts du I, du T, du L et du P.
- **Les liaisons** (feature `liga`, active par défaut) : fût partagé, lettre logée sur le pied du L et sous les bras du F, lettres sous la barre du T, lettres doubles empilées. **651 ligatures** par graisse : 336 pour le latin (dont 46 avec une lettre accentuée) et 315 pour le russe.
- **ss01** : les lettres doubles qui ont deux fûts en partagent un (HH, MM, NN, UU).
- **Chiffres tabulaires**, avec les mêmes pleins et déliés. Le 0 a les coins coupés.
- **Crénage** automatique par profils. Les chiffres ne se crénent jamais.
- **Le cyrillique** : А–Я et Ё dans le même dessin, avec leurs liaisons. Le Й garde sa brève et ne se lie pas.

## Ce qui diffère de KARKAS

- Le C et le P sont en courbes : ils ne logent pas de lettre. Le A n'a qu'un fût, à droite ; le O et le D n'en donnent pas. Il y a donc moins de liaisons (651 contre 948).
- Pas de losanges dans les creux (`ss02`) : les fûts portent déjà des nœuds.
- Les chiffres, la ponctuation et les signes reprennent le dessin de KARKAS avec les pleins et déliés de la Classic ; leurs fûts n'ont pas les bouts en coin.
- C'est une police de titre : les traits fins disparaissent en petit.

## Les graisses

Les trois écritures des scribes russes.

| Poids | Nom | Fût | Trait fin | Fichier |
| --- | --- | --- | --- | --- |
| 300 | Skoropis (la cursive) | 22 | 8 | `KARKASClassic-Skoropis.otf` |
| 500 | Poluustav (la demi-onciale) | 38 | 11 | `KARKASClassic-Poluustav.otf` |
| 800 | Ustav (l'onciale) | 54 | 15 | `KARKASClassic-Ustav.otf` |

## La fabrique

```
python3 source/build_all.py
```

- `cla_letters.py` : les lettres du manuscrit, latines et russes.
- `cla_fab.py` : donne ces lettres à la fabrique de KARKAS (`../karkas/source/kar_fab.py`) avec les réglages de la Classic.
- `build_all.py` : les 3 OTF, les 3 WOFF2 et le zip.
- `essai.py` : l'image d'essai, sans fabriquer la police.

Il faut Python 3 avec fontTools et skia-pathops.

## Les contrôles

- fontbakery `check-universal` : 0 erreur, 0 avertissement sur les 3 fichiers.

## Licence

Usage personnel gratuit. Usage commercial sur autorisation écrite de LaFleurStudio : info@lafleurstudio.ch. Voir [`LICENCE.txt`](LICENCE.txt).
