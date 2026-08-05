# Similarity and Distance Metrics

## Introduction

We now have the mental picture: embeddings are arrows in space, and similar meaning means similar direction. But the vector database cannot *look* at arrows. It needs a **number** it can sort.

That number comes from a **similarity or distance metric** — a formula that takes two vectors and answers one question:

```text
"How similar are these two pieces of text?"
```

In this chapter we cover the three metrics you will meet in RAG, spend most of our time on **cosine similarity** (the default in this course), and walk through a tiny worked example with real numbers.

---

## Learning Objectives

By the end of this chapter, you will understand:

- What cosine similarity is and why it is the most common choice in RAG
- The idea behind dot product and euclidean distance
- How the cosine formula works conceptually (no scary math)
- How to read similarity scores from a worked example
- When to use which metric

---

## The Three Metrics

### Cosine Similarity — the Default

Cosine similarity measures the **angle** between two vectors. It ignores *how long* the arrows are and only cares about *which way they point* — which, as we learned in chapter 02, is exactly the signal that encodes meaning.

```text
small angle  → cosine ≈ 1.0   → very similar
right angle  → cosine ≈ 0.0   → unrelated
big angle    → cosine < 0.0   → opposite meaning
```

The score always lands between **-1 and 1**, and RAG pipelines almost always see scores between 0 and 1 for real text.

```text
  cos = 0.95                cos = 0.5            cos ≈ 0
  "leave policy"            "leave policy"       "leave policy"
  "vacation rules"          "payroll system"     "security policy"
  (nearly identical        (somewhat related,   (unrelated,
   direction)                moderate angle)      perpendicular)
```

Because it is robust to sentence length (a long detailed chunk and a short query about the same topic still point the same way), **cosine is the default metric in this course** — and in most of the industry.

### Dot Product — Similarity With an Attitude

The dot product also considers direction, but it **multiplies the lengths** of the vectors in:

```text
dot product = |a| × |b| × cos(angle)
```

For two vectors of the same length, dot product and cosine agree. But if one vector is very long, the dot product inflates the score even when the direction is only roughly aligned. That makes it useful when you *want* length to matter (e.g. term-frequency models), and dangerous when you don't.

### Euclidean Distance — the "Straight Line" Measure

Euclidean distance is the ordinary straight-line distance between two points — the same idea as measuring between two dots on a map.

```text
distance = length of the straight line from vector A to vector B
```

Small distance = similar. But here is the catch: two chunks about the same topic, one short and one long, can point in the same direction yet sit far apart in *distance* because one vector is much longer. That is why distance-based measures are often the wrong tool for text embeddings, where length mostly reflects verbosity, not meaning.

---

## The Cosine Formula (Concept, Not Math)

You may see the formula in code or docs:

```text
cos(angle between a and b) =  (a · b) / (|a| × |b|)

  a · b   →  the dot product: how much the two arrows agree
  |a|     →  the length of arrow a
  |b|     →  the length of arrow b
```

Here is all you need to remember about it:

```text
"the dot product of the arrows, divided by both arrows' lengths"
```

Dividing by the lengths is what **normalizes** away size differences — the whole trick that makes two vectors of very different lengths comparable. You do not need to compute this by hand in practice; `numpy` does it for you in the sample script.

---

## Worked Tiny Example

Let's squeeze three ideas into 2D space to see the numbers with our own eyes. We assign each idea a 2D vector (real embeddings are 384-dimensional, but the arithmetic works the same):

```text
"leave"    →  (1.0, 0.0)
"vacation" →  (0.9, 0.1)
"security" →  (0.0, 1.0)
```

Computing cosine similarity between each pair (this is exactly what `01-embeddings-basics.py` does with numpy, but at 384 dimensions):

```text
"leave" vs "vacation":   (1.0×0.9 + 0.0×0.1) / (1.0 × 0.906)  ≈  0.99   ← very similar
"leave" vs "security":   (1.0×0.0 + 0.0×1.0) / (1.0 × 1.0)    ≈  0.00   ← unrelated
"vacation" vs "security": (0.9×0.0 + 0.1×1.0) / (0.906 × 1.0) ≈  0.11   ← unrelated
```

The similarity matrix (the same shape the script prints):

```text
            leave    vacation    security
leave       1.000     0.990       0.000
vacation    0.990     1.000       0.110
security    0.000     0.110       1.000
```

Read it this way:

```text
Diagonal = 1.000     →  every vector is perfectly similar to itself
leave ↔ vacation = 0.99  →  near-identical meaning ✓
leave ↔ security = 0.00  →  completely different topic ✓
```

A retrieval system sorts chunks by this score and keeps the top `k`. The chunk about vacation wins for a leave query; the security chunk is never retrieved.

---

## When to Use Which

```text
Cosine similarity   →  DEFAULT for text embeddings
                      ✓ robust to sentence length
                      ✓ bounded -1..1, easy to threshold
                      ✓ what ChromaDB uses with {"hnsw:space": "cosine"}

Dot product         →  when vector length is meaningful
                      (word-frequency style models, not MiniLM)

Euclidean distance  →  when vectors are already normalized or length is meaningful
                      (rarely the first choice for embedding search)
```

Rule of thumb for this course: **start with cosine**. It is the setting baked into our ingestion script and it rarely steers you wrong.

---

## Real Enterprise Example

An HR bot searches an employee handbook for *"how many days of parental leave"*.

```text
Chunk A: "New parents receive 16 weeks of parental leave."      cos ≈ 0.91
Chunk B: "Parental leave can be taken within the first year."    cos ≈ 0.88
Chunk C: "The office dress code is business casual."             cos ≈ 0.15
```

Cosine cleanly ranks A and B at the top and keeps C out of the answer. If instead the pipeline used euclidean distance on un-normalized vectors, chunk length could accidentally shuffle this ordering — one more reason cosine is the default.

---

## Key Takeaways

- **Cosine similarity** measures the *angle* between vectors and is the default metric for text embeddings.
- **Dot product** adds vector length into the score; use it only when length carries meaning.
- **Euclidean distance** is the straight-line gap between points and can punish verbose chunks unfairly.
- The cosine formula is just "dot product divided by both lengths" — dividing by lengths cancels size differences.
- Scores from a similarity matrix read naturally: diagonal = 1.0, related pairs high, unrelated pairs near 0.

---

## Test Yourself

1. What does cosine similarity actually measure about two vectors?
2. What range of values can cosine similarity produce?
3. Why does dividing by both vector lengths (the denominator in the cosine formula) matter?
4. A query is compared to two chunks: one short and one long, about the same topic. Which metric is most likely to give them similar scores, cosine or euclidean distance?
5. In the worked example, why did "leave" vs "security" score near 0.00?

<details>
<summary>Answers</summary>

1. The **angle between the two vectors** — how similarly they point — ignoring how long they are.
2. Between **-1 and 1**. For typical text embeddings the values you care about fall between 0 and 1.
3. It **normalizes away vector length**, so a long and a short vector about the same topic still get compared fairly. Without it, length would dominate the score.
4. **Cosine similarity**, because it ignores length; euclidean distance would see the longer vector as "farther" even though the meaning matches.
5. Because `(1.0, 0.0)` and `(0.0, 1.0)` point in **perpendicular directions** — the angle between them is 90°, whose cosine is 0. The topics are unrelated, and the score reflects it.

</details>

---

## Next Chapter

Next up: [04-Choosing-an-Embedding-Model.md](04-Choosing-an-Embedding-Model.md) — which embedding model to pick, and the rule that index-time and query-time models must match.
