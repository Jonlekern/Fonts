# Nexum : le reste du jeu GF Latin Core (accents, lettres en plus, signes), dans la recette.
import sys, os, math, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import nexum as techno
import arrondi, triche
import accents as AC
S, path = techno.S, techno.path
H, X, A_, D_ = 1000.0, techno.XH, techno.ASC, techno.DESC
T67 = techno.T67

MARQUES = {0x300: 'grave', 0x301: 'aigu', 0x302: 'circonflexe', 0x303: 'tilde', 0x304: 'macron', 0x306: 'breve',
           0x307: 'point', 0x308: 'trema', 0x30A: 'rond', 0x30B: 'double', 0x30C: 'caron',
           0x326: 'virgule', 0x327: 'cedille', 0x328: 'ogonek'}
HAUT = {'grave', 'aigu', 'circonflexe', 'tilde', 'macron', 'breve', 'point', 'trema', 'rond', 'double', 'caron'}
VIRGULE_DESSOUS = set('ĶķĻļŅņĢ')          # en letton : virgule sous la lettre, pas de cédille
APOSTROPHE = set('ďľť')                     # caron en virgule à droite du fût

def det(sts):
    return [dict(st, detail=True) for st in sts]

def tr(sts, dx=0.0, dy=0.0, sx=1.0, sy=1.0, cx=0.0, cy=0.0):
    return [dict(st, p=[np.array([(x - cx) * sx + cx + dx, (y - cy) * sy + cy + dy]) for x, y in st['p']],
                 caps=list(st['caps'])) for st in sts]

def boite(sts, ymin=-1e9, ymax=1e9):
    P = np.vstack([np.array(st['p']) for st in sts])
    m = (P[:, 1] >= ymin) & (P[:, 1] <= ymax)
    P = P[m] if m.any() else P
    return P[:, 0].min(), P[:, 1].min(), P[:, 0].max(), P[:, 1].max()

def centre(sts):
    x0, _, x1, _ = boite(sts)
    return (x0 + x1) / 2

# ---------- formes des accents (centrés en cx, bas en y0) ----------
ECART_DOUBLE = [75.0]

def forme(nom, cx, y0, h):
    if nom in ('grave', 'aigu', 'circonflexe', 'caron', 'trema', 'point', 'rond', 'tilde', 'macron', 'breve'):
        return AC.accent(nom, cx, y0, h=h)
    if nom == 'double':
        e = ECART_DOUBLE[0]
        return AC.accent('aigu', cx - e, y0, h=h) + AC.accent('aigu', cx + e, y0, h=h)
    raise ValueError(nom)

def cedille(cx):
    return [S((cx, 30), (cx, -150, 60), (cx - 120, -150)), S((cx - 95, -60), (cx - 95, -230))]

def ogonek(x):
    return [S((x, 30), (x, -150, 70), (x + 130, -150))]

def virgule_dessous(cx, y=-130, s=60):
    return [S((cx + 40, y + s), (cx - 60, y - 170)), S((cx - s, y), (cx + s, y))]

def virgule_haute(x, y, s=55):          # ď ľ ť : petite virgule en dague à droite du fût
    return [S((x + 40, y + s), (x - 50, y - 150)), S((x - s, y), (x + s, y))]

def virgule_retournee(cx, y, s=55):     # ģ : virgule retournée au-dessus
    return [S((cx - 40, y - s), (cx + 60, y + 170)), S((cx - s, y), (cx + s, y))]

