# EY Portfolio Project: Brainstorm / Discovery Notes
Date: 2026-06-08 · Goal: Surface what's in Sean's head about this project — decisions made, gaps, interview readiness, next steps

## Summary / key decisions
(running synthesis, updated as we go)

## Q&A log

### Q7 — GitHub repo
- Asked: Existing repo or create new?
- Captured: No existing repo, no local git init. Creating manually on GitHub then pushing.
- Flags: none

### Q6 — Pinecone account + swap
- Asked: Have Pinecone account or need to create?
- Captured: Created Pinecone account. API key added to .env. ChromaDB → Pinecone swap complete and tested (12 chunks ingested, query returning correct answers). reset flag updated in CLI + UI.
- Flags: none

### Q6 (original) — Pinecone account
- Asked: Have Pinecone account or need to create?
- Captured: No account yet. Need to create + get API key + swap codebase from ChromaDB to Pinecone before Community Cloud deploy.
- Flags: none — will do now

### Q5 — Vector DB for deployment
- Asked: Accept ephemeral ChromaDB or swap to hosted vector DB?
- Captured: Swap ChromaDB → hosted vector DB before deploying to Community Cloud. Persistent store across deploys.
- Flags: Which hosted DB and account status -> Q6

### Q4 — Deployment target
- Asked: Streamlit Community Cloud vs production-grade first?
- Captured: Community Cloud first (fast portfolio signal), then production-grade deployment as a follow-on phase.
- Flags: Production-grade stack (FastAPI + React + ECS) is Phase 2 — no timeline set yet

### Q3 — Key skillsets to demonstrate
- Asked: Which enterprise skillsets are you targeting specifically?
- Captured: Focus is multimodal AI system first — this is the current build. "Something else" to follow after this ships. No specific second project named yet.
- Flags: What comes after multimodal AI system? -> Sean to decide after Phase 1 ships

### Q2 — Definition of "deployed"
- Asked: What does deployed mean — live URL, Docker, FastAPI+React?
- Captured: Confirmed cloud-hosted live product is the goal. Project targets enterprise companies, so the deployment and feature set need to reflect enterprise-relevant skillsets.
- Flags: Exact hosting platform TBD (see Q3+)

### Q1 — Purpose and audience
- Asked: Who is this for and what should they conclude?
- Captured: EY interviewers for AI PM role. Goal is to demonstrate scoping, architecting, and shipping a multimodal AI system — not just talk about it. User also wants to carry it end-to-end to deployment to see the actual final product himself. Both portfolio signal AND personal completion.
- Flags: none

## Open flags (pending input)
