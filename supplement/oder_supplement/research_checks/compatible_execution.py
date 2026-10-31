"""Finite verification of compatible-execution preservation synthesis. Python stdlib."""
import itertools, json
PRODUCT=list(itertools.product((0,1),repeat=2))

def signatures(n, mask, features):
    return [tuple(features[k][2][x] for k in range(len(features)) if mask>>k&1 and features[k][0]==i) for i in range(2) for x in range(n)]

def generated(n,mask,features):
    sig=signatures(n,mask,features)
    keys=[(i,sig[i*n+x]) for i in range(2) for x in range(n)]
    unique=list(dict.fromkeys(keys))
    tables=[]
    for bits in itertools.product((0,1),repeat=len(unique)):
        d=dict(zip(unique,bits))
        tables.append(tuple((d[keys[x]],d[keys[n+x]]) for x in range(n)))
    return tables

def repaired(witness,n,mask,features):
    for i in range(2):
        for x,y in itertools.combinations(range(n),2):
            if witness[x][i]!=witness[y][i] and not any(mask>>k&1 and f[0]==i and f[2][x]!=f[2][y] for k,f in enumerate(features)):
                return False
    return True

def check():
    n=3
    features=[(i,c,v) for i in range(2) for c,v in [(1,(1,0,0)),(2,(0,1,0))]]
    policies={m:generated(n,m,features) for m in range(16)}
    subsets=[tuple(p for k,p in enumerate(PRODUCT) if m>>k&1) for m in range(1,16)]
    cases=0
    for J in itertools.product(subsets,repeat=n):
        witnesses=list(itertools.product(*J))
        for m in range(16):
            direct=any(all(w[x] in J[x] for x in range(n)) for w in policies[m])
            cover=any(repaired(w,n,m,features) for w in witnesses)
            assert direct==cover,(J,m)
            cases+=1
    X=list(itertools.product((0,1),repeat=2))
    J=[tuple(p for p in PRODUCT if sum(p)==sum(x)) for x in X]
    fs=[(i,1,tuple(x[b] for x in X)) for i in range(2) for b in range(2)]
    feasible=[]; shared=[]
    for m in range(16):
        cost=m.bit_count()
        if any(all(w[x] in J[x] for x in range(4)) for w in generated(4,m,fs)): feasible.append((cost,m))
        sig=signatures(4,m,fs)
        # Each actor must select the identical complete joint tuple.
        edges=[(x,y) for x,y in itertools.combinations(range(4),2) if any(sig[i*4+x]==sig[i*4+y] for i in range(2))]
        components=[{x} for x in range(4)]
        for x,y in edges:
            a=next(c for c in components if x in c);b=next(c for c in components if y in c)
            if a is not b: a.update(b);components.remove(b)
        if all(set.intersection(*(set(J[x]) for x in c)) for c in components): shared.append((cost,m))
    assert min(feasible)[0]==2 and min(shared)[0]==4
    # Menus and global selector restrictions break bare witness coverage.
    unrestricted_success=any(all(w[x] in J[x] for x in range(4)) for w in generated(4,15,fs))
    constant_only_success=any(all(p in j for j in J) for p in PRODUCT)
    assert unrestricted_success and not constant_only_success
    return {'exhaustive_relation_feature_cases':cases,'disagreements':0,'example_compatible_min_cost':min(feasible)[0], 'example_shared_tuple_min_cost':min(shared)[0], 'compatible_min_masks':[m for c,m in feasible if c==2], 'shared_min_masks':[m for c,m in shared if c==4], 'global_selector_restriction_counterexample_confirmed':True}
