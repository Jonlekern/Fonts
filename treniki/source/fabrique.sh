#!/bin/bash
# TRENIKI, tout refait en une commande, à partir des 13 fichiers de Calebard 1.0.2 :
#   cd treniki/source && ./fabrique.sh
set -e
PY=${PY:-python3}
ICI=$(cd "$(dirname "$0")" && pwd); T=$ICI/..; CAL=$ICI/../../calebard/fonts/ttf
W=$(mktemp -d); mkdir -p $W/cal $W/out
cp $CAL/Calebard-*.ttf $W/cal/
cd $ICI
for w in Hairline Thin Light Regular Medium Bold ExtraBold SuperBold Black ExtraBlack ExtremeBlack; do
  $PY cyrillique.py $W/cal/Calebard-$w.ttf $W/cal/Calebard-$w.ttf > /dev/null      # les 66 lettres russes, crénage, accroches
done
for s in Goofy ExtraGoofy; do $PY cyrillique_goofy.py $W/cal/Calebard-$s.ttf $W/cal/Calebard-Black.ttf; done
$PY treniki.py $W/cal $W/out                                                        # russe + latin de base, noms russes
$PY anticollision.py $W/out/TRENIKI-*.ttf                                           # aucune paire russe ne se touche
rm -f $T/fonts/ttf/*.ttf $T/fonts/woff2/*.woff2
cp $W/out/*.ttf $T/fonts/ttf/
$PY -c "
import glob, os, sys
from fontTools.ttLib import TTFont
for f in sorted(glob.glob('$T/fonts/ttf/*.ttf')):
    t = TTFont(f); t.flavor = 'woff2'; t.save('$T/fonts/woff2/' + os.path.basename(f)[:-4] + '.woff2')
"
mkdir -p $W/zip/TRENIKI && cp $T/fonts/ttf/*.ttf $T/OFL.txt $W/zip/TRENIKI/
rm -f $T/TRENIKI.zip && (cd $W/zip && zip -qr9 $T/TRENIKI.zip TRENIKI)
rm -rf $W
echo "TRENIKI : $(ls $T/fonts/ttf | wc -l) fichiers, zip fait"
