# Deployment Log — DocIntel

## DPL-001 · Community Cloud Blank Screen on Initial Deploy

**Date:** 2026-06-09  
**Severity:** P2 — App deployed but completely non-functional  
**Environment:** Streamlit Community Cloud  
**Status:** Resolved  

---

### Summary

First deployment to Streamlit Community Cloud resulted in a blank white screen despite a successful server start (Uvicorn running on port 8501). No error was surfaced to the user. All secrets were correctly configured.

---

### Timeline

| Time (UTC) | Event |
|---|---|
| T+0 | Code pushed to GitHub (`main`). `requirements.txt`, README, and `secrets.toml.example` committed. |
| T+5m | Streamlit Cloud deployed, Uvicorn started. Blank white screen observed. |
| T+10m | Confirmed all 7 secrets set in Community Cloud settings. |
| T+15m | Logs showed server started cleanly — no exception in boot log. Issue is runtime, not startup. |
| T+20m | Identified root cause #1: `run_ui.py` configured as main file. |
| T+25m | Identified root cause #2: `run_ui.py` uses `subprocess.run()` to spawn a child Streamlit process. |
| T+30m | Fix committed: `run_ui.py` rewritten to use `exec()` in-process. `sys.path` fix added. |
| T+45m | Redeployed. App loaded successfully with full UI. |

---

### Root Cause Analysis

**Root Cause #1 — Subprocess launch inside Streamlit container**

`run_ui.py` was the configured entry point. Its implementation:

```python
# Before fix — BROKEN on Community Cloud
subprocess.run(
    [sys.executable, "-m", "streamlit", "run", "src/ui/app.py", "--server.headless=false"],
    check=True,
)
```

On Streamlit Community Cloud, the platform runs the entry point as `streamlit run run_ui.py`. When `run_ui.py` then tries to spawn a second `streamlit run` process inside the container, the subprocess call exits silently (the server port is already bound and the parent process is the Streamlit controller). No exception propagates to the user — the result is a blank white screen.

**Root Cause #2 — `sys.path` not guaranteed on Community Cloud**

`src/ui/app.py` uses package-relative imports (`from src.agents.router_agent import ...`). Locally, the developer runs from the repo root so `src` is on `sys.path`. On Community Cloud the working directory is the repo root but `sys.path` population order is not guaranteed, making imports fragile.

---

### Fix

**`run_ui.py`** — Replaced subprocess call with in-process `exec`:

```python
# After fix — works locally and on Community Cloud
_root = Path(__file__).parent.resolve()
sys.path.insert(0, str(_root))

_app = _root / "src" / "ui" / "app.py"
exec(compile(_app.read_text(), str(_app), "exec"), {"__file__": str(_app), "__name__": "__main__"})
```

`exec(compile(...))` runs `app.py` within the same Python process and the same Streamlit execution context. The `__file__` override ensures path calculations inside `app.py` resolve correctly relative to `app.py`, not `run_ui.py`.

**`src/ui/app.py`** — Added explicit `sys.path` guarantee at module top:

```python
_repo_root = Path(__file__).resolve().parent.parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))
```

**`src/ui/app.py`** — Wrapped `src.*` imports to surface failures visibly:

```python
try:
    from src.agents.router_agent import route_and_ingest, supported_extensions
    ...
except Exception as _import_err:
    st.error(f"Import error: {_import_err}")
    st.stop()
```

---

### Commits

| Commit | Description |
|---|---|
| `e0d69c2` | Initial deploy prep: README, secrets template, debug line removal |
| `8a49184` | `sys.path` fix + visible import error handling in `app.py` |
| `063ae80` | `run_ui.py` rewrite — `exec` replaces subprocess launch |

---

### Prevention

| Risk | Mitigation |
|---|---|
| Subprocess calls as Streamlit entry point | Never use `subprocess.run(streamlit run ...)` in the entry file. Use `exec` or point directly to the app file. |
| Silent import failures on cloud | Wrap top-level module imports in `try/except` with `st.error()` + `st.stop()` |
| `sys.path` fragility | Always add `repo_root` to `sys.path` explicitly at the entry point — do not rely on CWD |

---

### Lessons Learned

1. **Streamlit Cloud boot logs confirm server start, not app health.** Uvicorn running does not mean the Streamlit script executed successfully. Always test render path end-to-end.
2. **Blank white screen ≠ CSS failure.** The symptom (white screen, no dark theme) indicated the Streamlit script never reached `st.set_page_config()` — not a styling bug.
3. **Match entry point to platform contract.** Local dev convenience wrappers (`subprocess.run`) are not portable to managed platforms. Entry points must execute in-process.
