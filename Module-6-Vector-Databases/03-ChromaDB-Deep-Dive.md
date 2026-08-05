# ChromaDB Deep Dive

## Introduction

The best way to learn a vector database is to read a real one being built. This chapter walks through `Module-6-Vector-Databases/01-ingestion-pipeline.py` **line by line** — the script that turns `docs/` into a persistent ChromaDB store at `db/chroma_db`.

This is the single most important script in the course. Every later module reads from the store it builds. By the end of this chapter you will be able to explain every line of it, and you will know how to load an existing store and how to query it later.

---

## Learning Objectives

By the end of this chapter, you will understand:

- The full ingestion flow: load → chunk → embed → store
- What `DirectoryLoader` and `CharacterTextSplitter` do in this script
- What `Chroma.from_documents` does with `persist_directory` and `collection_metadata`
- How the script loads an **existing** store instead of re-ingesting (the early-return path)
- What `{"hnsw:space": "cosine"}` means and why it matters
- How to query the store later (spoiler: Module 7)

---

## The Script at a Glance

The whole script is four steps wearing function-shaped coats:

```python
load_documents()     →  read docs/*.txt
split_documents()    →  cut into chunks
create_vector_store()→  embed + store in ChromaDB
main()               →  orchestrate, or load an existing store
```

```text
docs/*.txt  →  DirectoryLoader  →  TextSplitter  →  Embeddings  →  Chroma.from_documents
  (files)         (pages)           (chunks)          (vectors)        (db/chroma_db)
```

Open `01-ingestion-pipeline.py` next to this chapter and follow along.

---

## Line-by-Line Walkthrough

### Step 0 — Imports and Environment

```python
import os
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

load_dotenv()
```

Each import maps to one stage of the pipeline:

```text
os                              →  file checks and paths
TextLoader / DirectoryLoader    →  document loading (Module 3)
CharacterTextSplitter           →  chunking (Module 4)
HuggingFaceEmbeddings           →  embedding (Module 5)
Chroma                          →  the vector database (this module)
load_dotenv()                   →  reads .env (needed if you switch to OpenAI embeddings)
```

---

### Step 1 — Load Documents

```python
def load_documents(docs_path="docs"):
    """Load all text files from the docs directory"""
    print(f"Loading documents from {docs_path}...")

    if not os.path.exists(docs_path):
        raise FileNotFoundError(f"The directory {docs_path} does not exist. ...")

    loader = DirectoryLoader(
        path=docs_path,
        glob="*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )

    documents = loader.load()
```

What each piece does:

```text
DirectoryLoader(path="docs", glob="*.txt")   →  grab every .txt file in docs/
loader_cls=TextLoader                         →  read each as plain text
loader_kwargs={"encoding": "utf-8"}           →  handle unicode safely
loader.load()                                 →  returns Document objects
```

A `Document` has two fields — the text in `page_content` and facts about it in `metadata`:

```python
Document(page_content="Google is an American multinational ...",
         metadata={"source": "docs/google.txt"})
```

The script then prints a preview of the first two documents so you can verify loading worked.

---

### Step 2 — Split Into Chunks

```python
def split_documents(documents, chunk_size=1000, chunk_overlap=0):
    """Split documents into smaller chunks with overlap"""

    text_splitter = CharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    chunks = text_splitter.split_documents(documents)
```

Module 4 territory, applied for real:

```text
chunk_size    = 1000   →  each chunk up to ~1000 characters
chunk_overlap = 0      →  no shared text between neighbors (simple default)
```

Key point: `split_documents` (not `split_text`) **carries the metadata over**. Each chunk inherits `metadata["source"]` from its parent document — that is what enables metadata filtering in chapter 05.

```text
Document(source="docs/microsoft.txt")
  └── Chunk A (source="docs/microsoft.txt")   ← metadata travels with the chunk
  └── Chunk B (source="docs/microsoft.txt")
  └── ...
```

The script prints the first five chunks with their source and content length, so you can see exactly what will be embedded.

---

### Step 3 — Embed and Store

```python
def create_vector_store(chunks, persist_directory="db/chroma_db"):
    """Create and persist ChromaDB vector store"""
    print("Creating embeddings and storing in ChromaDB...")

    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # Create ChromaDB vector store
    print("--- Creating vector store ---")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=persist_directory,
        collection_metadata={"hnsw:space": "cosine"}
    )
    print("--- Finished creating vector store ---")

    print(f"Vector store created and saved to {persist_directory}")
    return vectorstore
```

Decode the arguments:

```text
documents=chunks             →  the chunks from step 2 (text + metadata)
embedding=embedding_model    →  how to turn each chunk into a 384-dim vector
persist_directory="db/chroma_db"  →  where to save the store on disk
collection_metadata={"hnsw:space": "cosine"}  →  the similarity metric (below)
```

`Chroma.from_documents` does the heavy lifting in one call:

```text
for each chunk:
    text + metadata → embed (all-MiniLM-L6-v2) → vector
store all vectors with an HNSW index → save the whole store to db/chroma_db
```

The result on disk is a real database folder — not a temp object in memory. You can close Python, come back tomorrow, and reload it.

### The `{"hnsw:space": "cosine"}` Setting

This tells ChromaDB which metric the HNSW index should use for comparisons:

```text
"cosine"      →  cosine similarity (Module 5 chapter 03) — the default here
"l2"          →  euclidean distance
"ip"          →  inner product (dot product)
```

