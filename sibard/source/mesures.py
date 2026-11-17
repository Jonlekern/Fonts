# Les mesures de Sibard, graisse par graisse.
GRAISSES = (300, 400, 500, 600, 700, 800, 900, 1000)
NOMS = {300: 'Frais', 400: 'Froid', 500: 'Gel', 600: 'Givre', 700: 'Glace', 800: 'Bise', 900: 'Banquise',
        1000: 'Brevine'}        # de plus en plus froid, jusqu'à La Brévine, la Sibérie de la Suisse
MAITRES = (300, 500, 900)          # les graisses dessinées ; les autres sont entre deux
PENTE = 14.0                       # degrés, à Vitesse 100

CAP, X, ASC, DESC = 700, 480, 740, -190


def _entre(p, a, b):
    """Valeur à la graisse p, entre la plus fine (a) et la plus grasse (b)."""
    return a + (b - a) * (p - 300) / 600


def mesures(p, taille=0.36, vitesse=0.0):
    fut = _entre(p, 46, 184) if p <= 900 else 184 + (p - 900) * 0.92      # jusqu'à 900 : le fût d'Époque ; au-delà, encore plus gras
    #                  # l'épaisseur moyenne ; le fût de droite fait fut × (1 + écart)
    m = dict(
        poids=p, cap=CAP, x=X, asc=ASC, desc=DESC,
        fut=fut,                                   # trait vertical
        barre=11 + fut * 0.10,                          # le contraste Art déco : les barres et les jonctions sont des filets
        dep=10,                                    # dépassement des rondes
        filet=_entre(p, 11, 24),                   # chrome : les deux filets
        blanc=_entre(p, 10, 22),                    # chrome : les blancs
        ecart=_entre(p, 0.62, 0.76),               # la gauche légère, la droite lourde : fût gauche = fût × (1 − écart), fût droit × (1 + écart)
        tension=1.2,                              # virages superelliptiques (1 = arc de cercle)
        taille=taille,                             # hauteur des barres (taille basse)
        coude=30,                     # petit rayon : les coudes
        app=_entre(p, 70, 112),                     # approche d'un fût
        appr=_entre(p, 56, 88),                    # approche d'une ronde
        large=_entre(p, 0, 150) + max(0, p - 900) * 1.6,      # les très gras s'élargissent encore : les contreformes restent ouvertes
        vitesse=vitesse,                           # 0 à 1 : le curseur Vitesse
        air=36 * vitesse,                          # à pleine vitesse, chaque lettre prend de l'air à gauche
        sillage=(0.62 * (_entre(p, 62, 40) + _entre(p, 44, 26)) + 36) * vitesse,   # longueur des traits de vitesse                    # les lettres s'élargissent avec la graisse
    )
    return m
