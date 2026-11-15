# КИНОВАРЬ (KINOVAR) : les lettres. L'oustav russe du XIe siècle, tracé à la plume large tenue à plat :
# fûts épais à petite attaque en coin, traits horizontaux fins qui finissent en goutte, rondes à flancs épais.
# Le latin d'accompagnement est une onciale dessinée avec la même plume.
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'karkas', 'source'))
from kar_core import P, poly, rect, U, D, I, mv, mirror, flipv, link, losange

H = 700; SC = 546                      # hauteur des capitales, des petites capitales (les minuscules)
DESC = 0.20                            # descente du Р, du У, du Ф (part de la hauteur)
K = 0.5522847498
def ell(cx, cy, a, b):
    p = P(); pen = p.getPen(); pen.moveTo((cx + a, cy))
    pen.curveTo((cx + a, cy + K * b), (cx + K * a, cy + b), (cx, cy + b)); pen.curveTo((cx - K * a, cy + b), (cx - a, cy + K * b), (cx - a, cy))
    pen.curveTo((cx - a, cy - K * b), (cx - K * a, cy - b), (cx, cy - b)); pen.curveTo((cx + K * a, cy - b), (cx + a, cy - K * b), (cx + a, cy)); pen.closePath(); return p

class Wt:
    """une graisse : S fût, h trait fin"""
    def __init__(s, nom, S, h, wclass):
        s.nom, s.S, s.h, s.wclass = nom, S, h, wclass
        s.SB = round(34 + 0.22 * S)                           # approche d'un fût
        s.G = round(2.5 * s.SB); s.g = round(1.0 * s.SB); s.W = round(0.62 * H + 1.2 * S); s.B = h; s.CT = s.W - 2 * S   # pour le crénage commun
    def petit(s):
        w = Wt(s.nom, round(0.93 * s.S), s.h, s.wclass); w.SB = round(0.92 * s.SB); return w
WEIGHTS = {'Stroka': Wt('Stroka', 46, 15, 300), 'Zaglavie': Wt('Zaglavie', 80, 22, 500), 'Bukvitsa': Wt('Bukvitsa', 122, 30, 800)}

RU = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
AZ = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
TWIN = {'A': 'А', 'B': 'В', 'C': 'С', 'E': 'Е', 'H': 'И', 'K': 'К', 'M': 'М', 'O': 'О', 'P': 'Р', 'T': 'Т', 'X': 'Х', 'Y': 'У'}   # latin = même dessin
# côtés de la lettre, pour l'approche : S fût, O ronde, D oblique ou trait fin
SIDES = {'О': 'OO', 'С': 'OD', 'Е': 'OD', 'Э': 'DO', 'Т': 'DD', 'Г': 'SD', 'А': 'DD', 'Л': 'DD', 'Д': 'DD', 'У': 'DD', 'Х': 'DD', 'Ж': 'DD', 'Ч': 'OO', 'Ф': 'OO',
         'Р': 'SO', 'В': 'SO', 'Б': 'SO', 'Ь': 'SO', 'Ъ': 'DO', 'К': 'SD', 'З': 'DO', 'Ю': 'SO', 'Я': 'DS', 'Ц': 'SD', 'Щ': 'SD',
         'D': 'SO', 'F': 'SD', 'G': 'OS', 'J': 'DS', 'L': 'SD', 'Q': 'OO', 'R': 'SD', 'S': 'OO', 'U': 'SS', 'V': 'DD', 'W': 'DD', 'Z': 'DD'}

