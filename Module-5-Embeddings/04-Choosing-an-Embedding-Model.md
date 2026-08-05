# Choosing an Embedding Model

## Introduction

Not all embeddings are the same. Different models use different numbers of dimensions, different training data, and different trade-offs between quality, speed, and cost. Choosing a model is a real engineering decision — but for this course there is one rule that matters more than any other:

```text
Whatever model you use at INDEX time,
you MUST use the same model at QUERY time.
```

In this chapter we compare the models this course actually uses — `all-MiniLM-L6-v2` and `text-embedding-3-small` — plus two you will meet in production (BGE and E5), and we show exactly how to swap models in the course scripts.

---

## Learning Objectives

By the end of this chapter, you will understand:

- The comparison between all-MiniLM-L6-v2 and text-embedding-3-small
- What BGE and E5 are and when you might reach for them
- The multilingual caveat
- How to change the embedding model in the existing ingestion script
- Why the query-time model must be identical to the index-time model

---

## Comparison Table

| Model | Dims | Runs where | Cost | Best for |
|---|---|---|---|---|
| `all-MiniLM-L6-v2` (Hugging Face) | 384 | Local, offline | Free | Learning, prototypes, private data |
| `text-embedding-3-small` (OpenAI) | 1536 | OpenAI API | Per-token API fee | Production-quality, English-heavy content |
| BGE (BAAI, `bge-small` / `bge-large`) | 384 / 1024 | Local or API | Free to self-host | Chinese + English, strong retrieval leaderboards |
| E5 (`e5-small` / `e5-large`) | 384 / 1024 | Local or API | Free to self-host | General retrieval, designed for search tasks |

Quick rules of thumb:

```text
Just learning?            → all-MiniLM-L6-v2 (runs offline, instant)
Need top quality, no GPU? → text-embedding-3-small (API call)
Need multilingual?        → BGE / E5 or a model trained for your languages
```

---

## all-MiniLM-L6-v2 — the Course Default (Local)

This is the model used to build the vector store in Module 6:

- **384 dimensions** — compact, fast, small.
- **Runs fully offline** on your machine via the `sentence-transformers` package.
- The weights download once on first use (~90 MB), then it never needs the network again.
- Great quality-to-size ratio for a learning course and for internal data that must not leave your network.

In code it appears in `Module-6-Vector-Databases/01-ingestion-pipeline.py`:

```python
from langchain_huggingface import HuggingFaceEmbeddings

embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
```

---

## text-embedding-3-small — the API Option

This is the model the course's *retrieval* scripts use:

- **1536 dimensions** — more room to encode meaning.
- Runs on **OpenAI's servers**, so it needs an `OPENAI_API_KEY` in your `.env` file:

```text
OPENAI_API_KEY=sk-your-key
```

- You pay a small per-token fee for every chunk embedded and every query embedded.
- Requires internet access at both index time and query time.

In code it appears in `Module-7-Retrieval/01-retrieval-pipeline.py`:

```python
from langchain_openai import OpenAIEmbeddings

embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
```

> **Important:** because the ingestion pipeline in Module 6 uses `all-MiniLM-L6-v2` and the retrieval script in Module 7 uses `text-embedding-3-small`, the two scripts in this course do **not** currently share a model — Module 7 is written so you can swap in the same local model. Section "Changing the Model" below shows you exactly how.

---

## BGE and E5 — Worth Knowing

### BGE (BAAI)

A family of strong open-source embedding models, available in sizes like `bge-small-en-v1.5` (384 dims) and `bge-large-en-v1.5` (1024 dims). Known for:

- Excellent retrieval leaderboard results.
- Strong **bilingual** Chinese/English performance.
- Easy to run locally, same way as MiniLM:

```python
embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
```

### E5 (Microsoft)

Embedding models explicitly trained as *retrieval* encoders. In their older versions they famously required a prefix like `"passage: "` / `"query: "` before text. Newer versions removed that. If you see an E5 model in a pipeline, it will usually come wrapped in a custom function.

You do not need to master either today. Just know they exist, they are strong open-source alternatives to OpenAI, and their key difference from MiniLM is usually **size and training focus**.

---

## The Multilingual Caveat

`all-MiniLM-L6-v2` and `text-embedding-3-small` are primarily **English-trained**.

If your documents are in another language (or a mix), embeddings can degrade because the model never learned fine-grained meaning in that language. Symptoms:

```text
Hindi / Spanish / Chinese queries  →  lower similarity scores
Correct chunks rank lower than wrong ones
```

