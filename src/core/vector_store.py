import os
from pinecone import Pinecone


class VectorStore:
    def __init__(self, persist_dir: str = ".chromadb", collection: str = "documents"):
        # persist_dir kept for interface compatibility — Pinecone is cloud-hosted
        pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
        self._index = pc.Index(os.environ["PINECONE_INDEX"])

    def add(
        self,
        chunks: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict],
        ids: list[str],
    ) -> None:
        vectors = [
            {"id": vid, "values": emb, "metadata": {**meta, "text": chunk}}
            for vid, emb, meta, chunk in zip(ids, embeddings, metadatas, chunks)
        ]
        # Pinecone recommends batches of ≤100
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            self._index.upsert(vectors=vectors[i : i + batch_size])

    def query(
        self,
        embedding: list[float],
        n_results: int = 5,
        engagement_id: str = "default",
    ) -> dict:
        filter_ = {"engagement_id": engagement_id} if engagement_id != "default" else None
        resp = self._index.query(
            vector=embedding,
            top_k=n_results,
            include_metadata=True,
            filter=filter_,
        )
        matches = resp.get("matches", [])
        documents = [m["metadata"].pop("text", "") for m in matches]
        metadatas = [m["metadata"] for m in matches]
        # Return ChromaDB-compatible shape so callers need no changes
        return {"documents": [documents], "metadatas": [metadatas]}

    def has_source(self, filename: str) -> bool:
        resp = self._index.query(
            vector=[0.0] * 1536,
            top_k=1,
            include_metadata=False,
            filter={"source": {"$eq": filename}},
        )
        return len(resp.get("matches", [])) > 0

    def count(self) -> int:
        stats = self._index.describe_index_stats()
        return stats.get("total_vector_count", 0)
