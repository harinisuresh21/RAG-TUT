# Module 1: Why RAG Exists
## Understanding the Problem Before the Solution

### Learning Objectives

By the end of this module, learners will be able to:

- Understand the limitations of Large Language Models (LLMs)
- Explain why hallucinations occur
- Understand context window limitations
- Differentiate between Fine-Tuning and RAG
- Identify real-world scenarios where RAG is needed
- Build the mental model required for the rest of the course

---

# Introduction

Before learning Retrieval-Augmented Generation (RAG), it is important to understand why RAG was invented in the first place.

RAG is not a feature.

RAG is a solution to a major limitation of Large Language Models.

To understand RAG, we must first understand where traditional LLMs fail.

---

# What is an LLM?

A Large Language Model (LLM) is an AI system trained on massive amounts of text data.

Examples include:

- GPT
- Claude
- Gemini
- Llama
- Mistral

These models learn patterns from billions of documents and can answer questions, generate code, summarize text, and write content.

## An LLM is NOT a Database

Many beginners assume:

LLM = Search Engine

This is incorrect.

An LLM predicts the next most likely token based on patterns learned during training.

Think of an LLM as a highly advanced prediction engine, not a source of truth.

---

# The First Problem: Hallucinations

A hallucination occurs when an LLM generates information that sounds correct but is actually false.

Example:

User: Who won the IPL in 2035?

LLM: Chennai Super Kings won IPL 2035.

The answer sounds confident, but the event has not happened.

The model fabricated information.

---

# Why Hallucinations Occur

LLMs are optimized to generate the most probable response, not necessarily the most truthful one.

Question
↓
No Actual Knowledge
↓
Pattern Prediction
↓
Fabricated Answer

---

# Knowledge Cutoff Problem

LLMs are trained on data available only until a certain point in time.

Anything occurring after the training period may be unknown.

This results in stale knowledge.

---

# Private Data Problem

Most enterprise knowledge is private:

- Employee Handbooks
- Contracts
- SOPs
- Policies
- Compliance Reports

Private company data is not part of the training dataset.

Therefore, the model cannot answer questions about it accurately.

---

# Context Window Problem

Every LLM has a context window.

Large documents such as 1000-page PDFs cannot fit entirely inside the model context.

This creates limitations when working with enterprise knowledge bases.

---

# Why Not Fine-Tune?

Fine-tuning retrains a model using custom data.

While useful in some situations, it has limitations:

- Expensive
- Requires retraining when data changes
- Not suitable for frequently updated information

---

# Enter RAG

Retrieval-Augmented Generation (RAG) solves these problems.

Instead of storing knowledge inside the model, RAG stores knowledge externally and retrieves relevant information at query time.

Question
↓
Search Documents
↓
Retrieve Relevant Information
↓
Provide Context to LLM
↓
Generate Grounded Answer

---

# Traditional LLM vs RAG

## Traditional LLM

Question
↓
LLM
↓
Answer

Problems:

- Hallucinations
- No private knowledge
- Stale information

## RAG

Question
↓
Retriever
↓
Relevant Documents
↓
LLM
↓
Answer

Benefits:

- Reduced hallucinations
- Access to private data
- Real-time information updates
- Source-grounded answers

---

# Real Business Example

Imagine a company with thousands of documents:

- Policies
- Contracts
- Technical Documentation
- Compliance Reports

Without RAG:

The model guesses.

With RAG:

The system retrieves evidence from company documents and generates answers based on actual information.

---

# When Should You Use RAG?

Use RAG when:

- Knowledge changes frequently
- Documents are private
- Answers require evidence
- Data volume is large
- Real-time updates are required

Examples:

- Enterprise Chatbots
- Customer Support Systems
- Legal Assistants
- Healthcare Assistants
- Compliance Platforms

---

# When NOT to Use RAG

Do not use RAG for:

- Basic arithmetic
- Creative writing
- Generic coding questions
- General world knowledge

Example:

What is Python?

A standard LLM already knows this.

---

# Mental Model

Think of an LLM as a Brain.

Think of RAG as a Brain plus a Library.

Without RAG:

Brain
↓
Memory Only

With RAG:

Brain
↓
Search Library
↓
Read Relevant Information
↓
Answer

---

# Module Summary

In this module, we learned:

- Why LLMs hallucinate
- Knowledge cutoff limitations
- Private data challenges
- Context window constraints
- Fine-Tuning limitations
- Why RAG exists

## Key Takeaway

RAG is not about making models smarter.

RAG is about giving models access to the right information at the right time.

---

# Next Module

## Module 2: How RAG Works

User Query
↓
Embedding
↓
Vector Search
↓
Top-K Retrieval
↓
Context Augmentation
↓
LLM
↓
Final Answer
