"""Computed verification records and failure reporting."""

from __future__ import annotations

def make_record(case, domain, actual, independent, expected_agreement=True, details=None, skipped=False, exception=None):
    if skipped or exception is not None:
        agree = False
    else:
        agree = actual == independent
    passed = bool(agree == expected_agreement and not skipped and exception is None)
    return {
        "case": case,
        "domain": domain,
        "actual_result": actual,
        "independent_result": independent,
        "expected_agreement": expected_agreement,
        "agree": agree,
        "passed": passed,
        "skipped": skipped,
        "exception": exception,
        "details": details or {},
    }


def summarize_records(records, run_id=None):
    records = list(records)
    failures = [r for r in records if not r.get("passed")]
    summary = {
        "record_count": len(records),
        "pass_count": len(records) - len(failures),
        "failure_count": len(failures),
        "failures": failures,
        "records": records,
    }
    if run_id is not None:
        summary["run_id"] = run_id
    return summary


def assert_no_failures(summary):
    if summary["failure_count"]:
        raise SystemExit(1)

