"""Finite mixed lookup/monotone-response checks with fixed input polarity."""

from functools import lru_cache
from itertools import combinations, product

from .reporting import make_record


def below(left, right):
    return all(a <= b for a, b in zip(left, right))


@lru_cache(maxsize=None)
def rule_tables(width, monotone):
    domain = tuple(product((0, 1), repeat=width))
    tables = []
    for values in product((0, 1), repeat=len(domain)):
        if not monotone or all(values[i] <= values[j] for i, x in enumerate(domain)
                               for j, y in enumerate(domain) if below(x, y)):
            tables.append(values)
    return domain, tuple(tables)


def conflicts_covered(occurrences, features, selected, response_states):
    # Occurrence identity, not source identity, determines which pairs are tested.
    for i, (source, state, action) in enumerate(occurrences):
        for other_source, other_state, other_action in occurrences[i + 1:]:
            if state != other_state or action == other_action:
                continue
            if state in response_states:
                positive, negative = ((source, other_source) if action == 1
                                      else (other_source, source))
                covered = any(features[k][positive] == 1 and features[k][negative] == 0
                              for k in selected)
            else:
                covered = any(features[k][source] != features[k][other_source] for k in selected)
            if not covered:
                return False
    return True


def direct_permitted_rules(occurrences, features, selected, response_states):
    feasible = True
    evaluations = 0
    for state in set(r for _, r, _ in occurrences):
        domain, rules = rule_tables(len(selected), state in response_states)
        assignments = [(domain.index(tuple(features[k][x] for k in selected)), a)
                       for x, r, a in occurrences if r == state]
        successes = 0
        for rule in rules:
            evaluations += 1
            successes += all(rule[index] == action for index, action in assignments)
        feasible &= successes > 0
    return feasible, evaluations


def completion(occurrences, features, selected, response_states):
    domain = tuple(product((0, 1), repeat=len(selected)))
    rules = {}
    for state in set(r for _, r, _ in occurrences):
        reached = [(tuple(features[k][x] for k in selected), a)
                   for x, r, a in occurrences if r == state]
        if state in response_states:
            positive = [z for z, a in reached if a == 1]
            rules[state] = {z: int(any(below(p, z) for p in positive)) for z in domain}
        else:
            rules[state] = dict.fromkeys(domain, 0)
            rules[state].update(reached)
    return rules


def completion_valid(rules, occurrences, features, selected, response_states):
    reached_ok = all(rules[r][tuple(features[k][x] for k in selected)] == a
                     for x, r, a in occurrences)
    monotone_ok = all(not below(x, y) or values[x] <= values[y]
                      for r, values in rules.items() if r in response_states
                      for x in values for y in values)
    return reached_ok and monotone_ok


def monotone_family(sources):
    source_count = max(sources) + 1
    selected_sets = [s for size in range(3) for s in combinations(range(2), size)]
    cases = evaluations = completions = 0
    mismatches = []
    for bits in product((0, 1), repeat=2 * source_count):
        features = (bits[:source_count], bits[source_count:])
        for states in product((0, 1), repeat=3):
            for actions in product((0, 1), repeat=3):
                occurrences = tuple(zip(sources, states, actions))
                for selected in selected_sets:
                    cases += 1
                    covered = conflicts_covered(occurrences, features, selected, {1})
                    direct, tried = direct_permitted_rules(occurrences, features, selected, {1})
                    evaluations += tried
                    valid = True
                    if covered:
                        completions += 1
                        valid = completion_valid(completion(occurrences, features, selected, {1}),
                                                 occurrences, features, selected, {1})
                    if covered != direct or not valid:
                        mismatches.append({"occurrences": occurrences, "features": features,
                                           "selected": selected, "covered": covered,
                                           "direct": direct, "completion_valid": valid})
    return {"domain": {"occurrence_sources": sources, "baseline_states": [0, 1],
                       "response_states": [1], "features": 2,
                       "feature_assignments": 2 ** (2 * source_count),
                       "baseline_assignments": 8, "response_assignments": 8,
                       "selections": 4, "configured_inputs": "full selected Boolean cube",
                       "both_responses_legal": True},
            "cases": cases, "local_rule_tables_evaluated": evaluations,
            "upward_completions_checked": completions, "mismatches": mismatches}


def warning_example():
    features = ((0, 1), (1, 0))
    occurrences = ((0, 1, 1), (1, 1, 0))
    rows = []
    for selected in ((), (0,), (1,), (0, 1)):
        free, _ = direct_permitted_rules(occurrences, features, selected, set())
        restricted, _ = direct_permitted_rules(occurrences, features, selected, {1})
        rows.append({"features": ["fg"[k] for k in selected], "cost": sum(k + 1 for k in selected),
                     "unrestricted": free, "monotone": restricted,
                     "ordinary_coverage": conflicts_covered(occurrences, features, selected, set()),
                     "directional_coverage": conflicts_covered(occurrences, features, selected, {1})})
    return {"rows": rows, "unrestricted_minimum": min(r["cost"] for r in rows if r["unrestricted"]),
            "monotone_minimum": min(r["cost"] for r in rows if r["monotone"])}


def monotone_summary():
    return {"distinct_sources": monotone_family((0, 1, 2)),
            "repeated_source": monotone_family((0, 1, 0)), "warning": warning_example()}


def monotone_records(results):
    records = []
    for name in ("distinct_sources", "repeated_source"):
        family = results[name]
        records.append(make_record("monotone mixed policy " + name, family["domain"],
                                   len(family["mismatches"]), 0,
                                   details={k: family[k] for k in ("cases", "local_rule_tables_evaluated",
                                                                  "upward_completions_checked", "mismatches")}))
    warning = results["warning"]
    records.append(make_record("fixed-polarity warning preservation costs", {"records": 2, "selections": 4},
                               [warning["unrestricted_minimum"], warning["monotone_minimum"]], [1, 2],
                               details={"selections": warning["rows"]}))
    return records
