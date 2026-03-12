# Spec-Driven AI Systems Development

This project follows a **Spec-Driven AI Development** methodology — a structured approach to designing and building AI systems where every component is defined, designed, implemented, and evaluated through a repeatable process.

---

## Why This Methodology

Building AI systems without structure leads to:
- Prompts that "kind of work" but nobody knows why
- Modules that are hard to test or replace
- No way to measure if a change is an improvement

Spec-Driven AI Development treats AI components — prompts, retrievers, agents — with the same engineering rigor as traditional software.

---

## The 7-Step Flow

```
1. Problem Definition
       ↓
2. Specification
       ↓
3. Architecture Design
       ↓
4. AI Component Design
       ↓
5. Implementation
       ↓
6. Evaluation
       ↓
7. Iteration
```

---

### 1. Problem Definition
State clearly what problem the module solves and what the current limitation is.

> Example: *"Current retrieval only uses semantic search. This misses keyword-based matches for exact terms like product codes or proper names."*

### 2. Specification
Define what the system must support — inputs, outputs, and constraints.

> Example:
> - Must support semantic search, keyword search, and hybrid ranking
> - Must return results in under 500ms
> - Must handle Spanish and English queries

### 3. Architecture Design
Define the module structure before writing any code.

> Example:
> ```
> retrieval/
> ├── semantic_retriever.py
> ├── keyword_retriever.py
> └── hybrid_retriever.py
> ```

### 4. AI Component Design
Define the AI-specific elements: models, prompts, embeddings, ranking strategies.

> Example:
> - Embedding model: `all-MiniLM-L6-v2` (384 dims, multilingual-capable)
> - Vector store: ChromaDB with cosine similarity
> - Ranking strategy: weighted fusion (semantic 0.7 + keyword 0.3)

### 5. Implementation
Build following the spec. Use the [Module Design Template](module-design-template.md) for each component.

### 6. Evaluation
Test against defined metrics. Use the [Evaluation Framework](evaluation-framework.md) to score objectively.

> Example metrics: relevance, completeness, accuracy, latency

### 7. Iteration
Use evaluation results to identify the weakest component and improve it. Document what changed and why.

---

## How AI Participates in This Workflow

```
Problem Definition     → Human defines the problem
Specification          → Human + AI brainstorm requirements
Architecture Design    → AI assists with module structure
AI Component Design    → AI suggests models, prompts, strategies
Implementation         → AI-assisted code generation + human review
Evaluation             → Automated LLM-as-judge + human validation
Iteration              → AI generates improved prompt/code versions
```

This reflects how modern AI engineering works: **AI as a collaborator in the development process**, not just the output.

---

## Applied to This Project

| Module | Problem Solved | Key AI Component |
|---|---|---|
| `ingestion` | Raw documents unusable as-is | Chunking strategy (500w, 50 overlap) |
| `embeddings` | Need semantic similarity | MiniLM-L6-v2 embeddings |
| `retrieval` | Structured data not queryable in NL | Text-to-SQL with few-shot prompting |
| `rag` | Context + question → answer | Chain-of-thought system prompt |
| `prompts` | No way to measure prompt quality | LLM-as-judge evaluation loop |
| `agents` | Multiple sources, one interface | Query routing + synthesis |

---

## AI-Assisted Development in This Project

The following components were developed with AI assistance:

- **Architecture brainstorming** — module structure and separation of concerns
- **Code generation** — all Python modules generated and reviewed iteratively
- **Prompt design** — v1 prompts written, v2 improved through evaluation feedback
- **Documentation** — architecture.md, README, this methodology

This is intentional and transparent: the goal is to demonstrate how to work **with AI as an engineering tool**, not around it.
