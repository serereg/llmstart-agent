"""Knowledge base indexer — load PDF/MD, chunk, embed into Chroma."""

from pathlib import Path
from typing import Literal

import chromadb
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

Audience = Literal["b2b", "b2c"]

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
SUPPORTED_EXTENSIONS = {".md", ".pdf"}


def _load_markdown(path: Path, audience: Audience) -> list[Document]:
    text = path.read_text(encoding="utf-8")
    return [
        Document(
            page_content=text,
            metadata={"audience": audience, "source": path.name},
        ),
    ]


def _load_pdf(path: Path, audience: Audience) -> list[Document]:
    reader = PdfReader(str(path))
    pages: list[Document] = []
    for index, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if not text.strip():
            continue
        pages.append(
            Document(
                page_content=text,
                metadata={"audience": audience, "source": path.name, "page": index + 1},
            ),
        )
    return pages


def load_documents(data_dir: Path, audience: Audience) -> list[Document]:
    """Load all supported documents from an audience directory."""
    audience_dir = data_dir / audience
    if not audience_dir.is_dir():
        return []

    documents: list[Document] = []
    for path in sorted(audience_dir.iterdir()):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        if suffix not in SUPPORTED_EXTENSIONS:
            continue
        if suffix == ".md":
            documents.extend(_load_markdown(path, audience))
        elif suffix == ".pdf":
            documents.extend(_load_pdf(path, audience))
    return documents


def build_chroma_index(
    embeddings: Embeddings,
    data_dir: Path,
    *,
    collection_name: str = "knowledge_base",
) -> Chroma:
    """Build an in-memory Chroma index from b2b and b2c knowledge files."""
    all_docs: list[Document] = []
    all_docs.extend(load_documents(data_dir, "b2b"))
    all_docs.extend(load_documents(data_dir, "b2c"))

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(all_docs) if all_docs else []

    client = chromadb.EphemeralClient()
    if not chunks:
        return Chroma(
            client=client,
            collection_name=collection_name,
            embedding_function=embeddings,
        )

    return Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        client=client,
        collection_name=collection_name,
    )
