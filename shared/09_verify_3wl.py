import itertools, collections

def rook():
    V=[(i,j) for i in range(4) for j in range(4)]
    idx={v:k for k,v in enumerate(V)}
    E=set()
    for a in V:
        for b in V:
            if a!=b and (a[0]==b[0] or a[1]==b[1]): E.add((idx[a],idx[b]))
    return 16,E

def shrikhande():
    V=[(i,j) for i in range(4) for j in range(4)]
    idx={v:k for k,v in enumerate(V)}
    D={(1,0),(3,0),(0,1),(0,3),(1,1),(3,3)}
    E=set()
    for a in V:
        for b in V:
            if a!=b and ((b[0]-a[0])%4,(b[1]-a[1])%4) in D: E.add((idx[a],idx[b]))
    return 16,E

def check_srg(n,E):
    adj=[[False]*n for _ in range(n)]
    for u,v in E: adj[u][v]=True
    deg={sum(adj[u]) for u in range(n)}
    lam=set(); mu=set()
    for u in range(n):
        for v in range(n):
            if u==v: continue
            c=sum(1 for w in range(n) if adj[u][w] and adj[v][w])
            (lam if adj[u][v] else mu).add(c)
    return deg,lam,mu

def fwl2(n,E,rounds=12):
    """2-FWL, called 3-WL in the GNN literature."""
    adj=[[False]*n for _ in range(n)]
    for u,v in E: adj[u][v]=True
    c={}
    for u in range(n):
        for v in range(n):
            c[(u,v)] = 0 if u==v else (1 if adj[u][v] else 2)
    for _ in range(rounds):
        new={}
        for u in range(n):
            for v in range(n):
                multiset=sorted((c[(u,w)],c[(w,v)]) for w in range(n))
                new[(u,v)]=(c[(u,v)],tuple(multiset))
        # canonicalise to small ints
        order={k:i for i,k in enumerate(sorted(set(new.values())))}
        nxt={p:order[val] for p,val in new.items()}
        if len(set(nxt.values()))==len(set(c.values())) and _>0: 
            c=nxt; break
        c=nxt
    return collections.Counter(c.values())

def wl1(n,E,rounds=10):
    adj=collections.defaultdict(list)
    for u,v in E: adj[u].append(v)
    c={u:0 for u in range(n)}
    for _ in range(rounds):
        new={u:(c[u],tuple(sorted(c[w] for w in adj[u]))) for u in range(n)}
        order={k:i for i,k in enumerate(sorted(set(new.values())))}
        c={u:order[v] for u,v in new.items()}
    return collections.Counter(c.values())

for name,g in (('rook 4x4',rook()),('Shrikhande',shrikhande())):
    n,E=g
    print(name,' |E|/2 =',len(E)//2,' SRG(deg,lam,mu) =',check_srg(n,E))
print()
r=fwl2(*rook()); s=fwl2(*shrikhande())
print('1-WL  rook == Shrikhande ?', wl1(*rook())==wl1(*shrikhande()))
print('3-WL (2-FWL) colour histograms equal ?', r==s)
print('  rook       :', sorted(r.values()))
print('  Shrikhande :', sorted(s.values()))

print()
print('=== validation on pairs with known answers ===')
def cyc(ns):
    off=0; E=set(); n=sum(ns)
    for c in ns:
        for i in range(c):
            a,b=off+i,off+(i+1)%c
            E.add((a,b)); E.add((b,a))
        off+=c
    return n,E
c6=cyc([6]); c33=cyc([3,3])
print('C6 vs 2xC3   : 1-WL same? %s   3-WL same? %s   (expect: same, DIFFERENT)'
      %(wl1(*c6)==wl1(*c33), fwl2(*c6)==fwl2(*c33)))
c8=cyc([8]); c44=cyc([4,4])
print('C8 vs 2xC4   : 1-WL same? %s   3-WL same? %s   (expect: same, DIFFERENT)'
      %(wl1(*c8)==wl1(*c44), fwl2(*c8)==fwl2(*c44)))
# sanity: a graph against a relabelled copy of itself must agree
import random
n,E=shrikhande(); perm=list(range(n)); random.seed(0); random.shuffle(perm)
E2={(perm[u],perm[v]) for u,v in E}
print('Shrikhande vs relabelled self : 3-WL same? %s   (expect: same)'%(fwl2(n,E)==fwl2(n,E2)))
