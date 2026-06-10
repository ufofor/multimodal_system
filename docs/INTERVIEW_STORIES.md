# Interview Stories — DocIntel

**Author:** Sean Kang  
**Format:** STAR (Situation / Task / Action / Result)  
**Target roles:** Customer Solutions Engineer, AI Product Manager

---

## Story 1: Debugging a Silent Cloud Deployment Failure (CSE)

**Situation**

I built an enterprise document intelligence assistant — a RAG system that lets consultants query 50+ project documents in under 30 seconds. After a clean local build, I deployed to Streamlit Community Cloud for a live demo. The platform reported a successful start (Uvicorn running on port 8501), all 7 secrets were configured correctly — but every user saw a blank white screen. No error message, no stack trace, no dark theme. The app was structurally deployed but completely non-functional.

**Task**

Diagnose and fix a P2 incident with zero error signal, against a demo deadline. The blank screen had to resolve before I could show the product to anyone.

**Action**

I started from first principles rather than guessing. The blank white screen had one key diagnostic signal: the Streamlit dark theme never loaded, which meant `st.set_page_config()` — the first line of the app — never executed. The server started, but the script itself never ran.

I traced the execution path: the configured entry point was `run_ui.py`, which called `subprocess.run(["streamlit", "run", "src/ui/app.py"])`. On Community Cloud, the platform already owns the `streamlit run` process — spawning a second one inside the container silently fails because the port is already bound. No exception surfaces; the parent process just exits cleanly, leaving users with a blank screen.

I identified a second issue in parallel: `sys.path` population order on Community Cloud is not guaranteed, making `from src.agents.router_agent import ...` fragile even if the script reached it.

I fixed both in the same commit: replaced `subprocess.run()` with `exec(compile(...))` to run `app.py` in-process within the same Streamlit execution context, and added an explicit `sys.path.insert(0, repo_root)` at the top of both files. I also wrapped all `src.*` imports in a `try/except` with `st.error()` to surface any future import failures visibly rather than silently.

**Result**

The app loaded fully on the next deploy, 45 minutes after I first observed the blank screen. The fix was two files, 12 lines of code. More importantly, I documented the root cause in a deployment log with prevention guidelines — so the next engineer on a Streamlit Cloud project knows immediately that subprocess-spawned entry points fail silently on managed platforms.

---

## Story 2: ChromaDB to Pinecone — A Zero-Rearchitecture Migration (AI PM)

**Situation**

I was building an AI document assistant for consulting workflows. For Phase 1 (local PoC), I chose ChromaDB — free, zero setup, runs in-process. The system worked: documents were chunked, embedded, and queryable. But ChromaDB stores vectors on local disk. Every Streamlit page reload wiped the vector store, forcing users to re-upload and re-index all documents from scratch. For a demo to enterprise stakeholders, that was a non-starter.

**Task**

Migrate to a persistent cloud vector store without rewriting the application logic. The agents, retrieval pipeline, and UI had to stay intact — only the infrastructure layer should change.

**Action**

I evaluated five options across four dimensions: cost, setup friction, scale ceiling, and demo-readiness. I documented the comparison in an ADR before writing a line of migration code.

The key insight was that ChromaDB and Pinecone share the same logical interface — both take a vector and return ranked matches with metadata. The risk in migration wasn't the API; it was organizational: if I hadn't planned for this from the start, I'd be refactoring every query call.

I had planned for it. In Phase 1, every embedded chunk included an `engagement_id` metadata field (defaulting to `"default"`). That field was the seam — swapping to Pinecone namespacing meant populating that field and changing one config value. No agent logic changed.

I chose Pinecone over Weaviate (comparable managed offering) because the free tier covers 1 index at 100 dimensions indefinitely, the client library has a one-line init, and the namespace model maps directly to my existing `engagement_id` metadata structure.

I also added a `has_source()` method that checks Pinecone metadata before re-embedding — so reloading the page skips already-indexed files entirely, not just avoids duplicate chunks.

**Result**

The migration took one afternoon. Zero agent code changed. Page reloads now restore the indexed document list in under 3 seconds by checking Pinecone metadata rather than re-embedding. Query latency stayed under 5 seconds at p95. The architectural decision to add `engagement_id` at the start — before I needed it — made a potentially risky migration a single config swap.

---

## Demo Script (for video recording)

**Target:** Under 90 seconds. Show: upload → index → query → cited answer.

1. Open app — sidebar visible with DOCINTEL wordmark
2. Upload a PDF (e.g. a project proposal)
3. Watch "Indexed Documents" list populate with chunk count
4. Type: *"What are the key risks in this project?"*
5. Select a query variant
6. Answer appears with cited source filename

**Talking points while recording:**
- "Files persist to S3 — reloading the page doesn't lose your documents"
- "Query variants improve retrieval by rephrasing ambiguous questions"
- "Each answer cites the source document so consultants can verify"
