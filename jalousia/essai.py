# Jalousia : essai LAFLEURSTUDIO, style chiffres romains néo-gothiques.
# Unités : ligne de base 0, hauteur des capitales 1000, y vers le haut.
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

def tr(pts, x0, yb, yc):
    s = 1000.0 / (yb - yc)
    return [((x - x0) * s, (yb - y) * s) for x, y in pts]

def tick(x, y, sc=0.45, flip=False):
    # trait vertical à crochet du C (haut à droite), mis à l'échelle
    base = [(57, 258), (21, 280), (-13, 237), (-6, 95), (32, -74), (86, -242)]
    pts = [(dx * sc, dy * sc) for dx, dy in base]
    if flip:
        pts = [(-dx, -dy) for dx, dy in pts]
    return [(x + dx, y + dy) for dx, dy in pts]

G = {}

# ---- dessins d'origine (dossier dessins/) ----
G['I'] = [tr(s, 250, 665, 112) for s in [
    [(288, 142), (330, 118), (400, 107), (470, 112), (525, 132)],
    [(398, 140), (396, 300), (401, 470), (400, 645)],
    [(250, 690), (278, 664), (330, 656), (400, 660), (470, 668), (530, 680)],
]]
G['L'] = [tr(s, 415, 880, 205) for s in [
    [(415, 205), (600, 203), (790, 205)],
    [(568, 152), (540, 190), (522, 260), (495, 420), (462, 620), (430, 830), (420, 893)],
    [(420, 895), (470, 878), (600, 868), (800, 866), (930, 868), (955, 882), (962, 900)],
]]
G['D'] = [tr(s, 245, 1240, 215) for s in [
    [(515, 207), (503, 218), (500, 260), (505, 400), (495, 550), (478, 750), (462, 950), (468, 1060), (480, 1112)],
    [(548, 225), (650, 290), (800, 400), (920, 520), (1010, 650), (1050, 780), (1055, 880), (1030, 980),
     (960, 1060), (850, 1130), (700, 1185), (500, 1235), (245, 1265)],
    [(278, 980), (268, 1100), (258, 1265), (262, 1400), (262, 1432)],
]]

DESSINS = {}     # lettre -> (dessin, traits en pixels), pour comparer le tracé au dessin

def dessin(ch, fichier, x0, yb, yc, traits):
    G[ch] = [tr(s, x0, yb, yc) for s in traits]
    DESSINS[ch] = (fichier, traits)

dessin('V', 'I-V-X.jpg', 596, 665, 112, [
    [(596, 108), (604, 128), (610, 150)],
    [(608, 124), (700, 121), (785, 127)],
    [(650, 148), (660, 300), (680, 450), (700, 580), (714, 650)],
    [(1003, 172), (950, 270), (860, 410), (780, 530), (718, 645)],
    [(910, 175), (925, 156), (980, 150), (1060, 155), (1130, 152), (1180, 140)],
    [(618, 688), (700, 684), (780, 672), (855, 660)],
])
dessin('X', 'I-V-X.jpg', 130, 1560, 1012, [
    [(220, 1012), (300, 1015), (380, 1016), (465, 1013)],
    [(335, 1045), (420, 1170), (500, 1280), (580, 1400), (625, 1490), (650, 1550)],
    [(755, 1000), (700, 1065), (600, 1170), (500, 1280), (400, 1390), (310, 1500), (270, 1560)],
    [(655, 1040), (750, 1040), (870, 1050), (990, 1062)],
    [(130, 1568), (200, 1565), (280, 1560), (360, 1555)],
    [(570, 1562), (650, 1560), (740, 1563), (800, 1570), (838, 1585)],
])
dessin('C', 'L-C.jpg', 385, 1735, 1245, [
    [(388, 1262), (395, 1400), (405, 1550), (412, 1680), (418, 1735)],
    [(385, 1260), (450, 1245), (530, 1228), (620, 1205), (700, 1190), (760, 1188), (812, 1210)],
    [(803, 1072), (785, 1080), (775, 1120), (785, 1200), (805, 1260), (825, 1320)],
    [(420, 1735), (480, 1735), (560, 1720), (650, 1700), (750, 1675), (855, 1655)],
])
dessin('M', 'M.jpg', 155, 930, 232, [
    [(285, 232), (700, 233), (1200, 232)],
    [(155, 935), (215, 840), (300, 700), (400, 545), (500, 390), (560, 290), (590, 250)],
    [(590, 250), (615, 300), (645, 420), (658, 550), (660, 700), (670, 820), (705, 920)],
    [(705, 920), (760, 830), (850, 640), (930, 450), (990, 290), (1012, 235), (1030, 208), (1046, 220),
     (1055, 280), (1065, 400), (1090, 600), (1120, 780), (1138, 890), (1160, 970)],
])

