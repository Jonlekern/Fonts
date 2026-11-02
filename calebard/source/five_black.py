"""Retouche du 5 du Black (coin de la fente), faite à la main à 130 % : même déplacement, mis à l'échelle."""
import sys, os
from fontTools.ttLib import TTFont
EDIT = {17: ((702, 572), (764, 534)), 18: ((990, 608), (934, 608))}   # à 130 % : avant, après
K130 = 1.3342
f = TTFont(sys.argv[1]); g = f["glyf"]["five"]; c = g.coordinates
st = float(os.environ.get("STRETCH", "1.30"))
import re; k = float(re.search(r"'x_scale': ([0-9.]+)", [l for l in open(os.path.join(os.path.dirname(sys.argv[1]), "..", "log-family.txt")) if l.startswith("Black")][0]).group(1))
for i, ((ox, oy), (nx, ny)) in EDIT.items():
    cx, cy = c[i]
    if st == 1.30: assert (cx, cy) == (ox, oy)
    print("retouche five", i, (cx, cy), "à 130 % :", (ox, oy))
    c[i] = (cx + round((nx - ox) * k / K130), cy + (ny - oy))
g.recalcBounds(f["glyf"]); f.save(sys.argv[1])