# ---------- lettres en plus ----------
def nouvelles_lettres(G0, ov, ovl):
    """G0 : traits de la graisse, sans l'élargissement. Retourne les lettres de base en plus."""
    N = {}
    f = ov / 70.0; fl = ovl / 70.0
    N['ı'] = G0['i'][:3]          # i sans son point en croix
    N['ȷ'] = G0['j'][:3]
    N['Ł'] = G0['L'] + [S((-130, 360), (190, 680))]
    N['ł'] = G0['l'] + [S((-120, 420), (140, 680))]
    N['Đ'] = G0['D'] + [S((-170, 500), (250, 500))]
    N['Ð'] = N['Đ']
    N['đ'] = G0['d'] + [S((420 - 140, 830), (420 + 170, 830))]
    N['Ħ'] = G0['H'] + [S((-ov, 760), (540 + ov, 760))]
    N['ħ'] = G0['h'] + [S((-140, 830), (200, 830))]
    N['Þ'] = [S((0, H + ov), (0, -ov)), S((-150, H), (150, H)), S((-150, 0), (150, 0)),
              S((-ov, 780), (480, 780, 230), (480, 230, 230), (-ov, 230))]
    N['þ'] = [S((0, A_ + ovl), (0, D_ - ovl)), S((-150, A_), (150, A_)), S((-150, D_), (150, D_)),
              S((-ovl, X), (420, X, 200), (420, 0, 200), (-ovl, 0))]
    N['ß'] = [S((0, 0), (0, A_, 170), (380, A_, 150), (380, 640), (170, 640)),
              S((170 - ovl, 640), (430, 640, 170), (430, 0, 170), (60, 0)),
              S((-150, 0), (150, 0))]
    N['ẞ'] = [S((0, H + ov), (0, -ov)), S((-150, 0), (150, 0)), S((-ov, H), (480, H)),
              S((480, H), (230, 590)), S((230 - ov, 590), (500, 590, 220), (500, 0, 220), (60, 0))]
    ax = H / T67
    N['Æ'] = [S((0, 0), (ax + ov * techno.C67, H + ov * techno.S67)), S((ax, H + ov), (ax, -ov)),
              S((ax - ov, H), (ax + 520, H)), dict(S((ax + 520 - 30 * f, H + 70 * f), (ax + 520 - 30 * f, H - 110 * f)), detail=True),
              S((ax - ov, 510), (ax + 420, 510)), S((ax - ov, 0), (ax + 540, 0)),
              S((350 / T67 - 90, 350), (ax + 60, 350)), S((-150, 0), (150, 0))]
    e = G0['e']
    N['æ'] = G0['a'] + tr(e, dx=360)
    N['Œ'] = arrondi.ogive(over=ov) + tr(G0['E'], dx=560)
    N['œ'] = G0['o'] + tr(e, dx=410)
    N['Ø'] = G0['O'] + AC.barre_o(315, 500, 1150)
    N['ø'] = G0['o'] + AC.barre_o(220, 300, 700)
    N['ð'] = G0['o'] + [S((330, 560), (150, A_)), S((80, 860), (380, 860))]
    N['ª'] = det(tr(G0['a'], sx=0.55, sy=0.55, dy=560) + [S((-20, 470), (320, 470))])
    N['º'] = det(tr(G0['o'], sx=0.55, sy=0.55, dy=560) + [S((0, 470), (260, 470))])
    return N

