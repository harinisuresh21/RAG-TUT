# Semantic and Advanced Chunking

## Introduction

So far, every splitter has worked in the same way: **count something (characters, tokens) and cut at boundaries**. That approach is simple, fast, and good enough for most documents. But text has a deeper structure that character counts ignore — a document is a sequence of **ideas**, and the best chunks follow those ideas, not the character count.

Advanced chunking splits by **meaning** instead of raw length. This chapter explains the idea, shows the most useful techniques (sentence-based splitting, structure-aware splitting), and — just as importantly — when they are *not* worth it.

---

## Learning Objectives

By the end of this chapter, you will understand:

- The concept of splitting by meaning rather than length
- How sentence-based splitters work
- How `MarkdownHeaderTextSplitter` uses document structure
- The cost of advanced chunking
- When advanced splitting is worth the effort (and when it isn't)

---

## Splitting by Meaning

A character-based splitter decides chunk boundaries by *position*. A meaning-based splitter decides by *topic*: keep sentences together while they talk about the same thing, start a new chunk when the topic shifts.

```text
"Employees receive 30 leave days."  →  keep
"Leave requests need approval."     →  still about leave, keep
"Travel must be booked in advance." →  topic shifted → NEW CHUNK
```

```text
Character splitter:  cuts where the character count says so (may split mid-topic)
Semantic splitter:   cuts where the meaning shifts (topics stay together)
```

The intuition: **a chunk is not a length, it's a thought.** Retrieval works best when each vector represents one complete thought, because then a query matches the *whole* thought instead of a fragment of it.

---

## Sentence-Based Splitters

The simplest form of meaning-aware splitting is **sentence-based**: split a document into sentences, then group consecutive sentences into chunks.

The natural grouping is by **semantic similarity**. In its simplest form, the algorithm:

```text
1. Split the document into sentences
2. Embed each sentence (Module 5 machinery)
3. Measure how similar each sentence is to its neighbor
4. Start a new chunk where similarity drops sharply
```

```text
sentence 1  about annual leave   ┐
sentence 2  about annual leave   ┘ similar → same chunk

sentence 3  about travel        → big drop in similarity → new chunk
```

Why it works: sentences that belong to the same topic produce similar embeddings, so the similarity "gap" between sentence 2 and sentence 3 is a good boundary — usually far better than a character count.

The cost: you need embeddings to decide boundaries, so semantic chunking is **slower and more expensive** than character splitting. You also need to tune how big a drop counts as a "new topic."

---

## Structure-Aware Splitting: MarkdownHeaderTextSplitter

Many documents already come with **explicit structure** — headings. A 200-page handbook is organized into sections with titles:

```markdown
# Annual Leave
Full-time employees receive 30 days...

# Sick Leave
Full-time employees receive 15 days...

# Travel Policy
Business travel must be booked in advance...
```

When structure exists, the smartest splitter is the one that **reads it**. LangChain's `MarkdownHeaderTextSplitter` splits on headings and records the heading path in metadata:

```python
from langchain_text_splitters import MarkdownHeaderTextSplitter

headers_to_split_on = [
    ("#", "section"),
    ("##", "subsection"),
]

splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
chunks = splitter.split_text(handbook_markdown)

print(chunks[0].metadata)
```

```text
{'section': 'Annual Leave'}
```

Each chunk now:

```text
page_content = "Full-time employees receive 30 days..."
metadata     = {"section": "Annual Leave"}
```

The heading becomes searchable **metadata**. Retrieval can filter by section ("only from the Travel Policy") and the LLM always knows what section a chunk came from. This is meaning-aware chunking for free — because an author already did the hard work of marking topics.

The same idea applies to other structured formats:

```text
Markdown headings   →  MarkdownHeaderTextSplitter
HTML headings       →  split on <h1>/<h2>/... with HTML-aware splitters
Table of contents   →  use section boundaries as chunk boundaries
```

If your document has headings, **use them** — it beats both character counting and even semantic embedding for structure.

---

## When Advanced Splitting Is Worth It

Advanced chunking is strictly better in quality and strictly worse in cost. Use it where the quality matters more than the cost:

### Worth it

```text
Legal contracts        →  clause boundaries matter; retrieval must be precise
Regulatory manuals     →  section-level accuracy is audited
Long research reports  →  topic shifts are exactly what users search for
```

### Not worth it (yet)

```text
Short, homogeneous pages   →  character/recursive splitting is already fine
Huge volumes (millions)    →  embedding every sentence for boundaries is expensive
Rapid prototypes           →  don't optimize what you haven't measured failing
```

The honest rule: **start with recursive splitting. If a specific retrieval failure shows up, *then* consider advanced chunking.** Semantic chunking fixes real problems — but only after you've confirmed you have them.

---

## Real-World Example: The Regulatory Manual

A compliance team ingests a 900-page regulatory manual, clearly organized with headings and subheadings. They use `MarkdownHeaderTextSplitter`:

```text
Chunk = one (sub)section, with metadata:
  {"chapter": "Data Protection", "section": "Access Controls"}
```

An auditor asks *"what are the access control requirements in the Data Protection chapter?"* Retrieval filters on `chapter="Data Protection"` and matches the right section directly. The answer comes with the section name attached — traceable, precise, and cheaply produced, because the splitter just read the structure that already existed.

---

## Key Takeaways

- **Meaning-based chunking** splits where topics shift, not where character counts land.
- **Sentence-based splitters** embed sentences, measure neighbor similarity, and cut at big drops.
- **`MarkdownHeaderTextSplitter`** splits on headings and stores them in metadata — the easiest big win for structured documents.
- Advanced chunking is **slower and more expensive** than character splitting.
- Start recursive, confirm a real failure, *then* go advanced — don't optimize preemptively.

---

## Test Yourself

1. What does it mean to "split by meaning" instead of by length?
2. How does a sentence-based semantic splitter decide where a new chunk begins?
3. What does `MarkdownHeaderTextSplitter` put into `metadata`?
4. Why is heading-based splitting often better than semantic embedding for structured docs?
5. When is it NOT worth using advanced chunking?

<details>
<summary>Answers</summary>

1. Chunk boundaries follow **topic shifts** rather than character counts, so each chunk holds one complete idea.
2. It embeds sentences, measures the similarity between neighbors, and starts a new chunk where the similarity **drops sharply**.
3. The heading path, e.g. `{"section": "Annual Leave"}` — which becomes searchable, filterable metadata.
4. Because the document's author already marked the topic boundaries; the splitter reads real structure instead of approximating meaning, at a fraction of the cost.
5. When documents are short and homogeneous, when volume makes embedding every sentence too expensive, or during rapid prototyping — start with recursive splitting and only advance once a real failure is confirmed.

</details>

---

## Next Chapter

Next up: [05-Common-Chunking-Mistakes.md](05-Common-Chunking-Mistakes.md) — the mistakes that silently destroy retrieval quality, and how to spot them in your own pipeline.
