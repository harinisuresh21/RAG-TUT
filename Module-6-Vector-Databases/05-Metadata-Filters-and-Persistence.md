# Metadata Filters and Persistence

## Introduction

A vector database is powerful, but sometimes you want it to search **a specific slice** of your knowledge base — only HR documents, or only documents updated this quarter. That is what **metadata filtering** is for.

And once your knowledge base is built, you do not want to rebuild it from scratch every time a document changes. That is what **persistence** is for.

This chapter covers both halves of operating a real vector store:

```text
1. Metadata filtering  →  search only the right subset of chunks
2. Persistence & re-ingestion  →  build once, reuse forever, stay idempotent
```

---

## Learning Objectives

By the end of this chapter, you will understand:

- What metadata filtering is and why it matters in the enterprise
- How metadata flows from loaders into chunks
- How to apply a `filter` in a similarity search or retriever
- The persistence pattern that keeps re-ingestion safe (idempotency)

---

## The Metadata Filtering Concept

Metadata is the "facts about the chunk" stored next to its vector. Recall the record from chapter 02:

```text
id         →  "abc123"
embedding  →  [0.23, 0.84, -0.11, ...]
text       →  "Employees receive 30 annual leave days."
metadata   →  {"source": "docs/microsoft.txt", "page": 3, "date": "2026-01-15"}
```

A **filter** narrows the search *before* similarity ranking:

```text
WITHOUT filter:  search all 2,000,000 chunks, rank by similarity
WITH filter:     search only the 50,000 HR chunks, rank by similarity
```

Enterprise examples:

```text
"only chunks from the HR department"        →  filter by source/department
"only contracts signed after Jan 2026"      →  filter by date
"only the latest version of a policy"       →  filter by version
```

The filter both **speeds up** the query (fewer candidates) and **improves quality** (out-of-scope chunks can never win, no matter how similar they are).

```text
Query: "leave policy" + filter source contains "hr"
  ✗ a legal contract that happens to mention leave → filtered out
  ✓ HR handbook chunks about leave → returned
```

---

## How Metadata Flows From Loaders Into Chunks

Metadata starts at the **loader** and rides along through the splitter into every chunk.

```text
TextLoader → Document(page_content="...", metadata={"source": "docs/microsoft.txt"})
     │
     ▼
CharacterTextSplitter.split_documents(...)
     │  (splits text, KEEPS metadata on each piece)
     ▼
Chunk A  →  metadata={"source": "docs/microsoft.txt"}
Chunk B  →  metadata={"source": "docs/microsoft.txt"}
Chunk C  →  metadata={"source": "docs/microsoft.txt"}
```

Because the ingestion script calls `splitter.split_documents(documents)` (not `split_text`), each chunk inherits its parent's metadata. That single line is why filtering works at all — no metadata carried, no filters possible.

You can enrich metadata beyond what the loader provides:

```python
from langchain_community.document_loaders import TextLoader

loader = TextLoader("docs/microsoft.txt", encoding="utf-8")
docs = loader.load()

for doc in docs:
    doc.metadata["department"] = "engineering"
    doc.metadata["date_added"] = "2026-08-05"
```

---

## Filtering a Similarity Search

With ChromaDB, pass a `filter` dict to `similarity_search`:

```python
# No filter — search everything
results_all = vectorstore.similarity_search("Who founded Microsoft?", k=5)

# Only chunks from microsoft.txt (matches on part of the source path)
results_ms = vectorstore.similarity_search(
    "Who founded Microsoft?",
    k=5,
    filter={"source": {"$contains": "microsoft"}}
)
```

Or attach the filter to a retriever:

```python
retriever = vectorstore.as_retriever(
    search_kwargs={
        "k": 5,
        "filter": {"source": {"$contains": "hr"}}
    }
)
relevant_docs = retriever.invoke("How many leave days do I get?")
```

Common ChromaDB filter operators:

```text
{"source": {"$contains": "microsoft"}}   →  string contains (case-sensitive)
{"department": {"$eq": "hr"}}            →  exact equality
{"date": {"$gte": "2026-01-01"}}         →  greater-or-equal (numbers/dates)
{"$and": [{"department": {"$eq": "hr"}}, {"date": {"$gte": "2026-01-01"}}]}
                                         →  combine conditions
```

