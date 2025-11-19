import os
import chromadb
import glob

# Configuration
CHROMA_HOST = os.environ.get("CHROMA_HOST", "chroma")
CHROMA_PORT = os.environ.get("CHROMA_PORT", "8000")
COLLECTION_NAME = "dev_stack_codebase"
EXTENSIONS = ["*.py", "*.md", "*.js", "*.ts", "*.html", "*.css", "*.sh", "*.yml", "*.yaml"]
IGNORE_DIRS = [".git", ".worktrees", "node_modules", "__pycache__", ".pytest_cache", "chroma_data"]


def get_files(start_dir="."):
    files = []
    for ext in EXTENSIONS:
        # Recursive search
        for filepath in glob.glob(f"{start_dir}/**/{ext}", recursive=True):
            # Check ignore dirs
            if any(ignored in filepath for ignored in IGNORE_DIRS):
                continue
            files.append(filepath)
    return files


def chunk_text(text, chunk_size=1000, overlap=100):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def main():
    print(f"Connecting to ChromaDB at {CHROMA_HOST}:{CHROMA_PORT}...")

    try:
        client = chromadb.HttpClient(host=CHROMA_HOST, port=int(CHROMA_PORT))
        # Use default embedding function (all-MiniLM-L6-v2 usually)
        collection = client.get_or_create_collection(name=COLLECTION_NAME)
        print(f"Collection '{COLLECTION_NAME}' ready.")
    except Exception as e:
        print(f"Error connecting to ChromaDB: {e}")
        print("Make sure the chroma service is running: docker compose up -d chroma")
        return

    files = get_files()
    print(f"Found {len(files)} files to index.")

    ids = []
    documents = []
    metadatas = []

    for filepath in files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            chunks = chunk_text(content)
            for i, chunk in enumerate(chunks):
                doc_id = f"{filepath}::{i}"
                ids.append(doc_id)
                documents.append(chunk)
                metadatas.append({"source": filepath, "chunk_index": i})

        except Exception as e:
            print(f"Skipping {filepath}: {e}")

    if documents:
        print(f"Upserting {len(documents)} chunks...")
        # Process in batches to avoid hitting limits
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            batch_end = i + batch_size
            collection.upsert(
                ids=ids[i:batch_end],
                documents=documents[i:batch_end],
                metadatas=metadatas[i:batch_end]
            )
            print(f"  Indexed chunks {i} to {min(batch_end, len(documents))}")

        print("Indexing complete!")
    else:
        print("No documents found to index.")


if __name__ == "__main__":
    main()
