"""Structured verification for maintained research and marginal/frontier checks."""

import traceback
from itertools import product
from pathlib import Path

from .heterogeneous import boundary_suite
from .marginal import construction_suite, coupling_suite, feature_suite, certificate
from .reporting import make_record
from .research_checks import (
    timed_preservation, occurrence_cover, causal_recovery, compatible_execution,
    endpoint_search, endpoint_partition, marginal_support,
)
from .stochastic import diagnostic_channels, direct_rule_check


def checked(function):
    try:
        if not __debug__:
            raise RuntimeError("Research assertion checks require Python without -O")
        return {"result": function(), "error": None}
    except Exception as error:
        frames = traceback.extract_tb(error.__traceback__)
        last = error.__traceback__
        while last.tb_next:
            last = last.tb_next
        names = ("t", "start", "target_count", "n", "m", "durations", "budget", "costs", "T",
                 "mask", "targets", "routes", "observed", "transition", "success", "keep", "accepted", "sx")
        inputs = {key: last.tb_frame.f_locals[key] for key in names if key in last.tb_frame.f_locals}
        return {"result": None, "error": {"type": type(error).__name__, "message": str(error),
                "inputs": inputs,
                "frames": [{"file": Path(f.filename).name, "function": f.name, "line": f.lineno}
                           for f in frames]}}


def dependence_example():
    accepted, aligned, crossed = diagnostic_channels()
    supports = [tuple(frozenset(r[i] for r, mass in aligned[x].items() if mass > 0) for i in (0, 1))
                for x in aligned]
    robust = certificate(supports, list(accepted.values()), catalogue=("a", "b"))
    return {"aligned": direct_rule_check(aligned, accepted)["succeeds"],
            "crossed": direct_rule_check(crossed, accepted)["succeeds"],
            "all_couplings": robust["feasible"]}


def compatible_suite():
    result = compatible_execution.check()
    # Enumerate constant profiles after changing exact demand to a lower bound.
    records = tuple(product((0, 1), repeat=2))
    result["excess_activation_allowed_constant_success"] = any(
        all(sum(actions) >= sum(source) for source in records)
        for actions in product((0, 1), repeat=2)
    )
    return result


def research_summary():
    checks = {
        "single_query": timed_preservation.check,
        "occurrence": occurrence_cover.check,
        "causal_retry": causal_recovery.check,
        "compatible_execution": compatible_suite,
        "endpoint_search": endpoint_search.check,
        "endpoint_partition": endpoint_partition.check,
        "marginal_support": marginal_support.check,
        "heterogeneous_boundaries": boundary_suite,
        "marginal_construction": construction_suite,
        "marginal_couplings": coupling_suite,
        "marginal_features": feature_suite,
        "dependence_contrast": dependence_example,
    }
    return {name: checked(function) for name, function in checks.items()}


