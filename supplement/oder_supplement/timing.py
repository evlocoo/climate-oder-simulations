"""Timing, acquisition, and schedule checks."""

from __future__ import annotations

from collections import defaultdict
from math import inf

from .finite import hhmm, minutes


def heat_timing_rows():
    query = 15
    target = 30
    rows = []
    for label in ("10:00", "10:30", "11:00", "11:15", "11:30"):
        t = minutes(label)
        query_finish = t + query + target
        rows.append(
            {
                "decision_point": label,
                "common_plan_available": t <= minutes("10:30"),
                "targeted_plan_available": t <= minutes("11:30"),
                "query_target_completion": hhmm(query_finish),
                "query_route_timely": query_finish <= minutes("12:00"),
            }
        )
    return rows


def latest_recovery_start(query_minutes=15, action_minutes=30, deadline="12:00"):
    return minutes(deadline) - query_minutes - action_minutes


def latest_send_times(edges, terminal, terminal_deadline):
    """Backward recurrence for a contact DAG with freely available holding memory."""
    outgoing = defaultdict(list)
    nodes = {terminal}
    for edge in edges:
        outgoing[edge["u"]].append(edge)
        nodes.add(edge["u"])
        nodes.add(edge["v"])
    latest = {node: -inf for node in nodes}
    latest[terminal] = terminal_deadline
    changed = True
    while changed:
        changed = False
        for u in list(nodes):
            feasible = []
            for edge in outgoing.get(u, []):
                downstream = latest[edge["v"]]
                if downstream == -inf:
                    continue
                send = min(edge["end"], downstream - edge["duration"])
                if send >= edge["start"]:
                    feasible.append(send)
            if feasible and max(feasible) > latest[u]:
                latest[u] = max(feasible)
                changed = True
    return latest


def enumerate_two_edge_schedule():
    edges = (
        {"u": "A", "v": "B", "start": minutes("09:50"), "end": minutes("10:00"), "duration": 5},
        {"u": "B", "v": "C", "start": minutes("10:10"), "end": minutes("10:20"), "duration": 4},
    )
    latest = latest_send_times(edges, "C", minutes("11:00"))
    constructed = {
        "A_send": minutes("10:00"),
        "B_receives": minutes("10:05"),
        "B_forward": minutes("10:10"),
        "C_receives": minutes("10:14"),
    }
    reset_without_storage_blocks = constructed["B_receives"] < minutes("10:07") < constructed["B_forward"]
    return {"latest": latest, "constructed": constructed, "reset_without_storage_blocks": reset_without_storage_blocks}


def enumerate_path_schedules(edges, source, terminal, start_time, terminal_deadline, resets=None, protected_storage=False):
    """Enumerate integer-minute schedules over a small contact graph.

    Contacts and terminal deadlines are inclusive. A reset at a node erases
    unprotected information if receipt occurs at or before the reset and the
    next send is strictly after the reset. Receipt and send at the reset minute
    are treated as an immediate handoff before erasure.
    """
    resets = resets or {}
    outgoing = defaultdict(list)
    for edge in edges:
        outgoing[edge["u"]].append(edge)
    feasible = []

    def blocked_by_reset(node, receipt, send):
        if protected_storage:
            return False
        for reset in resets.get(node, ()):
            if receipt <= reset < send:
                return True
        return False

    def dfs(node, current_time, path):
        if node == terminal:
            if current_time <= terminal_deadline:
                feasible.append(tuple(path))
            return
        for edge in outgoing.get(node, []):
            earliest_send = max(current_time, edge["start"])
            latest_send = min(edge["end"], terminal_deadline - edge["duration"])
            for send in range(earliest_send, latest_send + 1):
                if blocked_by_reset(node, current_time, send):
                    continue
                arrival = send + edge["duration"]
                dfs(edge["v"], arrival, path + [{"edge": (edge["u"], edge["v"]), "send": send, "arrival": arrival}])

    dfs(source, start_time, [])
    return feasible


def schedule_verification_cases():
    base_edges = (
        {"u": "A", "v": "B", "start": minutes("09:50"), "end": minutes("10:00"), "duration": 5},
        {"u": "B", "v": "C", "start": minutes("10:10"), "end": minutes("10:20"), "duration": 4},
    )
    unavailable_edges = (
        {"u": "A", "v": "B", "start": minutes("09:50"), "end": minutes("09:54"), "duration": 5},
        {"u": "B", "v": "C", "start": minutes("10:10"), "end": minutes("10:20"), "duration": 4},
    )
    boundary_edges = (
        {"u": "A", "v": "B", "start": minutes("10:00"), "end": minutes("10:00"), "duration": 5},
        {"u": "B", "v": "C", "start": minutes("10:05"), "end": minutes("10:05"), "duration": 4},
    )
    cases = {}
    for name, edges, deadline, resets, storage in (
        ("free_holding_memory", base_edges, minutes("11:00"), {}, False),
        ("unavailable_route", unavailable_edges, minutes("10:13"), {}, False),
        ("reset_without_storage", base_edges, minutes("11:00"), {"B": (minutes("10:07"),)}, False),
        ("reset_with_storage_repair", base_edges, minutes("11:00"), {"B": (minutes("10:07"),)}, True),
        ("boundary_receipt_and_send", boundary_edges, minutes("10:09"), {}, False),
    ):
        recurrence = latest_send_times(edges, "C", deadline)
        schedules = enumerate_path_schedules(edges, "A", "C", minutes("09:45"), deadline, resets=resets, protected_storage=storage)
        cases[name] = {
            "recurrence_latest": recurrence,
            "enumerated_schedule_count": len(schedules),
            "enumerated_feasible": bool(schedules),
            "recurrence_feasible": recurrence.get("A", -inf) != -inf,
            "first_schedule": schedules[0] if schedules else None,
            "assumptions": {
                "integer_minute_grid": True,
                "inclusive_windows": True,
                "protected_storage": storage,
                "resets": resets,
            },
        }
    return cases


def message_timing(bits, rate_bits_per_minute, channel_close, encoding_latest=inf):
    duration = bits / rate_bits_per_minute
    latest = min(encoding_latest, channel_close - duration)
    return latest
