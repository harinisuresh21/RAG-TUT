"""Embeddings basics: turn text into vectors and measure semantic similarity.

Embeds a few short HR-style phrases with the local all-MiniLM-L6-v2 model,
then computes cosine similarity between every pair by hand with numpy
(no vector database needed) and prints a similarity matrix.

Run from the repo root:
    python "Module-5-Embeddings/01-embeddings-basics.py"

Requires: langchain-huggingface, sentence-transformers, numpy
Runs fully offline (weights download once on first use).
"""

import numpy as np
from langchain_huggingface import HuggingFaceEmbeddings


def load_embedding_model():
    """Load the all-MiniLM-L6-v2 embedding model with a friendly error message"""
    try:
        print("Loading embedding model all-MiniLM-L6-v2 (first run downloads weights)...")
        embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        print("Embedding model loaded.\n")
        return embedding_model
    except ImportError:
        print(
            "\nERROR: The 'sentence-transformers' package is missing.\n"
            "Install it with:\n"
            "    pip install sentence-transformers\n"
            "(or run: pip install -r requirements.txt)\n"
            "Then run this script again."
        )
        raise
    except Exception as e:
        print(
            f"\nERROR: Could not load the embedding model.\n"
            f"Reason: {e}\n"
            "Make sure 'sentence-transformers' is installed and that you have\n"
            "an internet connection for the one-time weight download."
        )
        raise


def embed_phrases(phrases, embedding_model):
    """Embed every phrase and return the list of vectors"""
    print("Embedding phrases...")
    vectors = embedding_model.embed_documents(phrases)
    for i, phrase in enumerate(phrases):
        print(f"  '{phrase}' -> vector of {len(vectors[i])} dimensions")
    print()
    return vectors


def cosine_similarity(vec_a, vec_b):
    """Compute cosine similarity between two vectors with numpy"""
    a = np.array(vec_a, dtype=float)
    b = np.array(vec_b, dtype=float)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def build_similarity_matrix(vectors):
    """Build a pairwise cosine similarity matrix between all vectors"""
    n = len(vectors)
    matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            matrix[i, j] = cosine_similarity(vectors[i], vectors[j])
    return matrix


def print_similarity_matrix(phrases, matrix):
    """Pretty-print the similarity matrix so clusters are easy to spot"""
    n = len(phrases)
    labels = [phrase[:18] for phrase in phrases]

    print("--- Cosine similarity matrix (1.0 = identical, ~0 = unrelated) ---\n")
    print(f"{'':24}" + "".join(f"{label:>18}" for label in labels))
    for i in range(n):
        row = f"{labels[i]:>24}"
        for j in range(n):
            row += f"{matrix[i, j]:>18.3f}"
        print(row)

    print("\nMost similar pairs (excluding each phrase with itself):")
    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            pairs.append((matrix[i, j], i, j))
    pairs.sort(reverse=True)
    for score, i, j in pairs[:3]:
        print(f"  '{phrases[i]}' <-> '{phrases[j]}': {score:.3f}")


def main():
    """Main demo: embed phrases, compute similarities, print the matrix"""
    print("=== Embeddings Basics: Semantic Similarity Demo ===\n")

    phrases = [
        "employee leave policy",
        "vacation rules",
        "annual leave days",
        "company security policy",
        "how to reset my password",
    ]

    embedding_model = load_embedding_model()
    vectors = embed_phrases(phrases, embedding_model)

    print("=" * 70)
    print("Manual cosine similarity via numpy (no vector database used)")
    print("=" * 70)
    matrix = build_similarity_matrix(vectors)
    print_similarity_matrix(phrases, matrix)

    print("\n" + "=" * 70)
    print("What to notice")
    print("=" * 70)
    print("- The three leave/vacation phrases score highest against each other.")
    print("- 'company security policy' scores low against leave phrases.")
    print("- Cosine similarity measures meaning, not shared keywords.")


if __name__ == "__main__":
    main()
