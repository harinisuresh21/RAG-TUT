# Module 1 Summary: Why RAG Exists

> **Module 1** — [Course home](../README.md) · Previous: [08-When not to use RAG](08-When%20not%20to%20use%20RAG.md) · Next: [Module 2: How RAG Works](../Module-2-How-RAG-Works/README.md)

## Recap

In this module, we discovered why Large Language Models (LLMs) are powerful prediction engines but not reliable knowledge databases. They can hallucinate, their knowledge freezes at training time, they cannot see private company data, they are limited by context windows, and they cannot verify sources or produce consistent answers. We saw how these limitations play out in real enterprises — where HR policies, contracts, and compliance reports must be answered accurately. We learned that fine-tuning changes a model's behavior but not its memory, and that Retrieval-Augmented Generation (RAG) solves the knowledge problem by retrieving relevant documents and grounding the model's answer in evidence. Finally, we learned that RAG is not always the answer, and that the simplest architecture that solves the problem is usually the best one.

---

## Core Problems and How RAG Helps

| Core problem | Why it happens | How RAG helps |
|--------------|----------------|---------------|
| Hallucinations | The model predicts the next likely tokens and guesses when knowledge is missing | Retrieval provides evidence, so the model answers from retrieved context instead of guessing |
| Knowledge cutoff | Training is a snapshot, and the world keeps changing after it | RAG retrieves fresh, current documents at query time |
| Private data | Company documents never enter public training data | RAG indexes internal documents and lets the model use them without retraining |
| Context window | A model can only process a limited number of tokens at once | RAG selects only the most relevant chunks instead of sending everything |
| No source verification | LLMs generate text without checking sources | RAG returns answers tied to retrievable, citable sources |
| Inconsistent answers | Generation is probabilistic, so answers vary between runs | Grounded retrieval keeps answers consistent and traceable |

---

## The Employee and Library Mental Model

Think of an LLM as a highly intelligent employee and your company documents as a library.

Without access to the library, the employee answers from memory and often guesses. With RAG, the employee searches the library, reads the relevant pages, and answers with real evidence.

```text
Without RAG:  Employee → Memory → Guess
With RAG:     Employee → Search Library → Read Relevant Pages → Answer
```

**RAG is the library. The LLM is the employee.**

---

## Key Terms Glossary

- **LLM** — Large Language Model, an AI system trained on massive amounts of text to predict the next most likely token.
- **Token** — A unit of text a model reads; it can be a word, part of a word, a symbol, or punctuation.
- **Hallucination** — Confident, plausible-sounding output that is false or unsupported by evidence.
- **Knowledge cutoff** — The point in time after which a model has no inherent knowledge because the information was not in its training data.
- **Context window** — The maximum amount of tokens a model can process in a single interaction.
- **Grounding** — Tying an answer to verifiable evidence rather than to the model's memory.
- **Retrieval** — The step of finding the most relevant documents or chunks for a given question.
- **RAG** — Retrieval-Augmented Generation, the architecture that retrieves relevant information and feeds it to the LLM as context.
- **Fine-tuning** — Additional training that changes a model's behavior, tone, and style — not its stored knowledge.
- **RAG vs fine-tuning** — RAG provides knowledge and memory, while fine-tuning provides skills and behavior; the best systems combine both.

---

## Module 1 Quiz

1. Why is an LLM best described as a prediction engine rather than a knowledge database?
2. What is grounding, and how does RAG achieve it?
3. Why is a standalone LLM unreliable when a company policy changed yesterday?
4. Why is RAG usually better than fine-tuning for private, frequently changing company data?
5. What is the recommended architecture hierarchy when building an AI system?

<details>
<summary>Answers</summary>

1. It predicts the most likely next token from patterns learned during training; it does not retrieve or verify facts.
2. Grounding ties answers to verifiable evidence; RAG achieves it by retrieving relevant documents and providing them as context.
3. The model only knows what existed at training time, so recent changes are invisible to it.
4. Fine-tuning creates a frozen snapshot, while RAG retrieves the latest documents at query time without retraining.
5. Start with prompting, move to fine-tuning if behavior must change, and add RAG only when external knowledge access is needed.
</details>
