#!/bin/bash
# usage : ./finish.sh <dossier sortie>   (Goofy, Extra Goofy depuis le Black, puis la fleur partout)
set -e
PY=${PY:-python3}
O=$1
$PY build_goofy.py $O/ttf/Calebard-Black.ttf $O/raw/goofy.ttf > /dev/null
$PY build_extra_goofy.py $O/ttf/Calebard-Black.ttf $O/raw/eg.ttf > /dev/null
$PY rename_style.py $O/raw/goofy.ttf $O/ttf/Calebard-Goofy.ttf Goofy > /dev/null
$PY liga_off.py $O/ttf/Calebard-Goofy.ttf
$PY rename_style.py $O/raw/eg.ttf $O/ttf/Calebard-ExtraGoofy.ttf "Extra Goofy" > /dev/null
$PY add_flower.py $O/ttf/*.ttf > /dev/null
