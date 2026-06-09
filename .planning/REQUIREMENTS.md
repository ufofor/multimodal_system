# Requirements — Milestone v1.0: Market-Ready & Interview-Ready

## UI Stability

- [ ] **UI-01**: Sidebar is always visible on Streamlit Community Cloud (Streamlit 1.58)
- [ ] **UI-02**: Sidebar content (wordmark, file uploader, indexed docs list, reset button) renders correctly

## Persistence

- [ ] **PERSIST-01**: Uploaded files are stored in AWS S3 on ingest
- [ ] **PERSIST-02**: On page reload, app lists S3 bucket and identifies files not yet in Pinecone
- [ ] **PERSIST-03**: On page reload, new S3 files are re-ingested and session state rebuilt
- [ ] **PERSIST-04**: Files already in Pinecone (checked by deterministic ID) are skipped on reload (no re-embedding)
- [ ] **PERSIST-05**: S3 bucket name and AWS credentials configurable via Streamlit secrets / env vars

## Interview Assets

- [ ] **ASSET-01**: `docs/INTERVIEW_STORIES.md` exists with CSE story in STAR format (Community Cloud debug incident)
- [ ] **ASSET-02**: `docs/INTERVIEW_STORIES.md` includes AI PM story in STAR format (ChromaDB → Pinecone decision)
- [ ] **ASSET-03**: README updated with demo video link (Loom)

## Future Requirements (deferred to v2)

- Per-user authentication and workspace isolation (Supabase Auth)
- Google Drive / SharePoint integration
- Multi-tenant access control
- Customer discovery documentation

## Out of Scope (v1.0)

- Auth/login — adds weeks, not needed for demo or first paying customer
- Integrations — deferred until v1 revenue validates the product
- Mobile-responsive layout — desktop-first for enterprise buyers
- Customer discovery interviews — no contacts yet, deferred

## Traceability

| REQ-ID | Phase | Status |
|--------|-------|--------|
| UI-01 | Phase 1 | Pending |
| UI-02 | Phase 1 | Pending |
| PERSIST-01 | Phase 2 | Pending |
| PERSIST-02 | Phase 2 | Pending |
| PERSIST-03 | Phase 2 | Pending |
| PERSIST-04 | Phase 2 | Pending |
| PERSIST-05 | Phase 2 | Pending |
| ASSET-01 | Phase 3 | Pending |
| ASSET-02 | Phase 3 | Pending |
| ASSET-03 | Phase 3 | Pending |