DOMAINS = {
    "single_query": {"sources": 4, "binary_target_assignments": 16, "route_maps": 4,
                     "retention_modes": 2, "duration_pairs": [(5, 25), (10, 20), (0, 0)],
                     "start_times": [5, 15, 25, 35, 40, 41], "feature_selections": 4,
                     "model": "one query maximum; wrong fast endpoint inadmissible; no retry"},
    "occurrence": {"sources": 2, "hidden_states": 2, "transition_maps": 16,
                   "success_maps": 16, "observation_maps": 16, "feature_selections": 4,
                   "maximum_decisions": 2, "controller_inputs": "observed symbol and persistent tag; no clock/history"},
    "causal_retry": {"overwrite_starts": "integers 0..60", "retry_targets": [2, 3, 5, 10],
                     "retry_starts": "integers 0..60", "overwrite_model": "source-specific single query",
                     "retry_model": "both endpoints legal; observed failure; reply retained"},
    "compatible_execution": {"sources": 3, "participants": 2, "binary_actions": 2,
                             "nonempty_acceptable_joint_relations": 15, "owned_features": 4,
                             "feature_selections": 16, "scope": "compatible local actions, not shared-plan equivalence",
                             "excess_activation": "four binary demand records; four constant profiles; total activation >= demand"},
    "endpoint_search": {"endpoint_target_pairs": [(2, 2), (2, 3), (3, 2), (3, 3), (4, 3)],
                        "durations": "all vectors in {1,2}^n", "budgets": "integers 0..sum(f)",
                        "encodings": "all partitions with fewer than m cells; target encoding supplies m"},
    "endpoint_partition": {"specifications": [(2, 2, [1, 3]), (2, 3, [1, 3]), (3, 2, [1, 2, 3]),
                                              (3, 3, [1, 2, 3]), (3, 3, [2, 2, 2]), (4, 2, [1, 1, 2, 3])],
                           "budgets": "integers 0..sum(f)", "encodings": "all initial partitions"},
    "marginal_support": {"participants_and_source_counts": {2: [1, 2, 3], 3: [1, 2]},
                         "local_symbols": [0, 1], "plans": [0, 1], "supports": "all three nonempty subsets",
                         "acceptable_sets": "all four subsets including empty", "profiles": "all binary lookup tables"},
    "heterogeneous_boundaries": {"target_duration_vectors": [(2, [2]), (3, [1, 3]), (3, [1, 2, 3]), (5, [1, 1, 2, 2])],
                                 "deadline": 20, "action_duration": 3,
                                 "query_budgets": "every half-unit from -0.5 through sum(f)+0.5"},
    "marginal_construction": {"domain": "same 59760 support/action configurations as marginal_support",
                              "completion": "unused local symbol 2 assigned legal plan 0"},
    "marginal_couplings": {"sources": 2, "participants": 2, "probabilities_of_zero": [0, "1/3", "1/2", 1],
                           "coupling_parameters": "Frechet endpoints, midpoint, product", "acceptable_sets": 16},
    "marginal_features": {"sources": 2, "participants": 2, "support_assignments": 81,
                          "acceptable_assignments": 16, "features": "one source bit owned by each actor",
                          "selections": 4},
    "dependence_contrast": {"sources": 3, "participants": 2, "channels": "aligned, crossed, all couplings"},
}


def research_records(results):
    records = []
    for name, entry in results.items():
        result = entry["result"]
        if entry["error"]:
            records.append(make_record("research " + name, DOMAINS[name], None, None,
                                       exception=entry["error"], details={"execution_failed": True}))
            continue
        if name == "single_query":
            actual = [result["temporal_policy_cover_comparisons"], result["disagreements"], result["minimum_cost_intervals"]]
            expected = [9216, 0, {"0..15": 0, "16..35": 1, "36..40": 2, "41..60": None}]
        elif name == "occurrence":
            actual = [result["occurrence_policy_cover_comparisons"], result["disagreements"],
                      result["false_positives_if_same_source_conflicts_omitted"]]
            expected = [16384, 0, 880]
        elif name == "causal_retry":
            actual = [result[k] for k in ("streaming_policy_cover_comparisons", "streaming_policy_cover_disagreements",
                      "recoverable_retry_checks", "streaming_locator_last_start", "zero_information_with_retry_last_start",
                      "single_source_success_with_constant_source_feature", "single_source_success_with_causal_channel")]
            expected = [61, 0, 244, 35, 30, False, True]
        elif name == "compatible_execution":
            actual = [result[k] for k in ("exhaustive_relation_feature_cases", "disagreements",
                      "example_compatible_min_cost", "example_shared_tuple_min_cost", "global_selector_restriction_counterexample_confirmed",
                      "excess_activation_allowed_constant_success")]
            expected = [54000, 0, 2, 4, True, True]
        elif name == "endpoint_search":
            actual = [result[k] for k in ("models", "arbitrary_encoding_partitions_checked", "disagreements")]
            expected = [232, 241212, 0]
        elif name == "endpoint_partition":
            actual, expected = [result["comparisons"], result["disagreements"]], [39, 0]
        elif name == "marginal_support":
            actual = [result[k] for k in ("cases", "disagreements", "single_actor_direct", "single_actor_component")]
            expected = [59760, 0, True, False]
        elif name == "dependence_contrast":
            actual, expected = result, {"aligned": True, "crossed": False, "all_couplings": False}
        else:
            actual, expected = len(result["mismatches"]), 0
        records.append(make_record("research " + name, DOMAINS[name], actual, expected, details=result))
    return records
