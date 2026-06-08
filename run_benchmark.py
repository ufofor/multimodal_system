"""
Benchmark: measures ingestion latency, query latency, and retrieval precision.
Usage: python run_benchmark.py
"""
import os, time, json
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

from src.core.vector_store import VectorStore
from src.agents.ingest_agent import ingest_file
from src.agents.vision_agent import ingest_image
from src.agents.rag_agent import query as rag_query

# ── Test questions + expected keywords (manual precision check) ──────────────
TEST_QA = [
    {
        "q": "What is Sean Kang's most recent job title and employer?",
        "expected": ["EY", "Ernst", "Senior", "Manager", "Consultant"],
    },
    {
        "q": "What university did Sean Kang attend and what degree did he earn?",
        "expected": ["University", "Bachelor", "MBA", "degree"],
    },
    {
        "q": "What programming languages or technical skills does Sean have?",
        "expected": ["Python", "SQL", "Java", "JavaScript", "AWS", "Azure"],
    },
    {
        "q": "What AI or machine learning experience does Sean have?",
        "expected": ["AI", "machine learning", "LLM", "model", "data"],
    },
    {
        "q": "What certifications or awards has Sean received?",
        "expected": ["certif", "award", "PMP", "AWS", "certified"],
    },
]

RESUME_PATH = "data/Sean_Kang_Resume.pdf"
IMAGE_PATH  = "data/pie_chart_example1.png"


def run():
    results = {}

    # ── Ingest PDF ───────────────────────────────────────────────────────────
    store = VectorStore(persist_dir=".chromadb_bench")
    t0 = time.perf_counter()
    ingest_result = ingest_file(RESUME_PATH, store)
    pdf_ingest_ms = (time.perf_counter() - t0) * 1000
    results["pdf_ingest_ms"] = round(pdf_ingest_ms)
    results["pdf_chunks"] = ingest_result.get("chunks_stored", 0)
    print(f"PDF ingest: {pdf_ingest_ms:.0f}ms, {results['pdf_chunks']} chunks")

    # ── Ingest image (if exists) ─────────────────────────────────────────────
    if Path(IMAGE_PATH).exists():
        t0 = time.perf_counter()
        img_result = ingest_image(IMAGE_PATH, store)
        img_ingest_ms = (time.perf_counter() - t0) * 1000
        results["image_ingest_ms"] = round(img_ingest_ms)
        results["image_chunks"] = img_result.get("chunks_stored", 0)
        print(f"Image ingest: {img_ingest_ms:.0f}ms, {results['image_chunks']} chunks")
    else:
        print(f"No image at {IMAGE_PATH}, skipping image benchmark")
        results["image_ingest_ms"] = None
        results["image_chunks"] = None

    # ── Query latency + precision ────────────────────────────────────────────
    query_latencies = []
    hits = 0

    for i, qa in enumerate(TEST_QA):
        t0 = time.perf_counter()
        resp = rag_query(qa["q"], store)
        lat_ms = (time.perf_counter() - t0) * 1000
        query_latencies.append(lat_ms)

        answer = resp.get("answer", "").lower()
        hit = any(kw.lower() in answer for kw in qa["expected"])
        hits += int(hit)

        print(f"Q{i+1} [{lat_ms:.0f}ms] {'✓' if hit else '✗'}: {qa['q'][:60]}")
        if not hit:
            print(f"  Answer snippet: {resp.get('answer','')[:200]}")

    results["query_latencies_ms"] = [round(l) for l in query_latencies]
    results["avg_query_ms"] = round(sum(query_latencies) / len(query_latencies))
    results["p95_query_ms"] = round(sorted(query_latencies)[int(len(query_latencies)*0.95)-1])
    results["precision_at_5"] = round(hits / len(TEST_QA), 2)
    results["hits"] = hits
    results["total_questions"] = len(TEST_QA)

    print(f"\nRetrieval precision@{len(TEST_QA)}: {hits}/{len(TEST_QA)} = {results['precision_at_5']}")
    print(f"Avg query latency: {results['avg_query_ms']}ms")

    # ── Cleanup bench store ──────────────────────────────────────────────────
    import shutil
    shutil.rmtree(".chromadb_bench", ignore_errors=True)

    # ── Dump JSON results ────────────────────────────────────────────────────
    out = Path("benchmark_results.json")
    out.write_text(json.dumps(results, indent=2))
    print(f"\nResults saved to {out}")
    return results


if __name__ == "__main__":
    run()
