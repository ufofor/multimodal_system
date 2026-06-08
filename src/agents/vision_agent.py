"""Vision Agent: extracts text from images via Claude Vision, then embeds + stores."""
import base64
import re
from pathlib import Path

import anthropic

from src.core.embeddings import embed_texts
from src.core.vector_store import VectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 2048
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
EMBED_BATCH_SIZE = 50

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg"}
MEDIA_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
}

_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client
_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
)


def _safe_id(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]", "_", text)


def _extract_text_from_image(image_path: Path) -> str:
    """Send image to Claude Vision, return extracted text content."""
    suffix = image_path.suffix.lower()
    media_type = MEDIA_TYPES[suffix]

    image_data = base64.standard_b64encode(image_path.read_bytes()).decode("utf-8")

    response = _get_client().messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": (
                            "Extract ALL information from this image for search indexing. Be exhaustive and literal.\n\n"
                            "If the image contains a chart, graph, or diagram:\n"
                            "- List EVERY data point with its exact label and value (e.g. 'General Financial: 4.11%')\n"
                            "- Include ALL axis labels, legend entries, and titles\n"
                            "- Preserve exact numbers, percentages, and units as shown\n"
                            "- Use the format: '<Category>: <Value>' for each data point\n\n"
                            "If the image contains a table:\n"
                            "- Reproduce every row and column with exact values\n\n"
                            "If the image contains text:\n"
                            "- Transcribe it verbatim\n\n"
                            "Do NOT summarize or paraphrase. Extract exact values so they can be found by keyword search."
                        ),
                    },
                ],
            }
        ],
    )
    return response.content[0].text


def ingest_image(
    file_path: str | Path,
    store: VectorStore,
    engagement_id: str = "default",
) -> dict:
    """
    Extract text from image via Claude Vision, chunk, embed, and store.
    Returns {"chunks_stored": int, "source": str, "modality": str}.
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported image type: {suffix}. Supported: {SUPPORTED_EXTENSIONS}")

    extracted_text = _extract_text_from_image(path)

    page_chunks = _splitter.split_text(extracted_text)
    chunks, metadatas, ids = [], [], []

    for idx, chunk_text in enumerate(page_chunks):
        if not chunk_text.strip():
            continue
        chunk_id = _safe_id(f"{path.stem}_img_c{idx}")
        chunks.append(chunk_text)
        metadatas.append({
            "source": path.name,
            "page": 1,
            "modality": "image",
            "engagement_id": engagement_id,
        })
        ids.append(chunk_id)

    for i in range(0, len(chunks), EMBED_BATCH_SIZE):
        batch_chunks = chunks[i : i + EMBED_BATCH_SIZE]
        batch_meta = metadatas[i : i + EMBED_BATCH_SIZE]
        batch_ids = ids[i : i + EMBED_BATCH_SIZE]
        embeddings = embed_texts(batch_chunks)
        store.add(batch_chunks, embeddings, batch_meta, batch_ids)

    return {"chunks_stored": len(chunks), "source": path.name, "modality": "image"}
