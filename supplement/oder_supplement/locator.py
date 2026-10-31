"""Initial handoff partitions and executable lookup policies for legal retries."""

from fractions import Fraction
from functools import lru_cache
from itertools import combinations, product
from math import inf

from .finite import set_partitions
from .reporting import make_record


DEADLINE, ACTION_TIME, QUERY_TIME, UNIVERSAL_TIME, COMMON_TIME = 60, 20, 5, 25, 50
PROBES = (0, Fraction(59, 2), 30, Fraction(61, 2), Fraction(69, 2), 35,
          Fraction(71, 2), Fraction(79, 2), 40, Fraction(81, 2), 60)


def frontier(m, start):
    if start <= DEADLINE - ACTION_TIME - 2 * QUERY_TIME:
        return 1
    if start <= DEADLINE - ACTION_TIME - QUERY_TIME:
        return 2
    if start <= DEADLINE - ACTION_TIME:
        return m
    return inf


def immediate_frontier(m, start):
    if start + COMMON_TIME <= DEADLINE:
        return 1
    return m if start + ACTION_TIME <= DEADLINE else inf


def replay(worlds, start, policy):
    """Return an unassigned observed state, failure, or all-record success.

    A category is handled separately, so its category identifier is constant.
    The source record drives physics only, never the policy key.
    """
    for endpoint, target in worlds:
        state = (start, 0, None, None)  # clock, query stage, failed endpoint, retained reply
        while True:
            time, stage, failed, reply = state
            if time + ACTION_TIME > DEADLINE:
                return False
            if state not in policy:
                return state
            kind, value = policy[state]
            if kind == "target":
                if value != target:
                    return False
                break
            if kind == "common":
                if time + COMMON_TIME > DEADLINE:
                    return False
                break
            if kind == "universal":
                state = (time + UNIVERSAL_TIME, stage + 1, None, target)
            elif kind == "endpoint":
                state = (time + QUERY_TIME, stage + 1,
                         value if value != endpoint else None,
                         None if value != endpoint else target)
            else:
                raise ValueError("unknown operation")
    return True


def direct_policy(worlds, start, m, recovery=True):
    """Enumerate reachable lookup entries, sharing them across all source runs.

    Positive query durations bound search depth. Off-path states admit any
    target action as a legal default; success is required only on reached states.
    """
    policy = {}
    trials = 0

    def search():
        nonlocal trials
        result = replay(worlds, start, policy)
        if result is True:
            return dict(policy)
        if result is False:
            return None
        time, stage, failed, reply = result
        choices = [("common", None)] + [("target", b) for b in range(1, m + 1)]
        if recovery:
            endpoints = (0, 1) if failed is None else (1 - failed, failed)
            choices += [("endpoint", a) for a in endpoints] + [("universal", None)]
        for action in choices:
            trials += 1
            policy[result] = action
            successful = search()
            if successful is not None:
                return successful
        del policy[result]
        return None

    witness = search()
    return witness is not None, trials, witness


def partition_suite():
    rows = []
    mismatches = []
    partitions_checked = block_checks = trials = 0
    for m in (2, 3, 4):
        worlds = tuple(product((0, 1), range(1, m + 1)))
        partitions = sorted(set(set_partitions(worlds)))
        for start in PROBES:
            cache = {}
            for recovery in (False, True):
                for size in range(1, len(worlds) + 1):
                    for block in combinations(worlds, size):
                        success, attempts, _ = direct_policy(block, start, m, recovery)
                        cache[recovery, block] = success
                        block_checks += 1
                        trials += attempts
            best = {False: inf, True: inf}
            for partition in partitions:
                partitions_checked += 1
                for recovery in (False, True):
                    if all(cache[recovery, tuple(sorted(block))] for block in partition):
                        best[recovery] = min(best[recovery], len(partition))
            expected = frontier(m, start)
            immediate = immediate_frontier(m, start)
            row = {"targets": m, "start": start, "partitions": len(partitions),
                   "recovery_categories": best[True], "stated_recovery": expected,
                   "immediate_categories": best[False], "stated_immediate": immediate}
            if 30 < start <= 35:
                row["ratio"] = (Fraction(best[False], best[True])
                                if best[False] != inf and best[True] != inf else None)
            rows.append(row)
            if best[True] != expected or best[False] != immediate:
                mismatches.append(row)
    return {"domain": {"targets": [2, 3, 4], "start_times": PROBES,
                       "deadline": DEADLINE, "target_duration": ACTION_TIME,
                       "endpoint_duration": QUERY_TIME, "universal_duration": UNIVERSAL_TIME,
                       "common_duration": COMMON_TIME, "all_initial_partitions": True},
            "cases": len(rows), "partition_time_cases": partitions_checked,
            "block_policy_searches": block_checks, "reachable_rule_assignments_tried": trials,
            "rows": rows, "mismatches": mismatches}


def retry_suite():
    rows, mismatches = [], []
    for m in range(2, 6):
        worlds = tuple(product((0, 1), range(1, m + 1)))
        encodings = {"constant": (worlds,),
                     "locator": tuple(tuple(x for x in worlds if x[0] == a) for a in (0, 1)),
                     "target": tuple(tuple(x for x in worlds if x[1] == b) for b in range(1, m + 1))}
        for start in range(61):
            direct = {name: all(direct_policy(block, start, m)[0] for block in blocks)
                      for name, blocks in encodings.items()}
            expected = {"constant": start <= 30, "locator": start <= 35, "target": start <= 40}
            row = {"targets": m, "start": start, "direct": direct, "expected": expected}
            rows.append(row)
            if direct != expected:
                mismatches.append(row)
    return {"domain": {"targets": [2, 3, 4, 5], "start_times": "all integer minutes 0 through 60",
                       "encodings": ["constant", "locator", "target"]},
            "cases": len(rows), "encoding_comparisons": 3 * len(rows),
            "mismatches": mismatches}


@lru_cache(maxsize=1)
def locator_summary():
    return {"partitions": partition_suite(), "retry": retry_suite()}


def locator_records(results):
    return [make_record("locator " + name, suite["domain"], len(suite["mismatches"]), 0,
                        details=suite) for name, suite in results.items()]
