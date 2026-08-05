# Common Chunking Mistakes

## Introduction

Most retrieval failures are not caused by the embedding model or the vector database — they are caused by **chunking**. And most chunking mistakes share one trait: they are silent. Nothing crashes, the pipeline completes, and the system just gives slightly-wrong answers forever.

This chapter lists the mistakes that show up in real projects again and again. Learn to recognize them and you will save yourself weeks of debugging.

---

## Learning Objectives

By the end of this chapter, you will understand:

- Why fixed-size splitting without overlap breaks retrieval
- How splitting mid-table or mid-code destroys meaning
- Why ignoring document structure hurts
- How the same chunk can be retrieved twice
- Why "chunking is not one-size-fits-all"

---

## Mistake 1: Fixed Size Without Overlap

The most common setup for a beginner:

```python
CharacterTextSplitter(chunk_size=500, chunk_overlap=0)
```

Zero overlap means every sentence that lands on a boundary is **cut in half and lost**:

```text
Chunk 7:  "...unused leave may be carried"
Chunk 8:  "forward for up to 90 days..."
```

Ask *"can I carry unused leave?"* and the system retrieves chunk 7 — which contains the question's keywords but *not the answer*. It looks like a retrieval failure; it's actually a boundary-cut failure.

**The fix:** always add some overlap (10–20% of `chunk_size`). It is nearly free and prevents the single most common silent failure.

---

## Mistake 2: Splitting Mid-Table or Mid-Code

A `CharacterTextSplitter` does not know what a table is. Given a table, it happily cuts between a header row and its values:

```text
Original table:
  Vendor        |  Status
  Acme Supplies |  Approved
  Globex Ltd    |  Under review

After a bad split:
  Chunk A: "Vendor        |  Status"
  Chunk B: "Acme Supplies |  Approved"
  Chunk C: "Globex Ltd    |  Under review"
```

Now no chunk connects a vendor to its status. Same problem with code:

```text
def connect_db():
    creds = load_credentials()      ← chunk ends here
def connect_db():                   ← no wait, chunk 2 repeats it
    creds = load_credentials()
    db = Database(creds)            ← imports/logic separated
```

**The fix:** chunk tables at logical blocks (never inside a cell/row group) and chunk code at function boundaries. Use structure-aware splitting (chapter 04) when your content has tables or code.

---

## Mistake 3: Ignoring Document Structure

Authors already organize content — headings, sections, chapters. A splitter that ignores all of it cuts across those boundaries:

```text
Chunk: "Annual Leave
Full-time employees receive 30 days per year.

Travel Policy
Business travel..."      ← two topics welded together
```

The chunk is half leave policy and half travel policy. It embeds as a blur (remember the muddy vector) and matches both queries poorly. And the heading "Travel Policy" can no longer be used as a filter, because it's buried inside a leave chunk.

**The fix:** feed the splitter the structure. `MarkdownHeaderTextSplitter` (or any heading-aware splitter) keeps sections intact and puts headings in metadata. Structure is information — don't throw it away.

---

## Mistake 4: The Same Chunk Duplicated Across Retrieval

With heavy overlap, neighboring chunks share text:

```text
Chunk 7:  "...receive 30 leave days and 15 sick days..."
Chunk 8:  "...30 leave days and 15 sick days. Approval..."
```

Ask *"how many sick days do I get?"* and the top-3 results may contain **chunks 7, 8, and 9 — three copies of the same sentence**. The LLM gets the same fact three times and nothing else. The answer isn't wrong, it's just *thinner* than it should be.

**The fix:** two things.

1. Use overlap that's large enough to protect boundaries but **small enough to avoid mass duplication** (10–20% is a good middle).
2. In retrieval, **deduplicate by source region** before sending chunks to the LLM — if two chunks come from the same document and overlap heavily, keep the one with the higher score. (You'll apply this in Module 7.)

---

## Mistake 5: "Chunking Is One-Size-Fits-All"

The most expensive mistake of all: assuming one setting works for every document.

```text
Legal contracts      →  need long, clause-sized chunks
Support articles     →  need short, focused chunks
Code files           →  need function-sized chunks
Financial tables     →  must never be split at all
```

A single `chunk_size` across a mixed corpus guarantees that *some* content is chunked badly — and you won't know which until a query fails. Real pipelines often use **different splitters and sizes per document type**, then tag each chunk with its type in metadata.

**The fix:** group your documents by type, tune each group separately, and record the setting used in metadata (`"chunking": "recursive-1000-overlap-200"`). When retrieval quality drops, the metadata tells you exactly which setting produced the bad chunk.

---

## Real-World Example: The "Wrong Answers" Debug

A support assistant retrieves well but users say answers are "missing half the info." Debugging finds:

1. Zero overlap → **boundary cuts** losing sentence halves.
2. A pricing table split across three chunks → **vendor/price pairs detached**.
3. Top-3 results containing three near-identical chunks → **duplicate retrieval**.

Each fix was one small change:

```text
+ overlap 150 chars        →  boundary cuts gone
+ table-aware block split  →  rows stay intact
+ dedupe by source region  →  three unique chunks retrieved
```

Same embedding model, same vector store — retrieval quality changed completely. That is the power of chunking done right.

---

## Key Takeaways

- **No overlap** → sentences cut at boundaries and effectively lost.
- **Splitting tables/code** → rows and functions broken into unreadable fragments.
- **Ignoring structure** → topics welded together and headings unusable.
- **Heavy overlap + no dedup** → the same chunk retrieved multiple times, thinning the answer.
- **One setting for everything** → some content is always chunked badly; split by document type and record your settings in metadata.

---

## Test Yourself

1. Why is `chunk_overlap=0` dangerous?
2. What happens if a splitter cuts a table between the header row and its values?
3. How does `MarkdownHeaderTextSplitter` fix the "ignoring structure" mistake?
4. How can heavy overlap cause the *same* chunk to appear twice in retrieval results?
5. Why is a single chunking setting across all document types a mistake?

<details>
<summary>Answers</summary>

1. Sentences that fall exactly on a boundary are **cut in half**, and neither half contains the full answer — a silent retrieval failure.
2. No chunk connects a vendor to its status, so questions like "is Acme approved?" cannot be answered from the chunks.
3. It splits on headings and stores them in `metadata`, keeping sections intact and making the section name searchable.
4. Neighboring chunks share text, so the same sentence can appear in several chunks; if they all rank in the top-k, retrieval returns near-duplicates.
5. Because different content needs different chunking — contracts need long clauses, support articles need short focused chunks, code needs function boundaries. One setting guarantees some content is chunked badly.

</details>

---

## Next Chapter

Module 4 is complete. Next up: [Module 5: Embeddings](../Module-5-Embeddings/README.md) — how each chunk becomes a vector that computers can compare.
