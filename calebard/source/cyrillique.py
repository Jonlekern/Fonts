# Cyrillique de Calebard : les lettres russes dessinées à partir des pièces latines de chaque graisse.
#
#   python3 cyrillique.py Calebard-Black.ttf sortie.ttf [A|B]
#
# Chaque graisse est mesurée (fût, barre, diagonale, hauteurs, approches) puis les lettres sont
# construites avec ces mesures : rien n'est étiré, les épaisseurs restent celles de la graisse.
# A ou B : la forme de Л et Д (A = en pointe comme le A, B = droite comme le П).
import sys
import pathops
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.reverseContourPen import ReverseContourPen
from fontTools.pens.boundsPen import BoundsPen

OP = pathops.PathOp


# ---------- outils de tracé ----------
def poly(*pts):
    p = pathops.Path(); pen = p.getPen()
    pen.moveTo(pts[0])
    for q in pts[1:]: pen.lineTo(q)
    pen.closePath()
    return p

def rect(x0, y0, x1, y1):
    return poly((x0, y0), (x1, y0), (x1, y1), (x0, y1))

def union(*ps):
    r = pathops.Path()
    for p in ps:
        r = pathops.op(r, p, OP.UNION, fix_winding=True)
    return r

def moins(a, b):
    return pathops.op(a, b, OP.DIFFERENCE, fix_winding=True)

def inter(a, b):
    return pathops.op(a, b, OP.INTERSECTION, fix_winding=True)

def transf(p, sx=1, sy=1, dx=0, dy=0):
    rp = RecordingPen(); p.draw(rp)
    q = pathops.Path(); pen = q.getPen()
    for op, a in rp.value:
        getattr(pen, op)(*[(x * sx + dx, y * sy + dy) for x, y in a])
    return pathops.simplify(q, fix_winding=True)

def bornes(p):
    b = p.bounds
    return b[0], b[1], b[2], b[3]

def coupes_x(p, y):
    r = inter(p, rect(-9000, y, 19000, y + 1)); out = []
    for c in r.contours:
        x = [pt[0] for pt in c.points]; out.append((min(x), max(x)))
    return sorted(out)

def coupes_y(p, x):
    r = inter(p, rect(x, -9000, x + 1, 9000)); out = []
    for c in r.contours:
        y = [pt[1] for pt in c.points]; out.append((min(y), max(y)))
    return sorted(out)


