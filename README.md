# Climate ODER Computational Supplement

This package accompanies the paper [*Climate ODER: Information, Coordination, and the Time to Act*](https://www.preprints.org/manuscript/202503.2255/v3). It follows information from a heat-response briefing through distributed coordination, temporal preservation, constrained responses, and deadline-limited recovery.

The computational supplement checks specified finite examples and bounded enumerations concerning coordination, information preservation, timing, and stochastic support. The manuscript provides the general mathematical arguments.

## Read the examples

Open the saved [notebook](supplement/Climate_ODER_Verification.ipynb) in a notebook viewer or its rendered repository preview. All results are already included; reading requires no kernel or Python installation. The [HTML reading copy](supplement/Climate_ODER_Verification.html) can be opened directly in a browser and shows the same narrative and outputs without code cells. Download the HTML file to read it if the repository displays its source.

| Notebook section | Question and computational scope |
| --- | --- |
| Heat briefing | Two records at six decision times, including inclusive deadlines and physical infeasibility; coarse-rule enumeration and minimum category comparisons. A separate 15-minute query regime distinguishes recovery from retained information. |
| Retention loss | Four stipulated error probabilities distinguish the 30-unit average-loss tolerance from guaranteed acceptable selection. A three-record example also shows why pairwise compatibility is insufficient. |
| Shelter coordination | All 16 binary local-rule pairs on three situations; the uniform optimum and three rational distributions, with and without individual-adequacy constraints. |
| Preservation design | All 19 feature subsets across six scenarios, including eight subsets of the three-feature budget example; actor-labelled witness constraints compared with direct local rules. Budgets 1, 2, 3, and 4 are evaluated in the toy example. |
| Contacts and storage | Five two-contact scenarios with integer-minute sends, waiting, nonzero durations, inclusive endpoints, an unavailable route, a reset, and protected storage. |
| Joint retention | Aligned/crossed channels and support sensitivity; 2,025 two-world support/action cases, each checked against 16 binary rule pairs, for 32,400 evaluations. Empty acceptable-action sets are checked separately. |
| Mixture optimum | All 66 source-prior triples on the tenths simplex and 11 epsilon values from 0 to 1: 726 cases and 11,616 rule-pair evaluations compare the unrestricted average optimum with `1 - min {p(L), p(R), p(M) epsilon}`. |
| One rule across mechanisms | Two sources, two participants, binary observations and plans; 136 unordered pairs with repetition of 16 deterministic channels and 16 acceptable-set pairs including empty sets. All 2,176 cases compare union components with 16 profiles checked against each original channel: 34,816 evaluations. Separate-feasibility and common-rule contrasts are also checked. |
| Situation restriction | All 15 nonempty worksheet restrictions and eight feature bundles, plus three no-feature pairs: 123 restricted-bundle comparisons. Independent local-rule enumeration checks component-based feasibility, 144 full/restricted cost comparisons, and 108 cutoff comparisons, including equality, strict improvement, sufficient baselines, and infeasibility. |
| Early regime information | All eight fixed bundles and 64 regime-dependent policies for the four worksheet situations. Component calculations and direct policy enumeration verify costs, optimal bundles, a common 10:00 cutoff, and a regime-2 cutoff of 11:00. |
| Temporal preservation | All-occurrence witness coverage versus executable retained-state policy search: 32,768 two-source and 256 single-source two-stage cases, plus 488 coded-reply/channel-selection cases. A preparation example distinguishes persistent features from a causal memory flag. |
| Monotone responses | 16,384 three-source and 4,096 repeated-source cases compare ordinary/directional coverage with all permitted Boolean tables. Upward-closure completions are checked on the full configured input cube. The clearance warning requires minimum cost 1 unrestricted and 2 monotone. |
| Initial locator frontier | All 15, 203, and 4,140 handoff partitions for two, three, and four targets at 11 exact times: 47,938 partition/time cases and 33 minimum-category comparisons. A 244-case integer-time sweep checks three specified encodings, for 732 encoding comparisons. |
| Distinct temporal research models | 9,216 source-specific single-query cases; 16,384 hidden-state step/stop cases; 61 causal-overwrite comparisons; and 244 legal-retry checks for target counts 2, 3, 5, and 10. These are distinct from the independently implemented families above. |
| Compatible execution | 54,000 acceptable-relation/feature-selection comparisons. A constructed example requires cost 2 for compatible local actions but 4 for identifying the same complete joint tuple. Allowing excess activation instead permits a constant profile across its four records. This is a contrast with shared-plan agreement, not an equivalence. |
| Unequal endpoint frontier | Ordered-policy covers and 241,212 candidate encodings across 232 models; full partition/recursive-policy comparisons at 39 budgets; and 48 half-unit boundary cases. The four-endpoint example reproduces 5, 3, 2, and 1 categories. |
| Marginal-support guarantee | 59,760 binary support/action configurations across two or three participants. Component construction supplies 16,809 successful profiles on that same domain. Additional comparisons cover 4,096 rational-coupling cases and 5,184 participant-owned feature selections. |

Restriction and early-information checks use exact rational-minute times 08:00, 09:00, 09:00:30, 10:00, 10:00:30, 11:00, 11:00:30, and noon. Restriction cutoffs use budgets 0, 1, 2, 3, 4, and 5. Only the included situations change in each restriction comparison; catalogs, ownership, costs, windows, retained information, storage, decision schedule, and executable-rule class stay fixed. Infeasible cost is positive infinity, an empty affordable successful family has cutoff negative infinity, and an already sufficient baseline has cost zero and cutoff positive infinity. The latter means no acquisition is required, not permission to acquire after the decision.

Early regime knowledge belongs to the coordinator at acquisition time, distinct from transport's unchanged knowledge at noon. Acquisition policies may depend on regime but not the hidden target. Cost is the maximum expenditure across regimes, without an assumed prior. Savings exclude the cost and time of obtaining regime information.

Temporal controllers see only their declared baseline and selected retained channels. The two-stage family enumerates all binary observation maps, initial and terminal action subsets including empty sets, binary persistent features, and feature selections. A decision bound is not an observed clock. Coded replies use all four `(u,v)` sources, eight selections from overwrite, decode, and persistent-code channels, and all integer-minute starts from 11:00 through noon. Channel updates use only their own current value, the new observation, and declared baseline state.

The monotone family checks partial-lookup extension for three occurrences, two baseline states, two Boolean features, all baseline and response assignments, and four feature selections; not every assignment is a physically successful trajectory. Ordinary states allow unrestricted lookup; designated response states require nondecreasing Boolean tables. Both responses remain legal throughout the full selected Boolean cube. Input polarity is fixed, so inversion requires an approved complementary input.

The locator model permits legal retries. Its deadline is minute 60; targeted action, endpoint query, universal query, and common protection take 20, 5, 25, and 50 minutes. Partition checks use starts 0, 29.5, 30, 30.5, 34.5, 35, 35.5, 39.5, 40, 40.5, and 60. The additional encoding sweep uses target counts 2 through 5 and integer starts 0 through 60. Policy keys contain the handoff category, clock, query stage, failed endpoint, and retained reply, never the analyst's hidden source or complete history.

The single-query model allows a fast query only at its source-specific endpoint and has no retry. Its constant-handoff deadline is minute 15; the legal-retry construction instead permits constant-handoff success through minute 30. The occurrence family observes no clock or history and detects 880 false positives if same-source conflicts are omitted. Its 16,384 cases are not the monotone family's 16,384 cases. The two 244-case retry sweeps also have different target-count domains, specified in the notebook and JSON report.

For unequal endpoint durations, the source is the complete endpoint/target product. Queries are serial, positive-duration, and legal at every endpoint; failure carries no target information. Only targeted protection is available. The formula compares target categories with the minimum packing of endpoint durations into the remaining query time. The notebook specifies all tested duration vectors, integer and half-unit budgets, encoding domains, and explicit clock, schedule, and reply registers.

The marginal-support certificate requires at least two participants, all conditional couplings of the known marginals, and one fixed executable profile. It does not assume actual independence. Exhaustive binary families use every nonempty support and every acceptable-set subset, including empty sets. Rational-law comparisons use symbol-zero probabilities 0, 1/3, 1/2, and 1, with Frechet endpoints, midpoint and product couplings. Participant-owned refinement checks retain each other participant's overlap edges. The single-participant counterexample and the aligned/crossed dependence contrast are checked separately.

## File inventory

Paths below are relative to `supplement/`.

| File or directory | Purpose |
| --- | --- |
| `Climate_ODER_Verification.ipynb` | Executed notebook with narrative, code, and saved tables. |
| `Climate_ODER_Verification.html` | Reading copy exported from the executed notebook. |
| `build_notebook.py` | Generates the notebook with narrative, code, and empty outputs. |
| `execute_notebook.py` | Runs the notebook in a fresh Jupyter kernel using the selected Python executable. |
| `render_notebook.py` | Exports saved notebook results to HTML without rerunning calculations. |
| `run_verification.py` | Runs the scientific comparisons and writes the machine-readable report. |
| `oder_supplement/finite.py` | Single-actor representations, action sets, lookup rules, categories, and expected loss. |
| `oder_supplement/coordination.py` | Shared plans, witness constraints, feature subsets, and acquisition deadlines. |
| `oder_supplement/timing.py` | Recovery deadlines, message timing, backward recurrence, and direct schedule enumeration. |
| `oder_supplement/stochastic.py` | Joint channels, support graphs, direct rules, and the bounded stochastic family. |
| `oder_supplement/bounded.py` | Common rules across mechanisms, situation restrictions, and early-regime acquisition policies, with independent exhaustive comparators. |
| `oder_supplement/temporal.py` | Successful trajectory witnesses, all-occurrence conflicts, direct retained-state policies, and causal channel examples. |
| `oder_supplement/monotone.py` | Mixed unrestricted/monotone rules, directional coverage, upward-closure completion, and the fixed-polarity warning example. |
| `oder_supplement/locator.py` | All initial partitions for small target counts, executable-policy search, four deadline regimes, and legal retries. |
| `oder_supplement/research_checks/` | Single-query, occurrence, causal-retry, compatible-execution, unequal-endpoint, and marginal-support calculations, implemented separately from the comparison modules. |
| `oder_supplement/heterogeneous.py` | Direct schedule/reply simulation and exact policy-success covers versus endpoint packing, including half-unit boundaries and the four-endpoint example. |
| `oder_supplement/marginal.py` | Constructed component profiles, rational conditional couplings, and participant-owned refinements. |
| `oder_supplement/research.py` | Explicit research-family domains, structured results, and captured comparison failures with local input diagnostics. |
| `oder_supplement/examples.py`, `reporting.py`, `__init__.py` | Example orchestration, computed verification records, and package version. |
| `tests/` | 54 tests across verification, bounded, temporal, and research modules, including injected disagreements that verify report and diagnostic output before a nonzero exit. |
| `reports/verification_summary.json` | Supplement version, computed results, domain sizes, comparison records, and failures. |
| `reports/source_to_computation_map.csv` | Manuscript labels, assumptions, implementations, and notebook references. |
| `requirements-notebook.txt` | Pinned direct dependencies for notebook execution. |
| `requirements-render.txt` | Additional dependency for regenerating the HTML reading copy. |
| `requirements-tested.txt` | Tested interpreter and package versions; an environment record, not a pip input. |

## Dependencies

Use Python 3.12. Core calculations, tests, report generation, and notebook generation require only the standard library. Notebook execution requires `nbclient`, `nbformat`, `ipykernel`, and their dependencies, including IPython for table display. HTML export additionally requires `nbconvert`.

From the directory containing this README, install the dependencies for notebook execution and HTML export:

```text
cd supplement
python -m pip install --target .jupyter_deps -r requirements-render.txt
```

The helper scripts use `.jupyter_deps/` and create a kernelspec in `.jupyter_data/` for the Python interpreter used to launch them. For execution without HTML export, use `requirements-notebook.txt` instead. The earlier logistic simulations have their own dependencies and execution instructions.

## Reproduce the results

Run these commands from `supplement/`, with the notebook dependencies installed:

```text
python -m unittest discover -s tests
python run_verification.py
python build_notebook.py
python execute_notebook.py
python render_notebook.py
```

The complete workflow was tested with Python 3.12.14 in PowerShell on Windows. macOS and Linux have not been verified. Use your chosen Python executable in place of `python` if it is not on `PATH`.

The executor starts a fresh kernel for `Climate_ODER_Verification.ipynb`. In an independently installed interactive Jupyter environment, use `supplement/` as the working directory and choose **Restart Kernel and Run All Cells**.

`build_notebook.py` replaces saved outputs with an unexecuted notebook. Always execute it afterward before distributing the result. HTML export reads the saved outputs and does not execute the notebook.

## Expected outputs

The test command reports **54 tests, OK**. The verifier writes `reports/verification_summary.json` and reports **zero verification failures**. Successful notebook execution reports **27 executed code cells and zero error outputs**. It also writes the JSON summary. HTML export writes `Climate_ODER_Verification.html`, with 45 tables matching the saved notebook outputs.

The summary contains **68 computed verification records**. Each record identifies its finite domain, actual and independent results, and any disagreement. Records group comparisons of different sizes; they are not 68 equally sized mathematical instances. The 32,400, 11,616, and 34,816 rule-profile evaluations belong to the support, mixture, and mechanism families. The monotone families evaluate 179,200 local rule tables and check 12,060 completions. The two-endpoint locator partition checks use 7,326 category-block policy searches and 64,384 reachable lookup assignments. Unequal-duration boundary checks evaluate 5,788 schedule/fallback policies; rational marginal-law checks evaluate 65,536 fixed profiles. Cases, partitions, local tables and profile evaluations are different units and should not be added into one total. Other example tables are explanatory outputs and are not all separate report records.

An expected impossibility is not a verification failure. No acceptable common plan, no feasible feature selection, and loss of a route after a memory reset are intended outcomes in their respective examples. The reset-without-storage comparison explicitly expects the free-memory recurrence and erased-memory enumeration to differ. Unexpected disagreement is a failure; the command-line verifier writes `reports/verification_diagnostics.json` and exits nonzero. The isolated mismatch test verifies that reporting detects a deliberately introduced disagreement without adding it to the scientific report.

## Limits of the checks

The general mathematical claims rest on the manuscript's arguments. Enumeration covers the specified small domains, not arbitrary numbers of actors, plans, or features. The stochastic family assigns uniform rational mass within each selected support and is exhaustive over those supports and acceptable-plan sets, not over all distributions. The five contact scenarios enumerate integer-minute starts, not all continuous schedules or arbitrary graphs. Their reset ordering is a stated convention, not a measured property of a communication system.

The preservation calculations use hypothetical additive costs, common-time instantaneous acquisition, and retention through a fixed later decision. The worksheet compares a fixed advance bundle with choices conditioned on explicitly available early regime information. Costs represent the declared institutional preservation budget and omit broader implementation burdens. Required costs and acquisition cutoffs are checked on the listed finite domains, not arbitrary catalogs or all real acquisition times. The general frontier and restriction results remain established by the manuscript's proofs. The mechanism family enumeration is limited to deterministic binary channels; additional tests exercise a stochastic example and zero-probability outcomes, not all stochastic mechanisms.

No calculation validates observed emergency-response behavior, estimates real institutional losses, or measures climate impacts. High average success is not a probability-one guarantee. Separate participant marginals can omit dependence needed to assess coordination, and finite nonoccurrence cannot certify that a rare outcome has zero probability without further assumptions.

Temporal comparisons cover their declared operation and memory models, not arbitrary operation systems. The mixed-rule checks assume both response choices legal at every configured input and impose no coupling between rules at different baseline states. They do not resolve arbitrary authorization or interpretation constraints. Single-query and legal-retry conclusions are not interchangeable. The two-endpoint exhaustive category minima cover target counts 2, 3, and 4; the unequal-endpoint families have their own stated domains. Category counts and the middle-interval ratio `m/2` concern initial handoff distinctions: the reply still supplies the target and requires capacity for its possible values. They do not establish reduced total information or peak memory.

The source-component marginal shortcut is invalid in general for one participant. Justified dependence restrictions can also exclude the product witness, making the all-couplings certificate conservative rather than exact for that smaller family. The rational coupling samples do not enumerate every real-valued law. General results remain established by the manuscript's proofs, under its declared assumptions.

## Earlier retrieval simulations

Earlier releases contain logistic retrieval simulations and event-based illustrations developed for the previous formulation of Climate ODER. They remain available as earlier work and are separate from the current theory supplement.

The [historical v1.0.1 release](https://github.com/evlocoo/climate-oder-simulations/releases/tag/v1.0.1) preserves that implementation. Its [versioned README](https://github.com/evlocoo/climate-oder-simulations/blob/v1.0.1/README.md) supplies the earlier execution instructions and dependencies. The historical event illustrations do not validate the current theory.

## Citation and license

- **Paper:** Cooper III, Evlondo (2026). *Climate ODER: Information, Coordination, and the Time to Act*. Preprints.org, version 3, posted November 4, 2026. [doi:10.20944/preprints202503.2255.v3](https://doi.org/10.20944/preprints202503.2255.v3).
- **Supplement:** Cooper III, Evlondo (2026). *Climate ODER Computational Supplement* (Version 2.0.0). GitHub. [Release and reproduction materials](https://github.com/evlocoo/climate-oder-simulations/releases/tag/v2.0.0).
- **Historical simulations:** Cooper, Evlondo (2025). *Climate ODER Retrieval Simulation: Benchmarking Forecast Recognition Across Institutional Observers*, v1.0.1. Zenodo. [doi:10.5281/zenodo.15824444](https://doi.org/10.5281/zenodo.15824444). This DOI identifies the earlier simulation package only.

The supplement's software and associated documentation are covered by the included [MIT license](LICENSE).
