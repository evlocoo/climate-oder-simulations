import copy
import json
import tempfile
import unittest
from fractions import Fraction
from math import inf
from pathlib import Path
from unittest.mock import patch

from oder_supplement.bounded import bounded_records, bounded_summary, mechanism_comparison
import run_verification


class BoundedChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results = bounded_summary()

    def test_channel_pair_domain(self):
        r = self.results["mechanisms"]
        self.assertEqual(r["cases"], 2176)
        self.assertEqual(r["rule_profile_evaluations"], 34816)
        self.assertEqual(r["mismatches"], [])

    def test_common_rule_examples_and_stochastic_support(self):
        examples = self.results["mechanisms"]["examples"]
        self.assertEqual(examples["separately_feasible_only"]["separate_feasibility"], [True, True])
        self.assertFalse(examples["separately_feasible_only"]["direct_feasible"])
        self.assertTrue(examples["common_rule_exists"]["direct_feasible"])
        correct = {0: {(0, 0): 1, (1, 1): 0}, 1: {(1, 1): 1}}
        r = mechanism_comparison((correct,), {0: {"a"}, 1: {"b"}})
        self.assertTrue(r["union_feasible"] and r["direct_feasible"])
        mixed = {0: {(0, 0): Fraction(1, 2), (1, 0): Fraction(1, 2)},
                 1: {(0, 1): Fraction(1, 2), (1, 1): Fraction(1, 2)}}
        r = mechanism_comparison((correct, mixed), {0: {"a"}, 1: {"a"}})
        self.assertTrue(r["union_feasible"] and r["direct_feasible"])

    def test_mechanism_domain_validation(self):
        with self.assertRaises(ValueError):
            mechanism_comparison((), {0: {"a"}})
        with self.assertRaises(ValueError):
            mechanism_comparison(({0: {(0,): 1}},), {0: {"a"}})
        with self.assertRaises(ValueError):
            mechanism_comparison(({1: {(0, 0): 1}},), {0: {"a"}})

    def test_restriction_comparisons(self):
        r = self.results["restriction"]
        self.assertEqual(len(r["cases"]), 18)
        self.assertEqual(r["restricted_selection_comparisons"], 123)
        self.assertEqual(sum(len(c["costs"]) for c in r["cases"]), 144)
        self.assertEqual(sum(len(c["deadlines"]) for c in r["cases"]), 108)
        records = bounded_records(self.results)
        self.assertEqual(len(records), 10)
        self.assertTrue(all(r["passed"] for r in records))

    def test_restriction_equality_and_strict_improvement(self):
        cases = self.results["restriction"]["cases"]
        full = next(c for c in cases if c["restricted"] == ((1, 0), (1, 1), (2, 0), (2, 1)))
        regime2 = next(c for c in cases if c["restricted"] == ((2, 0), (2, 1)))
        self.assertTrue(all(c["direct"][0] == c["direct"][1] for c in full["costs"]))
        self.assertEqual(regime2["costs"][1]["direct"], [1, 1])
        self.assertEqual(regime2["costs"][3]["direct"], [4, 2])
        self.assertEqual(regime2["deadlines"][2]["direct"], [540, 660])
        self.assertEqual(regime2["deadlines"][0]["direct"], [-inf, -inf])

    def test_empty_family_conventions(self):
        cases = {c["name"]: c for c in self.results["restriction"]["cases"]}
        baseline = cases["baseline sufficient equality"]
        impossible = cases["unrepairable on both sets"]
        removal = cases["remove the empty-action obstruction"]
        self.assertTrue(all(c["direct"] == [0, 0] for c in baseline["costs"]))
        self.assertTrue(all(c["direct"] == [inf, inf] for c in baseline["deadlines"]))
        self.assertTrue(all(c["direct"] == [inf, inf] for c in impossible["costs"]))
        self.assertTrue(all(c["direct"] == [-inf, -inf] for c in impossible["deadlines"]))
        self.assertTrue(all(c["direct"] == [inf, 0] for c in removal["costs"]))
        self.assertTrue(all(c["direct"] == [-inf, inf] for c in removal["deadlines"]))

    def test_worksheet_choices(self):
        r = self.results["early_information"]
        early, later = r["costs"][1], r["costs"][3]
        self.assertEqual(early["regime_optima"], [(("g",), ("g",))])
        self.assertEqual(later["fixed_optima"], [(("f", "h"), ("f", "h"))])
        self.assertEqual(later["regime_optima"], [(("f",), ("h",))])
        self.assertEqual(r["policy_cutoffs"], [600, 600, 660])

    def test_acquisition_knowledge_and_boundaries(self):
        r = self.results["early_information"]
        self.assertEqual(len(r["policies"]), 64)
        self.assertEqual(sum(p["fixed"] for p in r["policies"]), 8)
        self.assertTrue(all(len(p["bundles"]) == 2 for p in r["policies"]))
        self.assertEqual([row["policy_costs"] for row in r["costs"]],
                         [[1, 1], [1, 1], [4, 2], [4, 2], [inf, inf], [inf, inf], [inf, inf], [inf, inf]])
        self.assertEqual(r["regime_2_costs"], [1, 1, 2, 2, 2, 2, inf, inf])

    def test_new_failure_writes_report_before_exit(self):
        faulty = copy.deepcopy(self.results)
        faulty["mechanisms"]["mismatches"].append({"injected": True})
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            report, diagnostic = root / "report.json", root / "diagnostic.json"
            args = ["run_verification.py", "--out", str(report),
                    "--diagnostic-out", str(diagnostic)]
            with patch("oder_supplement.examples.bounded_summary", return_value=faulty), patch("sys.argv", args):
                with self.assertRaises(SystemExit) as error:
                    run_verification.main()
            self.assertEqual(error.exception.code, 1)
            result = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(result["verification"]["record_count"], len(result["verification"]["records"]))
            self.assertEqual(result["verification"]["failure_count"], 1)
            self.assertEqual(json.loads(diagnostic.read_text())["failures"][0]["case"], "common rules across channel pairs")


if __name__ == "__main__":
    unittest.main()
