"""
vector_store.py
Manages ChromaDB vector store: add, search, and persist embeddings.
"""
import os
from typing import List, Dict
from src.ingestion.document_loader import Document


class VectorStore:
    def __init__(self, collection_name: str = "knowledge_hub", persist_dir: str = "data/processed/chroma"):
        try:
            import chromadb
            from chromadb.config import Settings
            self.client = chromadb.PersistentClient(path=persist_dir)
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            print(f"✅ VectorStore ready — collection: '{collection_name}' ({self.collection.count()} docs)")
        except ImportError:
            raise ImportError("Install chromadb: pip install chromadb")

    def add_documents(self, docs: List[Document], embeddings: List[List[float]]):
        """Add documents and their embeddings to the vector store."""
        if len(docs) != len(embeddings):
            raise ValueError("Docs and embeddings must have the same length")

        ids       = [f"doc_{i}_{hash(d.source)}" for i, d in enumerate(docs)]
        texts     = [d.content for d in docs]
        metadatas = [{**d.metadata, "source": d.source, "doc_type": d.doc_type} for d in docs]

        # Batch insert
        batch_size = 64
        for i in range(0, len(docs), batch_size):
            self.collection.upsert(
                ids=ids[i:i+batch_size],
                documents=texts[i:i+batch_size],
                embeddings=embeddings[i:i+batch_size],
                metadatas=metadatas[i:i+batch_size],
            )
        print(f"✅ Added {len(docs)} documents to vector store")

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """Search for the most similar documents."""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, self.collection.count()),
            include=["documents", "metadatas", "distances"],
        )
        hits = []
        for i in range(len(results["documents"][0])):
            hits.append({
                "content":  results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "score":    1 - results["distances"][0][i],  # cosine similarity
            })
        return hits

    def count(self) -> int:
        return self.collection.count()

    def reset(self):
        """Clear all documents from the collection."""
        self.collection.delete(where={"doc_type": {"$in": ["pdf", "txt", "url"]}})
        print("🧹 Vector store cleared")


class EmbeddingGenerator:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
            self.model = HuggingFaceEmbeddings(model_name=model_name)
            self.model_name = model_name
            print(f"✅ Embedding model loaded: {model_name}")
        except ImportError:
            raise ImportError("Install: pip install langchain-huggingface sentence-transformers")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.model.embed_documents(texts)

    def embed_query(self, query: str) -> List[float]:
        return self.model.embed_query(query)