# ---- lettres déduites ----
# A : la moitié du M, barre en haut, traverse ondulée
G['A'] = [
    [(230, 1000), (650, 1000)],
    [(0, 20), (80, 170), (200, 430), (330, 720), (420, 940), (440, 990)],
    [(440, 990), (462, 940), (490, 800), (500, 600), (505, 400), (515, 200), (540, 60), (570, 10)],
    [(100, 350), (250, 338), (400, 355), (560, 362), (660, 345)],
]
# F : barre et fût du L, crochet du C au bout de la barre, pied ondulé du I
G['F'] = [
    [(0, 1000), (300, 1003), (620, 1000)],
    [(225, 1080), (190, 1025), (172, 930), (160, 700), (150, 400), (142, 150), (140, 0)],
    [(60, 500), (150, 520), (260, 530), (380, 515), (440, 525)],
    tick(600, 1000),
    [(-10, -40), (40, 0), (130, 12), (240, 8), (330, -10)],
]
# E : le C (moins penché) + barre du milieu
G['E'] = [
    [(30, 1000), (25, 700), (35, 350), (45, 0)],
    [(30, 1000), (150, 1012), (300, 1025), (420, 1040), (520, 1045)],
    tick(500, 1045),
    [(-30, 505), (80, 515), (220, 525), (350, 520), (420, 530)],
    [(45, 0), (180, 10), (330, 25), (470, 40), (560, 45)],
]
# U : le V avec le bas arrondi
G['U'] = [
    [(-10, 1030), (10, 985), (70, 1000), (180, 1008), (320, 1002)],
    [(100, 975), (110, 800), (115, 500), (125, 250), (170, 90), (260, 15), (370, 25), (460, 110), (515, 260)],
    [(545, 985), (538, 700), (528, 400), (518, 150), (528, 30), (565, 0)],
    [(440, 935), (470, 960), (560, 968), (700, 962), (800, 985)],
]
# R : fût et panse du D, jambe qui tombe sur un pied ondulé
G['R'] = [
    [(263, 1008), (250, 995), (247, 950), (250, 800), (240, 550), (228, 300), (220, 100), (222, 0)],
    [(296, 992), (380, 940), (490, 860), (570, 770), (590, 680), (560, 590), (470, 530), (330, 495),
     (200, 482), (130, 478)],
    [(152, 555), (146, 478), (140, 400)],
    [(380, 505), (450, 380), (540, 220), (620, 80), (660, 10)],
    [(560, -10), (640, 0), (740, -5), (820, -30)],
]
# S : un seul trait, crochets du C aux deux bouts (symétrique)
G['S'] = [
    [(600, 1000), (470, 1012), (300, 1005), (150, 985), (70, 950), (35, 880), (45, 780), (100, 690),
     (250, 570), (420, 440), (530, 340), (580, 240), (570, 130), (510, 50), (400, 12), (250, 0),
     (100, -5), (0, -15)],
    tick(590, 1000),
    tick(10, -15, flip=True),
]
# T : barre droite du L/M, fût qui dépasse, pied ondulé
G['T'] = [
    [(0, 1000), (350, 1002), (720, 1000)],
    [(410, 1080), (378, 1025), (362, 930), (352, 700), (340, 400), (332, 150), (330, 10)],
    [(180, -40), (225, 0), (300, 14), (400, 9), (480, -4), (540, -25)],
]
# O : ogive gothique, deux arcs qui se croisent en haut et en bas
G['O'] = [
    [(370, 1070), (300, 1000), (150, 830), (70, 560), (110, 280), (230, 60), (330, -10), (380, -40)],
    [(250, 1060), (330, 995), (480, 830), (560, 560), (520, 280), (410, 60), (310, -10), (260, -40)],
]

