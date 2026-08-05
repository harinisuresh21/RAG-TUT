# Answer Metrics

## Introduction

Retrieval delivered the right chunks. Now the hard part: did the LLM produce a
good answer from them?

Two qualities matter most:

- **Faithfulness (groundedness)** — is the answer supported by the retrieved context?
- **Relevance** — does the answer actually address the question?

An answer can fail on either one.

---

## Learning Objectives

By the end of this chapter, you will understand:

- The difference between faithful and hallucinated answers
- The difference between relevance and faithfulness
- Why exact-match grading does not work for LLM answers
- How LLM-as-judge scoring works

---

## Faithfulness

A faithful answer only makes claims that can be found in the retrieved context.

```text
Question: What is the annual leave policy?

Retrieved context:
  "Employees receive 30 annual leave days.
   Unused leave may be carried forward."

Faithful answer:
  "Employees get 30 annual leave days, and unused leave can be carried forward."

Unfaithful (hallucinated) answer:
  "Employees get 45 annual leave days, and unused leave expires."
```

The unfaithful answer sounds confident but contradicts the evidence.

---

## Relevance

A relevant answer addresses the user's question.

```text
Question: How do I request leave?

Irrelevant (but faithful) answer:
  "Employees receive 30 annual leave days."

Relevant answer:
  "Submit the request in the HR portal; your manager must approve it."
```

The first answer is true to the context but does not answer the question.

---

## Why Exact Matching Fails

LLMs rarely answer identically twice:

```text
"30 days"            vs  "Thirty days"
"carried forward"    vs  "can be carried over"
```

Both are correct, but string comparison scores them as wrong. So simple
exact-match grading is useless for LLM answers.

---

## LLM-as-Judge

The practical approach: use an LLM to grade the answer against the context.

```text
Context: [retrieved chunks]
Question: ...
Answer: ...

Does the answer contradict the context? Respond YES or NO and explain.
```

The grading LLM checks for contradictions (faithfulness) and whether the
question is addressed (relevance). It can also return a score like 0-5.

---

## Key Takeaways

- Faithfulness: does the answer match the retrieved evidence?
- Relevance: does the answer address the question?
- Exact matching cannot grade natural-language answers.
- An LLM judge is the pragmatic way to score answer quality at scale.

---

## Test Yourself

1. What does faithfulness measure?
2. Give an example of an answer that is faithful but irrelevant.
3. Why is exact-match grading unsuitable for LLM answers?
4. What is "LLM-as-judge"?
5. True or False: A faithful answer can still fail to help the user.

<details>
<summary>Answers</summary>

1. Whether the answer's claims are supported by the retrieved context.
2. A question about how to request leave answered with the number of leave days.
3. Because correct answers can be phrased in unlimited ways.
4. Using an LLM to score another answer's faithfulness and relevance against the context.
5. True. It can be grounded but still not answer the user's actual question.
</details>
