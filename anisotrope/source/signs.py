# Ponctuation et signes (sans les chiffres ni %, qui attendent les chiffres de Johnny)
from core import *
import caps

DR = round(ST * 0.62 + 4)              # rayon d'un point
MY = round(XH * 0.52)                  # axe des signes de calcul
MW = round(500 + 0.6 * ST)             # largeur des signes de calcul
AT = round(ST * 0.9)                   # épaisseur des petits traits

def pt(cx, cy, r=None): return dot(cx, cy, r or DR)

def comma_shape(x=0, y=0):
    """virgule : un point rond (vintage) qui file en coin coupé net (futur)"""
    r = DR
    tail = poly([(r * 0.15, r * 0.2), (r * 0.98, r * 0.15), (r * 0.6, -r * 1.25), (-r * 0.55, -r * 2.5), (-r * 0.2, -r * 1.25)])
    return mv(U(pt(0, 0, r), tail), x + r, y + r)

@reg('period', '.')
def g_period(): return out(pt(DR, DR), 'T', 'T')

@reg('comma', ',')
def g_comma(): return out(comma_shape(), 'T', 'T')

@reg('colon', ':')
def g_colon(): return out(U(pt(DR, DR), pt(DR, XH - DR)), 'T', 'T')

@reg('semicolon', ';')
def g_semicolon(): return out(U(comma_shape(), pt(DR, XH - DR)), 'T', 'T')

@reg('ellipsis', '…')
def g_ellipsis():
    g = round(DR * 2 + 0.9 * S_STEM)
    return out(U(pt(DR, DR), pt(DR + g, DR), pt(DR + 2 * g, DR)), 'T', 'T')

def excl_body(x=0):
    t0 = round(ST * 1.10); t1 = round(ST * 0.55); y1 = round(DR * 2 + 120)
    return poly([(x - t0 / 2, CAP), (x + t0 / 2, CAP), (x + t1 / 2, y1), (x - t1 / 2, y1)])

@reg('exclam', '!')
def g_exclam(): return out(U(excl_body(DR), pt(DR, DR)), 'T', 'T')

def quest_body():
    rx = round(0.36 * NW + 0.2 * ST); ry = round(CAP * 0.24); cx = rx; cy = CAP + OV - ry
    arc = I(ring(cx, cy, rx, ry, r=0), pie(cx, cy, -90, 165))
    x0 = cx - ST / 2; y1 = round(DR * 2 + 120)
    neck = poly([(x0, cy - ry + TH), (x0 + ST, cy - ry + TH), (x0 + ST * 0.8, y1), (x0 + ST * 0.2, y1)])
    return U(arc, neck, pt(cx, DR)), cx

@reg('question', '?')
def g_question(): return out(quest_body()[0], 'T', 'T')

def turn(p, yc):
    b = p.bounds; return rot(p, 180, (b[0] + b[2]) / 2, yc)

@reg('exclamdown', '¡')
def g_exclamdown():
    p = turn(U(excl_body(DR), pt(DR, DR)), CAP / 2)
    b = p.bounds; return out(mv(p, 0, XH - b[3]), 'T', 'T')

@reg('questiondown', '¿')
def g_questiondown():
    p = turn(quest_body()[0], CAP / 2)
    b = p.bounds; return out(mv(p, 0, XH - b[3]), 'T', 'T')

def tick(x=0, top=CAP + 10):
    t0 = round(ST * 0.95); t1 = round(ST * 0.55)
    return poly([(x - t0 / 2, top), (x + t0 / 2, top), (x + t1 / 2, top - 260), (x - t1 / 2, top - 260)])

@reg('quotesingle', "'")
def g_quotesingle(): return out(tick(), 'T', 'T')

@reg('quotedbl', '"')
def g_quotedbl(): return out(U(tick(), tick(round(ST * 1.9))), 'T', 'T')

def high_comma(x=0):
    p = comma_shape(); b = p.bounds; return mv(p, x - b[0], CAP + 10 - b[3])

@reg('quoteright', '’')
def g_quoteright(): return out(high_comma(), 'T', 'T')

@reg('quoteleft', '‘')
def g_quoteleft():
    p = turn(comma_shape(), 0); b = p.bounds; return out(mv(p, -b[0], CAP + 10 - b[3]), 'T', 'T')

