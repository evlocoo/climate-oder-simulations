"""Independent exact partition/policy check of heterogeneous locator frontier."""
from functools import lru_cache
from itertools import product
import json

def partitions(n):
    def rec(i, blocks):
        if i == n:
            yield tuple(blocks)
            return
        for j in range(len(blocks)):
            b = blocks[j]
            blocks[j] |= 1 << i
            yield from rec(i+1, blocks)
            blocks[j] = b
        blocks.append(1 << i)
        yield from rec(i+1, blocks)
        blocks.pop()
    yield from rec(0, [])

def verify(n, m, durations):
    records = list(product(range(n), range(m)))
    encodings = sorted(partitions(n*m), key=len)
    endpoint_parts = list(partitions(n))
    checked = 0
    for budget in range(sum(durations)+1):
        @lru_cache(None)
        def feasible(mask, remaining):
            xs = [records[i] for i in range(n*m) if mask >> i & 1]
            if not xs or len({b for a,b in xs}) == 1:
                return True
            # Correct reply supplies target; all-failure branch consumes f_i.
            for a in range(n):
                if durations[a] <= remaining:
                    fail = sum(1 << i for i,(aa,b) in enumerate(records)
                               if mask >> i & 1 and aa != a)
                    if fail != mask and feasible(fail, remaining-durations[a]):
                        return True
            return False
        direct = next(len(p) for p in encodings
                      if all(feasible(mask,budget) for mask in p))
        loads = lambda p: [sum(durations[i] for i in range(n) if mask >> i & 1)
                           for mask in p]
        batches = min((len(p) for p in endpoint_parts
                       if max(loads(p)) <= budget), default=float('inf'))
        predicted = min(m,batches)
        assert direct == predicted, (n,m,durations,budget,direct,predicted)
        checked += 1
    return checked, len(encodings)

def check():
    rows = []
    for n,m,ds in [(2,2,(1,3)), (2,3,(1,3)), (3,2,(1,2,3)),
                   (3,3,(1,2,3)), (3,3,(2,2,2)), (4,2,(1,1,2,3))]:
        count, encodings = verify(n,m,ds)
        rows.append(dict(endpoints=n,targets=m,durations=ds,budgets=count,
                         arbitrary_encoder_partitions=encodings))
    return {'comparisons':sum(r['budgets'] for r in rows), 'disagreements':0, 'rows':rows}
