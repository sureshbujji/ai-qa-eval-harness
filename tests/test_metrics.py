import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from metrics import (
    pass_rate,
    category_breakdown,
    severity_weighted_score,
    hallucination_escape_estimate,
    summary,
)

SAMPLE = [
    {"id": "faith-001", "category": "faithfulness", "severity": "high", "score": 5, "passed": True},
    {"id": "faith-002", "category": "faithfulness", "severity": "medium", "score": 3, "passed": False},
    {"id": "hall-001", "category": "hallucination", "severity": "critical", "score": 1, "passed": False},
    {"id": "hall-002", "category": "hallucination", "severity": "critical", "score": 5, "passed": True},
]


def test_pass_rate():
    assert pass_rate(SAMPLE) == 0.5
    assert pass_rate([]) == 0.0


def test_category_breakdown():
    b = category_breakdown(SAMPLE)
    assert b["faithfulness"] == {"total": 2, "passed": 1, "pass_rate": 0.5}
    assert b["hallucination"]["total"] == 2


def test_severity_weighted_score():
    # (5*3 + 3*2 + 1*5 + 5*5) / (3+2+5+5) = 51/15 = 3.4
    assert severity_weighted_score(SAMPLE) == 3.4
    assert severity_weighted_score([]) == 0.0


def test_hallucination_escape_estimate():
    # one critical (weight 5) failed out of two critical (weight 10) -> 0.5
    assert hallucination_escape_estimate(SAMPLE) == 0.5
    assert hallucination_escape_estimate([]) == 0.0


def test_summary_shape():
    s = summary(SAMPLE)
    assert s["total"] == 4 and s["passed"] == 2 and s["pass_rate"] == 0.5
    assert "by_category" in s
