import glob
import os
from langchain_community.document_loaders import (
    TextLoader,
    DirectoryLoader,
    PyPDFLoader,
    Docx2txtLoader,
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_PATH = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "docs"))


def load_text_files(docs_path=DOCS_PATH):
    """Load every .txt file from the docs directory with DirectoryLoader"""
    print("Loading .txt files from the docs directory...")

    if not os.path.exists(docs_path):
        raise FileNotFoundError(
            f"The directory {docs_path} does not exist. Please create it and add your documents."
        )

    loader = DirectoryLoader(
        path=docs_path,
        glob="*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )

    documents = loader.load()

    if len(documents) == 0:
        raise FileNotFoundError(
            f"No .txt files found in {docs_path}. Please add your company documents."
        )

    print(f"Found {len(documents)} text document(s).")
    return documents


def load_pdf_files(docs_path=DOCS_PATH):
    """Load every PDF in the docs directory with PyPDFLoader (one Document per page)"""
    print("Looking for PDFs in the docs directory...")
    pdf_files = glob.glob(os.path.join(docs_path, "*.pdf"))

    if not pdf_files:
        print("  No PDF files found. Skipping PDF loading (add a .pdf to docs/ to try it).")
        return []

    documents = []
    for pdf_path in pdf_files:
        try:
            loader = PyPDFLoader(pdf_path)
            pages = loader.load()
            documents.extend(pages)
            print(f"  Loaded {os.path.basename(pdf_path)}: {len(pages)} page(s).")
        except FileNotFoundError:
            print(f"  Warning: could not find {os.path.basename(pdf_path)}. Skipping.")
        except Exception as e:
            print(f"  Warning: could not read {os.path.basename(pdf_path)}: {e}. Skipping.")

    return documents


def load_docx_files(docs_path=DOCS_PATH):
    """Load every .docx file in the docs directory with Docx2txtLoader"""
    print("Looking for Word (.docx) documents in the docs directory...")
    docx_files = glob.glob(os.path.join(docs_path, "*.docx"))

    if not docx_files:
        print("  No .docx files found. Skipping Word loading (add a .docx to docs/ to try it).")
        return []

    documents = []
    for docx_path in docx_files:
        try:
            loader = Docx2txtLoader(docx_path)
            loaded = loader.load()
            documents.extend(loaded)
            print(f"  Loaded {os.path.basename(docx_path)}: {len(loaded)} document(s).")
        except FileNotFoundError:
            print(f"  Warning: could not find {os.path.basename(docx_path)}. Skipping.")
        except Exception as e:
            print(f"  Warning: could not read {os.path.basename(docx_path)}: {e}. Skipping.")

    return documents


def print_document_summary(documents, label="Document", limit=3):
    """Print a readable summary of the first few documents"""
    if not documents:
        return

    shown = min(limit, len(documents))
    print(f"\n--- First {shown} {label}(s) ---")
    for i, doc in enumerate(documents[:shown]):
        print(f"\n{label} {i + 1}:")
        print(f"  Source: {doc.metadata.get('source', 'unknown')}")
        print(f"  Content length: {len(doc.page_content)} characters")
        print(f"  Content preview: {doc.page_content[:80]}...")
        print(f"  Metadata: {doc.metadata}")


def main():
    """Load TXT, PDF, and DOCX sample documents and print a friendly summary"""
    print("=== RAG Document Loading Examples (TXT / PDF / DOCX) ===\n")
    print(f"Looking in the repo's docs folder: {DOCS_PATH}\n")

    text_docs = []
    pdf_docs = []
    docx_docs = []

    try:
        text_docs = load_text_files()
        print_document_summary(text_docs, label="Text document")
    except FileNotFoundError as e:
        print(f"\nError: {e}")

    print("\n" + "-" * 60)
    pdf_docs = load_pdf_files()
    print_document_summary(pdf_docs, label="PDF document")

    print("\n" + "-" * 60)
    docx_docs = load_docx_files()
    print_document_summary(docx_docs, label="Word document")

    total = len(text_docs) + len(pdf_docs) + len(docx_docs)
    print(f"\n=== Done. Loaded {total} document(s) in total. ===")


if __name__ == "__main__":
    main()
