"""Finite checks for uncertain channels, situation restriction, and early information."""

from fractions import Fraction
from itertools import combinations, combinations_with_replacement, product
from math import inf

from .coordination import (
    acquisition_deadline, budget_preservation_example, optimize_features,
    refine_observations, shared_plan_graph_criterion,
)
from .stochastic import supported_graph_criterion, uniform_channel_from_supports, validate_channel
from .reporting import make_record


TIMES = (480, 540, Fraction(1081, 2), 600, Fraction(1201, 2), 660, Fraction(1321, 2), 720)
BUDGETS = (0, 1, 2, 3, 4, 5)
PLANS = ("plan_0", "plan_1")


def mechanism_comparison(channels, action_sets):
    """Two participants, fixed binary alphabets and plans; one rule for all channels."""
    if not channels or not action_sets:
        raise ValueError("Require a nonempty channel family and source set")
    for channel in channels:
        validate_channel(channel)
        if set(channel) != set(action_sets):
            raise ValueError("All channels must use the same source set")
        if any(len(obs) != 2 or any(v not in (0, 1) for v in obs)
               for outcomes in channel.values() for obs in outcomes):
            raise ValueError("This finite check requires two binary local alphabets")
    if any(not set(a) <= {"a", "b"} for a in action_sets.values()):
        raise ValueError("This finite check uses the fixed plan catalog a,b")
    supports = {x: set() for x in action_sets}
    for channel in channels:
        for x, outcomes in channel.items():
            supports[x].update(obs for obs, p in outcomes.items() if p > 0)
    union = uniform_channel_from_supports(supports)
    graph = supported_graph_criterion(union, action_sets)["succeeds"]
    successful = []
    checked = 0
    # The comparator reads each original channel, not the union or its components.
    for choices in product(("a", "b"), repeat=4):
        rules = (choices[:2], choices[2:])
        ok = all(rules[0][obs[0]] == rules[1][obs[1]]
                 and rules[0][obs[0]] in action_sets[x]
                 for channel in channels for x, outcomes in channel.items()
                 for obs, p in outcomes.items() if p > 0)
        checked += 1
        if ok:
            successful.append(rules)
    return {"union_feasible": graph, "direct_feasible": bool(successful),
            "successful_rules": successful, "rule_profiles_checked": checked}


def mechanism_suite():
    outcomes = tuple(product((0, 1), repeat=2))
    channels = [{0: {a: Fraction(1)}, 1: {b: Fraction(1)}} for a, b in product(outcomes, repeat=2)]
    allowed = (set(), {"a"}, {"b"}, {"a", "b"})
    mismatches = []
    cases = evaluations = 0
    for i, j in combinations_with_replacement(range(16), 2):
        for a, b in product(allowed, repeat=2):
            r = mechanism_comparison((channels[i], channels[j]), {0: a, 1: b})
            cases += 1
            evaluations += r["rule_profiles_checked"]
            if r["union_feasible"] != r["direct_feasible"]:
                mismatches.append({"channels": (i, j), "actions": (sorted(a), sorted(b)), "result": r})
    correct = {0: {(0, 0): Fraction(1)}, 1: {(1, 1): Fraction(1)}}
    reversed_labels = {0: {(1, 1): Fraction(1)}, 1: {(0, 0): Fraction(1)}}
    examples = {}
    for name, actions in (("separately_feasible_only", {0: {"a"}, 1: {"b"}}),
                          ("common_rule_exists", {0: {"a"}, 1: {"a"}})):
        r = mechanism_comparison((correct, reversed_labels), actions)
        r["separate_feasibility"] = [mechanism_comparison((k,), actions)["direct_feasible"]
                                      for k in (correct, reversed_labels)]
        examples[name] = r
    return {"domain": {"sources": 2, "participants": 2, "local_states": 2, "plans": 2,
                       "deterministic_channels": 16, "unordered_channel_pairs_with_replacement": 136,
                       "acceptable_set_pairs_including_empty": 16},
            "cases": cases, "rule_profile_evaluations": evaluations,
            "mismatches": mismatches, "examples": examples}


def selections(features):
    return tuple(tuple(f for i, f in enumerate(features) if mask & (1 << i))
                 for mask in range(1 << len(features)))


