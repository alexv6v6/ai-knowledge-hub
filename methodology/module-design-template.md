# Module Design Template

Use this template before implementing any new module. Fill in all sections before writing code.

---

## Module: [Module Name]

**Date:** YYYY-MM-DD  
**Author:** [Name]  
**Status:** `draft` | `approved` | `implemented` | `evaluated`

---

### 1. Problem Definition

> What problem does this module solve?  
> What is the current limitation or gap?

```
[Describe the problem in 2-3 sentences]
```

---

### 2. Specification

**Inputs:**
```
- [Input 1]: [type and description]
- [Input 2]: [type and description]
```

**Outputs:**
```
- [Output 1]: [type and description]
- [Output 2]: [type and description]
```

**Constraints:**
```
- [Performance constraint, e.g. latency < 500ms]
- [Language support, e.g. Spanish and English]
- [Data constraint, e.g. max chunk size 500 words]
```

---

### 3. Architecture Design

**File structure:**
```
src/[module_name]/
├── __init__.py
├── [component_1].py    # [brief description]
└── [component_2].py    # [brief description]
```

**Dependencies:**
```
- [Library/module this depends on]
- [External API or service]
```

---

### 4. AI Component Design

**Model(s) used:**
```
- [Model name]: [purpose, e.g. "all-MiniLM-L6-v2 for generating 384-dim embeddings"]
```

**Prompt strategy:**
```
- Technique: [zero-shot | few-shot | chain-of-thought | RAG]
- Version: v1.0
- Key instructions: [describe the main rules given to the LLM]
```

**Vector/data strategy:**
```
- Storage: [ChromaDB | PostgreSQL | SQLite | in-memory]
- Similarity: [cosine | euclidean | dot product]
- Top-K: [number of results to retrieve]
```

---

### 5. Implementation Notes

> Any important decisions made during implementation.  
> Deviations from the spec and why.

```
[Notes here]
```

---

### 6. Evaluation Plan

**Test questions / cases:**
```
1. [Question or test case]
2. [Question or test case]
3. [Question or test case]
```

**Metrics to track:**

| Metric | Target | Method |
|---|---|---|
| Relevance | ≥ 4.0/5.0 | LLM-as-judge |
| Completeness | ≥ 4.0/5.0 | LLM-as-judge |
| Accuracy | ≥ 4.0/5.0 | LLM-as-judge |
| Latency | < 3s | Timer |

**Evaluation script:**
```bash
python scripts/evaluate_prompts.py
```

---

### 7. Iteration Log

| Version | Change | Score Before | Score After | Date |
|---|---|---|---|---|
| v1.0 | Initial implementation | — | [score] | [date] |
| v1.1 | [What changed] | [before] | [after] | [date] |

---

## Example: Hybrid Retrieval Module

### 1. Problem Definition
```
Current retrieval only uses semantic search via ChromaDB.
This misses keyword-based matches for exact terms like product codes,
proper names, or technical identifiers.
```

### 2. Specification
```
Inputs:  user query (string), top_k (int, default 5)
Outputs: ranked list of document chunks with scores

Constraints:
- Must support Spanish and English
- Must combine semantic + keyword scores
- Latency < 500ms for queries under 100 words
```

### 3. Architecture Design
```
src/retrieval/
├── semantic_retriever.py    # existing ChromaDB search
├── keyword_retriever.py     # BM25 keyword search
└── hybrid_retriever.py      # weighted fusion of both
```

### 4. AI Component Design
```
Embedding model: all-MiniLM-L6-v2 (semantic leg)
Keyword model:   BM25 (rank_bm25 library)
Ranking:         weighted fusion — semantic 0.7, keyword 0.3
```

### 6. Evaluation Plan
```
Test questions:
1. "AI Chatbot Module" (exact keyword match)
2. "What products help with automation?" (semantic match)
3. "CRM" (acronym — tests keyword retrieval)

Target: relevance ≥ 4.2/5.0 (improvement over current 4.0)
```
