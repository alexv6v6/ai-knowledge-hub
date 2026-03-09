"""
document_loader.py
Unified loader that handles multiple source types: PDF, TXT, and URLs.
"""
import os
from dataclasses import dataclass
from typing import List
from pathlib import Path


@dataclass
class Document:
    content: str
    source: str
    doc_type: str  # "pdf" | "txt" | "url"
    metadata: dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


def load_from_directory(directory: str) -> List[Document]:
    """Load all supported documents from a directory."""
    docs = []
    path = Path(directory)

    if not path.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    for file in path.rglob("*"):
        if file.suffix.lower() == ".pdf":
            docs.extend(load_pdf(str(file)))
        elif file.suffix.lower() == ".txt":
            docs.extend(load_txt(str(file)))

    print(f"✅ Loaded {len(docs)} documents from {directory}")
    return docs


def load_pdf(filepath: str) -> List[Document]:
    """Load a PDF file and return a list of Documents (one per page)."""
    try:
        import pypdf
        docs = []
        with open(filepath, "rb") as f:
            reader = pypdf.PdfReader(f)
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                if text.strip():
                    docs.append(Document(
                        content=text,
                        source=filepath,
                        doc_type="pdf",
                        metadata={"page": i + 1, "total_pages": len(reader.pages)},
                    ))
        return docs
    except ImportError:
        raise ImportError("Install pypdf: pip install pypdf")


def load_txt(filepath: str) -> List[Document]:
    """Load a plain text file."""
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    return [Document(content=content, source=filepath, doc_type="txt")]


def load_url(url: str) -> List[Document]:
    """Fetch and load content from a URL."""
    try:
        import requests
        from bs4 import BeautifulSoup
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        # Remove scripts and styles
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        return [Document(content=text, source=url, doc_type="url", metadata={"url": url})]
    except ImportError:
        raise ImportError("Install dependencies: pip install requests beautifulsoup4")
