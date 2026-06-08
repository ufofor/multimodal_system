# EY Interview Portfolio Project — Handoff Doc

**Project:** Enterprise Multimodal Document Intelligence Assistant  
**Goal:** PoC → portfolio piece covering all EY JD requirements  
**Status:** Pre-build. Create project folder, then start with PRD.md.

---

## JD → Project Coverage Map

| EY JD Requirement | How This Project Covers It |
|---|---|
| AI/ML SaaS / PoC experience | Multi-agent RAG system as PoC |
| Multimodal AI (text + image + audio) | Option A: text + image / Option B: + audio |
| Enterprise client-facing project | Framed as auditor/consultant use case |
| Cloud (AWS/GCP), Vector DB, Embeddings | Option A: local / Option B: AWS S3 + Pinecone |
| Programming → built service/application | Full working Streamlit app |

---

## User Persona

**Who:** Management consultant / internal auditor  
**Job to be done:** "I have 50 client engagement files — PDFs, Excel exports saved as images, screenshot slides. I need to query across all of them without opening each one."  
**Current pain:** Ctrl+F doesn't cross files. Images are unsearchable. No semantic understanding.

---

## Architecture

### Option A (Build first)

```
User uploads file (PDF or image)
          │
          ▼
  ┌───────────────┐
  │  Router Agent │  ← detects file type (text vs image)
  └──────┬────────┘
         │
    ┌────┴────────────┐
    ▼                 ▼
Text Agent        Vision Agent
(chunk + embed)   (Claude Vision → extract → embed)
    │                 │
    └────────┬────────┘
             ▼
      ChromaDB (local)
      vector store
             │
             ▼
      RAG / Q&A Agent
      (retrieve → synthesize → answer)
             │
             ▼
      Streamlit UI
```

### Option B (Later)

Add:
- Audio Agent (Whisper/AWS Transcribe → transcript → embed)
- AWS S3 for file storage
- Pinecone for managed vector DB
- FastAPI backend (replace Streamlit as API layer)
- Eval harness (retrieval accuracy, latency benchmarks)

---

## Folder Structure (create this)

```
enterprise-doc-assistant/
├── README.md                  ← product overview + demo
├── agents/
│   ├── router_agent.py
│   ├── text_agent.py
│   ├── vision_agent.py
│   └── rag_agent.py
├── core/
│   ├── vector_store.py        ← ChromaDB wrapper
│   └── embeddings.py
├── app.py                     ← Streamlit UI
├── data/                      ← sample test docs (add 3-5 PDFs + images)
├── docs/
│   ├── PRD.md
│   ├── ADR.md
│   ├── METRICS.md
│   └── TEARDOWN.md
└── requirements.txt
```

---

## Service & Model Comparisons

Use these in interviews to demonstrate tradeoff thinking. Chosen options starred (★).

---

### LLM — Text + Reasoning

| Model | Input | Output | Latency (est) | Notes |
|---|---|---|---|---|
| **claude-sonnet-4-6 ★** | $3/MTok | $15/MTok | 2–4s | Best reasoning, strong vision |
| claude-haiku-4-5 | $0.80/MTok | $4/MTok | 0.5–1.5s | Fast, cheap, weaker reasoning |
| gpt-4o | $2.50/MTok | $10/MTok | 2–3s | Strong all-around |
| gpt-4o-mini | $0.15/MTok | $0.60/MTok | 1–2s | Cost-optimized, weaker |
| gemini-1.5-flash | $0.075/MTok | $0.30/MTok | ~1s | Cheapest, good for high volume |
| gemini-1.5-pro | $1.25/MTok | $5/MTok | 2–4s | Strong multimodal |

**Interview rationale:** "I chose claude-sonnet-4-6 because the use case is document-heavy with complex reasoning requirements. For a high-volume production system, I'd consider routing simple queries to Haiku or GPT-4o-mini to reduce cost by ~70%."

---

### LLM — Vision (Image Understanding)

| Model | Vision Quality | Est. cost/image | Notes |
|---|---|---|---|
| **claude-sonnet-4-6 ★** | Excellent | ~$0.01–0.03 | Strong on charts, tables, diagrams |
| gpt-4o | Excellent | ~$0.01–0.02 | Strong all-around vision |
| gpt-4o-mini | Good | ~$0.001–0.003 | OK for simple screenshots |
| gemini-1.5-pro | Excellent | ~$0.01–0.02 | Multimodal-native, long context |
| claude-haiku-4-5 | Fair | ~$0.003–0.008 | Adequate for simple images |

**Cost per image** = rough estimate for a medium-resolution image (~1000 tokens input).

**Interview rationale:** "For PoC I used claude-sonnet-4-6 for both text and vision to reduce integration complexity. In production I'd evaluate GPT-4o-mini for simpler images to cut vision costs ~10x, routing only complex charts to the stronger model."

---

### Embedding Models

| Model | Cost | Dimensions | Quality | Notes |
|---|---|---|---|---|
| **text-embedding-3-small ★** | $0.02/MTok | 1536 | Good | Best cost/quality for PoC |
| text-embedding-3-large | $0.13/MTok | 3072 | Best (OpenAI) | 6.5x more expensive |
| voyage-3 (Anthropic) | $0.06/MTok | 1024 | Strong RAG | Recommended for Claude stack |
| cohere-embed-v3 | $0.10/MTok | 1024 | Good multilingual | Better for non-English |
| ada-002 (legacy) | $0.10/MTok | 1536 | Weaker | Avoid for new builds |

