import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from mesures import mesures


def test_mesures_storm():
    m = mesures('Storm')
    assert m['fut_cap'] == 254          # H : 54 → 308
    assert m['barre_cap'] == 173        # E : barre du bas
    assert m['fut_min'] == 218          # l : 46 → 264
    assert m['barre_min'] == 149        # z : barre du bas
    assert m['cap'] == 730 and m['x'] == 599
    assert m['approche_cap'] == 54 and m['approche_min'] == 46
    assert m['contre_H'] == 410


def test_mesures_calm():
    m = mesures('Calm')
    assert m['fut_cap'] == 38 and m['barre_cap'] == 36
    assert m['fut_min'] == 33 and m['barre_min'] == 31
