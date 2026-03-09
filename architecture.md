# Architecture — AI Knowledge Hub

## Overview

AI Knowledge Hub is a hybrid knowledge retrieval system that combines two complementary data access patterns:

- **RAG (Retrieval-Augmented Generation)** for unstructured knowledge (PDFs, text files, URLs)
- **Text-to-SQL** for structured data (relational databases)

The agent intelligently routes each query to the appropriate source — or both — and synthesizes a unified response via LLM.

---

## System Architecture

```
                        User Query
                            │
                            ▼
                    ┌───────────────┐
                    │ Knowledge     │
                    │ Agent         │
                    │ (orchestrator)│
                    └──────┬────────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
    ┌──────────────────┐     ┌──────────────────┐
    │   RAG Pipeline   │     │  SQL Pipeline    │
    │                  │     │                  │
    │ query embedding  │     │ NL → SQL via LLM │
    │       ↓          │     │       ↓          │
    │ vector search    │     │ execute query    │
    │       ↓          │     │       ↓          │
    │ top-k chunks     │     │ structured rows  │
    └────────┬─────────┘     └────────┬─────────┘
             │                        │
             └──────────┬─────────────┘
                        ▼
                 ┌─────────────┐
                 │  LLM Groq   │
                 │ (synthesis) │
                 └─────────────┘
                        │
                        ▼
                    Response
```

---

## Module Descriptions

### `src/ingestion/`
Responsible for loading and preparing raw documents.

| File | Responsibility |
|---|---|
| `document_loader.py` | Unified loader for PDF, TXT, and URL sources |
| `text_cleaner.py` | Removes noise, normalizes whitespace |
| `text_chunker.py` | Splits documents into overlapping chunks |

**Flow:** `raw document → text → cleaned text → chunks`

### `src/embeddings/`
Converts text chunks into vector representations.

| File | Responsibility |
|---|---|
| `vector_store.py` | ChromaDB wrapper: add, search, persist |
| `embedding_generator.py` | HuggingFace MiniLM-L6-v2 embeddings |

**Flow:** `chunks → embeddings → ChromaDB index`

### `src/retrieval/`
Retrieves relevant information from both data sources.

| File | Responsibility |
|---|---|
| `semantic_search.py` | Cosine similarity search over vector store |
| `sql_connector.py` | SQLite/PostgreSQL connector + Text-to-SQL |

**Flow:** `query → embedding → top-k chunks` and `query → SQL → rows`

### `src/rag/`
Builds the complete RAG pipeline.

| File | Responsibility |
|---|---|
| `prompt_builder.py` | Constructs context-aware prompts |
| `rag_pipeline.py` | Orchestrates retrieval + LLM synthesis |

**Flow:** `context + question → prompt → LLM → answer`

### `src/agents/`
Top-level agent that exposes a simple `.ask()` interface.

| File | Responsibility |
|---|---|
| `knowledge_agent.py` | Initializes all components, routes queries |

### `src/api/`
FastAPI REST interface.

| Endpoint | Method | Description |
|---|---|---|
| `/ask` | POST | Ask a question |
| `/ingest/url` | POST | Ingest a URL |
| `/ingest/file` | POST | Upload a PDF/TXT |
| `/status` | GET | Knowledge base status |
| `/health` | GET | Health check |

---

## Key Design Decisions

### 1. Direct Groq SDK over LangChain Agent
Using the Groq SDK directly avoids compatibility issues with LangChain's agent output parsers and gives full control over the tool-calling loop.

### 2. Hybrid RAG + SQL routing
A simple keyword classifier routes queries to the appropriate source. SQL keywords (`total`, `count`, `sales`, etc.) trigger the SQL pipeline; all other queries use RAG. Ambiguous queries use both.

### 3. HuggingFace embeddings (free, local)
`sentence-transformers/all-MiniLM-L6-v2` runs locally with no API cost, producing 384-dimensional embeddings with strong semantic performance for English and Spanish.

### 4. ChromaDB with cosine similarity
Persistent ChromaDB with cosine similarity provides fast approximate nearest neighbor search without requiring a separate vector database service.

### 5. SQLite as default, PostgreSQL-compatible
SQLite works out of the box for demos and development. The `SQLConnector` is designed to support PostgreSQL via `DATABASE_URL` environment variable for production use.

---

## Data Flow

```
Documents (PDF/TXT/URL)
        ↓
    Loading
        ↓
    Cleaning
        ↓
    Chunking (500 words, 50 overlap)
        ↓
    Embedding (MiniLM-L6-v2, 384 dims)
        ↓
    ChromaDB Index
        ↓
    Semantic Search (cosine similarity)
        ↓
    Top-K Chunks + SQL Results
        ↓
    Prompt Builder
        ↓
    Groq LLM (LLaMA 3.3-70b)
        ↓
    Response
```

---

## Technology Stack

| Component | Technology | Reason |
|---|---|---|
| LLM | Groq + LLaMA 3.3-70b | Free tier, fast inference |
| Embeddings | HuggingFace MiniLM-L6-v2 | Free, runs locally |
| Vector DB | ChromaDB | Simple, persistent, no server needed |
| SQL DB | SQLite / PostgreSQL | Universal, zero config for demos |
| API | FastAPI | Auto docs, async, typed |
| UI | Streamlit | Fast prototyping, Python-native |
