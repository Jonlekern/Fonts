# Cyrillique de Calebard : les lettres russes dessinées à partir des pièces latines de chaque graisse.
#
#   python3 cyrillique.py Calebard-Black.ttf sortie.ttf
#
# Chaque graisse est mesurée (fût, barre, diagonale, hauteurs, approches) puis les lettres sont
# construites avec ces mesures : les épaisseurs restent celles de la graisse.
# Л et Д sont droits, comme le П (version B, validée).
import sys, copy
from fontTools.ttLib.tables import otTables as ot
import pathops
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.recordingPen import RecordingPen, DecomposingRecordingPen
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
        getattr(pen, op)(*[None if q is None else (q[0] * sx + dx, q[1] * sy + dy) for q in a])
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


# ---------- outils sur les contours bruts (on garde les points de courbe d'origine) ----------
def chemin(rec):
    p = pathops.Path(); pen = p.getPen()
    for op, a in rec: getattr(pen, op)(*a)
    return pathops.simplify(p, fix_winding=True)

def bouge(rec, f):
    return [(op, tuple(f(q) for q in a)) for op, a in rec]

def carte(k, v):
    """Carte par morceaux : chaque (ancien, nouveau) est un repère, on glisse droit entre deux repères."""
    if v <= k[0][0]: return v + k[0][1] - k[0][0]
    if v >= k[-1][0]: return v + k[-1][1] - k[-1][0]
    for (a, A), (b, B) in zip(k, k[1:]):
        if a <= v <= b: return A if b == a else A + (v - a) * (B - A) / (b - a)

def recale(rec, kx=None, ky=None):
    """Déplace les traits sans changer leur épaisseur : seuls les blancs entre deux repères s'étirent."""
    return bouge(rec, lambda q: (carte(kx, q[0]) if kx else q[0], carte(ky, q[1]) if ky else q[1]))

def droites(rec):
    """Les segments droits horizontaux et verticaux d'un contour."""
    H = []; V = []; cur = dep = None
    def seg(p, q):
        if p[1] == q[1] and p[0] != q[0]: H.append((min(p[0], q[0]), max(p[0], q[0]), p[1]))
        if p[0] == q[0] and p[1] != q[1]: V.append((min(p[1], q[1]), max(p[1], q[1]), p[0]))
    for op, a in rec:
        if op == 'moveTo': cur = dep = a[0]
        elif op == 'lineTo': seg(cur, a[0]); cur = a[0]
        elif op in ('qCurveTo', 'curveTo'): cur = a[-1]
        elif op == 'closePath': seg(cur, dep)
    return H, V

def zone_x(rec, xfut, mini):
    """La zone où toutes les barres sont droites, à droite du fût : on peut y raccourcir la lettre sans toucher aux courbes."""
    H, _ = droites(rec); H = [h for h in H if h[0] <= xfut + 1 and h[1] >= xfut + mini]
    return xfut, min(h[1] for h in H)

def zone_y(rec, mini):
    _, V = droites(rec); bas = min(v[0] for v in V)
    V = [v for v in V if v[1] - v[0] >= mini and v[0] <= bas + 1]          # les fûts qui partent du pied
    return bas, min(v[1] for v in V)


