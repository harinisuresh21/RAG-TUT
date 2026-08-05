# Grounded Prompting

## Introduction

Retrieval found the evidence; the previous chapter said the prompt must keep the model inside the fence. This chapter shows **exactly how** — by walking through `01-answer-pipeline.py` line by line and explaining every instruction in its prompt.

---

## Learning Objectives

By the end of this chapter, you will:

- Walk through `01-answer-pipeline.py` step by step
- Recreate the grounded prompt pattern from memory
- Explain why each instruction in the prompt exists
- Compare a hallucinated answer with a grounded one

---

## The Pipeline So Far

`01-answer-pipeline.py` reuses everything from Module 7 (load the store, retrieve top-5 chunks), then adds generation:

```python
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

persistent_directory = "db/chroma_db"

# Load embeddings and vector store (same as Module 7)
embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
db = Chroma(
    persist_directory=persistent_directory,
    embedding_function=embedding_model,
    collection_metadata={"hnsw:space": "cosine"}
)

# Search for relevant documents
query = "How much did Microsoft pay to acquire GitHub?"
retriever = db.as_retriever(search_kwargs={"k": 5})
relevant_docs = retriever.invoke(query)
```

The first two-thirds is exactly the Module 7 retrieval pipeline. Generation starts after the chunks are in hand.

---

## The Prompt Pattern

### 1. Combine chunks and question

```python
combined_input = f"""Based on the following documents, please answer this question: {query}

Documents:
{chr(10).join([f"- {doc.page_content}" for doc in relevant_docs])}

Please provide a clear, helpful answer using only the information from these documents. If you can't find the answer in the documents, say "I don't have enough information to answer that question based on the provided documents."
"""
```

`chr(10)` is a newline; the join turns the document list into readable bullet lines. The result is a single text block:

```text
Based on the following documents, please answer this question: How much did Microsoft pay to acquire GitHub?

Documents:
- On June 4, 2018, Microsoft officially announced the acquisition of GitHub for $7.5 billion...
- ...

Please provide a clear, helpful answer using only the information from these documents. If you can't find the answer in the documents, say "I don't have enough information to answer that question based on the provided documents."
```

### 2. Create the model and messages

```python
model = ChatOpenAI(model="gpt-4o")

messages = [
    SystemMessage(content="You are a helpful assistant."),
    HumanMessage(content=combined_input),
]
```

`ChatOpenAI(model="gpt-4o")` is the LLM. The messages follow the chat format: a **system message** setting the assistant's role, and a **human message** containing the full grounded prompt.

### 3. Invoke and print

```python
result = model.invoke(messages)
print(result.content)
```

`result.content` is the model's answer text.

---

## Why Each Instruction Exists

The prompt has three deliberate pieces:

### "Based on the following documents, please answer this question"

Signals the task: the answer is a **derivative of the documents**, not free knowledge.

### The `Documents:` list

Gives the model its **only source of evidence**. Every fact in the answer must come from these lines.

### "Answer using only the information from these documents"

The **constraint**. Without it, the model treats the documents as optional background and falls back to its own training data. With it, the model is told to stay inside the fence.

### "If you can't find the answer... say 'I don't have enough information...'"

The **escape hatch**. It gives the model permission to say "I don't know" instead of inventing something. (Chapter 04 covers this instruction in depth.)

---

## Before / After: Hallucinated vs Grounded

Same question, two prompts — notice what the model does when the constraint is removed:

```text
WEAK prompt:
  "Question: How much did Microsoft pay to acquire GitHub?
   Answer:"

Model output (from training memory):
  "Microsoft acquired GitHub in 2018. While reports varied, the
   acquisition was widely reported as roughly $7.5 billion, which
   analysts valued the deal at."

Close, but hedged and sloppy — and for a question with NO relevant
chunks this model will happily invent a plausible number.
```

```text
GROUNDED prompt (the pattern above):

Model output:
  "According to the documents, Microsoft announced the acquisition of
   GitHub for $7.5 billion, a deal that closed on October 26, 2018."
```

The grounded answer states the number confidently **because the evidence is in the prompt**. The weak answer is vague or invented **because nothing constrained it**. Run `02-grounded-prompt-styles.py` (chapter 04) to see this side by side with a real question.

---

## Enterprise Example

An HR assistant answers *"What is the maternity leave policy?"*. With the grounded pattern, a question whose chunks are all about *paternity* leave produces:

```text
"I don't have enough information to answer that question based on the provided documents."
```

Instead of a confident but fabricated maternity policy.

---

## Key Takeaways

- `01-answer-pipeline.py` = Module 7 retrieval + `ChatOpenAI(model="gpt-4o")` + a structured prompt.
- The grounded prompt = task line + `Documents:` list + "answer only from these" + "say you don't know".
- Each instruction exists to **constrain the model** to the evidence.
- Without the constraint, the model falls back to its training memory — hallucination territory.
- `result.content` is the model's answer text.

---

## Test Yourself

1. What three ingredients make up the grounded prompt in `01-answer-pipeline.py`?
2. What does `chr(10).join(...)` do?
3. Why does the prompt say "using only the information from these documents"?
4. What does the "I don't have enough information..." fallback do for the model?
5. What would likely happen if you removed the constraint sentence from the prompt?

<details>
<summary>Answers</summary>

1. A **task line** ("answer this question"), the **Documents list**, and the **constraints** ("only from these documents" + the "I don't know" fallback).
2. It **joins the document texts into a single string separated by newlines**, so each chunk becomes a bullet line.
3. It is the **constraint** that tells the model its only evidence is the documents — keeping the answer grounded instead of pulling from training data.
4. It gives the model an **escape hatch** — permission to admit a missing answer rather than hallucinate one.
5. The model would treat the documents as optional and fall back to its **training memory**, producing a confident, often hallucinated answer.

</details>

---

## Next Chapter

Next up: [03-Citations-and-Evidence.md](03-Citations-and-Evidence.md) — telling the user *where* an answer came from.
