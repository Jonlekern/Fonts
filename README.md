# LaFleurStudio — Fonts

Les polices de **LaFleurStudio**, libres et gratuites.

Site : **https://jonlekern.github.io/Fonts/**

## Polices

| Police | Style | Graisses | Licence | Liens |
| --- | --- | --- | --- | --- |
| **Calebard** | Sans-serif super étendue | 11 (Hairline → Extreme Black) + Goofy, Extra Goofy | SIL OFL 1.1 | [Page](https://jonlekern.github.io/Fonts/calebard/) · [Zip](calebard/Calebard.zip) · [Dossier](calebard/) |
| **Falsard** | Display géométrique d'inspiration techno, au centre de gravité bas | 10 (XXXS → XXXXL) | SIL OFL 1.1 | [Page](https://jonlekern.github.io/Fonts/falsard/) · [Zip](falsard/Falsard.zip) · [Dossier](falsard/) |
| **Clebard** | Néo-grotesque suisse en extra-large | 6 (Demi → Trenta) | GUST Font License | [Page](https://jonlekern.github.io/Fonts/clebard/) · [Zip](clebard/Clebard.zip) · [Dossier](clebard/) |
| **Malabard** | Display de course allongée | 7 (ExtraLight → ExtraBold) + 7 italiques | SIL OFL 1.1 | [Page](https://jonlekern.github.io/Fonts/malabard/) · [Zip](malabard/Malabard.zip) · [Dossier](malabard/) |
| **Brécard** | Display en pointes et en losanges, poids en haut | 9 (wa'vatlh → Hutvatlh, en klingon) + 9 italiques | SIL OFL 1.1 | [Page](https://jonlekern.github.io/Fonts/brecard/) · [Zip](brecard/Brecard.zip) · [Dossier](brecard/) |

## Organisation

```
index.html              Catalogue des polices (page d'accueil du site)
shared/
  site.css              Styles communs à toutes les pages
  specimen.js           Spécimen commun : graisses, testeur, caractères
calebard/, falsard/,    Un dossier par police
clebard/, malabard/,
brecard/
  index.html            Page de la police
  README.md             Graisses, fichiers, licence
  OFL.txt               Licence de la police (Clebard : LICENCE.txt + GUST)
  Calebard.zip          Toutes les graisses en TTF + licence
  fonts/ttf/            Polices à installer
  fonts/woff2/          Polices pour le web
  images/               Images de la page
  source/               Scripts de fabrication
```

## Ajouter une police

1. Créer un dossier en minuscules à la racine (ex. `nouvelle-police/`) avec la même organisation que `calebard/`.
2. Copier `calebard/index.html` comme modèle : adapter les `@font-face`, l'objet `window.SPECIMEN` (nom, graisses, texte d'exemple) et les textes.
3. Ajouter une carte dans `index.html` (racine) et une ligne dans le tableau ci-dessus.
4. Mettre la licence de la police dans son dossier.

Chaque police garde sa propre licence. Les pages utilisent les fichiers WOFF2 de leur dossier.