**Interview rationale:** "For the PoC I used text-embedding-3-small — it's 6.5x cheaper than the large model with minimal quality loss for this use case. If retrieval accuracy drops below target in METRICS.md, I'd upgrade to voyage-3 or text-embedding-3-large."

---

### Vector Database

| DB | Cost | Query latency | Scaling limit | Best for |
|---|---|---|---|---|
| **ChromaDB (local) ★** | Free | <10ms | Single machine | Option A / PoC |
| Pinecone | Free tier (1 index, 2GB), ~$70+/mo | 20–50ms | Fully managed | Option B / production |
| Weaviate Cloud | Free tier, ~$25+/mo | 20–40ms | Fully managed | Good Pinecone alt |
| pgvector | Infra cost only | 5–20ms | Your Postgres limit | Enterprise, SQL needed |
| Qdrant | Free (self-hosted), cloud ~$25+/mo | 10–30ms | Scalable | Modern, fast |

**Interview rationale:** "ChromaDB is right for the PoC — zero cost, zero infra, embeds directly in Python. For production with enterprise clients, I'd migrate to Pinecone (fully managed, SLA, no ops burden) or pgvector if the client already runs Postgres and wants to minimize vendor sprawl."

---

### Audio Transcription (Option B reference)

| Service | Cost | Latency | Notes |
|---|---|---|---|
| Whisper (local) | Compute cost only | ~0.3–0.5x audio length | Free, needs GPU for speed |
| OpenAI Whisper API | $0.006/min | ~1–2x audio length | Simple, no infra |
| AWS Transcribe | $0.024/min | Near real-time | Enterprise, speaker diarization |
| Google Speech-to-Text | $0.016/min | Near real-time | Strong accuracy, multilingual |
| Azure Speech | $0.016/min | Near real-time | Enterprise, Microsoft ecosystem |

**Interview rationale:** "For Option B I'd start with OpenAI Whisper API — low friction for PoC. If the client is AWS-native or needs speaker identification, AWS Transcribe justifies its 4x cost premium."

---

### Cloud Storage (Option B reference)

| Service | Cost (storage) | Cost (egress) | Notes |
|---|---|---|---|
| AWS S3 | $0.023/GB/mo | $0.09/GB | Standard; most enterprise-compatible |
| GCP Cloud Storage | $0.020/GB/mo | $0.08/GB | Slightly cheaper |
| Azure Blob | $0.018/GB/mo | $0.08/GB | Microsoft ecosystem |

**For PoC (Option A):** local filesystem, no cost, no infra.

---

## PM Artifacts to Build Alongside Code

| File | Content | Interview usage |
|---|---|---|
| `docs/PRD.md` | Problem, persona, requirements, scope, out-of-scope | "I scoped before coding" |
| `docs/ADR.md` | Architecture decisions with rationale (use table above) | Shows tradeoff thinking |
| `docs/METRICS.md` | Retrieval accuracy, latency, doc coverage results | Quantified outcomes |
| `docs/TEARDOWN.md` | What failed, what I'd change, Option B roadmap | Shows PM maturity |

---

## Success Metrics to Measure

| Metric | How to measure | Target |
|---|---|---|
| Retrieval accuracy | Manual: 20 test queries, score top-3 hit | >70% hit rate |
| Query latency | Time from question → answer | <5s p95 |
| Ingestion latency | Time to process + embed 1 doc | <10s |
| Image extraction quality | Manual: did Vision capture useful content? | >80% useful |
| Doc types supported | # formats successfully ingested | PDF, PNG, JPG, TXT |

---

## Build Order (Option A)

```
Step 1: ChromaDB + embeddings layer (text only, no agents)
        → verify: can embed a PDF chunk and retrieve it

Step 2: Text agent + Streamlit Q&A
        → verify: ask a question about an uploaded PDF, get correct answer

Step 3: Vision agent (Claude Vision → extract text from image → embed)
        → verify: upload a chart image, query about its content

Step 4: Router agent (classify file type → dispatch to correct agent)
        → verify: drop PDF and image, both processed correctly

Step 5: Polish Streamlit UI + load sample enterprise docs
        → verify: works end-to-end with realistic data

Step 6: Measure METRICS.md, write ADR.md, TEARDOWN.md
```

---

## First Actions When Folder Created

1. `mkdir enterprise-doc-assistant && cd enterprise-doc-assistant`
2. `git init`
3. Create `docs/PRD.md` first (write the problem before touching code)
4. Create `requirements.txt`
5. Tell Claude Code: "Start Step 1 — build ChromaDB + embeddings layer"

---

## Interview Talking Points

**"Why multi-agent vs single LLM call?"**  
Single call can't specialize. Router + specialized agents = cleaner separation of concerns, easier to swap models per modality, easier to debug failures.

**"Why ChromaDB for PoC?"**  
Zero infra, zero cost, embeds in Python. Pinecone is right for production but wrong for PoC — you pay for managed infra before proving the concept works.

**"Why claude-sonnet-4-6 and not GPT-4o?"**  
Similar capability and cost. I chose claude-sonnet-4-6 because the use case is document-heavy with complex reasoning, Claude excels there, and I was building in the Anthropic ecosystem. In production, I'd A/B test both.

**"How would you scale this for an enterprise client?"**  
Replace ChromaDB with Pinecone, add AWS S3 for file storage, wrap in FastAPI, add auth, add eval harness for ongoing retrieval quality monitoring, add Option B audio layer.

**"What failed?"**  
→ Fill in after building. Document real failures in TEARDOWN.md. Interviewers value honesty + learning more than a perfect demo.
