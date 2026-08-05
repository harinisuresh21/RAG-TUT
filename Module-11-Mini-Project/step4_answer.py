"""
STEP 4: Answer with Citations

Goal: add generation on top of retrieval (this is the "G" in RAG).

  1. Retrieve the top-5 chunks for the question (from step 2's store).
  2. Build a GROUNDED prompt: the chunks are the ONLY evidence GPT-4o
     is allowed to use.
  3. Ask GPT-4o to answer, ending with a source citation for every fact
     (e.g. "Source: microsoft.txt"), and to honestly say "I don't know"
     when the answer is not in the documents.

Printing the retrieved sources first lets you check the evidence BEFORE
the answer — the core habit of a trustworthy RAG system.

This step calls the OpenAI API, so it needs OPENAI_API_KEY in your .env.
A friendly try/except handles a missing key or missing store.

Run this from the REPO ROOT so the relative paths resolve:
    python "Module-11-Mini-Project/step4_answer.py"
"""

import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

persist_directory = "db/knowledge_assistant"
TOP_K = 5


def get_source(doc):
    """Return just the file name for a chunk's metadata source.

    DirectoryLoader stores the full path in metadata['source'], e.g.
    "docs\\microsoft.txt". We want the short name for the citation.
    """
    return os.path.basename(doc.metadata.get("source", "unknown"))


def build_grounded_prompt(question, documents):
    """Build a prompt that forces the model to use ONLY the documents.

    The rules encode the three habits of trustworthy RAG generation:
    1. answer only from the provided documents,
    2. cite the source file for every claim, and
    3. say "I don't know" instead of hallucinating.
    """
    combined_input = f"""You are a Company Knowledge Assistant. Answer the question below using ONLY the provided documents.

Question: {question}

Documents:
{chr(10).join([f"- [{get_source(doc)}]: {doc.page_content}" for doc in documents])}

Rules:
1. Base your answer ONLY on the information inside the documents above.
2. If the documents do not contain the answer, reply with exactly:
   "I don't have enough information to answer that question based on the provided documents."
3. At the end of your answer, list every source file you used, one per line, like this:
   Source: microsoft.txt
"""
    return combined_input


def main():
    """Run step 4: retrieve evidence and generate a cited answer."""
    print("=== Step 4: Grounded Answering with Citations ===\n")

    # Step 0: load the vector store built by step2 (same embedding model).
    try:
        print(f"Loading vector store from {persist_directory}...")
        embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        db = Chroma(
            persist_directory=persist_directory,
            embedding_function=embedding_model,
            collection_metadata={"hnsw:space": "cosine"}
        )
    except Exception as e:
        print(f"Could not load the vector store: {e}")
        print("Did you run step2_build_vector_store.py first?")
        return

    # Step 1: get the question (or use the built-in example).
    question = input("Your question (press Enter to use the example): ").strip()
    if not question:
        question = "How much did Microsoft pay to acquire GitHub?"

    print(f"\nQuery: {question}\n")

    # Step 2: retrieve the top-5 most relevant chunks.
    retriever = db.as_retriever(search_kwargs={"k": TOP_K})
    documents = retriever.invoke(question)

    # Step 3: show the evidence BEFORE the answer, so you can check it.
    print("--- Retrieved Sources ---")
    for i, doc in enumerate(documents, 1):
        print(f"  {i}. {get_source(doc)}")
    print()

    # Step 4: build the grounded prompt and call GPT-4o.
    prompt = build_grounded_prompt(question, documents)

    try:
        model = ChatOpenAI(model="gpt-4o")
        result = model.invoke([
            SystemMessage(content="You are a helpful assistant that answers questions based on provided documents."),
            HumanMessage(content=prompt),
        ])
    except Exception as e:
        print(f"Could not reach the OpenAI API: {e}")
        print("Make sure OPENAI_API_KEY is set in your .env file and try again.")
        return

    # Step 5: show the final grounded answer.
    print("\n--- Answer ---")
    print(result.content)


if __name__ == "__main__":
    main()
