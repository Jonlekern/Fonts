"""Assemblage de la police variable GUÉPARD (axes VITE et BAND)."""
from pathlib import Path
from fontTools.designspaceLib import DesignSpaceDocument, AxisDescriptor, SourceDescriptor, InstanceDescriptor
from fontTools import varLib
from fontTools.otlLib.builder import buildStatTable
from fontTools.misc.treeTools import build_n_ary_tree  # noqa: F401 (fontTools présent)
from gp_base import charger_base
from gp_tranches import decouper
from gp_masters import master_band, vitesse, glyphe, BAND, ETIRE, PENTE, PIVOT

FAMILLE = "Guepard"
CREDITS = "Afrotype, Seyi Olusanya, Eyiyemi Adegbite, David Udoh, Mirko Velimirović (Danfo) ; LaFleurStudio (Guépard)"
COPYRIGHT = "Copyright 2023 The Danfo Project Authors (https://github.com/Afrotype/danfo). Copyright 2026 LaFleurStudio (Guépard)."
LICENCE = ("This Font Software is licensed under the SIL Open Font License, Version 1.1. "
           "This license is available with a FAQ at: https://openfontlicense.org")
INSTANCES = [("Regular", 0, 0), ("Course", 100, 0), ("Bandes", 0, 50),
             ("Course Bandes", 100, 50), ("Glitch", 0, 100), ("Course Glitch", 100, 100)]


def _gpos_vitesse(f):
    vus = set()

    def visite(o):
        if o is None or id(o) in vus:
            return
        vus.add(id(o))
        cls = type(o).__name__
        if cls == "ValueRecord":
            for a in ("XAdvance", "XPlacement"):
                if hasattr(o, a):
                    setattr(o, a, round(getattr(o, a) * ETIRE))
            return
        if cls == "Anchor":
            o.XCoordinate = round(o.XCoordinate * ETIRE + PENTE * (o.YCoordinate - PIVOT))
            return
        if isinstance(o, (list, tuple)):
            for x in o:
                visite(x)
            return
        if hasattr(o, "__dict__") and type(o).__module__.endswith("otTables"):
            for v in vars(o).values():
                visite(v)

    if "GPOS" in f:
        for lk in f["GPOS"].table.LookupList.Lookup:
            visite(lk.SubTable)


def _noms(f):
    nt = f["name"]
    for rec in list(nt.names):
        if rec.platformID == 1:
            nt.names.remove(rec)
        elif rec.nameID < 256:
            nt.removeNames(nameID=rec.nameID)
    vals = {0: COPYRIGHT, 1: FAMILLE, 2: "Regular", 3: f"1.000;LAFS;{FAMILLE}-Regular",
            4: f"{FAMILLE} Regular", 5: "Version 1.000", 6: f"{FAMILLE}-Regular", 8: "LaFleurStudio",
            9: CREDITS, 11: "https://jonlekern.github.io/Fonts/guepard/", 13: LICENCE,
            14: "https://openfontlicense.org", 25: FAMILLE}
    for i, v in vals.items():
        nt.setName(v, i, 3, 1, 0x409)
    f["head"].fontRevision = 1.0
    f["OS/2"].achVendID = "LAFS"


def _prep(f):
    from fontTools.ttLib import newTable
    from fontTools.ttLib.tables import ttProgram
    prep = newTable("prep")
    prep.program = ttProgram.Program()
    prep.program.fromAssembly(["PUSHW[]", "511", "SCANCTRL[]", "PUSHB[]", "4", "SCANTYPE[]"])
    f["prep"] = prep
    gasp = newTable("gasp")
    gasp.gaspRange = {0xFFFF: 15}
    gasp.version = 1
    f["gasp"] = gasp


def _masters():
    base = charger_base()
    gs = base.getGlyphSet()
    tranches = {n: decouper(gs, n) for n in base.getGlyphOrder()}
    out = {}
    for b, prm in BAND.items():
        for v in (0, 100):
            f = charger_base()
            glyf, hmtx = f["glyf"], f["hmtx"]
            for n, tr in tranches.items():
                c = master_band(tr, *prm)
                if v:
                    c = vitesse(c)
                g = glyphe(c)
                glyf[n] = g
                g.recalcBounds(glyf)
                adv, _ = hmtx[n]
                if v:
                    adv = round(adv * ETIRE)
                hmtx[n] = (adv, g.xMin if g.numberOfContours else 0)
            if v:
                _gpos_vitesse(f)
            if "STAT" in f:
                del f["STAT"]
            _noms(f)
            out[(v, b)] = f
    return out


def fabriquer(dossier):
    dossier = Path(dossier)
    dossier.mkdir(parents=True, exist_ok=True)
    ds = DesignSpaceDocument()
    for tag, nom in (("VITE", "Vitesse"), ("BAND", "Bandes")):
        a = AxisDescriptor()
        a.tag, a.name, a.minimum, a.default, a.maximum = tag, nom, 0, 0, 100
        ds.addAxis(a)
    for (v, b), f in _masters().items():
        s = SourceDescriptor()
        s.font = f
        s.name = f"m{v}_{b}"
        s.location = {"Vitesse": v, "Bandes": b}
        ds.addSource(s)
    for nom, v, b in INSTANCES:
        i = InstanceDescriptor()
        i.familyName, i.styleName = FAMILLE, nom
        i.postScriptFontName = f"{FAMILLE}-{nom.replace(' ', '')}"
        i.location = {"Vitesse": v, "Bandes": b}
        ds.addInstance(i)
    vf, _, _ = varLib.build(ds)
    buildStatTable(vf, [
        dict(tag="VITE", name="Vitesse", values=[
            dict(value=0, name="Droite", flags=0x2), dict(value=100, name="Course")]),
        dict(tag="BAND", name="Bandes", values=[
            dict(value=0, name="Pleine", flags=0x2), dict(value=50, name="Bandes"), dict(value=100, name="Glitch")]),
    ], elidedFallbackName="Regular")
    for rec in list(vf["name"].names):
        if rec.platformID == 1:
            vf["name"].names.remove(rec)
    vf["name"].removeUnusedNames(vf)
    _prep(vf)
    sortie = dossier / f"{FAMILLE}[VITE,BAND].ttf"
    vf.save(sortie)
    return sortie


if __name__ == "__main__":
    print(fabriquer(Path(__file__).parent.parent))
