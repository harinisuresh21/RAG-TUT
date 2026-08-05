# Similarity Search

## Introduction

The default and most common way a vector store finds chunks is **similarity search**: embed the query, compare it to every chunk vector, and return the ones with the highest cosine similarity. It is simple, fast, and good enough for most RAG systems.

In this chapter you will read `01-retrieval-pipeline.py` line by line — the script this module is built around — and see exactly what it returns.

---

## Learning Objectives

By the end of this chapter, you will:

- Explain what the default retriever does under the hood
- Walk through every line of `01-retrieval-pipeline.py`
- Describe what a returned `Document` looks like (`page_content` + `metadata`)
- Explain what `k` means and how it changes the output

---

## What Similarity Search Does

ChromaDB stores each chunk as a vector. A query arrives and goes through the same embedding model, producing a query vector. The store then computes a similarity score between the query vector and every chunk vector, sorts them, and keeps the top `k`.

```text
Query vector
    │
    ├─ compare with chunk vectors (cosine similarity)
    │
    ▼
0.78  microsoft.txt (GitHub acquisition)   ← top 1
0.41  microsoft.txt (ZeniMax deal)
0.38  microsoft.txt (LinkedIn)
0.35  microsoft.txt (Activision)
0.31  microsoft.txt (Yammer)               ← top 5 (k = 5)
```

"Similarity" here is **semantic similarity**: two texts score high if they mean similar things, even with different words.

---

## Walking Through 01-retrieval-pipeline.py

Here is the whole script (already in this folder). We'll read it top to bottom.

### 1. Imports and environment

```python
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()
```

- `Chroma` is the LangChain wrapper around ChromaDB — the same class Module 6 used to build the store.
- `OpenAIEmbeddings` embeds the query (and would embed chunks, if we were ingesting).
- `load_dotenv()` reads `OPENAI_API_KEY` from the `.env` file.

### 2. Load the vector store

```python
persistent_directory = "db/chroma_db"

embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

db = Chroma(
    persist_directory=persistent_directory,
    embedding_function=embedding_model,
    collection_metadata={"hnsw:space": "cosine"}
)
```

This opens the store that Module 6 built and saved to disk. Three things matter:

- `persist_directory` points at the persisted store — no re-ingestion needed.
- `embedding_function` must match the query embedding model.
- `collection_metadata={"hnsw:space": "cosine"}` must match the space the store was created with, so scores are comparable.

### 3. Create a retriever

```python
query = "How much did Microsoft pay to acquire GitHub?"

retriever = db.as_retriever(search_kwargs={"k": 5})
```

`db.as_retriever()` builds a retriever from the store. `search_kwargs={"k": 5}` says: return the **5 most similar chunks**.

### 4. Invoke it

```python
relevant_docs = retriever.invoke(query)
```

This runs the whole retrieval pipeline and returns a list of `Document` objects.

### 5. Print the results

```python
print(f"User Query: {query}")
print("--- Context ---")
for i, doc in enumerate(relevant_docs, 1):
    print(f"Document {i}:\n{doc.page_content}\n")
```

---

## What a Retrieved Document Looks Like

Every chunk comes back as a LangChain `Document` with two important fields:

```text
page_content : the raw chunk text
metadata     : a dictionary of extra info, e.g. {'source': 'docs/microsoft.txt'}
```

For the sample query you would see something like:

```text
User Query: How much did Microsoft pay to acquire GitHub?
--- Context ---
Document 1:
On June 4, 2018, Microsoft officially announced the acquisition of GitHub for $7.5 billion, a deal that closed on October 26, 2018...
```

`doc.page_content` is the text the LLM will see. `doc.metadata` is used later for **citations** (Module 8) and **filtering** (chapter 05).

---

## What `k` Means

`k` is the number of chunks the retriever returns:

```text
k = 1  →  only the single best chunk
k = 5  →  the five best chunks
k = 20 →  the twenty best chunks
```

Small `k` keeps the prompt focused but risks leaving out the fact you need. Large `k` makes sure nothing is missed but fills the prompt with noise — which costs tokens and confuses the model. Chapter 05 gives rules of thumb; the sample scripts in this course use `k = 5` (and `k = 3` in the Module 8 pipeline).

---

## Enterprise Example

An HR knowledge assistant is asked:

```text
"What is the company's remote work policy?"
```

The retriever embeds the query and returns the 5 most similar chunks from the policy library. The number-one chunk is a paragraph from the *Remote Work Policy* document. The assistant's answer, a moment later, will be grounded in exactly that paragraph — because similarity search found it.

---

## Key Takeaways

- Similarity search = **embed query → score every chunk → return top-k**.
- `db.as_retriever(search_kwargs={"k": 5})` uses the default search type.
- Returned chunks are `Document` objects with **`page_content`** and **`metadata`**.
- `k` controls how many chunks enter the prompt.
- The store must be loaded with the same embedding model and distance space it was created with.

---

## Test Yourself

1. What happens inside the store when `retriever.invoke(query)` is called?
2. What two fields does a returned `Document` have?
3. What does the `"hnsw:space": "cosine"` argument tell Chroma?
4. What is the default search type of `db.as_retriever()`?
5. If `k = 3` and only two chunks are relevant, what is the third chunk?

<details>
<summary>Answers</summary>

1. The query is **embedded**, compared to every chunk vector, and the **top-k most similar chunks** are returned.
2. `page_content` (the chunk text) and `metadata` (extra info like the source file).
3. It tells Chroma to use **cosine** as the distance metric, so similarity scores are computed as cosine similarity.
4. Plain **similarity search**.
5. The **next most similar chunk** — which may be irrelevant "noise", which is exactly the trade-off chapters 03 and 04 deal with.

</details>

---

## Next Chapter

Next up: [03-Similarity-Score-Thresholds.md](03-Similarity-Score-Thresholds.md) — only keep chunks that are similar *enough*.
