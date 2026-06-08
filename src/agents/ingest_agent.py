"""Ingest Agent: routes files, chunks text, embeds, and stores in VectorStore."""
import re
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.core.embeddings import embed_texts
from src.core.vector_store import VectorStore
from src.agents.vision_agent import ingest_image, SUPPORTED_EXTENSIONS as IMAGE_EXTENSIONS

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
EMBED_BATCH_SIZE = 50

_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
)


def _safe_id(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]", "_", text)


def ingest_file(
    file_path: str | Path,
    store: VectorStore,
    engagement_id: str = "default",
) -> dict:
    """
    Ingest a single file into the vector store.
    Returns {"chunks_stored": int, "source": str, "modality": str}.
    Images are accepted but deferred to Step 3 (vision agent).
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return _ingest_pdf(path, store, engagement_id)
    elif suffix in IMAGE_EXTENSIONS:
        return ingest_image(path, store, engagement_id)
    elif suffix == ".txt":
        return _ingest_txt(path, store, engagement_id)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")


def _ingest_pdf(path: Path, store: VectorStore, engagement_id: str) -> dict:
    loader = PyPDFLoader(str(path))
    pages = loader.load()

    chunks = []
    metadatas = []
    ids = []

    for page_doc in pages:
        page_num = page_doc.metadata.get("page", 0) + 1  # 1-indexed
        page_chunks = _splitter.split_text(page_doc.page_content)

        for idx, chunk_text in enumerate(page_chunks):
            if not chunk_text.strip():
                continue
            chunk_id = _safe_id(f"{path.stem}_p{page_num}_c{idx}")
            chunks.append(chunk_text)
            metadatas.append({
                "source": path.name,
                "page": page_num,
                "modality": "text",
                "engagement_id": engagement_id,
            })
            ids.append(chunk_id)

    _embed_and_store(chunks, metadatas, ids, store)
    return {"chunks_stored": len(chunks), "source": path.name, "modality": "text"}


def _ingest_txt(path: Path, store: VectorStore, engagement_id: str) -> dict:
    text = path.read_text(encoding="utf-8", errors="ignore")
    page_chunks = _splitter.split_text(text)

    chunks, metadatas, ids = [], [], []
    for idx, chunk_text in enumerate(page_chunks):
        if not chunk_text.strip():
            continue
        chunk_id = _safe_id(f"{path.stem}_c{idx}")
        chunks.append(chunk_text)
        metadatas.append({
            "source": path.name,
            "page": 1,
            "modality": "text",
            "engagement_id": engagement_id,
        })
        ids.append(chunk_id)

    _embed_and_store(chunks, metadatas, ids, store)
    return {"chunks_stored": len(chunks), "source": path.name, "modality": "text"}


def _embed_and_store(chunks, metadatas, ids, store: VectorStore) -> None:
    for i in range(0, len(chunks), EMBED_BATCH_SIZE):
        batch_chunks = chunks[i : i + EMBED_BATCH_SIZE]
        batch_meta = metadatas[i : i + EMBED_BATCH_SIZE]
        batch_ids = ids[i : i + EMBED_BATCH_SIZE]
        embeddings = embed_texts(batch_chunks)
        store.add(batch_chunks, embeddings, batch_meta, batch_ids)
