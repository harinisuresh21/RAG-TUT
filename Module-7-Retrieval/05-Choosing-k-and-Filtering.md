# Choosing k and Filtering

## Introduction

Retrieval gives you two more practical levers: **how many** chunks to grab (`k`), and **which slices** of the store to search at all (metadata filtering). Get both right and your prompt is focused and cheap. Get them wrong and you either miss facts or drown the LLM in noise.

---

## Learning Objectives

By the end of this chapter, you will:

- Choose a sensible `k` for a given task
- Explain the cost and quality consequences of a large `k`
- Combine a metadata filter with retrieval
- Know when filtering is and isn't enough

---

## Choosing `k`: The 3–5 Rule of Thumb

`k` is the number of chunks in the prompt. For typical enterprise setups the sweet spot is **3 to 5**:

```text
k = 3  →  tight, focused context  (great for simple, single-fact questions)
k = 5  →  the default in this course (covers multi-fact questions)
k = 10 →  when chunks are small or the question spans many topics
```

Think about what a question needs:

```text
"How much did Microsoft pay for GitHub?"   → 1 fact → k = 3 is plenty
"What are all Microsoft's acquisitions?"   → many facts → k = 10
```

Start at `k = 3–5`, look at what the retriever actually returns, and tune from there.

---

## Why Too Many Chunks Hurts

A big `k` sounds safer, but it costs you twice:

```text
Noise →  irrelevant chunks confuse the model and can crowd out the right answer
Cost  →  every extra chunk spends tokens before the model even writes a word
```

Example: `k = 20` with 1,000-character chunks is ~20,000 characters of context — before the LLM starts answering. If 18 of those chunks are irrelevant, you paid for confusion.

```text
k too small  →  the fact you need never arrives → the LLM guesses
k too large  →  the prompt is noisy and expensive → the LLM hedges
```

---

## Filtering Before Searching

Metadata filters shrink the search space **before** similarity is even computed. If your documents carry `source` metadata (they do — the loader stores it), you can restrict retrieval to a single file:

```python
retriever = db.as_retriever(
    search_kwargs={
        "k": 5,
        "filter": {"source": "docs/microsoft.txt"}
    }
)
```

With the filter, only chunks from `microsoft.txt` are candidates. The NVIDIA and Google chunks are never even scored — cheaper and cleaner.

---

## Filtering in Practice

Two ways to combine a filter with retrieval in LangChain:

### 1. Pass the filter through `as_retriever`

```python
retriever = db.as_retriever(
    search_kwargs={
        "k": 5,
        "filter": {"source": "docs/microsoft.txt"}
    }
)
```

### 2. Search directly on the store

```python
relevant_docs = db.similarity_search(
    query,
    k=5,
    filter={"source": "docs/microsoft.txt"}
)
```

Both return only chunks whose metadata matches the filter. The `filter` dictionary keys correspond to the **metadata keys** stored at ingestion time.

---

## When Filtering Is Not Enough

Filters only work if your metadata is good. If the ingest step (Modules 3–6) did not tag documents with useful fields, there is nothing to filter on. Two real-world patterns:

```text
Department → filter to HR chunks only              {"source": "docs/hr/remote-work.txt"}
Date/version → filter to the latest contract       {"contract_year": 2025}
```

If you find yourself needing "the newest version" or "only the HR department", that is a signal to add that metadata during **ingestion**, not to work around its absence at retrieval time.

---

## Enterprise Example

A legal assistant handles *2025 supplier contracts*. The corpus has contracts from many years. With `k = 3` plus `filter={"contract_year": 2025}` it searches only this year's contracts — three focused chunks, no old-contract noise, and a small prompt.

---

## Key Takeaways

- Start at **`k = 3–5`**; raise it for broad questions, lower it for single-fact ones.
- A large `k` means **noise and token cost**, not automatically better answers.
- **Metadata filters** (`filter={"source": ...}`) restrict the search space before scoring.
- Filters depend on good metadata from ingestion.
- Combine a reasonable `k` + a filter for the cheapest, cleanest retrieval.

---

## Test Yourself

1. What is the recommended starting range for `k`?
2. Name two costs of setting `k` too high.
3. Write a retriever that returns at most 5 chunks only from `docs/nvidia.txt`.
4. What do the keys of a `filter` dictionary correspond to?
5. Why is good metadata a prerequisite for filtering?

<details>
<summary>Answers</summary>

1. **3 to 5** chunks for typical enterprise questions.
2. **Noise** (irrelevant chunks confuse the model) and **cost** (every extra chunk spends tokens).
3.
   ```python
   retriever = db.as_retriever(
       search_kwargs={"k": 5, "filter": {"source": "docs/nvidia.txt"}}
   )
   ```
4. The **metadata keys** that were stored on each chunk at ingestion time (e.g. `source`).
5. Without metadata there is **nothing to filter on** — the search space can't be narrowed, so irrelevant chunks stay in the candidate pool.

</details>