@reg('quotesinglbase', '‚')
def g_quotesinglbase(): return out(comma_shape(), 'T', 'T')

def pair(p):
    b = p.bounds; g = (b[2] - b[0]) + round(ST * 0.6); return U(p, mv(p, g, 0))

@reg('quotedblright', '”')
def g_quotedblright(): return out(pair(high_comma()), 'T', 'T')

@reg('quotedblleft', '“')
def g_quotedblleft(): return out(pair(g_quoteleft()[0]), 'T', 'T')

@reg('quotedblbase', '„')
def g_quotedblbase(): return out(pair(comma_shape()), 'T', 'T')

def chevron(w, h, t, x=0, y=None, left=True):
    y = MY if y is None else y
    p = U(bar(x, y, x + w, y + h, t), bar(x, y, x + w, y - h, t))
    p = I(p, rect(x - t * 0.35, y - h, x + w + t, y + h))
    return p if left else flipx(p, x + w / 2)

@reg('guilsinglleft', '‹')
def g_guilsinglleft(): return out(chevron(170, 150, ST * 0.95, y=round(XH * 0.48)), 'T', 'T')

@reg('guilsinglright', '›')
def g_guilsinglright(): return out(chevron(170, 150, ST * 0.95, y=round(XH * 0.48), left=False), 'T', 'T')

@reg('guillemotleft', '«')
def g_guillemotleft():
    c = chevron(170, 150, ST * 0.95, y=round(XH * 0.48)); return out(U(c, mv(c, 150 + ST * 0.7)), 'T', 'T')

@reg('guillemotright', '»')
def g_guillemotright():
    c = chevron(170, 150, ST * 0.95, y=round(XH * 0.48), left=False); return out(U(c, mv(c, 150 + ST * 0.7)), 'T', 'T')

DASH_Y = round(XH * 0.50)
DT = round(TH * 1.2)
@reg('hyphen', '-')
def g_hyphen(): return out(rect(0, DASH_Y - DT / 2, round(0.52 * NW + 40), DASH_Y + DT / 2), 'T', 'T')

@reg('endash', '–')
def g_endash(): return out(rect(0, DASH_Y - DT / 2, 500, DASH_Y + DT / 2), 30, 30)

@reg('emdash', '—')
def g_emdash(): return out(rect(0, DASH_Y - DT / 2, 940, DASH_Y + DT / 2), 30, 30)

PB, PT = DESC + 40, ASC + 40
def paren(left=True):
    """parenthèse : croissant, épais au milieu, effilé aux bouts"""
    h = (PT - PB) / 2; cy = PB + h; rx = round(h * 0.70); cx = rx
    p = D(ellipse(cx, cy, rx, h), ellipse(cx + ST * 0.9, cy, rx, h - 8))
    p = I(p, rect(-5, PB - 5, cx, PT + 5))
    return p if left else flipx(p, cx / 2)

@reg('parenleft', '(')
def g_parenleft(): return out(paren(), 'T', 'T')

@reg('parenright', ')')
def g_parenright(): return out(paren(False), 'T', 'T')

def bracket(left=True):
    w = round(170 + 0.4 * ST)
    p = U(rect(0, PB, ST, PT), rect(0, PB, w, PB + TH), rect(0, PT - TH, w, PT))
    return p if left else flipx(p, w / 2)

@reg('bracketleft', '[')
def g_bracketleft(): return out(bracket(), 'P', 'T')

@reg('bracketright', ']')
def g_bracketright(): return out(bracket(False), 'T', 'P')

def brace(left=True):
    t = round(ST * 0.9); w = round(190 + 0.3 * ST); cy = (PB + PT) / 2; xm = w * 0.45
    up = U(rect(xm, cy + 70, xm + t, PT - 90), I(ring(xm + 90 + t / 2, PT - 90, 90 + t / 2, 90, sx=t, sy=TH, r=0), rect(xm, PT - 90, xm + 90 + t, PT + 5)))
    lo = flipy(up, cy)
    mid = poly([(0, cy), (xm + t * 0.2, cy + 90), (xm + t, cy + 90), (xm + t, cy - 90), (xm + t * 0.2, cy - 90)])
    p = U(up, lo, mid)
    return p if left else flipx(p, (xm + 90 + t) / 2)

