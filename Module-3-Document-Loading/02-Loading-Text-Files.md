# Loading Text Files

## Introduction

Text files (`.txt`) are the simplest document format in existence — and the perfect place to learn how loaders work. There is no complex structure hiding inside a `.txt` file; what you read is what you get.

In this chapter you will load the sample company documents in `docs/` (`google.txt`, `microsoft.txt`, `Nvidia.txt`) using LangChain's `TextLoader` and `DirectoryLoader`, and you will meet the **LangChain Document object** that every loader in this course produces.

---

## Learning Objectives

By the end of this chapter, you will understand:

- Why text files are the ideal starting point
- What a LangChain `Document` object is (`page_content` + `metadata`)
- How `TextLoader` loads a single file
- How `DirectoryLoader` loads every `.txt` in a folder at once
- How `metadata` records the source file for traceability

---

## Why Start with Text Files

A `.txt` file is nothing but plain characters. There are:

```text
No fonts         No tables        No layout
No images        No page numbers  No hidden markup
```

Compare that with a PDF, where the text is buried inside compressed objects, or an HTML page, where the real content is mixed with tags. With `.txt` there is nothing to extract or clean — loading is basically "read the file, done." That makes it the perfect format for learning the *shape* of a loader before the harder formats in chapters 03–04.

The repo's `docs/` folder already contains three text files:

```text
docs/
├── google.txt
├── microsoft.txt
└── Nvidia.txt
```

---

## What Is a LangChain Document?

When a loader reads a file, it does not return a plain string. It returns a **`Document` object** with two attributes:

```text
Document
  ├── page_content   →  the extracted text (a string)
  └── metadata       →  a dictionary of facts about the document
```

For a text file, LangChain automatically records the file path in metadata:

```json
{
  "page_content": "Google LLC ... is an American multinational corporation ...",
  "metadata": {
    "source": "docs\\google.txt"
  }
}
```

This is the single most important idea in the module: **text alone is not enough — you always keep the context of where it came from.** Later, when a chunk is retrieved, its `metadata` tells you exactly which document it belongs to.

---

## TextLoader: Load One File

`TextLoader` is the simplest loader in `langchain_community`. You give it one file path and it returns a list containing one `Document`:

```python
from langchain_community.document_loaders import TextLoader

loader = TextLoader("docs/google.txt", encoding="utf-8")
documents = loader.load()

print(documents[0].page_content[:100])   # first 100 characters
print(documents[0].metadata)             # {'source': 'docs\\google.txt'}
```

```text
Google
Google LLC (/ˈɡuːɡəl/ ⓘ , GOO-gəl) is an Google LLC
{'source': 'docs\\google.txt'}
```

Notes:

- `encoding="utf-8"` avoids errors on files with special characters.
- `.load()` always returns a **list** of `Document` objects — even when there is only one.

---

## DirectoryLoader: Load Every .txt in a Folder

Loading files one at a time gets tedious. `DirectoryLoader` loads **everything matching a pattern** in a folder, and it accepts another loader as its engine:

```python
from langchain_community.document_loaders import TextLoader, DirectoryLoader

loader = DirectoryLoader(
    path="docs",
    glob="*.txt",
    loader_cls=TextLoader,
    loader_kwargs={"encoding": "utf-8"},
)

documents = loader.load()
print(f"Loaded {len(documents)} documents")
```

```text
Loaded 3 documents
```

What is happening:

- `path="docs"` — the folder to scan
- `glob="*.txt"` — only files ending in `.txt`
- `loader_cls=TextLoader` — use `TextLoader` to read each matching file
- `loader_kwargs` — settings passed to `TextLoader` (here, the encoding)

Each file in `docs/` becomes one `Document`, and every one carries its source in metadata:

```python
for doc in documents:
    print(doc.metadata["source"], "-", len(doc.page_content), "characters")
```

```text
docs\google.txt - 15789 characters
docs\microsoft.txt - 13902 characters
docs\Nvidia.txt - 9847 characters
```

(Character counts will vary — the important part is one `Document` per file, each tagged with its source.)

---

## Running the Example

The module script [01-loading-txt-pdf-docx.py](01-loading-txt-pdf-docx.py) combines everything you just learned. For text files it uses `DirectoryLoader` + `TextLoader` on `docs/`, then prints, for the first few documents:

```text
Text document 1:
  Source: ...\docs\google.txt
  Content length: 15789 characters
  Content preview: Google
Google LLC (......
  Metadata: {'source': '...\docs\google.txt'}
```

Run it from the repo root:

```bash
python "Module-3-Document-Loading/01-loading-txt-pdf-docx.py"
```

The script also scans for any `.pdf` and `.docx` files you drop into `docs/` — add one and re-run to see chapters 03 and 04 loaders kick in.

---

## Real-World Example: Employee Directory

Your company keeps employee bios as plain `.txt` files on a shared drive, one per person:

```text
C:\shared\employees\aisha-patel.txt
C:\shared\employees\dmitri-volkov.txt
C:\shared\employees\mei-lin.txt
```

With `DirectoryLoader` you ingest all of them in one call, and every bio is automatically tagged with its source file. That means when the assistant later answers *"what does Aisha Patel work on?"*, the retrieved chunk can point straight back to `aisha-patel.txt` — source traceability with zero extra code.

---

## Key Takeaways

- Text files are the **simplest format** and the best way to learn loaders.
- A LangChain `Document` has two parts: **`page_content`** (the text) and **`metadata`** (facts about the document).
- `TextLoader` loads **one file**; `DirectoryLoader` loads **many files** matching a `glob` pattern.
- Every text document carries its **`source`** in metadata — free traceability.
- `.load()` returns a **list** of `Document` objects, even for a single file.

---

## Test Yourself

1. What are the two attributes of a LangChain `Document` object?
2. What does `metadata["source"]` contain after loading `docs/google.txt`?
3. Which loader would you use to load *every* `.txt` file in a folder?
4. Why does `TextLoader` work so much better on `.txt` files than on PDFs?
5. In the employee-directory example, why is keeping the `source` in metadata valuable?

<details>
<summary>Answers</summary>

1. `page_content` (the extracted text) and `metadata` (a dictionary of facts about the document, like its source file).
2. The file path, e.g. `docs\google.txt` — it tells you which document the text came from.
3. `DirectoryLoader` with `glob="*.txt"` and `loader_cls=TextLoader`.
4. Because a `.txt` file is already plain text — there is no structure to extract from. A PDF hides its text inside internal objects.
5. Because when a chunk is retrieved, `metadata["source"]` lets you trace the answer back to the exact bio file it came from — essential for citations and debugging.

</details>

---

## Next Chapter

Next up: [03-Loading-PDFs.md](03-Loading-PDFs.md) — the most common enterprise format, and the one that causes the most trouble.
