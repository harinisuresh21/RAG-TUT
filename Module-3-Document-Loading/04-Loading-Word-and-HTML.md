# Loading Word, HTML, and CSV

## Introduction

Text files and PDFs cover a lot of ground, but real enterprises live in Microsoft Word, on web pages, and in spreadsheets. A policy handbook is a `.docx`. A knowledge-base article is an HTML page. A list of approved vendors is a `.csv`.

The good news: each format has a small, focused LangChain loader, and they all produce the same `Document` objects you already know. In this chapter you will load all three.

---

## Learning Objectives

By the end of this chapter, you will understand:

- How to load `.docx` files with `Docx2txtLoader` (and `python-docx` directly)
- How to load HTML pages with `BSHTMLLoader` (backed by BeautifulSoup)
- How to load tabular data with `CSVLoader`
- What each loader puts into `page_content` and `metadata`

---

## Word Documents: Docx2txtLoader / python-docx

Word files are much friendlier than PDFs. A `.docx` stores text in a structured, readable form (a zip of XML), so extraction is usually clean — paragraphs come out in order, headings included.

LangChain offers `Docx2txtLoader` for this:

```python
from langchain_community.document_loaders import Docx2txtLoader

loader = Docx2txtLoader("docs/employee-handbook.docx")
documents = loader.load()

print(documents[0].metadata)
print(documents[0].page_content[:200])
```

```text
{'source': 'docs/employee-handbook.docx'}
"Employee Handbook
1. Introduction
This handbook describes the policies and benefits for all full-time employees.
..."
```

One file becomes **one `Document`** — no page splitting, because Word documents flow like a single text stream.

### Using python-docx directly

If you want finer control, `python-docx` lets you read paragraph by paragraph:

```python
from docx import Document

doc = Document("docs/employee-handbook.docx")

text = "\n".join(paragraph.text for paragraph in doc.paragraphs)
print(text[:200])
```

Both approaches use the same underlying extraction; the loader just wraps it in a `Document` object for you.

---

## HTML Pages: BSHTMLLoader / BeautifulSoup

Web pages are where content and noise live together. An article about the VPN policy is surrounded by navigation menus, cookie banners, and footer links. You want the **article text**, not the chrome.

`BSHTMLLoader` uses BeautifulSoup under the hood to parse the HTML and pull out readable text:

```python
from langchain_community.document_loaders import BSHTMLLoader

loader = BSHTMLLoader("docs/vpn-policy.html")
documents = loader.load()

print(documents[0].metadata)          # includes the title
print(documents[0].page_content[:150])
```

```text
{'source': 'docs/vpn-policy.html', 'title': 'VPN Access Policy'}
"VPN Access Policy
All employees must use the company VPN when working outside the office.
..."
```

Two things to notice:

- **`title`** appears in metadata automatically — the loader reads the HTML `<title>` tag.
- The content is **cleaned text**, not raw HTML. BeautifulSoup strips the tags so the LLM never sees `<div class="nav">`.

### Doing it yourself with BeautifulSoup

If you ever need custom parsing, the underlying library is yours to use directly:

```python
from bs4 import BeautifulSoup

with open("docs/vpn-policy.html", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

text = soup.get_text()
```

The loader just standardizes this into `Document` objects.

---

## CSV Files: CSVLoader

CSV files store **structured, tabular data** — vendor lists, employee rosters, product catalogs. Each row is a record; each column is a field.

`CSVLoader` turns every row into its own `Document`:

```python
from langchain_community.document_loaders import CSVLoader

loader = CSVLoader("docs/vendors.csv")
documents = loader.load()

print(len(documents))                # number of rows
print(documents[0].page_content)
print(documents[0].metadata)
```

```text
25
"Vendor: Acme Supplies; Category: Office Supplies; Status: Approved"
{'source': 'docs/vendors.csv', 'row': 0}
```

What happened to the row?

```text
Vendor,Category,Status          ← header
Acme Supplies,Office Supplies,Approved
```

became one text string:

```text
Vendor: Acme Supplies; Category: Office Supplies; Status: Approved
```

And each row is tagged with its **`row`** number in metadata, so you can always trace a retrieved answer back to the exact record.

---

## Loader Cheat-Sheet

| Format | Loader | Library behind it | One file produces |
|---|---|---|---|
| `.txt` | `TextLoader` | built-in | 1 `Document` |
| `.pdf` | `PyPDFLoader` | `pypdf` | 1 `Document` per page |
| `.docx` | `Docx2txtLoader` | `python-docx` | 1 `Document` |
| `.html` | `BSHTMLLoader` | `BeautifulSoup` | 1 `Document` (with `title`) |
| `.csv` | `CSVLoader` | `csv` | 1 `Document` per row |

They all return a list of `Document` objects with `page_content` and `metadata` — which is exactly why the rest of the pipeline can treat every format identically.

---

## Running the Example

The module script [01-loading-txt-pdf-docx.py](01-loading-txt-pdf-docx.py) already includes the Word loader. Drop a `.docx` into `docs/` and re-run:

```bash
python "Module-3-Document-Loading/01-loading-txt-pdf-docx.py"
```

```text
Looking for Word (.docx) documents in the docs directory...
  Loaded employee-handbook.docx: 1 document(s).
Word document 1:
  Source: ...\docs\employee-handbook.docx
  Content length: 4210 characters
  Content preview: Employee Handbook
...
```

---

## Real-World Example: A Single Knowledge Source, Four Formats

Your company's internal knowledge lives in four places at once:

```text
Policies          →  employee-handbook.docx   (Word)
Portal pages      →  how-to-vpn.html          (HTML)
Vendor registry   →  approved-vendors.csv     (CSV)
Old reports       →  annual-report.pdf        (PDF)
```

Each format gets its own loader, but the output is always the same: a list of `Document` objects. That uniformity is the whole point of loaders — the rest of the RAG pipeline never needs to know what format a document originally came from.

---

## Key Takeaways

- `.docx` → **`Docx2txtLoader`** (or `python-docx` directly): clean, ordered paragraphs, one `Document` per file.
- `.html` → **`BSHTMLLoader`** (BeautifulSoup behind it): strips markup and records the `title` in metadata.
- `.csv` → **`CSVLoader`**: one `Document` per row, with the `row` number in metadata.
- Every loader returns the **same kind of object**, so the pipeline is format-agnostic.
- Different formats → different loaders → same `Document` shape.

---

## Test Yourself

1. Which loader would you use for a `.docx` employee handbook?
2. What extra metadata key does `BSHTMLLoader` add for an HTML page?
3. When `CSVLoader` loads a 25-row file, how many `Document` objects do you get?
4. Why is the HTML content *cleaned* rather than raw markup?
5. What is the one thing all loaders in this course have in common?

<details>
<summary>Answers</summary>

1. `Docx2txtLoader` (or the `python-docx` library directly).
2. `title` — read from the page's `<title>` tag.
3. 25 — one `Document` per row, each tagged with its `row` number.
4. Because an LLM should consume **text, not markup** — navigation menus, tags, and scripts are noise that would pollute retrieval.
5. They all return a **list of `Document` objects** with `page_content` and `metadata`.

</details>

---

## Next Chapter

Next up: [05-Web-Loading-and-Crawling.md](05-Web-Loading-and-Crawling.md) — loading live web pages and crawling whole sites.
