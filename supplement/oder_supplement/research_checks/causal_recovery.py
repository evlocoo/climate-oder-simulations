"""Causal overwriting and recoverable query errors.

These are finite stipulated models, not empirical climate validation.
"""
from itertools import product, combinations
import json
from . import timed_preservation as base


def streaming_cover(witness):
    entries = []
    for x, steps in enumerate(witness):
        for retained, operation in steps:
            baseline = retained[:2]  # Stage and observed time, without reply bit.
            bit = base.X[x][0] if retained[0] == 'start' else base.X[x][1]
            entries.append((baseline, bit, operation))
    return all(r != s or op == other_op or bit != other_bit
               for (r, bit, op), (s, other_bit, other_op)
               in combinations(entries, 2))


def streaming_direct(start):
    routes, targets = (0, 0, 1, 1), (0, 1, 0, 1)
    choices = []
    for group in ([0, 1], [2, 3]):
        candidates = []
        for operation in base.OPS:
            stopping = []
            for x in group:
                if operation[0] != 'query':
                    if operation not in base.terminal_choices(targets[x], start):
                        break
                else:
                    retained = base.advance(x, operation, start, routes, targets,
                                            (5, 25), True)
                    if retained is None:
                        break
                    # Replace locator a with the returned target b in one bit.
                    stopping.append((retained[:2], targets[x],
                                     base.terminal_choices(targets[x], retained[1])))
            else:
                candidates.append(stopping)
        if not candidates:
            return False
        choices.append(candidates)
    for profile in product(*choices):
        allowed = {}
        for final in profile:
            for retained, bit, actions in final:
                key = retained, bit
                allowed[key] = allowed.get(key, actions) & actions
        if all(allowed.values()):
            return True
    return False


def constant_retention_with_retry(start, target_count):
    """Wrong fast query returns observable failure in 5 min; retry is legal.

After success, target reply is retained. After failure, the retained failure
state and observed time permit querying the other endpoint. Both endpoints
always accept attempts. This differs from the source-specific legal-query
restriction in timed_preservation.py.
    """
    records = list(product((0, 1), range(target_count)))
    operations = [('act', b) for b in range(target_count)] + [
        ('both',), ('generic',), ('fast', 0), ('fast', 1)]

    def succeeds(record, operation):
        route, target = record
        if operation[0] == 'act':
            return operation[1] == target and start + 20 <= 60
        if operation[0] == 'both':
            return start + 50 <= 60
        if operation[0] == 'generic':
            return start + 25 + 20 <= 60
        return start + (5 if operation[1] == route else 10) + 20 <= 60

    return any(all(succeeds(record, op) for record in records)
               for op in operations)


def single_source_controller(uses_channel):
    """No observed clock/stage; prepare then execute is the sole valid path."""
    memory_values = (0, 1) if uses_channel else (0,)
    for outputs in product(('prepare', 'execute'), repeat=len(memory_values)):
        policy = dict(zip(memory_values, outputs))
        stage, memory = 0, 0
        for _ in range(2):
            operation = policy[memory]
            if stage == 0 and operation == 'prepare':
                stage = 1
                memory = 1 if uses_channel else 0
            elif stage == 1 and operation == 'execute':
                stage = 2
                break
            else:
                break
        if stage == 2:
            return True
    return False


def check():
    routes, targets = (0, 0, 1, 1), (0, 1, 0, 1)
    for start in range(61):
        witnesses = base.witnesses(start, routes, targets, (5, 25), True)
        direct = streaming_direct(start)
        assert direct == any(streaming_cover(w) for w in witnesses)
        assert direct == base.direct(start, routes, targets, (5, 25), True, 1)
    assert streaming_direct(30) and streaming_direct(35)
    assert not streaming_direct(36)
    retry_checks = 0
    for target_count in (2, 3, 5, 10):
        for start in range(61):
            assert constant_retention_with_retry(start, target_count) == (start <= 30)
            retry_checks += 1
    assert not single_source_controller(False)
    assert single_source_controller(True)
    return {
        'streaming_policy_cover_comparisons': 61,
        'streaming_policy_cover_disagreements': 0,
        'streaming_locator_last_start': 35,
        'recoverable_retry_checks': retry_checks,
        'zero_information_with_retry_last_start': 30,
        'strict_locator_advantage_with_retry': '31..35',
        'tested_target_cardinalities': [2, 3, 5, 10],
        'single_source_success_with_constant_source_feature': False,
        'single_source_success_with_causal_channel': True,
    }
