"""Evaluation Basics — a self-contained, offline demo of retrieval and answer metrics.

This script teaches the core metrics WITHOUT needing an LLM or a vector database:
  - Recall@k:     of all relevant chunks, how many did we retrieve?
  - Precision@k:  of the chunks we retrieved, how many were relevant?
  - Faithfulness: does the answer contradict the evidence? (keyword overlap)

Run it with:
    python "Module-10-Evaluation/01-evaluation-basics.py"
"""

# A tiny pretend "document store": chunk_id -> text
STORE = {
    "chunk_1": "Microsoft was founded by Bill Gates and Paul Allen.",
    "chunk_2": "Microsoft announced it would acquire GitHub for $7.5 billion.",
    "chunk_3": "The GitHub acquisition was completed in October 2018.",
    "chunk_4": "Tesla produces electric vehicles.",
    "chunk_5": "NVIDIA invented the GPU.",
}

# A pretend test set: question -> the chunks that truly answer it (ground truth)
TEST_SET = {
    "How much did Microsoft pay for GitHub?": {"chunk_2", "chunk_3"},
    "Who founded Microsoft?": {"chunk_1"},
    "What does NVIDIA make?": {"chunk_5"},
}

# A pretend retriever: question -> top-k chunk ids it "found"
PRETEND_RETRIEVER = {
    "How much did Microsoft pay for GitHub?": ["chunk_2", "chunk_4", "chunk_3"],
    "Who founded Microsoft?": ["chunk_1", "chunk_5", "chunk_4"],
    "What does NVIDIA make?": ["chunk_5", "chunk_1", "chunk_2"],
}


def recall_at_k(retrieved, relevant):
    """Recall@k = relevant retrieved / total relevant"""
    if not relevant:
        return 0.0
    hits = len(set(retrieved) & relevant)
    return hits / len(relevant)


def precision_at_k(retrieved, relevant):
    """Precision@k = relevant retrieved / total retrieved"""
    if not retrieved:
        return 0.0
    hits = len(set(retrieved) & relevant)
    return hits / len(retrieved)


def is_grounded(answer, evidence):
    """A naive faithfulness check: does the answer only use words from the evidence?

    Real systems use an LLM judge; this keyword-overlap version is just for teaching.
    """
    answer_words = set(answer.lower().split())
    evidence_text = " ".join(STORE[c] for c in evidence).lower()
    suspicious = [w for w in answer_words if w not in evidence_text]
    return len(suspicious) == 0


def main():
    print("=" * 60)
    print("RETRIEVAL METRICS: Recall@k and Precision@k")
    print("=" * 60)

    total_recall = 0.0
    total_precision = 0.0

    for question, relevant in TEST_SET.items():
        retrieved = PRETEND_RETRIEVER[question]
        rec = recall_at_k(retrieved, relevant)
        prec = precision_at_k(retrieved, relevant)
        total_recall += rec
        total_precision += prec

        print(f"\nQuestion: {question}")
        print(f"  Relevant chunks:  {sorted(relevant)}")
        print(f"  Retrieved (k=3):  {retrieved}")
        print(f"  Recall@3:         {rec:.2f}")
        print(f"  Precision@3:      {prec:.2f}")

    n = len(TEST_SET)
    print("\n" + "-" * 60)
    print(f"Average Recall@3:    {total_recall / n:.2f}")
    print(f"Average Precision@3: {total_precision / n:.2f}")

    print("\n" + "=" * 60)
    print("ANSWER METRIC: Faithfulness (grounded vs hallucinated)")
    print("=" * 60)

    # Two answers for the same question: one grounded, one hallucinated
    question = "How much did Microsoft pay for GitHub?"
    relevant = TEST_SET[question]

    grounded_answer = "Microsoft acquired GitHub for $7.5 billion, completed in October 2018."
    hallucinated_answer = "Microsoft acquired GitHub for $1.2 billion, completed in 2021."

    for label, answer in [("Grounded", grounded_answer), ("Hallucinated", hallucinated_answer)]:
        ok = is_grounded(answer, relevant)
        status = "GROUNDED (faithful)" if ok else "NOT GROUNDED (hallucination risk)"
        print(f"\n{label} answer: \"{answer}\"")
        print(f"  -> {status}")


if __name__ == "__main__":
    main()
