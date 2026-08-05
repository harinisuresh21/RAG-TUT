from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

load_dotenv()

persistent_directory = "db/chroma_db"

embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

db = Chroma(
    persist_directory=persistent_directory,
    embedding_function=embedding_model,
    collection_metadata={"hnsw:space": "cosine"}
)

query = "How much did Microsoft pay to acquire GitHub?"

print("Step 1: Vector search returns candidates (k=5)\n")
retriever = db.as_retriever(search_kwargs={"k": 5})
candidates = retriever.invoke(query)

for i, doc in enumerate(candidates, 1):
    first_line = doc.page_content.split("\n")[0]
    print(f"  Candidate {i}: {first_line}")

print("\nStep 2: Rerank candidates with a cross-encoder\n")
try:
    from sentence_transformers import CrossEncoder

    reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    pairs = [[query, doc.page_content] for doc in candidates]
    scores = reranker.predict(pairs)

    ranked = sorted(zip(scores, candidates), key=lambda x: x[0], reverse=True)

    print("  Reranked order (score | first line):")
    for score, doc in ranked:
        first_line = doc.page_content.split("\n")[0]
        print(f"    {score:.2f} | {first_line}")

    print("\n  Final context sent to the LLM (top 3):")
    for score, doc in ranked[:3]:
        first_line = doc.page_content.split("\n")[0]
        print(f"    - {first_line}")

except ImportError:
    print("  sentence-transformers is not installed.")
    print("  Install it with: pip install sentence-transformers")
    print("  (On first run it also downloads the cross-encoder model.)")
