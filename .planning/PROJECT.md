# DocIntel

## What This Is

DocIntel is a multimodal RAG system for boutique consulting firms. Consultants upload PDFs, images, and text files and get cited answers from their engagement documents in seconds — replacing manual document hunting. Live at Streamlit Community Cloud, targeting $399/month per workspace SaaS.

## Core Value

Consultants find answers buried in 50 project documents in 30 seconds instead of 30 minutes.

## Current Milestone: v1.0 — Market-Ready & Interview-Ready

**Goal:** Fix UI, add S3 persistence, and create interview assets — making DocIntel demo-able to enterprise buyers and hiring managers by 2026-07-07.

**Target features:**
- Sidebar visibility fix (Streamlit 1.58 CSS)
- AWS S3 persistence (upload → S3, page reload → re-ingest)
- STAR interview story docs (CSE + AI PM)
- Demo video (90-sec Loom)

## Requirements

### Validated

- ✓ Multimodal ingest (PDF, TXT, PNG, JPG) via router agent — Phase 1
- ✓ RAG query with citations — Phase 1
- ✓ Claude Vision for image/chart extraction — Phase 1
- ✓ LangSmith observability tracing — Phase 1
- ✓ Query variant generation (Haiku generates 3 rephrasing options) — Phase 1
- ✓ Pinecone vector store (cloud-hosted) — Phase 1
- ✓ Streamlit UI (Obsidian Intelligence dark theme) — Phase 1
- ✓ Deployed to Streamlit Community Cloud — Phase 1

### Active

- [ ] Sidebar always visible on Streamlit 1.58 Community Cloud
- [ ] Files persisted to AWS S3; session state rebuilt on page reload
- [ ] STAR interview stories written (CSE + AI PM)
- [ ] Demo video recorded and linked in README

### Out of Scope

- Per-user auth / login — deferred to v2 (Supabase)
- Google Drive / SharePoint integrations — v2+
- Multi-tenant workspace isolation — v2+
- Customer discovery interviews — deferred (no contacts yet)

## Context

- **Stack:** Claude Sonnet 4.6 + Haiku 4.5, OpenAI text-embedding-3-small, Pinecone (cosine, 1536-dim), Streamlit 1.58, AWS S3 (planned), LangSmith
- **Entry point:** `run_ui.py` (exec's `src/ui/app.py` in-process for Community Cloud compatibility)
- **GitHub:** https://github.com/ufofor/multimodal_system
- **Live URL:** https://multimodalsystem-iunqdkekbrxbe9mm5qohzq.streamlit.app
- **Target buyer:** Boutique consulting firms (50–500 people), $399/month flat workspace
- **Target roles (job search):** CSE at Tier 1 AI-native companies (Anthropic, OpenAI, Databricks), AI PM at Tier 2 enterprise (Salesforce, Microsoft, Google, AWS)
- **Phase 1 benchmark:** precision@5=100%, avg query=5.1s, p95=9.8s

## Constraints

- **Platform:** Streamlit Community Cloud — no subprocess spawning, no persistent local filesystem
- **Runtime:** Python 3.14 on Community Cloud (uv installs latest compatible versions)
- **Timeline:** 4 weeks to v1.0 milestone (deadline 2026-07-07)
- **Budget:** Free-tier services preferred (Pinecone free, Supabase free, S3 minimal cost)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Pinecone over ChromaDB | Cloud-hosted, no local filesystem dependency | ✓ Good |
| exec() in run_ui.py | subprocess fails on Community Cloud (port already bound) | ✓ Good |
| Streamlit over FastAPI/React | Fastest path to deployed portfolio piece | ✓ Good — Phase 2 will migrate |
| Flat workspace pricing ($399/mo) | No per-seat friction, single buyer decision | — Pending validation |
| S3 for file persistence | Aligns with Phase 2 roadmap, AWS ecosystem | — Pending implementation |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition:**
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions

**After each milestone:**
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-06-09 — Milestone v1.0 started*
