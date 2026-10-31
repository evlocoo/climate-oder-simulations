"""Independent finite-policy check of the all-couplings support certificate."""
from itertools import product

SUPPORTS = (frozenset((0,)), frozenset((1,)), frozenset((0, 1)))
ACTIONS = (frozenset(), frozenset((0,)), frozenset((1,)), frozenset((0, 1)))

def components(sx):
    groups = [{x} for x in range(len(sx))]
    for x in range(len(sx)):
        for y in range(x):
            if any(a & b for a, b in zip(sx[x], sx[y])):
                gx = next(c for c in groups if x in c)
                gy = next(c for c in groups if y in c)
                if gx is not gy:
                    gx.update(gy)
                    groups.remove(gy)
    return groups

def direct(sx, accepted):
    n = len(sx[0])
    realizations = [(x, r) for x, supports in enumerate(sx)
                    for r in product(*supports)]
    # Each integer 0..3 is the truth table of a local binary-to-binary rule.
    for profile in product(range(4), repeat=n):
        good = True
        for x, r in realizations:
            outputs = {(profile[i] >> r[i]) & 1 for i in range(n)}
            if len(outputs) != 1 or not outputs <= accepted[x]:
                good = False
                break
        if good:
            return True
    return False

def check():
    total = 0
    rows = []
    for n, source_counts in ((2, (1, 2, 3)), (3, (1, 2))):
        subtotal = 0
        for ns in source_counts:
            for cfg in product(SUPPORTS, repeat=n * ns):
                sx = [cfg[x*n:(x+1)*n] for x in range(ns)]
                groups = components(sx)
                for accepted in product(ACTIONS, repeat=ns):
                    certificate = all(set.intersection(*(set(accepted[x]) for x in c))
                                      for c in groups)
                    assert certificate == direct(sx, accepted), (sx, accepted)
                    subtotal += 1
        rows.append({"participants": n, "cases": subtotal, "disagreements": 0})
        total += subtotal
    # Source contraction is deliberately invalid for a single actor.
    sx = [(frozenset((0, 1)),), (frozenset((0,)),), (frozenset((1,)),)]
    accepted = (frozenset((0, 1)), frozenset((0,)), frozenset((1,)))
    assert direct(sx, accepted)
    assert not all(set.intersection(*(set(accepted[x]) for x in c))
                   for c in components(sx))
    return {"cases": total, "rows": rows, "disagreements": 0,
            "single_actor_direct": direct(sx, accepted),
            "single_actor_component": all(set.intersection(*(set(accepted[x]) for x in c))
                                          for c in components(sx))}
