# Metadata and Cleaning

## Introduction

By now you can load text, PDFs, Word files, HTML, CSV, and web pages. But loading is only half the job. Two more things decide whether your documents are *useful* or merely *loaded*:

1. **Metadata** — the facts attached to each document that make retrieval traceable and filterable.
2. **Cleaning** — removing the noise that extraction drags in, so the text the pipeline embeds is actually good.

This chapter is short but arguably the most important in the module, because mistakes here poison *everything* downstream. Remember the law of the course: **garbage in, garbage out.**

---

## Learning Objectives

By the end of this chapter, you will understand:

- Why metadata matters (source traceability, filtering, provenance)
- How to add custom metadata to a `Document`
- Common text-cleaning tasks (headers/footers, whitespace, page numbers)
- Why "garbage in, garbage out" is the first rule of RAG

---

## Why Metadata Matters

Metadata is the context that makes text *actionable*. It answers three questions the text alone cannot:

### 1. Source traceability

```text
Where did this chunk come from?
→ metadata["source"] = "docs/leave-policy.pdf", page 7
```

This is what lets your system say *"according to the Leave Policy (page 7)"* — and what lets a human audit any answer back to its origin.

### 2. Filtering

Metadata is a **search filter**. With it you can answer questions like:

```text
"Show me HR policies updated after January 2026."
"Find contracts with vendor = Acme Supplies."
```

```text
metadata = {"department": "HR", "updated": "2026-01-15", "vendor": "Acme Supplies"}
```

Filtered retrieval is dramatically faster and more accurate than unfiltered search — you'll build on this in Module 7.

### 3. Provenance and governance

Compliance teams need to know who authored a document and when it was last reviewed. Metadata carries that record through the whole pipeline.

---

## Adding Custom Metadata

Loaders add basic metadata automatically (usually `source`, sometimes `page` or `title`). For richer retrieval, add your own. When you create a `Document` you can pass a metadata dictionary directly:

```python
from langchain_core.documents import Document

doc = Document(
    page_content="Employees receive 30 annual leave days.",
    metadata={
        "source": "docs/leave-policy.pdf",
        "page": 4,
        "department": "HR",
        "policy_id": "HR-201",
        "last_reviewed": "2026-01-15",
    },
)
```

You can also enrich documents *after* loading:

```python
from langchain_community.document_loaders import TextLoader

documents = TextLoader("docs/leave-policy.txt").load()

for doc in documents:
    doc.metadata["department"] = "HR"
    doc.metadata["last_reviewed"] = "2026-01-15"

print(documents[0].metadata)
```

```text
{'source': 'docs/leave-policy.txt', 'department': 'HR', 'last_reviewed': '2026-01-15'}
```

Now a user asking *"what changed in HR policies this year?"* can be answered with a metadata filter instead of a fuzzy search.

---

## Cleaning Text

Extraction is rarely perfect. Loaders drag in **noise** that would pollute embeddings and confuse retrieval. Common offenders:

### Headers and footers

Repeated on every page of a PDF:

```text
"HR Policy - Confidential - Page 7 of 42"
```

Three hundred identical lines like this across a 42-page PDF add nothing but noise — and they make unrelated pages look similar to each other.

### Page numbers and section labels

```text
Page 12 / 12. Employee Benefits (continued)
```

### Broken whitespace

PDF extraction often leaves ragged lines and double spaces:

```text
"Employees receive 30\n paid \nannual leave\ndays."
```

A cleaning pass normalizes this:

```python
import re


def clean_text(text):
    """A small cleaning pass: collapse blank lines and strip repeated page footers"""
    text = re.sub(r"\n\s*\n+", "\n\n", text)     # collapse runs of blank lines
    text = re.sub(r"[ \t]{2,}", " ", text)        # collapse double spaces
    text = re.sub(r"^\s*Page\s*\d+.*$", "", text, flags=re.MULTILINE)
    return text.strip()


raw = documents[0].page_content
documents[0].page_content = clean_text(raw)
```

```text
Before:  "Employees receive 30\n paid \nannual leave\n   days.\nPage 1"
After:   "Employees receive 30 paid annual leave days."
```

Keep cleaning **small and targeted**. Over-aggressive cleaning (removing punctuation, lowercasing everything) can destroy meaning. The goal is to remove *repetitive noise*, not to rewrite the document.

---

## Garbage In, Garbage Out

This is the single most important concept in the module. Every downstream step only rearranges what you give it:

```text
Bad loaded text
   → bad chunks      (Module 4)
   → bad embeddings  (Module 5)
   → bad retrieval   (Module 7)
   → bad answers     (Module 8)
```

You cannot fix a noisy document at the retrieval stage. The garbage was baked in at loading time. This is why experienced RAG engineers spend a surprising amount of their time on loading, metadata, and cleaning — it's where quality is won or lost.

A useful habit: **inspect what you load.** Print a sample of loaded `page_content` and `metadata` before proceeding. If the sample looks wrong, fix the loader before building anything on top of it.

---

## Real-World Example: Regulatory Compliance

A bank ingests 5,000 policy documents for a compliance assistant. Before anything is embedded, the pipeline:

1. Adds metadata to every document: **department, document type, last review date, owner**.
2. Strips repeated **"Confidential — Internal Use Only"** headers and page numbers.
3. Normalizes the ragged whitespace PDF extraction leaves behind.
4. Logs each document with a unique ID so every future answer is traceable.

The result: regulators can ask *"which IT policies were last reviewed before 2025?"* and get a filtered, cleaned, fully traceable answer — instead of a fuzzy search over 5,000 noisy documents.

---

## Key Takeaways

- Metadata gives text **traceability, filterability, and provenance** — add it deliberately.
- Add custom metadata by passing a `metadata` dict to `Document`, or by editing `doc.metadata` after loading.
- Cleaning removes **headers, footers, page numbers, and ragged whitespace** — nothing else.
- Cleaning should be **small and targeted**; over-cleaning destroys meaning.
- **Garbage in, garbage out** — loading-time quality decides retrieval-time quality, so always inspect a sample of what you load.

---

## Test Yourself

1. Name three things metadata is used for in a RAG system.
2. Write the code to attach `{"department": "HR"}` to an already-loaded document.
3. What is the risk of *over*-cleaning a document?
4. Why does a repeated footer like "Page 7 of 42" hurt retrieval quality?
5. What is the meaning of "garbage in, garbage out" in the RAG context?

<details>
<summary>Answers</summary>

1. **Source traceability** (where did this come from), **filtering** (search by department/date/vendor), and **provenance/governance** (who wrote it, when it was reviewed).
2. `doc.metadata["department"] = "HR"` (after loading).
3. You can **destroy meaning** — e.g. removing punctuation or lowercaseing everything can change the semantics of the text and hurt embeddings.
4. Because hundreds of identical footer lines add noise to every chunk, and they make **unrelated pages look artificially similar** to each other during retrieval.
5. If the loaded text is bad, every later stage (chunks, embeddings, retrieval, answers) inherits that badness — quality must be ensured at loading time, not patched later.

</details>

---

## Next Chapter

Next up: [07-Enterprise-Ingestion.md](07-Enterprise-Ingestion.md) — putting it all together: how real companies ingest from many sources into one pipeline.
