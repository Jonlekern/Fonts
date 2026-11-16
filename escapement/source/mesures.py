# Les mesures de la police de lecture, graisse par graisse.
# Les traits viennent d'Overshoot (sa graisse sœur), ramenés aux hauteurs du texte.
from functools import lru_cache
from releve import releve

GRAISSES = (300, 400, 500, 600, 700)
NOMS = {300: 'Gotthard', 400: 'Albula', 500: 'Bernina', 600: 'Rigi', 700: 'Pilatus'}   # lignes de train suisses, de la moins raide à la plus raide
SOEUR = {300: 'LightBreeze', 400: 'GentleBreeze', 500: 'ModerateBreeze', 600: 'FreshBreeze', 700: 'StrongBreeze'}
CAP, X = 700, 504


@lru_cache(None)
def mesures(poids):
    o = releve(SOEUR[poids])
    fut_min = round(o['fut_min'] * X / o['x'])
    fut_cap = round(fut_min * o['fut_cap'] / o['fut_min'])        # le même rapport capitales / minuscules qu'Overshoot
    # l'espacement aéré : l'approche et le blanc du n se serrent un peu quand le trait grossit
    approche_min = round(65 - 0.08 * (fut_min - 88))
    contre_n = round(244 - 0.35 * (fut_min - 88))
    return {
        'upm': 1000, 'cap': CAP, 'x': X, 'asc': 740, 'desc': -220, 'depasse': 12,
        'fut_min': fut_min, 'fut_cap': fut_cap,
        'barre_min': round(0.85 * fut_min), 'barre_cap': round(0.85 * fut_cap),
        'pied': round(o['pied'] * X / o['x'] * 0.8),
        'expo': round(2 + (o['expo'] - 2) * 0.5, 3), 'expo_ovs': o['expo'],
        'approche_min': approche_min, 'approche_cap': approche_min + 10,
        'contre_n': contre_n, 'chasse_n': 2 * fut_min + contre_n + 2 * approche_min,
        'large_ovs': 1.22,
    }