def cr(pts, n=20):
    P = np.array(pts, float)
    if len(P) == 2:
        t = np.linspace(0, 1, n * 3)[:, None]
        return P[0] * (1 - t) + P[1] * t
    P = np.vstack([2 * P[0] - P[1], P, 2 * P[-1] - P[-2]])
    out = []
    def tj(ti, a, b):
        return ti + max(np.linalg.norm(b - a), 1e-6) ** 0.5
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        t0 = 0.0; t1 = tj(t0, p0, p1); t2 = tj(t1, p1, p2); t3 = tj(t2, p2, p3)
        for t in np.linspace(t1, t2, n, endpoint=False):
            A1 = (t1 - t) / (t1 - t0) * p0 + (t - t0) / (t1 - t0) * p1
            A2 = (t2 - t) / (t2 - t1) * p1 + (t - t1) / (t2 - t1) * p2
            A3 = (t3 - t) / (t3 - t2) * p2 + (t - t2) / (t3 - t2) * p3
            B1 = (t2 - t) / (t2 - t0) * A1 + (t - t0) / (t2 - t0) * A2
            B2 = (t3 - t) / (t3 - t1) * A2 + (t - t1) / (t3 - t1) * A3
            out.append((t2 - t) / (t2 - t1) * B1 + (t - t1) / (t2 - t1) * B2)
    out.append(P[-2])
    return np.array(out)

R = 16          # demi-épaisseur du trait (unités)
GAP = 170       # écart minimal entre deux lettres (unités)
BAND = 20

def samples(ch):
    return [cr(s) for s in G[ch]]

def profile(ch):
    pts = np.vstack(samples(ch))
    bands = {}
    for x, y in pts:
        b = int(np.floor(y / BAND))
        for bb in (b - 1, b, b + 1):
            lo, hi = bands.get(bb, (1e9, -1e9))
            bands[bb] = (min(lo, x - R), max(hi, x + R))
    return bands, pts[:, 0].min() - R, pts[:, 0].max() + R

def layout(word):
    xs = []
    prev = None
    x = 0.0
    for ch in word:
        bands, lo, hi = profile(ch)
        if prev is None:
            off = -lo
        else:
            pb, plo, phi, px = prev
            need = -1e9
            for b, (l, h) in bands.items():
                if b in pb:
                    need = max(need, px + pb[b][1] - l + GAP)
            # la lettre ne rentre pas sous la précédente de plus d'un quart de hauteur
            need = max(need, px + phi - lo - 120)
            off = need
        xs.append(off)
        prev = (bands, lo, hi, off)
    end = prev[3] + prev[2]
    return xs, end

def render(word, out, k=0.3, ss=2, craie=True):
    xs, end = layout(word)
    K = k * ss
    W = int((end + 600) * K)
    top, bot = 1450, -350
    Hh = int((top - bot) * K)
    img = Image.new('L', (W, Hh), 0)
    d = ImageDraw.Draw(img)
    r = R * K
    for ch, ox in zip(word, xs):
        for s in samples(ch):
            P = [((x + ox + 300) * K, (top - y) * K) for x, y in s]
            d.line(P, fill=255, width=int(round(2 * r)))
            for px, py in P:
                d.ellipse([px - r, py - r, px + r, py + r], fill=255)
    if not craie:
        im = img.resize((W // ss, Hh // ss), Image.LANCZOS).point(lambda v: v * 238 // 255).convert('RGB')
        im.save(out)
        return xs
    M = np.asarray(img.filter(ImageFilter.GaussianBlur(r * 0.35)), float) / 255
    rng = np.random.default_rng(7)
    def noise(sig):
        n = Image.fromarray((rng.random(M.shape) * 255).astype(np.uint8))
        a = np.asarray(n.filter(ImageFilter.GaussianBlur(sig)), float)
        return (a - a.mean()) / (a.std() + 1e-6)
    n1, n2, n3 = noise(0.8), noise(3.0), noise(0.7)
    near = np.clip(M * 4, 0, 1)
    A = M + (0.20 * n1 + 0.08 * n2) * near
    alpha = np.clip((A - 0.42) / 0.22, 0, 1)
    grain = np.clip(0.86 + 0.14 * n3, 0, 1)
    v = (alpha * grain * 238).astype(np.uint8)
    im = Image.fromarray(v).resize((W // ss, Hh // ss), Image.LANCZOS).convert('RGB')
    im.save(out)
    return xs

if __name__ == '__main__':
    word = sys.argv[1] if len(sys.argv) > 1 else 'LAFLEURSTUDIO'
    out = sys.argv[2] if len(sys.argv) > 2 else 'essai.png'
    print(render(word, out, craie=(len(sys.argv) < 4)))
