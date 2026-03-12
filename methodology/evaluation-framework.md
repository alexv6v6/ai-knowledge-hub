# Evaluation Framework

This document defines how AI components in this project are evaluated. Every module that involves an LLM — prompts, retrievers, agents — must be evaluated before being considered production-ready.

---

## Evaluation Philosophy

> *"You can't improve what you can't measure."*

AI components are evaluated using **LLM-as-Judge** — a technique where a separate LLM instance scores the output of another LLM against defined criteria. This enables automated, repeatable evaluation without manual labeling.

---

## Metrics

### Response Quality (scored 1–5)

| Metric | Definition | Bad (1-2) | Good (4-5) |
|---|---|---|---|
| **Relevance** | Does the response answer the question? | Off-topic or partially answers | Directly and completely on-point |
| **Completeness** | Are all parts of the question addressed? | Misses major parts | Covers everything asked |
| **Conciseness** | Is the response appropriately brief? | Verbose, repetitive, padded | Precise without losing substance |
| **Accuracy** | Are facts/numbers correct per context? | Fabricates or misquotes data | All figures match the source |
| **Language Match** | Does language match the question? | Wrong language | Perfect language alignment |

**Overall score** = average of the 5 metrics above.

**Target:** ≥ 4.0/5.0 overall for production readiness.

---

## Evaluation Levels

### Level 1 — Quick Check
Run 3-5 representative questions and check overall score.
```bash
python scripts/evaluate_prompts.py
```

### Level 2 — Full Evaluation
Run 10+ questions covering:
- Different query types (document, SQL, hybrid)
- Both languages (Spanish and English)
- Edge cases (empty context, ambiguous questions)

### Level 3 — A/B Comparison
Compare two prompt versions head-to-head on the same question set.
```python
from src.prompts.evaluator import PromptEvaluator

evaluator = PromptEvaluator()
results = evaluator.compare(
    question="What products are low on stock?",
    responses={"v1": response_v1, "v2": response_v2},
    context=context,
    prompt_name="knowledge_agent_system",
)
evaluator.print_comparison(results)
```

---

## Evaluation Results Log

Track results over time to measure improvement.

| Date | Module | Prompt Version | Avg Score | Notes |
|---|---|---|---|---|
| 2026-03-09 | knowledge_agent | v2 | 4.25/5.0 | Initial evaluation — 4 questions |
| — | text_to_sql | v2 | — | Pending full evaluation |
| — | rag_pipeline | v2 | — | Pending full evaluation |

---

## Interpreting Results

| Score Range | Status | Action |
|---|---|---|
| 4.5 – 5.0 | ✅ Excellent | Ship it |
| 4.0 – 4.4 | ✅ Good | Monitor in production |
| 3.5 – 3.9 | ⚠️ Acceptable | Plan improvement |
| 3.0 – 3.4 | ⚠️ Needs work | Run optimizer before shipping |
| < 3.0 | ❌ Poor | Redesign prompt or component |

---

## Running the Optimizer

When a score is below 4.0, run the auto-optimizer:

```python
from src.prompts.optimizer import PromptOptimizer
from src.prompts.templates import get_prompt

optimizer = PromptOptimizer()
current_prompt = get_prompt("knowledge_agent_system", "latest")

# Pass the evaluation result with the lowest score
improved = optimizer.optimize(
    prompt=current_prompt,
    evaluation_result=worst_result,
    poor_examples=["Which customers are from Bogotá?"],
)

print(f"New version: {improved.version}")
print(improved.template)
```

---

## What Good Evaluation Looks Like

A well-evaluated module has:

1. **A test question set** — at least 5 representative questions
2. **Baseline scores** — v1 evaluation documented
3. **Improvement evidence** — v2 scores higher than v1
4. **Iteration log** — what changed and why (in the module design template)
5. **Known limitations** — documented weaknesses that are accepted or planned for improvement

---

## Current System Scores (2026-03-09)

```
knowledge_agent_system v2
─────────────────────────
Q: What products are low on stock?      4.2/5.0
Q: Which customers are from Bogotá?     4.0/5.0  ⚠ fabricates names
Q: What is the total revenue?           4.0/5.0
Q: ¿Qué productos tenemos en inventario? 4.8/5.0

Average: 4.25/5.0  ✅ Good
Weakest area: accuracy when context is sparse
Next action: optimize prompt to enforce "no fabrication" rule
```
