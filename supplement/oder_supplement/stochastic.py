"""Stochastic distributed coordination extension."""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations, product


def supported_realizations(channel):
    validate_channel(channel)
    out = []
    for x, outcomes in channel.items():
        for observations, probability in outcomes.items():
            if probability > 0:
                out.append((x, tuple(observations)))
    return tuple(out)


def validate_channel(channel):
    expected_dim = None
    for x, outcomes in channel.items():
        if not outcomes:
            raise ValueError(f"source {x!r} has empty outcome support")
        total = Fraction(0)
        for observations, probability in outcomes.items():
            probability = Fraction(probability)
            if probability < 0:
                raise ValueError(f"negative probability for {x!r}, {observations!r}")
            if expected_dim is None:
                expected_dim = len(observations)
            elif len(observations) != expected_dim:
                raise ValueError("inconsistent participant dimensions")
            total += probability
        if total != 1:
            raise ValueError(f"probabilities for {x!r} sum to {total}, not 1")
    return True


def realization_components(channel):
    omega = supported_realizations(channel)
    parent = {w: w for w in omega}

    def find(w):
        while parent[w] != w:
            parent[w] = parent[parent[w]]
            w = parent[w]
        return w

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for a, b in combinations(omega, 2):
        if any(a[1][i] == b[1][i] for i in range(len(a[1]))):
            union(a, b)
    comps = {}
    for w in omega:
        comps.setdefault(find(w), []).append(w)
    return tuple(tuple(v) for v in comps.values())


def supported_graph_criterion(channel, action_sets):
    comps = realization_components(channel)
    failures = []
    choices = {}
    for comp in comps:
        common = set(action_sets[comp[0][0]])
        for x, _ in comp[1:]:
            common &= set(action_sets[x])
        if common:
            choices[comp] = sorted(common)[0]
        else:
            failures.append(comp)
    return {"succeeds": not failures, "components": comps, "choices": choices, "failed_components": tuple(failures)}


def direct_rule_check(channel, action_sets):
    """Enumerate local observation rules, checking every positive-probability realization."""
    omega = supported_realizations(channel)
    n = len(omega[0][1]) if omega else 0
    local_obs = [sorted({obs[i] for _, obs in omega}) for i in range(n)]
    actions = tuple(sorted({a for values in action_sets.values() for a in values}))
    successes = []
    for choices in product(*(tuple(product(actions, repeat=len(obs))) for obs in local_obs)):
        rules = [dict(zip(local_obs[i], choices[i])) for i in range(n)]
        ok = True
        for x, obs in omega:
            selected = [rules[i][obs[i]] for i in range(n)]
            if len(set(selected)) != 1 or selected[0] not in action_sets[x]:
                ok = False
                break
        if ok:
            successes.append(rules)
    return {"succeeds": bool(successes), "rule_count": len(successes), "rules": successes}


def direct_binary_rule_pair_check(channel, action_sets):
    """Direct checker specialized to two participants with binary observations."""
    omega = supported_realizations(channel)
    actions = ("a", "b")
    successes = 0
    for choices_0 in product(actions, repeat=2):
        rule_0 = {0: choices_0[0], 1: choices_0[1]}
        for choices_1 in product(actions, repeat=2):
            rule_1 = {0: choices_1[0], 1: choices_1[1]}
            ok = True
            for x, obs in omega:
                a0 = rule_0[obs[0]]
                a1 = rule_1[obs[1]]
                if a0 != a1 or a0 not in action_sets[x]:
                    ok = False
                    break
            if ok:
                successes += 1
    return {"succeeds": successes > 0, "rule_count": successes, "rule_pairs_checked": 16}


def average_success(channel, source_probabilities, action_sets, rules):
    total = Fraction(0)
    for x, outcomes in channel.items():
        for obs, p in outcomes.items():
            selected = [rules[i][obs[i]] for i in range(len(obs))]
            if len(set(selected)) == 1 and selected[0] in action_sets[x]:
                total += source_probabilities[x] * p
    return total


