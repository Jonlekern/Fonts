# Allonge les parties verticales : coupe horizontale là où tout le contour est vertical, on insère D.
import sys
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
TOL=2; EPS=0.5

def contours_of(font,gn):
    gs=font.getGlyphSet(); rp=DecomposingRecordingPen(gs); gs[gn].draw(rp)
    return parse(rp.value)
def parse(value):
    cs=[];cur=None
    for op,args in value:
        if op=='moveTo': cur=[(args[0][0],args[0][1],True)]
        elif op=='lineTo': cur.append((args[0][0],args[0][1],True))
        elif op=='qCurveTo':
            pts=list(args)
            if pts[-1] is None: # contour fermé sans point on
                pts=pts[:-1]; offs=pts
                # convertir : points implicites
                n=len(offs); cur=[]
                for i in range(n):
                    a=offs[i];b=offs[(i+1)%n]
                    cur.append(((a[0]+b[0])/2,(a[1]+b[1])/2,True)); cur.append((b[0],b[1],False))
                continue
            offs=pts[:-1]
            for i,o in enumerate(offs):
                if i>0:
                    p=offs[i-1]; cur.append(((p[0]+o[0])/2,(p[1]+o[1])/2,True))
                cur.append((o[0],o[1],False))
            cur.append((pts[-1][0],pts[-1][1],True))
        elif op=='curveTo': raise Exception('cubique')
        elif op=='closePath' or op=='endPath':
            if cur and len(cur)>1 and cur[-1][:2]==cur[0][:2] and cur[-1][2]: cur.pop()
            cs.append(cur); cur=None
    return cs

def segments(c):
    # liste de segments : ('L',p0,p1) ou ('Q',p0,c,p1) ; c est un cycle de points avec on/off alternés
    n=len(c); i0=next(i for i,p in enumerate(c) if p[2]); segs=[]
    k=0
    while k<n:
        i=(i0+k)%n; j=(i+1)%n
        if c[j][2]: segs.append(('L',c[i],c[j])); k+=1
        else: segs.append(('Q',c[i],c[j],c[(j+1)%n])); k+=2
    return segs

def cut_ok(cs,y):
    pen_=[0]
    for c in cs:
        n=len(c)
        for k,p in enumerate(c):
            if p[2] and abs(p[1]-y)<=EPS:
                a=c[k-1]; b=c[(k+1)%n]
                if abs(a[1]-y)<=EPS or abs(b[1]-y)<=EPS:
                    pen_[0]+=2; continue
                if (a[1]-y)*(b[1]-y)>0: return False                     # extremum vertical
                for q_ in (a,b):
                    if abs(q_[0]-p[0])>TOL:
                        if not q_[2]: return False          # courbe pas verticale
                        if abs(q_[1]-p[1])<0.6*abs(q_[0]-p[0]): return False
                        pen_[0]+=1
        for s in segments(c):
            if s[0]=='L':
                p0,p1=s[1],s[2]
                if min(p0[1],p1[1])+EPS<y<max(p0[1],p1[1])-EPS and abs(p0[0]-p1[0])>TOL:
                    dx=abs(p0[0]-p1[0]); dy=abs(p0[1]-p1[1])
                    if dy<0.6*dx: return False
                    pen_[0]+=1
            else:
                p0,q,p1=s[1],s[2],s[3]
                ys=[p0[1],q[1],p1[1]]
                if min(ys)+EPS<y<max(ys)-EPS:
                    # le segment traverse y ailleurs qu'en ses extrémités ?
                    if not (abs(p0[1]-y)<=EPS or abs(p1[1]-y)<=EPS): return False
                    # traverse en un point intérieur aussi ?
                    a=p0[1]-2*q[1]+p1[1]; bb=2*(q[1]-p0[1]); cc=p0[1]-y
                    import math
                    roots=[]
                    if abs(a)<1e-9:
                        if abs(bb)>1e-9: roots=[-cc/bb]
                    else:
                        disc=bb*bb-4*a*cc
                        if disc>=0: roots=[(-bb+s_*math.sqrt(disc))/(2*a) for s_ in (1,-1)]
                    if any(0.02<t<0.98 for t in roots): return False
    return pen_[0]

