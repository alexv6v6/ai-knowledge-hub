"""
scripts/ingest_documents.py
Ingest all documents from data/raw/documents/ into the vector store.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.agents.knowledge_agent import KnowledgeAgent

if __name__ == "__main__":
    agent = KnowledgeAgent()

    # Ingest from directory
    docs_dir = "data/raw/documents"
    if os.path.exists(docs_dir) and os.listdir(docs_dir):
        n = agent.ingest_directory(docs_dir)
        print(f"\n✅ Done. Indexed {n} chunks.")
    else:
        print(f"⚠️  No documents found in {docs_dir}")
        print("   Add PDF or TXT files to that folder and run again.")

    print("\nCurrent status:", agent.status())
