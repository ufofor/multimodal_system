# Roadmap — Milestone v1.0: Market-Ready & Interview-Ready

**3 phases** | **10 requirements mapped** | Deadline: 2026-07-07

| # | Phase | Goal | Requirements | Duration |
|---|-------|------|--------------|----------|
| 1 | Sidebar Fix | Sidebar always visible on Community Cloud | UI-01, UI-02 | Days 1–3 |
| 2 | S3 Persistence | Files survive page reload via AWS S3 | PERSIST-01–05 | Days 4–14 |
| 3 | Interview Assets | STAR stories + demo video ready | ASSET-01–03 | Days 15–21 |

---

## Phase 1: Sidebar Fix

**Goal:** Sidebar is always visible and functional on Streamlit 1.58 Community Cloud.

**Requirements:** UI-01, UI-02

**Success criteria:**
1. Sidebar panel is visible on page load without any user action
2. DOCINTEL wordmark, file uploader, and Reset Store button are all visible
3. Sidebar remains visible after uploading a file and after page refresh
4. No CSS rule hides or collapses the sidebar unintentionally

**Approach notes:**
- Root cause: `header { visibility: hidden }` hides Streamlit's sidebar toggle in v1.58
- Fix: `transform: translateX(0px) !important` pins sidebar open; stop hiding header element
- Verify on live Community Cloud URL after each push

---

## Phase 2: S3 Persistence

**Goal:** Uploaded files persist to AWS S3 and are restored on page reload.

**Requirements:** PERSIST-01, PERSIST-02, PERSIST-03, PERSIST-04, PERSIST-05

**Success criteria:**
1. Upload a PDF → close browser → reopen app → doc appears in INDEXED list
2. Pinecone ID check skips re-embedding already-indexed files (fast reload)
3. Fresh S3 file is fully ingested and queryable after reload
4. AWS credentials stored in Streamlit secrets (not hardcoded)
5. S3 bucket name configurable via `S3_BUCKET_NAME` env var

**Approach notes:**
- New module: `src/core/storage.py` — S3 upload + list + download
- Modify `ingest_agent.py`: after ingest, upload original file to S3
- Modify `app.py` `_init_state()`: on load, call `restore_from_s3()` before rendering
- Deterministic Pinecone ID = `hashlib.sha256(filename + chunk_index)` — already used, check before re-embed
- New secrets needed: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `S3_BUCKET_NAME`

---

## Phase 3: Interview Assets

**Goal:** STAR-format interview stories written and demo video recorded.

**Requirements:** ASSET-01, ASSET-02, ASSET-03

**Success criteria:**
1. `docs/INTERVIEW_STORIES.md` exists with CSE story in full STAR format
2. `docs/INTERVIEW_STORIES.md` includes AI PM story in full STAR format
3. Each story is 200–400 words, uses concrete metrics (latency numbers, time saved)
4. README contains demo video link (Loom or equivalent)
5. Demo video shows: upload → index → query → cited answer (under 90 seconds)

**Approach notes:**
- CSE story: Community Cloud blank screen incident — subprocess → exec() fix (DEPLOYMENT_LOG.md is source material)
- AI PM story: ChromaDB → Pinecone migration decision (ADR.md is source material)
- Demo video: record on local with `.env` keys; show clean UI with sidebar + upload + query flow
