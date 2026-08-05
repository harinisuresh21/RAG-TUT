# Character vs Recursive Splitting

## Introduction

There are many ways to cut text into chunks, but two splitters do the vast majority of the work in real RAG systems:

- **`CharacterTextSplitter`** — cuts by raw character count.
- **`RecursiveCharacterTextSplitter`** — cuts at natural boundaries (paragraphs, sentences, words) first.

This chapter explains the difference, then walks through the exact example in the module's starter script [01-recursive-vs-character-splitter.py](01-recursive-vs-character-splitter.py) so you can see it in action.

---

## Learning Objectives

By the end of this chapter, you will understand:

- How `CharacterTextSplitter` works and where it fails
- How `RecursiveCharacterTextSplitter` picks its split points
- The recursive separators list: `["\n\n", "\n", ". ", " ", ""]`
- Exactly what the starter script demonstrates, and why

---

## CharacterTextSplitter: Fixed Size, Single Separator

`CharacterTextSplitter` counts characters and cuts at regular intervals. It has one separator, applied everywhere.

```python
from langchain.text_splitter import CharacterTextSplitter

splitter = CharacterTextSplitter(
    separator=" ",      # only split on this one separator
    chunk_size=100,     # target chunk length in characters
    chunk_overlap=0,
)

chunks = splitter.split_text("Some long company policy text ...")
```

Because the splitter only understands one separator and a character count, it has two classic failure modes:

```text
1. It can cut mid-word (when the separator appears nowhere near the 100-char mark
   and it has to fall back to a raw character break).

2. It ignores structure — a sentence or paragraph boundary means nothing to it.
```

It works fine for simple, uniform text. On real documents it produces ugly cuts.

---

## RecursiveCharacterTextSplitter: Try Boundaries in Order

`RecursiveCharacterTextSplitter` is the same idea with one crucial upgrade: instead of one separator, it has a **list of separators**, tried in order.

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", ". ", " ", ""],   # paragraphs → lines → sentences → words → anywhere
    chunk_size=100,
    chunk_overlap=0,
)
```

The recursion works like this:

```text
Try to split on "\n\n" (paragraph breaks)
  → if the pieces are still too big, split those on "\n" (line breaks)
    → if still too big, split on ". " (sentence breaks)
      → if still too big, split on " " (word breaks)
        → only as a last resort, split anywhere (the "" fallback)
```

The splitter respects **natural boundaries** as much as possible, and only destroys them when the text leaves no other choice.

```mermaid
flowchart TD

A[Text too big?] --> B{Split on "\n\n"?}

B -->|paragraphs still too big| C{Split on "\n"?}

C -->|still too big| D{Split on ". "?}

D -->|still too big| E{Split on " "?}

E -->|still too big| F[Split on "" anywhere]
```

That is why it is the **default choice** in most RAG frameworks: it keeps paragraphs and sentences intact, which keeps meaning intact.

---

## Walking Through the Starter Script

The script [01-recursive-vs-character-splitter.py](01-recursive-vs-character-splitter.py) builds one test document and shows both splitters against it. Here is the document:

```python
tesla_text = """Tesla's Q3 Results

Tesla reported record revenue of $25.2B in Q3 2024.

Model Y Performance

The Model Y became the best-selling vehicle globally, with 350,000 units sold.

Production Challenges

Supply chain issues caused a 12% increase in production costs.

This is one very long paragraph that definitely exceeds our 100 character limit and has no double newlines inside it whatsoever making it impossible to split properly."""
```

The key feature of this text: **every short section is separated by a blank line, but the last paragraph is one very long sentence with no paragraph breaks at all.** It's exactly the kind of text that separates good splitters from bad ones.

### The CharacterTextSplitter version (commented out)

The script includes a `CharacterTextSplitter` setup with `separator=" "` and `chunk_size=100` — but it is **commented out**, because it shows the failure mode:

```python
# splitter1 = CharacterTextSplitter(
#     separator=" ",  # Default separator. Other options include ["\n\n", "\n", ". ", " ", ""]
#     chunk_size=100,
#     chunk_overlap=0
# )
```

If you uncomment it and run it, you would see chunks that look like this shape — roughly 100 characters each, cut purely at spaces:

```text
Chunk 1: (100 chars) "Tesla's Q3 Results Tesla reported record revenue of $25.2B in Q3 2024. Model Y"
Chunk 2: (100 chars) "Performance The Model Y became the best-selling vehicle globally, with 350,000 units"
...
```

The separator is only ever `" "`, so the splitter **ignores paragraphs and sentences entirely**. The "Model Y Performance" heading is welded onto the revenue sentence; the "Production Challenges" heading is stuck to the previous sentence. Meaning is jumbled even though no word is technically cut in half.

### The RecursiveCharacterTextSplitter version (active)

```python
recursive_splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", ". ", " ", ""],  # Multiple separators
    chunk_size=100,
    chunk_overlap=0
)

