# ADR: Architecture Decision Record

**Project:** Enterprise Multimodal Document Intelligence Assistant  
**Author:** Sean Kang  
**Date:** 2026-05-27

---

## ADR-001: Hybrid LangChain + Direct Anthropic SDK

**Status:** Accepted

**Context:**  
Needed a framework strategy. Pure LangChain abstracts too much — every architectural decision becomes invisible. Pure custom code means writing boilerplate that frameworks already solved.

**Decision:**  
Hybrid approach: LangChain for commodity utilities (loaders, chunkers, memory, vector store wrappers), direct Anthropic SDK for all LLM calls, custom Python for routing and orchestration.

| Component | Approach | Rationale |
|---|---|---|
| PDF/image loading | LangChain (`UnstructuredPDFLoader`) | Saves boilerplate, handles edge cases |
| Text chunking | LangChain (`RecursiveCharacterTextSplitter`) | Tuned defaults, handles overlap |
| Vector store interface | LangChain wrapper | ChromaDB → Pinecone = 1 config change |
| Conversation memory | LangChain (`ConversationBufferWindowMemory`) | Well-solved, window=6 turns |
| Routing logic | Plain Python | File type detection = code, not AI |
| LLM calls | Direct Anthropic SDK | Explicit, cacheable, controllable |
| Agent orchestration | Custom Python | Every decision is explicit, debuggable |
| Observability | LangSmith | Trace every retrieval + LLM call |

**Consequences:**  
- Full visibility into every architectural choice — critical for interview narrative  
- LangSmith traces are portfolio-ready screenshots  
- Slightly more code than pure LangChain, but understandable to any engineer  

**Rejected alternatives:**  
- Pure LangChain LCEL chains: too magical, decision rationale buried in abstraction  
- Pure custom: unnecessary re-implementation of solved problems  

---

## ADR-002: ChromaDB for Phase 1 Vector Store

**Status:** Accepted

**Context:**  
Phase 1 is a PoC running locally. Need a vector store that works without cloud accounts, infra setup, or cost.

**Decision:**  
ChromaDB (local, in-process mode).

| Option | Cost | Setup | Scale ceiling | Verdict |
|---|---|---|---|---|
| **ChromaDB** | Free | 0 infra | Single machine | ✅ Phase 1 |
| Pinecone | $0–$70+/mo | Account + API key | Fully managed | Phase 2 |
| Weaviate Cloud | Free tier, $25+/mo | Account | Fully managed | Phase 2 alt |
| pgvector | Infra cost | Postgres setup | Postgres limits | Enterprise only |
| Qdrant | Free (self-hosted) | Docker | Scalable | Phase 2 alt |

**Namespace seam:** All embeddings include `engagement_id` metadata field (defaults to `"default"` in Phase 1). Migration to Pinecone namespacing = populate that field + swap vector store config. Zero rearchitecture.

**Consequences:**  
- Zero cost, zero setup friction for PoC  
- Performance degrades past ~100K chunks on a single machine (acceptable for demo)  
- Pinecone migration path is explicit and low-risk  

---

## ADR-003: claude-sonnet-4-6 for Text + Vision

**Status:** Accepted

**Context:**  
Need a model for (a) document reasoning and answer synthesis, (b) image content extraction. Could use different models per task.

**Decision:**  
Single model — `claude-sonnet-4-6` — for both text reasoning and vision extraction in Phase 1.

| Model | $/MTok in | $/MTok out | Vision | Notes |
|---|---|---|---|---|
| **claude-sonnet-4-6** | $3 | $15 | Excellent | ✅ Chosen |
| claude-haiku-4-5 | $0.80 | $4 | Fair | 10x cheaper, weaker reasoning |
| gpt-4o | $2.50 | $10 | Excellent | Comparable, different ecosystem |
| gemini-1.5-pro | $1.25 | $5 | Excellent | Good multimodal, Google stack |

**Interview rationale:**  
"For Phase 1 I used claude-sonnet-4-6 for both tasks to reduce integration complexity. In production I'd route simple image extraction to claude-haiku-4-5 (~10x cheaper) and reserve Sonnet for reasoning-heavy queries. I'd A/B test claude-sonnet-4-6 vs gpt-4o on a retrieval accuracy benchmark before committing."

**Consequences:**  
- Single API integration = simpler PoC  
- Slightly higher cost per image extraction than a dedicated lighter model  
- Production optimization: model routing by task complexity  

---

## ADR-004: text-embedding-3-small for Embeddings

**Status:** Accepted

**Context:**  
Embedding model determines retrieval quality and cost. Higher dimensions = better recall, higher cost.

**Decision:**  
`text-embedding-3-small` (OpenAI) for Phase 1.

| Model | $/MTok | Dims | Quality | Notes |
|---|---|---|---|---|
| **text-embedding-3-small** | $0.02 | 1536 | Good | ✅ Best cost/quality for PoC |
| text-embedding-3-large | $0.13 | 3072 | Best (OAI) | 6.5x more expensive |
| voyage-3 | $0.06 | 1024 | Strong RAG | Recommended for Claude stack |
| cohere-embed-v3 | $0.10 | 1024 | Good multilingual | Better for non-English |

**Upgrade trigger:** If retrieval accuracy drops below 70% target in METRICS.md, upgrade to `voyage-3` (optimized for RAG use cases) or `text-embedding-3-large`.

**Consequences:**  
- Lowest cost option that meets quality bar for PoC  
- If client corpus shifts to non-English, Cohere becomes preferred  

---

## ADR-005: Multi-Agent Architecture (Router + Specialized Agents)

**Status:** Accepted

**Context:**  
Could process all file types with a single LLM call. Multi-agent adds complexity — is it justified?

**Decision:**  
Separate agents: Router Agent, Ingest Agent (text path), Vision Agent (image path), RAG Agent.

**Rationale:**

| Concern | Single-call approach | Multi-agent approach |
|---|---|---|
| Debugging | Hard — which part failed? | Isolated — failure is traceable |
| Model swapping | All-or-nothing | Swap vision model independently |
| Scaling | Can't optimize per modality | Route cheap/expensive tasks independently |
| Interview narrative | Invisible | Every decision is explicit |

**Interview rationale:**  
"A single call can't specialize. Separation of concerns means I can swap the vision model to Haiku without touching the reasoning layer. It also made debugging straightforward — when image extraction was wrong, I knew exactly where to look."

**Consequences:**  
- More files, more interfaces, more testable  
- Slightly higher orchestration overhead (acceptable at PoC scale)  
- Clear extension point for audio agent in Phase 2  

---

## ADR-006: Streamlit for Phase 1 UI

**Status:** Accepted

**Context:**  
Need a UI. Could build a full React/FastAPI app or use a rapid-prototype framework.

**Decision:**  
Streamlit for Phase 1. Claude-designed custom UI components for visual quality.

| Option | Build time | Visual quality | Interview signal |
|---|---|---|---|
| **Streamlit + custom design** | 1–2 days | High (with care) | Fast shipping + polish |
| React + FastAPI | 1–2 weeks | Highest | Overbuilt for PoC |
| Gradio | 0.5 days | Medium | Less control |
| Jupyter notebook | 0 days | Low | Not demo-ready |

**Phase 2 migration:** FastAPI backend (replace Streamlit as API layer) + React frontend. Business logic already in agents — UI is a thin wrapper.

**Consequences:**  
- PoC ships fast; demo-ready in days not weeks  
- UI code is not production architecture (documented in TEARDOWN.md)  
- Claude-assisted design ensures visual polish beyond default Streamlit aesthetics  
