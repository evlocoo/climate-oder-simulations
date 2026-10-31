"""Constructive marginal-support guarantee and finite coupling comparisons."""

from fractions import Fraction
from itertools import product

from .research_checks.marginal_support import ACTIONS, SUPPORTS


def certificate(supports, accepted, catalogue=(0, 1)):
    if not supports or len(supports[0]) < 2:
        raise ValueError("source-component certificate requires at least two participants")
    actors = len(supports[0])
    if len(accepted) != len(supports) or not catalogue:
        raise ValueError("provide one acceptable set per source and a nonempty plan catalogue")
    if any(len(row) != actors or any(not values for values in row) for row in supports):
        raise ValueError("nonempty conditional supports and constant participant count required")
    remaining = set(range(len(supports)))
    groups = []
    while remaining:
        group = {min(remaining)}
        frontier = list(group)
        remaining -= group
        while frontier:
            x = frontier.pop()
            joined = {y for y in remaining if any(supports[x][i] & supports[y][i] for i in range(actors))}
            frontier.extend(sorted(joined))
            group |= joined
            remaining -= joined
        groups.append(sorted(group))
    rules = [{} for _ in range(actors)]
    for group in groups:
        common = set(catalogue)
        for x in group:
            common &= set(accepted[x])
        if not common:
            return {"feasible": False, "components": groups, "rules": []}
        choice = min(common)
        for x in group:
            for actor, values in enumerate(supports[x]):
                for symbol in values:
                    rules[actor][symbol] = choice
    return {"feasible": True, "components": groups, "rules": rules}


def succeeds(rules, supports, accepted):
    return all(len({rules[i][r[i]] for i in range(len(r))}) == 1
               and rules[0][r[0]] in accepted[x]
               for x, row in enumerate(supports) for r in product(*row))


def direct(supports, accepted):
    alphabets = [sorted(set().union(*(row[i] for row in supports)), key=repr)
                 for i in range(len(supports[0]))]
    for tables in product(*(tuple(product((0, 1), repeat=len(a))) for a in alphabets)):
        rules = [dict(zip(a, table)) for a, table in zip(alphabets, tables)]
        if succeeds(rules, supports, accepted):
            return True
    return False


def construction_suite():
    cases = constructed = 0
    mismatches = []
    for actors, sizes in ((2, (1, 2, 3)), (3, (1, 2))):
        for sources in sizes:
            for config in product(SUPPORTS, repeat=actors * sources):
                supports = tuple(config[x * actors:(x + 1) * actors] for x in range(sources))
                for accepted in product(ACTIONS, repeat=sources):
                    cases += 1
                    result = certificate(supports, accepted)
                    if result["feasible"]:
                        constructed += 1
                        # Symbol 2 is unused; a legal default must not alter reached behavior.
                        rules = [dict(rule) for rule in result["rules"]]
                        for rule in rules:
                            rule[2] = 0
                        if not succeeds(rules, supports, accepted):
                            mismatches.append({"supports": supports, "accepted": accepted,
                                               "rules": rules})
    return {"cases": cases, "constructed_profiles_checked": constructed, "mismatches": mismatches}


def binary_couplings(p, q):
    low, high = max(Fraction(0), p + q - 1), min(p, q)
    values = sorted({low, high, (low + high) / 2, p * q})
    return [{(0, 0): t, (0, 1): p - t, (1, 0): q - t, (1, 1): 1 - p - q + t}
            for t in values]


def coupling_suite():
    probabilities = (Fraction(0), Fraction(1, 3), Fraction(1, 2), Fraction(1))
    laws = tuple(product(probabilities, repeat=2))
    cases = profile_checks = 0
    mismatches = []
    for source_laws in product(laws, repeat=2):
        channels = [binary_couplings(p, q) for p, q in source_laws]
        supports = tuple(tuple(frozenset(b for b, mass in ((0, prob), (1, 1 - prob)) if mass > 0)
                               for prob in law) for law in source_laws)
        for accepted in product(ACTIONS, repeat=2):
            cases += 1
            expected = certificate(supports, accepted)["feasible"]
            feasible = False
            for profile in product(range(4), repeat=2):
                profile_checks += 1
                good = all(len({(profile[i] >> r[i]) & 1 for i in (0, 1)}) == 1
                           and ((profile[0] >> r[0]) & 1) in accepted[x]
                           for x, choices in enumerate(channels) for channel in choices
                           for r, mass in channel.items() if mass > 0)
                feasible |= good
            if feasible != expected:
                mismatches.append({"conditional_marginals": source_laws, "accepted": accepted,
                                   "certificate": expected, "direct": feasible})
    return {"cases": cases, "rule_profiles_evaluated": profile_checks,
            "probabilities_of_zero": probabilities,
            "couplings": "Frechet endpoints, midpoint, and product; duplicate laws removed",
            "mismatches": mismatches}


def feature_suite():
    cases = 0
    mismatches = []
    example = []
    for config in product(SUPPORTS, repeat=4):
        base = (config[:2], config[2:])
        for accepted in product(ACTIONS, repeat=2):
            for selected in ((), (0,), (1,), (0, 1)):
                cases += 1
                refined = tuple(tuple(frozenset((r, x if i in selected else None) for r in base[x][i])
                                      for i in (0, 1)) for x in (0, 1))
                predicted_edges = [i for i in (0, 1) if base[0][i] & base[1][i] and i not in selected]
                actual_edges = [i for i in (0, 1) if refined[0][i] & refined[1][i]]
                computed = certificate(refined, accepted)["feasible"]
                independent = direct(refined, accepted)
                if computed != independent or predicted_edges != actual_edges:
                    mismatches.append({"supports": base, "accepted": accepted, "selected_owners": selected,
                                       "predicted_edges": predicted_edges, "actual_edges": actual_edges,
                                       "certificate": computed, "direct": independent})
                if all(s == SUPPORTS[2] for s in config) and accepted == (ACTIONS[1], ACTIONS[2]):
                    example.append({"selected_owners": selected, "surviving_edges": actual_edges,
                                    "feasible": computed})
    return {"cases": cases, "mismatches": mismatches, "example": example}
