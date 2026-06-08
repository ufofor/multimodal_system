"""Router Agent: single entry point for all file ingestion. Classifies by type, dispatches."""
from pathlib import Path

from src.core.vector_store import VectorStore
from src.agents.ingest_agent import ingest_file
from src.agents.vision_agent import SUPPORTED_EXTENSIONS as IMAGE_EXTENSIONS

TEXT_EXTENSIONS = {".pdf", ".txt"}
ALL_SUPPORTED = TEXT_EXTENSIONS | IMAGE_EXTENSIONS


def route_and_ingest(
    file_path: str | Path,
    store: VectorStore,
    engagement_id: str = "default",
) -> dict:
    """
    Classify file type and dispatch to the correct ingest pipeline.
    Returns {"chunks_stored": int, "source": str, "modality": str, "file_type": str}.
    Raises ValueError for unsupported types.
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix not in ALL_SUPPORTED:
        raise ValueError(
            f"Unsupported file type '{suffix}'. Supported: {sorted(ALL_SUPPORTED)}"
        )

    result = ingest_file(path, store, engagement_id)
    result["file_type"] = suffix
    return result


def supported_extensions() -> set[str]:
    return ALL_SUPPORTED
