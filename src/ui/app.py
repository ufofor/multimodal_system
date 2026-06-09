"""DocIntel — Enterprise Multimodal Document Intelligence Assistant."""
import os
import sys
import tempfile
from pathlib import Path

# Ensure repo root is in sys.path (required for Streamlit Community Cloud)
_repo_root = Path(__file__).resolve().parent.parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Inject Streamlit secrets into os.environ (needed on Community Cloud)
try:
    import streamlit as _st
    for _k, _v in _st.secrets.items():
        if _k not in os.environ:
            os.environ[_k] = str(_v)
except Exception:
    pass

try:
    from src.agents.router_agent import route_and_ingest, supported_extensions
    from src.agents.rag_agent import query as rag_query
    from src.core.vector_store import VectorStore
    from src.utils.prompt_variants import generate_variants
except Exception as _import_err:
    import streamlit as _st
    _st.set_page_config(page_title="DocIntel")
    _st.error(f"Import error: {_import_err}")
    _st.stop()

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="DocIntel",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Theme ─────────────────────────────────────────────────────────────────────
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600&family=Space+Mono:wght@400;700&display=swap');

:root {
  --bg-base:       #080C10;
  --bg-surface:    #0F1620;
  --bg-raised:     #162030;
  --bg-hover:      #1A2840;
  --border:        #1E2D40;
  --border-bright: #2A3F58;
  --accent:        #00D4AA;
  --accent-dim:    rgba(0,212,170,0.10);
  --accent-warm:   #FFB547;
  --text-1:        #D8E8F0;
  --text-2:        #6B8499;
  --text-3:        #2E4358;
  --badge-img:     #FF7B6B;
  --badge-txt:     #4ECDC4;
  --font:          'Outfit', sans-serif;
  --mono:          'Space Mono', monospace;
}

/* Base */
.stApp { background-color: var(--bg-base) !important; font-family: var(--font) !important; }
#MainMenu, footer, header { visibility: hidden !important; }
.stDeployButton { display: none !important; }

/* Sidebar */
section[data-testid="stSidebar"] {
  background-color: var(--bg-surface) !important;
  border-right: 1px solid var(--border) !important;
}

/* All text */
p, span, div, label, li {
  font-family: var(--font) !important;
  color: var(--text-2);
}
h1, h2, h3 { font-family: var(--font) !important; color: var(--text-1) !important; }

/* Buttons */
.stButton > button {
  background: var(--bg-raised) !important;
  color: var(--text-1) !important;
  border: 1px solid var(--border-bright) !important;
  border-radius: 8px !important;
  font-family: var(--font) !important;
  font-size: 0.83rem !important;
  font-weight: 500 !important;
  transition: all 0.15s ease !important;
  text-align: left !important;
}
.stButton > button:hover {
  background: var(--bg-hover) !important;
  border-color: var(--accent) !important;
  color: var(--accent) !important;
}
.stButton > button:focus { outline: none !important; box-shadow: 0 0 0 2px rgba(0,212,170,0.25) !important; }

