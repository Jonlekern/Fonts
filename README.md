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
| **DIHEDRON-008** | Display en pointes et en losanges, poids en haut | 9 (wa'vatlh → Hutvatlh, en klingon) + 9 italiques | Usage personnel gratuit, commercial sur autorisation | [Page](https://jonlekern.github.io/Fonts/dihedron-008/) · [Zip](dihedron-008/DIHEDRON008.zip) · [Dossier](dihedron-008/) |
| **Nexum** | Techno gothique : géométrie stricte, croisements partout, bouts en pointe | 9 (Hairline → Black) | Usage personnel gratuit, commercial sur autorisation | [Page](https://jonlekern.github.io/Fonts/nexum/) · [Zip](nexum/Nexum.zip) · [Dossier](nexum/) |
| **Typefive** | Chasse fixe faite avec les vraies frappes d'une machine à écrire : le grain du ruban, 5 versions de chaque signe | 1 (Regular) | Usage personnel gratuit, commercial sur autorisation | [Page](https://jonlekern.github.io/Fonts/typefive/) · [Zip](typefive/Typefive.zip) · [Dossier](typefive/) |
| **Jalousia** | Chiffres romains néo-gothiques dessinés à la main, en deux polices : Net (trait net) et Craie | 4 (Centum → Quadringenti, en latin) + 4 italiques, pour chacune | Usage personnel gratuit, commercial sur autorisation | [Page](https://jonlekern.github.io/Fonts/jalousia/) · [Zip Net](jalousia/JalousiaNet.zip) · [Zip Craie](jalousia/JalousiaCraie.zip) · [Dossier](jalousia/) |
| **Espresso 4.40.-** | Projet artistique : écriture à la main tirée des ardoises des cafés et des boulangeries biennois | 5 (Lungo → Moka) | SIL OFL 1.1 | [Page](https://jonlekern.github.io/Fonts/espresso-440/) · [Zip](espresso-440/Espresso440.zip) · [Dossier](espresso-440/) |
| **DOTSIGNAL** | Points lumineux inspirés des transports et des affichages LED, avec italique glitch | 6 (Thin → Black) + 6 italiques glitch | SIL OFL 1.1 | [Page](https://jonlekern.github.io/Fonts/dotsignal/) · [Zip](dotsignal/DOTSIGNAL.zip) · [Dossier](dotsignal/) |
| **The Forever Font** | Chasse fixe au flou exact de l'encre : lettres tirées de tatouages et d'une machine à écrire, 3 versions de chaque signe | 1 (Regular) | Usage personnel gratuit, commercial sur autorisation | [Page](https://jonlekern.github.io/Fonts/the-forever-font/) · [Zip](the-forever-font/TheForeverFont.zip) · [Dossier](the-forever-font/) |
| **Biel/Bienne WildStyle** | Graffiti tiré des murs de Biel/Bienne : majuscules en wildstyle, minuscules en bubble ; versions noire, couleur et calques | 4 (Toy → Legend) | Usage personnel gratuit, commercial sur autorisation | [Page](https://jonlekern.github.io/Fonts/biel-bienne-wildstyle/) · [Zip](biel-bienne-wildstyle/BielBienneWildStyle.zip) · [Dossier](biel-bienne-wildstyle/) |
| **Swift Rallye 01** | Course, années 70 : large, penchée vers l'avant, coins ronds, bouts en biseau ; née de l'étude des traits de Biel/Bienne WildStyle | 12 (Reco → Groupe B) | Usage personnel gratuit, commercial sur autorisation | [Page](https://jonlekern.github.io/Fonts/swift-rallye-01/) · [Zip](swift-rallye-01/SwiftRallye01.zip) · [Dossier](swift-rallye-01/) |

## Organisation

```
index.html              Catalogue des polices (page d'accueil du site)
shared/
  site.css              Styles communs à toutes les pages
  specimen.js           Spécimen commun : graisses, testeur, caractères
calebard/, falsard/,    Un dossier par police
clebard/, malabard/,
dihedron-008/, nexum/,
jalousia/, espresso-440/, dotsignal/,
the-forever-font/, typefive/,
biel-bienne-wildstyle/, swift-rallye-01/
  index.html            Page de la police
  README.md             Graisses, fichiers, licence
  OFL.txt               Licence de la police (Clebard : LICENCE.txt + GUST ; DIHEDRON-008, Nexum, Jalousia, The Forever Font, Typefive, Biel/Bienne WildStyle et Swift Rallye 01 : LICENCE.txt)
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

## Règle : noms des polices

**Les noms en -ard sont réservés aux polices modifiées** (Calebard, Falsard, Clebard, Malabard…). **Toutes les autres sont des créations** et ne finissent pas en -ard (Nexum, DIHEDRON-008, DOTSIGNAL…).

## Règle : polices en couleur

Une police dont la couleur est dans le fichier (images ou couleurs fixes, comme **The Forever Font** et **Typefive** et leur encre noire) ne suit pas le mode sombre : elle resterait noire sur fond noir.

**Police noire = la page garde les couleurs claires du site, même en mode sombre.**

- Sur sa page : `<html lang="fr" data-theme="light">` et, dans le `<style>` de la page : `:root{color-scheme:light}`.
- Les pages de ces polices restent **blanches** (le papier, la peau : on voit la vraie encre).
- Sur la page d'accueil, leur carte suit le mode sombre comme les autres : le nom et l'exemple portent la classe `encre` (`class="name encre"`, `class="sample encre"`). En mode clair l'encre reste noire ; en mode sombre elle est retournée en blanc avec `filter:invert(1)`, halo compris (c'est un négatif : la police elle-même reste noire).
- Vérifier la page et la carte en mode sombre avant de mettre en ligne.

Exemple complet : `the-forever-font/index.html`.

## Règle : cartes de l'accueil

**Deux lignes de tags au maximum** sous chaque carte, mesurées sur téléphone (390 px de large). Si ça déborde, on garde les tags les plus utiles (graisses, licence, année) et on enlève les autres.

## Règle : signes du standard Google

Les signes ajoutés pour le standard Google (Europe de l'Est, turc, gallois, accents seuls : ł ş ğ č ř ő ȷ ˇ ˘…) **ne sont pas montrés sur le site** : ni dans la grille des caractères, ni dans les exemples ou les images. Ils restent dans les polices et s'affichent quand on les tape dans le testeur.

- La grille les retire toute seule : liste `SIGNES_CACHES` dans `shared/specimen.js`.
- Une page peut en garder avec `glyphsGarder` (Clebard garde Ă ă Đ đ, pour le vietnamien).
- L'espagnol et le portugais (ñ á ó ã…) restent montrés.
