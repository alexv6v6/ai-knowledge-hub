"""
knowledge_agent.py
Top-level agent that initializes all components and exposes a simple .ask() interface.
"""
import os
from dotenv import load_dotenv

load_dotenv()


def _build_adapter(manager):
    """Wrap a ModelManager so it matches the Groq client interface."""
    class _Completions:
        def create(self, model, messages, temperature=0.1, **kwargs):
            prompt = messages[-1]["content"]
            system = next((m["content"] for m in messages if m["role"] == "system"), None)
            resp   = manager.generate(prompt, system=system, temperature=temperature)
            text   = resp.content  # capture value before class definition

            class _Msg:
                def __init__(self, c): self.content = c
            class _Choice:
                def __init__(self, c): self.message = _Msg(c)
            class _Resp:
                def __init__(self, c): self.choices = [_Choice(c)]

            return _Resp(text)

    class _Chat:
        completions = _Completions()

    class _Adapter:
        chat = _Chat()

    return _Adapter()


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

    def ask(self, question: str, llm=None) -> dict:
        """
        Ask a question. Returns answer + metadata.
        Optionally pass a ModelManager instance to override the default LLM.
        """
        if llm is not None:
            old_llm = self.pipeline.llm_client
            self.pipeline.llm_client = _build_adapter(llm)
            result = self.pipeline.query(question)
            self.pipeline.llm_client = old_llm
            return result
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