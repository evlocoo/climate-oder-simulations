from itertools import product, permutations
from functools import lru_cache

def covers_min(universe, supports):
    supports=tuple(sorted(set(supports),reverse=True))
    supports=tuple(x for x in supports if not any(x!=y and x|y==y for y in supports))
    bybit={b:tuple(x for x in supports if x>>b&1) for b in range(universe.bit_length())}
    @lru_cache(None)
    def solve(left):
        if not left:return 0
        b=min((b for b in bybit if left>>b&1),key=lambda b:len(bybit[b]))
        return 1+min(solve(left&~x) for x in bybit[b])
    return solve(universe)

def verify(n,m,costs,T):
    # Direct policies: ordered endpoint queries, stop on successful reply, otherwise terminal guess.
    policy_supports=[]
    for L in range(n+1):
        for seq in permutations(range(n),L):
            if sum(costs[a] for a in seq)>T:continue
            for guess in range(m):
                good=0
                for a,b in product(range(n),range(m)):
                    # Simulate observations until correct endpoint or final guess.
                    target=None
                    for q in seq:
                        if q==a:target=b;break
                    if target==b or target is None and guess==b:good|=1<<(a*m+b)
                policy_supports.append(good)
    direct=covers_min((1<<(n*m))-1,policy_supports)
    batches=[mask for mask in range(1,1<<n) if sum(costs[a] for a in range(n) if mask>>a&1)<=T]
    B=covers_min((1<<n)-1,batches) if batches and all(any(mask>>a&1 for mask in batches) for a in range(n)) else float('inf')
    return direct,min(m,B)


def partitions(size,kmax):
    cells=[]
    def rec(i):
        if i==size:yield tuple(cells);return
        for j in range(len(cells)):
            cells[j]|=1<<i
            yield from rec(i+1)
            cells[j]^=1<<i
        if len(cells)<kmax:
            cells.append(1<<i)
            yield from rec(i+1)
            cells.pop()
    yield from rec(0)

def partition_verify(n,m,costs,T):
    supports=[]
    for L in range(n+1):
        for seq in permutations(range(n),L):
            if sum(costs[a] for a in seq)>T:continue
            for guess in range(m):
                mask=sum(1<<(a*m+b) for a,b in product(range(n),range(m)) if a in seq or b==guess)
                supports.append(mask)
    # Every arbitrary encoding is a partition; m categories encoding target gives upper bound.
    best=m; checked=0
    for cells in partitions(n*m,m-1):
        checked+=1
        if len(cells)>=best:continue
        if all(any(cell&~support==0 for support in supports) for cell in cells):best=len(cells)
    return best,checked

def check():
    cases=parts=0
    for n,m in ((2,2),(2,3),(3,2),(3,3),(4,3)):
     for costs in product((1,2),repeat=n):
      for T in range(sum(costs)+1):
       direct,formula=verify(n,m,costs,T)
       encoded,count=partition_verify(n,m,costs,T)
       cases+=1;parts+=count
       assert direct==formula==encoded,(n,m,costs,T,direct,formula,encoded)
    return {'models':cases,'arbitrary_encoding_partitions_checked':parts,'disagreements':0}
