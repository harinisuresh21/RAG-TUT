from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import os


load_dotenv()

persistent_directory = "db/chroma_db"
query = "How much did Microsoft pay to acquire GitHub?"


def print_docs(label, docs):
    """Print a labeled list of retrieved documents."""
    print("=" * 60)
    print(label)
    print("=" * 60)
    if not docs:
        print("No documents passed the threshold.")
        print()
        return
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "unknown")
        print(f"[{i}] source: {source}")
        print(doc.page_content)
        print()


def main():
    """Run the same query through three retrieval strategies and compare the results."""
    if not os.path.exists(persistent_directory):
        print("=" * 60)
        print("VECTOR STORE NOT FOUND")
        print("=" * 60)
        print(f"Expected at: {persistent_directory}")
        print("Run Module 6 ingestion first to build it:")
        print('  python "Module-6-Vector-Databases/01-ingestion-pipeline.py"')
        return

    if not os.getenv("OPENAI_API_KEY"):
        print("=" * 60)
        print("OPENAI API KEY MISSING")
        print("=" * 60)
        print("Add OPENAI_API_KEY=your-key to the .env file in the repo root.")
        print("Example:")
        print('  echo OPENAI_API_KEY=sk-your-key > .env')
        return

    try:
        print("Loading embeddings and vector store from db/chroma_db...")
        embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

        db = Chroma(
            persist_directory=persistent_directory,
            embedding_function=embedding_model,
            collection_metadata={"hnsw:space": "cosine"}
        )

        # Show relevance scores first, so the threshold below makes sense
        scored = db.similarity_search_with_relevance_scores(query, k=5)
        print("\nRelevance scores for the top-5 chunks:")
        for i, (doc, score) in enumerate(scored, 1):
            source = doc.metadata.get("source", "unknown")
            print(f"  [{i}] score {score:.3f}  source: {source}")

        # 1. Plain similarity (the default)
        plain_retriever = db.as_retriever(search_kwargs={"k": 5})
        plain_docs = plain_retriever.invoke(query)

        print_docs("1. PLAIN SIMILARITY (k=5)", plain_docs)

        # 2. Similarity score threshold
        threshold_retriever = db.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "k": 5,
                "score_threshold": 0.3  # Only return chunks with cosine similarity >= 0.3
            }
        )
        threshold_docs = threshold_retriever.invoke(query)

        print_docs("2. SIMILARITY SCORE THRESHOLD (k=5, score_threshold=0.3)", threshold_docs)

        # 3. MMR for diversity
        mmr_retriever = db.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": 5,
                "lambda_mult": 0.5  # balance relevance and diversity
            }
        )
        mmr_docs = mmr_retriever.invoke(query)

        print_docs("3. MMR (k=5, lambda_mult=0.5)", mmr_docs)

        print("=" * 60)
        print("Compare the three lists: which chunks repeat across all three,")
        print("and which differ? The threshold version may drop weak chunks,")
        print("and MMR may swap near-duplicates for more diverse ones.")
        print("=" * 60)

    except Exception as e:
        print("=" * 60)
        print("SOMETHING WENT WRONG")
        print("=" * 60)
        print("Common causes:")
        print("  - db/chroma_db is missing or was built with a different embedding model")
        print("  - OPENAI_API_KEY is missing or invalid")
        print(f"Error details: {e}")


if __name__ == "__main__":
    main()
