# TEARDOWN: Post-Mortem & Roadmap

**Project:** Enterprise Multimodal Document Intelligence Assistant  
**Author:** Sean Kang  
**Date:** 2026-06-08  
**Status:** Complete — Phase 1 post-mortem

---

## What This Document Is

An honest post-mortem written after Phase 1 build completes. Documents what failed, what was harder than expected, what I'd change, and the concrete path to Phase 2. Interviewers value this — it signals PM maturity and engineering honesty over a polished, unrealistic demo story.

---

## What Went Well

| Observation | Why It Mattered |
|---|---|
| ChromaDB integration was zero-friction | No infra to stand up — upsert + query worked on first run. Right call for PoC. |
| Claude Vision extracted pie chart values accurately on first prompt | Validated the multimodal retrieval hypothesis without iteration — chart segments and percentages were queryable. |
| LangSmith tracing worked out of the box | `@traceable` decorator + `LANGCHAIN_TRACING_V2=true` → traces visible in UI immediately. Zero config overhead, high portfolio signal. |
| Hybrid LangChain approach held up | Used LangChain for loaders/splitters, direct Anthropic SDK for LLM. Avoided LangChain's LLM wrapper complexity entirely. Every architectural decision remained explicit and owned. |
| Batch embedding cut ingest time ~10x | Sending 50 chunks per OpenAI call instead of 1 made PDF ingestion practical (3.5s for 12 chunks). |
| Streamlit variant selection UX worked | Haiku-generated query rephrasing gave the demo a concrete "AI PM thinking about UX" moment — not just a chat box. |

---

## What Failed or Was Harder Than Expected

| Failure / Obstacle | Root Cause | What I'd Do Differently |
|---|---|---|
| Query latency p95 = 9.8s — missed < 5s target | Synchronous embed → retrieve → LLM chain. Long LLM responses (AI/ML question) drive up tail latency. | Async throughout. Stream LLM tokens to UI so perceived latency drops even if wall-clock stays same. |
| pypdf emits "Ignoring wrong pointing object" warnings on every PDF load | pypdf's strict PDF parser warns on common malformed PDFs | Suppress with `warnings.filterwarnings` or pin a pypdf version that handles this silently |
| Image extraction latency is 6.9s per file | Full Claude Vision API round-trip + embedding + store on upload | Acceptable for PoC. Production path: background worker with progress indicator. |
| Prompt variants add ~500–800ms round-trip before every query | Haiku API call is synchronous — user waits before variant cards appear | Pre-generate variants async while user finishes typing. |
| Eval scope was too ambitious for Phase 1 | Planned 20 questions across 5 documents — shipped with 1 document | Set eval scope to match the build scope. 5 questions, 1 doc, real measurements. |
| No `.docx` export of filled METRICS/TEARDOWN | Deferred — filled docs after build session ended | Wire docx export into the build checklist so it runs automatically after docs are updated. |

---

## Architectural Limitations of Phase 1

| Limitation | Impact | Phase 2 Fix |
|---|---|---|
| Single ChromaDB namespace | All docs in one pool — no client isolation | Pinecone per-engagement namespacing |
| No auth / user isolation | Single user only | SSO + RBAC layer |
| Local filesystem for uploads | No persistence, no sharing | AWS S3 with presigned URLs |
| Streamlit UI | Not production API | FastAPI backend + React frontend |
| No audio support | Meeting recordings unsearchable | Whisper / AWS Transcribe → transcript → embed |
| No eval harness | Manual testing only | Automated retrieval eval on every deploy |
| No rate limiting | Demo cost risk | Token budget + caching |

---

## Phase 2 Roadmap

### Milestone 1: Production Infrastructure
- Replace ChromaDB → Pinecone (per-engagement namespacing)
- Replace local filesystem → AWS S3
- Add FastAPI backend (replace Streamlit as API layer)
- Docker + ECS deployment

### Milestone 2: Auth & Multi-User
- SSO integration (Okta / Azure AD)
- RBAC: user can only query their own engagement namespace
- Audit log: who queried what, when

### Milestone 3: Audio
- Whisper API for transcription
- Transcript chunked + embedded same as text
- Meeting recordings become queryable alongside docs

### Milestone 4: Eval Harness
- Automated retrieval accuracy eval on every deploy
- Latency regression alerts
- Retrieval quality dashboard (LangSmith)

---

## Things I'd Change If Starting Over

1. **Write the eval harness first.** Before any RAG code, define 10 test questions and expected answers. Every subsequent change gets scored against them. I had the questions in my head but not in a harness — so I measured at the end instead of throughout.

2. **Set per-component latency budgets upfront.** The p95 miss was predictable: embed (~200ms) + retrieve (~50ms) + LLM (~4–9s) = always going to blow a 5s ceiling on complex questions. Had I set budgets first, I'd have known to stream the LLM response from the start.

3. **Async from day one.** Adding async to a synchronous codebase is a refactor; starting async is just writing normal code. Every API call in this stack (OpenAI, Anthropic, ChromaDB) has an async client.

4. **One namespace per document, not one global namespace.** ChromaDB supports metadata filters — using a per-document filter from the start would have given cleaner attribution and a clearer migration path to Pinecone namespaces.

---

## Interview Talking Points

> "I built the teardown structure before writing a line of code — it forced me to think clearly about what Phase 1 is deliberately not solving and why. Scope creep kills PoCs. Documenting the Phase 2 roadmap upfront meant I could say 'no' to features mid-build without losing the vision."

> "The architectural limitations section is intentional — ChromaDB has a scale ceiling, Streamlit isn't a production API, there's no auth. I knew all of this going in. The PoC's job was to prove retrieval quality and user value, not to be production-ready. Phase 2 addresses every limitation with a concrete plan."
