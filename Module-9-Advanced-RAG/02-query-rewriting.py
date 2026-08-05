from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

persistent_directory = "db/chroma_db"

embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

db = Chroma(
    persist_directory=persistent_directory,
    embedding_function=embedding_model,
    collection_metadata={"hnsw:space": "cosine"}
)

model = ChatOpenAI(model="gpt-4o")

# A deliberately vague, conversational-style question
raw_question = "how much did it pay for GitHub?"


def rewrite_query(raw_question):
    """Use the LLM to turn a vague question into a standalone search query"""
    messages = [
        SystemMessage(content="Rewrite the user question into a standalone, clear search query. Just return the rewritten query, nothing else."),
        HumanMessage(content=f"User question: {raw_question}"),
    ]
    result = model.invoke(messages)
    return result.content.strip()


print(f"Raw question: {raw_question}")
rewritten = rewrite_query(raw_question)
print(f"Rewritten query: {rewritten}\n")

retriever = db.as_retriever(search_kwargs={"k": 1})

print("--- Top result using the RAW question ---")
raw_docs = retriever.invoke(raw_question)
for i, doc in enumerate(raw_docs, 1):
    first_line = doc.page_content.split("\n")[0]
    print(f"  Doc {i}: {first_line}")

print("\n--- Top result using the REWRITTEN query ---")
rewritten_docs = retriever.invoke(rewritten)
for i, doc in enumerate(rewritten_docs, 1):
    first_line = doc.page_content.split("\n")[0]
    print(f"  Doc {i}: {first_line}")
