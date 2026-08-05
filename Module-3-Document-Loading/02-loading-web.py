from langchain_community.document_loaders import WebBaseLoader

URL = "https://www.example.com"


def load_web_page(url=URL):
    """Load a single web page with WebBaseLoader"""
    print(f"Fetching {url} ...")
    print("Note: this example needs an internet connection.\n")

    loader = WebBaseLoader(web_path=url)
    documents = loader.load()

    if not documents:
        raise RuntimeError("The loader returned no documents.")

    return documents[0]


def print_document_summary(doc):
    """Print a readable summary of a loaded web page"""
    print("=== Loaded Web Document ===\n")
    print(f"Title: {doc.metadata.get('title', 'N/A')}")
    print(f"Source URL: {doc.metadata.get('source', 'N/A')}")
    print(f"Content length: {len(doc.page_content)} characters")
    print(f"\nContent preview (first 300 characters):\n")
    print(doc.page_content[:300])
    print(f"\nMetadata: {doc.metadata}")


def main():
    """Load example.com with WebBaseLoader and print a summary"""
    print("=== RAG Document Loading Example (Web) ===\n")

    try:
        doc = load_web_page()
        print_document_summary(doc)
    except Exception as e:
        print(f"\nCould not load the web page: {e}")
        print("This usually means you are offline, the site is unreachable, or the")
        print("network is blocking the request. Connect to the internet and try again.")


if __name__ == "__main__":
    main()