# ---------- crénage : chaque lettre russe reprend le crénage d'une lettre latine qui a le même bord ----------
# code : (jumelle du bord gauche, jumelle du bord droit)
JUMELLES = {
    0x410: 'AA', 0x411: ('H', 'B'), 0x412: 'BB', 0x413: ('H', 'F'), 0x414: 'HH', 0x415: 'EE', 0x401: 'EE',
    0x416: 'XX', 0x417: ('three', 'B'), 0x418: 'HH', 0x419: 'HH', 0x41A: 'KK', 0x41B: 'AH', 0x41C: 'MM',
    0x41D: 'HH', 0x41E: 'OO', 0x41F: 'HH', 0x420: 'PP', 0x421: 'CC', 0x422: 'TT', 0x423: 'YY', 0x424: 'OO',
    0x425: 'XX', 0x426: 'HH', 0x427: 'UH', 0x428: 'HH', 0x429: 'HH', 0x42A: 'TB', 0x42B: 'HH', 0x42C: 'HB',
    0x42D: 'OO', 0x42E: 'HO', 0x42F: 'HH',
    0x430: 'aa', 0x431: 'oo', 0x432: 'nb', 0x433: 'nr', 0x434: 'nn', 0x435: 'ee', 0x451: 'ee', 0x436: 'xx',
    0x437: 'zo', 0x438: 'nn', 0x439: 'nn', 0x43A: 'kk', 0x43B: 'vn', 0x43C: 'nn', 0x43D: 'nn', 0x43E: 'oo',
    0x43F: 'nn', 0x440: 'pp', 0x441: 'cc', 0x442: 'zz', 0x443: 'yy', 0x444: 'oo', 0x445: 'xx', 0x446: 'nn',
    0x447: 'un', 0x448: 'nn', 0x449: 'nn', 0x44A: 'zb', 0x44B: 'nn', 0x44C: 'nb', 0x44D: 'oo', 0x44E: 'no',
    0x44F: 'nn',
}

def crenage(t, jum):
    """jum : {glyphe : (jumelle gauche, jumelle droite)}. Copie le crénage des jumelles latines."""
    gid = t.getReverseGlyphMap(rebuild=True)
    for lk in t['GPOS'].table.LookupList.Lookup:
        for st in lk.SubTable:
            st = st.ExtSubTable if lk.LookupType == 9 else st
            if not hasattr(st, 'Coverage') or lk.LookupType not in (2, 9): continue
            if st.Format == 1 and hasattr(st, 'PairSet'):
                for ps in st.PairSet:                                       # la lettre russe en second
                    extra = []
                    for r in ps.PairValueRecord:
                        for g, (L, R) in jum.items():
                            if r.SecondGlyph == L:
                                r2 = copy.deepcopy(r); r2.SecondGlyph = g; extra.append(r2)
                    ps.PairValueRecord = sorted([r for r in ps.PairValueRecord if r.SecondGlyph not in jum] + extra,
                                                key=lambda r: gid[r.SecondGlyph]); ps.PairValueCount = len(ps.PairValueRecord)
                pairs = [(g, ps) for g, ps in zip(st.Coverage.glyphs, st.PairSet) if g not in jum]
                d = dict(pairs)                                             # la lettre russe en premier
                pairs += [(g, copy.deepcopy(d[R])) for g, (L, R) in jum.items() if R in d]
                pairs.sort(key=lambda p: gid[p[0]])
                st.Coverage.glyphs = [g for g, _ in pairs]; st.PairSet = [ps for _, ps in pairs]; st.PairSetCount = len(pairs)
            elif st.Format == 2 and hasattr(st, 'ClassDef1'):
                cov = set(st.Coverage.glyphs)
                for g, (L, R) in jum.items():
                    for cd, j in ((st.ClassDef1, R), (st.ClassDef2, L)):
                        cd.classDefs.pop(g, None)
                        if j in cd.classDefs: cd.classDefs[g] = cd.classDefs[j]
                    if R in cov: cov.add(g)
                st.Coverage.glyphs = sorted(cov, key=gid.get)

def cyrl(t, neufs):
    """Le script cyrillique dans GSUB et GPOS (les mêmes fonctions que DFLT), GDEF, OS/2."""
    for tag in ('GSUB', 'GPOS'):
        sl = t[tag].table.ScriptList
        if any(sr.ScriptTag == 'cyrl' for sr in sl.ScriptRecord): continue
        dflt = [sr for sr in sl.ScriptRecord if sr.ScriptTag == 'DFLT'][0]
        sr = ot.ScriptRecord(); sr.ScriptTag = 'cyrl'; sr.Script = ot.Script()
        sr.Script.DefaultLangSys = copy.deepcopy(dflt.Script.DefaultLangSys)
        sr.Script.LangSysRecord = []; sr.Script.LangSysCount = 0
        sl.ScriptRecord = sorted(sl.ScriptRecord + [sr], key=lambda r: r.ScriptTag); sl.ScriptCount = len(sl.ScriptRecord)
    if 'GDEF' in t and t['GDEF'].table.GlyphClassDef:
        for g in neufs: t['GDEF'].table.GlyphClassDef.classDefs[g] = 1
    os2 = t['OS/2']
    os2.ulUnicodeRange1 |= 1 << 9                                           # cyrillique
    os2.ulCodePageRange1 |= 1 << 2                                          # page de code 1251


