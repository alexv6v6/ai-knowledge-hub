"""
rag_pipeline.py
Core RAG pipeline: retrieves context from documents OR database,
then synthesizes a response using the LLM.
"""
import os
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are an expert AI Knowledge Assistant with access to two data sources:
1. A document knowledge base (RAG) — contains unstructured knowledge from PDFs, text files and URLs
2. A SQL database — contains structured business data (products, sales, customers)

When answering:
- Use the provided context to give accurate, grounded answers
- Cite the source when referencing documents (e.g. "According to [filename]...")
- For database results, present data clearly with numbers and structure
- If context is insufficient, say so clearly
- Respond in the same language as the user (Spanish or English)
- Be concise and actionable"""


def build_prompt(question: str, doc_context: List[Dict], sql_context: str = None) -> str:
    """Build the final prompt combining document and SQL context."""
    parts = [f"Question: {question}\n"]

    if doc_context:
        parts.append("=== Document Context ===")
        for i, chunk in enumerate(doc_context, 1):
            source = chunk["metadata"].get("source", "unknown")
            parts.append(f"[{i}] Source: {source}\n{chunk['content']}\n")

    if sql_context:
        parts.append("=== Database Results ===")
        parts.append(sql_context)

    parts.append("\nAnswer based on the context above:")
    return "\n".join(parts)


class RAGPipeline:
    def __init__(self, vector_store=None, embedding_gen=None, sql_connector=None, llm_client=None):
        self.vector_store    = vector_store
        self.embedding_gen   = embedding_gen
        self.sql_connector   = sql_connector
        self.llm_client      = llm_client

    def _classify_query(self, question: str) -> str:
        """Classify whether a question needs docs, SQL, or both."""
        sql_keywords = ["how many", "total", "count", "sum", "average", "list all",
                        "show me", "sales", "revenue", "customers", "products", "stock",
                        "cuántos", "total de", "ventas", "clientes", "productos"]
        q_lower = question.lower()
        needs_sql = any(kw in q_lower for kw in sql_keywords)
        return "both" if needs_sql else "docs"

    def query(self, question: str, top_k: int = 4) -> Dict:
        """
        Main query method. Routes the question to docs, SQL, or both,
        then synthesizes a response.
        """
        query_type  = self._classify_query(question)
        doc_context = []
        sql_context = None
        sql_query   = None

        # ── Document retrieval ─────────────────────────────────────────────────
        if self.vector_store and self.embedding_gen and self.vector_store.count() > 0:
            query_embedding = self.embedding_gen.embed_query(question)
            doc_context     = self.vector_store.search(query_embedding, top_k=top_k)

        # ── SQL retrieval ──────────────────────────────────────────────────────
        if self.sql_connector and query_type in ("sql", "both"):
            try:
                sql_query   = self.sql_connector.natural_language_to_sql(question, self.llm_client)
                sql_results = self.sql_connector.execute_query(sql_query)
                if sql_results:
                    rows_str    = "\n".join(str(r) for r in sql_results[:20])
                    sql_context = f"SQL: {sql_query}\nResults:\n{rows_str}"
            except Exception as e:
                sql_context = f"SQL query failed: {e}"

        # ── LLM synthesis ──────────────────────────────────────────────────────
        if not doc_context and not sql_context:
            return {
                "answer":      "I don't have enough context to answer this question. Please ingest some documents first.",
                "doc_sources": [],
                "sql_query":   None,
                "query_type":  query_type,
            }

        prompt   = build_prompt(question, doc_context, sql_context)
        response = self.llm_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt},
            ],
            temperature=0.1,
        )

        return {
            "answer":      response.choices[0].message.content,
            "doc_sources": [c["metadata"].get("source", "") for c in doc_context],
            "sql_query":   sql_query,
            "query_type":  query_type,
        }
