# Loading PDFs

## Introduction

The PDF is the **workhorse of the enterprise**. HR policies, contracts, compliance manuals, financial reports, product specs — almost everything official eventually becomes a PDF. So almost every real RAG system has to load PDFs.

But PDFs are also the format most likely to make your life difficult. In this chapter you will learn why, how to load them with `PyPDFLoader` (`pypdf`), and what to do when the PDF's text simply isn't there.

---

## Learning Objectives

By the end of this chapter, you will understand:

- Why PDFs dominate enterprise document stores
- Why PDFs are hard to extract text from
- How to load a PDF with `PyPDFLoader` from `langchain_community`
- What the loaded output looks like (one `Document` per page)
- The concept of **OCR** for scanned PDFs

---

## Why PDFs Are Everywhere

A PDF is a **fixed-layout document**: it looks identical on every screen and printer. That is exactly what legal teams and compliance departments want. "What you sign is what you see."

```text
HR Policy        →   hr-policy.pdf
Supplier Contract →  contract-2026.pdf
Audit Report     →   audit-q3.pdf
```

The catch: PDFs are designed for **humans to read**, not for **computers to parse**. The text is not stored the way it appears — it is stored as positioned glyphs inside internal objects. Recovering readable, ordered text is genuinely hard.

---

## Why PDFs Are Hard

Three problems account for most extraction pain:

### 1. Scanned PDFs (images, no text)

Many old documents were printed and then scanned. The PDF is just a series of **page images** — there is *zero text* inside the file. A text extractor returns an empty string:

```text
PDF contains:   [picture of a page]
Extraction:     ""   ← nothing
```

### 2. Tables

Text in a table is scattered across grid cells. A naive extractor often reads it **left-to-right, row by row**, scrambling columns and mixing headers with data.

### 3. Multi-column layouts

Newsletters and brochures print in two or three columns. The extractor reads top-to-bottom, so it **interleaves the columns** and produces nonsense like:

```text
"Employees receive management approves 30 paid days all requests..."
```

None of these problems have a perfect solution. For tables and columns you need layout-aware tools; for scans you need OCR.

---

## PyPDFLoader and pypdf

LangChain's `PyPDFLoader` wraps the excellent `pypdf` library. It splits the PDF **per page**, producing one `Document` per page with the page number in metadata:

```python
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("docs/hr-policy.pdf")
documents = loader.load()

print(f"Loaded {len(documents)} pages")
print(documents[0].metadata)
```

```text
Loaded 24 pages
{'source': 'docs/hr-policy.pdf', 'page': 0}
```

Each page is a separate `Document`:

```text
Document 1  →  page_content = "HR Policy ..."      metadata = {source, page: 0}
Document 2  →  page_content = "Leave policy ..."   metadata = {source, page: 1}
...
```

That `page` number in metadata is gold: when a chunk is later retrieved, you can answer *"which page of which file?"* without any extra work.

### Loading a PDF that may not exist

In the module script [01-loading-txt-pdf-docx.py](01-loading-txt-pdf-docx.py), PDF loading is guarded so the script never crashes if there is no PDF (or a broken one) in `docs/`:

```python
import glob
from langchain_community.document_loaders import PyPDFLoader

pdf_files = glob.glob("docs/*.pdf")

for pdf_path in pdf_files:
    try:
        loader = PyPDFLoader(pdf_path)
        pages = loader.load()
        print(f"Loaded {pdf_path}: {len(pages)} page(s).")
    except FileNotFoundError:
        print(f"Warning: could not find {pdf_path}. Skipping.")
    except Exception as e:
        print(f"Warning: could not read {pdf_path}: {e}. Skipping.")
```

```text
Looking for PDFs in the docs directory...
  No PDF files found. Skipping PDF loading (add a .pdf to docs/ to try it).
```

Add any `.pdf` file to `docs/` and re-run — the loader picks it up automatically.

---

## The OCR Concept

A **scanned** PDF has no text layer, so no text extractor can read it. The solution is **OCR** — *Optical Character Recognition* — which looks at the page *image* and recognizes the shapes of letters:

```text
Scanned page (image)
     ↓  OCR
Text: "Employees receive 30 paid leave days."
```

The most common free OCR engine is **Tesseract**, often combined with layout detection. In Python, `pytesseract` wraps Tesseract and LangChain offers OCR-aware loaders (for example the unstructured-family loaders).

Important practical notes:

- OCR is **slower and less accurate** than text extraction — expect typos in results.
- OCR quality depends on the scan: clean, straight, high-contrast pages work best.
- Always **spot-check** a sample of OCR output before trusting it.

---

## Real-World Example: Contract Review

A law firm loads thousands of supplier contracts for a RAG assistant that answers *"what are the termination clauses in this contract?"* The contracts are a mix of:

- **Modern PDFs** → `PyPDFLoader` extracts text cleanly, page by page.
- **Scanned agreements from the 1990s** → routed through OCR first.

Each contract becomes many page-level `Documents`, all tagged with `source` and `page`. When the assistant quotes a termination clause, it can cite *contract-2026.pdf, page 12* — exactly what a lawyer needs to verify the answer.

---

## Key Takeaways

- PDFs are the **most common enterprise format** but also the **hardest to parse**.
- `PyPDFLoader` (wrapping `pypdf`) extracts text and returns **one `Document` per page** with `page` in metadata.
- The three classic PDF problems: **scanned images, tables, and multi-column layouts**.
- **OCR** (e.g. Tesseract) recovers text from scanned page images — slower, less accurate, needs spot-checks.
- Always wrap PDF loading in `try/except` so one bad file doesn't kill your whole ingestion run.

---

## Test Yourself

1. Why does `PyPDFLoader` return *multiple* `Document` objects for one PDF?
2. What two metadata keys does a page from `PyPDFLoader` typically contain?
3. What is the difference between a scanned PDF and a normal PDF?
4. Which tool would you reach for when a PDF has no extractable text at all?
5. Why does the module script wrap PDF loading in `try/except`?

<details>
<summary>Answers</summary>

1. Because it splits the PDF **per page**, so each page becomes its own `Document` (which keeps retrieval page-level precise).
2. `source` (the file path) and `page` (the zero-based page number).
3. A scanned PDF is just a set of **page images** with no text inside; a normal PDF stores its text as positioned glyphs that can be extracted.
4. **OCR** — Optical Character Recognition, e.g. Tesseract via `pytesseract`.
5. So a missing or corrupt file prints a **friendly warning and is skipped** instead of crashing the whole ingestion run.

</details>

---

## Next Chapter

Next up: [04-Loading-Word-and-HTML.md](04-Loading-Word-and-HTML.md) — Word documents, HTML pages, and CSV files.
