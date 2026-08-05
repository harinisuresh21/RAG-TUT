"""FAISS example: build, search, save, and reload an in-memory FAISS store.

Builds a FAISS vector store (langchain_community.vectorstores.FAISS) from a
few example sentences using the local all-MiniLM-L6-v2 model, runs a
similarity search, then saves the index to db/faiss_index and reloads it to
prove the persistence round-trip works.

Run from the repo root:
    python "Module-6-Vector-Databases/03-faiss-example.py"

Requires: langchain-community, langchain-huggingface, sentence-transformers
Runs fully offline (weights download once on first use).
"""

import os
import shutil

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

PERSIST_DIR = "db/faiss_index"

EXAMPLE_SENTENCES = [
    "Employees receive 30 annual leave days per year.",
    "Vacation requests must be submitted at least two weeks in advance.",
    "All employees must complete security awareness training annually.",
    "The office dress code is business casual.",
    "Expense reports must be submitted within 30 days of the trip.",
]


def load_embedding_model():
    """Load the all-MiniLM-L6-v2 embedding model with a friendly error message"""
    try:
        print("Loading embedding model all-MiniLM-L6-v2 (first run downloads weights)...")
        embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        print("Embedding model loaded.\n")
        return embedding_model
    except ImportError:
        print(
            "\nERROR: The 'sentence-transformers' package is missing.\n"
            "Install it with:\n"
            "    pip install sentence-transformers\n"
            "(or run: pip install -r requirements.txt)\n"
            "Then run this script again."
        )
        raise
    except Exception as e:
        print(
            f"\nERROR: Could not load the embedding model.\n"
            f"Reason: {e}\n"
            "Make sure 'sentence-transformers' is installed and that you have\n"
            "an internet connection for the one-time weight download."
        )
        raise


def print_results(query, results, k):
    """Print the top-k results for a query"""
    print(f'Query: "{query}"')
    for i, doc in enumerate(results[:k], 1):
        print(f"  Result {i}: {doc.page_content}")
    print()


def main():
    """Build a FAISS store, search it, save it, and reload it"""
    print("=== FAISS Vector Store Example ===\n")

    embedding_model = load_embedding_model()

    # Step 1: Build the store in memory
    print("Building in-memory FAISS store from example sentences...")
    vectorstore = FAISS.from_texts(EXAMPLE_SENTENCES, embedding_model)
    print(f"Created FAISS store with {len(EXAMPLE_SENTENCES)} sentences.\n")

    # Step 2: Search before saving
    print("--- Search 1: on the in-memory store ---")
    query = "How many leave days do employees get?"
    results = vectorstore.similarity_search(query, k=2)
    print_results(query, results, 2)

    # Step 3: Save to a local folder
    if os.path.exists(PERSIST_DIR):
        print(f"Removing previous {PERSIST_DIR} for a clean save...")
        shutil.rmtree(PERSIST_DIR)

    print(f"Saving FAISS index to {PERSIST_DIR}...")
    vectorstore.save_local(PERSIST_DIR)
    print("Saved. Files in the folder: index.faiss (vectors) + index.pkl (texts/metadata).\n")

    # Step 4: Reload from disk
    print(f"Reloading FAISS index from {PERSIST_DIR}...")
    loaded = FAISS.load_local(
        PERSIST_DIR,
        embedding_model,
        allow_dangerous_deserialization=True,
    )
    print("Reloaded successfully.\n")

    # Step 5: Search after reloading (proves the round-trip worked)
    print("--- Search 2: on the reloaded store ---")
    results_after = loaded.similarity_search(query, k=2)
    print_results(query, results_after, 2)

    print("=" * 70)
    print("What to notice")
    print("=" * 70)
    print("- The same query on the reloaded store returns the same top chunks.")
    print("- FAISS stores vectors in index.faiss and chunk text in index.pkl.")
    print("- The store is ephemeral unless you call save_local() - always save.")


if __name__ == "__main__":
    main()
