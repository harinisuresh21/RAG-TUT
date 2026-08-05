# Similarity Score Thresholds

## Introduction

Plain similarity search always returns `k` chunks — even when nothing in the store is really related to the query. If an employee asks about a topic your documents barely cover, the top-5 will still contain five chunks, most of them noise.

Score thresholds fix this: **only return chunks whose similarity score is high enough.**

---

## Learning Objectives

By the end of this chapter, you will:

- Understand the `similarity_score_threshold` search type
- Explain what `score_threshold` filters out
- Describe the too-high / too-low trade-off
- Read and interpret a worked example with real scores

---

## The Commented-Out Code

`01-retrieval-pipeline.py` has an alternative retriever sitting in a comment. Uncomment it (and comment out the plain one) to switch search types:

```python
retriever = db.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={
        "k": 5,
        "score_threshold": 0.3  # Only return chunks with cosine similarity ≥ 0.3
    }
)
```

Two new pieces:

- `search_type="similarity_score_threshold"` — switch from "always give me k chunks" to "give me chunks that are good enough".
- `score_threshold=0.3` — only chunks whose similarity to the query is **at least 0.3** come back.

`k` now becomes an **upper bound**: the store returns *at most* `k` chunks, and only the ones that clear the threshold. It may return fewer — even zero.

---

## What the Threshold Filters Out

The threshold acts as a quality gate:

```text
Without threshold:  5 chunks returned, no matter how weak they are
With threshold:     only chunks with similarity ≥ 0.3 come back
```

Example: an employee asks *"How many vacation days do I get?"* and your library only contains procurement contracts.

```text
chunk (procurement)  sim 0.18  ← below 0.3, dropped
chunk (procurement)  sim 0.15  ← dropped
chunk (procurement)  sim 0.12  ← dropped
...
→ retriever returns 0 chunks
```

That is a *feature*: the system now knows it has no evidence, and the generation step (Module 8) can honestly say *"I don't have enough information."*

---

## The Trade-off: Too High vs Too Low

Threshold tuning is a balance:

```text
Threshold too HIGH  →  nothing passes → the LLM gets no context
Threshold too LOW   →  everything passes → noise creeps back in, threshold is pointless
```

```text
0.8  →  almost nothing qualifies   (fine for a tiny, precise store)
0.5  →  still quite strict
0.3  →  a common starting point     (used in the sample script)
0.1  →  almost everything qualifies (barely filters at all)
```

When the store is small (three docs), 0.3 is a good starting point. If you routinely get **no results**, lower it. If you get **irrelevant results**, raise it.

---

## Worked Example Scores

Query: *"How much did Microsoft pay to acquire GitHub?"*

Imagine these are the similarity scores Chroma computes:

```text
chunk A  microsoft.txt  "GitHub for $7.5 billion"               sim 0.78
chunk B  microsoft.txt  "ZeniMax ... about $7.5 billion"        sim 0.41
chunk C  microsoft.txt  "LinkedIn for $26.2 billion"            sim 0.38
chunk D  microsoft.txt  "Activision Blizzard ... $68.7 billion" sim 0.35
chunk E  microsoft.txt  "Yammer for US$1.2 billion"             sim 0.31
chunk F  nvidia.txt     "NVIDIA's first graphics accelerator"   sim 0.09
```

Now set different thresholds and see what comes back (with `k = 5`):

```text
threshold 0.8  →  nothing (0.78 < 0.8)              → no evidence
threshold 0.4  →  chunk A only                      → focused, but risky
threshold 0.3  →  chunks A, B, C, D, E              → good coverage
threshold 0.0  →  A, B, C, D, E, plus F and more    → noise included
```

0.3 is the sweet spot here: it keeps the relevant acquisitions and drops the unrelated NVIDIA chunk. Note that chunk F (sim 0.09) would have entered the prompt with a very low threshold — exactly the noise you want to avoid.

---

## Enterprise Example

A contract-management assistant is asked about *indemnification clauses*. Your contract corpus has one relevant clause scoring 0.71 and dozens of invoices scoring below 0.15. With `score_threshold=0.5` the assistant returns exactly the clause — and with nothing else, it returns an empty list, prompting a truthful "I don't know" instead of a hallucinated invoice summary.

---

## Key Takeaways

- `similarity_score_threshold` + `score_threshold` returns only chunks **similar enough**.
- `k` becomes an upper bound; the store may return **fewer than k**, or zero.
- **Too high** → no results; **too low** → noise (the threshold is pointless).
- Zero results is useful: it lets the system admit it doesn't know.
- 0.3 is a reasonable starting point; tune by watching what comes back.

---

## Test Yourself

1. What does `search_type="similarity_score_threshold"` change compared to default retrieval?
2. In the sample script, what does `score_threshold: 0.3` mean?
3. What happens if the threshold is 0.8 and the best chunk scores 0.78?
4. What is the trade-off of setting the threshold too low?
5. Why can returning zero chunks be a good thing?

<details>
<summary>Answers</summary>

1. Instead of always returning `k` chunks, the retriever only returns chunks whose similarity score **clears the threshold** — possibly fewer than `k`.
2. Only chunks with cosine similarity **≥ 0.3** are returned.
3. Nothing is returned — even the best chunk fails the threshold, so the retriever returns **zero chunks**.
4. Too low means **noise sneaks back in** — irrelevant chunks fill the prompt and the threshold filters almost nothing.
5. Zero chunks tells the system it has **no evidence**, so generation can honestly say "I don't have enough information" instead of hallucinating.

</details>

---

## Next Chapter

Next up: [04-MMR-for-Diversity.md](04-MMR-for-Diversity.md) — what to do when the top-k chunks all repeat the same fact.
