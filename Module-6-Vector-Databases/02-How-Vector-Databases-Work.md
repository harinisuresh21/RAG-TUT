# How Vector Databases Work

## Introduction

Chapter 01 made the case: at scale you cannot compare a query to every stored vector. This chapter answers the follow-up question — **how** does a vector database actually get away with searching without scanning everything?

The answer has three layers, and this chapter is a tour of all three:

```text
1. How vectors are stored
2. What an index is (approximate nearest neighbor)
3. What a collection is
```

You will not build an index by hand today — the database does that for you. But understanding what is happening under the hood tells you why ChromaDB works, why HNSW is the default, and why choosing the right "space" (metric) matters.

---

## Learning Objectives

By the end of this chapter, you will understand:

- How a vector database stores vectors and their text side by side
- What an index is and what "approximate nearest neighbor" means
- The HNSW index concept without the heavy math
- What a collection is and why you might have more than one

---

## How Vectors Get Stored

When you call `Chroma.from_documents(...)` (or `FAISS.from_texts(...)`), the database builds a record for every chunk:

```text
record
├── id          →  "abc123"
├── embedding   →  [0.23, 0.84, -0.11, ..., 0.07]   (384 numbers)
├── text        →  "Employees receive 30 annual leave days."
└── metadata    →  {"source": "docs/microsoft.txt"}
```

Every record has three parts you care about:

- The **embedding** — the numbers used for searching.
- The **text** — what you retrieve and feed to the LLM later.
- The **metadata** — extra facts you can filter on (chapter 05).

```text
Embedding = the address for searching
Text      = the content you actually get back
Metadata  = the tags you can filter on
```

Storage is two-sided: the vectors live in a structure built for fast search, and each vector points back to its text and metadata. When a search finds a winning vector, the database hands you the matching text — which is what RAG uses.

---

## What an Index Is

An **index** is an extra data structure the database builds over the vectors so it can answer "nearest to this query?" without checking everything.

The exact answer requires checking all vectors:

```text
EXACT search:  compare query to all 5,000,000 vectors → guaranteed best k
               but 5,000,000 comparisons per query → slow at scale
```

The fast answer accepts a tiny risk:

```text
APPROXIMATE search:  compare query to a small, well-chosen subset
                     → almost always the right answer, in milliseconds
```

This is **Approximate Nearest Neighbor (ANN)**: you trade an infinitesimal amount of accuracy for a massive speedup. In practice the "approximate" part is invisible — you get the same top chunks, orders of magnitude faster.

```text
Exact search     →  guaranteed best, slow
ANN index        →  almost guaranteed best, fast    ← what production uses
```

---

## The HNSW Index Concept

ChromaDB (and FAISS) default to an index called **HNSW** — Hierarchical Navigable Small World. It sounds intimidating, but the idea is a familiar one.

Think of how you find a restaurant in an unfamiliar city:

```text
1. Start at a friend's neighborhood (coarse layer)
2. Get directions to the right side of town
3. Zoom in, street by street, until you reach the block
4. Walk the last few steps
```

HNSW does the same thing with vectors. It builds **multiple layers** of connected "landmark" vectors:

```text
Layer 2 (coarse):  a few far-apart landmark vectors
Layer 1:           a medium grid connecting them
Layer 0 (fine):    every vector, densely connected

Search:
  query enters at Layer 2  →  jumps between landmarks
  moves down to Layer 1    →  narrower neighborhood
  arrives at Layer 0       →  walks the exact nearest neighbors
```

```text
Start at landmarks ──► narrow down ──► land near the answer
   (Layer 2)          (Layer 1)         (Layer 0)
```

Instead of measuring the distance to every vector, HNSW makes a series of "is this direction better?" hops. The result: nearest-neighbor search in milliseconds on millions of vectors.

> **Deep dive: covered in Module 7** — you do not need to tune HNSW to use it. ChromaDB wraps it so that `collection_metadata={"hnsw:space": "cosine"}` is all you ever type.

---

## What a Collection Is

A **collection** is a named group of vectors — think "table" in a relational database, or "folder" for your chunks.

```text
collection: "my_docs"
┌──────────────────────────────────────────────┐
│ id      │ embedding          │ text  │ metadata │
│ abc123  │ [0.23, ...]        │ ...   │ source   │
│ def456  │ [0.84, ...]        │ ...   │ source   │
│ ghi789  │ [-0.11, ...]       │ ...   │ source   │
└──────────────────────────────────────────────┘
```

Why you might keep separate collections:

```text
"hr_policies"     →  HR handbook chunks
"legal_contracts" →  contract clauses
"product_docs"    →  technical documentation
```

Separate collections let you search only the relevant world — e.g. ask the contracts DB, not the HR DB. Each collection carries its own metadata settings and its own embedding space.

---

## Real Enterprise Example

A company indexes 3 million chunks into a ChromaDB collection. A query arrives:

```text
"travel reimbursement policy"
```

Behind the scenes:

```text
1. The query is embedded → one 384-dim vector
2. HNSW index skips 2,999,900 chunks via coarse-to-fine hops
3. Exact cosine similarity runs on ~100 promising candidates
4. Top 5 chunks come back with their text and metadata
5. Total: ~30 milliseconds
```

The user never sees the index. They just get the right answer, fast — which is the entire point of this chapter.

---

## Key Takeaways

- Vectors are stored **side by side with their text and metadata**, pointing back to the chunk they represent.
- An **index** is a structure for answering nearest-neighbor queries without scanning everything.
- **ANN** (approximate nearest neighbor) trades a tiny accuracy risk for huge speed — production standard.
- **HNSW** searches coarse-to-fine through layered landmark vectors, like navigating a city.
- A **collection** is a named group of vectors, like a table — keep different corpora in different collections.

---

## Test Yourself

1. Besides the vector itself, what two things does the database store alongside it?
2. What does ANN stand for and what does it trade off?
3. In one sentence, how does HNSW avoid comparing the query to every vector?
4. What is a collection?
5. Why would a company keep HR chunks and legal chunks in separate collections?

<details>
<summary>Answers</summary>

1. The **chunk text** (what you retrieve) and its **metadata** (facts like source/date you can filter on).
2. **Approximate Nearest Neighbor** — it trades a tiny amount of accuracy for a huge speedup over exact search.
3. HNSW hops through **coarse-to-fine layers of landmark vectors**, narrowing down a neighborhood instead of measuring distance to every vector.
4. A **named group of vectors**, like a table — a named container holding embeddings, text, and metadata for one set of documents.
5. So queries can be scoped — searching only the contracts collection avoids HR chunks polluting legal answers, and keeps each collection smaller and faster.

</details>

---

## Next Chapter

Next up: [03-ChromaDB-Deep-Dive.md](03-ChromaDB-Deep-Dive.md) — a line-by-line walkthrough of the actual ingestion script that builds the course's ChromaDB store.
