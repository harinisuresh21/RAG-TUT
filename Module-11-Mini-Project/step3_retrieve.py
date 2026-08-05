"""
STEP 3: Retrieve

Goal: given a user question, find the most relevant chunks in the vector
store built by step 2. This is the "R" in RAG — retrieval.

  Question  ->  Embed  ->  Vector search (top 5)  ->  Chunks with sources

We load `db/knowledge_assistant` with the SAME HuggingFaceEmbeddings model
used in step 2. Embeddings are model-specific: mixing models would make the
similarity scores meaningless, so always use the same one on both sides.

This step also includes an OPTIONAL reranking section (turned off by
default) that re-orders the retrieved chunks with a cross-encoder for even
better precision. You can flip USE_RERANKING to True to try it.

Run this from the REPO ROOT so the relative path resolves:
    python "Module-11-Mini-Project/step3_retrieve.py"
"""

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

persist_directory = "db/knowledge_assistant"
TOP_K = 5

# Flip this to True to re-order the retrieved chunks with a cross-encoder
# reranker (downloads a small model on first use). Plain similarity search
# already works fine — this just sharpens the ordering.
USE_RERANKING = False


def load_vector_store():
    """Load the vector store built by step 2 (same embedding model!)."""
    print(f"Loading vector store from {persist_directory}...")

    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    return Chroma(
        persist_directory=persist_directory,
        embedding_function=embedding_model,
        collection_metadata={"hnsw:space": "cosine"}
    )


def rerank_documents(query, documents, top_k=TOP_K):
    """Optional: re-order retrieved chunks by true relevance.

    A cross-encoder looks at the question and each chunk TOGETHER (unlike
    the embedding-model bi-encoder, which encodes them separately), which
    gives a much sharper relevance score.
    """
    from sentence_transformers import CrossEncoder

    print("Reranking the retrieved chunks...")
    reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    pairs = [[query, doc.page_content] for doc in documents]
    scores = reranker.predict(pairs)

    ranked = sorted(zip(documents, scores), key=lambda pair: pair[1], reverse=True)
    return [doc for doc, _ in ranked[:top_k]]


def print_documents(documents):
    """Print each chunk with the file it came from."""
    for i, doc in enumerate(documents, 1):
        source = doc.metadata.get("source", "unknown")
        print(f"\n--- Retrieved chunk {i} ---")
        print(f"Source: {source}")
        print(f"Content: {doc.page_content[:300]}...")


def main():
    """Run step 3: retrieve the top-k chunks for a question."""
    print("=== Step 3: Retrieval ===\n")

    # Friendly guard: if the store is missing, tell the user to run step2.
    try:
        db = load_vector_store()
    except Exception as e:
        print(f"Could not load the vector store: {e}")
        print("Did you run step2_build_vector_store.py first?")
        print("That script creates db/knowledge_assistant before you can retrieve.")
        return

    # Accept a typed question, or fall back to a built-in example.
    question = input("Your question (press Enter to use the example): ").strip()
    if not question:
        question = "How much did Microsoft pay to acquire GitHub?"

    print(f"\nQuery: {question}\n")

    # Step 1: plain similarity search — the top-5 most similar chunks.
    retriever = db.as_retriever(search_kwargs={"k": TOP_K})
    documents = retriever.invoke(question)

    print(f"Found {len(documents)} chunks from similarity search:")
    print_documents(documents)

    # Step 2 (optional): re-order the results with a cross-encoder reranker.
    if USE_RERANKING:
        print("\n" + "-" * 60)
        reranked = rerank_documents(question, documents)
        print(f"Top {len(reranked)} chunks AFTER reranking:")
        print_documents(reranked)

    print("\nStep 3 complete! These chunks are the evidence for step4_answer.py.")


if __name__ == "__main__":
    main()
