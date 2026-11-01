import sys
from fontTools.ttLib import TTFont
src, dst, style = sys.argv[1], sys.argv[2], sys.argv[3]
F = TTFont(src); nm = F["name"]; fam = "Calebard"; ps = style.replace(" ", "")
ribbi = style in ("Regular", "Bold")
vals = {1: fam if ribbi else f"{fam} {style}", 2: style if ribbi else "Regular",
        3: f"1.000;{fam}-{ps}", 4: f"{fam} {style}", 6: f"{fam}-{ps}", 16: fam, 17: style}
nm.names = [r for r in nm.names if r.nameID not in vals]
for i, v in vals.items():
    nm.setName(v, i, 3, 1, 0x409); nm.setName(v, i, 1, 0, 0)
os2 = F["OS/2"]
os2.fsSelection &= ~((1 << 0) | (1 << 5) | (1 << 6))
os2.fsSelection |= (1 << 5) if style == "Bold" else (1 << 6)
F["head"].macStyle = 1 if style == "Bold" else 0
F.save(dst)
t = TTFont(dst)
print({i: t["name"].getDebugName(i) for i in (1, 2, 4, 6, 17)}, t["OS/2"].usWeightClass, "bold-flag" if t["OS/2"].fsSelection & 32 else "")
