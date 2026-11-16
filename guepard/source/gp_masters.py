"""Masters de GUÉPARD, tous tirés du même découpage : compatibles par construction."""
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphCoordinates
from gp_tranches import COUPES, RECOUVRE

OUVERTURE = 18          # épaisseur d'une bande ouverte (BAND 50 et 100)
DECALAGE = 60           # glissement des tranches au glitch (BAND 100)
SENS = (1, -1, 1)       # sens du glissement, tranche 0 (sol) à 2
PENTE = 0.21            # ≈ tan 12°, à VITE 100
ETIRE = 1.15            # étirement horizontal à VITE 100
OVERLAP_SIMPLE = 0x40

# (ouverture, décalage) par valeur de BAND
BAND = {0: (-2 * RECOUVRE, 0), 50: (OUVERTURE, 0), 100: (OUVERTURE, DECALAGE)}


def master_band(tranches, ouverture, decalage):
    out = []
    der = len(COUPES)
    for rang, contours in enumerate(tranches):
        bas = -1e9 if rang == 0 else COUPES[rang - 1] + ouverture / 2
        haut = 1e9 if rang == der else COUPES[rang] - ouverture / 2
        dx = decalage * SENS[rang] if rang < der else 0
        for c in contours:
            out.append([[x + dx, min(max(y, bas), haut), on] for x, y, on in c])
    return out


def vitesse(contours, pente=PENTE, etire=ETIRE):
    return [[[etire * x + pente * y, y, on] for x, y, on in c] for c in contours]


def glyphe(contours):
    g = Glyph()
    if not contours:
        g.numberOfContours = 0
        return g
    pts, flags, ends = [], [], []
    for c in contours:
        for x, y, on in c:
            pts.append((round(x), round(y)))
            flags.append(1 if on else 0)
        ends.append(len(pts) - 1)
    flags[0] |= OVERLAP_SIMPLE
    g.coordinates = GlyphCoordinates(pts)
    g.flags = bytearray(flags)
    g.endPtsOfContours = ends
    g.numberOfContours = len(ends)
    g.program = None
    from fontTools.ttLib.tables import ttProgram
    g.program = ttProgram.Program(); g.program.fromBytecode(b"")
    return g
