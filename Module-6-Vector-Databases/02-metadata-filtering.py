"""Metadata filtering demo: search a ChromaDB store with and without a filter.

Loads the existing vector store from db/chroma_db (built by
Module-6-Vector-Databases/01-ingestion-pipeline.py) and runs the same query
twice: once with no filter and once filtered to a specific source document,
so you can see filtering in action.

Run from the repo root (after running the ingestion pipeline):
    python "Module-6-Vector-Databases/02-metadata-filtering.py"

Requires: langchain-huggingface, langchain-chroma, sentence-transformers
Uses the same all-MiniLM-L6-v2 model that built the store.
"""

import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

persistent_directory = "db/chroma_db"


def load_vector_store():
    """Load the existing Chroma store, or tell the user to run ingestion first"""
    if not os.path.exists(persistent_directory):
        print(
            f"ERROR: No vector store found at {persistent_directory}.\n"
            "Run the ingestion pipeline first:\n"
            '    python "Module-6-Vector-Databases/01-ingestion-pipeline.py"\n'
            "It builds db/chroma_db from the docs/ folder."
        )
        raise FileNotFoundError(
            f"Vector store directory {persistent_directory} does not exist."
        )

    try:
        print("Loading embedding model all-MiniLM-L6-v2...")
        embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        print("Loading vector store from db/chroma_db...")

        vectorstore = Chroma(
            persist_directory=persistent_directory,
            embedding_function=embedding_model,
            collection_metadata={"hnsw:space": "cosine"},
        )
        print(f"Loaded existing vector store with {vectorstore._collection.count()} documents\n")
        return vectorstore
    except Exception as e:
        print(
            f"\nERROR: Could not load the vector store.\n"
            f"Reason: {e}\n"
            "Make sure the ingestion pipeline ran successfully first:\n"
            '    python "Module-6-Vector-Databases/01-ingestion-pipeline.py"'
        )
        raise


def print_results(results, title, k):
    """Print the top-k results of a search under a title"""
    print(f"--- {title} ---")
    if not results:
        print("  (No chunks matched - the filter returned nothing)\n")
        return

    for i, doc in enumerate(results[:k], 1):
        print(f"Result {i}:")
        print(f"  Source: {doc.metadata.get('source', 'unknown')}")
        print(f"  Content: {doc.page_content[:120]}...")
        print()
    print()


def main():
    """Run the same query with and without a metadata filter"""
    print("=== Metadata Filtering Demo ===\n")

    vectorstore = load_vector_store()

    query = "Who founded Microsoft?"

    print("=" * 70)
    print(f'Query: "{query}"')
    print("=" * 70)

    # 1. Search WITHOUT a filter (searches every chunk in the store)
    print("1. SEARCH WITHOUT A FILTER\n")
    results_all = vectorstore.similarity_search(query, k=3)
    print_results(results_all, "Top results across the whole store", 3)

    # 2. Search WITH a filter (only chunks from microsoft.txt)
    print("2. SEARCH WITH FILTER: source contains 'microsoft'\n")
    results_filtered = vectorstore.similarity_search(
        query,
        k=3,
        filter={"source": {"$contains": "microsoft"}},
    )
    print_results(
        results_filtered,
        "Top results limited to docs/microsoft.txt",
        3,
    )

    # 3. Search with a filter that matches NOTHING (graceful handling)
    print("3. SEARCH WITH FILTER THAT MATCHES NOTHING: source contains 'salesforce'\n")
    results_empty = vectorstore.similarity_search(
        query,
        k=3,
        filter={"source": {"$contains": "salesforce"}},
    )
    print_results(
        results_empty,
        "Filtered to a document that does not exist in the store",
        3,
    )

    print("=" * 70)
    print("What to notice")
    print("=" * 70)
    print("- The unfiltered search returns a mix of sources.")
    print("- The filtered search returns only docs/microsoft.txt chunks.")
    print("- An empty filter result is an empty list - no crash.")


if __name__ == "__main__":
    main()
