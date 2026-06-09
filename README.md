# DocIntel — Enterprise Multimodal Document Intelligence Assistant

A multimodal RAG system that ingests PDFs, text files, and images, then answers questions with cited sources. Built as an AI PM portfolio project demonstrating multi-agent architecture, vector search, and enterprise observability.

**Live demo:** *(Streamlit Community Cloud link — add after deploy)*

---

## Architecture

```
Upload (PDF / TXT / PNG / JPG)
        │
        ▼
   Router Agent
   ├── Text/PDF → LangChain loaders → RecursiveCharacterTextSplitter
   └── Images   → Claude Vision (sonnet-4-6) → extract text/charts
        │
        ▼
   OpenAI Embeddings (text-embedding-3-small, 1536-dim)
        │
        ▼
   Pinecone Vector Store
        │
   Query ──► Haiku generates 3 rephrasing variants → user picks
        │
        ▼
   RAG Agent → Claude Sonnet → answer + citations
        │
   LangSmith tracing
```

**Stack:** Anthropic Claude (Sonnet + Haiku) · OpenAI embeddings · Pinecone · LangChain · Streamlit · LangSmith

---

## Local Setup

**Prerequisites:** Python 3.11+, API keys for Anthropic, OpenAI, Pinecone, LangSmith

```bash
git clone https://github.com/ufofor/multimodal_system
cd multimodal_system
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your API keys
python run_ui.py
```

**Required env vars** (see `.env.example`):
```
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
LANGCHAIN_API_KEY=
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=enterprise-doc-assistant
PINECONE_API_KEY=
PINECONE_INDEX=docintel   # name of your Pinecone index (1536 dims, cosine)
```

**Create Pinecone index** (one-time):
- Dimensions: `1536`
- Metric: `cosine`
- Name: `docintel` (or whatever you set `PINECONE_INDEX` to)

---

## Deploy to Streamlit Community Cloud

1. Fork or push this repo to GitHub (no `.env` file — it's gitignored)
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app
3. Set **Main file path** to `src/ui/app.py`
4. Under **Advanced settings → Secrets**, paste:
```toml
ANTHROPIC_API_KEY = "sk-ant-..."
OPENAI_API_KEY = "sk-..."
LANGCHAIN_API_KEY = "ls__..."
LANGCHAIN_TRACING_V2 = "true"
LANGCHAIN_PROJECT = "enterprise-doc-assistant"
PINECONE_API_KEY = "..."
PINECONE_INDEX = "docintel"
```
5. Deploy — app auto-injects secrets into `os.environ` on startup

---

## PM Docs

| Doc | Purpose |
|-----|---------|
| `docs/PRD.md` | Product requirements, scope, success criteria |
| `docs/ADR.md` | Architecture decision records with tradeoff analysis |
| `docs/METRICS.md` | Measured performance: latency, retrieval precision, cost |
| `docs/TEARDOWN.md` | What worked, failures, what I'd change |

---

## CLI Usage

```bash
# Ingest a file and ask a question
python run_cli.py data/sample.pdf
python run_cli.py data/chart.png --debug

# Reset vector store
python run_cli.py data/sample.pdf --reset
```
