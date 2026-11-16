import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from mesures import mesures, GRAISSES


def test_hauteurs():
    for p in GRAISSES:
        m = mesures(p)
        assert (m['upm'], m['cap'], m['x'], m['asc'], m['desc'], m['depasse']) == (1000, 700, 504, 740, -220, 12)


def test_futs_croissants():
    for k in ('fut_min', 'fut_cap'):
        v = [mesures(p)[k] for p in GRAISSES]
        assert all(a < b for a, b in zip(v, v[1:])), (k, v)
    assert 85 <= mesures(400)['fut_min'] <= 92


def test_barres():
    for p in GRAISSES:
        m = mesures(p)
        assert m['barre_min'] == round(0.85 * m['fut_min'])
        assert m['barre_cap'] == round(0.85 * m['fut_cap'])


def test_expo():
    for p in GRAISSES:
        m = mesures(p)
        assert 2 < m['expo'] < m['expo_ovs']
        assert 2.5 <= m['expo_ovs'] <= 5


def test_chasse_n():
    assert 540 <= mesures(400)['chasse_n'] <= 560


def test_approche():
    assert 60 <= mesures(400)['approche_min'] <= 70


def test_ovs():
    assert mesures(400)['large_ovs'] == 1.22


def test_rapport_capitales_minuscules():
    """Le trait des capitales garde le rapport d'Overshoot avec celui des minuscules (environ 1,16)."""
    for p in GRAISSES:
        m = mesures(p)
        assert 1.12 <= m['fut_cap'] / m['fut_min'] <= 1.20, (p, m['fut_cap'], m['fut_min'])
