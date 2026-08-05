"""
STEP 1: Document Loading

Goal: pull the raw text out of every file in `docs/` so the rest of the
pipeline can work with it. Nothing is stored on disk in this step — we just
read the files into memory and take a look at what we have.

Run this from the REPO ROOT so the relative path "docs" resolves:
    python "Module-11-Mini-Project/step1_ingest.py"

NOTE ON PDFs: the sample project uses plain .txt files so everyone can follow
along without special libraries. In the real world, most company knowledge
lives in PDFs (HR policies, contracts, handbooks). LangChain has a ready-made
loader for those too:

    from langchain_community.document_loaders import PyPDFLoader
    loader = PyPDFLoader("docs/employee-handbook.pdf")
    pdf_pages = loader.load()

The rest of the pipeline (chunking, embedding, retrieval) is identical —
only the loader changes.
"""

import os
from langchain_community.document_loaders import TextLoader, DirectoryLoader


def load_documents(docs_path="docs"):
    """Load all text files from the docs directory and preview each one."""
    print(f"Loading documents from {docs_path}...")

    if not os.path.exists(docs_path):
        raise FileNotFoundError(
            f"The directory {docs_path} does not exist. "
            "Please create it and add your company files."
        )

    loader = DirectoryLoader(
        path=docs_path,
        glob="*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )

    documents = loader.load()

    if len(documents) == 0:
        raise FileNotFoundError(
            f"No .txt files found in {docs_path}. Please add your company documents."
        )

    print(f"Loaded {len(documents)} document(s).")
    print("=" * 60)

    # Preview EVERY document so you can see exactly what the assistant
    # will have to work with (the course uses a sample of 2; we keep it
    # simple here since the docs folder only holds a few files).
    for i, doc in enumerate(documents, 1):
        print(f"\nDocument {i}:")
        print(f"  Source: {doc.metadata['source']}")
        print(f"  Content length: {len(doc.page_content)} characters")
        print(f"  Content preview: {doc.page_content[:200]}...")
        print(f"  metadata: {doc.metadata}")

    return documents


def main():
    """Run step 1: load the documents."""
    print("=== Step 1: Document Loading ===\n")

    documents = load_documents("docs")

    print(f"\nStep 1 complete! {len(documents)} document(s) are loaded.")
    print("Next: run step2_build_vector_store.py to chunk, embed, and store them.")


if __name__ == "__main__":
    main()
