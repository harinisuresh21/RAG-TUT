"""
STEP 2: Build the Vector Store

Goal: turn the raw documents from step 1 into a searchable index.

  Load  ->  Chunk (RecursiveCharacterTextSplitter)  ->  Embed  ->  Store

- Chunking: long files are split into ~1000-character pieces with a
  200-character overlap so meaning is not lost at the seam between chunks.
- Embedding: every chunk is converted into a vector with the local
  all-MiniLM-L6-v2 model (fully offline, no API key needed).
- Storing: the vectors are persisted to ChromaDB at `db/knowledge_assistant`.

IMPORTANT: this project uses its OWN folder (`db/knowledge_assistant`),
separate from the course's `db/chroma_db`, so the mini project is
self-contained and never touches the other modules' data.

The script is IDEMPOTENT: if `db/knowledge_assistant` already exists, it
loads the store instead of re-processing the documents (same early-return
trick as the Module 6 ingestion script).

Run this from the REPO ROOT so the relative paths resolve:
    python "Module-11-Mini-Project/step2_build_vector_store.py"
"""

import os
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# This project's own vector store location (note: NOT db/chroma_db).
persist_directory = "db/knowledge_assistant"


def load_documents(docs_path="docs"):
    """Load all text files from the docs directory (same logic as step1)."""
    print(f"Loading documents from {docs_path}...")

    if not os.path.exists(docs_path):
        raise FileNotFoundError(
            f"The directory {docs_path} does not exist. "
            "Please create it and add your company files."
        )

    loader = DirectoryLoader(
        path=docs_path,
        glob="*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )

    documents = loader.load()

    if len(documents) == 0:
        raise FileNotFoundError(
            f"No .txt files found in {docs_path}. Please add your company documents."
        )

    print(f"Loaded {len(documents)} document(s).")
    return documents


def split_documents(documents, chunk_size=1000, chunk_overlap=200):
    """Split documents into overlapping chunks with a recursive splitter."""
    print(f"Splitting documents into chunks (size={chunk_size}, overlap={chunk_overlap})...")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        # Split on paragraph breaks first, then newlines, then sentences —
        # this keeps chunks semantically whole instead of cutting mid-thought.
        separators=["\n\n", "\n", ".", " ", ""]
    )

    chunks = text_splitter.split_documents(documents)

    print(f"Created {len(chunks)} chunks.")

    if chunks:
        first = chunks[0]
        print(f"\nPreview of chunk 1 (from {first.metadata.get('source', 'unknown')}):")
        print(f"  Length: {len(first.page_content)} characters")
        print(f"  Content: {first.page_content[:150]}...")

    return chunks


def create_vector_store(chunks, persist_directory=persist_directory):
    """Embed the chunks and persist them to ChromaDB."""
    print(f"Embedding chunks with all-MiniLM-L6-v2 and saving to {persist_directory}...")

    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=persist_directory,
        # Cosine distance is a good default for embedding similarity.
        collection_metadata={"hnsw:space": "cosine"}
    )

    print(f"--- Finished creating vector store at {persist_directory} ---")
    return vectorstore


def main():
    """Run step 2: chunk, embed, and store the documents."""
    print("=== Step 2: Build the Vector Store ===\n")

    # Idempotency check: if the store already exists, just load it.
    if os.path.exists(persist_directory):
        print(f"Vector store already exists at {persist_directory}. "
              "Loading it instead of re-processing documents...")

        embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=embedding_model,
            collection_metadata={"hnsw:space": "cosine"}
        )
        print(f"Loaded existing store with {vectorstore._collection.count()} chunks.")
        print(f"Store location: {persist_directory}")
        return vectorstore

    print(f"Store not found. Building it for the first time...\n")

    # Step 1: Load the raw documents.
    documents = load_documents("docs")

    # Step 2: Split them into overlapping chunks.
    chunks = split_documents(documents)

    # Step 3: Embed the chunks and persist them to ChromaDB.
    create_vector_store(chunks, persist_directory)

    print(f"\nStep 2 complete! {len(chunks)} chunks are stored at {persist_directory}.")
    print("Next: run step3_retrieve.py to search the store.")


if __name__ == "__main__":
    main()
