"""Fabrique tout GUÉPARD : variable, WOFF2, 6 fixes, zip."""
import shutil
import zipfile
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.ttLib.removeOverlaps import removeOverlaps
from gp_fab import fabriquer, INSTANCES, FAMILLE

RACINE = Path(__file__).parent.parent


def fixes(vf_path):
    dossier = RACINE / "fonts" / "ttf"
    shutil.rmtree(dossier, ignore_errors=True)
    dossier.mkdir()
    sorties = []
    for nom, v, b in INSTANCES:
        f = instantiateVariableFont(TTFont(vf_path), {"VITE": v, "BAND": b}, updateFontNames=False)
        removeOverlaps(f)
        ps = nom.replace(" ", "")
        nt = f["name"]
        for i, val in {1: f"{FAMILLE} {nom}" if nom != "Regular" else FAMILLE, 2: "Regular",
                       4: f"{FAMILLE} {nom}", 6: f"{FAMILLE}-{ps}",
                       3: f"1.000;LAFS;{FAMILLE}-{ps}", 16: FAMILLE, 17: nom}.items():
            nt.setName(val, i, 3, 1, 0x409)
        for rec in list(nt.names):
            if rec.nameID == 25:
                nt.names.remove(rec)
        if "STAT" in f:
            del f["STAT"]
        nt.removeUnusedNames(f)
        s = dossier / f"{FAMILLE}-{ps}.ttf"
        f.save(s)
        sorties.append(s)
    return sorties


def main():
    vf = fabriquer(RACINE / "fonts" / "variable")
    f = TTFont(vf)
    f.flavor = "woff2"
    (RACINE / "fonts" / "woff2").mkdir(parents=True, exist_ok=True)
    f.save(RACINE / "fonts" / "woff2" / vf.with_suffix(".woff2").name)
    fx = fixes(vf)
    ofl = (Path(__file__).parent / "danfo" / "OFL.txt").read_text()
    ofl = ofl.replace("(https://github.com/Afrotype/danfo)\n",
                      "(https://github.com/Afrotype/danfo)\nCopyright 2026 LaFleurStudio (Guépard, https://jonlekern.github.io/Fonts/guepard/)\n", 1)
    (RACINE / "OFL.txt").write_text(ofl)
    with zipfile.ZipFile(RACINE / f"{FAMILLE}.zip", "w", zipfile.ZIP_DEFLATED) as z:
        z.write(vf, vf.name)
        for s in fx:
            z.write(s, f"fixes/{s.name}")
        z.write(RACINE / "OFL.txt", "OFL.txt")
    print("ok", vf.name, len(fx), "fixes")


if __name__ == "__main__":
    main()
