# Les mesures d'Overshoot, graisse par graisse, lues dans ses fichiers.
import os
from functools import lru_cache
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen

RACINE = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))
GRAISSES = ['Calm', 'LightAir', 'LightBreeze', 'GentleBreeze', 'ModerateBreeze', 'FreshBreeze', 'StrongBreeze', 'Gale', 'Storm']
NOMS = ['Shtil', 'Tikhiy', 'Lyogkiy', 'Slabyy', 'Umerennyy', 'Svezhiy', 'Silnyy', 'Krepkiy', 'Shtorm']


def chemin(graisse, italique=False):
    return os.path.join(RACINE, 'overshoot', 'fonts', 'otf', f'Overshoot-{graisse}{"Italic" if italique else ""}.otf')


@lru_cache(None)
def police(graisse, italique=False):
    return TTFont(chemin(graisse, italique))


def points(font, nom):
    """Les points d'appui (débuts et fins de segments) du glyphe, arrondis."""
    rp = RecordingPen(); font.getGlyphSet()[nom].draw(rp)
    return [tuple(round(v) for v in a[-1]) for op, a in rp.value if a]


@lru_cache(None)
def mesures(graisse):
    f = police(graisse); gs = f.getGlyphSet(); hm = f['hmtx']
    xs = sorted({x for x, y in points(f, 'H')})
    e = points(f, 'E'); l = sorted({x for x, y in points(f, 'l')}); z = points(f, 'z')
    r = points(f, 'R'); a = points(f, 'a')
    # pied évasé du R : le bout du pied sur la ligne, et le fût droit de la jambe
    pied_r = max(x for x, y in r if y == 0)
    fut_r = max(x for x, y in r if 0 < y < 400)
    pied_a = max(x for x, y in a if y == 0)
    fut_a = max(x for x, y in a if 0 < y < 300)
    return {
        'fut_cap': xs[1] - xs[0], 'barre_cap': e[2][1], 'fut_min': l[1] - l[0], 'barre_min': z[2][1],
        'cap': f['OS/2'].sCapHeight, 'x': f['OS/2'].sxHeight,
        'approche_cap': hm['H'][1], 'approche_min': hm['l'][1], 'contre_H': xs[2] - xs[1],
        'chasse_M': hm['M'][0], 'chasse_m': hm['m'][0],
        'pied_cap': pied_r - fut_r, 'pied_min': pied_a - fut_a,
        'barre_H': sorted({y for x, y in points(f, 'H') if 0 < y < 730}),
        'jambage': 164,
    }


@lru_cache(None)
def penche(graisse):
    """La pente de l'italique d'Overshoot : x' = x + k*y + dx, mesurée sur H E L T I N."""
    import numpy as np
    up, it = police(graisse), police(graisse, True); A = []; B = []
    for n in ('H', 'E', 'L', 'T', 'I', 'N'):
        pu, pi = points(up, n), points(it, n)
        if len(pu) == len(pi):
            for (x, y), (xi, yi) in zip(pu, pi):
                A.append([y, 1]); B.append(xi - x)
    k, dx = np.linalg.lstsq(np.array(A, float), np.array(B, float), rcond=None)[0]
    return float(k), float(dx)
