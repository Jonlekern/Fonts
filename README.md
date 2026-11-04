# LaFleurStudio — Fonts

Les polices de **LaFleurStudio**. Presque toutes libres et gratuites : chaque police a sa licence dans son dossier.

Site : **https://jonlekern.github.io/Fonts/**

## Polices

| Police | Style | Graisses | Licence | Liens |
| --- | --- | --- | --- | --- |
| **Calebard** | Sans-serif super étendue | 11 (Hairline → Extreme Black) + Goofy, Extra Goofy | SIL OFL 1.1 | [Page](https://jonlekern.github.io/Fonts/calebard/) · [Zip](calebard/Calebard.zip) · [Dossier](calebard/) |
| **Falsard** | Display géométrique d'inspiration techno, au centre de gravité bas | 10 (XXXS → XXXXL) | SIL OFL 1.1 | [Page](https://jonlekern.github.io/Fonts/falsard/) · [Zip](falsard/Falsard.zip) · [Dossier](falsard/) |
| **Clebard** | Néo-grotesque suisse en extra-large | 6 (Demi → Trenta) | GUST Font License | [Page](https://jonlekern.github.io/Fonts/clebard/) · [Zip](clebard/Clebard.zip) · [Dossier](clebard/) |
| **Malabard** | Display de course allongée | 7 (ExtraLight → ExtraBold) + 7 italiques | SIL OFL 1.1 | [Page](https://jonlekern.github.io/Fonts/malabard/) · [Zip](malabard/Malabard.zip) · [Dossier](malabard/) |
| **Brécard** | Display en pointes et en losanges, poids en haut | 9 (wa'vatlh → Hutvatlh, en klingon) + 9 italiques | Usage personnel gratuit, commercial sur autorisation | [Page](https://jonlekern.github.io/Fonts/brecard/) · [Zip](brecard/Brecard.zip) · [Dossier](brecard/) |
| **Fûsard-032** | Techno gothique : géométrie stricte, croisements partout, bouts en pointe | 9 (Hairline → Black) | Usage personnel gratuit, commercial sur autorisation | [Page](https://jonlekern.github.io/Fonts/fusard-032/) · [Zip](fusard-032/Fusard032.zip) · [Dossier](fusard-032/) |
| **Jalousia** | Chiffres romains néo-gothiques dessinés à la main, en deux polices : Net (trait net) et Craie | 4 (Centum → Quadringenti, en latin) + 4 italiques, pour chacune | Usage personnel gratuit, commercial sur autorisation | [Page](https://jonlekern.github.io/Fonts/jalousia/) · [Zip Net](jalousia/JalousiaNet.zip) · [Zip Craie](jalousia/JalousiaCraie.zip) · [Dossier](jalousia/) |
| **Espresso 4.4.-** | Projet artistique : écriture à la main tirée des ardoises des cafés et des boulangeries biennois | 5 (Lungo → Moka) | SIL OFL 1.1 | [Page](https://jonlekern.github.io/Fonts/espresso-44/) · [Zip](espresso-44/Espresso44.zip) · [Dossier](espresso-44/) |
| **Bussard** | Points lumineux inspirés des transports et des affichages LED, avec italique glitch | 6 (Thin → Black) + 6 italiques glitch | SIL OFL 1.1 | [Page](https://jonlekern.github.io/Fonts/bussard/) · [Zip](bussard/Bussard.zip) · [Dossier](bussard/) |
| **The Forever Font** | Chasse fixe au flou exact de l'encre : lettres tirées de tatouages et d'une machine à écrire, 3 versions de chaque signe | 1 (Regular) | Usage personnel gratuit, commercial sur autorisation | [Page](https://jonlekern.github.io/Fonts/the-forever-font/) · [Zip](the-forever-font/TheForeverFont.zip) · [Dossier](the-forever-font/) |

## Organisation

```
index.html              Catalogue des polices (page d'accueil du site)
shared/
  site.css              Styles communs à toutes les pages
  specimen.js           Spécimen commun : graisses, testeur, caractères
calebard/, falsard/,    Un dossier par police
clebard/, malabard/,
brecard/, fusard-032/,
jalousia/, espresso-44/, bussard/,
the-forever-font/
  index.html            Page de la police
  README.md             Graisses, fichiers, licence
  OFL.txt               Licence de la police (Clebard : LICENCE.txt + GUST ; Brécard, Fûsard-032, Jalousia et The Forever Font : LICENCE.txt)
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

## Règle : polices en couleur

Une police dont la couleur est dans le fichier (images ou couleurs fixes, comme **The Forever Font** et son encre noire) ne suit pas le mode sombre : elle resterait noire sur fond noir.

**Police noire = la page garde les couleurs claires du site, même en mode sombre.**

- Sur sa page : `<html lang="fr" data-theme="light">` et, dans le `<style>` de la page : `:root{color-scheme:light}`.
- Sur la page d'accueil : sa carte garde les couleurs claires, avec ses propres couleurs sur la balise `<a class="font-card">` :
  `style="--bg:#f4f1ec;--ink:#141414;--muted:#6f685e;--line:#d9d2c6;background:#f4f1ec;color:#141414;border-color:#d9d2c6"`.
- Vérifier la page et la carte en mode sombre avant de mettre en ligne.

Exemple complet : `the-forever-font/index.html`.
