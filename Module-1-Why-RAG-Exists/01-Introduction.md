# Module 1: Why RAG Exists

# Introduction

Welcome to the first module of the RAG-TUT course.

Before we learn about embeddings, vector databases, retrieval strategies, chunking techniques, reranking models, or advanced RAG architectures, we must first understand a fundamental question:

> Why does Retrieval-Augmented Generation (RAG) exist?

Many developers immediately jump into building RAG applications without understanding the problem it was designed to solve. As a result, they learn the implementation details but fail to understand the architectural decisions behind modern AI systems.

This module focuses on building that foundation.

---

# What You Will Learn

By the end of this module, you will understand:

- What Large Language Models (LLMs) are
- How LLMs generate responses
- The major limitations of LLMs
- Why hallucinations occur
- Why private company data creates challenges
- Why context windows matter
- Why fine-tuning is not always the answer
- Why Retrieval-Augmented Generation was invented

Most importantly, you will develop the mental model required to understand every other module in this course.

---

# The Evolution of Information Systems

To understand RAG, it helps to understand how information systems evolved.

## Traditional Software

In traditional applications:

```text
User
 ↓
Application
 ↓
Database
 ↓
Result
```

The database returns exact answers. There is no guessing.

---

## Search Engines

Search engines introduced retrieval.

```text
User Query
 ↓
Search Engine
 ↓
Relevant Documents
 ↓
User Reads Results
```

The search engine finds information, but humans must interpret it.

---

## Large Language Models

Modern AI systems introduced LLMs.

```text
Question
 ↓
LLM
 ↓
Generated Answer
```

Instead of returning documents, the system generates a natural language response.

---

# What is a Large Language Model?

A Large Language Model is an AI system trained on massive amounts of text data.

Examples include:

- GPT
- Claude
- Gemini
- Llama
- Mistral
- Qwen

These models learn patterns from billions of documents and can perform a wide range of language tasks.

---

# The Biggest Misconception

Many beginners believe:

```text
LLM = Knowledge Database
```

This is not true.

An LLM is not a database.

Instead:

```text
Input
 ↓
Pattern Matching
 ↓
Probability Calculation
 ↓
Next Token Prediction
 ↓
Response
```

The model predicts the most likely next word based on what it learned during training.

Think of an LLM as a highly advanced prediction engine, not a perfect source of truth.

---

# Why This Matters

Imagine a company called Acme Technologies.

The company has an internal leave policy stating that employees receive 30 annual leave days.

If you ask a generic LLM about this policy, the model has never seen the document.

Any answer it provides is likely a guess.

This is the first clue that something is missing.

---

# The Four Core Challenges

Modern AI systems face four major challenges:

1. Hallucinations
2. Knowledge Cutoffs
3. Private Data
4. Context Limits

These challenges become increasingly severe as AI moves into enterprise production systems.

---

# Real Enterprise Example

Imagine a company with:

- 50,000 PDF documents
- 10,000 contracts
- 5,000 policies
- 2,000 compliance reports

Now a user asks:

```text
What is our customer data retention policy?
```

The answer exists somewhere in the document repository.

But the LLM does not know where.

Without retrieval, the model has no reliable way to locate that information.

This is where RAG enters the picture.

---

# Introducing Retrieval-Augmented Generation

Retrieval-Augmented Generation combines:

```text
Search
+
Knowledge Retrieval
+
Language Models
```

Instead of relying entirely on memory:

```text
Question
 ↓
LLM
 ↓
Answer
```

RAG performs:

```text
Question
 ↓
Retrieve Relevant Information
 ↓
Provide Context
 ↓
LLM Generates Answer
```

The model no longer needs to guess.

It can answer using actual evidence.

---

# The Mental Model

Think of an LLM as a highly intelligent employee.

Without access to documentation:

```text
Employee
 ↓
Memory
 ↓
Answer
```

With access to a company library:

```text
Employee
 ↓
Search Library
 ↓
Read Relevant Pages
 ↓
Answer
```

RAG is the library.

The LLM is the employee.

---

# Why This Course Starts Here

Many RAG tutorials begin with implementation details.

However, before learning chunking, embeddings, vector databases, and retrieval strategies, it is important to understand the problem that RAG was designed to solve.

Once you understand the problem, the architecture becomes much easier to understand.

---

# Summary

In this introduction, we learned:

- LLMs are prediction engines, not databases
- Traditional AI systems face significant limitations
- Private enterprise knowledge creates unique challenges
- Hallucinations and knowledge cutoffs affect reliability
- RAG was created to solve these problems

In the next lesson, we will explore the first major limitation of LLMs: LLM Limitations.