import math
def xs_at(cs,y):
    xs=[]
    for c in cs:
        for sg in segments(c):
            if sg[0]=='L':
                p0,p1=sg[1],sg[2]
                if (p0[1]-y)*(p1[1]-y)<0: xs.append(p0[0]+(y-p0[1])*(p1[0]-p0[0])/(p1[1]-p0[1]))
            else:
                p0,q,p1=sg[1],sg[2],sg[3]
                a=p0[1]-2*q[1]+p1[1]; b=2*(q[1]-p0[1]); cc=p0[1]-y
                ts=[]
                if abs(a)<1e-9:
                    if abs(b)>1e-9: ts=[-cc/b]
                else:
                    d=b*b-4*a*cc
                    if d>=0: ts=[(-b+sg_*math.sqrt(d))/(2*a) for sg_ in (1,-1)]
                for t in ts:
                    if 0<=t<1: xs.append((1-t)**2*p0[0]+2*t*(1-t)*q[0]+t*t*p1[0])
    return sorted(xs)
MAXRUN=400
def runs_ok(cs,y):
    for yy in (y-1.3,y+1.3):
        xs=xs_at(cs,yy)
        for a,b in zip(xs[::2],xs[1::2]):
            if b-a>MAXRUN: return False
    return True
def find_cut(cs,lo,hi):
    ys=sorted({round(p[1],2) for c in cs for p in c})
    cand=[y for y in ys if lo<=y<=hi]
    for a,b in zip(ys,ys[1:]):
        m=(a+b)/2
        if lo<=m<=hi: cand.append(m)
    mid=(lo+hi)/2
    best=None
    for y in cand:
        r=cut_ok(cs,y)
        if r is False or not runs_ok(cs,y): continue
        sc=(r,abs(y-mid))
        if best is None or sc<best[0]: best=(sc,y)
    return best and best[1]

def apply_cut(cs,y,D):
    out=[]
    def on(p): return abs(p[1]-y)<=EPS
    def side(c,k,step):
        n=len(c); j=k
        for _ in range(n):
            j=(j+step)%n
            if not on(c[j]): return 1 if c[j][1]>y else -1
        return -1
    for c in cs:
        n=len(c); nc=[]
        for k,p in enumerate(c):
            if on(p):
                sa=side(c,k,-1); sb=side(c,k,1)
                pa=on(c[k-1]); pb=on(c[(k+1)%n])
                if sa==sb: nc.append((p[0],p[1]+D,p[2]) if sa>0 or (sa<0 and (pa or pb)) else p)
                elif not pa and not pb:
                    if sa<0: nc+= [p,(p[0],p[1]+D,True)]
                    else: nc+= [(p[0],p[1]+D,True),p]
                elif pa and not pb:   # fin de suite : on rejoint le côté b
                    if sb>0: nc+= [p,(p[0],p[1]+D,True)] if sa<0 else [(p[0],p[1]+D,True)]
                    else: nc+= [(p[0],p[1]+D,True),p] if sa>0 else [p]
                else:                 # début de suite (ou milieu) : on garde le côté a
                    nc.append((p[0],p[1]+D,p[2]) if sa>0 else p)
            elif p[1]>y: nc.append((p[0],p[1]+D,p[2]))
            else: nc.append(p)
        out.append(nc)
    return out

def draw(cs,pen):
    for c in cs:
        i0=next(i for i,p in enumerate(c) if p[2]); c=c[i0:]+c[:i0]
        pen.moveTo(c[0][:2]); k=1; n=len(c)
        while k<n:
            if c[k][2]: pen.lineTo(c[k][:2]); k+=1
            else:
                nxt=c[(k+1)%n]; pen.qCurveTo(c[k][:2],nxt[:2]); k+=2
        pen.closePath()
