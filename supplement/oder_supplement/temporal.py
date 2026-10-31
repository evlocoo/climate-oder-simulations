"""All-occurrence cover versus direct causal retained-state policy search."""

from dataclasses import dataclass
from itertools import combinations, product

from .reporting import make_record


@dataclass(frozen=True)
class Channel:
    name: str
    initial: object
    update: object


@dataclass(frozen=True)
class Model:
    sources: tuple
    actions: tuple
    initial: object
    observe: object
    transition: object
    channels: tuple
    decision_bound: int


def advance(model, source, physical, memory, action):
    result = model.transition(source, physical, action)
    if result[0] == "terminal":
        return result
    _, next_physical, observation, context = result
    baseline = model.observe(source, physical)
    next_memory = tuple(channel.update(value, action, observation, context, baseline)
                        for channel, value in zip(model.channels, memory))
    return "next", next_physical, next_memory


def successful_paths(model, source):
    paths = []

    def visit(physical, memory, path):
        if len(path) == model.decision_bound:
            return
        baseline = model.observe(source, physical)
        for action in model.actions:
            occurrence = (source, baseline, memory, action)
            result = advance(model, source, physical, memory, action)
            if result[0] == "terminal":
                if result[1]:
                    paths.append(path + (occurrence,))
            else:
                visit(result[1], result[2], path + (occurrence,))
    visit(model.initial(source), tuple(c.initial(source) for c in model.channels), ())
    return paths


def witness_cover(model, selected):
    paths = [successful_paths(model, x) for x in model.sources]
    for witness in product(*paths):
        occurrences = tuple(v for path in witness for v in path)
        if all(r != s or a == b or any(memory[k] != other[k] for k in selected)
               for (_, r, memory, a), (_, s, other, b) in combinations(occurrences, 2)):
            return True
    return False


def direct_policy(model, selected):
    """Search one lookup shared across records and all repeated occurrences."""
    policy = {}

    def evaluate():
        for source in model.sources:
            physical = model.initial(source)
            memory = tuple(c.initial(source) for c in model.channels)
            for _ in range(model.decision_bound):
                key = (model.observe(source, physical), tuple(memory[k] for k in selected))
                if key not in policy:
                    return key
                result = advance(model, source, physical, memory, policy[key])
                if result[0] == "terminal":
                    if not result[1]:
                        return False
                    break
                physical, memory = result[1:]
            else:
                return False
        return True

    def search():
        status = evaluate()
        if status is True or status is False:
            return status
        for action in model.actions:
            policy[status] = action
            if search():
                return True
        del policy[status]
        return False
    return search()


def two_stage_model(sources, observations, first_allowed, final_allowed, feature):
    def transition(x, stage, action):
        if stage == 0 and action in first_allowed[x]:
            return "next", 1, None, None
        return "terminal", stage == 1 and action in final_allowed[x]
    channel = Channel("persistent", lambda x: feature[x], lambda old, a, z, c, r: old)
    return Model(sources, (0, 1), lambda x: 0, lambda x, stage: observations[2 * x + stage],
                 transition, (channel,), 2)


def temporal_family(source_count):
    sources = tuple(range(source_count))
    subsets = ((), (0,), (1,), (0, 1))
    cases = 0
    mismatches = []
    for observations in product((0, 1), repeat=2 * source_count):
        for first in product(subsets, repeat=source_count):
            for final in product(subsets, repeat=source_count):
                for feature in product((0, 1), repeat=source_count):
                    model = two_stage_model(sources, observations, first, final, feature)
                    for selected in ((), (0,)):
                        cases += 1
                        covered, direct = witness_cover(model, selected), direct_policy(model, selected)
                        if covered != direct:
                            mismatches.append({"observations": observations, "first": first,
                                               "final": final, "feature": feature, "selected": selected,
                                               "cover": covered, "direct": direct})
    return {"domain": {"sources": source_count, "physical_stages": 2, "observable_states": 2,
                       "actions": 2, "decisions_at_most": 2, "persistent_features": 1,
                       "observation_maps": 2 ** (2 * source_count),
                       "initial_action_set_assignments": 4 ** source_count,
                       "final_action_set_assignments": 4 ** source_count,
                       "feature_maps": 2 ** source_count, "selections": 2},
            "cases": cases, "mismatches": mismatches}


def preparation_example():
    channels = (Channel("persistent", lambda x: 1, lambda old, a, z, c, r: old),
                Channel("preparation flag", lambda x: 0, lambda old, a, z, c, r: z))
    def transition(x, physical, action):
        if physical == 0 and action == "prepare":
            return "next", 1, 1, None
        return "terminal", physical == 1 and action == "execute"
    model = Model((0,), ("prepare", "execute"), lambda x: 0, lambda x, p: 0,
                  transition, channels, 2)
    return [{"selection": [channels[k].name for k in selected],
             "cover": witness_cover(model, selected), "direct": direct_policy(model, selected)}
            for selected in ((), (0,), (1,), (0, 1))]


def coded_reply_model(start):
    def transition(x, physical, action):
        time, stage = physical
        if action in ("A", "B"):
            return "terminal", time + 30 <= 720 and (action == "B") == bool(x[0] ^ x[1])
        if stage >= 2 or time + 5 > 720:
            return "terminal", False
        return "next", (time + 5, stage + 1), x[stage], None
    channels = (Channel("overwrite", lambda x: 0, lambda old, a, z, c, r: z),
                Channel("decode", lambda x: 0, lambda old, a, z, c, r: z if r[1] == 0 else old ^ z),
                Channel("persistent code", lambda x: x[0], lambda old, a, z, c, r: old))
    return Model(tuple(product((0, 1), repeat=2)), ("read", "A", "B"),
                 lambda x: (start, 0), lambda x, p: p, transition, channels, 3)


def overwrite_suite():
    rows, mismatches = [], []
    for start in range(660, 721):
        model = coded_reply_model(start)
        for size in range(4):
            for selected in combinations(range(3), size):
                covered, direct = witness_cover(model, selected), direct_policy(model, selected)
                row = {"start": start, "selection": [model.channels[k].name for k in selected],
                       "cover": covered, "direct": direct}
                rows.append(row)
                if covered != direct:
                    mismatches.append(row)
    examples = [r for r in rows if r["start"] == 660]
    return {"domain": {"sources": 4, "start_times": "integer minutes 11:00 through noon",
                       "read_duration": 5, "action_duration": 30, "deadline": 720,
                       "selections": 8, "decisions_at_most": 3},
            "cases": len(rows), "mismatches": mismatches, "examples": examples}


def temporal_summary():
    return {"two_source": temporal_family(2), "single_source": temporal_family(1),
            "overwrite": overwrite_suite(), "preparation": preparation_example()}


def temporal_records(results):
    records = [make_record("temporal " + name, results[name]["domain"],
                           len(results[name]["mismatches"]), 0, details=results[name])
               for name in ("two_source", "single_source", "overwrite")]
    rows = results["preparation"]
    records.append(make_record("same-source preparation needs causal memory", {"sources": 1, "selections": 4},
                               [[r["cover"], r["direct"]] for r in rows],
                               [[False, False], [False, False], [True, True], [True, True]], details={"rows": rows}))
    return records