# ---------- signes ----------
def signes(G0, P, ov, ovl, hacc, yacc):
    """P : ponctuation déjà dessinée (pour la virgule, le point…)."""
    Z = {}
    f = ov / 70.0
    Z['$'] = G0['S'] + [S((280, H + ov), (280, -ov))]
    Z['<'] = AC_chevron(0, -1, 420, 300, ovl)
    Z['>'] = AC_chevron(0, 1, 420, 300, ovl)
    Z['^'] = forme('circonflexe', 220, 640, 300)
    Z['`'] = forme('grave', 120, yacc, hacc)
    Z['{'] = [S((240, 1120), (110, 1120, 80), (110, 450), (-30, 450)), S((-30, 450), (110, 450), (110, -220, 80), (240, -220))]
    Z['}'] = [S((0, 1120), (130, 1120, 80), (130, 450), (270, 450)), S((270, 450), (130, 450), (130, -220, 80), (0, -220))]
    Z['~'] = forme('tilde', 220, 330, 200)
    Z[' '] = P[' ']
    Z['¡'] = tr(P['!'], sx=-1, sy=-1, cy=400)
    Z['¿'] = tr(P['?'], sx=-1, sy=-1, cx=200, cy=400)
    Z['¢'] = G0['c'] + [S((210, X + 160), (210, -160))]
    Z['£'] = [S((470, 880), (470, H, 120), (100, H, 120), (100, 0)), S((-60, 480), (330, 480)), S((-ov, 0), (520, 0))]
    by = (H - 470) / T67
    Z['¥'] = G0['Y'] + [S((by - 210, 330), (by + 210, 330)), S((by - 210, 180), (by + 210, 180))]
    s_min = G0['s']
    Z['§'] = det(tr(s_min, sx=0.6, sy=0.6, dy=520) + tr(s_min, sx=-0.6, sy=-0.6, cx=220, cy=300, dy=-60))
    Z['¨'] = forme('trema', 220, yacc, hacc); Z['´'] = forme('aigu', 120, yacc, hacc); Z['¯'] = forme('macron', 180, yacc, hacc)
    Z['¸'] = cedille(150); Z['˘'] = forme('breve', 160, yacc, hacc); Z['˙'] = forme('point', 100, yacc, hacc)
    Z['˚'] = forme('rond', 130, yacc, hacc); Z['˛'] = ogonek(60); Z['˜'] = forme('tilde', 180, yacc, hacc)
    Z['˝'] = forme('double', 160, yacc, hacc)
    Z['ˆ'] = forme('circonflexe', 160, yacc, hacc); Z['ˇ'] = forme('caron', 160, yacc, hacc)
    O = arrondi.ogive(cx=315.0, top=1010.0, bot=-5.0, w=245.0, over=ov * 0.6)
    Z['©'] = det(O) + det(tr(G0['C'], sx=0.38, sy=0.38, dx=209, dy=310))
    Z['®'] = det(O) + det(tr(G0['R'], sx=0.38, sy=0.38, dx=224, dy=310))
    Z['™'] = det(tr(G0['T'], sx=0.42, sy=0.42, dy=580) + tr(G0['M'], sx=0.42, sy=0.42, dx=360, dy=580))
    Z['°'] = arrondi.ogive(cx=130.0, top=1000.0, bot=700.0, w=100.0, over=40.0)
    Z['¶'] = [S((300, H + ov), (300, -ov)), S((440, H + ov), (440, -ov)), S((300, H), (560, H)),
              S((300, H), (60, H, 170), (60, 520, 170), (300, 520))]
    Z['×'] = [S((0, 220), (360, 580)), S((0, 580), (360, 220))]
    Z['÷'] = [S((0, 400), (440, 400))] + AC.point(220, 620) + AC.point(220, 180)
    Z['‚'] = P[',']
    Z['„'] = P[','] + tr(P[','], dx=200)
    Z['•'] = AC.point(110, 420, s=120)
    Le = arrondi.ogive(cx=315.0, top=1010.0, bot=-5.0, w=245.0, over=ov * 0.6)[0]
    Z['€'] = [Le, S((-80, 600), (420, 600)), S((-80, 400), (380, 400))]
    Z['−'] = [S((0, 420), (440, 420))]
    # --- jeu Windows complet ---
    Z['±'] = [S((0, 540), (440, 540)), S((220, 320), (220, 760)), S((0, 160), (440, 160))]
    Z['¬'] = [S((0, 440), (440, 440)), S((440, 440 + 60), (440, 240))]
    Z['\u00ad'] = P['-']
    Z['¦'] = [S((0, 1120), (0, 520)), S((0, 380), (0, -220))]
    Oc = arrondi.ogive(cx=220.0, top=640.0, bot=200.0, w=140.0, over=30.0)
    Z['¤'] = Oc + [S((40, 620), (-40, 700)), S((400, 620), (480, 700)), S((40, 220), (-40, 140)), S((400, 220), (480, 140))]
    mini = lambda c: det(tr(G0[c], sx=0.5, sy=0.5))
    Z['¹'] = tr(mini('1'), dy=520); Z['²'] = tr(mini('2'), dy=520); Z['³'] = tr(mini('3'), dy=520)
    frac = lambda a, b: tr(mini(a), dy=520) + [S((-20, -60), (560, 1060))] + tr(mini(b), dx=330, dy=-20)
    Z['¼'] = frac('1', '4'); Z['½'] = frac('1', '2'); Z['¾'] = frac('3', '4')
    Z['µ'] = G0['u'] + [S((100, 0), (100, D_ - ovl))]
    Z['ƒ'] = [st for st in G0['f'] if not (len(st['p']) == 2 and abs(st['p'][0][1]) < 1 and abs(st['p'][1][1]) < 1)] + \
             [S((120, 10), (120, D_, 140), (-150, D_)), dict(S((-120, D_ + 110 * ovl / 70), (-120, D_ - 70 * ovl / 70)), detail=True)]
    Z['†'] = [S((0, H + ov), (0, -220)), S((-170, 700), (170, 700))]
    Z['‡'] = [S((0, H + ov), (0, -220)), S((-170, 700), (170, 700)), S((-170, 150), (170, 150))]
    Z['‰'] = P['%'] + tr(arrondi.ogive(cx=60.0, top=340.0, bot=0.0, w=90.0, over=60.0), dx=60 + 900 / T67 + 260)
    return Z