/* Chat messages */
[data-testid="stChatMessage"] {
  background: var(--bg-surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  margin-bottom: 0.6rem !important;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
  background: var(--accent-dim) !important;
  border-color: rgba(0,212,170,0.18) !important;
}

/* Chat input */
[data-testid="stChatInput"] {
  background: var(--bg-surface) !important;
  border: 1px solid var(--border-bright) !important;
  border-radius: 10px !important;
}
[data-testid="stChatInput"] textarea {
  background: transparent !important;
  color: var(--text-1) !important;
  font-family: var(--font) !important;
}
[data-testid="stChatInput"] button { background: var(--accent) !important; border-radius: 6px !important; }

/* File uploader */
[data-testid="stFileUploaderDropzone"] {
  background: var(--bg-raised) !important;
  border: 1px dashed var(--border-bright) !important;
  border-radius: 8px !important;
}

/* Spinner */
.stSpinner > div { border-top-color: var(--accent) !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb { background: var(--border-bright); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }

/* Divider */
hr { border-color: var(--border) !important; margin: 1rem 0 !important; }

/* Success/error */
[data-testid="stAlert"] { border-radius: 8px !important; font-family: var(--font) !important; }
"""
st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────
def _init_state():
    if "store" not in st.session_state:
        try:
            st.session_state["store"] = VectorStore()
        except Exception as e:
            st.error(f"Failed to connect to vector store: {e}")
            st.stop()
    defaults = {
        "store": st.session_state["store"],
        "messages": [],          # {role, content, sources?, chunks_used?}
        "ingested": [],          # {name, chunks_stored, modality}
        "pending_q": None,       # question waiting for variant selection
        "variants": [],          # 3 alternative phrasings
        "show_variants": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()


# ── Helpers ───────────────────────────────────────────────────────────────────
def _ingest(uploaded_file) -> None:
    suffix = Path(uploaded_file.name).suffix.lower()
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(uploaded_file.getbuffer())
        tmp_path = tmp.name
    try:
        result = route_and_ingest(tmp_path, st.session_state.store)
        result["name"] = uploaded_file.name
        st.session_state.ingested.append(result)
    finally:
        os.unlink(tmp_path)


def _run_query(question: str) -> None:
    st.session_state.messages.append({"role": "user", "content": question})
    result = rag_query(question, st.session_state.store)
    st.session_state.messages.append({
        "role": "assistant",
        "content": result["answer"],
        "sources": result.get("sources", []),
        "chunks_used": result.get("chunks_used", 0),
    })


def _select_variant(idx: int) -> None:
    """Called when user picks a variant (0 = original, 1-3 = variants)."""
    if idx == 0:
        question = st.session_state.pending_q
    else:
        question = st.session_state.variants[idx - 1]
    st.session_state.show_variants = False
    st.session_state.pending_q = None
    st.session_state.variants = []
    _run_query(question)


def _reset_store() -> None:
    st.session_state.store._index.delete(delete_all=True)
    st.session_state.store = VectorStore()
    st.session_state.ingested = []
    st.session_state.messages = []
    st.session_state.show_variants = False
    st.session_state.pending_q = None
    st.session_state.variants = []


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Wordmark
    st.markdown("""
    <div style="margin-bottom:2rem;padding:0 0.5rem;">
      <div style="font-family:'Space Mono',monospace;font-size:1.05rem;color:#00D4AA;
                  letter-spacing:0.12em;font-weight:700;">◈ DOCINTEL</div>
      <div style="font-size:0.65rem;color:#2E4358;margin-top:5px;
                  letter-spacing:0.1em;font-family:'Space Mono',monospace;">
        ENTERPRISE DOCUMENT INTELLIGENCE
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Upload
    st.markdown(
        '<div style="font-size:0.7rem;color:#6B8499;letter-spacing:0.1em;'
        'font-family:\'Space Mono\',monospace;margin-bottom:0.5rem;">UPLOAD DOCUMENTS</div>',
        unsafe_allow_html=True,
    )
    ext_list = [e.lstrip(".") for e in supported_extensions()]
    uploaded = st.file_uploader(
        f"PDF · TXT · PNG · JPG",
        type=ext_list,
        accept_multiple_files=False,
        label_visibility="visible",
    )
    if uploaded:
        already = any(f["name"] == uploaded.name for f in st.session_state.ingested)
        if not already:
            with st.spinner(f"Indexing {uploaded.name}…"):
                try:
                    _ingest(uploaded)
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

    # Indexed documents list
    if st.session_state.ingested:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size:0.7rem;color:#6B8499;letter-spacing:0.1em;'
            'font-family:\'Space Mono\',monospace;margin-bottom:0.6rem;">INDEXED</div>',
            unsafe_allow_html=True,
        )
        for doc in st.session_state.ingested:
            mod = doc.get("modality", "text")
            badge_col = "#FF7B6B" if mod == "image" else "#4ECDC4"
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:0.45rem 0.65rem;margin-bottom:5px;
                        background:#162030;border:1px solid #1E2D40;border-radius:6px;">
              <span style="font-size:0.75rem;color:#D8E8F0;white-space:nowrap;
                           overflow:hidden;text-overflow:ellipsis;max-width:130px;">
                {doc['name']}
              </span>
              <div style="display:flex;gap:5px;align-items:center;flex-shrink:0;margin-left:6px;">
                <span style="font-size:0.6rem;background:{badge_col}20;color:{badge_col};
                             border:1px solid {badge_col}40;padding:1px 5px;border-radius:3px;
                             font-family:'Space Mono',monospace;white-space:nowrap;">{mod}</span>
                <span style="font-size:0.6rem;color:#2E4358;font-family:'Space Mono',monospace;">
                  {doc['chunks_stored']}c
                </span>
              </div>
            </div>
            """, unsafe_allow_html=True)

        total = st.session_state.store.count()
        st.markdown(
            f'<div style="font-size:0.65rem;color:#2E4358;font-family:\'Space Mono\',monospace;'
            f'margin-top:0.4rem;">{total} chunks in store</div>',
            unsafe_allow_html=True,
        )

    # Reset
    st.markdown("<hr>", unsafe_allow_html=True)
    if st.button("⟳  Reset Store", use_container_width=True):
        _reset_store()
        st.rerun()


# ── Main area ─────────────────────────────────────────────────────────────────
# Header
st.markdown("""
<div style="margin-bottom:1.75rem;">
  <h1 style="font-size:1.55rem;font-weight:600;color:#D8E8F0;margin:0;letter-spacing:-0.02em;">
    Document Intelligence
  </h1>
  <p style="color:#2E4358;font-size:0.75rem;margin:5px 0 0;font-family:'Space Mono',monospace;
            letter-spacing:0.05em;">
    multimodal · retrieval-augmented generation · enterprise
  </p>
</div>
""", unsafe_allow_html=True)

# Empty state
if not st.session_state.ingested:
    st.markdown("""
    <div style="text-align:center;padding:5rem 2rem;
                border:1px dashed #1E2D40;border-radius:14px;margin:1rem 0;">
      <div style="font-size:3rem;color:#1E2D40;margin-bottom:1.25rem;
                  font-family:'Space Mono',monospace;">◈</div>
      <div style="color:#2E4358;font-size:0.88rem;line-height:1.9;
                  font-family:'Space Mono',monospace;">
        Upload a document in the sidebar to begin.<br>
        PDF, TXT, PNG and JPG are supported.<br>
        Text and visual content are indexed together.
      </div>
    </div>
    """, unsafe_allow_html=True)

# Chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(
            f'<div style="color:#D8E8F0;font-size:0.9rem;line-height:1.65;">{msg["content"]}</div>',
            unsafe_allow_html=True,
        )
        if msg["role"] == "assistant" and msg.get("sources"):
            badges = ""
            for s in msg["sources"]:
                mod = s.get("modality", "text")
                bc = "#FF7B6B" if mod == "image" else "#4ECDC4"
                badges += (
                    f'<span style="font-family:\'Space Mono\',monospace;font-size:0.63rem;'
                    f'background:{bc}18;color:{bc};border:1px solid {bc}30;'
                    f'padding:2px 7px;border-radius:3px;margin-right:5px;white-space:nowrap;">'
                    f'{s["source"]} · p{s["page"]} · {mod}</span>'
                )
            st.markdown(
                f'<div style="margin-top:0.7rem;display:flex;flex-wrap:wrap;gap:4px;">{badges}</div>',
                unsafe_allow_html=True,
            )

# Variant selection panel
if st.session_state.show_variants and st.session_state.variants:
    st.markdown("""
    <div style="margin:1.25rem 0 0.75rem;padding:1.1rem 1.25rem 0.5rem;
                background:#0F1620;border:1px solid #1E2D40;border-radius:10px;">
      <div style="font-size:0.65rem;color:#2E4358;letter-spacing:0.12em;margin-bottom:0.9rem;
                  font-family:'Space Mono',monospace;">SELECT QUERY PHRASING</div>
    </div>
    """, unsafe_allow_html=True)

    options = [st.session_state.pending_q] + st.session_state.variants
    labels = ["Original", "Variant 1", "Variant 2", "Variant 3"]
    cols = st.columns(4)
    for i, (col, label, text) in enumerate(zip(cols, labels, options)):
        with col:
            preview = text[:90] + "…" if len(text) > 90 else text
            st.markdown(
                f'<div style="font-size:0.62rem;color:#6B8499;letter-spacing:0.08em;'
                f'font-family:\'Space Mono\',monospace;margin-bottom:4px;">{label}</div>',
                unsafe_allow_html=True,
            )
            if st.button(preview, key=f"v_{i}", use_container_width=True):
                _select_variant(i)
                st.rerun()

    st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)

# Chat input (only when documents loaded and not in variant selection)
if st.session_state.ingested and not st.session_state.show_variants:
    user_input = st.chat_input("Ask a question about your documents…")
    if user_input:
        with st.spinner("Generating query variants…"):
            variants = generate_variants(user_input, n=3)
        st.session_state.pending_q = user_input
        st.session_state.variants = variants
        st.session_state.show_variants = True
        st.rerun()
