"""
knowledge_agent.py
Top-level agent that initializes all components and exposes a simple .ask() interface.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class KnowledgeAgent:
    """
    Unified knowledge agent combining:
    - Document RAG (PDFs, TXT, URLs via ChromaDB + HuggingFace embeddings)
    - SQL database queries (Text-to-SQL via Groq LLM)
    """

    def __init__(self):
        from groq import Groq
        from src.embeddings.vector_store import VectorStore, EmbeddingGenerator
        from src.retrieval.sql_connector import SQLConnector
        from src.rag.rag_pipeline import RAGPipeline

        print("🚀 Initializing Knowledge Agent...")

        self.llm       = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.embedder  = EmbeddingGenerator()
        self.vector_db = VectorStore()
        self.sql_db    = SQLConnector()
        self.pipeline  = RAGPipeline(
            vector_store=self.vector_db,
            embedding_gen=self.embedder,
            sql_connector=self.sql_db,
            llm_client=self.llm,
        )
        print("✅ Knowledge Agent ready")

    def ask(self, question: str) -> dict:
        """Ask a question. Returns answer + metadata."""
        return self.pipeline.query(question)

    def ingest(self, source: str):
        """
        Ingest a document or URL into the knowledge base.
        source: file path (PDF/TXT) or URL
        """
        from src.ingestion.document_loader import load_pdf, load_txt, load_url
        from src.ingestion.text_cleaner import clean_documents, chunk_documents

        print(f"📥 Ingesting: {source}")

        if source.startswith("http"):
            raw_docs = load_url(source)
        elif source.endswith(".pdf"):
            raw_docs = load_pdf(source)
        else:
            raw_docs = load_txt(source)

        cleaned = clean_documents(raw_docs)
        chunks  = chunk_documents(cleaned)

        texts      = [c.content for c in chunks]
        embeddings = self.embedder.embed_documents(texts)
        self.vector_db.add_documents(chunks, embeddings)

        print(f"✅ Ingested {len(chunks)} chunks from {source}")
        return len(chunks)

    def ingest_directory(self, directory: str):
        """Ingest all documents from a directory."""
        from src.ingestion.document_loader import load_from_directory
        from src.ingestion.text_cleaner import clean_documents, chunk_documents

        raw_docs = load_from_directory(directory)
        cleaned  = clean_documents(raw_docs)
        chunks   = chunk_documents(cleaned)

        texts      = [c.content for c in chunks]
        embeddings = self.embedder.embed_documents(texts)
        self.vector_db.add_documents(chunks, embeddings)

        print(f"✅ Ingested {len(chunks)} chunks from {directory}")
        return len(chunks)

    def status(self) -> dict:
        """Return current status of the knowledge base."""
        return {
            "documents_indexed": self.vector_db.count(),
            "embedding_model":   self.embedder.model_name,
            "db_schema":         self.sql_db.get_schema(),
        }


if __name__ == "__main__":
    agent = KnowledgeAgent()
    print("\nStatus:", agent.status())
    result = agent.ask("What products do we have in stock?")
    print("\nAnswer:", result["answer"])
    if result["sql_query"]:
        print("SQL used:", result["sql_query"])
