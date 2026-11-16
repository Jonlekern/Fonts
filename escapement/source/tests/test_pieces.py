import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from fontTools.pens.recordingPen import RecordingPen
from pieces import superellipse, anneau, ouverture, bornes, courses, coupe, aire


def test_superellipse_bornes():
    b = bornes(superellipse(300, 250, 200, 260, 2.76))
    assert all(abs(a - e) <= 1 for a, e in zip(b, (100, -10, 500, 510)))


def test_superellipse_expo():
    assert abs(aire(superellipse(0, 0, 200, 200, 2)) - math.pi * 200 * 200) / (math.pi * 40000) < 0.005
    assert aire(superellipse(0, 0, 200, 200, 4)) > aire(superellipse(0, 0, 200, 200, 2.76)) > math.pi * 40000


def test_anneau_epaisseurs():
    a = anneau(300, 250, 200, 260, 90, 76, 2.76)
    (g0, g1), (d0, d1) = courses(a, 250)
    assert abs((g1 - g0) - 90) <= 1 and abs((d1 - d0) - 90) <= 1
    v = coupe(a, 299, -100, 301, 600)
    hs = sorted(round(c.bounds[3] - c.bounds[1]) for c in v.contours)
    assert all(abs(h - 76) <= 1 for h in hs) and len(hs) == 2


def test_ouverture_plate():
    a = ouverture(anneau(300, 250, 200, 260, 90, 76, 2.76), 300, 150, 380, 'droite')
    rp = RecordingPen(); a.draw(rp)
    pts = [p[-1] for op, p in rp.value if p]
    for y in (150, 380):
        bord = [x for x, yy in pts if abs(yy - y) < 0.01 and x > 300]
        assert len(bord) == 2, (y, bord)
    assert len(courses(a, 250)) == 1          # le côté droit est ouvert
