# Chat History and Context

## Introduction

So far the assistant answers each question from scratch. But users ask follow-ups: *"How much did Microsoft pay for GitHub?"* → *"And when did that deal close?"* The second question is meaningless without the first. This chapter introduces **conversational RAG**: passing conversation history alongside the retrieved context so the model can answer follow-ups coherently.

---

## Learning Objectives

By the end of this chapter, you will:

- Explain why single-turn retrieval fails on follow-up questions
- Pass chat history into the model alongside retrieved context
- Distinguish single-turn from multi-turn RAG
- Know where to go for the full treatment (Module 9)

---

## The Follow-Up Problem

In a single-turn system every query is treated as a fresh question:

```text
User:  "How much did Microsoft pay for GitHub?"   →  "7.5 billion dollars."
User:  "And when did that deal close?"            →  "Which deal?"  ✗
```

The second question has no context. The retrieved chunks for *"when did that deal close"* don't obviously point at GitHub, and the model doesn't remember the first exchange. The fix: **hand the conversation to the model**, not just the latest question.

---

## Messages List with History

The `ChatOpenAI` model already speaks "messages". Instead of one question, give it the full conversation — plus the retrieved context:

```python
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

history = [
    HumanMessage(content="How much did Microsoft pay for GitHub?"),
    AIMessage(content="Microsoft acquired GitHub for $7.5 billion."),
]

retrieved_context = ...  # top-k chunks for the CURRENT question

combined_input = f"""Based on the following documents, please answer this question: {query}

Documents:
{chr(10).join([f"- {doc.page_content}" for doc in relevant_docs])}

Use only the information from these documents. If you can't find the answer, say "I don't have enough information to answer that question based on the provided documents."
"""

messages = [
    SystemMessage(content="You are a helpful assistant."),
    *history,
    HumanMessage(content=combined_input),
]

result = ChatOpenAI(model="gpt-4o").invoke(messages)
print(result.content)
```

Key detail: **history goes into `messages`**, and the **retrieved context stays with the current question**. The model sees the past conversation (to understand "that deal") *and* the fresh evidence (to answer correctly).

---

## Single-Turn vs Multi-Turn RAG

```text
SINGLE-TURN RAG (so far in this course)
  query → retrieve → prompt → answer
  each question is independent; follow-ups lose context

MULTI-TURN / CONVERSATIONAL RAG
  history + query → retrieve → prompt with history → answer
  the model understands references like "that deal"
```

Two honest notes:

1. **What to retrieve** gets harder in multi-turn — should you embed the latest question alone, or the whole conversation? (Module 9 covers rewriting the question to include context.)
2. **Prompt length** grows with history, so real systems keep a rolling window of recent turns.

For this course, the core idea is simple: **add the history to the messages**. Retrieval strategies for history are the Module 9 deep dive.

---

## Enterprise Example

```text
User:   "What's our remote work policy?"
Bot:    "Full-time employees may work remotely up to 3 days per week."
User:   "Can I do it more often?"
Bot:    "The policy allows more than 3 days only with manager approval."
```

The second answer only makes sense because the model saw both the first exchange and the relevant chunks. That is conversational RAG.

---

## Key Takeaways

- Follow-ups need **conversation history**, not just the latest question.
- Add history to the `messages` list; keep retrieved context with the current question.
- **Single-turn**: query → retrieve → answer. **Multi-turn**: history + query → retrieve → answer.
- Retrieval for follow-ups is harder than generation — Module 9 handles it.
- Keep a rolling window so history doesn't blow up the prompt.

---

## Test Yourself

1. Why does single-turn RAG fail on the follow-up "And when did that deal close?"
2. Where does chat history go in the messages list?
3. Where does the retrieved context go?
4. What is one challenge multi-turn RAG creates for retrieval?
5. How do real systems keep prompts from growing forever?

<details>
<summary>Answers</summary>

1. The second question has **no context** — "that deal" references a previous exchange the model never saw, and retrieval alone can't fill the gap.
2. History goes **into the `messages` list** between the system message and the current human message (as `HumanMessage`/`AIMessage` pairs).
3. It stays **with the current question**, in the prompt (the `combined_input`) — the model answers from fresh evidence.
4. Deciding **what to embed and retrieve** — the raw follow-up may not contain enough information; Module 9 covers rewriting the question.
5. By keeping a **rolling window** of recent turns instead of the entire transcript.

</details>