def direct_selection(records, actions, observations, selected):
    """Enumerate lookup profiles on independently assembled terminal observations."""
    actors = tuple(observations)
    states = {a: {x: (observations[a][x], tuple(f.values[x] for f in selected if f.actor == a))
                  for x in records} for a in actors}
    alphabets = {a: tuple(dict.fromkeys(states[a].values())) for a in actors}
    rule_lists = [tuple(dict(zip(alphabets[a], values))
                        for values in product(PLANS, repeat=len(alphabets[a]))) for a in actors]
    successful = checked = 0
    for profile in product(*rule_lists):
        checked += 1
        if all(len({profile[i][states[a][x]] for i, a in enumerate(actors)}) == 1
               and profile[0][states[actors[0]][x]] in actions[x] for x in records):
            successful += 1
    return {"feasible": successful > 0, "profiles_checked": checked,
            "successful_profiles": successful}


def selection_rows(records, actions, observations, features):
    rows = []
    for selected in selections(features):
        direct = direct_selection(records, actions, observations, selected)
        graph = shared_plan_graph_criterion(records, actions,
                                            refine_observations(records, observations, selected))["succeeds"]
        rows.append({"selection": tuple(f.name for f in selected), "cost": sum(f.cost for f in selected),
                     "cutoff": min((f.deadline for f in selected), default=inf),
                     "graph_feasible": graph, "direct_feasible": direct["feasible"],
                     "profiles_checked": direct["profiles_checked"]})
    return rows


def required_cost(rows, time, method="direct_feasible"):
    return min((r["cost"] for r in rows if r[method] and time <= r["cutoff"]), default=inf)


def direct_cutoff(rows, budget=inf):
    return max((r["cutoff"] for r in rows if r["direct_feasible"] and r["cost"] <= budget), default=-inf)


def restriction_suite():
    records, actions, observations, features = budget_preservation_example()
    specifications = []
    for size in range(1, 5):
        for subset in combinations(records, size):
            specifications.append(("worksheet " + str(subset), records, subset, actions, observations, features))
    simple = (0, 1, 2)
    known = {a: {x: x for x in simple} for a in ("transport", "receiving")}
    same = {a: {x: 0 for x in simple} for a in known}
    specifications += [
        ("baseline sufficient equality", simple, (0, 1), {x: {"plan_0"} for x in simple}, same, ()),
        ("unrepairable on both sets", simple, (0, 1), {0: set(), 1: {"plan_0"}, 2: {"plan_1"}}, known, ()),
        ("remove the empty-action obstruction", simple, (1, 2),
         {0: set(), 1: {"plan_0"}, 2: {"plan_1"}}, known, ()),
    ]
    cases = []
    for name, full, subset, actions, observations, features in specifications:
        # Only the evaluation set changes: catalogs, costs, ownership and terminal states stay fixed.
        xrows = selection_rows(full, actions, observations, features)
        yrows = selection_rows(subset, actions, observations, features)
        costs = []
        deadlines = []
        for s in TIMES:
            values = []
            for domain in (full, subset):
                value = optimize_features(domain, actions, observations, features, available_at=s)["minimum_cost"]
                values.append(inf if value is None else value)
            costs.append({"time": s, "graph": values,
                          "direct": [required_cost(xrows, s), required_cost(yrows, s)]})
        for budget in BUDGETS:
            deadlines.append({"budget": budget,
                              "graph": [acquisition_deadline(z, actions, observations, features, budget)
                                        for z in (full, subset)],
                              "direct": [direct_cutoff(xrows, budget), direct_cutoff(yrows, budget)]})
        cases.append({"name": name, "full": full, "restricted": subset,
                      "full_selections": xrows, "restricted_selections": yrows,
                      "costs": costs, "deadlines": deadlines})
    return {"domain": {"worksheet_nonempty_restrictions": 15, "worksheet_feature_subsets": 8,
                       "additional_no_feature_pairs": 3, "times": TIMES, "budgets": BUDGETS,
                       "plan_catalog": PLANS, "decision_time": 720},
            "cases": cases, "restricted_selection_comparisons": sum(len(c["restricted_selections"]) for c in cases)}


