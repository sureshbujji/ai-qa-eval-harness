"""Aggregate metrics for AI QA evaluation runs.

Pure functions: take a list of per-case result dicts and return computed
metrics. A result dict is expected to look like:

    {"id": "faith-001", "category": "faithfulness", "severity": "high",
     "score": 4, "passed": True, "error": None}
"""

from collections import defaultdict

PASS_SCORE = 4  # scores >= 4 on the 1-5 rubric count as passing
SEVERITY_WEIGHTS = {"low": 1, "medium": 2, "high": 3, "critical": 5}


def pass_rate(results):
    """Fraction of cases that passed (0.0 - 1.0)."""
    if not results:
        return 0.0
    return sum(1 for r in results if r.get("passed")) / len(results)


def category_breakdown(results):
    """Per-category {total, passed, pass_rate}."""
    totals = defaultdict(int)
    passed = defaultdict(int)
    for r in results:
        cat = r.get("category", "unknown")
        totals[cat] += 1
        if r.get("passed"):
            passed[cat] += 1
    return {
        cat: {
            "total": totals[cat],
            "passed": passed[cat],
            "pass_rate": passed[cat] / totals[cat] if totals[cat] else 0.0,
        }
        for cat in totals
    }


def severity_weighted_score(results):
    """Mean score weighted by severity; weights: low=1, medium=2, high=3, critical=5."""
    total_weight, weighted_sum = 0.0, 0.0
    for r in results:
        if r.get("score") is None:
            continue
        w = SEVERITY_WEIGHTS.get(r.get("severity"), 1)
        total_weight += w
        weighted_sum += r["score"] * w
    if not total_weight:
        return 0.0
    return round(weighted_sum / total_weight, 2)


def hallucination_escape_estimate(results):
    """Estimated share of hallucination cases that slipped through (failed).

    A hallucination 'escape' is a failed hallucination-detection case,
    weighted by severity. Returns a 0.0-1.0 estimate.
    """
    hall = [r for r in results if r.get("category") == "hallucination"]
    if not hall:
        return 0.0
    esc_w = sum(SEVERITY_WEIGHTS.get(r.get("severity"), 1) for r in hall if not r.get("passed"))
    tot_w = sum(SEVERITY_WEIGHTS.get(r.get("severity"), 1) for r in hall)
    return round(esc_w / tot_w, 3) if tot_w else 0.0


def summary(results):
    """One dict with all aggregate metrics."""
    return {
        "total": len(results),
        "passed": sum(1 for r in results if r.get("passed")),
        "pass_rate": round(pass_rate(results), 3),
        "severity_weighted_score": severity_weighted_score(results),
        "hallucination_escape_estimate": hallucination_escape_estimate(results),
        "by_category": category_breakdown(results),
    }


if __name__ == "__main__":
    # Small self-test with synthetic results.
    sample = [
        {"id": "faith-001", "category": "faithfulness", "severity": "high", "score": 5, "passed": True},
        {"id": "faith-002", "category": "faithfulness", "severity": "medium", "score": 3, "passed": False},
        {"id": "hall-001", "category": "hallucination", "severity": "critical", "score": 1, "passed": False},
        {"id": "hall-002", "category": "hallucination", "severity": "critical", "score": 5, "passed": True},
    ]
    s = summary(sample)
    assert s["total"] == 4
    assert s["passed"] == 2
    assert s["pass_rate"] == 0.5
    assert s["by_category"]["faithfulness"]["pass_rate"] == 0.5
    # weighted: (5*3 + 3*2 + 1*5 + 5*5) / (3+2+5+5) = 51/15 = 3.4
    assert s["severity_weighted_score"] == 3.4
    # hallucination escape: critical weight 5 failed out of 10 total = 0.5
    assert s["hallucination_escape_estimate"] == 0.5
    print("metrics self-test OK:", s)
