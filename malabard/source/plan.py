import sys;sys.path.insert(0,'.')
from stretch import *
TOLC=45
def cand_ys(cs,lo,hi):
    ys=sorted({round(p[1],2) for c in cs for p in c})
    cand=[y for y in ys if lo<=y<=hi]
    for a,b in zip(ys,ys[1:]):
        m=(a+b)/2
        if lo<=m<=hi: cand.append(m)
    return cand
def tolerant_cut(cs,lo,hi):
    mid=(lo+hi)/2
    for y in sorted(cand_ys(cs,lo,hi),key=lambda y:abs(y-mid)):
        if not runs_ok(cs,y): continue
        per=[]
        for c in cs:
            ys=[p[1] for p in c]
            if min(ys)<y<max(ys):
                best=None
                for yc in cand_ys([c],y-TOLC,y+TOLC):
                    r_=cut_ok([c],yc)
                    if r_ is not False and r_==0 and (best is None or abs(yc-y)<abs(best-y)): best=yc
                if best is None: per=None; break
                per.append(best)
            else: per.append(y)
        if per is not None: return per
    return None
def plan(cs,h):
    n=len(cs)
    a=find_cut(cs,0.1*h,0.48*h); b=find_cut(cs,0.52*h,0.9*h)
    if a is not None and b is not None and cut_ok(cs,a)==0 and cut_ok(cs,b)==0:
        return [[a]*n,[b]*n]
    y=find_cut(cs,0.15*h,0.85*h)
    if y is not None: return [[y]*n]
    a=tolerant_cut(cs,0.1*h,0.48*h); b=tolerant_cut(cs,0.52*h,0.9*h)
    if a and b: return [a,b]
    y=tolerant_cut(cs,0.15*h,0.85*h)
    return None if y is None else [y]
def stretch_glyph(cs,cuts,D):
    d=D/len(cuts)
    for cut in sorted(cuts,key=lambda c:-max(c)):
        cs=[apply_cut([c],y,d)[0] for c,y in zip(cs,cut)]
    return cs
