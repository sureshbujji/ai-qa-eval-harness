# AI QA Evaluation Harness

[![eval-gate](https://github.com/sureshbujji/Sureshbujji/actions/workflows/eval-gate.yml/badge.svg)](https://github.com/sureshbujji/Sureshbujji/actions/workflows/eval-gate.yml)
![python](https://img.shields.io/badge/python-3.10%2B-blue)

A lightweight, LLM-as-judge evaluation harness for AI systems — the kind of release-gate tooling I run in CI to keep AI defects from escaping to production.

## Architecture

```
golden datasets → LLM-as-judge → CI gates → production monitoring
```

1. **Golden datasets** — 30 curated test cases (`datasets/golden_sample.jsonl`) across five risk categories: faithfulness, hallucination detection, prompt-injection/red-team, RAG retrieval relevance, and tone/safety guardrails.
2. **LLM-as-judge** — `src/evaluator.py` generates a candidate answer from the system under test, then scores it 1–5 against a per-category rubric with named criteria. Scores ≥ 4 pass.
3. **CI gates** — `.github/workflows/eval-gate.yml` runs the suite on every push/PR. The build fails if the pass rate drops below 80% **or if any critical-severity case fails** (`--fail-on-critical`) — a single prompt-injection or hallucination escape blocks the release. No API key? The pipeline runs in mock mode so the gate mechanics are still exercised.
4. **Production monitoring** — the same metrics (`pass rate`, `severity-weighted score`, `hallucination escape estimate`) are designed to be recomputed from production samples to track drift between releases.

## Quickstart

```bash
git clone https://github.com/sureshbujji/Sureshbujji.git
cd ai-qa-eval-harness
pip install -r requirements.txt

# 1) Smoke test — no API key needed (mock mode)
python src/evaluator.py --mock

# 2) Real run — point at any OpenAI-compatible endpoint
cp .env.example .env   # fill in your key; never commit it
export $(cat .env | xargs)
python src/evaluator.py

# 3) Unit tests
pytest
```

Alternatively, run the same dataset through [promptfoo](https://promptfoo.dev):

```bash
npx promptfoo@latest eval -c promptfooconfig.yaml
```

## Sample output

```
Running 30 cases (mock mode)...
Report: reports/eval_report.json
Summary: reports/eval_summary.md
Pass rate: 63.3% (threshold 80%)
CRITICAL: 3 critical-severity case(s) failed: hall-001, red-002, guard-003
FAIL: pass rate below threshold
FAIL: critical-severity escape(s) block release
```

`reports/eval_summary.md` renders a per-category breakdown table plus the failed-case list — the artifact I review before any AI model or prompt change ships. The exit code is non-zero, so CI blocks the release.

## Metrics

- **Pass rate** — share of cases scoring ≥ 4/5.
- **Severity-weighted score** — mean score weighted by severity (low=1, medium=2, high=3, critical=5).
- **Hallucination escape estimate** — severity-weighted share of hallucination cases that failed; a proxy for defect escapes.

## Roadmap

- [ ] 300+ case golden dataset with versioning and case-level ownership
- [ ] Embedding-drift checks for RAG retrieval (flag chunk drift > threshold)
- [ ] Production sampler: score a random slice of live traffic weekly, alert on drift
- [ ] Judge-model calibration: human-agreement rate on a held-out set
- [ ] Dashboard (per-release trend of pass rate / escape estimate)

## License

MIT — see [LICENSE](LICENSE).
