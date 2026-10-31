import copy
import json
import tempfile
import unittest
from fractions import Fraction
from math import inf
from pathlib import Path
from unittest.mock import patch

import run_verification
from oder_supplement.locator import direct_policy as locator_policy, locator_summary, replay
from oder_supplement.monotone import (
    completion, completion_valid, conflicts_covered, direct_permitted_rules,
    monotone_summary, rule_tables, warning_example,
)
from oder_supplement.temporal import (
    coded_reply_model, direct_policy, preparation_example, successful_paths,
    temporal_summary, two_stage_model, witness_cover,
)


class TemporalChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results = temporal_summary()

    def test_exhaustive_trajectory_domains(self):
        for name, expected in (("two_source", 32768), ("single_source", 256), ("overwrite", 488)):
            self.assertEqual(self.results[name]["cases"], expected)
            self.assertEqual(self.results[name]["mismatches"], [])

    def test_repeated_occurrence_is_not_an_extra_observation(self):
        model = two_stage_model((0,), (0, 0), ((0,),), ((1,),), (1,))
        self.assertEqual(len(successful_paths(model, 0)), 1)
        self.assertFalse(witness_cover(model, (0,)))
        self.assertFalse(direct_policy(model, (0,)))
        observed_stage = two_stage_model((0,), (0, 1), ((0,),), ((1,),), (1,))
        self.assertTrue(direct_policy(observed_stage, ()))

    def test_causal_preparation_flag_repairs_same_source(self):
        self.assertEqual([r["direct"] for r in preparation_example()], [False, False, True, True])

    def test_overwrite_is_not_perfect_recall(self):
        model = coded_reply_model(660)
        self.assertFalse(direct_policy(model, (0,)))
        self.assertTrue(direct_policy(model, (1,)))
        self.assertFalse(direct_policy(model, (2,)))
        self.assertTrue(direct_policy(model, (0, 2)))

    def test_two_read_deadline_is_inclusive(self):
        self.assertTrue(direct_policy(coded_reply_model(680), (1,)))
        self.assertFalse(direct_policy(coded_reply_model(Fraction(1361, 2)), (1,)))


class MonotoneChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results = monotone_summary()

    def test_exhaustive_mixed_families(self):
        for name, count in (("distinct_sources", 16384), ("repeated_source", 4096)):
            self.assertEqual(self.results[name]["cases"], count)
            self.assertEqual(self.results[name]["mismatches"], [])
            self.assertGreater(self.results[name]["upward_completions_checked"], 0)

    def test_all_boolean_rule_tables_and_monotone_subfamily(self):
        self.assertEqual([len(rule_tables(k, False)[1]) for k in range(3)], [2, 4, 16])
        self.assertEqual([len(rule_tables(k, True)[1]) for k in range(3)], [2, 3, 6])

    def test_fixed_polarity_cost_warning(self):
        example = warning_example()
        self.assertEqual([example["unrestricted_minimum"], example["monotone_minimum"]], [1, 2])
        self.assertTrue(example["rows"][1]["ordinary_coverage"])
        self.assertFalse(example["rows"][1]["directional_coverage"])

    def test_ordinary_lookup_may_invert_but_response_may_not(self):
        occurrences, features = ((0, 0, 1), (1, 0, 0)), ((0, 1),)
        self.assertTrue(direct_permitted_rules(occurrences, features, (0,), {1})[0])
        self.assertFalse(direct_permitted_rules(occurrences, features, (0,), {0})[0])

    def test_response_and_ordinary_states_have_no_coupling(self):
        occurrences = ((0, 0, 1), (1, 0, 0), (0, 1, 0), (1, 1, 1))
        self.assertTrue(direct_permitted_rules(occurrences, ((0, 1),), (0,), {1})[0])

    def test_upward_closure_off_path_and_empty_positive_set(self):
        features = ((1, 0), (0, 0))
        occurrences = ((0, 1, 1), (1, 1, 0))
        rules = completion(occurrences, features, (0, 1), {1})
        self.assertEqual(rules[1][(1, 1)], 1)
        self.assertEqual(rules[1][(0, 1)], 0)
        self.assertTrue(completion_valid(rules, occurrences, features, (0, 1), {1}))
        zero = completion(((0, 1, 0),), features, (0, 1), {1})
        self.assertEqual(set(zero[1].values()), {0})

    def test_repeated_source_opposite_response_is_impossible(self):
        occurrences = ((0, 1, 0), (0, 1, 1))
        self.assertFalse(conflicts_covered(occurrences, ((1,),), (0,), {1}))
        self.assertFalse(direct_permitted_rules(occurrences, ((1,),), (0,), {1})[0])


class LocatorChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results = locator_summary()

    def test_all_partitions_and_four_regimes(self):
        family = self.results["partitions"]
        self.assertEqual(family["cases"], 33)
        self.assertEqual(family["partition_time_cases"], 11 * (15 + 203 + 4140))
        self.assertEqual(family["mismatches"], [])
        rows = {(r["targets"], r["start"]): r for r in family["rows"]}
        for m in (2, 3, 4):
            self.assertEqual([rows[m, t]["recovery_categories"] for t in (30, 35, 40, 60)], [1, 2, m, inf])
            self.assertEqual(rows[m, Fraction(61, 2)]["ratio"], Fraction(m, 2))
            self.assertEqual(rows[m, Fraction(71, 2)]["recovery_categories"], m)
            self.assertEqual(rows[m, Fraction(81, 2)]["recovery_categories"], inf)

    def test_legal_retry_and_inclusive_boundary(self):
        worlds = ((0, 1), (0, 2), (1, 1), (1, 2))
        ok, _, policy = locator_policy(worlds, 30, 2)
        self.assertTrue(ok)
        self.assertTrue(replay(worlds, 30, policy))
        self.assertFalse(locator_policy(worlds, Fraction(61, 2), 2)[0])

    def test_reply_must_be_retained_and_not_a_source_oracle(self):
        worlds = ((0, 1), (0, 2), (0, 3))
        ok, _, policy = locator_policy(worlds, 35, 3)
        self.assertTrue(ok)
        self.assertEqual({key[3] for key in policy if key[1] == 1}, {1, 2, 3})
        self.assertTrue(all(len(key) == 4 for key in policy))
        self.assertFalse(locator_policy(worlds, 35, 3, recovery=False)[0])

    def test_integer_retry_sweep(self):
        self.assertEqual(self.results["retry"]["cases"], 244)
        self.assertEqual(self.results["retry"]["encoding_comparisons"], 732)
        self.assertEqual(self.results["retry"]["mismatches"], [])


class IntegratedFailureChecks(unittest.TestCase):
    def test_new_disagreement_writes_diagnostics_and_exits(self):
        faulty = copy.deepcopy(monotone_summary())
        faulty["distinct_sources"]["mismatches"].append({"features": [[0, 1]], "covered": True, "direct": False})
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "report.json"
            diagnostic = Path(directory) / "diagnostic.json"
            args = ["run_verification.py", "--out", str(report), "--diagnostic-out", str(diagnostic)]
            with patch("oder_supplement.examples.monotone_summary", return_value=faulty), patch("sys.argv", args):
                with self.assertRaises(SystemExit) as error:
                    run_verification.main()
            self.assertEqual(error.exception.code, 1)
            result = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(result["verification"]["failure_count"], 1)
            self.assertEqual(result["verification"]["record_count"], len(result["verification"]["records"]))
            failure = json.loads(diagnostic.read_text())["failures"][0]
            self.assertEqual(failure["case"], "monotone mixed policy distinct_sources")
            self.assertIn("features", failure["details"]["mismatches"][0])


if __name__ == "__main__":
    unittest.main()