Setting `"hnsw:space": "cosine"` matches how we defined "similar" in Module 5: compare by **angle/direction**, not by length. It is deliberately the same metric taught in chapter 03 and used in the retrieval scripts.

> When you load the store later, you must pass the **same** `collection_metadata` — ChromaDB uses it to build the search index the same way.

---

### Step 4 — main(): Build or Load (The Early-Return Path)

```python
def main():
    """Main ingestion pipeline"""
    print("=== RAG Document Ingestion Pipeline ===\n")

    docs_path = "docs"
    persistent_directory = "db/chroma_db"

    # Check if vector store already exists
    if os.path.exists(persistent_directory):
        print("Vector store already exists. No need to re-process documents.")

        embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vectorstore = Chroma(
            persist_directory=persistent_directory,
            embedding_function=embedding_model,
            collection_metadata={"hnsw:space": "cosine"}
        )
        print(f"Loaded existing vector store with {vectorstore._collection.count()} documents")
        return vectorstore

    print("Persistent directory does not exist. Initializing vector store...\n")

    # Step 1: Load documents
    documents = load_documents(docs_path)

    # Step 2: Split into chunks
    chunks = split_documents(documents)

    # Step 3: Create vector store
    vectorstore = create_vector_store(chunks, persistent_directory)

    print("\nIngestion complete! Your documents are now ready for RAG queries.")
    return vectorstore
```

This is the pattern you will copy everywhere. Two behaviors:

**If `db/chroma_db` exists** → do NOT re-process. Rebuild a `Chroma` object pointed at the existing folder:

```python
vectorstore = Chroma(
    persist_directory=persistent_directory,   # open the existing folder
    embedding_function=embedding_model,       # must match the model used to build it
    collection_metadata={"hnsw:space": "cosine"}
)
```

Note the **different parameter name** from step 3: `embedding_function` here vs `embedding` in `from_documents`. Both mean "the model that turns text into vectors" — LangChain just uses different keywords for the constructor vs the builder.

**If `db/chroma_db` does not exist** → run the full pipeline: load → split → embed → persist.

The `return vectorstore` inside the `if` is what makes it an **early return** — the rest of the function never runs when the store already exists.

```text
Run 1: db/chroma_db missing → full ingestion, store saved
Run 2: db/chroma_db exists  → load it, print count, return immediately
Run 3: same → still instant
```

That is idempotency: running the script twice is as safe as running it once. Chapter 05 revisits this pattern.

---

## How to Query the Store Later

Building the store is only half the story. To actually use it you run a similarity search against the loaded `Chroma` object:

```python
results = vectorstore.similarity_search("How many leave days do I get?", k=5)
```

Or the retriever flavor:

```python
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
relevant_docs = retriever.invoke("How many leave days do I get?")
```

The search embeds your query with the **same model** that built the store, then asks the HNSW index for the nearest chunks.

> **Deep dive: covered in Module 7** — [Module 7: Retrieval](../Module-7-Retrieval/README.md) turns this one-liner into a full retrieval pipeline with score thresholds, MMR, and tuning `k`. `Module-7-Retrieval/01-retrieval-pipeline.py` already loads `db/chroma_db` and runs `as_retriever`.

---

## Real Enterprise Example

The script above is the skeleton of a production ingestion service. An enterprise version adds:

```text
More loaders         →  PDF, DOCX, HTML (Module 3)
Better splitters     →  recursive or semantic chunking (Module 4)
More metadata        →  department, date, author (chapter 05 of this module)
A cron/scheduler     →  re-run ingestion nightly on new files
```

The core loop is identical: `load → chunk → embed → Chroma.from_documents(persist_directory=...)`. Once you can explain this script, you can explain most production ingestion pipelines.

---

## Key Takeaways

- The ingestion flow is **load → chunk → embed → store**, one function per step.
- `DirectoryLoader` reads every `.txt` in `docs/` into `Document` objects (text + metadata).
- `CharacterTextSplitter` cuts documents into chunks while **carrying metadata forward**.
- `Chroma.from_documents(...)` embeds every chunk and persists a real store to `db/chroma_db`.
- `{"hnsw:space": "cosine"}` selects cosine similarity as the HNSW index metric.
- The **early-return pattern** loads an existing store instead of re-processing — the idempotency trick.
- You query later with `similarity_search` or `as_retriever` (Module 7).

---

## Test Yourself

1. What does `DirectoryLoader` return for each text file?
2. Why does the splitter carry metadata from the document into each chunk?
3. Which class and method creates and persists the vector store in one call?
4. What does `{"hnsw:space": "cosine"}` tell ChromaDB?
5. What happens if you run `01-ingestion-pipeline.py` twice in a row?

<details>
<summary>Answers</summary>

1. A **`Document` object** with `page_content` (the text) and `metadata` (e.g. `{"source": "docs/google.txt"}`).
2. So each chunk knows where it came from — which enables **metadata filtering** (chapter 05) and later citation of sources.
3. **`Chroma.from_documents(...)`** — it takes the chunks and embedding model, builds the store, and saves it to `persist_directory`.
4. That the HNSW index should measure similarity with **cosine similarity** (angle/direction) instead of euclidean distance or dot product.
5. On the second run the `if os.path.exists(persistent_directory)` branch fires, so it **loads the existing store** and returns immediately instead of re-processing the documents.

</details>

---

## Next Chapter

Next up: [04-FAISS-Deep-Dive.md](04-FAISS-Deep-Dive.md) — a second vector store implementation and a Chroma vs FAISS comparison.