@reg('braceleft', '{')
def g_braceleft(): return out(brace(), 'T', 'T')

@reg('braceright', '}')
def g_braceright(): return out(brace(False), 'T', 'T')

@reg('slash', '/')
def g_slash():
    t = round(ST * 0.9); return out(bar(0, PB + 60, round(330 + 0.3 * ST), PT - 40, t), 'T', 'T')

@reg('backslash', '\\')
def g_backslash():
    t = round(ST * 0.9); return out(bar(round(330 + 0.3 * ST), PB + 60, 0, PT - 40, t), 'T', 'T')

@reg('bar', '|')
def g_bar(): return out(rect(0, PB, round(ST * 0.85), PT), 'P', 'P')

@reg('underscore', '_')
def g_underscore(): return out(rect(0, -150, 520, -150 + TH), 10, 10)

# signes de calcul
@reg('plus', '+')
def g_plus():
    h = MW / 2; t = round(TH * 1.15)
    return out(U(rect(0, MY - t / 2, MW - 2 * 60, MY + t / 2), rect(h - 60 - t / 2, MY - h + 60, h - 60 + t / 2, MY + h - 60)), 'T', 'T')

@reg('uni2212', '−')
def g_minus():
    t = round(TH * 1.15); return out(rect(0, MY - t / 2, MW - 120, MY + t / 2), 'T', 'T')

@reg('equal', '=')
def g_equal():
    t = round(TH * 1.15); g = round(70 + 0.3 * ST)
    return out(U(rect(0, MY + g - t / 2, MW - 120, MY + g + t / 2), rect(0, MY - g - t / 2, MW - 120, MY - g + t / 2)), 'T', 'T')

@reg('multiply', '×')
def g_multiply():
    s = round((MW - 120) * 0.72); t = round(TH * 1.15)
    p = U(bar(0, MY - s / 2, s, MY + s / 2, t * 1.25), bar(s, MY - s / 2, 0, MY + s / 2, t * 1.25))
    return out(I(p, rect(-100, MY - s / 2, s + 100, MY + s / 2)), 'T', 'T')

@reg('divide', '÷')
def g_divide():
    t = round(TH * 1.15); w = MW - 120; r = round(DR * 0.85); g = round(110 + 0.5 * ST)
    return out(U(rect(0, MY - t / 2, w, MY + t / 2), pt(w / 2, MY + g, r), pt(w / 2, MY - g, r)), 'T', 'T')

@reg('less', '<')
def g_less(): return out(chevron(MW - 140, 190, TH * 1.25, y=MY), 'T', 'T')

@reg('greater', '>')
def g_greater(): return out(chevron(MW - 140, 190, TH * 1.25, y=MY, left=False), 'T', 'T')

@reg('asciitilde', '~')
def g_asciitilde():
    w = MW - 120; a = 48; t = round(TH * 1.2); n = 40
    top = [(w * i / n, MY - a * math.sin(math.pi * 2 * i / n) + t / 2) for i in range(n + 1)]
    bot = [(w * i / n, MY - a * math.sin(math.pi * 2 * i / n) - t / 2) for i in range(n, -1, -1)]
    p = poly(top + bot)
    return out(p, 'T', 'T')

@reg('asciicircum', '^')
def g_asciicircum():
    w = round(MW * 0.75); h = 230; t = round(TH * 1.2)
    p = U(bar(0, CAP - h, w / 2, CAP, t), bar(w, CAP - h, w / 2, CAP, t))
    return out(I(p, rect(-100, CAP - h, w + 100, CAP)), 'T', 'T')

@reg('asterisk', '*')
def g_asterisk():
    cy = CAP - 150; L = 150; ps = []
    for k in range(5):
        a = math.radians(90 + 72 * k); c, s = math.cos(a), math.sin(a)
        t0, t1 = ST * 0.35, ST * 0.85
        px, py = -s, c
        ps.append(poly([(px * t0 / 2, py * t0 / 2), (c * L + px * t1 / 2, s * L + py * t1 / 2),
                        (c * L - px * t1 / 2, s * L - py * t1 / 2), (-px * t0 / 2, -py * t0 / 2)]))
    return out(mv(U(*ps, dot(0, 0, ST * 0.4)), 200, cy), 'T', 'T')

