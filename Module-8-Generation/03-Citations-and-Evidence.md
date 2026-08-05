# Citations and Evidence

## Introduction

A grounded answer is trustworthy; a **cited** answer is verifiable. When an employee reads *"Microsoft paid $7.5 billion for GitHub"*, the natural next question is *"according to what?"*. Citations answer that — by telling the model to name its source.

---

## Learning Objectives

By the end of this chapter, you will:

- Explain why citing sources builds trust
- Add source metadata to the prompt
- Use a prompt pattern that asks the model to quote its source
- Read and produce answers with a "Source: ..." line

---

## Why Citations Build Trust

Enterprise users are accountable for the answers they rely on:

```text
No citation:   "You get 25 leave days."          → why should I trust this?
With citation: "You get 25 leave days. Source: docs/hr/leave-policy.txt"  → I can check it!
```

Citations turn the assistant from a mysterious oracle into an assistant that shows its work. They also make errors **discoverable** — if the cited chunk doesn't actually support the answer, a human can spot it.

---

## Where the Source Comes From

Every retrieved document already carries its source. The Module 6 loader stored it in metadata:

```python
for doc in relevant_docs:
    print(doc.metadata)
# {'source': 'docs/microsoft.txt'}
```

So the evidence about where a chunk came from is already in your hands — you just have to include it in the prompt.

---

## Adding Sources to the Prompt

Instead of sending only `page_content`, send both content and source:

```python
context = chr(10).join(
    f"- {doc.page_content}  (Source: {doc.metadata['source']})"
    for doc in relevant_docs
)

prompt = f"""Based on the following documents, please answer this question: {query}

Documents:
{context}

Use only the information from these documents. When you state a fact, mention which document it came from, like "(Source: docs/microsoft.txt)". If you can't find the answer, say "I don't have enough information to answer that question based on the provided documents."
"""
```

Two changes from the basic pattern:

- Each chunk now carries its **source label**.
- The instructions tell the model to **name the source** when it states a fact.

---

## Prompt Pattern: Quote the Source

You can push further and ask for exact quotes:

```text
Documents:
- <chunk 1>  (Source: docs/microsoft.txt)
- <chunk 2>  (Source: docs/google.txt)

Instructions:
Answer using only these documents.
For every fact, quote the supporting text and name its source, e.g.
"Microsoft acquired GitHub for $7.5 billion (Source: docs/microsoft.txt)."
```

---

## Example Output Format

With the source-aware prompt, the answer to our sample question looks like:

```text
Microsoft announced the acquisition of GitHub for $7.5 billion, a deal
that closed on October 26, 2018.
Source: docs/microsoft.txt
```

Or, with per-fact citations:

```text
Microsoft acquired GitHub for $7.5 billion (Source: docs/microsoft.txt).
```

For HR, a cited answer is even more persuasive:

```text
You receive 25 paid leave days per year.
Source: docs/hr/leave-policy.txt
```

---

## A Worked Snippet

Putting it together, the generation half of the pipeline becomes:

```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

context = chr(10).join(
    f"- {doc.page_content}  (Source: {doc.metadata['source']})"
    for doc in relevant_docs
)

prompt = f"""Based on the following documents, please answer this question: {query}

Documents:
{context}

Use only the information from these documents. When you state a fact,
mention which document it came from, like "(Source: docs/microsoft.txt)".
If you can't find the answer, say you don't have enough information.
"""

messages = [
    SystemMessage(content="You are a helpful assistant."),
    HumanMessage(content=prompt),
]

result = ChatOpenAI(model="gpt-4o").invoke(messages)
print(result.content)
```

---

## Key Takeaways

- Citations make answers **verifiable**, which builds trust.
- The source already lives in **`doc.metadata['source']`**.
- Add the source to each chunk in the prompt, then **instruct the model to name it**.
- "Answer + Source:" output gives users a way to check the assistant's work.
- Citations make hallucinations **discoverable** — a mismatch between answer and source is easy to catch.

---

## Test Yourself

1. Why do citations build trust with enterprise users?
2. Where is the source of a retrieved chunk stored?
3. Write the snippet that appends a source label to each chunk in the prompt.
4. What should the prompt instructions ask the model to do about sources?
5. How do citations help catch hallucinations?

<details>
<summary>Answers</summary>

1. They make answers **verifiable** — users can check the original document instead of trusting the assistant blindly.
2. In the chunk's **`metadata`**, specifically `doc.metadata['source']`.
3.
   ```python
   context = chr(10).join(
       f"- {doc.page_content}  (Source: {doc.metadata['source']})"
       for doc in relevant_docs
   )
   ```
4. It should ask the model to **name the source for each fact it states**, e.g. `(Source: docs/microsoft.txt)`.
5. If the cited source doesn't actually support the answer, the **mismatch is visible** to a human reviewer.

</details>

---

## Next Chapter

Next up: [04-Handling-I-Dont-Know.md](04-Handling-I-Dont-Know.md) — the "say you don't know" instruction and why it is the strongest hallucination defense.
