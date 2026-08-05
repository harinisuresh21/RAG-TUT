# What Is an Embedding?

## Introduction

Every RAG pipeline has a moment where **text becomes numbers**. That moment is the embedding.

A user asks:

```text
"How many annual leave days do I get?"
```

The system must find the chunk in the company handbook that answers this. But computers do not "understand" words the way we do — they work with numbers. So before anything can be searched, we need a way to translate text into a form a computer can compare.

An **embedding** is exactly that translation: a piece of text (a word, a sentence, a whole chunk) converted into a **list of numbers** — a vector — that captures its meaning.

---

## Learning Objectives

By the end of this chapter, you will understand:

- What an embedding is and how text becomes a list of numbers
- What the *dimensions* of an embedding actually mean
- Why numbers are better than keywords for finding meaning
- Why "leave policy" and "vacation rules" end up close together while "security policy" sits far away

---

## Text → List of Numbers

Here is the core idea, in one line:

```text
"leave policy"  →  [0.23, 0.84, -0.11, ...]
```

The text `"leave policy"` has been turned into a vector. A vector is just a list of numbers, one for each *dimension* of the model:

```text
"leave policy"
  dimension 1 →  0.23
  dimension 2 →  0.84
  dimension 3 → -0.11
  ...
  dimension 384 →  0.07
```

The `...` in the example hides the fact that a real embedding from `all-MiniLM-L6-v2` has **384 numbers** — it is a 384-dimensional vector. Each number is a tiny coordinate that, taken together, describes where this text "lives" in the model's map of meaning.

```text
"leave policy"  →  [0.23, 0.84, -0.11, ..., 0.07]   (384 numbers)
```

That whole list of numbers is what gets stored in the vector database in Module 6.

---

## What Is a Dimension?

A dimension is one **position in the list of numbers** — one coordinate.

In 2D space you locate a point with two numbers: `(x, y)`. In 3D you add `z`. An embedding model uses far more dimensions — 384, 768, 1024, 1536 — which lets it represent far more subtle distinctions than a map could.

```text
2D point:      (0.6, 0.8)            → 2 coordinates
3D point:      (0.6, 0.8, 0.2)       → 3 coordinates
Embedding:     (0.23, 0.84, -0.11, ...)  → 384 coordinates
```

You do not need to "see" each dimension. Think of them as hidden switches the model flips to describe meaning: a handful might light up for words about *time*, others for *people*, others for *places*, and so on. No single dimension means anything on its own — the **combination** is what encodes meaning.

> **Deep dive: covered in Module 5** — chapter [02-How-Embeddings-Represent-Meaning.md](02-How-Embeddings-Represent-Meaning.md) builds the intuition for thinking of embeddings as points in space.

---

## Why Numbers Instead of Keywords?

Before embeddings, the classic way to search was by **keywords**:

```text
Query:  "How many leave days?"
        ↓ find exact word "leave" in documents
```

That approach fails in two everyday situations:

```text
1. Synonyms:  the doc says "vacation" but the user asks about "leave"
              → keyword search finds nothing

2. Paraphrase: the doc says "annual days off" but the user asks about
               "leave days" → keyword search finds nothing
```

A user almost never types the exact words that appear in the document. Embeddings solve this because they store **meaning**, not words. Two different sentences that *mean the same thing* get embeddings that are **close together** in vector space.

```text
Keyword search:   "vacation rules"  ✗  does not match  "leave policy"
Semantic search:  "vacation rules"  ✓  close to       "leave policy"
```

This is the property called **semantic similarity**, and it is the entire reason RAG works better than a plain keyword lookup over the same documents.

---

## Close Together vs Far Apart

The whole point of embeddings is that meaning controls distance.

In the model's vector space:

```text
"employee leave policy"      ·
                             \
"vacation rules"   ·          \        · "security policy"
                              
   leave-related ideas are       security is far away because it is
   clustered close together      about a completely different topic
```

When the system compares your query to every chunk, it is really asking:

```text
"How close is this chunk's vector to my query's vector?"
```

So if you ask about **leave**, the chunks about leave and vacation score as very similar and get retrieved. The chunk about the **security policy** scores as very different and stays buried in the database — which is exactly what we want.

---

## Real Enterprise Example

A company's knowledge base has these chunks:

```text
Chunk A: "Employees receive 30 annual leave days per year."
Chunk B: "Vacation requests must be approved by the manager."
Chunk C: "All employees must complete security awareness training."
```

A user asks: *"How many vacation days am I entitled to?"*

Even though the words "vacation days" only appear in the user's question, the embedding of Chunk A (annual leave days) lands very close to the question because both talk about the *same thing*. The system retrieves Chunk A and answers correctly — without ever sharing a keyword.

```text
Question vector:  "How many vacation days am I entitled to?"
  Chunk A (leave days)   → distance small  ✓ retrieved
  Chunk B (vacation req) → distance small  ✓ retrieved
  Chunk C (security)     → distance large  ✗ not retrieved
```

---

## Key Takeaways

- An **embedding** is a piece of text converted into a list of numbers (a vector).
- `all-MiniLM-L6-v2` produces **384-dimensional** vectors; each dimension is one coordinate of meaning.
- Embeddings enable **semantic search**: related ideas land close together even when they use different words.
- Keyword search matches exact words; embedding search matches **meaning**.
- "leave policy" and "vacation rules" embed close together; "security policy" embeds far away.

---

## Test Yourself

1. What is an embedding, in one sentence?
2. How many numbers does `all-MiniLM-L6-v2` produce for one chunk of text?
3. Why does a query about "leave days" match a document about "vacation rules" even though they share no keywords?
4. What does the phrase "dimension" refer to in an embedding?
5. If a user searches for "security policy", which of these chunks should rank closest: (a) "annual leave days", (b) "password reset steps", or (c) "employee onboarding"?

<details>
<summary>Answers</summary>

1. An embedding is a piece of text converted into a **list of numbers (a vector)** that captures its meaning.
2. **384 numbers** (a 384-dimensional vector).
3. Because embeddings store **meaning**, not words — "leave" and "vacation" mean nearly the same thing, so their vectors land close together.
4. A dimension is **one position in the vector** — one coordinate in the model's map of meaning. 384 dimensions = 384 coordinates.
5. (b) **"password reset steps"** — it is closest in meaning to "security policy" (security/IT topics), while leave and onboarding are unrelated.

</details>

---

## Next Chapter

Next up: [02-How-Embeddings-Represent-Meaning.md](02-How-Embeddings-Represent-Meaning.md) — how meaning becomes *direction* in vector space, and where embeddings fall short.
