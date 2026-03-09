"""
test_ingestion.py — Unit tests for document ingestion pipeline.
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.ingestion.document_loader import Document
from src.ingestion.text_cleaner import clean_text, clean_documents, chunk_text, chunk_documents


class TestCleanText:
    def test_removes_extra_whitespace(self):
        assert clean_text("hello   world") == "hello world"

    def test_collapses_newlines(self):
        result = clean_text("line1\n\n\n\nline2")
        assert "\n\n\n" not in result

    def test_strips_text(self):
        assert clean_text("  hello  ") == "hello"

    def test_empty_string(self):
        assert clean_text("") == ""


class TestChunkText:
    def test_basic_chunking(self):
        text = " ".join(["word"] * 1000)
        chunks = chunk_text(text, chunk_size=100, overlap=10)
        assert len(chunks) > 1

    def test_chunk_size_respected(self):
        text = " ".join(["word"] * 200)
        chunks = chunk_text(text, chunk_size=50, overlap=0)
        for chunk in chunks[:-1]:  # last chunk may be smaller
            assert len(chunk.split()) <= 50

    def test_overlap_creates_more_chunks(self):
        text = " ".join(["word"] * 200)
        chunks_no_overlap   = chunk_text(text, chunk_size=50, overlap=0)
        chunks_with_overlap = chunk_text(text, chunk_size=50, overlap=10)
        assert len(chunks_with_overlap) >= len(chunks_no_overlap)

    def test_single_chunk_for_short_text(self):
        text = "short text"
        chunks = chunk_text(text, chunk_size=100)
        assert len(chunks) == 1


class TestCleanDocuments:
    def test_filters_empty_docs(self):
        docs = [
            Document(content="x", source="test.txt", doc_type="txt"),
            Document(content="valid content with enough text here", source="test2.txt", doc_type="txt"),
        ]
        cleaned = clean_documents(docs)
        assert len(cleaned) == 1

    def test_preserves_metadata(self):
        docs = [Document(content="valid long enough content for testing", source="test.txt", doc_type="txt", metadata={"page": 1})]
        cleaned = clean_documents(docs)
        assert cleaned[0].metadata["page"] == 1


class TestChunkDocuments:
    def test_produces_chunk_metadata(self):
        docs = [Document(content=" ".join(["word"] * 600), source="test.txt", doc_type="txt")]
        chunks = chunk_documents(docs, chunk_size=100, overlap=0)
        assert all("chunk_index" in c.metadata for c in chunks)
        assert all("total_chunks" in c.metadata for c in chunks)

    def test_multiple_docs(self):
        docs = [
            Document(content=" ".join(["word"] * 200), source=f"doc{i}.txt", doc_type="txt")
            for i in range(3)
        ]
        chunks = chunk_documents(docs, chunk_size=100, overlap=0)
        assert len(chunks) >= 3
