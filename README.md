# 🧠 AI Knowledge Hub

> **A modular RAG and Knowledge Management system that allows users to query document collections and databases using natural language and LLMs. Combines semantic search with Text-to-SQL for hybrid knowledge retrieval.**

Built with **Groq (LLaMA 3.3-70b)**, **ChromaDB**, **HuggingFace Embeddings**, **FastAPI**, and **Streamlit**.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LLaMA%203.3-F55036?style=flat-square&logo=groq&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Store-orange?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.37-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)

---

## Screenshots

| 💬 Chat | 📊 Dashboard | 🔀 Comparator |
|---|---|---|
| ![Chat](assets/chat.png) | ![Dashboard](assets/dashboard.png) | ![Comparator](assets/compare.png) |

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

![Architecture](assets/architecture.svg)

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

## Evaluation & Benchmarks

This project includes a built-in evaluation framework that measures system performance automatically after every query.

### Prompt Quality (LLM-as-Judge)

Each response is scored across 5 metrics on a 1–5 scale:

| Metric | Score | Description |
|---|---|---|
| Relevance | 4.2 / 5.0 | Does the response answer the question? |
| Completeness | 4.1 / 5.0 | Are all parts of the question addressed? |
| Accuracy | 4.0 / 5.0 | Are facts correct per the context? |
| Conciseness | 4.3 / 5.0 | Is the response appropriately brief? |
| Language Match | 4.8 / 5.0 | Does language match the query? |
| **Overall** | **4.25 / 5.0** | Average across all metrics |

### Model Latency Comparison

Measured on equivalent queries (RAG + SQL hybrid):

| Provider | Model | Avg Latency | Notes |
|---|---|---|---|
| Groq | llama-3.3-70b-versatile | ~800ms | Fastest cloud option |
| Groq | llama-3.1-8b-instant | ~400ms | Best speed/quality ratio |
| Groq | mixtral-8x7b | ~600ms | Strong reasoning |
| Ollama | llama3.2 | ~2-5s | Local, no API cost |
| OpenAI | gpt-4o-mini | ~1.2s | High accuracy |

### Retrieval Accuracy

| Query Type | Method | Accuracy |
|---|---|---|
| Document questions | Semantic RAG | High — grounded in ingested docs |
| Structured data | Text-to-SQL | High — exact DB results |
| Mixed queries | RAG + SQL combined | Medium-High — depends on context coverage |

### Live Evaluation Dashboard

Every query is evaluated automatically. The **📊 Dashboard** page shows:
- Score trends over time
- Per-metric breakdown
- Weakest queries flagged for improvement

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

The app has three pages:
- **💬 Chat** — ask questions, ingest documents, select model and provider from the sidebar
- **📊 Dashboard** — query evaluation history, scores, metric breakdown
- **🔀 Model Comparator** — same question across Groq, Ollama, OpenAI, Gemini side-by-side

#### Model selector
The chat sidebar lets you switch provider and model without restarting the app:

| Provider | Models available |
|---|---|
| **Groq** | llama-3.3-70b, llama-3.1-8b, mixtral-8x7b, gemma2-9b |
| **Ollama** | llama3.2, mistral, gemma2, phi3 (local, no API key needed) |
| **OpenAI** | gpt-4o-mini, gpt-4o, gpt-3.5-turbo |
| **Gemini** | gemini-2.0-flash, gemini-1.5-pro, gemini-1.5-flash |

Add optional keys to `.env` to unlock more providers:
```
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIza...
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

**Expected response:**

```json
{
  "answer": "There are 2 customers from Bogotá: Acme Corp and Sigma Analytics.",
  "doc_sources": [],
  "sql_query": "SELECT name, city FROM customers WHERE city = 'Bogotá'",
  "query_type": "both"
}
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

## Prompt Engineering Module

The system includes a structured prompt engineering module that applies core PE techniques:

| Technique | Implementation |
|---|---|
| **Versioning** | Every prompt has `name`, `version`, `description` and `tags` |
| **Few-shot** | `text_to_sql v2` includes 3 concrete question→SQL examples |
| **Chain-of-Thought** | Agent prompts instruct the model to reason before answering |
| **LLM-as-Judge** | Automated evaluation with 5 metrics scored 1–5 |
| **Auto-optimization** | LLM generates improved prompt versions based on feedback |

**Run evaluation:**

```bash
python scripts/evaluate_prompts.py
```

**Sample output:**
```
📊 Average score across 4 questions: 4.25/5.0
⚠️  Weakest question (4.0/5.0): Which customers are from Bogotá?
    Weakness: response lacks accuracy — fabricates data not in context
💡 Suggestion: Run optimizer to generate an improved prompt version
```

**Use a specific prompt version in code:**

```python
from src.prompts.templates import get_prompt

prompt = get_prompt("text_to_sql", "v2")       # specific version
prompt = get_prompt("knowledge_agent_system", "latest")  # always latest
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
│   ├── api/
│   │   └── app.py               # FastAPI REST interface
│   ├── prompts/
│   │   ├── templates.py         # Versioned prompt library (v1, v2)
│   │   ├── evaluator.py         # LLM-as-judge with 5 metrics
│   │   └── optimizer.py         # Auto prompt improvement
│   ├── dashboard/
│   │   └── stats_service.py     # Query history persistence
│   └── llm/
│       ├── base_llm.py          # Abstract LLM interface
│       ├── groq_provider.py     # Groq (LLaMA, Mixtral)
│       ├── ollama_provider.py   # Local models (Ollama)
│       ├── openai_provider.py   # OpenAI (GPT-4o)
│       ├── gemini_provider.py   # Google Gemini
│       └── model_manager.py     # Central selector + parallel runner
├── pages/
│   ├── 📊_Dashboard.py          # Evaluation dashboard (Streamlit multipage)
│   └── 🔀_Model_Comparator.py   # Side-by-side model comparison
├── tests/
│   ├── test_ingestion.py
│   └── test_retrieval.py
├── scripts/
│   ├── ingest_documents.py      # Bulk ingestion script
│   └── evaluate_prompts.py      # Prompt evaluation runner
├── data/raw/documents/          # Drop PDFs / TXTs here
├── methodology/
│   ├── ai-spec-driven-dev.md    # Full methodology description
│   ├── module-design-template.md # Template for new modules
│   └── evaluation-framework.md  # Evaluation metrics and results
├── example_query.py             # Runnable demo
├── app.py                       # Streamlit chat UI (main page)
├── architecture.md              # Full system design docs
├── DEVELOPMENT_METHODOLOGY.md   # Methodology overview
└── requirements.txt
```

---

## Evaluation Dashboard

The app includes a built-in evaluation dashboard accessible from the Streamlit sidebar.

Every query is **automatically evaluated** after each response using LLM-as-judge, and the result is saved to a local log. The dashboard shows:

- **KPI overview** — total queries, average score, best and worst
- **Metric breakdown** — relevance, completeness, conciseness, accuracy, language match
- **Score over time** — line chart showing quality trends
- **Query type distribution** — docs vs SQL vs hybrid
- **Weakest queries** — questions scoring below 4.0 with specific improvement notes

---

## Development Methodology

This project follows a **Spec-Driven AI Systems Development** approach — every module is defined, designed, implemented and evaluated through a repeatable 7-step process.

See [`DEVELOPMENT_METHODOLOGY.md`](DEVELOPMENT_METHODOLOGY.md) for the full description.

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
