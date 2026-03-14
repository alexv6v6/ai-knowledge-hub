# Document Preparation SOP for RAG Systems
## Procedimiento Estándar de Preparación de Documentos para RAG

## Scope / Alcance

This SOP is intended for teams building RAG-based knowledge systems. It standardizes how documents must be prepared before indexing into a vector database. Following this procedure ensures consistent retrieval quality across different document types and domains.

Este SOP está dirigido a equipos que construyen sistemas de conocimiento basados en RAG. Estandariza cómo deben prepararse los documentos antes de indexarlos en una base de datos vectorial. Seguir este procedimiento garantiza una calidad de recuperación consistente en diferentes tipos de documentos y dominios.

---

> This SOP defines a practical methodology derived from internal testing and practical RAG implementations, comparing 5 document versions across 2 embedding models and 3 retriever strategies.
>
> Este SOP define una metodología práctica derivada de pruebas internas e implementaciones prácticas de RAG, comparando 5 versiones de documentos con 2 modelos de embeddings y 3 estrategias de recuperación.

---

## The 5-Step Pipeline / El Pipeline de 5 Pasos

```
Raw Document
     ↓
01 · Plain Text Conversion
     ↓
02 · Section Structuring
     ↓
03 · Text Normalization
     ↓
04 · Metadata Enrichment      ← highest impact step
     ↓
05 · Semantic Chunking
     ↓
Vector Index (ChromaDB)
```

---

## Step 01 — Plain Text Conversion / Conversión a Texto Plano

**What:** Convert the source document (PDF, Word, HTML) to `.txt`.

**Why:** PDFs contain embedded fonts, misaligned tables, and hidden characters that degrade embedding quality silently.

**How:**
- Use a reliable PDF extraction tool (avoid OCR unless the document is scanned)
- Do not re-wrap lines — preserve original paragraph structure
- Verify all sections of the source document appear in the output

**Success criterion:** The `.txt` contains all original content with no broken lines, encoding errors, or stray symbols.

---

## Step 02 — Section Structuring / Estructuración en Secciones

**What:** Organize the document with explicit section headers so the chunker produces semantically coherent fragments.

**Why:** Chunks must have unique, unambiguous semantics. A section mixing two topics produces chunks the retriever cannot discriminate.

**How:**
- Identify the natural sections of the document (chapters, procedures, requirements)
- Add explicit UPPERCASE headers for each section (e.g., `SECTION 1: WATER CONCESSION REQUIREMENTS`)
- Remove bullet points — convert to numbered lists or plain prose
- Remove special characters, decorative elements, and redundant whitespace
- Split any section that covers more than one topic into sub-sections

**Success criterion:** Each section covers exactly one topic or procedure and has a clear uppercase header.

---

## Step 03 — Text Normalization / Normalización del Texto

**What:** Normalize the text to improve embedding consistency.

**Why:** Reduces vocabulary fragmentation in the embedding space. Empirically improved Context Precision from 0.617 → 0.670 (+8.6%) with all-MiniLM-L6-v2.

**How:**
- Convert all text to lowercase
- Remove repeated page headers and footers
- Standardize punctuation (fix double spaces, inconsistent hyphens)
- Preserve technical terms and acronyms in their standard form

**Success criterion:** The document contains no uppercase except section headers.

---

## Step 04 — Metadata Enrichment / Enriquecimiento con Metadatos

**What:** Attach structured metadata to every chunk before indexing.

**Why:** This is the highest-impact step. Empirical results:
- Without metadata: **0% of retriever configurations** recovered the expected context
- With metadata: **100% of retriever configurations** recovered the expected context

**Metadata schema:**

```json
{
  "section":       "section name / nombre de la sección",
  "section_path":  "parent > child > section (e.g. Procedures > Water > Requirements)",
  "keywords":      ["term1", "term2", "term3"],
  "process":       "business process name / nombre del proceso",
  "doc_id":        "source document ID / ID del documento",
  "source":        "file path or URL of the original document",
  "language":      "es",
  "version":       "2024-v1",
  "created_at":    "2024-01-15T10:00:00Z"
}
```

**Field reference:**

| Field | Required | Description |
|---|---|---|
| `section` | Yes | Name of the section this chunk belongs to |
| `section_path` | Yes | Full hierarchical path (e.g. `Manual > Chapter 2 > Requirements`) |
| `keywords` | Yes | Key terms specific to this chunk — not the whole document |
| `process` | Yes | Business process this chunk supports |
| `doc_id` | Yes | Unique identifier of the source document |
| `source` | Yes | File path or URL of the original document |
| `language` | Yes | Content language (`es`, `en`, etc.) |
| `version` | Yes | Document version |
| `created_at` | Recommended | ISO 8601 timestamp of when the chunk was indexed |

