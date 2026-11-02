#!/bin/bash
# usage : ./post.sh <dossier>  (après pipeline.sh) : U et J, espacement du logo, puis Goofy, Extra Goofy et la fleur
set -e
PY=${PY:-python3}
O=$1
$PY -c "
import uj
for w in ['Hairline','Thin','Light','Regular','Medium','Bold','ExtraBold','SuperBold','Black','ExtraBlack','ExtremeBlack']:
    p='$O/ttf/Calebard-'+w+'.ttf'; info,_=uj.process(p,p); print(w,{k:v[2] for k,v in info.items()})
"
$PY spacing.py $O/ttf espaces-logo.json
./finish.sh $O
