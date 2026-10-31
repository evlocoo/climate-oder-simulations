import json
import tempfile
import unittest
from fractions import Fraction
from itertools import product
from math import ceil, inf
from pathlib import Path
from unittest.mock import patch

import run_verification
from oder_supplement.heterogeneous import packing_number, policy_frontier
from oder_supplement.marginal import binary_couplings, certificate, direct, succeeds
from oder_supplement.research import checked, research_records, research_summary
from oder_supplement.research_checks import timed_preservation, causal_recovery, marginal_support


class ResearchChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary = research_summary()

    def result(self, name):
        self.assertIsNone(self.summary[name]["error"])
        return self.summary[name]["result"]

    def test_original_temporal_domains(self):
        self.assertEqual(self.result("single_query")["temporal_policy_cover_comparisons"], 9216)
        occurrence = self.result("occurrence")
        self.assertEqual(occurrence["occurrence_policy_cover_comparisons"], 16384)
        self.assertEqual(occurrence["false_positives_if_same_source_conflicts_omitted"], 880)
        causal = self.result("causal_retry")
        self.assertEqual(causal["streaming_policy_cover_comparisons"], 61)
        self.assertEqual(causal["recoverable_retry_checks"], 244)
        self.assertEqual(causal["tested_target_cardinalities"], [2, 3, 5, 10])

    def test_single_query_and_retry_are_not_interchangeable(self):
        args = ((0, 0, 1, 1), (0, 1, 0, 1), (5, 25), True, 0)
        self.assertTrue(timed_preservation.direct(15, *args))
        self.assertFalse(timed_preservation.direct(Fraction(31, 2), *args))
        self.assertFalse(timed_preservation.direct(30, *args))
        self.assertTrue(causal_recovery.constant_retention_with_retry(30, 5))
        self.assertFalse(causal_recovery.constant_retention_with_retry(Fraction(61, 2), 5))
        self.assertIsNone(timed_preservation.advance(0, ("query", 1), 0, args[0], args[1], args[2], True))

    def test_streaming_replaces_locator_with_target(self):
        self.assertTrue(causal_recovery.streaming_direct(35))
        self.assertFalse(causal_recovery.streaming_direct(Fraction(71, 2)))
        self.assertFalse(causal_recovery.single_source_controller(False))
        self.assertTrue(causal_recovery.single_source_controller(True))

    def test_compatible_local_actions_not_shared_tuple(self):
        r = self.result("compatible_execution")
        self.assertEqual(r["exhaustive_relation_feature_cases"], 54000)
        self.assertEqual([r["example_compatible_min_cost"], r["example_shared_tuple_min_cost"]], [2, 4])
        self.assertTrue(r["excess_activation_allowed_constant_success"])

    def test_original_unequal_endpoint_families(self):
        self.assertEqual(self.result("endpoint_search")["models"], 232)
        self.assertEqual(self.result("endpoint_search")["arbitrary_encoding_partitions_checked"], 241212)
        self.assertEqual(self.result("endpoint_partition")["comparisons"], 39)

    def test_unequal_endpoint_example_and_boundary_domain(self):
        r = self.result("heterogeneous_boundaries")
        self.assertEqual(r["cases"], 48)
        self.assertEqual(r["mismatches"], [])
        self.assertEqual([row["policy_categories"] for row in r["example"]], [5, 3, 2, 1])
        self.assertEqual(packing_number((1, 1, 2, 2), 2), 3)
        self.assertEqual(packing_number((1, 1, 2, 2), Fraction(3, 2)), inf)
        self.assertEqual(policy_frontier((1, 1, 2, 2), 5, 17)[0], 5)
        self.assertEqual(policy_frontier((1, 1, 2, 2), 5, Fraction(35, 2))[0], inf)

    def test_equal_duration_specialization(self):
        for budget in range(9):
            slots = budget // 2
            expected = min(3, ceil(4 / slots)) if slots else 3
            self.assertEqual(policy_frontier((2, 2, 2, 2), 3, 17 - budget)[0], expected)

    def test_marginal_support_domains(self):
        r = self.result("marginal_support")
        self.assertEqual([row["cases"] for row in r["rows"]], [47988, 11772])
        self.assertEqual(r["cases"], 59760)
        self.assertEqual(self.result("marginal_construction")["constructed_profiles_checked"], 16809)
        self.assertEqual(self.result("marginal_construction")["mismatches"], [])

    def test_constructed_rules_and_unused_symbol_completion(self):
        supports = ((frozenset((0,)), frozenset((0,))), (frozenset((1,)), frozenset((1,))))
        accepted = ({0}, {1})
        r = certificate(supports, accepted)
        for rule in r["rules"]:
            rule[2] = 0
        self.assertTrue(succeeds(r["rules"], supports, accepted))

    def test_component_contraction_rejects_one_participant(self):
        supports = ((frozenset((0, 1)),), (frozenset((0,)),), (frozenset((1,)),))
        accepted = ({0, 1}, {0}, {1})
        self.assertTrue(marginal_support.direct(supports, accepted))
        with self.assertRaises(ValueError):
            certificate(supports, accepted)

    def test_support_validation_and_empty_acceptable_set(self):
        with self.assertRaises(ValueError):
            certificate(((frozenset(), frozenset((0,))),), ({0},))
        r = certificate(((frozenset((0,)), frozenset((0,))),), (set(),))
        self.assertFalse(r["feasible"])

    def test_nonuniform_couplings_have_prescribed_marginals(self):
        for p, q in product((Fraction(0), Fraction(1, 3), Fraction(1, 2), Fraction(1)), repeat=2):
            for law in binary_couplings(p, q):
                self.assertEqual(sum(law.values()), 1)
                self.assertTrue(all(mass >= 0 for mass in law.values()))
                self.assertEqual(law[0, 0] + law[0, 1], p)
                self.assertEqual(law[0, 0] + law[1, 0], q)
            union = {r for law in binary_couplings(p, q) for r, mass in law.items() if mass > 0}
            rectangle = {(a, b) for a, pa in ((0, p), (1, 1 - p))
                         for b, pb in ((0, q), (1, 1 - q)) if pa * pb > 0}
            self.assertEqual(union, rectangle)
        self.assertEqual(self.result("marginal_couplings")["cases"], 4096)
        self.assertEqual(self.result("marginal_couplings")["rule_profiles_evaluated"], 65536)

    def test_feature_ownership_preserves_other_actors_edge(self):
        r = self.result("marginal_features")
        self.assertEqual(r["cases"], 5184)
        self.assertEqual(r["mismatches"], [])
        self.assertEqual([row["surviving_edges"] for row in r["example"]], [[0, 1], [1], [0], []])
        self.assertEqual([row["feasible"] for row in r["example"]], [False, False, False, True])

    def test_specific_dependence_can_improve_on_robust_design(self):
        self.assertEqual(self.result("dependence_contrast"),
                         {"aligned": True, "crossed": False, "all_couplings": False})

    def test_research_records_pass_and_count_executed_results(self):
        records = research_records(self.summary)
        self.assertEqual(len(records), len(self.summary))
        self.assertTrue(all(r["passed"] for r in records))

    def test_failed_original_comparison_is_a_reported_failure(self):
        with patch("oder_supplement.research_checks.endpoint_search.verify", return_value=(0, 1)):
            from oder_supplement.research_checks.endpoint_search import check
            failure = checked(check)
        self.assertIsNotNone(failure["error"])
        self.assertIn("costs", failure["error"]["inputs"])
        faulty = dict(self.summary, endpoint_search=failure)
        with tempfile.TemporaryDirectory() as directory:
            output, diagnostic = Path(directory) / "report.json", Path(directory) / "diagnostic.json"
            args = ["run_verification.py", "--out", str(output), "--diagnostic-out", str(diagnostic)]
            with patch("oder_supplement.examples.research_summary", return_value=faulty), patch("sys.argv", args):
                with self.assertRaises(SystemExit) as error:
                    run_verification.main()
            self.assertEqual(error.exception.code, 1)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(report["verification"]["failure_count"], 1)
            failed = json.loads(diagnostic.read_text())["failures"][0]
            self.assertEqual(failed["case"], "research endpoint_search")
            self.assertIn("costs", failed["exception"]["inputs"])


if __name__ == "__main__":
    unittest.main()
