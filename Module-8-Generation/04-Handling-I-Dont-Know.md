# Handling "I Don't Know"

## Introduction

The single most dangerous behavior of an LLM is **confidently wrong answers**. When a model doesn't know something, it doesn't say "I don't know" — it *generates* something plausible. The antidote is a prompt instruction that makes "I don't know" the safe, expected output.

---

## Learning Objectives

By the end of this chapter, you will:

- Explain why the "say you don't know" instruction matters
- Describe what happens without it (confident hallucinations)
- Use the other safety patterns: answer only from context, no assumptions, ask follow-up

---

## The Confident Hallucination Problem

LLMs are trained to complete text, not to be honest about gaps in knowledge. Given a question their context doesn't cover, they produce a fluent guess:

```text
Question:  "What is the company's bereavement leave policy?"
Context:   (nothing about bereavement leave — only vacation policy)

Model without instruction:
  "Employees receive 5 days of bereavement leave, which can be extended
   for immediate family members."

← confident, specific, and completely fabricated
```

The answer sounds authoritative. A user who can't check will believe it. This is the failure mode RAG is meant to prevent — and the prompt is where you prevent it.

---

## The "I Don't Know" Instruction

One sentence in the prompt changes the behavior:

```text
"If you can't find the answer in the documents, say 'I don't have enough
information to answer that question based on the provided documents.'"
```

Now the model has an **explicit, safe alternative** to guessing. The same question produces:

```text
"I don't have enough information to answer that question based on the provided documents."
```

The instruction matters for three reasons:

1. It **removes the pressure to answer** — the model no longer needs to fill every gap.
2. It gives the model **exact wording** — instead of improvising a refusal, it quotes the fallback.
3. It is **testable** — you can verify the behavior in evaluation (Module 10).

---

## Why Without It, It Guesses

Models weigh what they generate toward what sounds plausible. Without an explicit instruction, "answer the question" means "produce an answer". The escape hatch is what makes honesty possible:

```text
With escape hatch:      uncertainty → "I don't have enough information..."
Without escape hatch:   uncertainty → the most plausible-sounding guess
```

---

## Other Safety Patterns

The "I don't know" fallback works best alongside a small set of reinforcing rules:

### Answer only from context

```text
"Answer using ONLY the information provided in the documents."
```

Closes the door on training-data knowledge.

### No assumptions

```text
"Do not assume facts that are not stated in the documents."
```

Blocks the "standard practice" style guesses.

### Ask a follow-up

```text
"If the question is unclear or lacks information, ask for clarification
instead of guessing."
```

Turns a weak query into a dialogue instead of a hallucination.

A combined safety prompt:

```text
You are an assistant that answers ONLY from the provided documents.
- Use only the information in the documents.
- Do not assume facts not stated in the documents.
- If you cannot answer from the documents, reply exactly:
  "I don't have enough information to answer that question based on the provided documents."
- If the question is unclear, ask a clarifying question.
```

---

## Short Example

```text
Question: "How many vacation days do contractors get?"
Context:   (contractor policy not in the documents)

Answer (grounded prompt):
"I don't have enough information to answer that question based on the
provided documents. The documents cover employee leave but do not
mention contractor vacation days."
```

The model declines *and* explains why — far more useful than a fabricated policy.

---

## Enterprise Example

In a legal assistant, the cost of a confident hallucination is a wrong contract clause repeated in a negotiation. The "I don't know" instruction means the assistant returns zero invented clauses — and the prompt-style comparison in `02-grounded-prompt-styles.py` demonstrates exactly this behavior change.

---

## Key Takeaways

- Without an instruction, LLMs **confidently fabricate** when context is missing.
- The "I don't know" fallback gives the model a **safe, explicit alternative**.
- Pair it with **"answer only from context"** and **"no assumptions"**.
- For unclear queries, **ask a follow-up** instead of guessing.
- This behavior is **testable** — evaluation (Module 10) checks whether the assistant refuses when it should.

---

## Test Yourself

1. What does an LLM tend to do when it lacks the information to answer?
2. Why does giving the model exact fallback wording matter?
3. Name two other safety patterns besides "say you don't know".
4. What happens to the answer if you remove the escape hatch?
5. Why is a refusal that explains *why* better than a plain "I don't know"?

<details>
<summary>Answers</summary>

1. It **generates a plausible guess** — a confident, fluent hallucination.
2. Exact wording makes the behavior **consistent and testable**, and the model doesn't have to improvise a refusal.
3. **"Answer only from the documents"** and **"do not assume facts not stated"** (also: ask a clarifying follow-up).
4. The model fills the gap with **training-data guesswork**, producing a confident but unsupported answer.
5. It tells the user **what's missing**, so they can rephrase the question or add documents — a plain "I don't know" leaves them stuck.

</details>

---

## Next Chapter

Next up: [05-Chat-History-and-Context.md](05-Chat-History-and-Context.md) — turning the assistant into a conversation partner.