> When a filter matches nothing, `similarity_search` returns an **empty list** — your code should handle that gracefully (the course script `02-metadata-filtering.py` shows exactly how).

---

## Persistence and Re-Ingestion (Idempotency)

The ingestion script's persistence trick is its **early-return check**:

```python
if os.path.exists(persistent_directory):
    print("Vector store already exists. No need to re-process documents.")
    vectorstore = Chroma(
        persist_directory=persistent_directory,
        embedding_function=embedding_model,
        collection_metadata={"hnsw:space": "cosine"}
    )
    print(f"Loaded existing vector store with {vectorstore._collection.count()} documents")
    return vectorstore
```

This is the pattern called **idempotency**: running the operation multiple times produces the same result as running it once.

```text
Run 1  →  store missing → full ingestion → saved to db/chroma_db
Run 2  →  store exists  → load it, return instantly (no re-embedding)
Run 3  →  same as run 2
```

### Why This Matters

Re-ingestion is expensive — every chunk must be re-split, re-embedded, re-indexed:

```text
100 documents → 20,000 chunks → 20,000 embedding calls
= minutes of compute and, if using an API model, real money
```

The idempotency check skips all of that when nothing changed.

### Re-Ingesting When Data Changes

The pattern only works if you rebuild when you *mean* to. To force a fresh index:

```text
1. Delete the store folder:     remove db/chroma_db   (or rm -rf db/chroma_db)
2. Re-run the ingestion script → builds everything again
```

```bash
Remove-Item -Recurse -Force db\chroma_db
python "Module-6-Vector-Databases/01-ingestion-pipeline.py"
```

A production system would instead ingest only *new or changed* documents and upsert their vectors — but the delete-and-rebuild flow is perfectly fine for this course and small corpora.

---

## Real Enterprise Example

A company keeps HR, legal, and engineering docs in one big store. Two scenarios show the filter + persistence pattern in action:

```text
Scenario 1 (filtering)
  Legal intern asks: "What is our liability cap?"
  Retriever filters source contains "legal" before ranking
  → HR and engineering chunks can never pollute the answer

Scenario 2 (persistence)
  Nightly job runs ingestion. Most nights the store exists,
  so it loads instantly and re-processing is skipped.
  When a new contract lands in docs/, the team re-runs after
  deleting db/chroma_db → the store rebuilds with the new chunk.
```

Both behaviors come from the two halves of this chapter: filter to the right slice, persist to avoid rework.

---

## Key Takeaways

- **Metadata filtering** restricts similarity search to a subset of chunks — faster and higher quality.
- Metadata flows **loader → document → chunks** because the splitter uses `split_documents`.
- ChromaDB filters use dicts like `{"source": {"$contains": "microsoft"}}` on `similarity_search` or `as_retriever`.
- An empty filter result returns an **empty list** — handle it gracefully.
- **Idempotent persistence** (the early-return check) skips re-ingestion when the store already exists.
- To intentionally rebuild, delete `db/chroma_db` and re-run the script.

---

## Test Yourself

1. What is metadata filtering, in one sentence?
2. Why must the splitter use `split_documents` (not `split_text`) for filters to work?
3. Write a ChromaDB filter that only matches chunks whose source contains `"legal"`.
4. What does `similarity_search` return when the filter matches nothing?
5. What makes the ingestion script "idempotent"?

<details>
<summary>Answers</summary>

1. Restricting similarity search to chunks that meet a metadata condition (source, date, department, etc.) before ranking by similarity.
2. Because `split_documents` **carries each document's metadata onto every chunk**; `split_text` returns plain strings with no metadata, so there would be nothing to filter on.
3. `filter={"source": {"$contains": "legal"}}`.
4. An **empty list** (`[]`) — no chunks matched the condition, so nothing to rank.
5. The `if os.path.exists(persistent_directory)` early-return: when the store already exists it loads it and returns immediately instead of re-processing the documents.

</details>

---

## Next Chapter

This is the last conceptual chapter of Module 6. Next up: [Module 7: Retrieval](../Module-7-Retrieval/README.md) — turning this store into a full retrieval pipeline with score thresholds, MMR, and tuned `k`.