def marginal_channel(channel, participant_index):
    out = {}
    for x, outcomes in channel.items():
        totals = {}
        for obs, p in outcomes.items():
            totals[obs[participant_index]] = totals.get(obs[participant_index], Fraction(0)) + p
        out[x] = totals
    return out


def diagnostic_channels():
    half = Fraction(1, 2)
    aligned = {
        "L": {(0, 0): Fraction(1)},
        "M": {(0, 0): half, (1, 1): half},
        "R": {(1, 1): Fraction(1)},
    }
    crossed = {
        "L": {(0, 0): Fraction(1)},
        "M": {(0, 1): half, (1, 0): half},
        "R": {(1, 1): Fraction(1)},
    }
    action_sets = {"L": {"a"}, "M": {"a", "b"}, "R": {"b"}}
    return action_sets, aligned, crossed


def uniform_channel_from_supports(world_supports):
    channel = {}
    for world, support in world_supports.items():
        support = tuple(support)
        p = Fraction(1, len(support))
        channel[world] = {obs: p for obs in support}
    return channel


def all_nonempty_subsets(items):
    items = tuple(items)
    for mask in range(1, 1 << len(items)):
        yield tuple(items[i] for i in range(len(items)) if mask & (1 << i))


def exhaustive_two_world_support_family():
    obs_pairs = ((0, 0), (0, 1), (1, 0), (1, 1))
    plan_sets = ({"a"}, {"b"}, {"a", "b"})
    records = []
    mismatches = []
    case_count = 0
    rule_pair_checks = 0
    for support_0 in all_nonempty_subsets(obs_pairs):
        for support_1 in all_nonempty_subsets(obs_pairs):
            channel = uniform_channel_from_supports({"x0": support_0, "x1": support_1})
            for actions_0 in plan_sets:
                for actions_1 in plan_sets:
                    action_sets = {"x0": set(actions_0), "x1": set(actions_1)}
                    graph = supported_graph_criterion(channel, action_sets)
                    direct = direct_binary_rule_pair_check(channel, action_sets)
                    case_count += 1
                    rule_pair_checks += direct["rule_pairs_checked"]
                    agree = graph["succeeds"] == direct["succeeds"]
                    if not agree:
                        mismatch = {
                            "support_0": support_0,
                            "support_1": support_1,
                            "action_sets": {k: tuple(sorted(v)) for k, v in action_sets.items()},
                            "graph": graph["succeeds"],
                            "direct": direct["succeeds"],
                        }
                        mismatches.append(mismatch)
                    if len(records) < 5:
                        records.append(
                            {
                                "support_0": support_0,
                                "support_1": support_1,
                                "action_sets": {k: tuple(sorted(v)) for k, v in action_sets.items()},
                                "graph": graph["succeeds"],
                                "direct": direct["succeeds"],
                                "agree": agree,
                            }
                        )
    return {
        "case_count": case_count,
        "expected_case_count": 2025,
        "rule_pair_checks": rule_pair_checks,
        "mismatch_count": len(mismatches),
        "mismatches": tuple(mismatches),
        "sample_records": tuple(records),
    }


def support_sensitivity_channel(epsilon=Fraction(1, 1000)):
    return {
        "A": {(0, 0): Fraction(1)},
        "B": {(1, 1): Fraction(1) - epsilon, (0, 0): epsilon},
    }, {"A": {"a"}, "B": {"b"}}


def manuscript_support_sensitivity(epsilon=Fraction(1, 100), p_m=Fraction(1, 3)):
    half_aligned = (1 - epsilon) / 2
    half_crossed = epsilon / 2
    channel = {
        "L": {(0, 0): Fraction(1)},
        "M": {(0, 0): half_aligned, (1, 1): half_aligned, (0, 1): half_crossed, (1, 0): half_crossed},
        "R": {(1, 1): Fraction(1)},
    }
    action_sets = {"L": {"a"}, "M": {"a", "b"}, "R": {"b"}}
    label_rules = [{0: "a", 1: "b"}, {0: "a", 1: "b"}]
    source_p = {"L": (1 - p_m) / 2, "M": p_m, "R": (1 - p_m) / 2}
    return {
        "epsilon": epsilon,
        "p_M": p_m,
        "graph": supported_graph_criterion(channel, action_sets),
        "direct": direct_rule_check(channel, action_sets),
        "label_following_average_success": average_success(channel, source_p, action_sets, label_rules),
        "stated_formula": 1 - p_m * epsilon,
    }


