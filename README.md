# LaFleurStudio — Fonts

Les polices de **LaFleurStudio**, libres et gratuites.

Site : **https://jonlekern.github.io/Fonts/**

## Polices

| Police | Style | Graisses | Licence | Liens |
| --- | --- | --- | --- | --- |
| **Calebard** | Sans-serif super étendue | 11 (Hairline → Extreme Black) + Goofy, Extra Goofy | SIL OFL 1.1 | [Page](https://jonlekern.github.io/Fonts/calebard/) · [Zip](calebard/Calebard.zip) · [Dossier](calebard/) |

## Organisation

```
index.html              Catalogue des polices (page d'accueil du site)
shared/
  site.css              Styles communs à toutes les pages
  specimen.js           Spécimen commun : graisses, testeur, caractères
calebard/               Un dossier par police
  index.html            Page de la police
  README.md             Graisses, fichiers, licence
  OFL.txt               Licence de la police
  Calebard.zip          Toutes les polices en TTF + licence
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
