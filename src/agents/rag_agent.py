"""RAG Agent: retrieves relevant chunks and calls Claude to answer with citations."""
import os

import anthropic
from langsmith import traceable

from src.core.embeddings import embed_query
from src.core.vector_store import VectorStore

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 2048
TOP_K = 5

SYSTEM_PROMPT = """You are a document intelligence assistant helping consultants and auditors query their engagement files.

Rules:
- Answer based ONLY on the provided context chunks.
- Always cite sources using: [Source: <filename>, page <N>]
- If multiple chunks support the answer, cite all relevant ones.
- If the answer is not in the context, respond: "I couldn't find that in the uploaded documents."
- Be concise and direct. Use bullet points for lists."""

_client = anthropic.Anthropic()


@traceable(name="rag-query")
def query(
    question: str,
    store: VectorStore,
    conversation_history: list[dict] | None = None,
    engagement_id: str = "default",
    debug: bool = False,
) -> dict:
    """
    Retrieve relevant chunks and call Claude to answer.
    Returns {"answer": str, "sources": list[dict], "chunks_used": int}.
    conversation_history: list of {"role": "user"|"assistant", "content": str}
    """
    history = conversation_history or []

    # Retrieve
    q_embedding = embed_query(question)
    results = store.query(q_embedding, n_results=TOP_K, engagement_id=engagement_id)

    chunks = results["documents"][0] if results["documents"] else []
    metadatas = results["metadatas"][0] if results["metadatas"] else []

    if not chunks:
        return {
            "answer": "I couldn't find that in the uploaded documents.",
            "sources": [],
            "chunks_used": 0,
        }

    # Build context block
    context_lines = []
    for i, (chunk, meta) in enumerate(zip(chunks, metadatas)):
        context_lines.append(
            f"[Chunk {i+1} | Source: {meta['source']}, page {meta['page']}]\n{chunk}"
        )
    context = "\n\n".join(context_lines)

    # Build messages: history + current question with context
    messages = list(history) + [
        {
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {question}",
        }
    ]

    response = _client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=messages,
    )

    answer = response.content[0].text

    # Deduplicate sources
    seen = set()
    sources = []
    for meta in metadatas:
        key = (meta["source"], meta["page"])
        if key not in seen:
            seen.add(key)
            sources.append({"source": meta["source"], "page": meta["page"], "modality": meta["modality"]})

    result = {"answer": answer, "sources": sources, "chunks_used": len(chunks)}
    if debug:
        result["debug_chunks"] = chunks
    return result
