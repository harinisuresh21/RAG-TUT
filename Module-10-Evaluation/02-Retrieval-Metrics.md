# Retrieval Metrics

## Introduction

Before judging the answer, judge the retrieval.

If the right chunks never reach the LLM, no prompt in the world can save the
answer. Retrieval metrics tell you whether the **right chunks** are being found.

The two most important are:

- **Recall@k** — of all the relevant chunks, how many did we retrieve?
- **Precision@k** — of the chunks we retrieved, how many were actually relevant?

---

## Learning Objectives

By the end of this chapter, you will understand:

- How to decide whether a chunk is "relevant" for a question
- What Recall@k measures
- What Precision@k measures
- How to interpret both together

---

## The Setup

For every question in your test set, you define ground truth:

```text
Question: How much did Microsoft pay for GitHub?

Relevant chunks (in the whole store):
  chunk_3  ("Microsoft announced it would acquire GitHub for $7.5 billion")
  chunk_9  ("The GitHub acquisition was completed in October 2018")
```

The retriever returns its top-k. Suppose with k=3 it returns:

```text
Retrieved: chunk_3, chunk_5, chunk_9
```

---

## Recall@k

Recall@k = relevant chunks retrieved ÷ total relevant chunks.

```text
Relevant retrieved: chunk_3, chunk_9  (2)
Total relevant:     chunk_3, chunk_9  (2)

Recall@3 = 2 / 2 = 1.0
```

Perfect recall. Low recall means the system is **missing** relevant chunks —
a retrieval failure.

---

## Precision@k

Precision@k = relevant chunks retrieved ÷ total chunks retrieved.

```text
Relevant retrieved: chunk_3, chunk_9  (2)
Total retrieved:    chunk_3, chunk_5, chunk_9  (3)

Precision@3 = 2 / 3 ≈ 0.67
```

Low precision means the system is returning **noise** — chunks that do not help.

---

## Reading the Two Together

| Recall | Precision | Diagnosis |
|---|---|---|
| High | High | Healthy retrieval |
| High | Low | Correct chunks found, but too much noise |
| Low | High | Few results, but the ones returned are on-topic |
| Low | Low | Retrieval is fundamentally broken |

---

## How to Build Ground Truth

Ground truth takes effort:

- Manually inspect your documents and note which chunks answer each question.
- Or run a first version and correct the chunks it retrieved.
- For a real project, 20-30 questions with labeled chunks is a solid start.

---

## Key Takeaways

- Retrieval must be measured separately from the final answer.
- Recall@k measures whether the right chunks are found; Precision@k measures whether noise is kept out.
- Read them together to diagnose missing vs noisy retrieval.
- Ground truth chunk labels require manual effort, and that effort is worth it.

---

## Test Yourself

1. What does Recall@k measure?
2. What does Precision@k measure?
3. If the retriever returns only 1 of 4 relevant chunks, what is Recall@4?
4. High recall and low precision together indicate what?
5. True or False: Retrieval metrics tell you whether the final answer is correct.

<details>
<summary>Answers</summary>

1. Of all the relevant chunks, how many were retrieved (within the top k).
2. Of the chunks retrieved, how many were actually relevant.
3. 1/4 = 0.25.
4. The right chunks are found, but retrieval returns too much noise.
5. False. They only measure retrieval; answer correctness is a separate metric.
</details>
