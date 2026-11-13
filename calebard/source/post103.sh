#!/bin/bash
# usage : ./post103.sh <dossier ttf>   (les 13 fichiers de la version 1.0.2)
# Version 1.0.3 : le cyrillique russe (33 capitales, 33 minuscules), Л et Д droits
set -e
PY=${PY:-python3}
D=$1
W="Hairline Thin Light Regular Medium Bold ExtraBold SuperBold Black ExtraBlack ExtremeBlack"
for w in $W; do $PY cyrillique.py $D/Calebard-$w.ttf $D/Calebard-$w.ttf; done   # les 11 graisses
for s in Goofy ExtraGoofy; do $PY cyrillique_goofy.py $D/Calebard-$s.ttf $D/Calebard-Black.ttf; done
$PY set_version.py 1.003 $D/Calebard-*.ttf