def letter(ch, w, y0=0, y1=H, moderne=False):
    """rend (encre, largeur). moderne : le И, le Н et le Ч d'aujourd'hui (ss01) au lieu de ceux de l'oustav."""
    if ch in TWIN: return letter(TWIN[ch], w, y0, y1)
    S, h = w.S, w.h; hh = y1 - y0
    def stem(x, a=y0, b=y1, top=True, foot=True):
        p = rect(x, a, x + S, b)
        if top: p = U(p, poly([(x - 0.42 * S, b), (x + 2, b), (x + 2, b - 0.55 * S)]))                  # l'attaque de la plume
        if foot: p = U(p, poly([(x + S - 2, a), (x + S + 0.30 * S, a), (x + S - 2, a + 0.42 * S)]))    # la sortie
        return p
    hb = lambda xa, xb, y: rect(xa, y, xb, y + h)
    def goutte(x, y, sens=-1, k=1.0):                       # goutte au bout d'un trait fin
        s = (1.5 * h + 0.10 * S) * k; return poly([(x - s * 0.55, y), (x + s * 0.45, y), (x + s * 0.45, y + sens * 2.1 * s)])
    def ring(cx, cy, a, b, ts=S, tv=None):
        tv = h * 1.25 if tv is None else tv; return D(ell(cx, cy, a, b), ell(cx, cy, a - ts, b - tv))
    def diag(xb, xt, t, a=y0, b=y1): return poly([(xb, a), (xb + t, a), (xt + t, b), (xt, b)])
    fin = lambda xa, ya, xb, yb, wa=0, wb=0: link(xa, ya, xb, yb, h * 1.2, wa, wb)
    att = lambda x: poly([(x - 0.42 * S, y1), (x + 2, y1), (x + 2, y1 - 0.5 * S)])
    ym = y0 + 0.5 * hh; ov = round(8 * hh / H); d = DESC * hh
    WO = round(0.80 * hh + 0.5 * S)                         # largeur d'une ronde
    WN = round(0.62 * hh + 1.2 * S)                         # largeur d'une lettre à deux fûts
    box = rect(-200, y0, 3000, y1)
    if ch == 'О':
        w_ = WO; p = ring(w_ / 2, ym, w_ / 2, hh / 2 + ov)
    elif ch in 'СЕЭ':
        w_ = round(0.92 * WO); r = ring(WO / 2, ym, WO / 2, hh / 2 + ov)
        p = D(r, poly([(WO * 0.52, ym), (WO + 20, ym + 0.36 * hh), (WO + 20, ym - 0.30 * hh)]))
        p = I(p, rect(-10, y0 - 20, w_, y1 + 20)); p = U(p, goutte(w_ - 0.5 * h, y1 - 0.07 * hh, -1, 0.8))
        if ch in 'ЕЭ': p = U(p, hb(S * 0.6, w_ - 0.04 * hh, ym - h / 2 + 0.03 * hh), goutte(w_ - 0.04 * hh - 0.3 * h, ym + 0.03 * hh + 1.6 * h, -1, 0.6))
        if ch == 'Э': p = mirror(p, w_ / 2)
    elif ch == 'Т':
        w_ = round(0.86 * hh + 0.3 * S); x = (w_ - S) / 2
        p = U(stem(x, top=False), hb(0, w_, y1 - h), goutte(0.6 * h, y1 - h + 1), goutte(w_ - 0.5 * h, y1 - h + 1))
    elif ch == 'Г':
        w_ = round(0.50 * hh + S); p = U(stem(0, top=False), hb(-0.2 * S, w_, y1 - h), goutte(w_ - 0.5 * h, y1 - h + 1))
    elif ch == 'П':
        w_ = WN; p = U(stem(0, top=False), stem(w_ - S, top=False), hb(-0.25 * S, w_ + 0.25 * S, y1 - h))
    elif ch in 'ИЙНN':
        w_ = WN; p = U(stem(0), stem(w_ - S))
        barre = hb(S - 2, w_ - S + 2, ym + 0.04 * hh)                                              # la barre droite : le И de l'oustav, le Н d'aujourd'hui
        pente = fin(S / 2, ym + 0.13 * hh, w_ - S / 2, ym - 0.10 * hh, S, S)                       # la barre oblique : le Н de l'oustav
        monte = fin(S / 2, y0 + 0.16 * hh, w_ - S / 2, y1 - 0.16 * hh, S, S)                       # le И d'aujourd'hui
        if ch == 'N': p = U(p, fin(S / 2, y1 - 0.10 * hh, w_ - S / 2, y0 + 0.10 * hh, S, S))
        elif ch in 'ИЙ': p = U(p, monte if moderne else barre)
        else: p = U(p, barre if moderne else pente)
        if ch == 'Й':
            cy = y1 + 0.17 * hh; a = 0.27 * w_; b = 0.12 * hh
            p = U(p, D(ell(w_ / 2, cy, a, b), ell(w_ / 2, cy + h, a - h * 1.3, b), rect(-50, cy, w_ + 50, cy + 400)))
    elif ch == 'Р':
        w_ = round(0.46 * hh + S); a = w_ - S * 0.5; b = 0.30 * hh
        p = U(stem(0, y0 - d), I(ring(S * 0.5, y1 - b + ov / 2, a, b), rect(S * 0.5, y0, w_ + 20, y1 + 30)))
    elif ch == 'Ф':
        w_ = round(0.92 * WO); x = (w_ - S) / 2
        p = U(stem(x, y0 - d, y1 + 0.06 * hh), ring(w_ / 2, ym + 0.04 * hh, w_ / 2, 0.30 * hh, S * 0.9))
    elif ch in 'ВБЬЪЫ':
        w_ = round(0.50 * hh + S); a = w_ - S * 0.5
        low = I(ring(S * 0.5, y0 + 0.29 * hh - ov / 2, a, 0.29 * hh), rect(S * 0.5, y0 - 30, w_ + 20, y1))
        p = U(stem(0, top=(ch != 'Б')), low)
        if ch == 'В': p = U(p, I(ring(S * 0.5, y1 - 0.225 * hh + ov / 2, a * 0.86, 0.225 * hh), rect(S * 0.5, y0, w_ + 20, y1 + 30)))
        if ch == 'Б': p = U(p, hb(-0.2 * S, w_ * 0.92, y1 - h), goutte(w_ * 0.92 - 0.5 * h, y1 - h + 1))
        if ch == 'Ъ': e = round(0.30 * hh); p = U(mv(p, e), hb(0, e + 2, y1 - h), goutte(0.6 * h, y1 - h + 1)); w_ += e
        if ch == 'Ы': g = round(0.16 * hh); p = U(p, mv(stem(0), w_ + g)); w_ += g + S
    elif ch == 'М':
        w_ = round(0.98 * hh + S); xm = w_ / 2; yv = y0 + 0.16 * hh; t = round(0.92 * S)
        p = U(stem(0), stem(w_ - S), poly([(S * 0.7, y1), (S * 0.7 + t, y1), (xm + t * 0.5, yv), (xm - t * 0.5, yv)]), fin(xm, yv + h, w_ - S / 2, y1 - 0.02 * hh, 0, S))
    elif ch in 'АЛД':
        w_ = round(0.80 * hh + 0.6 * S); xa = w_ * 0.40; t = round(1.02 * S)
        p = I(U(diag(w_ - t, xa, t), fin(0.6 * h, y0, xa + t * 0.5, y1 - 0.01 * hh), att(xa)), box)
        if ch == 'А':                                        # la barre va du trait fin au bord gauche du trait épais, sans dépasser
            k = 0.26 + h / hh; xg = 0.6 * h + (xa + t * 0.5 - 0.6 * h) * 0.26; xd = (w_ - t) + (xa - (w_ - t)) * k
            p = U(p, hb(xg, xd + 3, y0 + 0.26 * hh))
        if ch == 'Д': e = round(0.10 * hh); p = U(mv(p, e), hb(0, w_ + 2 * e, y0), goutte(0.6 * h, y0 + 1), goutte(w_ + 2 * e - 0.5 * h, y0 + 1)); w_ += 2 * e
    elif ch == 'У':
        w_ = round(0.74 * hh + 0.5 * S); t = round(1.0 * S); xj = w_ * 0.42
        p = I(U(diag(w_ * 0.16, w_ - t, t, y0 - d, y1), fin(h, y1, xj + t * 0.2, ym - 0.06 * hh), att(w_ - t)), rect(-200, y0 - d, 3000, y1))
    elif ch == 'Ч':
        w_ = round(0.74 * hh + 0.5 * S)
        if moderne:
            w_ = WN; yq = y0 + 0.44 * hh; p = U(stem(0, yq, y1, foot=False), hb(S - 2, w_ - S + 2, yq), stem(w_ - S))
        else:                                               # le Ч de l'oustav : une coupe sur un pied
            cy = y1 - 0.02 * hh; b = 0.50 * hh
            p = U(I(ring(w_ / 2, cy, w_ / 2, b, S * 0.9, h * 1.6), rect(-10, y0, w_ + 10, cy)), stem((w_ - S) / 2, y0, cy - b + h, top=False))
    elif ch == 'К':
        w_ = round(0.62 * hh + S); t = round(0.9 * S)
        p = U(stem(0), fin(S / 2, ym + 0.02 * hh, w_ - h, y1 - 0.03 * hh, S, 0), goutte(w_ - h * 0.6, y1 - 0.02 * hh, -1, 0.7), poly([(S - 2, ym + 0.04 * hh), (S + t * 0.9, ym + 0.04 * hh), (w_, y0), (w_ - t, y0)]))
    elif ch == 'З':
        w_ = round(0.46 * hh + 0.9 * S); a = w_ * 0.98
        up = I(ring(0, y1 - 0.24 * hh + ov / 2, a * 0.90, 0.24 * hh), rect(0.10 * w_, y0, w_ + 20, y1 + 30))
        lo = I(ring(0, y0 + 0.30 * hh - ov / 2, a, 0.30 * hh), rect(0.02 * w_, y0 - 30, w_ + 20, y1))
        p = U(up, lo)
    elif ch == 'Х':
        w_ = round(0.74 * hh + 0.5 * S); t = round(1.0 * S)
        p = I(U(diag(w_ - t, 0, t), fin(h * 0.6, y0, w_ - h * 0.6, y1)), box)
    elif ch in 'ШЩЦ':
        n = 3 if ch != 'Ц' else 2; st = round(0.36 * hh + 0.5 * S); w_ = (n - 1) * st + S
        p = U(*[stem(i * st, foot=False) for i in range(n)], hb(0, w_, y0))
        if ch != 'Ш': e = round(0.10 * hh); p = U(p, hb(w_ - 2, w_ + e, y0), goutte(w_ + e - 0.5 * h, y0 + 1)); w_ += e
    elif ch == 'Ж':
        w_ = round(1.0 * hh + 0.3 * S); xm = w_ / 2; t = round(0.8 * S)
        p = I(U(stem(xm - S / 2), fin(h * 0.6, y1, xm, ym), fin(xm, ym, w_ - h * 0.6, y1),
                poly([(0, y0), (t, y0), (xm + t * 0.3, ym + 0.02 * hh), (xm - t * 0.6, ym + 0.02 * hh)]), poly([(w_ - t, y0), (w_, y0), (xm + t * 0.6, ym + 0.02 * hh), (xm - t * 0.3, ym + 0.02 * hh)])), box)
    elif ch == 'Ю':
        e = round(S + 0.16 * hh); wo = round(0.86 * WO); w_ = e + wo
        p = U(stem(0), hb(S - 2, e + S * 0.5, ym), mv(ring(wo / 2, ym, wo / 2, hh / 2 + ov), e))
    elif ch == 'Я':
        w_ = round(0.50 * hh + S); a = w_ - S * 0.5; b = 0.29 * hh
        bowl = I(ring(S * 0.5, y1 - b + ov / 2, a, b), rect(S * 0.5, y0, w_ + 20, y1 + 30))
        p = I(U(mirror(U(stem(0), bowl), w_ / 2), fin(h * 0.6, y0, w_ - S * 0.5, y1 - 2 * b + h, 0, S)), rect(-200, y0, 3000, y1 + 30))
    # ---- le latin qui n'a pas de jumeau
    elif ch == 'D':
        w_ = round(0.66 * hh + 0.8 * S); a = w_ - S * 0.5
        p = U(stem(0), I(ring(S * 0.5, ym, a, hh / 2 + ov / 2), rect(S * 0.5, y0 - 30, w_ + 20, y1 + 30)))
    elif ch == 'F':
        w_ = round(0.46 * hh + S); p = U(stem(0, top=False), hb(-0.2 * S, w_, y1 - h), goutte(w_ - 0.5 * h, y1 - h + 1), hb(S - 2, w_ * 0.80, ym + 0.02 * hh), goutte(w_ * 0.80 - 0.4 * h, ym + 0.02 * hh + 1.6 * h, -1, 0.6))
    elif ch == 'G':
        w_ = round(0.96 * WO); r = ring(WO / 2, ym, WO / 2, hh / 2 + ov)
        p = D(r, poly([(WO * 0.52, ym), (WO + 20, ym + 0.36 * hh), (WO + 20, ym - 0.06 * hh)]))
        p = U(I(p, rect(-10, y0 - 20, w_, y1 + 20)), goutte(w_ - 0.5 * h, y1 - 0.07 * hh, -1, 0.8), rect(w_ - S, y0 + 0.10 * hh, w_, ym - 0.04 * hh), hb(w_ - S - 0.16 * hh, w_ + 0.02 * hh, ym - 0.04 * hh - h))
    elif ch == 'I':
        w_ = S; p = stem(0)
    elif ch == 'J':
        a = round(0.30 * hh); b = 0.30 * hh; w_ = round(a * 1.25 + S * 0.5); cx = w_ - a
        p = U(stem(w_ - S, y0 + b, y1, foot=False), D(I(ring(cx, y0 + b - ov / 2, a, b), rect(-10, y0 - 30, w_ + 10, y0 + b)), rect(-10, y0 + 0.45 * b, cx, y0 + b + 5)))
    elif ch == 'L':
        w_ = round(0.46 * hh + S); p = U(stem(0, foot=False), hb(0, w_, y0), goutte(w_ - 0.5 * h, y0 + h - 1, 1))
    elif ch == 'Q':
        w_ = WO; p = U(ring(w_ / 2, ym, w_ / 2, hh / 2 + ov), poly([(w_ * 0.46, y0 + 0.16 * hh), (w_ * 0.46 + 0.9 * S, y0 + 0.16 * hh), (w_ * 1.02, y0 - 0.16 * hh), (w_ * 1.02 - 0.5 * S, y0 - 0.16 * hh)]))
    elif ch == 'R':
        w_ = round(0.50 * hh + S); a = w_ - S * 0.5; b = 0.27 * hh; t = round(0.9 * S)
        bowl = I(ring(S * 0.5, y1 - b + ov / 2, a * 0.92, b), rect(S * 0.5, y0, w_ + 20, y1 + 30))
        p = U(stem(0), bowl, poly([(S + 0.04 * hh, y1 - 2 * b + h), (S + 0.04 * hh + t, y1 - 2 * b + h), (w_ + 0.04 * hh, y0), (w_ + 0.04 * hh - t, y0)])); w_ = round(w_ + 0.04 * hh)
    elif ch == 'S':
        # deux boucles qui se chevauchent au milieu : celle du haut est épaisse en bas, celle du bas épaisse en haut, et le dos du S est plein
        w_ = round(0.50 * hh + 0.9 * S); a = w_ / 2; T = round(0.82 * S); b = (hh + 2 * ov + T) / 4; cu = y1 + ov - b; cl = y0 - ov + b
        def boucle(cy, aa, haut, bas): return D(ell(a, cy, aa, b), ell(a, cy + (bas - haut) / 2, aa - S, b - (haut + bas) / 2))
        up = D(boucle(cu, a * 0.93, h * 1.25, T), rect(a * 1.12, cu - b - 5, w_ + 5, cu - 0.16 * b))
        lo = D(boucle(cl, a, T, h * 1.25), rect(-5, cl + 0.16 * b, a * 0.88, cl + b + 5))
        p = U(up, lo, goutte(a + a * 0.93 - 0.5 * h, y1 - 0.08 * hh, -1, 0.8))
    elif ch == 'U':
        w_ = WN; b = 0.36 * hh
        p = U(stem(0, y0 + b - 2, y1, foot=False), stem(w_ - S, y0, y1), I(ring(w_ / 2, y0 + b - ov / 2, w_ / 2, b), rect(-10, y0 - 30, w_ + 10, y0 + b)))
    elif ch in 'VW':
        wv = round(0.76 * hh + 0.4 * S); t = round(1.0 * S); xm = wv * 0.56
        v = I(U(diag(xm - t / 2, 0, t), fin(xm, y0, wv - h * 0.6, y1), att(0)), box)
        if ch == 'V': p, w_ = v, wv
        else: st = round(wv * 0.62); p = U(v, mv(v, st)); w_ = wv + st
    elif ch == 'Z':
        w_ = round(0.70 * hh + 0.4 * S); t = round(1.0 * S)
        p = U(hb(0, w_, y1 - h), hb(0, w_, y0), I(diag(0, w_ - t, t), box), goutte(0.6 * h, y1 - h + 1), goutte(w_ - 0.5 * h, y0 + h - 1, 1))
    else: raise KeyError(ch)
    return p, w_
