"""Worked examples and JSON-friendly summary builders."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from fractions import Fraction
from math import inf

from . import __version__
from .bounded import bounded_records, bounded_summary
from .temporal import temporal_records, temporal_summary
from .monotone import monotone_records, monotone_summary
from .locator import locator_records, locator_summary
from .research import research_records, research_summary
from .coordination import (
    acquisition_deadline,
    compare_preservation_subsets,
    direct_shared_rule_enumeration,
    nonuniform_shelter_formula,
    preservation_case_suite,
    repaired_shelter_examples,
    shared_plan_graph_criterion,
    shelter_example,
)
from .finite import (
    common_action_report,
    enumerate_lookup_rules,
    heat_action_sets,
    heat_briefing_checks,
    hhmm,
    minimum_category_count_by_cover,
    minimum_partitions_by_enumeration,
    minutes,
    stochastic_retention_heat,
)
from .stochastic import (
    diagnostic_channels,
    direct_rule_check,
    exhaustive_two_world_support_family,
    exhaustive_mixture_optimum_family,
    manuscript_support_sensitivity,
    marginal_channel,
    support_sensitivity_channel,
    supported_realizations,
    supported_graph_criterion,
)
from .timing import enumerate_two_edge_schedule, heat_timing_rows, latest_recovery_start, message_timing, schedule_verification_cases
from .reporting import make_record, summarize_records


def clean(value):
    if isinstance(value, Fraction):
        return str(value)
    if value == inf:
        return "infinity"
    if value == -inf:
        return "-infinity"
    if is_dataclass(value):
        return clean(asdict(value))
    if isinstance(value, dict):
        return {str(clean(k)): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [clean(v) for v in value]
    return value


def run_single_actor_examples():
    records = ("A", "B")
    rows = heat_briefing_checks()
    pairwise_records = (1, 2, 3)
    pairwise_actions = {1: {"a", "b"}, 2: {"b", "c"}, 3: {"a", "c"}}
    pairwise_rep = {1: "merged", 2: "merged", 3: "merged"}
    return {
        "domain_sizes": {"heat_records": 2, "pairwise_records": 3},
        "heat_rows": rows,
        "late_coarse_rules_by_direct_enumeration": len(enumerate_lookup_rules(records, heat_action_sets(minutes("11:00")), {"A": "coarse", "B": "coarse"})),
        "minimum_cover_10_00": minimum_category_count_by_cover(records, heat_action_sets(minutes("10:00"))),
        "minimum_cover_11_00": minimum_category_count_by_cover(records, heat_action_sets(minutes("11:00"))),
        "minimum_partitions_11_00": minimum_partitions_by_enumeration(records, heat_action_sets(minutes("11:00"))),
        "pairwise_not_enough": common_action_report(pairwise_records, pairwise_actions, pairwise_rep),
        "stochastic_retention": [stochastic_retention_heat(e) for e in (Fraction(0), Fraction(1, 10), Fraction(1, 6), Fraction(1, 5))],
    }


def run_shelter_examples():
    records, action_sets, observations = shelter_example()
    uniform = {x: Fraction(1, 3) for x in records}
    direct = direct_shared_rule_enumeration(records, action_sets, observations, uniform)
    graph = shared_plan_graph_criterion(records, action_sets, observations)
    _, _, repairs = repaired_shelter_examples()
    repair_results = {name: shared_plan_graph_criterion(records, action_sets, obs) for name, obs in repairs.items()}
    rational_examples = {
        "balanced": nonuniform_shelter_formula({1: Fraction(1, 3), 2: Fraction(1, 3), 3: Fraction(1, 3)}),
        "middle_heavy": nonuniform_shelter_formula({1: Fraction(1, 5), 2: Fraction(3, 5), 3: Fraction(1, 5)}),
        "right_light": nonuniform_shelter_formula({1: Fraction(2, 5), 2: Fraction(2, 5), 3: Fraction(1, 5)}),
    }
    displayed = {
        "transport": {1: "a", 2: "a", 3: "b"},
        "receiving": {1: "a", 2: "b", 3: "b"},
    }
    displayed_success = {x: displayed["transport"][x] == displayed["receiving"][x] and displayed["transport"][x] in action_sets[x] for x in records}
    return {
        "domain_sizes": {"situations": 3, "participants": 2, "binary_rule_pairs": direct["rule_tuple_count"]},
        "direct_enumeration": direct,
        "graph_criterion": graph,
        "displayed_individually_adequate_rules": displayed,
        "displayed_joint_success_by_situation": displayed_success,
        "repairs": repair_results,
        "nonuniform": rational_examples,
    }


def run_preservation_examples():
    return preservation_case_suite()


def run_timing_examples():
    schedule = enumerate_two_edge_schedule()
    schedule_cases = schedule_verification_cases()
    return {
        "heat_timing_rows": heat_timing_rows(),
        "latest_recovery_start": hhmm(latest_recovery_start()),
        "unknown_later_task_latest_start": hhmm(int(message_timing(8, 2, minutes("10:00")))),
        "known_task_latest_start_minutes_after_09_59": message_timing(1, 2, minutes("10:00")) - minutes("09:59"),
        "contact_dag": schedule,
        "schedule_enumeration_cases": schedule_cases,
    }


def run_stochastic_coordination_examples():
    action_sets, aligned, crossed = diagnostic_channels()
    support_channel, support_actions = support_sensitivity_channel()
    family = exhaustive_two_world_support_family()
    sensitivity = manuscript_support_sensitivity()
    return {
        "domain_sizes": {
            "aligned_supported_realizations": len(supported_realizations(aligned)),
            "crossed_supported_realizations": len(supported_realizations(crossed)),
            "support_sensitivity_realizations": len(supported_realizations(support_channel)),
            "exhaustive_support_action_cases": family["case_count"],
        },
        "status": "manuscript proposition coord:prop:stochastic",
        "aligned": {
            "graph": supported_graph_criterion(aligned, action_sets),
            "direct": direct_rule_check(aligned, action_sets),
        },
        "crossed": {
            "graph": supported_graph_criterion(crossed, action_sets),
            "direct": direct_rule_check(crossed, action_sets),
        },
        "marginals_equal": {
            "participant_0": marginal_channel(aligned, 0) == marginal_channel(crossed, 0),
            "participant_1": marginal_channel(aligned, 1) == marginal_channel(crossed, 1),
        },
        "support_sensitivity": {
            "graph": supported_graph_criterion(support_channel, support_actions),
            "direct": direct_rule_check(support_channel, support_actions),
        },
        "manuscript_support_sensitivity": sensitivity,
        "exhaustive_two_world_support_family": family,
        "mixture_optimum_family": exhaustive_mixture_optimum_family(),
    }


def verification_records():
    records = []
    single = run_single_actor_examples()
    for row in single["heat_rows"]:
        records.append(
            make_record(
                f"heat coarse briefing {row['time']}",
                {"records": 2, "retained_states": len(row["coarse"]["fibers"])},
                row["coarse"]["sufficient"],
                row["rule_count_check"] > 0,
            )
        )
    records.append(
        make_record(
            "minimum category count at 11:00",
            {"records": 2},
            single["minimum_cover_11_00"][0],
            single["minimum_partitions_11_00"][0],
        )
    )
    shelter = run_shelter_examples()
    records.append(
        make_record(
            "distributed shelter graph versus direct enumeration",
            shelter["domain_sizes"],
            shelter["graph_criterion"]["succeeds"],
            shelter["direct_enumeration"]["guaranteed_rule_count"] > 0,
            details={"best_uniform_success": shelter["direct_enumeration"]["best_score"]},
        )
    )
    for name, result in shelter["nonuniform"].items():
        records.append(
            make_record(
                f"shelter nonuniform all-rule formula {name}",
                {"situations": 3, "participants": 2},
                result["all_local_rule_optimum"],
                result["formula_all_local"],
            )
        )
        records.append(
            make_record(
                f"shelter nonuniform individually adequate formula {name}",
                {"situations": 3, "participants": 2},
                result["individually_adequate_optimum"],
                result["formula_displayed_rules"],
            )
        )
    pres = run_preservation_examples()
    for name, result in pres.items():
        comparison = result["witness_direct_comparison"]
        records.append(
            make_record(
                f"preservation witness/direct subset feasibility {name}",
                result["domain"],
                comparison["all_agree"],
                True,
                details={
                    "subset_comparisons": comparison["subset_comparisons"],
                    "minimum_witness_cost": comparison["minimum_witness_cost"],
                    "minimum_direct_cost": comparison["minimum_direct_cost"],
                    "constraint_count": len(comparison["constraints"]),
                },
            )
        )
        records.append(
            make_record(
                f"preservation minimum cost {name}",
                result["domain"],
                comparison["minimum_witness_cost"],
                comparison["minimum_direct_cost"],
            )
        )
    timing = run_timing_examples()
    for name, case in timing["schedule_enumeration_cases"].items():
        expected_same = name not in {"reset_without_storage"}
        records.append(
            make_record(
                f"schedule recurrence/enumeration {name}",
                {"integer_minute_grid": True, "inclusive_deadlines": True},
                case["recurrence_feasible"],
                case["enumerated_feasible"],
                expected_agreement=expected_same,
                details={"enumerated_schedule_count": case["enumerated_schedule_count"]},
            )
        )
    stoch = run_stochastic_coordination_examples()
    records.append(
        make_record(
            "stochastic aligned diagnostic",
            {"supported_realizations": stoch["domain_sizes"]["aligned_supported_realizations"]},
            stoch["aligned"]["graph"]["succeeds"],
            stoch["aligned"]["direct"]["succeeds"],
        )
    )
    records.append(
        make_record(
            "stochastic crossed diagnostic",
            {"supported_realizations": stoch["domain_sizes"]["crossed_supported_realizations"]},
            stoch["crossed"]["graph"]["succeeds"],
            stoch["crossed"]["direct"]["succeeds"],
        )
    )
    family = stoch["exhaustive_two_world_support_family"]
    records.append(
        make_record(
            "stochastic exhaustive two-world support/action family",
            {"cases": family["case_count"], "rule_pair_checks": family["rule_pair_checks"]},
            family["mismatch_count"],
            0,
            details={"expected_cases": family["expected_case_count"]},
        )
    )
    sensitivity = stoch["manuscript_support_sensitivity"]
    records.append(
        make_record(
            "stochastic support sensitivity label-following average",
            {"epsilon": sensitivity["epsilon"], "p_M": sensitivity["p_M"]},
            sensitivity["label_following_average_success"],
            sensitivity["stated_formula"],
        )
    )
    mixture = stoch["mixture_optimum_family"]
    records.append(
        make_record(
            "stochastic mixture optimum over all local rules",
            {"priors": mixture["prior_count"], "epsilon_values": mixture["epsilon_count"],
             "cases": mixture["case_count"], "rule_pair_checks": mixture["rule_pair_checks"]},
            mixture["mismatch_count"], 0,
            details={"expected_cases": mixture["expected_case_count"], "mismatches": mixture["mismatches"]},
        )
    )
    empty_channel = {"x0": {(0, 0): Fraction(1)}}
    empty_actions = {"x0": set()}
    records.append(
        make_record(
            "stochastic empty acceptable-action set",
            {"sources": 1, "supported_realizations": 1},
            supported_graph_criterion(empty_channel, empty_actions)["succeeds"],
            direct_rule_check(empty_channel, empty_actions)["succeeds"],
        )
    )
    return records


def verification_summary(run_id=None):
    bounded = bounded_summary()
    temporal = temporal_summary()
    monotone = monotone_summary()
    locator = locator_summary()
    research = research_summary()
    records_summary = summarize_records(clean(verification_records() + bounded_records(bounded)
                                             + temporal_records(temporal) + monotone_records(monotone)
                                             + locator_records(locator) + research_records(research)), run_id=run_id)
    summary = {
        "supplement_version": __version__,
        "bounded_extensions": bounded,
        "temporal_preservation": temporal,
        "monotone_response": monotone,
        "locator_frontier": locator,
        "research_comparisons": research,
        "single_actor": run_single_actor_examples(),
        "shelter": run_shelter_examples(),
        "preservation": run_preservation_examples(),
        "timing": run_timing_examples(),
        "stochastic_coordination": run_stochastic_coordination_examples(),
        "verification": records_summary,
        "failures": records_summary["failures"],
    }
    return clean(summary)
