1. **`requirements.txt`** — Add all required libraries such as LangGraph, LangChain OpenAI, Pinecone, Tavily, FastAPI, SQLite LangGraph checkpointer, document loaders, etc.

2. **`.env`** — Configure OpenAI API key, OpenAI LLM model, `text-embedding-3-large`, Pinecone API key/index/namespace, Tavily API key, and other environment settings.

3. **`src/config.py`** — Load and centralize all `.env` configurations including OpenAI models, Pinecone settings, embedding dimension, Tavily settings, and SQLite persistence database path.

4. **`documents/`** — Add the sample CloudOps knowledge-base documents such as Checkout API 502 Runbook, Payments High CPU Runbook, and Production Deployment Rollback SOP.

5. **`src/ingestion.py`** — Build the reusable document loading and chunking pipeline for PDF, TXT, Markdown, and DOCX files. Use the same ingestion pipeline for initial knowledge-base creation and new document uploads from the UI.

6. **`src/vectorstore.py`** — Configure OpenAI `text-embedding-3-large`, connect with Pinecone, validate/create the Pinecone index, store document vectors, and create the retriever.

7. **`data_ingestion.py`** — Create the single data-ingestion script that loads the documents, chunks them, generates OpenAI embeddings, and uploads them into the existing Pinecone index and namespace.

8. **Run `python data_ingestion.py`** — Prepare the initial Pinecone knowledge base and verify that the vectors are available inside the configured Pinecone namespace.

9. **`src/models.py`** — Define the API request and response models for chat, persistent thread/session information, workflow traces, sources, and document uploads.

10. **`src/db.py`** — Configure SQLite for application audit/history storage.

11. **`src/self_rag.py`** — Build the main Self-RAG LangGraph workflow: **Memory → Contextualize Question → Retrieve → Grade Documents → Rewrite Query → Internet Search → Generate → IsSUP → Revise → IsUSE → Final Answer**.

12. **LangGraph SQLite Persistence** — Configure the SQLite LangGraph checkpointer inside the workflow, compile the graph with persistence, and use a stable `thread_id` so conversation and workflow state can persist across requests.

13. **Tavily Internet Search Fallback** — Add Tavily as the internet-search fallback when Pinecone does not contain sufficient relevant evidence: **Retrieve → Grade Fails → Rewrite Query → Internet Search → Grade Evidence → Generate Answer**.

14. **`app.py`** — Create the FastAPI application and endpoints for Self-RAG chat, persistent sessions, new sessions, document uploads, adding uploaded documents to the existing Pinecone knowledge base, and health/status checks.

15. **`templates/index.html`** — Build the CloudOps Sentinel Incident Command Center UI containing the chat interface, example incident prompts, Self-RAG workflow visualization, SQLite memory status, source information, and knowledge-base document upload section.

16. **`static/styles.css`** — Add the new CloudOps/SRE dashboard styling with a dark operations-console design, professional cards, workflow indicators, responsive layout, and completely different branding.

17. **`static/app.js`** — Connect the frontend with FastAPI and handle chat requests, persistent `thread_id`, new sessions, workflow traces, sources, Self-RAG status, memory information, and live document uploads.

18. **Run `python app.py`** — Start the complete CloudOps Sentinel Self-RAG application.

19. **Test Private Knowledge Base** — Ask: **“Our checkout API started returning 502 errors after a production deployment. What should the on-call engineer check first?”** This should retrieve relevant evidence from the Pinecone private knowledge base.

20. **Test Persistent Memory** — In the same session, ask: **“What should I check next if that doesn’t solve the issue?”** This demonstrates LangGraph SQLite persistence and conversation context using the same `thread_id`.

21. **Test Internet Search Fallback** — Ask: **“What are the latest recommended troubleshooting steps for Kubernetes ImagePullBackOff errors?”** This should demonstrate: **Pinecone → No Relevant Evidence → Query Rewrite → Tavily Internet Search → Grade → IsSUP → IsUSE → Final Answer**.

22. **Test Dynamic Knowledge-Base Update** — Upload a new PDF, DOCX, Markdown, or TXT runbook from the UI, add it to the existing Pinecone knowledge base, and then ask a question from the newly uploaded document to verify immediate retrieval.