class Graisse:
    def __init__(self, chemin, pente=0.0):
        self.pente = pente                                   # pente en plus sur la jambe de Л et Д (Goofy penché à gauche)
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
        # la structure à trois barres des minuscules : celle du e
        e = g('e'); ex = (bornes(e)[0] + bornes(e)[2]) / 2; eb = coupes_y(e, ex)
        self.tb = self.larg(eb[0]); self.m0, self.m1 = eb[1]; self.tt = self.larg(eb[2])
        hb = coupes_y(H, (bornes(H)[0] + bornes(H)[2]) / 2)[0]
        self.tH = self.larg(hb); self.cH = (hb[0] + hb[1]) / 2 / self.CH       # barre du H
        self.kT = self.hm['T'][1] / self.dH                                      # approche d'une barre qui dépasse
        self.rn = self.hm['n'][0] - bornes(n)[2]
        self.neufs = {}

    @staticmethod
    def larg(c): return c[1] - c[0]

    def lat(self, nom):
        p = pathops.Path(); self.gs[nom].draw(p.getPen(glyphSet=self.gs))
        return pathops.simplify(p, fix_winding=True)

    def chasse(self, nom): return self.hm[nom][0]

    def brut(self, nom):
        rp = DecomposingRecordingPen(self.gs); self.gs[nom].draw(rp)
        return rp.value

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
    def dessine(self):
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
            if True:
                w = round(wH * 0.98); xa = round(w * 0.20 + self.pente * h)
                jambe = poly((0, 0), (st, 0), (xa + st, h), (xa, h))
                p = union(jambe, rect(xa, h - br, w, h), rect(w - st, 0, w, h))
                self.pose(u('uni041B', 'uni043B'), u(0x41B, 0x43B), transf(p, dx=aV * 1.2), w + aV * 1.2 + aH)
                deb = round(wH * 0.05 + st * 0.20); pied = round(st * 0.92)
                wD = w + 2 * deb; xa = round(w * 0.16 + self.pente * h)
                jambe = poly((deb, 0), (deb + st, 0), (deb + xa + st, h), (deb + xa, h))
                p = union(jambe, rect(deb + xa, h - br, deb + w, h), rect(deb + w - st, 0, deb + w, h),
                          rect(0, 0, wD, br), rect(0, -desc, pied, br), rect(wD - pied, -desc, wD, br))
                self.pose(u('uni0414', 'uni0434'), u(0x414, 0x434), transf(p, dx=aV * 0.8), wD + 2 * aV * 0.8)

            # Ф : le fût et l'anneau
            O = self.lat(rO); ox0, oy0, ox1, oy1 = bornes(O); wO = ox1 - ox0
            ho = coupes_y(O, (ox0 + ox1) / 2); epO = self.larg(ho[-1])
            if maj:
                ha = h * 0.74; y0 = (h - ha) / 2
                ep = min(epO, ha * 0.36)                                 # on garde un blanc dans les graisses noires
                wF = round(wO * 0.96); fut = st if ep == epO else st * 0.92
                cote = min(self.larg(coupes_x(O, (oy0 + oy1) / 2)[0]), st * 0.78)
                p = union(self.anneau(rO, 0, y0, wF, y0 + ha, cote=cote, haut=ep), rect(wF / 2 - fut / 2, 0, wF / 2 + fut / 2, h))
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
            fut = st * (0.86 - 0.30 * (st / 700) ** 2)              # le fût s'affine dans les graisses noires
            p = union(transf(X, dx=-xx0), rect(wX / 2 - fut / 2, 0, wX / 2 + fut / 2, h))
            self.pose(u('uni0416', 'uni0436'), u(0x416, 0x436), transf(p, dx=self.hm[rX][1]), self.chasse(rX))

            # Ш : trois fûts sur une barre
            w = round(wH * 1.2)
            p = union(rect(0, 0, st, h), rect(w / 2 - st / 2, 0, w / 2 + st / 2, h), rect(w - st, 0, w, h), rect(0, 0, w, br))
            self.pose(u('uni0428', 'uni0448'), u(0x428, 0x448), transf(p, dx=aH), w + 2 * aH)

            if maj:
                # Я : le R en miroir
                R = self.lat('R'); x0, _, x1, _ = bornes(R)
                self.pose('uni042F', 0x42F, transf(R, sx=-1, dx=x0 + x1 + (self.chasse('R') - x1 - x0)), self.chasse('R'))

        # les lettres qui existent déjà en latin
        for code, lat in ((0x410, 'A'), (0x420, 'P'), (0x421, 'C'), (0x422, 'T'), (0x41E, 'O'), (0x401, 'Edieresis'),
                          (0x430, 'a'), (0x440, 'p'), (0x441, 'c'), (0x43E, 'o'), (0x451, 'edieresis'), (0x443, 'y')):
            self.neufs['uni%04X' % code] = (code, self.lat(lat), self.chasse(lat))

    def minuscules(self):
        """Les 33 minuscules russes (л д и ж ф ш sont déjà dans dessine)."""
        h, st, br = self.XH, self.s, self.b
        n = self.lat('n'); wn = bornes(n)[2] - bornes(n)[0]
        g, d = self.dh, self.rn                              # approches d'un fût, à gauche et à droite
        m0, m1, tb, tt = self.m0, self.m1, self.tb, self.tt
        def pose(code, p, chasse): self.pose('uni%04X' % code, code, p, chasse)
        def droit(code, p, w, ag=1.0, ad=1.0): pose(code, transf(p, dx=g * ag), w + g * ag + d * ad)

        # г п н м т ц щ : des fûts et des barres
        w = round(wn * 0.72)
        droit(0x433, union(rect(0, 0, st, h), rect(0, h - br, w, h)), w, ad=self.kT)
        w = wn
        droit(0x43F, union(rect(0, 0, st, h), rect(w - st, 0, w, h), rect(0, h - br, w, h)), w)
        w = round(wn * 1.02); c = self.cH * h
        droit(0x43D, union(rect(0, 0, st, h), rect(w - st, 0, w, h), rect(0, c - self.tH / 2, w, c + self.tH / 2)), w)
        for code, lat, miroir, coef in ((0x43C, 'M', False, 0.90), (0x438, 'N', True, 0.92)):
            M = self.brut(lat); pM = chemin(M); x0, y0, x1, y1 = bornes(pM); wm = (x1 - x0) * coef
            kx = [(x0, x0), (x0 + self.S, x0 + st), (x1 - self.S, x0 + wm - st), (x1, x0 + wm)]
            M = recale(M, kx, [(0, 0), (self.CH, h)])
            if miroir: M = bouge(M, lambda q: (2 * x0 + wm - q[0], q[1]))
            pose(code, transf(chemin(M), dx=g - x0), wm + g + d)
        w = round(wn * 0.9)
        droit(0x442, union(rect(0, h - br, w, h), rect(w / 2 - st / 2, 0, w / 2 + st / 2, h)), w, ag=self.kT, ad=self.kT)
        desc = round(h * 0.19); dep = round(wn * 0.07 + st * 0.25); pied = round(st * 0.80)
        w = wn
        droit(0x446, union(rect(0, 0, st, h), rect(w - st, 0, w, h), rect(0, 0, w + dep, br),
                           rect(w + dep - pied, -desc, w + dep, br)), w + dep, ad=0.6)
        w = round(wn * 1.2)
        droit(0x449, union(rect(0, 0, st, h), rect(w / 2 - st / 2, 0, w / 2 + st / 2, h), rect(w - st, 0, w, h),
                           rect(0, 0, w + dep, br), rect(w + dep - pied, -desc, w + dep, br)), w + dep, ad=0.6)

        # к : le k coupé à la hauteur des minuscules
        pose(0x43A, inter(self.lat('k'), rect(-9000, -9000, 9000, h)), self.chasse('k'))

        # в : le B ramené à la hauteur des minuscules, avec les trois barres du e
        B = self.brut('B'); pB = chemin(B); x0, _, x1, H = bornes(pB)
        za, zb = zone_x(B, x0 + self.S, (x1 - x0) * 0.15); xc = (za + zb) / 2
        bb = coupes_y(pB, xc)
        ky = [(0, 0), (bb[0][1], tb), (bb[1][0], m0), (bb[1][1], m1), (bb[2][0], h - tt), (H, h)]
        dx = min((x1 - x0) * 0.10, zb - za - 40)
        kx = [(za + 10, za + 10), (za + 10 + dx, za + 10)]
        ve = chemin(recale(B, kx, ky))
        pose(0x432, ve, self.chasse('B') - dx)

        # ь ъ ы : le P retourné, sa panse à la hauteur de la panse basse du в
        P = bouge(self.brut('P'), lambda q: (q[0], self.CH - q[1])); pP = chemin(P); x0, _, x1, H = bornes(pP)
        za, zb = zone_x(P, x0 + self.S, (x1 - x0) * 0.15); xc = (za + zb) / 2
        bb = coupes_y(pP, xc)
        ky = [(0, 0), (bb[0][1], tb), (bb[1][0], m0), (bb[1][1], m1), (H, h)]
        def mou(coef):
            dx = min((x1 - x0) * coef, zb - za - 40)
            return chemin(recale(P, [(za + 10, za + 10), (za + 10 + dx, za + 10)], ky)), dx
        p, dx = mou(0.14); rP = self.chasse('P') - x1
        pose(0x44C, p, self.chasse('P') - dx)
        drap = round(wn * 0.13 + st * 0.3)                                   # le drapeau du ъ
        pose(0x44A, transf(union(p, rect(x0 - drap, h - br, x0 + st, h)), dx=drap * 0.8), self.chasse('P') - dx + drap * 0.8)
        p, dx = mou(0.30); wb = x1 - dx; esp = round(wn * 0.07 + st * 0.35)
        pose(0x44B, union(p, rect(wb + esp, 0, wb + esp + st, h)), wb + esp + st + d)

        # я : le R en miroir
        R0 = self.brut('R'); pR = chemin(R0); x0, _, x1, H = bornes(pR)
        za, zb = zone_x(R0, x0 + self.S, (x1 - x0) * 0.15); xc = (za + zb) / 2
        bb = coupes_y(pR, xc)[-2:]
        ky = [(0, 0), (bb[0][0], m0), (bb[0][1], m1), (bb[1][0], h - tt), (H, h)]
        dx = min((x1 - x0) * 0.10, zb - za - 40)
        R = recale(R0, [(za + 10, za + 10), (za + 10 + dx, za + 10)], ky)
        p = chemin(bouge(R, lambda q: (x0 + x1 - q[0], q[1])))
        rR = self.chasse('R') - x1
        pose(0x44F, transf(p, dx=rR - x0 * 0 - bornes(p)[0]), bornes(p)[2] - bornes(p)[0] + rR + g)

        # з : le 3 ramené à la hauteur des minuscules
        T = self.brut('three'); pT = chemin(T); x0, y0, x1, y1 = bornes(pT)
        bb = coupes_y(pT, x0 + (x1 - x0) * 0.62); bas, haut = bb[0], bb[-1]; mil = (bb[1][0], bb[-2][1])
        ky = [(bas[0], -10), (bas[1], -10 + tb), (mil[0], m0), (mil[1], m1), (haut[0], h + 10 - tt), (haut[1], h + 10)]
        pose(0x437, chemin(recale(T, None, ky)), self.chasse('three'))

        # б : le 6, sa panse à la hauteur du o, sa tête à la hauteur des montantes
        S6 = self.brut('six'); p6 = chemin(S6); x0, y0, x1, y1 = bornes(p6)
        bb = coupes_y(p6, (x0 + x1) / 2)
        ept = self.larg(bb[2]); jour = (bb[2][0] - bb[1][1]) * 0.6           # le blanc entre la panse et la tête
        tete = min(self.ASC + 20, max(self.ASC - 60, h + 10 + jour + ept))
        ept = min(ept, tete - (h + 10 + jour))                                # la tête s'affine si la place manque
        ky = [(bb[0][0], -10), (bb[0][1], -10 + self.larg(bb[0])), (bb[1][0], h + 10 - self.larg(bb[1])), (bb[1][1], h + 10),
              (bb[2][0], tete - ept), (bb[2][1], tete)]
        pose(0x431, chemin(recale(S6, None, ky)), self.chasse('six'))

        # ч : le h retourné, l'arche remontée
        Hh = self.brut('h'); ph = chemin(Hh); x0, _, x1, _ = bornes(ph)
        ya, yb = zone_y(Hh, h * 0.2)
        dy = min(h * 0.40, yb - ya - 30)
        Hh = recale(Hh, None, [(ya + 10, ya + 10), (ya + 10 + dy, ya + 10)])
        p = chemin(bouge(Hh, lambda q: (x0 + x1 - q[0], h - q[1])))
        fa, fb = coupes_x(p, bornes(p)[1] + 5)[-1]                 # le fût, tel qu'il est dans le h
        p = inter(union(p, rect(fa, 0, fb, bornes(p)[1] + 40)), rect(-9000, 0, 9000, 9000))
        ch = self.chasse('h')
        pose(0x447, transf(p, dx=(ch - x1) - x0), ch)

        # э : le c en miroir et sa barre
        C = self.lat('c'); x0, _, x1, _ = bornes(C)
        blanc = coupes_y(C, (x0 + x1) / 2); blanc = blanc[-1][0] - blanc[0][1]
        ep = min(self.m1 - self.m0, blanc * 0.36); cy = (blanc_c := (coupes_y(C, (x0 + x1) / 2)[0][1] + coupes_y(C, (x0 + x1) / 2)[-1][0]) / 2)
        cote = self.larg(coupes_x(C, cy)[0])
        p = union(transf(C, sx=-1, dx=x0 + x1), rect(x0 + (x1 - x0) * 0.42, cy - ep / 2, x1 - cote / 2, cy + ep / 2))
        rc = self.chasse('c') - x1
        pose(0x44D, transf(p, dx=rc - x0), self.chasse('c'))

        # ю : un fût, une barre, un o plus étroit
        O = self.lat('o'); x0, y0, x1, y1 = bornes(O); wo = (x1 - x0) * 0.76
        esp = round(wn * 0.07 + st * 0.3); xo = st + esp; c = self.cH * h
        cote = self.larg(coupes_x(O, (y0 + y1) / 2)[0])
        p = union(rect(0, 0, st, h), rect(0, c - self.tH / 2, xo + cote / 2, c + self.tH / 2),
                  self.anneau('o', xo, y0, xo + wo, y1))
        pose(0x44E, transf(p, dx=g), xo + wo + g + (self.chasse('o') - x1))

        # й : le и et sa brève
        comp = self.t['glyf']['abreve']
        if comp.isComposite():
            nomb, bx, by = [(k.glyphName, k.x, k.y) for k in comp.components][-1]
            br_ = transf(self.lat(nomb), dx=bx, dy=by)
            a = self.lat('a'); ca = (bornes(a)[0] + bornes(a)[2]) / 2; cb = (bornes(br_)[0] + bornes(br_)[2]) / 2
            _, pi, chi = self.neufs['uni0438']; ci = (bornes(pi)[0] + bornes(pi)[2]) / 2
            pose(0x439, union(pi, transf(br_, dx=ci - cb + (cb - ca))), chi)

        # celles qui existent déjà en latin
        for code, lat in ((0x430, 'a'), (0x435, 'e'), (0x451, 'edieresis'), (0x43E, 'o'), (0x440, 'p'), (0x441, 'c'),
                          (0x443, 'y'), (0x445, 'x')):
            pose(code, self.lat(lat), self.chasse(lat))

    def capitales(self):
        """Les 33 capitales russes (И Л Д Ф У Ж Ш Я sont déjà dans dessine)."""
        h, st, br = self.CH, self.S, self.B
        Hl = self.lat('H'); hx0, _, hx1, _ = bornes(Hl); wH = hx1 - hx0
        g, d = self.dH, self.chasse('H') - hx1
        def pose(code, p, chasse): self.pose('uni%04X' % code, code, p, chasse)
        def droit(code, p, w, ag=1.0, ad=1.0): pose(code, transf(p, dx=g * ag), w + g * ag + d * ad)
        # les trois barres du B : le modèle des panses
        B = self.brut('B'); pB = chemin(B); bx0, _, bx1, _ = bornes(pB)
        za, zb = zone_x(B, bx0 + st, (bx1 - bx0) * 0.15)
        bB = coupes_y(pB, (za + zb) / 2)
        tb, (m0, m1), tt = bB[0][1], bB[1], h - bB[2][0]
        desc = round(h * 0.19); dep = round(wH * 0.06 + st * 0.25); pied = round(st * 0.85)

        # П Ц Щ : des fûts et des barres
        droit(0x41F, union(rect(0, 0, st, h), rect(wH - st, 0, wH, h), rect(0, h - br, wH, h)), wH)
        droit(0x426, union(rect(0, 0, st, h), rect(wH - st, 0, wH, h), rect(0, 0, wH + dep, br),
                           rect(wH + dep - pied, -desc, wH + dep, br)), wH + dep, ad=0.6)
        w = round(wH * 1.2)
        droit(0x429, union(rect(0, 0, st, h), rect(w / 2 - st / 2, 0, w / 2 + st / 2, h), rect(w - st, 0, w, h),
                           rect(0, 0, w + dep, br), rect(w + dep - pied, -desc, w + dep, br)), w + dep, ad=0.6)

        # Г : le fût et le bras du haut du E
        Ee = self.lat('E'); ex0 = bornes(Ee)[0]
        bras = inter(Ee, rect(-9000, h - br - 1, 9000, 9000)); xb = bornes(bras)[2]
        p = union(bras, rect(ex0, 0, ex0 + st, h))
        pose(0x413, p, xb + g * self.kT)

        # Ь Ъ Ы Б : le P retourné, sa panse à la hauteur de la panse basse du B
        P = bouge(self.brut('P'), lambda q: (q[0], h - q[1])); pP = chemin(P); x0, _, x1, H = bornes(pP)
        za, zb = zone_x(P, x0 + st, (x1 - x0) * 0.15)
        bb = coupes_y(pP, (za + zb) / 2)
        ky = [(0, 0), (bb[0][1], tb), (bb[1][0], m0), (bb[1][1], m1), (H, h)]
        def mou(coef):
            dx = min((x1 - x0) * coef, zb - za - 40)
            return chemin(recale(P, [(za + 10, za + 10), (za + 10 + dx, za + 10)], ky)), dx
        p, dx = mou(0.10)
        pose(0x42C, p, self.chasse('P') - dx)
        pose(0x411, union(p, rect(x0, h - tt, x0 + (x1 - dx - x0) * 0.92, h)), self.chasse('P') - dx)
        drap = round(wH * 0.11 + st * 0.3)
        pose(0x42A, transf(union(p, rect(x0 - drap, h - br, x0 + st, h)), dx=drap * 0.8), self.chasse('P') - dx + drap * 0.8)
        p, dx = mou(0.26); wb = x1 - dx; esp = round(wH * 0.06 + st * 0.35)
        pose(0x42B, union(p, rect(wb + esp, 0, wb + esp + st, h)), wb + esp + st + d)

        # Ч : le U remonté, coupé, avec le fût de droite jusqu'en bas
        U = self.lat('U'); ux0, uy0, ux1, _ = bornes(U)
        p = inter(transf(U, dy=h * 0.40 - uy0), rect(-9000, 0, 9000, h))
        fa, fb = coupes_x(p, h - 5)[-1]
        p = union(p, rect(fa, 0, fb, h))
        pose(0x427, p, self.chasse('U'))

        # Э : le C en miroir et sa barre
        C = self.lat('C'); x0, _, x1, _ = bornes(C)
        cc = coupes_y(C, (x0 + x1) / 2); cy = (cc[0][1] + cc[-1][0]) / 2
        ep = min(m1 - m0, (cc[-1][0] - cc[0][1]) * 0.36)
        cote = self.larg(coupes_x(C, cy)[0])
        p = union(transf(C, sx=-1, dx=x0 + x1), rect(x0 + (x1 - x0) * 0.40, cy - ep / 2, x1 - cote / 2, cy + ep / 2))
        rc = self.chasse('C') - x1
        pose(0x42D, transf(p, dx=rc - x0), self.chasse('C'))

        # Ю : un fût, une barre, un O plus étroit
        O = self.lat('O'); x0, y0, x1, y1 = bornes(O); wo = (x1 - x0) * 0.76
        esp = round(wH * 0.06 + st * 0.3); xo = st + esp; c = self.cH * h
        cote = self.larg(coupes_x(O, (y0 + y1) / 2)[0])
        p = union(rect(0, 0, st, h), rect(0, c - self.tH / 2, xo + cote / 2, c + self.tH / 2),
                  self.anneau('O', xo, y0, xo + wo, y1))
        pose(0x42E, transf(p, dx=g), xo + wo + g + (self.chasse('O') - x1))

        # Й : le И et la brève des capitales
        comp = self.t['glyf']['Abreve']
        if comp.isComposite():
            nomb, bx, by = [(k.glyphName, k.x, k.y) for k in comp.components][-1]
            br_ = transf(self.lat(nomb), dx=bx, dy=by)
            a = self.lat('A'); ca = (bornes(a)[0] + bornes(a)[2]) / 2; cb = (bornes(br_)[0] + bornes(br_)[2]) / 2
            _, pi, chi = self.neufs['uni0418']; ci = (bornes(pi)[0] + bornes(pi)[2]) / 2
            pose(0x419, union(pi, transf(br_, dx=ci - cb + (cb - ca))), chi)

        # celles qui existent déjà en latin
        for code, lat in ((0x410, 'A'), (0x412, 'B'), (0x415, 'E'), (0x401, 'Edieresis'), (0x417, 'three'), (0x41A, 'K'),
                          (0x41C, 'M'), (0x41D, 'H'), (0x41E, 'O'), (0x420, 'P'), (0x421, 'C'), (0x422, 'T'), (0x425, 'X')):
            pose(code, self.lat(lat), self.chasse(lat))

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
        cyrl(t, self.neufs)
        jum = {}
        for nom, (code, _, _) in self.neufs.items():
            L, R = JUMELLES[code]; jum[nom] = (L, R)
        crenage(t, jum)
        t['OS/2'].recalcAvgCharWidth(t)
        t.save(sortie)


if __name__ == '__main__':
    g = Graisse(sys.argv[1])
    g.dessine(); g.minuscules(); g.capitales()
    g.ecrit(sys.argv[2])
    print(sys.argv[2], len(g.neufs), 'signes')