def early_information_suite():
    records, actions, observations, features = budget_preservation_example()
    full = selection_rows(records, actions, observations, features)
    regimes = [selection_rows(tuple(x for x in records if x[0] == e), actions, observations, features)
               for e in (1, 2)]
    policies = []
    # Choices depend on regime e only, never on the hidden target b.
    for first, second in product(*regimes):
        policies.append({"bundles": (first["selection"], second["selection"]),
                         "fixed": first["selection"] == second["selection"],
                         "feasible": first["direct_feasible"] and second["direct_feasible"],
                         "cost": max(first["cost"], second["cost"]),
                         "cost_by_regime": (first["cost"], second["cost"]),
                         "cutoff": min(first["cutoff"], second["cutoff"])})
    costs = []
    for s in TIMES:
        feasible = [p for p in policies if p["feasible"] and s <= p["cutoff"]]
        fixed_cost = min((p["cost"] for p in feasible if p["fixed"]), default=inf)
        adaptive_cost = min((p["cost"] for p in feasible), default=inf)
        costs.append({"time": s,
                      "component_costs": [required_cost(full, s, "graph_feasible"),
                                          max(required_cost(r, s, "graph_feasible") for r in regimes)],
                      "policy_costs": [fixed_cost, adaptive_cost],
                      "worksheet_costs": [1 if s <= 540 else 4 if s <= 600 else inf,
                                          1 if s <= 540 else 2 if s <= 600 else inf],
                      "fixed_optima": [p["bundles"] for p in feasible if p["fixed"] and p["cost"] == fixed_cost],
                      "regime_optima": [p["bundles"] for p in feasible if p["cost"] == adaptive_cost]})
    cutoff = [max((p["cutoff"] for p in policies if p["feasible"] and p["fixed"]), default=-inf),
              max((p["cutoff"] for p in policies if p["feasible"]), default=-inf),
              direct_cutoff(regimes[1])]
    component_cutoff = [acquisition_deadline(records, actions, observations, features),
                        min(acquisition_deadline(tuple(x for x in records if x[0] == e), actions, observations, features)
                            for e in (1, 2)),
                        acquisition_deadline(tuple(x for x in records if x[0] == 2), actions, observations, features)]
    return {"domain": {"situations": 4, "feature_bundles": 8, "fixed_policies": 8,
                       "regime_dependent_policies": len(policies), "times": TIMES,
                       "information_cost_and_delay_included": False,
                       "policy_cost": "maximum acquisition cost over regimes; no source prior"},
            "costs": costs, "policy_cutoffs": cutoff, "component_cutoffs": component_cutoff,
            "regime_2_costs": [required_cost(regimes[1], s) for s in TIMES],
            "policies": policies}


def bounded_summary():
    return {"mechanisms": mechanism_suite(), "restriction": restriction_suite(),
            "early_information": early_information_suite()}


def bounded_records(results):
    m, r, e = (results[k] for k in ("mechanisms", "restriction", "early_information"))
    records = [make_record("common rules across channel pairs", m["domain"], len(m["mismatches"]), 0,
                           details={"cases": m["cases"], "rule_profile_evaluations": m["rule_profile_evaluations"],
                                    "mismatches": m["mismatches"]})]
    for name, expected in (("separately_feasible_only", False), ("common_rule_exists", True)):
        item = m["examples"][name]
        records.append(make_record("mechanisms " + name, {"channels": 2, "rules": 16},
                                   [item["separate_feasibility"], item["union_feasible"], item["direct_feasible"]],
                                   [[True, True], expected, expected]))
    records.append(make_record("restriction selection feasibility", r["domain"],
                               [[x["graph_feasible"], row["graph_feasible"], not x["graph_feasible"] or row["graph_feasible"]]
                                for c in r["cases"] for x, row in zip(c["full_selections"], c["restricted_selections"])],
                               [[x["direct_feasible"], row["direct_feasible"], True] for c in r["cases"]
                                for x, row in zip(c["full_selections"], c["restricted_selections"])]))
    for key, label, direction in (("costs", "required costs", -1), ("deadlines", "acquisition cutoffs", 1)):
        records.append(make_record("restriction " + label, r["domain"],
                                   [[row["graph"], row["graph"][1] <= row["graph"][0] if direction == -1
                                     else row["graph"][1] >= row["graph"][0]]
                                    for c in r["cases"] for row in c[key]],
                                   [[row["direct"], True] for c in r["cases"] for row in c[key]]))
    records.append(make_record("early regime acquisition costs", e["domain"],
                               [[c["component_costs"], c["policy_costs"]] for c in e["costs"]],
                               [[c["worksheet_costs"], c["worksheet_costs"]] for c in e["costs"]]))
    records.append(make_record("early regime acquisition cutoffs", e["domain"],
                               [e["policy_cutoffs"], e["component_cutoffs"]], [[600, 600, 660], [600, 600, 660]]))
    early, later = e["costs"][1], e["costs"][3]
    records.append(make_record("worksheet optimal bundles", {"times": (540, 600)},
                               [early["fixed_optima"], early["regime_optima"], later["fixed_optima"], later["regime_optima"]],
                               [[(("g",), ("g",))], [(("g",), ("g",))],
                                [(("f", "h"), ("f", "h"))], [(("f",), ("h",))]]))
    records.append(make_record("regime-2 conditional availability", {"times": TIMES},
                               e["regime_2_costs"], [1, 1, 2, 2, 2, 2, inf, inf]))
    return records
