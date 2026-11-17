# Les mesures d'Époque, graisse par graisse.
GRAISSES = (300, 400, 500, 600, 700, 800, 900)
NOMS = {300: 'Forsthaus', 400: 'Bethlehem', 500: 'Eichholz', 600: 'Eymatt', 700: 'Wohlenrampe',
        800: 'Jordenrampe', 900: 'Glasbrunnen'}        # le tour du Bremgarten, du virage le plus lent à la section la plus rapide
MAITRES = (300, 500, 900)          # les graisses dessinées ; les autres sont entre deux
PENTE = 14.0                       # degrés, à Vitesse 100

CAP, X, ASC, DESC = 700, 480, 740, -190


def _entre(p, a, b):
    """Valeur à la graisse p, entre la plus fine (a) et la plus grasse (b)."""
    return a + (b - a) * (p - 300) / 600


def mesures(p, taille=0.36):
    fut = _entre(p, 70, 186)
    m = dict(
        poids=p, cap=CAP, x=X, asc=ASC, desc=DESC,
        fut=fut,                                   # trait vertical
        barre=fut * _entre(p, 0.90, 0.74),         # trait horizontal, un peu plus fin pour l'œil
        dep=10,                                    # dépassement des rondes
        filet=_entre(p, 11, 24),                   # chrome : les deux filets
        blanc=_entre(p, 10, 22),                    # chrome : les blancs
        tension=1.16,                              # virages superelliptiques (1 = arc de cercle)
        taille=taille,                             # hauteur des barres (taille basse)
        coude=fut * 0.62 + 14,                     # petit rayon : les coudes
        app=_entre(p, 62, 40),                     # approche d'un fût
        appr=_entre(p, 44, 26),                    # approche d'une ronde
        large=_entre(p, 0, 150),                    # les lettres s'élargissent avec la graisse
    )
    return m
