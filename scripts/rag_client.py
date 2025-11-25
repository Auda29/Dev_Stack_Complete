"""
RAG Client for Semantic Code Search

This module provides a dedicated interface to ChromaDB for semantic code search.
Agents use this to find relevant code snippets before making changes.
"""

import os
import chromadb
from typing import List, Dict, Optional


class RAGClient:
    """Client for querying the codebase vector database."""
    
    def __init__(self, 
                 host: Optional[str] = None,
                 port: Optional[int] = None,
                 collection_name: str = "dev_stack_codebase"):
        """
        Initialize RAG client.
        
        Args:
            host: ChromaDB host (defaults to CHROMA_HOST env var or 'chroma')
            port: ChromaDB port (defaults to CHROMA_PORT env var or 8000)
            collection_name: Name of the collection to query
        """
        self.host = host or os.environ.get("CHROMA_HOST", "chroma")
        self.port = int(port or os.environ.get("CHROMA_PORT", "8000"))
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        
    def connect(self):
        """Establish connection to ChromaDB."""
        try:
            self.client = chromadb.HttpClient(host=self.host, port=self.port)
            self.collection = self.client.get_collection(name=self.collection_name)
            return True
        except Exception as e:
            print(f"Warning: Could not connect to ChromaDB at {self.host}:{self.port}")
            print(f"Error: {e}")
            print("RAG features will be disabled. Run: docker compose up -d chroma")
            return False
    
    def query(self, 
              query_text: str, 
              n_results: int = 5,
              filter_metadata: Optional[Dict] = None) -> List[Dict]:
        """
        Query the codebase for relevant code snippets.
        
        Args:
            query_text: Natural language query or code description
            n_results: Number of results to return
            filter_metadata: Optional metadata filters (e.g., {"source": "scripts/"})
            
        Returns:
            List of dictionaries containing:
                - content: The code snippet
                - source: File path
                - chunk_index: Position in file
                - distance: Similarity score (lower is better)
        """
        if not self.collection:
            if not self.connect():
                return []
        
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=filter_metadata
            )
            
            # Format results
            formatted_results = []
            if results and results['documents']:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        'content': results['documents'][0][i],
                        'source': results['metadatas'][0][i].get('source', 'unknown'),
                        'chunk_index': results['metadatas'][0][i].get('chunk_index', 0),
                        'distance': results['distances'][0][i] if results['distances'] else 0
                    })
            
            return formatted_results
            
        except Exception as e:
            print(f"Error querying ChromaDB: {e}")
            return []
    
    def format_for_llm(self, results: List[Dict], max_length: int = 4000) -> str:
        """
        Format search results for inclusion in LLM prompt.
        
        Args:
            results: Results from query()
            max_length: Maximum character length for formatted output
            
        Returns:
            Formatted string with code snippets
        """
        if not results:
            return "No relevant code found in codebase."
        
        formatted = "## Relevant Code from Codebase\n\n"
        current_length = len(formatted)
        
        for i, result in enumerate(results):
            snippet = f"### Source: {result['source']}\n"
            snippet += f"```\n{result['content']}\n```\n\n"
            
            if current_length + len(snippet) > max_length:
                formatted += f"... (truncated {len(results) - i} more results)\n"
                break
            
            formatted += snippet
            current_length += len(snippet)
        
        return formatted
    
    def find_similar_implementations(self, 
                                     description: str, 
                                     n_results: int = 3) -> List[Dict]:
        """
        Find similar code implementations for a given task description.
        
        Args:
            description: Task description or feature requirement
            n_results: Number of similar implementations to find
            
        Returns:
            List of similar code snippets
        """
        return self.query(description, n_results=n_results)
    
    def find_dependencies(self, 
                         file_or_module: str, 
                         n_results: int = 10) -> List[Dict]:
        """
        Find code that imports or uses a specific file/module.
        
        Args:
            file_or_module: Name of file or module to search for
            n_results: Number of results to return
            
        Returns:
            List of code snippets that reference the file/module
        """
        query = f"import {file_or_module} from {file_or_module} {file_or_module}."
        return self.query(query, n_results=n_results)
    
    def search_by_functionality(self, 
                               functionality: str, 
                               file_pattern: Optional[str] = None,
                               n_results: int = 5) -> List[Dict]:
        """
        Search for code implementing specific functionality.
        
        Args:
            functionality: Description of what the code should do
            file_pattern: Optional file pattern to filter (e.g., "*.py")
            n_results: Number of results to return
            
        Returns:
            List of code snippets implementing the functionality
        """
        filter_meta = None
        if file_pattern:
            # This is a simple filter - ChromaDB supports more complex filters
            filter_meta = {"source": {"$contains": file_pattern.replace("*", "")}}
        
        return self.query(functionality, n_results=n_results, filter_metadata=filter_meta)
    
    def get_file_context(self, file_path: str, max_chunks: int = 10) -> List[Dict]:
        """
        Get all indexed chunks for a specific file.
        
        Args:
            file_path: Path to the file
            max_chunks: Maximum number of chunks to return
            
        Returns:
            List of code chunks from the file, in order
        """
        if not self.collection:
            if not self.connect():
                return []
        
        try:
            # Query for all chunks from this file
            results = self.collection.get(
                where={"source": file_path},
                limit=max_chunks
            )
            
            formatted_results = []
            if results and results['documents']:
                for i in range(len(results['documents'])):
                    formatted_results.append({
                        'content': results['documents'][i],
                        'source': results['metadatas'][i].get('source', 'unknown'),
                        'chunk_index': results['metadatas'][i].get('chunk_index', 0)
                    })
            
            # Sort by chunk_index
            formatted_results.sort(key=lambda x: x['chunk_index'])
            return formatted_results
            
        except Exception as e:
            print(f"Error getting file context: {e}")
            return []


# Convenience function for quick queries
def quick_search(query: str, n_results: int = 5) -> List[Dict]:
    """
    Quick one-off search of the codebase.
    
    Args:
        query: Search query
        n_results: Number of results
        
    Returns:
        List of relevant code snippets
    """
    rag = RAGClient()
    return rag.query(query, n_results=n_results)


if __name__ == "__main__":
    # Test the RAG client
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python rag_client.py <search query>")
        sys.exit(1)
    
    query = " ".join(sys.argv[1:])
    print(f"Searching for: {query}\n")
    
    rag = RAGClient()
    results = rag.query(query, n_results=3)
    
    if results:
        print(rag.format_for_llm(results))
    else:
        print("No results found.")
