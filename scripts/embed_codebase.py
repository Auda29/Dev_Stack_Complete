import os
import chromadb
import glob

# Configuration
CHROMA_HOST = os.environ.get("CHROMA_HOST")
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


def connect_to_chroma():
    """
    Attempt to connect to the configured Chroma host; if not provided,
    fall back to common defaults so users do not need to set CHROMA_HOST.
    """
    host_candidates = []
    if CHROMA_HOST:
        host_candidates.append(CHROMA_HOST)
    host_candidates.extend(["chroma", "localhost"])
    # Preserve order while removing duplicates
    seen = set()
    ordered_hosts = []
    for host in host_candidates:
        if host not in seen:
            ordered_hosts.append(host)
            seen.add(host)

    for host in ordered_hosts:
        print(f"Connecting to ChromaDB at {host}:{CHROMA_PORT}...")
        try:
            client = chromadb.HttpClient(host=host, port=int(CHROMA_PORT))
            collection = client.get_or_create_collection(name=COLLECTION_NAME)
            print(f"Collection '{COLLECTION_NAME}' ready (host: {host}).")
            return collection
        except Exception as err:
            print(f"  Connection attempt failed: {err}")

    print("Unable to connect to Chroma. Ensure the service is running (docker compose up -d chroma).")
    return None


def main():
    collection = connect_to_chroma()
    if not collection:
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
