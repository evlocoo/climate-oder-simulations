"""Unequal endpoint durations: policy-success cover versus endpoint packing."""

from fractions import Fraction
from itertools import permutations, product
from math import inf

from .research_checks.endpoint_partition import partitions
from .research_checks.endpoint_search import covers_min


def packing_number(durations, budget):
    return min((len(partition) for partition in partitions(len(durations))
                if all(sum(f for i, f in enumerate(durations) if block >> i & 1) <= budget
                       for block in partition)), default=inf)


def policy_frontier(durations, targets, start, action_duration=3, deadline=20):
    """Enumerate fixed failure-prefix schedules and target-contingent success.

    The controller observes schedule position, clock, and the retained reply.
    Repeating a positive-duration target-free failure cannot improve a route;
    schedules use distinct endpoints, but success can stop a long prefix early.
    """
    records = tuple(product(range(len(durations)), range(targets)))
    supports = []
    policies = 0
    for length in range(len(durations) + 1):
        for schedule in permutations(range(len(durations)), length):
            for fallback in range(targets):
                policies += 1
                good = 0
                for index, (endpoint, target) in enumerate(records):
                    clock, reply = start, None
                    for query in schedule:
                        clock += durations[query]
                        if query == endpoint:
                            reply = target
                            break
                    selected = fallback if reply is None else reply
                    if selected == target and clock + action_duration <= deadline:
                        good |= 1 << index
                if good:
                    supports.append(good)
    universe = (1 << len(records)) - 1
    if not supports or any(not any(s >> bit & 1 for s in supports) for bit in range(len(records))):
        return inf, policies
    return covers_min(universe, supports), policies


def boundary_suite():
    specifications = ((2, (2,)), (3, (1, 3)), (3, (1, 2, 3)), (5, (1, 1, 2, 2)))
    rows, mismatches = [], []
    evaluations = 0
    for targets, durations in specifications:
        for half in range(-1, 2 * sum(durations) + 2):
            budget = Fraction(half, 2)
            start = 20 - 3 - budget
            actual, count = policy_frontier(durations, targets, start)
            evaluations += count
            batches = packing_number(durations, budget)
            expected = min(targets, batches) if start <= 17 else inf
            row = {"durations": durations, "targets": targets, "query_budget": budget,
                   "start": start, "packing_categories": batches,
                   "policy_categories": actual, "formula_categories": expected}
            rows.append(row)
            if actual != expected:
                mismatches.append(row)
    return {"cases": len(rows), "schedule_fallback_policies_evaluated": evaluations,
            "rows": rows, "mismatches": mismatches,
            "example": [r for r in rows if r["targets"] == 5 and r["query_budget"] in (1, 2, 3, 6)]}