chunks2 = recursive_splitter.split_text(tesla_text)
```

Running it produces a very different shape:

```text
2. RECURSIVE CHARACTER TEXT SPLITTER SOLUTION
Same problem text, but with RecursiveCharacterTextSplitter:
Chunk 1: (…) "Tesla's Q3 Results"
Chunk 2: (…) "Tesla reported record revenue of $25.2B in Q3 2024."
Chunk 3: (…) "Model Y Performance"
Chunk 4: (…) "The Model Y became the best-selling vehicle globally, with 350,000 units sold."
Chunk 5: (…) "Production Challenges"
Chunk 6: (…) "Supply chain issues caused a 12% increase in production costs."
Chunk 7: (…) "This is one very long paragraph ... split properly."
```

### What the output shape tells you

Notice what happened:

1. **Paragraphs stayed intact.** Each section (Revenue, Model Y, Production) became its own chunk, because the splitter found `"\n\n"` breaks first.
2. **The long final paragraph was handled in stages.** It has no `\n\n` and no `\n`, so the splitter fell through to `". "`. Its single sentence is still too long for `chunk_size=100`, so it had to fall back to spaces — but only for that paragraph, not for the whole document.
3. **Each chunk is now one coherent idea**, which is exactly what a good embedding needs.

The contrast is the whole point of the script: **with a single separator you weld unrelated ideas together; with recursive separators you keep ideas separate and only split within them when you must.**

---

## When to Use Which

| Splitter | Use it when | Watch out |
|---|---|---|
| `CharacterTextSplitter` | Simple, uniform text; quick experiments; fixed-size chunks on purpose | Ignores paragraphs/sentences — welds unrelated ideas |
| `RecursiveCharacterTextSplitter` | Almost everything else — this is the default for a reason | Still counts characters, so it can break inside a sentence when text has no natural separators |

For real documents (policies, manuals, contracts), start with `RecursiveCharacterTextSplitter`. It is not perfect, but it respects the structure your authors actually used.

---

## Key Takeaways

- `CharacterTextSplitter` cuts on a **single separator** by character count — it can weld unrelated sentences together.
- `RecursiveCharacterTextSplitter` tries separators **in order**: `["\n\n", "\n", ". ", " ", ""]`.
- The recursive splitter keeps paragraphs and sentences intact **as much as possible**, only splitting within them as a last resort.
- The starter script shows both behaviors: the character splitter (if uncommented) welds headings to sentences; the recursive splitter produces one coherent idea per chunk.
- For real documents, **start with `RecursiveCharacterTextSplitter`**.

---

## Test Yourself

1. What separators does the recursive splitter try, in order?
2. What happens when the recursive splitter finds a `"\n\n"` break?
3. In the starter script, why did the final long paragraph still get split, even by the recursive splitter?
4. Why was the `CharacterTextSplitter` version in the script commented out?
5. Which splitter would you use as a first choice for an employee handbook, and why?

<details>
<summary>Answers</summary>

1. `["\n\n", "\n", ". ", " ", ""]` — paragraph breaks, line breaks, sentence breaks, word breaks, then anywhere as a last resort.
2. It splits there **first**, so paragraphs stay intact as long as they fit the chunk size.
3. Because that paragraph has **no `\n\n`, no `\n`, and only one `.`** — after `. ` the sentence is still over `chunk_size=100`, so the splitter fell back to spaces (and then `""`).
4. To show the failure mode: with only `separator=" "`, it welds the heading "Model Y Performance" onto the previous sentence and ignores paragraph structure.
5. `RecursiveCharacterTextSplitter` — because it respects paragraph and sentence boundaries, keeping each chunk a coherent idea that embeds well.

</details>

---

## Next Chapter

Next up: [03-Chunk-Size-and-Overlap.md](03-Chunk-Size-and-Overlap.md) — the two tuning knobs that turn any splitter into the right chunking strategy for your data.