**Rules:**
- All required fields must be populated — no partial metadata
- `keywords` must reflect the specific terminology of each chunk, not the document as a whole
- `section_path` enables filtering by document hierarchy in the retriever
- `source` enables traceability — users can always find the original document
- `created_at` enables cache invalidation and version management
- The schema must be consistent across all documents in the knowledge base

**Success criterion:** Every chunk has all required metadata fields populated with chunk-specific values.

---

## Step 05 — Semantic Chunking / Fragmentación Semántica

**What:** Split the enriched document into semantically coherent chunks and index them.

**Why:** Fixed-size chunking breaks semantic units. A chunk starting mid-procedure lacks sufficient context for accurate retrieval.

**How:**
- Use semantic chunking (split by topic coherence, not fixed character count)
- Target chunk size: **300–600 words**
- Overlap: **10–15%** between adjacent chunks to preserve boundary context
- Never split a numbered list or step-by-step procedure across chunks
- Index metadata alongside the vector embedding in ChromaDB

**Success criterion:** Each chunk is self-contained — it can be read independently and its topic is immediately clear.

---

## Validation Checklist / Lista de Verificación

Run this checklist before indexing any document into production.

```
DOCUMENT PREPARATION
□ Source document converted to .txt with no encoding errors
□ All original content preserved in the .txt output
□ Each section has an explicit UPPERCASE header
□ No section mixes more than one topic
□ Bullet points removed or converted to prose/numbered lists
□ All text converted to lowercase
□ Repeated headers/footers removed

METADATA
□ Every chunk has all 9 metadata fields populated
□ section_path reflects the full document hierarchy
□ keywords reflect the specific terminology of each chunk
□ source points to the original file or URL
□ created_at is set to the indexing timestamp
□ Metadata schema is consistent with all other documents in the knowledge base

CHUNKING & INDEXING
□ Semantic chunking applied (not fixed-size)
□ Chunk size between 300–600 words
□ 10–15% overlap between adjacent chunks
□ No numbered lists or procedures split across chunks
□ All chunks indexed in ChromaDB with metadata

RETRIEVER VALIDATION
□ At least 5 representative test queries defined
□ All test queries return relevant chunks in top results
□ No test query returns zero results
□ Retriever configuration documented (search_type, k, fetch_k, lambda_mult or score_threshold)
```

---

## Empirical Results Summary / Resumen de Resultados Empíricos

### Document Format Impact (all-MiniLM-L6-v2)

| Document Version | Context Precision | Retrieval Quality |
|---|---|---|
| Original plain text | 0.617 | 0.475 |
| Organized (sections) | 0.628 | 0.548 |
| Organized + lowercase | 0.670 | 0.550 |
| **Organized + metadata** | **0.680** | **0.652** |

### Document Format Impact (intfloat/multilingual-e5-small)

| Document Version | Context Precision | Retrieval Quality |
|---|---|---|
| Original plain text | 0.864 | 0.858 |
| Organized (sections) | 0.863 | 0.867 |
| Organized + lowercase | 0.858 | 0.872 |
| **Organized + metadata** | **0.862** | **0.867** |

### Retriever Configurations — Recommended

| Strategy | Parameters | Context Precision | Retrieval Quality |
|---|---|---|---|
| MMR | k=2, fetch_k=5, lambda=0.5 | 0.721 / 0.869 | 0.701 / 0.896 |
| MMR | k=3, fetch_k=8, lambda=0.5 | 0.687 / 0.869 | 0.639 / 0.896 |
| Similarity threshold | k=5, score≥0.5 | 0.721 / 0.867 | 0.701 / 0.882 |

*Values: all-MiniLM-L6-v2 / intfloat/multilingual-e5-small*

---

## Embedding Model Selection Guide

| Condition | Recommended Model |
|---|---|
| Spanish or multilingual documents | `intfloat/multilingual-e5-small` |
| Technical / administrative terminology | `intfloat/multilingual-e5-small` |
| English-only, general domain | `all-MiniLM-L6-v2` |
| Low resource environment | `all-MiniLM-L6-v2` |
| Production system, accuracy critical | `intfloat/multilingual-e5-small` |