@reg('numbersign', '#')
def g_numbersign():
    w = round(MW * 0.95); t = round(TH * 1.15); s = round(ST * 0.85)
    v1 = bar(w * 0.30, 0, w * 0.40, CAP * 0.92, s); v2 = bar(w * 0.62, 0, w * 0.72, CAP * 0.92, s)
    h1 = rect(0, CAP * 0.30, w, CAP * 0.30 + t); h2 = rect(w * 0.06, CAP * 0.62, w * 1.06, CAP * 0.62 + t)
    return out(U(v1, v2, h1, h2), 'T', 'T')

@reg('periodcentered', '·')
def g_periodcentered(): return out(pt(DR, MY), 'T', 'T')

@reg('bullet', '•')
def g_bullet(): return out(pt(DR * 1.5, MY, DR * 1.5), 'T', 'T')

@reg('degree', '°')
def g_degree():
    r = round(104 + 0.35 * ST); return out(ring(r, CAP - r, r, r, sx=TH * 0.95, sy=TH * 0.8, r=0), 'T', 'T')

def circle_mark(inner):
    R = 380; cy = CAP / 2 + 20
    o = ring(R, cy, R, R, sx=TH, sy=TH, r=0)
    ib = inner.bounds; s = 0.52
    inn = xf(inner, (s, 0, 0, s, 0, 0)); b = inn.bounds
    inn = mv(inn, R - (b[0] + b[2]) / 2, cy - (b[1] + b[3]) / 2)
    return U(o, inn)

@reg('copyright', '©')
def g_copyright(): return out(circle_mark(caps.g_C()[0]), 'O', 'O')

@reg('registered', '®')
def g_registered(): return out(circle_mark(caps.g_R()[0]), 'O', 'O')

@reg('trademark', '™')
def g_trademark():
    s = 0.42
    t = xf(caps.g_T()[0], (s, 0, 0, s, 0, 0)); m = xf(caps.g_M()[0], (s, 0, 0, s, 0, 0))
    tb = t.bounds; mb = m.bounds
    m = mv(m, tb[2] + 40 - mb[0], 0)
    p = U(t, m); b = p.bounds
    return out(mv(p, 0, CAP - b[3]), 'T', 'T')

@reg('section', '§')
def g_section():
    # deux s empilés qui se chevauchent à moitié : le classique
    import lower
    s = lower.g_s()[0]; b = s.bounds; h = b[3] - b[1]
    sc = (CAP + 10) / (h * 1.5); s = xf(s, (sc, 0, 0, sc, 0, 0)); b = s.bounds; h = b[3] - b[1]
    up = mv(s, 0, CAP + 10 - b[3]); lo = mv(s, 0, CAP + 10 - b[3] - h * 0.5)
    return out(U(up, lo), 'T', 'T')

@reg('paragraph', '¶')
def g_paragraph():
    w = round(0.82 * NW); t = round(ST * 0.85)
    bowlp = ellipse(w * 0.42, CAP - 190, w * 0.42, 190)
    return out(U(rect(w * 0.48, PB + 40, w * 0.48 + t, CAP), rect(w - t, PB + 40, w, CAP), I(bowlp, rect(-10, 0, w * 0.48 + 2, CAP + 5)),
                 rect(w * 0.42, CAP - TH, w, CAP)), 'O', 'P')

@reg('ampersand', '&')
def g_ampersand():
    # forme « Et » : le c de la police agrandi à la hauteur des capitales, et un t dont la barre le traverse
    import lower
    sc = CAP / (XH + 2 * OV); c = xf(lower.g_c()[0], (sc, 0, 0, sc, 0, -OV * sc + OV))
    b = c.bounds; cy = (b[1] + b[3]) / 2
    xs = b[2] + round(0.55 * ST); top = CAP + 30; h = 100
    t = U(stem(xs, h, top - 40), poly([(xs, top - 40), (xs + ST, top), (xs + ST, top - 70), (xs, top - 90)]))
    barre = rect(b[2] - 60, cy - TH / 2, xs + ST + round(W * 1.8), cy + TH / 2)
    hook = hook_r(xs, 0, h, round(40 + 0.3 * ST))
    return out(U(c, t, barre, hook), 'O', 'T')

