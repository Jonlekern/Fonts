"""Masters de GUÉPARD, tous tirés du même découpage : compatibles par construction."""
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphCoordinates
from gp_tranches import COUPES, RECOUVRE

OUVERTURE = 18          # épaisseur d'une bande ouverte (BAND 50 et 100)
DECALAGE = 110          # glissement des tranches au glitch (BAND 100)
SENS = (1, -1, 1)       # sens du glissement, tranche 0 (sol) à 2
PENTE = 0.21            # ≈ tan 12°, à VITE 100
ETIRE = 1.15            # étirement horizontal à VITE 100
OVERLAP_SIMPLE = 0x40

# (ouverture, décalage) par valeur de BAND
POINTE = 1.6           # au glitch, chaque tranche penche à l'opposé de sa voisine : bouts en lame
PIVOT = 358            # la vitesse penche autour de la mi-hauteur des capitales
BAND = {0: (-2 * RECOUVRE, 0, 0), 50: (OUVERTURE, 0, 0), 100: (OUVERTURE, DECALAGE, POINTE)}


def master_band(tranches, ouverture, decalage, pointe=0):
    out = []
    der = len(COUPES)
    entier = not any(tranches[:der])          # signe sans bas noir : intact
    for rang, contours in enumerate(tranches):
        bas = -1e9 if rang == 0 or entier else COUPES[rang - 1] + ouverture / 2
        haut = 1e9 if rang == der else COUPES[rang] - ouverture / 2
        dx = decalage * SENS[rang] if rang < der else 0
        k = pointe * SENS[rang] if rang < der else 0
        mid = ((COUPES[rang - 1] if rang else 0) + COUPES[rang]) / 2 if rang < der else 0
        for c in contours:
            pts = []
            for x, y, on in c:
                y = min(max(y, bas), haut)
                pts.append([x + dx + k * (y - mid), y, on])
            out.append(pts)
    return out


def vitesse(contours, pente=PENTE, etire=ETIRE):
    return [[[etire * x + pente * (y - PIVOT), y, on] for x, y, on in c] for c in contours]


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
