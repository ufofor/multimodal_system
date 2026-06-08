# PRD: Enterprise Multimodal Document Intelligence Assistant

**Version:** 1.0  
**Author:** Sean Kang  
**Date:** 2026-05-27  
**Status:** Active — Phase 1 (PoC)

---

## 1. Problem Statement

Management consultants and internal auditors accumulate dozens of client engagement files — PDFs, Excel exports saved as images, screenshot slides — across every engagement. Querying across them requires opening each file individually. Images are entirely unsearchable. There is no semantic understanding: searching for "revenue recognition issue" won't surface a paragraph discussing "ASC 606 non-compliance."

**The result:** analysts spend 20–40% of document review time on file navigation, not analysis.

---

## 2. Target Persona

**Primary:** Management consultant / internal auditor at a Big 4 or mid-market firm

| Attribute | Detail |
|---|---|
| Job | Senior associate or manager on a client engagement |
| Files per engagement | 30–200 docs (PDFs, scanned images, slide exports) |
| Current workflow | Manual search, Ctrl+F, reading through files linearly |
| Pain | Can't cross-reference across files; images are dead weight |
| Tech comfort | High — uses Excel, Power BI, Teams daily; not a developer |
| Success signal | "Ask one question, get the answer from the right document" |

---

## 3. Goals

### Phase 1 (This Build)
- Upload PDF and image files into a local knowledge base
- Ask natural language questions, get answers with source citations
- Support multimodal documents: text-heavy PDFs and image files (charts, scanned pages, slides)
- Run locally — no cloud account, no infra setup, no cost per query

### Phase 2 (Roadmap)
- Engagement namespacing: isolate each client matter's data
- Audio transcription: meeting recordings → searchable transcript
- Cloud storage + managed vector DB for enterprise scale
- Auth / RBAC for multi-user access
- Eval harness for ongoing retrieval quality monitoring

---

## 4. Requirements

### Functional

| ID | Requirement | Priority |
|---|---|---|
| F1 | Accept PDF file upload | P0 |
| F2 | Accept image file upload (PNG, JPG) | P0 |
| F3 | Answer natural language questions about uploaded docs | P0 |
| F4 | Cite source document + page/location in every answer | P0 |
| F5 | Support follow-up questions within a session (stateful) | P1 |
| F6 | Display ingestion status feedback to user | P1 |
| F7 | Handle multi-document queries ("compare doc A and doc B") | P1 |
| F8 | Accept TXT file upload | P2 |

### Non-Functional

| ID | Requirement | Target |
|---|---|---|
| NF1 | Query latency (question → answer) | p95 < 5 seconds |
| NF2 | Ingestion latency (upload → queryable) | < 10 seconds per doc |
| NF3 | Retrieval accuracy | > 70% top-3 hit rate on test set |
| NF4 | Image extraction utility | > 80% of images yield useful extracted text |
| NF5 | Local operation | Runs on MacBook Pro, no cloud services required (Phase 1) |

---

## 5. Out of Scope (Phase 1)

- Audio/video file support
- Multi-user access or authentication
- Cloud storage (S3, GCS)
- Managed vector DB (Pinecone, Weaviate)
- Per-engagement data isolation (namespace isolation)
- Real-time document collaboration
- Structured data querying (Excel, CSV parsing beyond text extraction)
- Summarization without a specific question

---

## 6. User Journey

```
1. Open app in browser (localhost)
2. Upload 1–N files (PDF or image) via drag-and-drop
3. System confirms ingestion: "3 files processed, 142 chunks indexed"
4. User types question in chat: "What were the key risks identified in the Q3 audit?"
5. System retrieves relevant chunks across all docs
6. System returns answer with citation: "Source: engagement_report.pdf, page 4"
7. User asks follow-up: "How does that compare to Q2?"
8. System uses conversation history to contextualize the follow-up
```

---

## 7. Success Metrics

| Metric | Measurement Method | Target | Status |
|---|---|---|---|
| Retrieval accuracy | 20-query manual eval, score top-3 hit | > 70% | To measure |
| Query latency | Timed from submit to first token | p95 < 5s | To measure |
| Ingestion latency | Timed from upload to "indexed" confirmation | < 10s | To measure |
| Image extraction quality | Manual review of 10 extracted images | > 80% useful | To measure |
| Format support | Verified file types | PDF, PNG, JPG | To verify |

---

## 8. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Vision extraction fails on low-quality scans | Medium | High | Fallback: return raw image context with low-confidence flag |
| Retrieval misses relevant chunks | Medium | High | Tune chunk size, overlap, top-K; add hybrid BM25 search |
| ChromaDB performance degrades at scale | Low (Phase 1) | Medium | Designed for Pinecone migration with 1-line config change |
| LLM hallucination on sparse context | Low | High | Prompt instructs Claude to cite sources or say "not found" |
| API cost overrun during demo | Low | Low | Rate-limit in UI; cache recent answers |

---

## 9. Open Questions

| Question | Owner | Due |
|---|---|---|
| Optimal chunk size for consultant docs (typically dense, structured) | Sean | Before Step 1 build |
| Hybrid search: worth implementing in Phase 1 or defer? | Sean | Before Step 2 build |
| Sample data: what 5 docs best represent engagement files? | Sean | Before Step 5 polish |