def mixture_average_optimum(source_probabilities, epsilon):
    """Compare all 16 local rule pairs with the three-situation mixture formula."""
    epsilon = Fraction(epsilon)
    prior = {x: Fraction(source_probabilities[x]) for x in ("L", "M", "R")}
    if not 0 <= epsilon <= 1 or any(p < 0 for p in prior.values()) or sum(prior.values()) != 1:
        raise ValueError("Require a normalized nonnegative source distribution and epsilon in [0, 1]")
    channel = {
        "L": {(0, 0): Fraction(1)},
        "M": {(0, 0): (1 - epsilon) / 2, (1, 1): (1 - epsilon) / 2,
              (0, 1): epsilon / 2, (1, 0): epsilon / 2},
        "R": {(1, 1): Fraction(1)},
    }
    actions = {"L": {"a"}, "M": {"a", "b"}, "R": {"b"}}
    validate_channel(channel)
    best = Fraction(-1)
    best_rules = []
    checked = 0
    # Evaluate outcomes directly; the formula is used only after enumeration.
    for choices in product(("a", "b"), repeat=4):
        rules = [{0: choices[0], 1: choices[1]}, {0: choices[2], 1: choices[3]}]
        score = average_success(channel, prior, actions, rules)
        checked += 1
        if score > best:
            best, best_rules = score, [rules]
        elif score == best:
            best_rules.append(rules)
    label_rules = [{0: "a", 1: "b"}, {0: "a", 1: "b"}]
    return {
        "source_probabilities": prior,
        "epsilon": epsilon,
        "direct_optimum": best,
        "stated_formula": 1 - min(prior["L"], prior["R"], prior["M"] * epsilon),
        "label_following_average_success": average_success(channel, prior, actions, label_rules),
        "best_rules": best_rules,
        "rule_pairs_checked": checked,
    }


def exhaustive_mixture_optimum_family():
    """All tenths-simplex priors and eleven mixture values, with exact fractions."""
    priors = [{"L": Fraction(l, 10), "M": Fraction(m, 10), "R": Fraction(10 - l - m, 10)}
              for l in range(11) for m in range(11 - l)]
    epsilons = tuple(Fraction(k, 10) for k in range(11))
    cases = 0
    rule_pairs = 0
    mismatches = []
    for prior in priors:
        for epsilon in epsilons:
            result = mixture_average_optimum(prior, epsilon)
            cases += 1
            rule_pairs += result["rule_pairs_checked"]
            if result["direct_optimum"] != result["stated_formula"]:
                mismatches.append(result)
    examples = {
        "label_following_optimal": mixture_average_optimum(
            {"L": Fraction(3, 10), "M": Fraction(4, 10), "R": Fraction(3, 10)}, Fraction(1, 10)),
        "constant_b_optimal": mixture_average_optimum(
            {"L": Fraction(1, 10), "M": Fraction(6, 10), "R": Fraction(3, 10)}, Fraction(1, 2)),
        "constant_a_optimal": mixture_average_optimum(
            {"L": Fraction(3, 10), "M": Fraction(6, 10), "R": Fraction(1, 10)}, Fraction(1, 2)),
    }
    return {
        "prior_count": len(priors), "epsilon_count": len(epsilons),
        "domain": "Nonnegative source weights in tenths summing to one; epsilon = 0, 1/10, ..., 1",
        "case_count": cases, "expected_case_count": 726,
        "rule_pair_checks": rule_pairs,
        "mismatch_count": len(mismatches), "mismatches": tuple(mismatches),
        "worked_examples": examples,
    }