class Graisse:
    def __init__(self, chemin):
        self.t = TTFont(chemin); self.gs = self.t.getGlyphSet(); self.hm = self.t['hmtx']
        self.cm = self.t.getBestCmap()
        g = self.lat
        # capitales
        H = g('H'); self.CH = bornes(H)[3]
        self.S = self.larg(coupes_x(H, 100)[0])                 # fût
        E = g('E'); xm = (bornes(E)[0] + bornes(E)[2]) / 2
        self.B = self.larg(coupes_y(E, xm)[-1])                 # barre du haut
        V = g('V'); self.D = self.larg(coupes_x(V, self.CH - 3)[0])   # diagonale, mesurée à l'horizontale
        N = g('N'); self.DN = self.larg(coupes_x(N, self.CH / 2)[1])  # diagonale du N
        self.dH = self.hm['H'][1]; self.dV = self.hm['V'][1]; self.dO = self.hm['O'][1]
        # minuscules
        n = g('n'); v = g('v'); z = g('z')
        self.XH = bornes(v)[3]
        self.s = self.larg(coupes_x(n, 100)[0])
        zm = (bornes(z)[0] + bornes(z)[2]) / 2
        self.b = self.larg(coupes_y(z, zm)[-1])
        self.d = self.larg(coupes_x(v, self.XH - 3)[0])
        self.dn_ = self.DN * self.s / self.S
        self.dh = self.hm['n'][1]; self.dv = self.hm['v'][1]; self.do = self.hm['o'][1]
        self.ASC = bornes(g('l'))[3]; self.DESC = bornes(g('p'))[1]
        self.neufs = {}

    @staticmethod
    def larg(c): return c[1] - c[0]

    def lat(self, nom):
        p = pathops.Path(); self.gs[nom].draw(p.getPen(glyphSet=self.gs))
        return pathops.simplify(p, fix_winding=True)

    def chasse(self, nom): return self.hm[nom][0]

    # ---------- pièces ----------
    def anneau(self, nom, x0, y0, x1, y1, cote=None, haut=None):
        """Le rond (O ou o) remis dans une autre boîte, sans changer l'épaisseur du trait."""
        rp = RecordingPen(); self.gs[nom].draw(rp)
        cs = []; cur = []
        for op, a in rp.value:
            cur.append((op, a))
            if op == 'closePath': cs.append(cur); cur = []
        def bb(c):
            bp = BoundsPen(None)
            for op, a in c: getattr(bp, op)(*a)
            return bp.bounds
        cs.sort(key=lambda c: -(bb(c)[2] - bb(c)[0]))
        ext, itr = cs[0], cs[1]; be, bi = bb(ext), bb(itr)
        cote = cote if cote is not None else bi[0] - be[0]
        haut = haut if haut is not None else be[3] - bi[3]
        out = pathops.Path(); pen = out.getPen()
        for c, b, nb in ((ext, be, (x0, y0, x1, y1)), (itr, bi, (x0 + cote, y0 + haut, x1 - cote, y1 - haut))):
            fx = (nb[2] - nb[0]) / (b[2] - b[0]); fy = (nb[3] - nb[1]) / (b[3] - b[1])
            for op, a in c:
                getattr(pen, op)(*[((x - b[0]) * fx + nb[0], (y - b[1]) * fy + nb[1]) for x, y in a])
        return pathops.simplify(out, fix_winding=True)

    def pose(self, nom, code, p, chasse):
        self.neufs[nom] = (code, p, chasse)

    # ---------- les lettres ----------
    def dessine(self, variante='A'):
        for maj in (True, False):
            if maj:
                h, st, br, dg, dn = self.CH, self.S, self.B, self.D, self.DN
                aH, aV, aO = self.dH, self.dV, self.dO
                rH, rV, rO, rX = 'H', 'V', 'O', 'X'
            else:
                h, st, br, dg, dn = self.XH, self.s, self.b, self.d, self.dn_
                aH, aV, aO = self.dh, self.dv, self.do
                rH, rV, rO, rX = 'n', 'v', 'o', 'x'
            u = (lambda M, m: M if maj else m)
            wH = self.larg((bornes(self.lat(rH))[0], bornes(self.lat(rH))[2]))
            desc = round(h * 0.19)                       # les pieds de Д, Ц, Щ

            # И : deux fûts et la diagonale qui monte
            if maj:
                N = self.lat('N'); x0, _, x1, _ = bornes(N)
                p = transf(N, sx=-1, dx=x0 + x1)
                self.pose('uni0418', 0x418, p, self.chasse('N'))
            else:
                w = wH
                p = union(rect(0, 0, st, h), rect(w - st, 0, w, h),
                          poly((0, 0), (dn, 0), (w, h), (w - dn, h)))
                self.pose('uni0438', 0x438, transf(p, dx=aH), w + 2 * aH)

            # Л et Д
            V = self.lat(rV); vx0, _, vx1, _ = bornes(V); wV = vx1 - vx0
            if variante == 'A':
                lam = transf(V, sy=-1, dy=h, dx=-vx0)                    # le V retourné
                self.pose(u('uni041B', 'uni043B'), u(0x41B, 0x43B), transf(lam, dx=aV), wV + 2 * aV)
                deb = round(st * 0.30)                                    # la barre dépasse des jambes
                corps = transf(lam, dx=deb)
                pied = round(st * 0.92)
                wD = wV + 2 * deb
                p = union(corps, rect(0, 0, wD, br), rect(0, -desc, pied, br), rect(wD - pied, -desc, wD, br))
                self.pose(u('uni0414', 'uni0434'), u(0x414, 0x434), transf(p, dx=aV * 0.8), wD + 2 * aV * 0.8)
            else:
                w = round(wH * 0.98); xa = round(w * 0.20)
                jambe = poly((0, 0), (st, 0), (xa + st, h), (xa, h))
                p = union(jambe, rect(xa, h - br, w, h), rect(w - st, 0, w, h))
                self.pose(u('uni041B', 'uni043B'), u(0x41B, 0x43B), transf(p, dx=aV * 1.2), w + aV * 1.2 + aH)
                deb = round(st * 0.30); pied = round(st * 0.92)
                wD = w + 2 * deb; xa = round(w * 0.16)
                jambe = poly((deb, 0), (deb + st, 0), (deb + xa + st, h), (deb + xa, h))
                p = union(jambe, rect(deb + xa, h - br, deb + w, h), rect(deb + w - st, 0, deb + w, h),
                          rect(0, 0, wD, br), rect(0, -desc, pied, br), rect(wD - pied, -desc, wD, br))
                self.pose(u('uni0414', 'uni0434'), u(0x414, 0x434), transf(p, dx=aV * 0.8), wD + 2 * aV * 0.8)

            # Ф : le fût et l'anneau
            O = self.lat(rO); ox0, oy0, ox1, oy1 = bornes(O); wO = ox1 - ox0
            ho = coupes_y(O, (ox0 + ox1) / 2); epO = self.larg(ho[-1])
            if maj:
                ha = h * 0.70; y0 = (h - ha) / 2
                ep = min(epO, ha * 0.36)                                 # on garde un blanc dans les graisses noires
                wF = round(wO * 0.96); fut = st if ep == epO else st * 0.92
                p = union(self.anneau(rO, 0, y0, wF, y0 + ha, haut=ep), rect(wF / 2 - fut / 2, 0, wF / 2 + fut / 2, h))
                self.pose('uni0424', 0x424, transf(p, dx=aO), wF + 2 * aO)
            else:
                p = union(transf(O, dx=-ox0), rect(wO / 2 - st / 2, self.DESC, wO / 2 + st / 2, self.ASC))
                self.pose('uni0444', 0x444, transf(p, dx=aO), wO + 2 * aO)

            # У : la grande diagonale et le bras gauche
            if maj:
                w = wV * 0.94; xq = round(w * 0.16); yj = h * 0.36
                gd = poly((xq, 0), (xq + dg, 0), (w, h), (w - dg, h))
                xj = xq + (w - dg - xq) * yj / h                           # la grande diagonale à la hauteur yj
                bras = poly((0, h), (dg, h), (xj + dg, yj), (xj, yj))
                self.pose('uni0423', 0x423, transf(union(gd, bras), dx=aV), w + 2 * aV)

            # Ж : le X et son fût
            X = self.lat(rX); xx0, _, xx1, _ = bornes(X); wX = xx1 - xx0
            fut = st * (0.86 if maj else 0.86)
            p = union(transf(X, dx=-xx0), rect(wX / 2 - fut / 2, 0, wX / 2 + fut / 2, h))
            self.pose(u('uni0416', 'uni0436'), u(0x416, 0x436), transf(p, dx=self.hm[rX][1]), self.chasse(rX))

            # Ш : trois fûts sur une barre
            w = round(wH * 1.2)
            p = union(rect(0, 0, st, h), rect(w / 2 - st / 2, 0, w / 2 + st / 2, h), rect(w - st, 0, w, h), rect(0, 0, w, br))
            self.pose(u('uni0428', 'uni0448'), u(0x428, 0x448), transf(p, dx=aH), w + 2 * aH)

            # т minuscule : un petit T
            if not maj:
                w = round(wH * 0.9)
                p = union(rect(0, h - br, w, h), rect(w / 2 - st / 2, 0, w / 2 + st / 2, h))
                self.pose('uni0442', 0x442, transf(p, dx=aV * 1.3), w + 2 * aV * 1.3)

            if maj:
                # Я : le R en miroir
                R = self.lat('R'); x0, _, x1, _ = bornes(R)
                self.pose('uni042F', 0x42F, transf(R, sx=-1, dx=x0 + x1 + (self.chasse('R') - x1 - x0)), self.chasse('R'))
                # Б : le P retourné (Ь) et la barre du haut
                P = self.lat('P'); x0, _, x1, _ = bornes(P)
                p = union(transf(P, sy=-1, dy=h), rect(x0, h - br, x0 + (x1 - x0) * 0.90, h))
                self.pose('uni0411', 0x411, p, self.chasse('P'))

        # les lettres qui existent déjà en latin
        for code, lat in ((0x410, 'A'), (0x420, 'P'), (0x421, 'C'), (0x422, 'T'), (0x41E, 'O'), (0x401, 'Edieresis'),
                          (0x430, 'a'), (0x440, 'p'), (0x441, 'c'), (0x43E, 'o'), (0x451, 'edieresis'), (0x443, 'y')):
            self.neufs['uni%04X' % code] = (code, self.lat(lat), self.chasse(lat))

    def ecrit(self, sortie):
        t = self.t; glyf = t['glyf']; ordre = t.getGlyphOrder()
        for nom, (code, p, ch) in self.neufs.items():
            p = pathops.simplify(p, fix_winding=True)
            pen = TTGlyphPen(None)
            rp = RecordingPen(); p.draw(rp)
            # TrueType : le contour du dehors tourne dans le sens des aiguilles
            rp2 = RecordingPen(); rp.replay(ReverseContourPen(rp2))
            for op, a in rp2.value:
                getattr(pen, op)(*[None if q is None else (round(q[0]), round(q[1])) for q in a])
            g = pen.glyph()
            if nom not in ordre: ordre.append(nom)
            glyf[nom] = g
            g.recalcBounds(glyf)
            self.hm[nom] = (round(ch), g.xMin if g.numberOfContours else 0)
            for tb in t['cmap'].tables:
                if tb.isUnicode(): tb.cmap[code] = nom
        t.setGlyphOrder(ordre)
        t['maxp'].numGlyphs = len(ordre)
        t.save(sortie)


if __name__ == '__main__':
    g = Graisse(sys.argv[1])
    g.dessine(sys.argv[3] if len(sys.argv) > 3 else 'A')
    g.ecrit(sys.argv[2])
    print(sys.argv[2], len(g.neufs), 'signes')
