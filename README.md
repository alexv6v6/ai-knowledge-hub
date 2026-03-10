# 🧠 AI Knowledge Hub

> **A modular RAG system that allows users to query document collections and databases using natural language and LLMs.**

Built with **Groq (LLaMA 3.3-70b)**, **ChromaDB**, **HuggingFace Embeddings**, **FastAPI**, and **Streamlit**.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LLaMA%203.3-F55036?style=flat-square&logo=groq&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Store-orange?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.37-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)

---

## Problem

Organizations store knowledge in two places that rarely talk to each other:

- **Unstructured documents** — PDFs, manuals, reports, internal wikis
- **Structured databases** — sales records, inventory, customer data

Finding information requires knowing where to look and how to query it. This system unifies both into a single natural language interface.

---

## Use Cases

- **Internal documentation search** — ask questions about procedures, policies, manuals
- **Business knowledge assistant** — query sales, inventory and customer data in plain language
- **Technical documentation QA** — find answers across multiple technical documents
- **Hybrid analytics** — combine document context with live database figures in one answer

---

## Architecture

```mermaid
flowchart TD
    A[User Query] --> B{Knowledge Agent}

    B --> C[RAG Pipeline]
    B --> D[SQL Pipeline]

    C --> E[Embed Query\nMiniLM-L6-v2]
    E --> F[ChromaDB\nSemantic Search]
    F --> G[Top-K Chunks]

    D --> H[LLM generates SQL\nGroq LLaMA 3.3]
    H --> I[SQLite / PostgreSQL]
    I --> J[Structured Rows]

    G --> K[LLM Synthesis\nGroq LLaMA 3.3]
    J --> K

    K --> L[Answer]
```

**Ingestion pipeline:**

```mermaid
flowchart LR
    A[Documents\nPDF · TXT · URL] --> B[Loader]
    B --> C[Cleaner]
    C --> D[Chunker\n500 words · 50 overlap]
    D --> E[Embeddings\nMiniLM-L6-v2]
    E --> F[ChromaDB\nVector Index]
```

---

## Pipeline

Each query is automatically routed to the right data source:

| Query | Route | Method |
|---|---|---|
| *"What does the manual say about X?"* | Documents | Semantic search → RAG |
| *"How many products are in stock?"* | Database | Text-to-SQL |
| *"Summarize our top customers"* | Both | Combined context |

---

## Quickstart

### 1. Clone & install

```bash
git clone https://github.com/alexv6v6/ai-knowledge-hub.git
cd ai-knowledge-hub

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Add your free Groq API key from console.groq.com:
# GROQ_API_KEY=gsk_...
```

### 3. Run example

```bash
python example_query.py
```

### 4. Run the app

```bash
streamlit run app.py
```

### 4b. Or run the REST API

```bash
uvicorn src.api.app:app --reload
# Swagger docs → http://localhost:8000/docs
```

---

## Example Usage

```python
from src.agents.knowledge_agent import KnowledgeAgent

agent = KnowledgeAgent()

# Ingest documents
agent.ingest("data/raw/documents/manual.pdf")
agent.ingest("https://example.com/article")

# Query documents (RAG)
response = agent.ask("What is the return policy?")
print(response["answer"])
print("Sources:", response["doc_sources"])

# Query database (Text-to-SQL)
response = agent.ask("What products are low on stock?")
print(response["answer"])
print("SQL used:", response["sql_query"])
```

**REST API:**

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Which customers are from Bogotá?"}'
```

---

## Ingest Documents

Drop PDF or TXT files into `data/raw/documents/` then run:

```bash
python scripts/ingest_documents.py
```

Or ingest a URL directly:

```python
agent.ingest("https://example.com/documentation")
```

---

## Project Structure

```
ai-knowledge-hub/
├── src/
│   ├── ingestion/
│   │   ├── document_loader.py   # PDF, TXT, URL loaders
│   │   └── text_cleaner.py      # Clean + chunk text
│   ├── embeddings/
│   │   └── vector_store.py      # ChromaDB + HuggingFace embeddings
│   ├── retrieval/
│   │   └── sql_connector.py     # Text-to-SQL (SQLite / PostgreSQL)
│   ├── rag/
│   │   └── rag_pipeline.py      # Hybrid RAG pipeline
│   ├── agents/
│   │   └── knowledge_agent.py   # Top-level agent (.ask() / .ingest())
│   └── api/
│       └── app.py               # FastAPI REST interface
├── tests/
│   ├── test_ingestion.py
│   └── test_retrieval.py
├── scripts/
│   └── ingest_documents.py      # Bulk ingestion script
├── data/raw/documents/          # Drop PDFs / TXTs here
├── example_query.py             # Runnable demo
├── app.py                       # Streamlit UI
├── architecture.md              # Full system design docs
└── requirements.txt
```

---

## Running Tests

```bash
pytest tests/ -v
```

---

## Database

Uses **SQLite** by default (zero config). Switch to PostgreSQL:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

---

## Related Projects

- [business-ai-agent](https://github.com/alexv6v6/business-ai-agent) — AI business analyst with Groq function calling
- [mini-rag-assistant](https://github.com/alexv6v6/mini-rag-assistant) — RAG prototype with Chroma + LangChain
- [rag-evaluador-modelos](https://github.com/alexv6v6/rag-evaluador-modelos) — LLM evaluation framework
- [api-facturas](https://github.com/alexv6v6/api-facturas) — FastAPI invoice management API

---

## License

MIT
