#!/bin/bash
# usage : STRETCH=1.209 OVR1000=overrides-1000-120.json OVR1100=overrides-1100-120.json ./pipeline.sh <dossier sortie>
set -e
PY=${PY:-python3}
VF=${VF:-"Anybody[wdth,wght].ttf"}
O=$1; mkdir -p $O/raw $O/ttf
$PY build_family.py $VF $O/raw > $O/log-family.txt
XT=1.0 XNAME=W1000 $PY build_xw.py $VF $O/raw build_family.py ${OVR1000:-overrides-1000.json} > $O/log-1000.txt
XT=2.0 XNAME=W1100 $PY build_xw.py $VF $O/raw build_family.py ${OVR1100:-overrides-1100.json} > $O/log-1100.txt
r() { $PY rename_style.py $O/raw/Calebard-$1.ttf $O/ttf/Calebard-$2.ttf "$3" > /dev/null; }
r Thin Hairline Hairline; r ExtraLight Thin Thin; r Light Light Light; r Regular Regular Regular; r Medium Medium Medium
r SemiBold Bold Bold; r Bold ExtraBold "Extra Bold"; r ExtraBold SuperBold "Super Bold"; r Black Black Black
r W1000 ExtraBlack "Extra Black"; r W1100 ExtremeBlack "Extreme Black"
$PY five_black.py $O/ttf/Calebard-Black.ttf
for w in SuperBold Black ExtraBlack ExtremeBlack; do $PY fix_corners.py $O/ttf/Calebard-$w.ttf $O/ttf/Calebard-$w.ttf $O/corners-$w.json; done
if [ "$STRETCH" != "1.30" ]; then $PY nudge.py $O/ttf/Calebard-Black.ttf $O/ttf/Calebard-ExtraBlack.ttf; $PY nudge.py $O/ttf/Calebard-ExtraBlack.ttf $O/ttf/Calebard-ExtremeBlack.ttf; fi
