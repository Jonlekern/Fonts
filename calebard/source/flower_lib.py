import re, pathops
from fontTools.svgLib.path import parse_path
from fontTools.pens.transformPen import TransformPen
SVG = "logo-fleur.svg"  # logo fleur LaFleurStudio (dépôt lafleurstudio : images/logo-fleur.svg)
def flower(stroke_w=0):
    svg = open(SVG).read()
    p = pathops.Path(); pen = TransformPen(p.getPen(), (0.1, 0, 0, 0.1, 0, 0))
    for d in re.findall(r'<path d="([^"]+)"', svg, re.S): parse_path(d, pen)
    p.simplify(clockwise=True)
    if stroke_w:
        s = pathops.Path(p); s.stroke(stroke_w, pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 4)
        s.convertConicsToQuads()
        p = pathops.op(p, s, pathops.PathOp.UNION, clockwise=True)
    return p
