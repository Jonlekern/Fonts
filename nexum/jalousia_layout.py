import numpy as np
import droit
import jalousia as essai

def placer(word, G, R):
    GP = {ch: [st['p'] for st in v] for ch, v in G.items()}
    sauve = (essai.G, essai.cr, essai.GAP, essai.R)
    essai.G, essai.cr, essai.GAP, essai.R = GP, (lambda s, n=20: droit.dens(s)), R['gap'], R['rv']
    try:
        return essai.layout(word)
    finally:
        essai.G, essai.cr, essai.GAP, essai.R = sauve
