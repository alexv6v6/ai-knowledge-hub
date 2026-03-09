"""
text_cleaner.py + text_chunker.py
Clean raw text and split into overlapping chunks for embedding.
"""
import re
from typing import List
from src.ingestion.document_loader import Document


# ── Cleaner ────────────────────────────────────────────────────────────────────

def clean_text(text: str) -> str:
    """Remove noise: extra whitespace, special chars, page artifacts."""
    text = re.sub(r'\s+', ' ', text)               # collapse whitespace
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\$\%\/]', '', text)  # remove special chars
    text = re.sub(r'\n{3,}', '\n\n', text)          # max 2 newlines
    return text.strip()


def clean_documents(docs: List[Document]) -> List[Document]:
    """Clean all documents in place."""
    cleaned = []
    for doc in docs:
        cleaned_content = clean_text(doc.content)
        if len(cleaned_content) > 50:  # skip near-empty docs
            cleaned.append(Document(
                content=cleaned_content,
                source=doc.source,
                doc_type=doc.doc_type,
                metadata=doc.metadata,
            ))
    print(f"✅ Cleaned {len(cleaned)}/{len(docs)} documents")
    return cleaned


# ── Chunker ────────────────────────────────────────────────────────────────────

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks by word count."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def chunk_documents(docs: List[Document], chunk_size: int = 500, overlap: int = 50) -> List[Document]:
    """Chunk all documents and return a flat list of chunk Documents."""
    chunks = []
    for doc in docs:
        text_chunks = chunk_text(doc.content, chunk_size, overlap)
        for i, chunk in enumerate(text_chunks):
            chunks.append(Document(
                content=chunk,
                source=doc.source,
                doc_type=doc.doc_type,
                metadata={**doc.metadata, "chunk_index": i, "total_chunks": len(text_chunks)},
            ))
    print(f"✅ Created {len(chunks)} chunks from {len(docs)} documents")
    return chunks
