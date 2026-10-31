"""Single-actor finite ODER constructions."""

from __future__ import annotations

from itertools import combinations, product
from math import inf


def powerset(items):
    items = tuple(items)
    for r in range(len(items) + 1):
        yield from combinations(items, r)


def set_partitions(items):
    """Yield all set partitions of a short ordered tuple."""
    items = tuple(items)
    if not items:
        yield ()
        return
    first, rest = items[0], items[1:]
    for partition in set_partitions(rest):
        yield ((first,),) + partition
        for i in range(len(partition)):
            block = tuple(sorted(partition[i] + (first,)))
            new_partition = list(partition)
            new_partition[i] = block
            canonical = tuple(sorted(new_partition, key=lambda b: (len(b), b)))
            yield canonical


def fibers(records, representation):
    out = {}
    for x in records:
        out.setdefault(representation[x], []).append(x)
    return {r: tuple(xs) for r, xs in out.items()}


def common_action_report(records, action_sets, representation):
    fiber_map = fibers(records, representation)
    intersections = {}
    rule = {}
    witness = None
    for state, xs in fiber_map.items():
        common = set(action_sets[xs[0]])
        for x in xs[1:]:
            common &= set(action_sets[x])
        intersections[state] = tuple(sorted(common))
        if common:
            rule[state] = sorted(common)[0]
        elif witness is None:
            witness = {"state": state, "records": xs}
    return {
        "sufficient": witness is None,
        "fibers": fiber_map,
        "intersections": intersections,
        "rule": rule if witness is None else None,
        "witness": witness,
    }


def enumerate_lookup_rules(records, action_sets, representation):
    """Independent small-domain check by trying every rule on retained states."""
    states = tuple(sorted(set(representation.values()), key=str))
    actions = tuple(sorted({a for values in action_sets.values() for a in values}))
    successes = []
    for choices in product(actions, repeat=len(states)):
        rule = dict(zip(states, choices))
        ok = all(rule[representation[x]] in action_sets[x] for x in records)
        if ok:
            successes.append(rule)
    return successes


def minimum_category_count_by_cover(records, action_sets):
    actions = tuple(sorted({a for values in action_sets.values() for a in values}))
    covers = {a: {x for x in records if a in action_sets[x]} for a in actions}
    if any(not action_sets[x] for x in records):
        return inf, []
    best_size = inf
    best = []
    for subset in powerset(actions):
        if not subset:
            continue
        covered = set().union(*(covers[a] for a in subset))
        if covered == set(records):
            if len(subset) < best_size:
                best_size = len(subset)
                best = [subset]
            elif len(subset) == best_size:
                best.append(subset)
    return best_size, best


def minimum_partitions_by_enumeration(records, action_sets):
    """Brute-force partition enumeration for small independent checks."""
    best_size = inf
    best = []
    for partition in set(set_partitions(records)):
        ok = True
        for block in partition:
            common = set(action_sets[block[0]])
            for x in block[1:]:
                common &= set(action_sets[x])
            if not common:
                ok = False
                break
        if ok:
            if len(partition) < best_size:
                best_size = len(partition)
                best = [partition]
            elif len(partition) == best_size:
                best.append(partition)
    return best_size, best


def minutes(hhmm):
    hh, mm = hhmm.split(":")
    return int(hh) * 60 + int(mm)


def hhmm(total_minutes):
    return f"{total_minutes // 60:02d}:{total_minutes % 60:02d}"


def heat_action_sets(start_minute):
    """Manuscript heat example, with inclusive completion at noon."""
    if start_minute <= minutes("10:30"):
        return {"A": {"c", "a_A"}, "B": {"c", "a_B"}}
    if start_minute <= minutes("11:30"):
        return {"A": {"a_A"}, "B": {"a_B"}}
    return {"A": set(), "B": set()}


def heat_briefing_checks():
    records = ("A", "B")
    full = {"A": "earlier=A", "B": "earlier=B"}
    coarse = {"A": "two facilities; one earlier", "B": "two facilities; one earlier"}
    rows = []
    for t in (minutes("10:00"), minutes("10:30"), minutes("11:00"), minutes("11:15"), minutes("11:30"), minutes("11:31")):
        actions = heat_action_sets(t)
        rows.append(
            {
                "time": hhmm(t),
                "full": common_action_report(records, actions, full),
                "coarse": common_action_report(records, actions, coarse),
                "cover": minimum_category_count_by_cover(records, actions)[0],
                "rule_count_check": len(enumerate_lookup_rules(records, actions, coarse)),
            }
        )
    return rows


def stochastic_retention_heat(epsilon):
    """The manuscript's expected-loss contrast for the heat example."""
    correct_loss = 20
    reversed_loss = 80
    avg_loss = (1 - epsilon) * correct_loss + epsilon * reversed_loss
    guarantee = epsilon == 0
    return {"epsilon": epsilon, "retention_averaged_loss": avg_loss, "within_30_loss": avg_loss <= 30, "probability_one_guarantee": guarantee}
