# RAG-TUT — Step Into RAG From Scratch

A hands-on, module-by-module course that takes you from **"why does RAG exist?"** all the way to **building a production-style RAG application**.

Every module contains:

- **Concept chapters** (`.md`) — clear explanations with diagrams, real-world examples, and quizzes
- **Sample code** (`.py`) — runnable examples for each topic
- A **mini project** at the end that ties everything together

---

## Prerequisites

- Basic Python (functions, imports, file I/O)
- A basic idea of what an LLM API is (no RAG knowledge required)

### Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Some scripts need an OpenAI API key:

```bash
echo OPENAI_API_KEY=your-key > .env
```

Local embedding scripts (e.g. `all-MiniLM-L6-v2`) run fully offline.

> Add your own sample documents to `docs/` (any `.txt` files) and re-run the ingestion script to see the whole course work with your data.

---

## Course Map

| Module | Title | What you will learn | Sample code |
|---|---|---|---|
| 1 | Why RAG Exists | LLM limitations, hallucinations, knowledge cutoffs, private data, context windows, fine-tuning vs RAG, when NOT to use RAG | — |
| 2 | How RAG Works | The end-to-end pipeline: query → retrieval → generation | — |
| 3 | Document Loading | Loaders, PDF/DOCX/HTML/CSV, text extraction, metadata, enterprise ingestion | `01-loading-txt-pdf-docx.py`, `02-loading-web.py` |
| 4 | Chunking | Character vs recursive vs semantic splitters, chunk size & overlap | `01-recursive-vs-character-splitter.py` |
| 5 | Embeddings | Vectors, distance metrics, embedding models, visualizing similarity | `01-embeddings-basics.py` |
| 6 | Vector Databases | ChromaDB, FAISS, indexes, metadata filters, persistence | `01-ingestion-pipeline.py` |
| 7 | Retrieval | Similarity search, MMR, score thresholds, `k` selection, hybrid search | `01-retrieval-pipeline.py` |
| 8 | Generation | Grounded prompting, citations, answer quality, chat history | `01-answer-pipeline.py` |
| 9 | Advanced RAG | Query rewriting, multi-query, reranking, history-aware generation | `01-history-aware-generation.py` |
| 10 | Evaluation | Retrieval & answer metrics, RAGAS, failure analysis, iteration | `01-evaluation-basics.py` |
| 11 | Mini Project | Full company knowledge assistant — build it step by step | `step1_ingest.py` … `step5_chat.py` |

---

## Learning Path

```text
Module 1  →  Why RAG exists            (the problem)
Module 2  →  How RAG works             (the architecture)
Modules 3–8  →  Deep dives              (the building blocks)
Module 9  →  Advanced RAG              (make it better)
Module 10 →  Evaluation                (prove it works)
Module 11 →  Mini Project              (put it all together)
```

**Progression rule:** finish a module's chapters, run its sample code, then attempt the "Test yourself" quiz at the end of each chapter before moving on.

---

## Module Details

### Module 1 — Why RAG Exists
LLMs are prediction engines, not databases. Learn exactly which limitations make plain LLMs unreliable for enterprise knowledge, and why retrieval-augmented generation was invented to fix them.

### Module 2 — How RAG Works
A tour of the whole pipeline before any deep dives: user query → embedding → vector search → chunk retrieval → grounded generation.

### Module 3 — Document Loading
Every RAG system starts with getting text out of your sources. TXT, PDF, DOCX, HTML, CSV, databases, and web pages — plus metadata, cleaning, and enterprise ingestion patterns.

### Module 4 — Chunking
Why documents must be split, how different splitters behave, choosing chunk size and overlap, and avoiding split-related retrieval failures.

### Module 5 — Embeddings
How text becomes numbers, what similarity means in vector space, distance metrics, and choosing an embedding model.

### Module 6 — Vector Databases
Where embeddings live. ChromaDB and FAISS, collections, metadata filters, and persistence so you only ingest once.

### Module 7 — Retrieval
Getting the right chunks back. Similarity search, MMR for diversity, score thresholds, choosing `k`, and hybrid (keyword + vector) search.

### Module 8 — Generation
Turning retrieved evidence into trustworthy answers: grounded prompting, instructing the model to say "I don't know", citations, and chat history.

### Module 9 — Advanced RAG
Techniques that improve real systems: query rewriting, multi-query retrieval, reranking, and history-aware (conversational) RAG.

### Module 10 — Evaluation
How to know your RAG system is actually good: retrieval metrics, answer metrics, RAGAS, common failure modes, and a feedback loop.

### Module 11 — Mini Project
Build a **Company Knowledge Assistant** end-to-end:
1. Ingest PDFs and text files
2. Chunk and embed them
3. Store in a vector database
4. Retrieve with reranking
5. Answer with chat history and citations

---

## How to Run the Sample Code

Each module's scripts expect to be run from the **repo root** so relative paths like `docs/` and `db/chroma_db` work:

```bash
python "Module-4-Chunking/01-recursive-vs-character-splitter.py"   # needs nothing
python "Module-6-Vector-Databases/01-ingestion-pipeline.py"        # builds db/chroma_db from docs/
python "Module-7-Retrieval/01-retrieval-pipeline.py"               # needs the DB from step above
python "Module-8-Generation/01-answer-pipeline.py"                 # needs OpenAI API key
```

> Tip: run `Module-6` ingestion first — `Module-7`, `Module-8`, and `Module-9` read from the same `db/chroma_db` vector store.
