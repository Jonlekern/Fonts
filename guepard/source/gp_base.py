"""Base de GUÉPARD : Danfo figée à ELSH 0 (forme lisse), composites décomposés."""
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen

ICI = Path(__file__).parent
SOURCE = ICI / "danfo" / "Danfo[ELSH].ttf"


def charger_base() -> TTFont:
    f = instantiateVariableFont(TTFont(SOURCE), {"ELSH": 0})
    gs = f.getGlyphSet()
    glyf = f["glyf"]
    neufs = {}
    for n in f.getGlyphOrder():
        if glyf[n].isComposite():
            rec = DecomposingRecordingPen(gs)
            gs[n].draw(rec)
            pen = TTGlyphPen(None)
            rec.replay(pen)
            neufs[n] = pen.glyph()
    for n, g in neufs.items():
        glyf[n] = g
    for t in ("fpgm", "prep", "cvt ", "hdmx", "LTSH", "VDMX"):
        if t in f:
            del f[t]
    for n in f.getGlyphOrder():
        g = glyf[n]
        if hasattr(g, "program"):
            del g.program
    # Danfo : le deux-points modificateur (U+A789) a une chasse nulle ; on lui donne celle du deux-points.
    f["hmtx"]["uniA789"] = f["hmtx"]["colon"]
    return f
