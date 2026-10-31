"""Independent finite controller enumeration, including same-source aliases.

Two sources, two hidden physical states, observations in {0,1}, and
decisions step/stop. Step is always legal; stop succeeds according to the
physical-state success map. Clock and history are not observed.
"""
from itertools import product, combinations
import json

def tag(x, mask):
    return tuple(value for j, value in enumerate((x, 0)) if mask >> j & 1)

def successful_paths(x, transition, success, observed):
    paths = []
    p = 0
    prefix = []
    for _ in range(2):
        if success[2*x+p]:
            paths.append(tuple(prefix + [(observed[2*x+p], 'stop')]))
        prefix.append((observed[2*x+p], 'step'))
        p = transition[2*x+p]
    return paths

def covers(paths, mask, same_source=True):
    entries = [(x, b, a) for x, path in enumerate(paths) for b, a in path]
    return all((not same_source and x == y) or b != c or a == d or
               tag(x, mask) != tag(y, mask)
               for (x,b,a), (y,c,d) in combinations(entries, 2))

def direct(transition, success, observed, mask):
    keys = sorted({(b, tag(x,mask)) for x in range(2) for b in observed})
    for actions in product(('step','stop'), repeat=len(keys)):
        policy = dict(zip(keys, actions))
        valid = True
        for x in range(2):
            p = 0
            for _ in range(2):
                a = policy[observed[2*x+p], tag(x,mask)]
                if a == 'stop':
                    valid = bool(success[2*x+p])
                    break
                p = transition[2*x+p]
            else:
                valid = False
            if not valid:
                break
        if valid:
            return True
    return False

def check():
    count = false_positives = 0
    for transition in product((0,1), repeat=4):
        for success in product((0,1), repeat=4):
            for observed in product((0,1), repeat=4):
                witnesses = list(product(*(successful_paths(x, transition, success,
                                                           observed) for x in range(2))))
                for mask in range(4):
                    expected = direct(transition, success, observed, mask)
                    covered = any(covers(w, mask) for w in witnesses)
                    assert covered == expected, (transition, success, observed, mask)
                    false_positives += bool(not expected and any(
                        covers(w, mask, same_source=False) for w in witnesses))
                    count += 1
    return {'occurrence_policy_cover_comparisons':count, 'disagreements':0,
            'false_positives_if_same_source_conflicts_omitted':false_positives,
            'scope':'two sources, two hidden states, step/stop, no clock or history'}
