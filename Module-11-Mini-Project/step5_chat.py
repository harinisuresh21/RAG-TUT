"""
STEP 5: Chat with History — the finished Company Knowledge Assistant

Goal: bring everything from the course together into one chat loop.

For every turn the assistant:
  1. REWRITES the question — if it is a follow-up ("and when was that?"),
     the chat history turns it into a standalone, searchable question.
  2. RETRIEVES the top-5 most relevant chunks from db/knowledge_assistant.
  3. GENERATES a GROUNDED answer — GPT-4o may only use the retrieved
     documents, must end with source citations (Source: <file>), and must
     honestly say "I don't know" when the evidence is missing.
  4. REMEMBERS — the Human and AI messages are appended to chat_history so
     the next turn has context.

Type 'quit' to exit. Requires OPENAI_API_KEY in your .env for steps 1 and 3.

This follows the style of Module 9's history-aware generation script.
Run it from the REPO ROOT:
    python "Module-11-Mini-Project/step5_chat.py"
"""

import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI

load_dotenv()

persist_directory = "db/knowledge_assistant"
TOP_K = 5

# ---------------------------------------------------------------------------
# Load the vector store built by step 2. We use the SAME HuggingFaceEmbeddings
# model as step 2 — a mismatch would make the similarity search meaningless.
# ---------------------------------------------------------------------------
try:
    print(f"Loading vector store from {persist_directory}...")
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    db = Chroma(
        persist_directory=persist_directory,
        embedding_function=embedding_model,
        collection_metadata={"hnsw:space": "cosine"}
    )
    print("Store loaded.")
except Exception as e:
    print(f"Could not load the vector store: {e}")
    print("Did you run step2_build_vector_store.py first?")
    raise SystemExit(1)

# Set up the generation model (needs OPENAI_API_KEY in your .env).
model = ChatOpenAI(model="gpt-4o")

# Chat history: grows with every turn so the model can understand follow-ups.
chat_history = []


def get_source(doc):
    """Return just the file name for a chunk's metadata source (for citations)."""
    return os.path.basename(doc.metadata.get("source", "unknown"))


def ask_question(user_question):
    """Run one full RAG turn for a user question."""
    print(f"\n--- You asked: {user_question} ---")

    # Step 1: REWRITE the question using the chat history.
    # A follow-up like "and when was that?" only makes sense with context,
    # so we ask the model to turn it into a standalone searchable question.
    search_question = user_question
    if chat_history:
        rewrite_messages = [
            SystemMessage(content="Given the chat history, rewrite the new question "
                                  "to be standalone and searchable. Just return the "
                                  "rewritten question."),
        ] + chat_history + [
            HumanMessage(content=f"New question: {user_question}")
        ]
        search_question = model.invoke(rewrite_messages).content.strip()
        print(f"Searching for: {search_question}")

    # Step 2: RETRIEVE the top-k most relevant chunks.
    retriever = db.as_retriever(search_kwargs={"k": TOP_K})
    documents = retriever.invoke(search_question)

    print(f"Found {len(documents)} relevant chunks:")
    for i, doc in enumerate(documents, 1):
        print(f"  {i}. {get_source(doc)}")

    # Step 3: GENERATE a grounded answer with citations.
    combined_input = f"""Based on the following documents, please answer this question: {user_question}

Documents:
{chr(10).join([f"- [{get_source(doc)}]: {doc.page_content}" for doc in documents])}

Rules:
1. Answer using only the information from these documents.
2. If you can't find the answer in the documents, reply with exactly:
   "I don't have enough information to answer that question based on the provided documents."
3. At the end of your answer, list every source file you used, one per line, like this:
   Source: microsoft.txt
"""

    messages = [
        SystemMessage(content="You are a helpful Company Knowledge Assistant that answers "
                              "questions based on provided documents and conversation history."),
    ] + chat_history + [
        HumanMessage(content=combined_input)
    ]

    answer = model.invoke(messages).content

    # Step 4: REMEMBER this exchange for future turns.
    chat_history.append(HumanMessage(content=user_question))
    chat_history.append(AIMessage(content=answer))

    print(f"\nAnswer: {answer}")
    return answer


def start_chat():
    """The terminal chat loop — this is the final app."""
    print("\nWelcome to the Company Knowledge Assistant!")
    print("Ask me anything about your company documents.")
    print("Type 'quit' to exit.\n")

    while True:
        question = input("Your question: ")

        if question.lower() == 'quit':
            print("Goodbye!")
            break

        if not question.strip():
            continue

        # Friendly guard around each turn (e.g. missing API key).
        try:
            ask_question(question)
        except Exception as e:
            print(f"Something went wrong: {e}")
            print("Check that OPENAI_API_KEY is set in your .env file and try again.")


if __name__ == "__main__":
    start_chat()