If you need multiple languages, pick a model built for them — e.g. `BAAI/bge-m3` or a multilingual embedding model — and test it on your actual data before trusting it.

```text
English-only model + French documents  →  risky, test first
Multilingual model (bge-m3 etc.)       →  safer for mixed languages
```

---

## How to Change the Model in the Existing Scripts

The ingestion script builds embeddings in one place:

```text
Module-6-Vector-Databases/01-ingestion-pipeline.py
  → create_vector_store()  and  main() (early-return block)
  → HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
```

To switch to another local model, change the `model_name`:

```python
embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
```

To switch to the OpenAI model, replace the class and name:

```python
from langchain_openai import OpenAIEmbeddings
embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
```

**You must change BOTH spots in the ingestion script** — the one in `create_vector_store()` and the one in the early-return block of `main()` that loads an existing store. And if you change the store's model, you must re-run the ingestion from scratch (delete `db/chroma_db`) because the old vectors were made with the old model.

---

## The Golden Rule: Same Model at Index and Query

This is the most important fact in this chapter:

```text
Vectors from different models cannot be compared meaningfully.

[0.2, 0.9, -0.1, ...]   ← all-MiniLM-L6-v2 embedding of "leave policy"
[0.7, 0.1, 0.4, 0.8, ...] ← text-embedding-3-small embedding of "vacation"
```

Each model has its **own coordinate system**. MiniLM and OpenAI place the same word at totally different coordinates. If you index with MiniLM but query with OpenAI, the database compares points from two different maps — the result is garbage.

```text
Index with MiniLM + query with MiniLM  →  ✓ correct comparisons
Index with MiniLM + query with OpenAI  →  ✗ meaningless scores
Index with OpenAI + query with MiniLM  →  ✗ meaningless scores
```

The vector database does not know you made a mistake. It dutifully computes "similarity" between vectors that were never meant to be compared.

**How to stay safe:**

```text
1. Pick ONE model for the whole system.
2. Use it in every place embeddings are created:
   ingestion script, retrieval scripts, evaluation scripts.
3. If you change the model, re-ingest the entire corpus.
```

---

## Real Enterprise Example

A legal team indexes 200,000 contract clauses with `all-MiniLM-L6-v2` to keep data offline. Later, a new engineer "upgrades" the query script to `text-embedding-3-small` because it is "better". Suddenly every search returns nonsense.

```text
Before:   index MiniLM  +  query MiniLM  →  top results relevant ✓
After:    index MiniLM  +  query OpenAI  →  top results random    ✗
```

The engineer re-indexes the corpus with the OpenAI model (or switches the query script back). **The model is a system-wide decision, not a per-script one.**

---

## Key Takeaways

- `all-MiniLM-L6-v2` (384 dims, local, free, offline) vs `text-embedding-3-small` (1536 dims, API, needs key).
- BGE and E5 are strong open-source alternatives, often multilingual or retrieval-tuned.
- MiniLM and the OpenAI small model are **English-focused** — test before using on other languages.
- To change models, edit the embedding class/name in the ingestion script and re-ingest from scratch.
- **The same embedding model must be used at index time and query time** — different models produce vectors in different coordinate systems that cannot be compared.

---

## Test Yourself

1. How many dimensions does `all-MiniLM-L6-v2` produce? How many does `text-embedding-3-small`?
2. Which of the two course models runs fully offline with no API key?
3. Name one open-source alternative to MiniLM/OpenAI models, and one thing it is known for.
4. If your documents are in Spanish, what should you check before committing to `all-MiniLM-L6-v2`?
5. What happens if you index with MiniLM but query with text-embedding-3-small?

<details>
<summary>Answers</summary>

1. `all-MiniLM-L6-v2` → **384**; `text-embedding-3-small` → **1536**.
2. **`all-MiniLM-L6-v2`** — it runs locally via `sentence-transformers` and never needs an API key or network after the initial weight download.
3. **BGE** (e.g. `BAAI/bge-small-en-v1.5`) — strong retrieval performance and good Chinese/English support. **E5** is another open alternative, trained specifically for retrieval.
4. Check whether the model is **multilingual**. MiniLM is English-focused, so scores for Spanish text may degrade; consider a multilingual model like `bge-m3` and test on real data.
5. The scores become **meaningless** — the two models use different coordinate systems, so the database compares vectors that were never meant to be compared. You must use one model everywhere (and re-ingest if you switch).

</details>

---

## Next Chapter

Next up: [05-Visualizing-Embeddings.md](05-Visualizing-Embeddings.md) — how to see your high-dimensional vectors with your own eyes.
