# 🧠 AI Knowledge Hub

> **A hybrid knowledge retrieval system combining RAG (documents) and Text-to-SQL (databases) — ask questions in natural language and get answers backed by real data.**

Built with **Groq (LLaMA 3.3-70b)**, **ChromaDB**, **HuggingFace Embeddings**, **FastAPI**, and **Streamlit**. The agent automatically routes each query to the right data source — documents, database, or both.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LLaMA%203.3-F55036?style=flat-square&logo=groq&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Store-orange?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.37-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)

---

## 🎯 What Makes This Different

Most RAG systems only search documents. This system has **two knowledge sources** that work together:

| Source | Type | Used for |
|---|---|---|
| ChromaDB | Vector store | PDFs, text files, URLs |
| SQLite / PostgreSQL | Relational DB | Structured business data |

The agent classifies each query and routes it automatically:

```
"What is a RAG system?"           → Document search (semantic)
"How many products are in stock?" → SQL query (structured)
"Summarize our top customers"     → Both sources combined
```

---

## 🏗 Architecture

```
User Query
    │
    ▼
Knowledge Agent
    │
    ├──── RAG Pipeline ────────────────────────────────┐
    │     query → embedding → ChromaDB → top-k chunks │
    │                                                  │
    └──── SQL Pipeline ────────────────────────────────┤
          query → LLM → SQL → database → rows         │
                                                       │
                        LLM synthesizes final answer ←─┘
```

See [architecture.md](architecture.md) for full module documentation.

---

## 🚀 Quickstart

### 1. Clone & install

```bash
git clone https://github.com/alexv6v6/ai-knowledge-hub.git
cd ai-knowledge-hub

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Add your Groq API key (free at console.groq.com):
# GROQ_API_KEY=gsk_...
```

### 3. Run the Streamlit app

```bash
streamlit run app.py
```

### 3b. Or run the REST API

```bash
uvicorn src.api.app:app --reload
# Swagger docs at http://localhost:8000/docs
```

---

## 📁 Project Structure

```
ai-knowledge-hub/
├── src/
│   ├── ingestion/
│   │   ├── document_loader.py   # PDF, TXT, URL loaders
│   │   └── text_cleaner.py      # Clean + chunk text
│   ├── embeddings/
│   │   └── vector_store.py      # ChromaDB + HuggingFace embeddings
│   ├── retrieval/
│   │   └── sql_connector.py     # SQLite/PostgreSQL + Text-to-SQL
│   ├── rag/
│   │   └── rag_pipeline.py      # Hybrid RAG pipeline
│   ├── agents/
│   │   └── knowledge_agent.py   # Top-level agent (.ask(), .ingest())
│   └── api/
│       └── app.py               # FastAPI REST interface
├── tests/
│   ├── test_ingestion.py        # Unit tests for ingestion pipeline
│   └── test_retrieval.py        # Unit tests for SQL connector
├── scripts/
│   └── ingest_documents.py      # Bulk ingestion script
├── data/
│   └── raw/documents/           # Drop PDFs/TXTs here
├── app.py                       # Streamlit UI
├── architecture.md              # System design documentation
├── requirements.txt
└── .env.example
```

---

## 💡 Usage Examples

### Python API

```python
from src.agents.knowledge_agent import KnowledgeAgent

agent = KnowledgeAgent()

# Ingest a document
agent.ingest("data/raw/documents/report.pdf")
agent.ingest("https://example.com/article")

# Ask questions
result = agent.ask("What were the key findings in the report?")
print(result["answer"])
print("Sources:", result["doc_sources"])

# Query the database
result = agent.ask("Which products are low on stock?")
print(result["answer"])
print("SQL used:", result["sql_query"])
```

### REST API

```bash
# Ask a question
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What products do we have in stock?"}'

# Ingest a URL
curl -X POST http://localhost:8000/ingest/url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/article"}'
```

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

---

## 🗄️ Database Configuration

By default the system uses **SQLite** (zero config). To use PostgreSQL:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/yourdb
```

The demo database includes sample tables: `products`, `sales`, `customers`.

---

## 🔗 Related Projects

- [business-ai-agent](https://github.com/alexv6v6/business-ai-agent) — AI business analyst with Groq + LangChain
- [mini-rag-assistant](https://github.com/alexv6v6/mini-rag-assistant) — RAG prototype with Chroma + LangChain
- [rag-evaluador-modelos](https://github.com/alexv6v6/rag-evaluador-modelos) — LLM evaluation framework
- [api-facturas](https://github.com/alexv6v6/api-facturas) — FastAPI invoice management API

---

## 📄 License

MIT
