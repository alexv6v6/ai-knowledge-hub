"""
app.py + routes.py + schemas.py combined
FastAPI REST API for the AI Knowledge Hub.
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
import shutil

# ── Schemas ────────────────────────────────────────────────────────────────────

class AskRequest(BaseModel):
    question: str
    top_k: Optional[int] = 4

class AskResponse(BaseModel):
    answer: str
    doc_sources: List[str]
    sql_query: Optional[str]
    query_type: str

class IngestURLRequest(BaseModel):
    url: str

class StatusResponse(BaseModel):
    documents_indexed: int
    embedding_model: str
    db_schema: str

# ── App ────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="AI Knowledge Hub API",
    description="Hybrid RAG + SQL knowledge system. Ask questions about documents and databases.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lazy-load agent to avoid slow startup
_agent = None

def get_agent():
    global _agent
    if _agent is None:
        from src.agents.knowledge_agent import KnowledgeAgent
        _agent = KnowledgeAgent()
    return _agent

# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "AI Knowledge Hub is running 🧠", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/status", response_model=StatusResponse)
def status():
    return get_agent().status()

@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    try:
        result = get_agent().ask(request.question)
        return AskResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest/url")
def ingest_url(request: IngestURLRequest):
    try:
        chunks = get_agent().ingest(request.url)
        return {"message": f"Ingested {chunks} chunks from URL", "source": request.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest/file")
async def ingest_file(file: UploadFile = File(...)):
    try:
        tmp_path = f"/tmp/{file.filename}"
        with open(tmp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        chunks = get_agent().ingest(tmp_path)
        os.remove(tmp_path)
        return {"message": f"Ingested {chunks} chunks from {file.filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sample-questions")
def sample_questions():
    return {"questions": [
        "What products do we have in stock?",
        "Which customers are from Bogotá?",
        "What were the total sales in January 2024?",
        "Show me the top selling products",
        "What is a RAG system?",
    ]}
