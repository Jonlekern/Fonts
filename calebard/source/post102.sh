#!/bin/bash
# usage : ./post102.sh <dossier ttf>   (les 11 graisses de la version 1.0.1 ; Goofy et Extra Goofy ne sont pas touchés)
# Version 1.0.2 : réglée sur le vrai logo LAFLEURSTUDIO (t-shirt)
set -e
PY=${PY:-python3}
D=$1
W="Hairline Thin Light Regular Medium Bold ExtraBold SuperBold Black ExtraBlack ExtremeBlack"
for w in $W; do $PY logo102.py $D/Calebard-$w.ttf $D/Calebard-$w.ttf; done   # L, U, lettres rondes
$PY r102.py $(for w in $W; do echo $D/Calebard-$w.ttf; done)                  # R
$PY spacing102.py $D espaces-logo-tshirt.json                                    # règles d'espacement + 12 paires du logo
$PY j102.py $(for w in $W; do echo $D/Calebard-$w.ttf; done)                  # crochet du j
$PY f102.py $(for w in $W; do echo $D/Calebard-$w.ttf; done)                  # F
$PY set_version.py 1.002 $(for w in $W; do echo $D/Calebard-$w.ttf; done)