def AC_chevron(x, sens, y, a, d):
    tip = np.array([x, y], float); out = []
    for dy in (a, -a):
        far = tip + np.array([-sens * a, dy])
        u = (tip - far) / np.linalg.norm(tip - far)
        out.append(S(tuple(far), tuple(tip + u * d)))
    return out

# ---------- tout assembler pour une graisse ----------
def complet(R):
    """Tous les traits de la graisse (anciens + nouveaux), clés = caractères."""
    G = triche.glyphes(R)                                   # élargis (sx) avec les règles du gras
    sx = R['sx']; ov = R['ov']; ovl = ov * X / 1000.0
    k = (R['rv'] - 16) / (110 - 16)
    hacc = 200 * (1 + 0.35 * k)
    ECART_DOUBLE[0] = 75 + 60 * k
    y_min = X + ovl + 60; y_maj = H + ov + 50; y_asc = A_ + ovl + 60
    def elargir(sts):
        sts = [dict(st, p=[np.array([x * sx, y]) for x, y in st['p']], caps=list(st['caps'])) for st in sts]
        return triche.couper_biais(sts, ov) if R['poids'] >= 500 else sts
    G0 = {c: [dict(st, p=[np.array([x / sx, y]) for x, y in st['p']]) for st in v] for c, v in G.items()}
    P = techno.build_ponct(ovl); P['@'] = techno.arobase(ovl, techno.build_lc(ovl)['a'], k)
    out = dict(G)
    for c, v in nouvelles_lettres(G0, ov, ovl).items():
        out[c] = elargir(v)
    for c, v in signes(G0, P, ov, ovl, hacc, y_min).items():
        out[c] = elargir(v)
    for c, v in P.items():
        out.setdefault(c, elargir(v))
    # lettres accentuées
    for cp in range(0x00C0, 0x1EF4):
        ch = chr(cp)
        d = unicodedata.decomposition(ch)
        if not d or d.startswith('<') or ch in out:
            continue
        parts = [int(x, 16) for x in d.split()]
        if len(parts) != 2 or parts[1] not in MARQUES:
            continue
        b, m = chr(parts[0]), MARQUES[parts[1]]
        if b not in out:
            continue
        base = out[b]
        if b in 'ij' and m in HAUT:
            base = out['ı' if b == 'i' else 'ȷ']
        x0, y0b, x1, y1b = boite(base)
        cx = (x0 + x1) / 2
        if b == 'A' and R['poids'] < 600:
            cx = boite(base, ymin=900)[0] / 2 + boite(base, ymin=900)[2] / 2
        if ch in APOSTROPHE:
            xs = boite(base, ymin=700)[2]
            acc = virgule_haute(xs + 70 + 1.2 * R['rv'], 900 if b != 't' else 760)
        elif ch == 'ģ':
            acc = virgule_retournee(cx, y_min + 30)
        elif m in HAUT:
            yb = y_maj if b.isupper() else (y_asc if b in 'bdfhklt' else y_min)
            acc = forme(m, cx, yb, hacc)
        elif m == 'cedille' and ch in VIRGULE_DESSOUS:
            acc = virgule_dessous(cx)
        elif m == 'cedille':
            acc = cedille(cx + 40)
        elif m == 'virgule':
            acc = virgule_dessous(cx)
        elif m == 'ogonek':
            xr = boite(base, ymax=60)[2]
            acc = ogonek(xr - 90)
        out[ch] = base + det(acc)
    return out

if __name__ == '__main__':
    import json
    core = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gf_core.json')))
    R = triche.regles(100)
    C = complet(R)
    manque = [chr(c) for c in core if chr(c) not in C and not unicodedata.category(chr(c)).startswith('M')]
    print('caractères encore absents (hors accents combinants) :', ''.join(manque))
