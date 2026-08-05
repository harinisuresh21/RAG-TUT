from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import os


load_dotenv()

persistent_directory = "db/chroma_db"


def main():
    """Compare a weak prompt and a strong grounded prompt on the same context."""
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

        # Search for relevant documents
        query = "How much did Microsoft pay to acquire GitHub?"

        retriever = db.as_retriever(search_kwargs={"k": 3})

        relevant_docs = retriever.invoke(query)

        print(f"User Query: {query}")
        print("--- Context ---")
        for i, doc in enumerate(relevant_docs, 1):
            print(f"Document {i}:\n{doc.page_content}\n")

        # Same context, two different prompt styles
        documents_block = chr(10).join(
            [f"- {doc.page_content}" for doc in relevant_docs]
        )

        # Style 1: WEAK prompt - invites hallucination
        weak_prompt = f"""Question: {query}

Some context you might find useful:
{documents_block}

Answer the question:"""

        # Style 2: STRONG grounded prompt
        strong_prompt = f"""You are an assistant that answers ONLY from the provided documents.

Documents:
{documents_block}

Question: {query}

Instructions:
- Use ONLY the information from the documents above.
- Do not assume facts that are not stated in the documents.
- If the documents do not contain the answer, reply exactly:
  "I don't have enough information to answer that question based on the provided documents."

Answer:"""

        # Create a ChatOpenAI model
        model = ChatOpenAI(model="gpt-4o")

        print("=" * 60)
        print("STYLE 1: WEAK PROMPT (no grounding instructions)")
        print("=" * 60)
        print("The model is asked to answer freely - watch what it does.")
        weak_messages = [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content=weak_prompt),
        ]
        result1 = model.invoke(weak_messages)
        print("\n--- Weak prompt answer ---")
        print(result1.content)

        print()
        print("=" * 60)
        print("STYLE 2: STRONG GROUNDED PROMPT")
        print("=" * 60)
        print("Answer only from documents + 'say you don't know' fallback.")
        strong_messages = [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content=strong_prompt),
        ]
        result2 = model.invoke(strong_messages)
        print("\n--- Strong grounded answer ---")
        print(result2.content)

        print()
        print("=" * 60)
        print("Compare the two answers. The weak prompt lets the model")
        print("lean on its own knowledge; the grounded prompt forces it")
        print("to stay inside the documents and say 'I don't know' when")
        print("the evidence is missing.")
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
