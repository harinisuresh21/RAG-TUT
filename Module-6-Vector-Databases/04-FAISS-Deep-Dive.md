# FAISS Deep Dive

## Introduction

ChromaDB is a *database* — it persists to disk and you can load it back later. But there is a whole other family of tools for vector search: **indexing libraries**. The most famous is **FAISS** (Facebook AI Similarity Search), developed by Meta.

Where ChromaDB is a database with vectors, FAISS is a blazing-fast *library* that specializes in the math of similarity search. LangChain wraps it so you get the speed without touching C++:

```python
from langchain_community.vectorstores import FAISS
```

In this chapter we compare Chroma and FAISS, then look at a complete build/save/load cycle you will run yourself in `03-faiss-example.py`.

---

## Learning Objectives

By the end of this chapter, you will understand:

- What FAISS is and how it differs from a full vector database
- A practical Chroma vs FAISS comparison
- When to choose each
- How to build a FAISS store from text, save it, and reload it in LangChain

---

## What FAISS Is

FAISS is a **library for similarity search and clustering of dense vectors**. It provides the index structures (including HNSW) and the math, but it is *not* a database server:

```text
ChromaDB                 FAISS
────────                 ─────
Vector database          Vector indexing library
Persists full store      Stores only the index (vectors + ids)
Has metadata & filtering Has no built-in metadata logic
You query it directly    You query it in your own Python code
```

LangChain's `FAISS` class wraps the raw library into the same interface you already know — `similarity_search`, `as_retriever`, `from_documents` — so switching between Chroma and FAISS feels familiar.

---

## Chroma vs FAISS — Comparison Table

| Feature | ChromaDB (`langchain_chroma`) | FAISS (`langchain_community.vectorstores.FAISS`) |
|---|---|---|
| Type | Vector **database** | Vector **indexing library** |
| Persistence | Full store on disk (`db/chroma_db`) | Index files saved with `save_local` |
| Metadata filtering | Built-in, rich `filter=` | No native filtering; you filter the returned docs yourself |
| Deployment | Can run as embedded or a server | Always embedded in your process |
| Best for | Easy, persistent, filterable app databases | Maximum search speed embedded in Python |
| Extra | Collection concept, HNSW config | Raw FAISS speed, GPU support |

When to choose which:

```text
CHOOSE ChromaDB when:
  - you want persistence + metadata filters out of the box
  - you are building the course's main knowledge base
  - you want a familiar "database" mental model

CHOOSE FAISS when:
  - search speed is your bottleneck
  - your vectors live in memory for a session
  - you need a small, fast index embedded in your app
```

Rule of thumb for this course: **ChromaDB for the main store, FAISS as your second tool**. Many production systems use both — FAISS for hot in-memory search, a database for the durable record.

---

## Building a FAISS Store (Build, Save, Load)

Here is the complete lifecycle in LangChain — exactly what `03-faiss-example.py` runs:

```python
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# 1. Embedding model (same one used at query time)
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# 2. Example sentences
sentences = [
    "Employees receive 30 annual leave days per year.",
    "Vacation requests must be approved by the manager.",
    "The office dress code is business casual.",
]

# 3. Build the store in memory
vectorstore = FAISS.from_texts(sentences, embedding_model)

# 4. Search
results = vectorstore.similarity_search("How many leave days do I get?", k=2)

# 5. Save to a local folder
vectorstore.save_local("db/faiss_index")

# 6. Reload later
loaded = FAISS.load_local(
    "db/faiss_index",
    embedding_model,
    allow_dangerous_deserialization=True,
)
```

Notes on the pieces:

```text
from_texts(...)            →  embed the sentences and build an index in memory
similarity_search(query)   →  nearest-neighbor search, same interface as Chroma
save_local("db/faiss_index") →  writes index files + metadata to a folder
load_local(...)            →  reloads; the flag allows reading a serialized index
```

`allow_dangerous_deserialization=True` is required by recent LangChain versions because loading an index can execute pickled code — safe when the index came from your own machine, which is always true in this course.

```text
db/faiss_index/
├── index.faiss       ← the actual vector index
├── index.pkl         ← the stored document texts + metadata
```

The `.faiss` file holds the vectors; the `.pkl` file holds the chunk text and metadata so retrieval returns real sentences, not just coordinates.

---

## Real Enterprise Example

A trading desk needs sub-millisecond similarity search over 20 million trade-desk note chunks. They:

```text
1. Embed all chunks with the chosen embedding model
2. Build a FAISS index in memory at service startup
3. Serve similarity searches from RAM (no disk, no server round-trip)
4. Keep the durable record in a database for recovery
```

ChromaDB would also work at this scale, but FAISS's in-memory speed is the reason the team picked it. The decision was about **hot-path performance**, not correctness — both return the same nearest neighbors.

---

## Key Takeaways

- **FAISS** is an indexing *library*, not a database — raw speed over features.
- **Chroma** gives you persistence + metadata filtering; **FAISS** gives you speed + memory.
- The LangChain `FAISS` wrapper keeps the same interface: `from_texts`, `similarity_search`, `save_local`, `load_local`.
- `save_local` writes `index.faiss` (vectors) and `index.pkl` (texts + metadata) to a folder.
- Reloading requires `allow_dangerous_deserialization=True` — fine for your own local indexes.

---

## Test Yourself

1. Is FAISS a vector database or an indexing library?
2. Name two things ChromaDB has out of the box that raw FAISS does not.
3. Which method builds a FAISS store from a list of sentences?
4. What two files does `save_local` write to `db/faiss_index`?
5. Why does `load_local` need `allow_dangerous_deserialization=True`?

<details>
<summary>Answers</summary>

1. An **indexing library** (a library for fast similarity search over dense vectors), not a full database.
2. **Persistence as a full store** and **built-in metadata filtering** (plus collections and a server option).
3. **`FAISS.from_texts(sentences, embedding_model)`**.
4. **`index.faiss`** (the vector index) and **`index.pkl`** (the stored document texts and metadata).
5. Because loading a serialized index can execute pickled code; the flag confirms you trust the source — safe for indexes you created locally.

</details>

---

## Next Chapter

Next up: [05-Metadata-Filters-and-Persistence.md](05-Metadata-Filters-and-Persistence.md) — filtering chunks by source and date, and the persistence pattern that makes re-ingestion safe.