@reg('at', '@')
def g_at():
    R = 430; cy = CAP / 2 - 40; cx = R
    outer = I(ring(cx, cy, R, R, sx=TH * 1.05, sy=TH * 0.95, r=0), pie(cx, cy, -25, 305))
    # un petit o et un fût, comme un a à un étage
    r_ = 150; ox = cx - 30; oy = cy
    o = ring(ox, oy, r_, r_ + 10, sx=ST * 0.72, sy=TH * 0.75, r=0)
    xs = ox + r_ - ST * 0.72
    st_ = rect(xs, cy - 150, xs + ST * 0.72, cy + 150)
    tail = I(ring(xs + 150, cy - 60, 150 + ST * 0.36, 110, sx=ST * 0.72, sy=TH * 0.8, r=0), rect(xs - 10, cy - 200, cx + 450, cy - 60))
    return out(U(outer, o, st_, tail), 'O', 'O')

@reg('dollar', '$')
def g_dollar():
    s = caps.g_S()[0]; b = s.bounds; cx = (b[0] + b[2]) / 2; t = round(ST * 0.7)
    return out(U(s, rect(cx - t / 2, -120, cx + t / 2, 30), rect(cx - t / 2, CAP - 30, cx + t / 2, CAP + 120)), 'T', 'T')

@reg('cent', '¢')
def g_cent():
    import lower
    c = lower.g_c()[0]; b = c.bounds; cx = (b[0] + b[2]) / 2; t = round(ST * 0.7)
    return out(U(c, rect(cx - t / 2, -130, cx + t / 2, 30), rect(cx - t / 2, XH - 30, cx + t / 2, XH + 130)), 'O', 'T')

@reg('Euro', '€')
def g_Euro():
    c = caps.g_C()[0]; b = c.bounds; t = round(TH * 1.05)
    return out(U(c, rect(b[0] - 70, CAP * 0.58, b[0] + 360, CAP * 0.58 + t), rect(b[0] - 70, CAP * 0.38, b[0] + 330, CAP * 0.38 + t)), 'T', 'T')

@reg('yen', '¥')
def g_yen():
    y = caps.g_Y()[0]; b = y.bounds; t = round(TH * 1.0)
    return out(U(y, rect(b[0] + 90, CAP * 0.32, b[2] - 90, CAP * 0.32 + t), rect(b[0] + 90, CAP * 0.18, b[2] - 90, CAP * 0.18 + t)), 'D', 'D')

@reg('sterling', '£')
def g_sterling():
    x0 = 90; top = CAP; h = 130; reach = round(120 + 0.4 * ST)
    o = ellipse(x0 + ST + reach - 40, top - h, reach + ST - 40, h + OV)
    i = ellipse(x0 + ST + reach - 40, top - h - 4, reach - 40, h + OV - TH)
    crook = I(D(o, i), rect(x0, top - h, x0 + ST + reach + 10, top + OV + 5))
    s = rect(x0, TH, x0 + ST, top - h + 2)
    w = round(0.95 * NW)
    base = rect(0, 0, w, TH); cross = rect(0, CAP * 0.40, x0 + ST + 160, CAP * 0.40 + TH)
    return out(U(crook, s, base, cross, caps.beak(w, TH, dy=1)), 'T', 'T')

@reg('uni00A0', ' ')
def g_nbsp(): return out(P(), 0, 0)

def small_zero(sc=0.52):
    import digits
    z = digits.g_zero()[0]; return xf(z, (sc, 0, 0, sc, 0, 0))

@reg('percent', '%')
def g_percent():
    z = small_zero(); b = z.bounds; zw = b[2] - b[0]; zh = b[3] - b[1]
    gap = round(90 + 0.3 * ST)
    top = mv(z, 0, CAP - zh); bot = mv(z, zw + gap, 0)
    d = I(bar(zw + 8, 0, zw + gap - 8, CAP, ST * 0.72), rect(-50, 0, zw * 2 + gap + 50, CAP))      # la barre passe entre les deux zéros
    return out(U(top, bot, d), 'T', 'T')

@reg('perthousand', '‰')
def g_perthousand():
    p = g_percent()[0]; z = small_zero(); b = z.bounds; zw = b[2] - b[0]
    pb = p.bounds
    return out(U(p, mv(z, pb[2] + 60 - b[0], 0)), 'T', 'T')

