# CloudOps Sentinel — Enterprise Incident Response Self-RAG Copilot

A production-style **Self-RAG** demo for cloud operations and incident response. It searches private operational knowledge in Pinecone first, self-grades the retrieved evidence, corrects weak retrieval/generation, and uses **internet search only when the private knowledge base is insufficient**.

The project also demonstrates **LangGraph SQLite persistence memory** so follow-up questions can reuse the same incident context through a stable `thread_id`.

## Architecture

```text
User Incident / Follow-up
        ↓
LangGraph SQLite Memory
        ↓
Contextualize Follow-up
        ↓
Decide Retrieval
        ↓
Private Pinecone Knowledge Base
        ↓
Grade Retrieved Documents
   ┌────┴───────────────┐
Relevant             Weak / Missing
   ↓                      ↓
Generate              Rewrite Query
   ↓                      ↓
IsSUP              Retry Private KB
   ↓                      ↓
Revise if needed   Internet Search Fallback
   ↓                      ↓
IsUSE              Grade Web Evidence
   ↓                      ↓
Final Answer ← Generate → IsSUP → IsUSE
        ↓
SQLite Checkpoint / Memory
```

## Tech stack

- **LangGraph** — Self-RAG workflow, conditional routing, persistent thread state
- **OpenAI `gpt-5-mini`** — routing, query rewriting, generation, relevance grading, IsSUP and IsUSE
- **OpenAI `text-embedding-3-large`** — embeddings for private operational documents
- **Pinecone** — private runbooks/SOPs/postmortems knowledge base
- **Tavily** — controlled internet-search fallback
- **SQLite** — LangGraph persistence memory + simple audit database for the demo
- **FastAPI** — application/API backend
- **HTML/CSS/JavaScript** — incident-command-center UI with document upload
- **Docker** — deployment packaging

## Project structure

```text
CloudOps-Sentinel-Enterprise-Incident-Response-Self-RAG-Copilot/
├── app.py
├── data_ingestion.py          # ONE file to build the Pinecone KB
├── src/
│   ├── config.py
│   ├── db.py
│   ├── ingestion.py
│   ├── models.py
│   ├── self_rag.py
│   └── vectorstore.py
├── documents/                 # initial private knowledge documents
│   ├── checkout-api-runbook.md
│   ├── payments-high-cpu-runbook.md
│   └── deployment-rollback-sop.md
├── templates/index.html
├── static/styles.css
├── static/app.js
├── uploads/                   # documents uploaded through the UI
├── data/                      # SQLite persistence files
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## 1. Setup

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

macOS/Linux:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and configure:

```env
OPENAI_API_KEY=...
PINECONE_API_KEY=...
TAVILY_API_KEY=...
```

The defaults are:

```env
OPENAI_MODEL=gpt-5-mini
EMBEDDING_MODEL=text-embedding-3-large
EMBEDDING_DIMENSION=3072
PINECONE_INDEX_NAME=cloudops-sentinel-openai-self-rag
PINECONE_NAMESPACE=incident-runbooks
```

> The project intentionally uses a new default Pinecone index name. The earlier local embedding version used a different vector dimension, and Pinecone index dimensions cannot be mixed.

## 2. Build the entire Pinecone knowledge base with ONE command

Put your initial PDF/TXT/MD/DOCX documents inside `documents/`, then run:

```bash
python data_ingestion.py
```

That one file performs the complete ingestion pipeline:

```text
Read .env
  ↓
Create / validate Pinecone index
  ↓
Load ./documents
  ↓
Split documents into chunks
  ↓
OpenAI text-embedding-3-large
  ↓
Upsert to Pinecone
  ↓
Configured namespace is ready
```

The ingestion uses stable chunk IDs, so rerunning the script updates matching vectors rather than blindly generating a new random ID for every chunk.

## 3. Run the application

Either:

```bash
python app.py
```

or:

```bash
uvicorn app:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

## Add new documents from the UI

The left-side **Runbook Vault** accepts:

- PDF
- TXT
- Markdown
- DOCX

When you click **Add to knowledge base**, the backend uses the exact same ingestion layer and OpenAI embedding model as `data_ingestion.py`.

```text
New UI Document
      ↓
FastAPI /api/upload
      ↓
Document Loader + Chunking
      ↓
OpenAI Embeddings
      ↓
EXISTING Pinecone Index
      ↓
EXISTING Namespace
```

So you can prepare the initial knowledge base before recording, then upload another runbook live and immediately ask questions against the expanded knowledge base.

## LangGraph SQLite persistence memory

Every browser incident session has a persistent `thread_id`. The LangGraph workflow is compiled with a SQLite checkpointer and stores checkpoints in:

```text
data/langgraph_memory.sqlite
```

Example video demo:

**Question 1**

> Our checkout API is returning 502 errors after deployment. What should I check first?

**Question 2**

> What should I check next if that doesn't work?

For the second message, the `contextualize` node uses the persisted incident context and converts the follow-up into a standalone operational question before continuing through Self-RAG.

SQLite is intentionally used for the local demonstration. In a production implementation, you can explain that this persistence layer can be replaced with PostgreSQL or another production-grade LangGraph checkpointer/database.

## Recommended YouTube flow

### Demo A — Existing Pinecone knowledge

Ask:

> Our checkout API is returning 502 errors after deployment. What should the on-call engineer check first?

Expected route: **Private Runbooks**.

### Demo B — Persistent memory

Immediately ask:

> What should I check next if that does not work?

The same `thread_id` should reuse the previous incident context.

### Demo C — Upload new operational knowledge

Upload a new PDF/MD/DOCX from the UI. The status will show how many chunks were added to the existing namespace. Then ask a question whose answer exists only in the newly uploaded document.

### Demo D — Internet-search fallback

Ask about a technical issue that is not covered by any private runbook. Self-RAG first tries the private KB, grades the evidence, rewrites if necessary, and then transitions to **Internet Search** when internal evidence remains insufficient.

## Important configuration rule

The application and ingestion script both import `src/vectorstore.py`. That means they always use the same:

- OpenAI embedding model
- embedding dimension
- Pinecone index
- Pinecone namespace

This prevents a common RAG mistake where offline ingestion and runtime retrieval use different embeddings or different namespaces.
