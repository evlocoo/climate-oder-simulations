import unittest
from fractions import Fraction

from oder_supplement.coordination import (
    acquisition_deadline,
    budget_preservation_example,
    compare_preservation_subsets,
    direct_shared_rule_enumeration,
    nonuniform_shelter_formula,
    shared_plan_graph_criterion,
    shelter_example,
)
from oder_supplement.reporting import make_record, summarize_records
from oder_supplement.stochastic import exhaustive_mixture_optimum_family, mixture_average_optimum
from oder_supplement.finite import common_action_report, heat_action_sets, minutes, minimum_category_count_by_cover
from oder_supplement.stochastic import diagnostic_channels, direct_rule_check, exhaustive_two_world_support_family, marginal_channel, supported_graph_criterion, validate_channel
from oder_supplement.timing import enumerate_two_edge_schedule, latest_recovery_start, schedule_verification_cases


class VerificationTests(unittest.TestCase):
    def test_heat_common_action_changes_with_time(self):
        records = ("A", "B")
        coarse = {"A": "same", "B": "same"}
        self.assertTrue(common_action_report(records, heat_action_sets(minutes("10:00")), coarse)["sufficient"])
        self.assertFalse(common_action_report(records, heat_action_sets(minutes("11:00")), coarse)["sufficient"])
        self.assertEqual(minimum_category_count_by_cover(records, heat_action_sets(minutes("10:00")))[0], 1)
        self.assertEqual(minimum_category_count_by_cover(records, heat_action_sets(minutes("11:00")))[0], 2)

    def test_shelter_direct_and_graph_checks_agree(self):
        records, action_sets, observations = shelter_example()
        graph = shared_plan_graph_criterion(records, action_sets, observations)
        direct = direct_shared_rule_enumeration(records, action_sets, observations, {x: Fraction(1, 3) for x in records})
        self.assertFalse(graph["succeeds"])
        self.assertEqual(direct["guaranteed_rule_count"], 0)
        self.assertEqual(direct["rule_tuple_count"], 16)
        self.assertEqual(direct["best_score"], Fraction(2, 3))

    def test_shelter_nonuniform_formulas(self):
        probabilities = {1: Fraction(2, 5), 2: Fraction(2, 5), 3: Fraction(1, 5)}
        result = nonuniform_shelter_formula(probabilities)
        self.assertEqual(result["all_local_rule_optimum"], result["formula_all_local"])
        self.assertEqual(result["individually_adequate_optimum"], result["formula_displayed_rules"])

    def test_budget_deadlines(self):
        records, action_sets, observations, features = budget_preservation_example()
        self.assertEqual(acquisition_deadline(records, action_sets, observations, features, budget=1), minutes("09:00"))
        self.assertEqual(acquisition_deadline(records, action_sets, observations, features, budget=3), minutes("09:00"))
        self.assertEqual(acquisition_deadline(records, action_sets, observations, features, budget=4), minutes("10:00"))
        comparison = compare_preservation_subsets(records, action_sets, observations, features)
        self.assertTrue(comparison["all_agree"])
        self.assertEqual(comparison["minimum_witness_cost"], comparison["minimum_direct_cost"])

    def test_timing_boundaries(self):
        self.assertEqual(latest_recovery_start(), minutes("11:15"))
        schedule = enumerate_two_edge_schedule()
        self.assertEqual(schedule["latest"]["A"], minutes("10:00"))
        self.assertEqual(schedule["latest"]["B"], minutes("10:20"))
        self.assertTrue(schedule["reset_without_storage_blocks"])
        cases = schedule_verification_cases()
        self.assertTrue(cases["free_holding_memory"]["enumerated_feasible"])
        self.assertFalse(cases["unavailable_route"]["enumerated_feasible"])
        self.assertFalse(cases["reset_without_storage"]["enumerated_feasible"])
        self.assertTrue(cases["reset_with_storage_repair"]["enumerated_feasible"])
        self.assertTrue(cases["boundary_receipt_and_send"]["enumerated_feasible"])

    def test_stochastic_aligned_crossed_diagnostic(self):
        action_sets, aligned, crossed = diagnostic_channels()
        self.assertEqual(marginal_channel(aligned, 0), marginal_channel(crossed, 0))
        self.assertEqual(marginal_channel(aligned, 1), marginal_channel(crossed, 1))
        self.assertTrue(supported_graph_criterion(aligned, action_sets)["succeeds"])
        self.assertTrue(direct_rule_check(aligned, action_sets)["succeeds"])
        self.assertFalse(supported_graph_criterion(crossed, action_sets)["succeeds"])
        self.assertFalse(direct_rule_check(crossed, action_sets)["succeeds"])

    def test_stochastic_exhaustive_family(self):
        family = exhaustive_two_world_support_family()
        self.assertEqual(family["case_count"], 2025)
        self.assertEqual(family["rule_pair_checks"], 2025 * 16)
        self.assertEqual(family["mismatch_count"], 0)

    def test_mixture_optimum_family(self):
        family = exhaustive_mixture_optimum_family()
        self.assertEqual((family["prior_count"], family["epsilon_count"]), (66, 11))
        self.assertEqual(family["case_count"], 726)
        self.assertEqual(family["rule_pair_checks"], 11616)
        self.assertEqual(family["mismatch_count"], 0)

    def test_mixture_constant_plan_improves_average(self):
        result = mixture_average_optimum(
            {"L": Fraction(1, 10), "M": Fraction(6, 10), "R": Fraction(3, 10)}, Fraction(1, 2))
        self.assertEqual(result["direct_optimum"], Fraction(9, 10))
        self.assertEqual(result["label_following_average_success"], Fraction(7, 10))
        self.assertIn([{0: "b", 1: "b"}, {0: "b", 1: "b"}], result["best_rules"])

    def test_mixture_endpoints_and_zero_weights(self):
        for epsilon, prior, expected in (
            (0, {"L": Fraction(1, 3), "M": Fraction(1, 3), "R": Fraction(1, 3)}, Fraction(1)),
            (1, {"L": Fraction(1, 3), "M": Fraction(1, 3), "R": Fraction(1, 3)}, Fraction(2, 3)),
            (1, {"L": 0, "M": Fraction(1, 2), "R": Fraction(1, 2)}, Fraction(1)),
        ):
            with self.subTest(epsilon=epsilon, prior=prior):
                result = mixture_average_optimum(prior, epsilon)
                self.assertEqual(result["direct_optimum"], expected)
                self.assertEqual(result["stated_formula"], expected)
                self.assertEqual(result["rule_pairs_checked"], 16)
        with self.assertRaises(ValueError):
            mixture_average_optimum({"L": 0, "M": 0, "R": 0}, 0)

    def test_channel_validation(self):
        self.assertTrue(validate_channel({"x": {(0, 0): Fraction(1)}}))
        with self.assertRaises(ValueError):
            validate_channel({"x": {(0, 0): Fraction(1, 2)}})
        with self.assertRaises(ValueError):
            validate_channel({"x": {(0, 0): Fraction(1), (1,): Fraction(0)}})

    def test_reporting_records_failures(self):
        records = [
            make_record("deliberate mismatch", {"isolated": True}, True, False),
            make_record("ordinary pass", {"isolated": True}, True, True),
        ]
        summary = summarize_records(records, run_id="test-run")
        self.assertEqual(summary["failure_count"], 1)
        self.assertEqual(summary["failures"][0]["case"], "deliberate mismatch")


if __name__ == "__main__":
    unittest.main()
