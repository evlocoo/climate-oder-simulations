"""Build the narrative notebook; scientific calculations live in oder_supplement."""

from __future__ import annotations

import json
from pathlib import Path


def md(source):
    return {"cell_type": "markdown", "metadata": {}, "source": source.strip().splitlines(keepends=True)}


def code(source):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": source.strip().splitlines(keepends=True)}


cells = [
    md("""# Climate ODER Computational Supplement

What should a response team preserve now so that it can still choose an acceptable protective action later? A briefing may be sufficient while there is time to protect every potentially exposed facility. Once only targeted preparation remains possible, the team needs to know which facility faces earlier exposure. If a handoff has already discarded that association and timely recovery has ended, the team can lose the ability to select a successful plan before it loses the physical ability to carry one out.

This notebook develops that question from a single heat-response team to transport and receiving teams that must coordinate. It then examines which information to preserve, the time available to acquire or transmit it, and what changes when retention is unreliable. Each example specifies the protective objective and the information available to the people choosing the plan.

The computational supplement checks specified finite examples and bounded enumerations concerning coordination, information preservation, timing, and stochastic support. The manuscript provides the general mathematical arguments. These are constructed examples, not measurements of emergency-response performance.

Read the saved outputs from top to bottom without running any code. To reproduce them, follow [the reproduction guide](../README.md) and execute the notebook from the supplement directory in a fresh kernel. The narrative defines each calculation before its output; the concluding reference table connects examples to manuscript labels."""),
    code("""from pathlib import Path
from html import escape
from math import inf
import csv
import json

from IPython.display import HTML, display
from oder_supplement.examples import (
    run_preservation_examples, run_shelter_examples, run_single_actor_examples,
    run_stochastic_coordination_examples, run_timing_examples, verification_summary,
)
from oder_supplement.coordination import budget_preservation_example
from oder_supplement.bounded import bounded_summary
from oder_supplement.finite import hhmm, minutes
from oder_supplement.reporting import assert_no_failures

def table(headers, rows):
    head = "".join(f"<th scope='col'>{escape(str(h))}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{escape(str(v))}</td>" for v in row) + "</tr>" for row in rows)
    display(HTML("<div style='overflow-x:auto'><table><thead><tr>" + head +
                 "</tr></thead><tbody>" + body + "</tbody></table></div>"))

def yes_no(value):
    return "Yes" if value else "No"

def guaranteed(value):
    return "Guaranteed" if value else "No guarantee"

def cost_label(value):
    return "No feasible selection" if value is None else str(value)

def category_label(value):
    return "No physically feasible plan" if value == inf else str(value)

def deadline_label(value):
    if value == inf:
        return "No acquisition required"
    if value == -inf:
        return "No feasible acquisition time"
    return hhmm(value)

print("Saved tables below report the declared finite checks.")"""),
    md("""## 1. A heat briefing whose adequacy changes with time

A preparation team must have the **earlier-exposed facility ready by noon**. Record `A` identifies facility A as earlier exposed; record `B` identifies facility B. Plan `c` prepares both facilities in 90 minutes. Plans `a_A` and `a_B` each take 30 minutes and prepare their named facility. The targeted plan is acceptable only when it prepares the earlier-exposed facility. These durations and the service objective are stipulated; the task does not require both facilities to be ready by noon.

Before 10:00 the team has obtained the pairing between facility and exposure time. At the **10:00 handoff**, the full briefing retains it. The coarse briefing overwrites its sole local copy, leaving the facilities and times but losing their pairing. The detailed external source also closes at 10:00 in this baseline. Closing the source does not erase information that the team retained locally.

Through **10:30 inclusive**, the coarse briefing remains sufficient: preparing both facilities can still finish by noon. After 10:30, the common plan has expired and the team needs the pairing to select the correct targeted plan. Targeted preparation remains feasible through **11:30 inclusive**. After that time, even complete information cannot make a 30-minute action finish by noon.

A retained category groups source records that the team cannot distinguish. A briefing supports the task if each category has at least one acceptable action common to every record in it. The table compares that criterion with direct enumeration of lookup rules for the coarse briefing. The minimum category count asks how many distinct briefing states are necessary; it is not a measured human memory requirement."""),
    code("""single = run_single_actor_examples()
table(["Plan start", "Full briefing sufficient?", "Coarse briefing sufficient?", "Minimum categories", "Successful coarse rules"],
      [[r["time"], yes_no(r["full"]["sufficient"]), yes_no(r["coarse"]["sufficient"]),
        category_label(r["cover"]), r["rule_count_check"]] for r in single["heat_rows"]])
table(["11:00 category calculation", "Minimum categories"], [
    ["Cover records with acceptable actions", single["minimum_cover_11_00"][0]],
    ["Enumerate all partitions of the records", single["minimum_partitions_11_00"][0]],
])"""),
    md("""One briefing category is enough at 10:00 because the common plan works for either record. At 11:00, two categories are necessary, and the two independent category calculations agree. At 11:31 the obstacle is physical feasibility: no representation can supply an acceptable plan when the action sets are empty. The table therefore separates a lost distinction from an expired action opportunity.

### An alternative recovery route

Now consider a separate access regime in which a query can recover the pairing in 15 minutes. The team must complete that query before starting the 30-minute targeted plan. Its last query start is therefore **11:15 inclusive**, since 11:15 + 15 + 30 minutes is noon. This query is an alternative to the baseline closed-source arrangement, not an additional route implicitly available after the baseline handoff. In the next table, direct targeted availability assumes the pairing is already retained; query completion assumes it must first be recovered."""),
    code("""timing = run_timing_examples()
table(["Start", "Common plan feasible?", "Direct targeted plan feasible?", "Query + targeted finish", "Query route timely?"],
      [[r["decision_point"], yes_no(r["common_plan_available"]), yes_no(r["targeted_plan_available"]),
        r["query_target_completion"], yes_no(r["query_route_timely"])] for r in timing["heat_timing_rows"]])
print("Last query start in the alternative regime:", timing["latest_recovery_start"])"""),
    md("""At 11:30 a team that already knows the target can still act, but a team that first needs the 15-minute query cannot. A recovery deadline therefore depends on the permitted route as well as the action duration. It need not coincide with either source closure or the last physically feasible action start.

### Why pairwise compatibility is insufficient

For a separate three-record example, suppose the acceptable sets are `{a,b}`, `{b,c}`, and `{a,c}`. Every pair of records shares an acceptable action. All three together share none. A summary merging all three records would force one choice for the whole group, so it cannot guarantee success. This is a deliberately unsuccessful representation; correctly detecting that impossibility is an expected result."""),
    code("""table(["Merged three-record briefing", "Expected interpretation"], [[
    guaranteed(single["pairwise_not_enough"]["sufficient"]),
    "Pairwise intersections do not supply an action common to all three records",
]])"""),
    md("""## 2. Acceptable average loss and guaranteed selection

Return to the heat team while targeted action is feasible. Stipulate a loss of **20** when the retained pairing is correct and **80** when it is reversed, with an acceptable average-loss tolerance of **30**. Let epsilon be the probability of reversal, symmetrically for either source record. These losses and error probabilities are hypothetical inputs, not estimates from an event.

The rule that follows the retained label has retention-averaged loss `20(1 - epsilon) + 80 epsilon = 20 + 60 epsilon`. It meets the average-loss tolerance through epsilon = 1/6. A guaranteed acceptable selection is a different requirement: every retained outcome of positive probability must support an acceptable choice for its source record. For each positive error rate evaluated below, either label can arise from either record, so the label cannot provide that guarantee."""),
    code("""table(["Reversal probability", "Average loss", "Within tolerance 30?", "Acceptable selection guaranteed?"],
      [[r["epsilon"], r["retention_averaged_loss"], yes_no(r["within_30_loss"]),
        yes_no(r["probability_one_guarantee"])] for r in single["stochastic_retention"]])"""),
    md("""The 1/10 and 1/6 rows meet the average-loss criterion even though guaranteed selection is unavailable. A small error probability can be compatible with an acceptable average, while still leaving a possible outcome on which the required distinction is lost. Which criterion is appropriate depends on the declared protective objective.

## 3. Transport and receiving must choose the same shelter plan

Transport and receiving must select the same acceptable plan, `a` or `b`, without further informative exchange. In situation 1 only `a` is acceptable, in situation 2 either plan is acceptable, and in situation 3 only `b` is acceptable. Transport cannot distinguish situations 1 and 2; receiving cannot distinguish situations 2 and 3.

Each participant has individually sufficient information. Transport can select `a` for its unresolved pair and `b` for situation 3. Receiving can select `a` for situation 1 and `b` for its unresolved pair. Those individually acceptable choices disagree in situation 2. Joint success requires agreement as well as acceptability.

The component criterion connects situations whenever at least one participant cannot distinguish them. A guaranteed shared choice must be constant along those connections. Here the chain connects situations 1 and 3, whose acceptable sets are disjoint. We compare that criterion with all 16 deterministic binary local-rule pairs. Under the uniform source distribution, average joint success gives equal weight to each of the three situations."""),
    code("""shelter = run_shelter_examples()
direct = shelter["direct_enumeration"]
table(["Calculation", "Result"], [
    ["Local-rule pairs examined", direct["rule_tuple_count"]],
    ["Pairs guaranteeing joint success", direct["guaranteed_rule_count"]],
    ["Component criterion", guaranteed(shelter["graph_criterion"]["succeeds"])],
    ["Best uniform average joint success", direct["best_score"]],
])
table(["Situation", "Transport plan", "Receiving plan", "Joint success?"], [
    [x, shelter["displayed_individually_adequate_rules"]["transport"][x],
     shelter["displayed_individually_adequate_rules"]["receiving"][x], yes_no(ok)]
    for x, ok in shelter["displayed_joint_success_by_situation"].items()
])"""),
    md("""The absence of a guaranteed pair agrees with the component obstruction. The best uniform average is 2/3; it does not make the missing guarantee disappear. Preserving the extra distinction for either transport or receiving breaks the chain. The following comparison makes that intervention explicit."""),
    code("""repair_names = {"transport_repair": "Transport distinguishes 1 from 2",
                "receiving_repair": "Receiving distinguishes 2 from 3"}
table(["Additional retained distinction", "Shared selection"],
      [[repair_names[name], guaranteed(result["succeeds"])] for name, result in shelter["repairs"].items()])"""),
    md("""### Unequal source probabilities

Let `p(1), p(2), p(3)` be the probabilities of the three source situations. Optimizing over **all** local rules gives average joint success `1 - min p(x)`: a rule pair can sacrifice the least likely situation. Requiring each participant's rule to be individually acceptable in every situation restricts the choices to the displayed adequate rules, giving `1 - p(2)` instead. These are different feasible rule families.

The table evaluates three rational distributions: balanced `(1/3, 1/3, 1/3)`, middle-heavy `(1/5, 3/5, 1/5)`, and right-light `(2/5, 2/5, 1/5)`. Fractions are exact. The computed optima are compared with the stated formulas."""),
    code("""distribution_names = {"balanced": "Balanced", "middle_heavy": "Middle-heavy", "right_light": "Right-light"}
table(["Distribution", "All-rule optimum", "1 - min p(x)", "Individually adequate optimum", "1 - p(2)"],
      [[distribution_names[name], r["all_local_rule_optimum"], r["formula_all_local"],
        r["individually_adequate_optimum"], r["formula_displayed_rules"]]
       for name, r in shelter["nonuniform"].items()])"""),
    md("""When the middle situation is most likely, the unrestricted optimum is 4/5 but the individually adequate optimum is 2/5. High average joint success can thus depend on allowing a participant to choose an individually unacceptable plan in some situations. The constraint must be stated before comparing coordination performance.

## 4. Choosing which information to preserve

An institution purchases information-preservation features for transport before the operational regime is known. Four situations are pairs `(e,b)`: regime `e` is 1 or 2, and required plan `b` is 0 or 1. Both teams must choose that same plan at noon. Receiving already retains `(e,b)`; transport retains only `e`. The code names the plans `plan_0` and `plan_1`.

The hypothetical catalog offers three features, all held by transport. Feature `g` retains `b` in both regimes. Feature `f` retains it in regime 1 and has constant value 0 in regime 2; `h` does the reverse. Transport also retains the regime, so it can interpret these conditional features.

Costs are units of the institution's declared preservation budget. They charge every selected feature, including a feature not used in the realized regime. The catalog does not price all training, interface development, staff time, transmission, or institutional implementation burdens. Acquisition is instantaneous at one common selected time, inclusive of each feature's cutoff, with no competition between acquisitions. Acquired features remain available through the noon decision. These assumptions make the calculation a small preservation design example, not an operational procurement estimate."""),
    code("""pres = run_preservation_examples()
budget = pres["budget_example"]
_, _, _, features = budget_preservation_example()
feature_meanings = {"g": "Required plan in both regimes", "f": "Required plan in regime 1; constant in regime 2",
                    "h": "Constant in regime 1; required plan in regime 2"}
table(["Feature", "Holder", "Retained content", "Cost units", "Acquire through"],
      [[f.name, f.actor.capitalize(), feature_meanings[f.name], f.cost, hhmm(f.deadline)] for f in features])
table(["Budget units", "Latest common acquisition time"],
      [[B, deadline_label(t)] for B, t in budget["budget_deadlines"].items()])
print("Minimum declared cost:", cost_label(budget["minimum"]["minimum_cost"]))
print("Latest acquisition with no budget bound:", deadline_label(budget["unlimited_deadline"]))"""),
    md("""`g` alone resolves the required plan in both regimes for one unit, provided it is acquired by 09:00. Without `g`, transport needs both `f` and `h`: one repairs the regime-1 ambiguity and the other repairs regime 2. Selecting both costs four units and requires acquisition by 10:00, the earlier of their cutoffs. The 11:00 cutoff for `h` alone cannot extend the guarantee because `f` is already unavailable. Consequently, budgets 1, 2, and 3 have last acquisition time 09:00; budget 4 extends it to 10:00.

The calculations enumerate feature subsets. An independent comparison uses actor-labelled witness trees: each tree records a chain of unresolved distinctions whose acceptable plans have no common member. A successful selection must remove at least one relevant connection in each such obstruction. The second implementation refines each participant's observations with the selected features and directly enumerates local rules. Both methods must agree on every subset and on the minimum declared cost.

The six scenarios below include an already sufficient baseline, an unavailable repair, two equally cheap alternatives, a single situation with no acceptable action, and repairs assigned to different participants. Additional information cannot create a physically unavailable action, and preserving a feature for one participant does not automatically make it available to another."""),
    code("""preservation_names = {
    "budget_example": "Three-feature budget example",
    "baseline_feasible_no_features": "Baseline already sufficient",
    "no_available_repair": "No repair in the catalog",
    "multiple_optimal_repairs": "Two equally cheap repairs",
    "singleton_no_action": "One situation, no acceptable action",
    "different_participants": "Features held by different participants",
}
table(["Scenario", "Subsets", "Comparison", "Witness minimum cost", "Direct-rule minimum cost"], [
    [preservation_names[name], r["witness_direct_comparison"]["subset_comparisons"],
     "Agreement" if r["witness_direct_comparison"]["all_agree"] else "DISAGREEMENT",
     cost_label(r["witness_direct_comparison"]["minimum_witness_cost"]),
     cost_label(r["witness_direct_comparison"]["minimum_direct_cost"])] for name, r in pres.items()
])"""),
    md("""All 19 subsets across these six scenarios are compared. A zero cost means the baseline already supports the task without purchasing a feature; 'No feasible selection' means no offered bundle supplies a guarantee. Those expected infeasible cases are successful checks when both implementations detect the obstruction. The budget table evaluates the specified toy choices. Sections 8 and 9 compare finite required costs and acquisition cutoffs under situation restriction and early regime knowledge. The general frontier and inverse-cost results remain established by the manuscript's proofs.

## 5. Transmission time, contact windows, and storage

Information must reach the participant who needs it and survive until use. For a continuous channel transmitting 2 bits per minute through 10:00, an 8-bit message needs four minutes and must start by 09:56. If a known task needs only one bit, its transmission takes 30 seconds and can start at 09:59:30. This calculation assumes negligible encoding time, sufficiently early channel opening, and retention after receipt. It illustrates a specified message requirement for an unknown later task versus a known one-bit task; it is not a universal coding requirement."""),
    code("""known_start = minutes("09:59") + timing["known_task_latest_start_minutes_after_09_59"]
whole = int(known_start)
known_clock = f"{whole // 60:02d}:{whole % 60:02d}:{round((known_start - whole) * 60):02d}"
table(["Message requirement", "Rate", "Channel closes", "Latest start"], [
    ["8 bits for the declared unknown later task", "2 bits/min", "10:00", timing["unknown_later_task_latest_start"]],
    ["1 bit for the known task", "2 bits/min", "10:00", known_clock],
])"""),
    md("""### Two contacts with an intervening memory reset

In the contact example, A is the coordinator, B the intermediary, and C dispatch. A can start a five-minute transmission to B from 09:50 through 10:00. B can start a four-minute transmission to C from 10:10 through 10:20. These are **allowed start intervals**. Dispatch needs the bit by 11:00 for a subsequent 30-minute action completed by 11:30, and retains the bit after receipt.

Working backward under freely available holding memory gives latest sends of 10:20 from B and 10:00 from A. Every arrival at B is by 10:05. If B resets at 10:07 and erases its unprotected state, none of those arrivals can survive to the second contact. Protected storage across that reset restores the route. For example, send at 10:00, receive at 10:05, preserve across the reset, forward at 10:10, and receive at C at 10:14.

The independent enumerator tries all integer-minute sends in each two-contact scenario. It includes waiting, nonzero durations, inclusive contact endpoints, and an inclusive terminal deadline. The unavailable-route variant ends A's start window at 09:54 and requires C's receipt by 10:13, before the earliest possible 10:14 arrival. The boundary variant permits only starts at 10:00 and 10:05, and C receives exactly at its 10:09 deadline.

For resets, the declared ordering erases unprotected information when `receipt <= reset < next send`. A send at the reset minute is treated as occurring before erasure, including an immediate receipt-and-send handoff. Protected storage bypasses that erasure. Memory updates use retained state and new observations; they cannot retrieve a discarded private history without an available route."""),
    code("""schedule_names = {
    "free_holding_memory": "Uninterrupted holding memory",
    "unavailable_route": "Arrival deadline cannot be met",
    "reset_without_storage": "Reset without protected storage",
    "reset_with_storage_repair": "Reset with protected storage",
    "boundary_receipt_and_send": "Exact contact and arrival boundaries",
}
table(["Node", "Latest time under free holding memory"],
      [[node, deadline_label(timing["contact_dag"]["latest"][node])] for node in ("A", "B", "C")])
table(["Scenario", "Free-memory recurrence", "Enumerated feasible schedules", "Interpretation"], [
    [schedule_names[name], "Route feasible" if r["recurrence_feasible"] else "No route",
     r["enumerated_schedule_count"],
     "Expected difference: reset violates free-memory assumption" if name == "reset_without_storage"
     else ("Agreement" if r["recurrence_feasible"] == r["enumerated_feasible"] else "DISAGREEMENT")]
    for name, r in timing["schedule_enumeration_cases"].items()
])"""),
    md("""The reset-without-storage row intentionally contrasts two memory regimes. The free-memory recurrence reports a route, while the enumerator enforcing erasure finds none. That difference is expected and is recorded as such. It demonstrates why the recurrence cannot be applied unchanged when holding memory disappears. Restoring storage restores the feasible route. The boundary example checks equality at contact and arrival limits; it does not independently test every possible reset-minute ordering.

## 6. Joint retention can change the shared-plan guarantee

Suppose two participants each retain a binary label, 0 or 1. Source situations `L`, `M`, and `R` permit plans `{a}`, `{a,b}`, and `{b}`, respectively. In both channels, `L` produces label pair `(0,0)` and `R` produces `(1,1)`. At `M`, the **aligned** channel produces `(0,0)` or `(1,1)` with equal probability; the **crossed** channel produces `(0,1)` or `(1,0)` with equal probability.

For either participant considered separately, the conditional label distributions are identical between channels. The difference is which labels occur together. With aligned outcomes, both can follow `0 -> a` and `1 -> b` and always select the same acceptable plan. Crossed outcomes connect locally indistinguishable realizations with incompatible endpoint requirements, eliminating the guarantee.

The supported-realization graph includes each source-and-label outcome with positive probability. It connects outcomes sharing any participant's local state. We compare its shared-plan criterion with direct local-rule enumeration. The table's rule count is the number of successful rule pairs, not the number evaluated.

A supplementary two-world example provides another support obstruction. World `A` requires plan `a` and always produces `(0,0)`. World `B` requires plan `b` and produces `(1,1)` with probability 999/1000 or `(0,0)` with probability 1/1000. The rare shared observation makes the incompatible requirements indistinguishable, so a guarantee is unavailable."""),
    code("""stoch = run_stochastic_coordination_examples()
table(["Conditional marginal comparison", "Same distribution?"], [
    ["Participant 1: aligned versus crossed", yes_no(stoch["marginals_equal"]["participant_0"])],
    ["Participant 2: aligned versus crossed", yes_no(stoch["marginals_equal"]["participant_1"])],
])
table(["Channel", "Supported outcomes", "Graph result", "Direct-rule result", "Successful rule pairs"], [
    [label, stoch["domain_sizes"][size], guaranteed(stoch[key]["graph"]["succeeds"]),
     guaranteed(stoch[key]["direct"]["succeeds"]), stoch[key]["direct"]["rule_count"]]
    for label, key, size in [
        ("Aligned", "aligned", "aligned_supported_realizations"),
        ("Crossed", "crossed", "crossed_supported_realizations"),
        ("Two worlds with rare overlap", "support_sensitivity", "support_sensitivity_realizations"),
    ]
])"""),
    md("""Separate participant summaries cannot distinguish these aligned and crossed mechanisms even when their conditional marginals are known exactly. Operational records therefore need to preserve which participant states occurred together, linked to the same episode and source conditions, when joint behavior is the question. Paired observations can reveal that dependence. Finite observations alone cannot establish that an unobserved outcome is impossible without additional assumptions about the mechanism.

### A high average without a probability-one guarantee

For the manuscript's three-situation mixture, keep `L` and `R` fixed and give the crossed outcomes total probability epsilon at `M`. Each aligned outcome has probability `(1 - epsilon)/2`; each crossed outcome has probability `epsilon/2`. Any positive crossed mass removes the guarantee. The label-following rule still succeeds at `M` with probability `1 - epsilon`, giving source-averaged success `1 - p(M) epsilon`. This is the performance of that specified rule, not a claimed optimum. The calculation below uses epsilon = 1/100 and p(M) = 1/3."""),
    code("""sensitivity = stoch["manuscript_support_sensitivity"]
table(["Quantity", "Result"], [
    ["Crossed probability at M", sensitivity["epsilon"]],
    ["Source probability of M", sensitivity["p_M"]],
    ["Graph guarantee", guaranteed(sensitivity["graph"]["succeeds"])],
    ["Direct-rule guarantee", guaranteed(sensitivity["direct"]["succeeds"])],
    ["Label-following average success", sensitivity["label_following_average_success"]],
    ["Formula: 1 - p(M) epsilon", sensitivity["stated_formula"]],
])"""),
    md("""An average success of 299/300 coexists with the absence of a guarantee. Positive probability determines whether an outcome must be covered by a probability-one claim; making that probability small does not remove the requirement. These calculations concern the fixed channel and fixed acceptable plans. They do not rule out successful alternative communication protocols. If random outcomes also change physical feasibility, those changes must enter the acceptable-action model.

### Optimizing average success over all local rules

The previous calculation evaluates one specified rule. If all deterministic local-rule pairs are allowed, both participants can instead always choose `a` or always choose `b`. Write `p(L)`, `p(M)`, and `p(R)` for the source probabilities, corresponding to the manuscript's `p(x_L)`, `p(x_M)`, and `p(x_R)`. The optimum is

`P* = 1 - min {p(L), p(R), p(M) epsilon}`.

Always choosing `b` sacrifices situation L and has loss `p(L)`; always choosing `a` sacrifices R and has loss `p(R)`. Label-following succeeds at both endpoints but loses `p(M) epsilon` on crossed middle outcomes. A pair that succeeds at both endpoints must follow the labels, while any other pair fails at least one endpoint. These three candidate losses therefore attain the optimum. The calculation below independently evaluates all 16 local-rule pairs against the joint outcomes and compares their best score with the formula.

The bounded comparison uses all 66 nonnegative source-probability triples in multiples of 1/10 summing to one and all 11 values `epsilon = 0, 1/10, ..., 1`. Its 726 cases require 11,616 rule-pair evaluations. The example rows show label-following and each constant plan being optimal. The source weights are ordered L, M, R; all values are exact fractions."""),
    code("""mixture = stoch["mixture_optimum_family"]
policy_names = {"label_following_optimal": "Follow labels", "constant_b_optimal": "Always b", "constant_a_optimal": "Always a"}
table(["Source weights (L, M, R)", "Epsilon", "Label-following success", "All-rule optimum", "Formula", "An optimal pair"], [
    [", ".join(str(r["source_probabilities"][x]) for x in ("L", "M", "R")), r["epsilon"],
     r["label_following_average_success"], r["direct_optimum"], r["stated_formula"], policy_names[name]]
    for name, r in mixture["worked_examples"].items()
])
table(["Source priors", "Epsilon values", "Mixture cases", "Rule-pair evaluations", "Implementation disagreements"], [[
    mixture["prior_count"], mixture["epsilon_count"], mixture["case_count"],
    mixture["rule_pair_checks"], mixture["mismatch_count"],
]])"""),
    md("""In the two constant-plan examples, the optimum is 9/10 while label-following achieves 7/10. That improvement accepts failure whenever the sacrificed endpoint occurs. The optimization therefore permits rules that are not individually acceptable everywhere. A per-source probability-one guarantee remains a different requirement: it covers every source situation, including one assigned zero weight in an average. Agreement on this grid checks these 726 probability specifications; the manuscript gives the argument for the general formula.

### Exhaustive checks within a declared binary domain

The bounded family has two source worlds, two participants, binary local observations, and plans `{a,b}`. Each world has 15 possible nonempty subsets of the four joint binary outcomes and three possible nonempty acceptable-plan subsets. This gives `15^2 x 3^2 = 2,025` support/action cases. Uniform rational probability within each chosen support supplies a valid channel. The graph criterion depends on support; the enumeration does not range over all probability distributions.

For every case, direct enumeration evaluates all 16 binary local-rule pairs, including assignments to unreachable binary states. This totals 32,400 rule-pair evaluations. An empty acceptable-action set is checked separately and is outside the 2,025-case family."""),
    code("""family = stoch["exhaustive_two_world_support_family"]
table(["Support/action cases", "Expected cases", "Rule-pair evaluations", "Implementation disagreements"], [[
    family["case_count"], family["expected_case_count"], family["rule_pair_checks"], family["mismatch_count"],
]])"""),
    md("""## 7. One rule while the mechanism is uncertain

Knowing that each possible channel permits success is not enough when the participants must choose their rules before learning which channel applies. The rule at each local state must then be the same under every candidate mechanism. The union-of-support criterion combines supported realizations and connects outcomes sharing a participant's local state. The independent comparator enumerates every local-rule profile and checks it against each original channel separately.

The exhaustive finite domain has two source situations, two participants, binary local states, and the fixed plans `{a,b}`. There are 16 deterministic joint channels, 136 unordered pairs with repetition, and 16 pairs of acceptable sets (including empty sets). All 16 rule profiles are checked for each of the resulting 2,176 cases, giving 34,816 profile evaluations. This is not an enumeration of all channel families or probability distributions.

The two worked contrasts use a channel delivering the target label and a channel reversing it. If the two sources demand different plans, each channel admits a successful rule when known, but the pair admits no common rule. If plan `a` is acceptable in both sources, both participants can always choose it, so a common rule exists."""),
    code("""extensions = bounded_summary()
mechanisms = extensions["mechanisms"]
table(["Task requirements", "Each channel separately feasible?", "Union criterion", "One rule under both channels"], [
    [label, yes_no(all(mechanisms["examples"][key]["separate_feasibility"])),
     guaranteed(mechanisms["examples"][key]["union_feasible"]),
     guaranteed(mechanisms["examples"][key]["direct_feasible"])]
    for key, label in [("separately_feasible_only", "Different required plans"),
                       ("common_rule_exists", "Common acceptable plan a")]
])
table(["Channel-pair/action cases", "Rule-profile evaluations", "Disagreements"], [[
    mechanisms["cases"], mechanisms["rule_profile_evaluations"], len(mechanisms["mismatches"])
]])"""),
    md("""## 8. Restricting which situations must be covered

Does omitting a situation make preservation harder? Here only the evaluated situation set changes. The plan and feature catalogs, participants, feature ownership, values on retained situations, costs, acquisition windows, storage, noon decision, and executable lookup-rule class stay fixed. Every previously successful selection must remain successful after restriction. The comparison is not an improvement in the actual briefing or evidence that an omitted situation is safe.

We evaluate all 15 nonempty subsets of the worksheet's four situations and all eight feature bundles per subset. Three additional no-feature comparisons cover a sufficient baseline, a persistent empty-action obstruction, and removal of that obstruction. These give 18 full/restricted pairs and 123 restricted-bundle comparisons. For each pair, the component-based optimizer and cutoff sweep are compared with independent enumeration of terminal local-rule profiles for each bundle.

Required costs are evaluated at 08:00, 09:00, 09:00:30, 10:00, 10:00:30, 11:00, 11:00:30, and noon: 144 full/restricted cost comparisons. Cutoffs are evaluated at budgets 0, 1, 2, 3, 4, and 5: 108 comparisons. Times are exact rational minutes. An infeasible cost is positive infinity and an empty affordable successful family has cutoff negative infinity. An already sufficient baseline has cost zero and cutoff positive infinity, meaning no acquisition is required; operational acquisition remains restricted to times at or before noon."""),
    code("""restrictions = extensions["restriction"]
chosen = [c for c in restrictions["cases"] if c["restricted"] in (
    ((1, 0), (1, 1), (2, 0), (2, 1)), ((2, 0), (2, 1))) or not c["name"].startswith("worksheet")]
table(["Included situations", "Full cost at 10:00", "Restricted cost at 10:00", "Full cutoff, B=2", "Restricted cutoff, B=2"], [
    [str(c["restricted"]) if c["name"].startswith("worksheet") else c["name"],
     *c["costs"][3]["direct"], *[deadline_label(v) for v in c["deadlines"][2]["direct"]]]
    for c in chosen
])
table(["Full/restricted pairs", "Restricted bundles", "Cost comparisons", "Cutoff comparisons"], [[
    len(restrictions["cases"]), restrictions["restricted_selection_comparisons"],
    sum(len(c["costs"]) for c in restrictions["cases"]),
    sum(len(c["deadlines"]) for c in restrictions["cases"])
]])"""),
    md("""Keeping all four situations gives equality. Keeping regime 2 alone leaves the early one-unit option unchanged but lowers the 10:00 cost from four to two; at budget two, its cutoff improves from 09:00 to 11:00. The report also compares every full and restricted bundle's feasibility and verifies the direction of both inequalities at every listed time and budget. These finite checks supplement the restriction proposition's proof.

## 9. Regime information before acquisitions are selected

Transport knows the regime at noon in both designs. The new input is whether the authorized coordinator knows that regime when choosing what to acquire. Without that early information the same bundle must be purchased in both regimes. With it, a policy may select one bundle for regime 1 and another for regime 2, but cannot condition on the hidden target within a regime.

The direct calculation enumerates eight fixed bundles and all 64 mappings from two regimes to those bundles. Each bundle's terminal adequacy is checked by enumerating local lookup profiles; availability is checked against every selected feature's inclusive cutoff. Conditional component calculations provide the independent comparison. Policy cost is the maximum acquisition expenditure across regimes, not an average under an assumed prior. The optimal policies here cost the same in either realized regime.

The eight acquisition times below bracket all three feature cutoffs with exact half-minute probes. The finite timing table does not sample every real time; the returned bundle cutoffs and the manuscript's proof supply the interval interpretation. The cost and time needed to obtain regime information are excluded."""),
    code("""early = extensions["early_information"]
time_names = ["08:00", "09:00", "09:00:30", "10:00", "10:00:30", "11:00", "11:00:30", "12:00"]
table(["Acquisition time", "Fixed-bundle cost", "Early-regime policy cost", "Regime-2-only cost"], [
    [name, *row["policy_costs"], conditional]
    for name, row, conditional in zip(time_names, early["costs"], early["regime_2_costs"])
])
table(["Acquisition time", "Fixed choice in both regimes", "Choice in regime 1", "Choice in regime 2"], [
    [time_names[i], ", ".join(early["costs"][i]["fixed_optima"][0][0]),
     *[", ".join(bundle) for bundle in early["costs"][i]["regime_optima"][0]]]
    for i in (1, 3)
])
table(["Information available for acquisition", "Latest cutoff"], [
    [label, deadline_label(value)] for label, value in zip(
        ["Fixed bundle, both regimes", "Early regime information, both regimes", "Regime 2 only"],
        early["policy_cutoffs"])
])"""),
    md("""Through 09:00 the complete feature `g` costs one unit, so early regime information does not lower the displayed minimum. After 09:00 through 10:00, the fixed bundle `{f,h}` costs four; the contingent choices `{f}` and `{h}` cost two. Both designs lose the across-regime guarantee after 10:00. Conditional on regime 2, `h` remains obtainable through 11:00. Transport's terminal knowledge is unchanged throughout: it cannot justify conditioning an earlier acquisition on information the coordinator did not yet possess.

## 10. Preservation must support every decision occurrence

A physically successful sequence is an analyst's witness, not permission for the controller to read the complete history. The policy here is one lookup on the current baseline state and selected memory channels. If one trajectory returns to the same observed state, it must make the same choice there. The decision bound limits the search; it is not a hidden clock supplied to that lookup.

For the permanent-feature family, there are two physical stages, two possible observable states, two action labels, and at most two decisions. We enumerate every observation map, every initial and terminal acceptable-action subset (including the empty set), every binary persistent feature, and both feature selections. With two source records this gives 32,768 comparisons; with one source it gives 256. Successful path combinations are checked for conflicts between **all occurrences**, including two occurrences in the same trajectory. Independently, direct search assigns executable lookup entries shared across all records and repeated visits. Legal defaults exist for off-path entries.

In the preparation example the physical stage changes but the baseline observation does not. No persistent source feature can distinguish 'prepare' from 'execute' within the same source. A causal preparation flag can. Its update reads the newly available preparation observation, not the analyst's step number.

The coded-reply example has source `(u,v)` and target `u XOR v`. Two reads take five minutes each; targeted action takes 30 minutes before noon. The baseline contains clock and stage, not the answers. An overwrite channel replaces its content with each reply. A decode channel retains `u` on the first read and `u XOR v` on the second. A third channel permanently retains the source code `u`. Each update depends only on its own current value, the new reply, and declared baseline state, independently of which other channels were selected. All eight selections are compared at all 61 integer-minute starts from 11:00 through noon: 488 comparisons. Costs of including channels would not by themselves measure storage capacity."""),
    code("""from oder_supplement.temporal import temporal_summary
temporal = temporal_summary()
table(["Finite family", "Comparisons", "Disagreements"], [
    [label, temporal[key]["cases"], len(temporal[key]["mismatches"])]
    for key, label in [("two_source", "Two-source persistent feature"),
                       ("single_source", "One-source repeated occurrences"),
                       ("overwrite", "Coded replies and causal channels")]
])
table(["Preparation memory", "All-occurrence cover", "Executable policy"], [
    [", ".join(row["selection"]) or "No channel", yes_no(row["cover"]), yes_no(row["direct"])]
    for row in temporal["preparation"]
])
table(["Channels at 11:00", "All-occurrence cover", "Executable policy"], [
    [", ".join(row["selection"]) or "No channel", yes_no(row["cover"]), yes_no(row["direct"])]
    for row in temporal["overwrite"]["examples"]
])"""),
    md("""An overwritten answer is unavailable unless another selected channel actually retains it. The overwrite channel alone fails, while decoding or retaining the code alongside the overwritten final key permits the target choice. A timely complete two-read route can begin through 11:20 inclusive. These are finite checks of the temporal construction and causal update model, not general proofs.

## 11. Fixed-polarity inputs and monotone responses

At ordinary baseline states the policy is unrestricted lookup. At designated response states it is a nondecreasing Boolean function of the selected Boolean inputs. This response mode is observed and cannot be bypassed through a separate stopping choice. Both responses are legal at every configured input; task acceptability is a separate requirement. No input inversion or nonmonotone preprocessing is supplied.

Ordinary conflicts require unequal retained tuples. For a response-1 occurrence and response-0 occurrence at the same designated state, directional coverage requires a selected input that is 1 at the former and 0 at the latter. We compare these tests against enumeration of all permitted response tables on the **full Boolean input cube**, including off-path inputs. At each response state, upward closure of the prescribed positive tuples supplies a candidate completion; we verify both monotonicity and agreement with all prescribed responses. Rules at distinct baseline states have no additional coupling.

The domain has three decision occurrences, two baseline states (one ordinary, one monotone), two candidate Boolean features, all eight baseline assignments, all eight prescribed-response assignments, and all four feature selections. We use all 64 feature assignments on three distinct sources (16,384 cases), then all 16 feature assignments for the repeated-source sequence `(0,1,0)` (4,096 cases). These are partial-lookup extension checks, not a claim that every assignment is a physically successful trajectory. Repeated occurrences with conflicting responses cannot be separated by a permanent feature of their common source.

For the warning example, clearance `f(x)=x` costs one unit and the approved complementary input `g(x)=1-x` costs two. The required response is `1-x`. Retaining `f` permits unrestricted inversion but cannot implement that response monotonically. Selecting `g` permits the identity response. The comparison is about this declared rule class, not arbitrary authorization restrictions."""),
    code("""from oder_supplement.monotone import monotone_summary
monotone = monotone_summary()
table(["Occurrence sources", "Cases", "Local tables evaluated", "Completions checked", "Disagreements"], [
    [label, row["cases"], row["local_rule_tables_evaluated"], row["upward_completions_checked"], len(row["mismatches"])]
    for label, row in [("Three distinct sources", monotone["distinct_sources"]),
                       ("Sources 0, 1, 0", monotone["repeated_source"])]
])
table(["Approved inputs", "Cost", "Unrestricted success", "Monotone success"], [
    [", ".join(row["features"]) or "None", row["cost"], yes_no(row["unrestricted"]), yes_no(row["monotone"])]
    for row in monotone["warning"]["rows"]
])
print("Minimum costs: unrestricted =", monotone["warning"]["unrestricted_minimum"],
      "; monotone =", monotone["warning"]["monotone_minimum"])"""),
    md("""The two inputs distinguish the same records, but only the approved complementary input has the polarity needed for the monotone response. Free inversion would erase the cost difference and is outside this model. The ordinary-state policy remains unrestricted; the comparison does not impose an ordering on consultation endpoints.

## 12. Initial locator categories with legal retries

Record `(a,b)` specifies the correct endpoint `a` (0 or 1) and target `b` (1 through `m`). Every pair is possible. Targeted action takes 20 minutes, each endpoint query takes five, the universal query takes 25, and common protection takes 50, with deadline minute 60. Both endpoint queries are legal; a wrong endpoint returns failure without target information, and a retry is allowed. This is the **legal-retry model**, not a single-query construction.

The controller retains its initial handoff category, clock, query stage, failed endpoint, and successful reply. Physics uses the true source; lookup keys do not. Policy search branches over the available operations at unassigned reached states and reuses each assignment in every compatible source run. Positive query durations bound the search. Each handoff category can have its own lookup; within it, no hidden target or analyst history is available.

We enumerate all 15 partitions of four records (`m=2`), all 203 partitions of six (`m=3`), and all 4,140 partitions of eight (`m=4`). Each is checked for recovery and immediate-action feasibility at 11 exact times: 0, 29.5, 30, 30.5, 34.5, 35, 35.5, 39.5, 40, 40.5, and 60. This gives 47,938 partition/time cases and 33 comparisons of attained minima with the stated frontier. Direct search covers every nonempty category block at those times. A further 244 target-count/time cases (`m=2,3,4,5`, integer starts 0 through 60) check constant, locator, and target encodings, giving 732 encoding-feasibility comparisons.

The expected recovery minimum is one category through minute 30, two for `30 < s <= 35`, `m` for `35 < s <= 40`, and infeasible afterward. Immediate action requires `m` categories throughout the middle interval. The following table displays the four-target case, including both sides of each boundary."""),
    code("""from oder_supplement.locator import locator_summary
locator = locator_summary()
table(["Recovery start", "Recovery categories", "Immediate-action categories"], [
    [str(row["start"]), category_label(row["recovery_categories"]), category_label(row["immediate_categories"])]
    for row in locator["partitions"]["rows"] if row["targets"] == 4
])
table(["Targets", "Recovery categories at 30.5", "Immediate categories at 30.5", "Exact ratio"], [
    [row["targets"], row["recovery_categories"], row["immediate_categories"], str(row["ratio"])]
    for row in locator["partitions"]["rows"] if row["start"] == 30.5
])
table(["Comparison", "Cases", "Disagreements"], [
    ["Exhaustive partition minima", locator["partitions"]["cases"], len(locator["partitions"]["mismatches"])],
    ["Three encodings across integer starts", locator["retry"]["cases"], len(locator["retry"]["mismatches"])],
])"""),
    md("""The first interval includes the time for a failed query, retry, and action. The middle interval allows one successful consultation but not a failed one followed by retry. After minute 35, only preserving the target permits timely action; after minute 40 even correct immediate action is late. All endpoints are inclusive as stated.

The ratio `m/2` compares **initial handoff distinctions**. The query reply still supplies one of `m` target values and needs capacity to retain that answer until action. Here that reply is explicitly in the retained state. A separately specified register could overwrite the locator with the reply, but initially fewer occupied categories would still not imply smaller hardware capacity. These calculations do not establish reduced total information or peak memory. Exhaustive minima cover only the listed small target counts; the manuscript proves the general finite-family result.

## 13. Distinct temporal operation models

The independent implementations in Sections 10 and 12 remain separate from the maintained research calculations below. Similar case counts do not imply identical domains. The research functions run in the normal verification workflow.

The **single-query family** has four binary-pair source records, all 16 target assignments, four route maps, two reply-retention modes, duration pairs `(5,25)`, `(10,20)`, and `(0,0)`, six starts `5,15,25,35,40,41`, and four permanent-feature selections: 9,216 comparisons. A fast query is admissible only at its source-specific correct endpoint; the generic query is always available. There is at most one query, so zero durations in one specification do not allow infinitely many decisions. Wrong-endpoint failure and retry are not part of this construction.

The **occurrence family** has two sources and two hidden physical states, all 16 transition maps, 16 success maps, 16 observation maps, and four selections of a source bit and a constant feature: 16,384 comparisons. The only decisions are step and stop; at most two are permitted. No clock, physical state or complete history is observed. Omitting same-source occurrence conflicts produces 880 false positives in this exact domain.

The **causal overwrite family** replaces the initial locator with the returned target in one data register. Its baseline holds stage and clock but no independent reply copy. Direct policies and occurrence coverage agree at each integer start 0 through 60. Its separate **legal-retry family** allows either endpoint query, retains a failure and the queried endpoint sufficiently for retry, and retains a successful reply for action. It checks all 61 starts for target counts 2, 3, 5, and 10: 244 comparisons. Section 12's independently implemented 244-case sweep instead uses target counts 2, 3, 4, and 5 and checks three initial encodings. Neither sweep is a count of arbitrary encoding partitions.

An auxiliary compatible-execution family enumerates three-source nonempty acceptable relations on two participants' binary local actions and all 16 owned-feature selections: 54,000 comparisons. Its four-source contrast needs cost two for compatible local actions but four if both participants must identify the same complete joint tuple. This illustrates the manuscript's distinction between compatibility and shared-plan agreement; it is not an equivalence between those tasks.

A separate four-record perturbation enumerates all four constant binary-action profiles. If total activation need only meet or exceed demand, constant action `(1,1)` succeeds without retained information. The cost contrast therefore depends on the stipulated exact-demand acceptance relation, not merely on having two participants."""),
    code("""summary = verification_summary()
Path("reports/verification_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
if summary["verification"]["failure_count"]:
    Path("reports/verification_diagnostics.json").write_text(
        json.dumps({"failures": summary["verification"]["failures"]}, indent=2), encoding="utf-8")
assert_no_failures(summary["verification"])
research = summary["research_comparisons"]
research_results = {name: entry["result"] for name, entry in research.items()}
table(["Maintained research family", "Computed comparisons"], [
    ["Single-query permanent features", research_results["single_query"]["temporal_policy_cover_comparisons"]],
    ["Step/stop occurrence coverage", research_results["occurrence"]["occurrence_policy_cover_comparisons"]],
    ["One-register causal overwrite", research_results["causal_retry"]["streaming_policy_cover_comparisons"]],
    ["Legal retries, four target counts", research_results["causal_retry"]["recoverable_retry_checks"]],
    ["Compatible local actions", research_results["compatible_execution"]["exhaustive_relation_feature_cases"]],
])
table(["Construction", "Last constant-handoff start", "Locator route last start"], [
    ["Single query, source-specific endpoint legality", 15, research_results["causal_retry"]["streaming_locator_last_start"]],
    ["Wrong endpoint returns failure; retry permitted", research_results["causal_retry"]["zero_information_with_retry_last_start"], 35],
])"""),
    md("""In the single-query cost worksheet, no purchased feature is needed through minute 15; a one-unit locator works through minute 35; the two-unit target feature is then needed through minute 40. With legal retries, a constant initial category works through minute 30 instead. These different cutoffs follow from different operation menus, not a contradiction. The overwrite example explicitly provides the later reply register capacity and does not imply lower peak memory.

## 14. Unequal endpoint durations

For a complete source product `(endpoint,target)`, endpoint `i` takes positive duration `f_i` and either returns the target or a common target-free failure. Queries are serial and retries legal. Targeted action alone is acceptable and takes `p`; no universal query or common protective route is present. The controller observes clock, schedule position and the retained target reply. A category can specify a fixed failure-prefix search schedule; successful replies stop that search and supply the action target.

With query budget `T = D - s - p`, the endpoint batching number `B_f(T)` is the minimum number of endpoint groups whose duration sums each fit `T`, or infinity if any endpoint cannot fit. The proposition gives `min(m, B_f(T))` initial categories when action itself remains timely, and infinity afterward. Both arbitrary mixed target/locator encodings and pure batch encodings are included in the comparisons.

One maintained research implementation enumerates ordered search policies and exact covers of their successful source sets, then checks every initial partition with fewer than `m` cells; the target encoding supplies the `m`-cell upper bound. Across endpoint/target pairs `(2,2),(2,3),(3,2),(3,3),(4,3)`, all duration vectors in `{1,2}^n`, and integer budgets from zero through the total duration, it checks 232 models and 241,212 candidate partitions. A second implementation uses all partitions and recursive failure-branch policies for six specifications: `(n,m,f) = (2,2,(1,3)), (2,3,(1,3)), (3,2,(1,2,3)), (3,3,(1,2,3)), (3,3,(2,2,2)), (4,2,(1,1,2,3))`. It checks 39 budget comparisons. These methods retain distinct implementations.

Additional policy simulation checks every half-unit query budget from -0.5 through `sum(f)+0.5` for `(m,f) = (2,(2)), (3,(1,3)), (3,(1,2,3)), (5,(1,1,2,2))`, with deadline 20 and action duration 3: 48 comparisons and 5,788 schedule/fallback policies. Negative budget means even immediate action is late. Positive durations and target-free failures make repeated queries to an already failed endpoint unhelpful, so schedules enumerate distinct endpoints. A successful reply may stop a long schedule early. Minimum covers of policy-success sets represent arbitrary handoff categories; endpoint partitions independently supply the packing comparison."""),
    code("""heterogeneous = research_results["heterogeneous_boundaries"]
table(["Unequal-endpoint calculation", "Model/budget comparisons"], [
    ["Ordered policies and small arbitrary encodings", research_results["endpoint_search"]["models"]],
    ["Recursive policies and full partition lists", research_results["endpoint_partition"]["comparisons"]],
    ["Half-unit boundary and policy simulation", heterogeneous["cases"]],
])
table(["Query time available", "Endpoint batching categories", "Minimum initial categories"], [
    [str(row["query_budget"]), "No feasible batching" if row["packing_categories"] == "infinity" else row["packing_categories"],
     category_label(row["policy_categories"])]
    for row in heterogeneous["example"]
])"""),
    md("""For four endpoints with durations `(1,1,2,2)` and five targets, the four displayed query budgets give exactly 5, 3, 2, and 1 initial categories. At budget one, some endpoints cannot be queried in time, so preserving the target is optimal. At budget two, three endpoint batches suffice; at budget three, two suffice. Budget six permits a single initial category and a complete search. These are initial distinctions: the reply still represents one of five targets and must remain available for action. The general lower bound is supplied by the manuscript, not by these finite searches.

## 15. A shared-plan guarantee from marginal supports

Suppose only each participant's conditional marginal support is known. Allow **every** joint conditional coupling consistent with those marginals, with no additional dependence restriction. One fixed deterministic profile must succeed for every source and every allowed coupling; selecting a different rule for each unknown coupling would answer another question.

The source-overlap graph connects two sources whenever at least one participant's supports overlap. For at least two participants, each connected component must admit one common acceptable plan. The construction chooses that plan and assigns it to each local symbol occurring in the component. Unused symbols can receive a legal default. The product law is an allowed maximal-support witness; it is not an assumption that actual handoffs are independent, nor a claim about worst expected loss.

The maintained research calculation enumerates all three nonempty binary supports for each source/participant, all four binary acceptable-plan sets including the empty set, and all local binary lookup profiles. It covers two participants with one, two, or three sources (47,988 configurations), and three participants with one or two sources (11,772): 59,760 total. A separate implementation constructs and replays the successful component profiles, including a legal completion at unused symbol 2. This exercises 16,809 feasible profiles across the same domain; it is not another 59,760 distinct configurations.

For finite nonuniform-law checks, two sources and two participants have conditional probabilities of symbol zero in `{0,1/3,1/2,1}`. For each pair of marginals we use the two Frechet endpoints, their midpoint, and the product coupling, dropping duplicates. Across all 256 source-law assignments and 16 acceptable-set assignments, all 16 fixed profiles are compared: 4,096 cases and 65,536 profile evaluations. These representative exact rational laws check the implementation; the manuscript's maximal-support argument handles the entire continuous coupling family.

Finally, 5,184 cases examine participant-owned refinements: 81 support assignments, 16 acceptable-set assignments and four selections from one source-bit feature per participant. An edge belonging to one participant disappears only if that participant's selected feature separates the sources. Direct rule search on augmented local symbols is compared with the refined graph."""),
    code("""table(["Marginal-support comparison", "Configurations", "Unexpected disagreements"], [
    ["All binary support/action families", research_results["marginal_support"]["cases"], research_results["marginal_support"]["disagreements"]],
    ["Constructed profiles on the same family", research_results["marginal_construction"]["cases"], len(research_results["marginal_construction"]["mismatches"])],
    ["Exact rational conditional couplings", research_results["marginal_couplings"]["cases"], len(research_results["marginal_couplings"]["mismatches"])],
    ["Participant-owned refinements", research_results["marginal_features"]["cases"], len(research_results["marginal_features"]["mismatches"])],
])
table(["Participants retaining the source bit", "Remaining overlap-edge owners", "Robust guarantee"], [
    [", ".join(str(i + 1) for i in row["selected_owners"]) or "Neither",
     ", ".join(str(i + 1) for i in row["surviving_edges"]) or "None", yes_no(row["feasible"])]
    for row in research_results["marginal_features"]["example"]
])
table(["Dependence specification", "Shared acceptable plan guaranteed"], [
    [label, yes_no(research_results["dependence_contrast"][key])]
    for key, label in [("aligned", "Specified aligned channel"), ("crossed", "Specified crossed channel"),
                       ("all_couplings", "All couplings with those marginals")]
])"""),
    md("""With only one participant, the source-component shortcut need not hold. Supports `{0,1}`, `{0}`, `{1}` and acceptable sets `{0,1}`, `{0}`, `{1}` admit the identity local rule even though the overlap graph is connected with no common plan. This boundary is explicitly checked, and the constructive multi-participant API rejects it.

The aligned/crossed contrast distinguishes uncertainty about the actual mechanism from robust design over all compatible mechanisms. Extra justified dependence restrictions can restore feasibility; the maximal-support certificate must not be applied as an exact test for that smaller family. Restricted executable rule classes or off-path illegality likewise require an additional extension check.

## 16. What successful verification establishes

The final report groups the comparisons into verification records and computes their count below. These records have different domain sizes: a single boundary comparison, a collection of feature subsets, and an entire stochastic family are not interchangeable units. The support/action family contains 2,025 cases and 32,400 rule-pair evaluations. Separately, the mixture-optimum grid contains 726 cases and 11,616 rule-pair evaluations. The channel-family comparison contains 2,176 cases and 34,816 profile evaluations. The restriction, early-information, temporal, monotone, and locator domains are stated above. Records, cases, partitions, and rule evaluations describe different levels of accounting.

Agreement supports the implementations and stated outcomes on the supplied finite domains. Expected impossibilities, such as no shared plan or no surviving route after a reset, are successful checks when the calculation detects them correctly. The reset contrast is explicitly recorded as an expected difference between assumptions. An unexpected disagreement is a verification failure and should stop reproduction for investigation.

The scope includes two heat records at six decision times; all 16 shelter rule pairs and three rational source distributions; 19 feature subsets across six preservation scenarios; five integer-minute two-contact scenarios; the declared stochastic family and channel examples; and the mechanism, restriction, early-information, temporal, monotone, and locator domains above. It does not exhaust arbitrary intervention catalogs, continuous schedules, communication protocols, or probability distributions. The source-to-computation map below identifies the corresponding arguments. Scripts evaluate the specified finite constructions; they do not parse or prove the manuscript's mathematical claims."""),
    code("""summary = verification_summary()
Path("reports/verification_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
table(["Report quantity", "Count"], [
    ["Computed verification records", summary["verification"]["record_count"]],
    ["Unexpected verification failures", summary["verification"]["failure_count"]],
])
assert_no_failures(summary["verification"])
print("Completed the declared checks. Report: reports/verification_summary.json")"""),
    md("""The completed report makes the examples inspectable and reproducible. It does not estimate response-team error rates, institutional costs, or forecast consequences, and it does not establish the general results by computation. Empirical assessment would require evidence about actual retained information, communication arrangements, physical capacity, and timing under an independently justified protective objective.

## Reference: source-to-computation map

Manuscript labels identify the relevant results even if section numbering changes. The table summarizes the maintained [source map](reports/source_to_computation_map.csv), which also records assumptions and independent comparisons. Implementation names are reference aids for readers inspecting the code."""),
    code("""with Path("reports/source_to_computation_map.csv").open(encoding="utf-8", newline="") as stream:
    source_rows = list(csv.DictReader(stream))
table(["Example or result", "Manuscript labels", "Notebook section"], [
    [r["named_result_or_example"], r["manuscript_label_or_source"], r["notebook_output"]] for r in source_rows
])"""),
]


for index, cell in enumerate(cells):
    cell["id"] = f"climate-oder-{index:02d}"

notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

Path("Climate_ODER_Verification.ipynb").write_text(json.dumps(notebook, indent=2), encoding="utf-8")
print("wrote Climate_ODER_Verification.ipynb")
