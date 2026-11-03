# Fûsard-032 : essai du style des accents (recette : traits droits, pointes, croix, ogive)
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import fusard as techno
import arrondi, triche
S, path = techno.S, techno.path
T67 = techno.T67

def point(x, y, s=70):
    return [S((x, y + s), (x, y - s)), S((x - s, y), (x + s, y))]

def accent(nom, cx, y0, h=200, ov=50):
    """Accent centré en cx, posé à partir de y0 (bas de l'accent), hauteur h."""
    y1 = y0 + h
    if nom == 'aigu':
        dx = h / T67
        return [S((cx - dx / 2, y0), (cx + dx / 2, y1))]
    if nom == 'grave':
        dx = h / T67
        return [S((cx + dx / 2, y0), (cx - dx / 2, y1))]
    if nom == 'circonflexe':      # croisé en pointe, comme le haut du A
        dx = 0.8 * h / T67 * 1.6
        u = np.array([dx, h]) / math.hypot(dx, h)
        return [S((cx - dx, y0), tuple(np.array([cx, y1]) + u * ov)),
                S((cx + dx, y0), tuple(np.array([cx, y1]) + np.array([-u[0], u[1]]) * ov))]
    if nom == 'caron':
        dx = 0.8 * h / T67 * 1.6
        u = np.array([dx, -h]) / math.hypot(dx, h)
        return [S((cx - dx, y1), tuple(np.array([cx, y0]) + u * ov)),
                S((cx + dx, y1), tuple(np.array([cx, y0]) + np.array([-u[0], u[1]]) * ov))]
    if nom == 'trema':            # deux petites croix, comme le point du i
        return point(cx - 115, y0 + h / 2) + point(cx + 115, y0 + h / 2)
    if nom == 'point':
        return point(cx, y0 + h / 2)
    if nom == 'rond':             # petite ogive, comme le O
        return arrondi.ogive(cx=cx, top=y1 + 20, bot=y0 - 20, w=85.0, over=40.0)
    if nom == 'tilde':            # zigzag aux coins arrondis
        return [S((cx - 150, y0 + 20), (cx - 60, y1 - 20, 50), (cx + 60, y0 + 20, 50), (cx + 150, y1 - 20))]
    if nom == 'macron':
        return [S((cx - 140, y0 + h / 2), (cx + 140, y0 + h / 2))]
    if nom == 'breve':
        return [S((cx - 110, y1), (cx - 110, y0, 70), (cx + 110, y0, 70), (cx + 110, y1))]
    raise ValueError(nom)

def cedille(cx):
    return [S((cx, 30), (cx, -150, 60), (cx - 120, -150)), S((cx - 95, -60), (cx - 95, -230))]

def barre_o(cx, cy, h):
    dx = h / T67
    return [S((cx - dx / 2, cy - h / 2), (cx + dx / 2, cy + h / 2))]

def centre(sts):
    P = np.vstack([np.array(st['p']) for st in sts])
    return (P[:, 0].min() + P[:, 0].max()) / 2

def detail(sts):
    return [dict(st, detail=True) for st in sts]

def composer(G, R=None):
    """Quelques lettres accentuées pour l'essai."""
    X = techno.XH
    R = R or triche.regles(100)
    k = (R['rv'] - 16) / (110 - 16)
    out = {}
    def avec(base, acc, haut):
        c = centre(G[base]) if base not in ('a',) else 230.0 * R['sx']
        return G[base] + detail(accent(acc, c, haut, h=200 * (1 + 0.35 * k)))
    m = X + R['ov'] * techno.XH / 1000 + 60     # bas des accents des minuscules : au-dessus des pointes
    M = 1000 + R['ov'] + 50                      # bas des accents des capitales : au-dessus des pointes
    out['é'] = avec('e', 'aigu', m); out['è'] = avec('e', 'grave', m)
    out['ê'] = avec('e', 'circonflexe', m); out['ë'] = avec('e', 'trema', m)
    out['à'] = avec('a', 'grave', m); out['ñ'] = avec('n', 'tilde', m); out['å'] = avec('a', 'rond', m)
    out['ç'] = G['c'] + detail(cedille(200 * R['sx']))
    out['ø'] = G['o'] + barre_o(220 * R['sx'], 300, 700)
    out['É'] = avec('E', 'aigu', M); out['À'] = avec('A', 'grave', M); out['Ñ'] = avec('N', 'tilde', M)
    out['Å'] = avec('A', 'rond', M); out['Ç'] = G['C'] + detail(cedille(280 * R['sx']))
    out['Ø'] = G['O'] + barre_o(315 * R['sx'], 500, 1150)
    return out

def render_poly(word, out, G, R, k=0.3, ss=3):
    """Rendu avec le même moteur que les fichiers de police : un contour par trait, union, trous respectés."""
    from PIL import Image, ImageDraw
    from fontTools.pens.recordingPen import RecordingPen
    import jalousia_layout, build_family as B
    xs, end = jalousia_layout.placer(word, G, R)
    K = k * ss; top, bot = 1750, -600
    W = int((end + 700) * K); H = int((top - bot) * K)
    img = Image.new('L', (W, H), 0); d = ImageDraw.Draw(img)
    for ch, ox in zip(word, xs):
        path = B.contours(G[ch], R)
        rec = RecordingPen(); path.draw(rec)
        polys, cur = [], []
        for op, args in rec.value:
            if op == 'moveTo': cur = [args[0]]
            elif op == 'lineTo': cur.append(args[0])
            elif op in ('closePath', 'endPath'):
                if len(cur) >= 3: polys.append([(x / B.SC, y / B.SC) for x, y in cur])
                cur = []
        prof = [sum(1 for j, Q in enumerate(polys) if j != i and B._dedans(P[0], Q)) for i, P in enumerate(polys)]
        for p_, P in sorted(zip(prof, polys), key=lambda t: t[0]):
            d.polygon([((x + ox + 350) * K, (top - y) * K) for x, y in P], fill=238 if p_ % 2 == 0 else 0)
    img.resize((W // ss, H // ss), Image.LANCZOS).convert('RGB').save(out)

if __name__ == '__main__':
    from PIL import Image, ImageDraw, ImageFont
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 34)
    rows = []
    for p in (100, 500, 900):
        R = triche.regles(p)
        G = triche.glyphes(R)
        base = {kk: [dict(st, p=[np.array([x / R['sx'], y]) for x, y in st['p']]) for st in v] for kk, v in G.items()}
        comp = composer(base, dict(R, sx=1.0))
        for kk, v in comp.items():
            G[kk] = [dict(st, p=[np.array([x * R['sx'], y]) for x, y in st['p']], caps=list(st['caps'])) for st in v]
        for t in ('éèêëàçñåø', 'ÉÀÇÑÅØ'):
            fn = 'tmp-acc.png'; render_poly(t, fn, G, R, k=0.22)
            im = Image.open(fn).convert('RGB'); ImageDraw.Draw(im).text((12, 8), str(p), font=F, fill=(255, 210, 60)); rows.append(im)
    os.remove('tmp-acc.png')
    W = max(r.width for r in rows)
    sheet = Image.new('RGB', (W, sum(r.height for r in rows)), (0, 0, 0))
    y = 0
    for r in rows: sheet.paste(r, (0, y)); y += r.height
    sheet.save('accents-essai2.png'); print(sheet.size)
