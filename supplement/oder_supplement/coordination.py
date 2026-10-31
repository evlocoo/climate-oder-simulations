"""Distributed shared-plan and preservation checks."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, product
from math import inf


@dataclass(frozen=True)
class Feature:
    name: str
    actor: str
    values: dict
    cost: int
    deadline: int


def action_universe(action_sets):
    return tuple(sorted({a for values in action_sets.values() for a in values}))


def components_from_observations(records, observations):
    parent = {x: x for x in records}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    actors = tuple(observations)
    for x, y in combinations(records, 2):
        if any(observations[i][x] == observations[i][y] for i in actors):
            union(x, y)
    grouped = {}
    for x in records:
        grouped.setdefault(find(x), []).append(x)
    return tuple(tuple(sorted(v, key=str)) for v in grouped.values())


def shared_plan_graph_criterion(records, action_sets, observations):
    comps = components_from_observations(records, observations)
    choices = {}
    failures = []
    for comp in comps:
        common = set(action_sets[comp[0]])
        for x in comp[1:]:
            common &= set(action_sets[x])
        if common:
            choices[comp] = sorted(common)[0]
        else:
            failures.append(comp)
    return {"succeeds": not failures, "components": comps, "component_choices": choices, "failed_components": tuple(failures)}


def all_local_rules(obs_values, actions):
    obs_values = tuple(sorted(set(obs_values), key=str))
    for choices in product(actions, repeat=len(obs_values)):
        yield dict(zip(obs_values, choices))


def direct_shared_rule_enumeration(records, action_sets, observations, probabilities=None, require_individual=False):
    """Try every deterministic local rule tuple without using graph components."""
    actors = tuple(observations)
    actions = action_universe(action_sets)
    if not actions:
        return {
            "actors": actors,
            "actions": actions,
            "rule_tuple_count": 0,
            "guaranteed_rule_count": 0,
            "best_score": 0,
            "best_rules": [],
            "situation_scores": {},
        }
    rule_lists = [tuple(all_local_rules(observations[actor].values(), actions)) for actor in actors]
    if probabilities is None:
        probabilities = {x: 1 / len(records) for x in records}
    best_score = -1
    best_rules = []
    guaranteed = []
    situation_scores = {}
    for combo in product(*rule_lists):
        rules = dict(zip(actors, combo))
        if require_individual:
            if not all(rules[actor][observations[actor][x]] in action_sets[x] for actor in actors for x in records):
                continue
        successes = {}
        for x in records:
            chosen = [rules[actor][observations[actor][x]] for actor in actors]
            successes[x] = len(set(chosen)) == 1 and chosen[0] in action_sets[x]
        score = sum(probabilities[x] for x in records if successes[x])
        key = tuple((actor, tuple(sorted(rule.items()))) for actor, rule in rules.items())
        situation_scores[key] = successes
        if score > best_score:
            best_score = score
            best_rules = [rules]
        elif score == best_score:
            best_rules.append(rules)
        if all(successes.values()):
            guaranteed.append(rules)
    return {
        "actors": actors,
        "actions": actions,
        "rule_tuple_count": 1 if not rule_lists else product_len(rule_lists),
        "guaranteed_rule_count": len(guaranteed),
        "best_score": best_score,
        "best_rules": best_rules,
        "situation_scores": situation_scores,
    }


def product_len(lists):
    out = 1
    for values in lists:
        out *= len(values)
    return out


def shelter_example():
    records = (1, 2, 3)
    action_sets = {1: {"a"}, 2: {"a", "b"}, 3: {"b"}}
    observations = {
        "transport": {1: "12", 2: "12", 3: "3"},
        "receiving": {1: "1", 2: "23", 3: "23"},
    }
    return records, action_sets, observations


def baseline_labelled_edges(records, observations):
    edges = []
    for actor, obs in observations.items():
        for x, y in combinations(records, 2):
            if obs[x] == obs[y]:
                edges.append((x, y, actor))
    return tuple(edges)


def connected_by_edges(vertices, edges):
    if len(vertices) == 1:
        return True
    parent = {v: v for v in vertices}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for x, y, _ in edges:
        union(x, y)
    return len({find(v) for v in vertices}) == 1


def is_tree(vertices, edges):
    return len(edges) == len(vertices) - 1 and connected_by_edges(vertices, edges)


def common_actions_for_vertices(vertices, action_sets):
    if not vertices:
        return set()
    common = set(action_sets[vertices[0]])
    for x in vertices[1:]:
        common &= set(action_sets[x])
    return common


def bad_witness_trees(records, action_sets, observations):
    """Enumerate all actor-labelled bad witness trees for declared small domains."""
    records = tuple(records)
    edges = baseline_labelled_edges(records, observations)
    witnesses = []
    for size in range(1, len(records) + 1):
        for vertices in combinations(records, size):
            vertices = tuple(vertices)
            if common_actions_for_vertices(vertices, action_sets):
                continue
            if size == 1:
                witnesses.append({"vertices": vertices, "edges": (), "singleton_empty": True})
                continue
            candidate_edges = tuple(e for e in edges if e[0] in vertices and e[1] in vertices)
            for edge_subset in combinations(candidate_edges, size - 1):
                if is_tree(vertices, edge_subset):
                    witnesses.append({"vertices": vertices, "edges": tuple(edge_subset), "singleton_empty": False})
    return tuple(witnesses)


def repair_features_for_witness(witness, features):
    repairs = []
    for feature in features:
        for x, y, actor in witness["edges"]:
            if feature.actor == actor and feature.values[x] != feature.values[y]:
                repairs.append(feature.name)
                break
    return tuple(sorted(repairs))


def witness_constraints(records, action_sets, observations, features):
    witnesses = bad_witness_trees(records, action_sets, observations)
    return tuple(
        {
            "vertices": witness["vertices"],
            "edges": witness["edges"],
            "repairs": repair_features_for_witness(witness, features),
            "singleton_empty": witness["singleton_empty"],
        }
        for witness in witnesses
    )


def witness_feasible(records, action_sets, observations, features, selected_feature_names):
    selected = set(selected_feature_names)
    for constraint in witness_constraints(records, action_sets, observations, features):
        if not selected.intersection(constraint["repairs"]):
            return False, constraint
    return True, None


def direct_refined_feasible(records, action_sets, observations, features):
    refined = refine_observations(records, observations, features)
    direct = direct_shared_rule_enumeration(records, action_sets, refined)
    return direct["guaranteed_rule_count"] > 0, direct


def compare_preservation_subsets(records, action_sets, observations, features, budget=None, available_at=None):
    candidates = list(features)
    if available_at is not None:
        candidates = [f for f in candidates if available_at <= f.deadline]
    records_out = []
    for mask in range(1 << len(candidates)):
        selected = [candidates[i] for i in range(len(candidates)) if mask & (1 << i)]
        cost = selected_feature_cost(selected)
        if budget is not None and cost > budget:
            continue
        witness_ok, failed_constraint = witness_feasible(records, action_sets, observations, features, [f.name for f in selected])
        direct_ok, direct = direct_refined_feasible(records, action_sets, observations, selected)
        records_out.append(
            {
                "selected": tuple(f.name for f in selected),
                "cost": cost,
                "witness_feasible": witness_ok,
                "direct_feasible": direct_ok,
                "agree": witness_ok == direct_ok,
                "failed_constraint": failed_constraint,
                "direct_rule_count": direct["guaranteed_rule_count"],
            }
        )
    witness_costs = [r["cost"] for r in records_out if r["witness_feasible"]]
    direct_costs = [r["cost"] for r in records_out if r["direct_feasible"]]
    return {
        "subset_comparisons": len(records_out),
        "all_agree": all(r["agree"] for r in records_out),
        "minimum_witness_cost": None if not witness_costs else min(witness_costs),
        "minimum_direct_cost": None if not direct_costs else min(direct_costs),
        "records": tuple(records_out),
        "constraints": witness_constraints(records, action_sets, observations, features),
    }


def repaired_shelter_examples():
    records, action_sets, baseline = shelter_example()
    transport_repair = {
        "transport": {1: "1", 2: "2", 3: "3"},
        "receiving": baseline["receiving"],
    }
    receiving_repair = {
        "transport": baseline["transport"],
        "receiving": {1: "1", 2: "2", 3: "3"},
    }
    return records, action_sets, {"transport_repair": transport_repair, "receiving_repair": receiving_repair}


def nonuniform_shelter_formula(probabilities):
    records, action_sets, observations = shelter_example()
    all_rules = direct_shared_rule_enumeration(records, action_sets, observations, probabilities)
    individually_ok = direct_shared_rule_enumeration(records, action_sets, observations, probabilities, require_individual=True)
    return {
        "all_local_rule_optimum": all_rules["best_score"],
        "formula_all_local": 1 - min(probabilities.values()),
        "individually_adequate_optimum": individually_ok["best_score"],
        "formula_displayed_rules": 1 - probabilities[2],
    }


def refine_observations(records, observations, features):
    refined = {}
    for actor, base in observations.items():
        actor_features = [f for f in features if f.actor == actor]
        refined[actor] = {x: (base[x], tuple((f.name, f.values[x]) for f in actor_features)) for x in records}
    return refined


def selected_feature_cost(features):
    return sum(f.cost for f in features)


def optimize_features(records, action_sets, observations, features, budget=None, available_at=None):
    """Exact exhaustive subset optimization, suitable for small supplement domains."""
    candidates = list(features)
    if available_at is not None:
        candidates = [f for f in candidates if available_at <= f.deadline]
    best_cost = inf
    best_sets = []
    checked = 0
    for mask in range(1 << len(candidates)):
        selected = [candidates[i] for i in range(len(candidates)) if mask & (1 << i)]
        cost = selected_feature_cost(selected)
        if budget is not None and cost > budget:
            continue
        checked += 1
        result = shared_plan_graph_criterion(records, action_sets, refine_observations(records, observations, selected))
        if result["succeeds"]:
            if cost < best_cost:
                best_cost = cost
                best_sets = [(tuple(selected), result)]
            elif cost == best_cost:
                best_sets.append((tuple(selected), result))
    baseline = shared_plan_graph_criterion(records, action_sets, observations)
    obstruction = baseline["failed_components"][0] if baseline["failed_components"] else None
    return {
        "solver": "exhaustive_subset_enumeration",
        "status": "optimal" if best_sets else "infeasible",
        "checked_subsets": checked,
        "minimum_cost": None if not best_sets else best_cost,
        "solutions": best_sets,
        "baseline_obstruction": obstruction,
    }


def budget_preservation_example():
    records = tuple((e, b) for e in (1, 2) for b in (0, 1))
    action_sets = {x: {f"plan_{x[1]}"} for x in records}
    observations = {
        "transport": {x: ("regime", x[0]) for x in records},
        "receiving": {x: ("full", x) for x in records},
    }
    features = (
        Feature("g", "transport", {x: x[1] for x in records}, 1, 9 * 60),
        Feature("f", "transport", {x: x[1] if x[0] == 1 else 0 for x in records}, 2, 10 * 60),
        Feature("h", "transport", {x: x[1] if x[0] == 2 else 0 for x in records}, 2, 11 * 60),
    )
    return records, action_sets, observations, features


def acquisition_deadline(records, action_sets, observations, features, budget=None):
    cutoffs = sorted({f.deadline for f in features}, reverse=True)
    if shared_plan_graph_criterion(records, action_sets, observations)["succeeds"]:
        return inf
    for cutoff in cutoffs:
        result = optimize_features(records, action_sets, observations, features, budget=budget, available_at=cutoff)
        if result["status"] == "optimal":
            return cutoff
    return -inf


def preservation_case_suite():
    records, action_sets, observations, features = budget_preservation_example()
    cases = {}
    cases["budget_example"] = {
        "domain": {"situations": len(records), "participants": len(observations), "features": len(features), "subsets": 2 ** len(features)},
        "baseline": shared_plan_graph_criterion(records, action_sets, observations),
        "unlimited_deadline": acquisition_deadline(records, action_sets, observations, features),
        "budget_deadlines": {B: acquisition_deadline(records, action_sets, observations, features, budget=B) for B in (1, 2, 3, 4)},
        "minimum": optimize_features(records, action_sets, observations, features),
        "witness_direct_comparison": compare_preservation_subsets(records, action_sets, observations, features),
    }
    small_cases = {
        "baseline_feasible_no_features": ((1, 2), {1: {"a"}, 2: {"a"}}, {"actor": {1: "same", 2: "same"}}, ()),
        "no_available_repair": ((1, 2), {1: {"a"}, 2: {"b"}}, {"actor": {1: "same", 2: "same"}}, ()),
        "multiple_optimal_repairs": (
            (1, 2),
            {1: {"a"}, 2: {"b"}},
            {"actor": {1: "same", 2: "same"}},
            (
                Feature("left_copy", "actor", {1: 0, 2: 1}, 1, 9 * 60),
                Feature("right_copy", "actor", {1: "x", 2: "y"}, 1, 9 * 60),
            ),
        ),
        "singleton_no_action": ((1,), {1: set()}, {"actor": {1: "only"}}, ()),
        "different_participants": (
            (1, 2, 3),
            {1: {"a"}, 2: {"a", "b"}, 3: {"b"}},
            {"transport": {1: "12", 2: "12", 3: "3"}, "receiving": {1: "1", 2: "23", 3: "23"}},
            (
                Feature("transport_12", "transport", {1: 0, 2: 1, 3: 1}, 1, 10 * 60),
                Feature("receiving_23", "receiving", {1: 0, 2: 0, 3: 1}, 1, 10 * 60),
            ),
        ),
    }
    for name, (case_records, case_actions, case_observations, case_features) in small_cases.items():
        result = optimize_features(case_records, case_actions, case_observations, case_features)
        result["domain"] = {
            "situations": len(case_records),
            "participants": len(case_observations),
            "features": len(case_features),
            "subsets": 2 ** len(case_features),
        }
        result["witness_direct_comparison"] = compare_preservation_subsets(case_records, case_actions, case_observations, case_features)
        cases[name] = result
    return cases
