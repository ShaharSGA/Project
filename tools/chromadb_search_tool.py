# -*- coding: utf-8 -*-
"""
Direct ChromaDB Search Tool - Query existing collections without rebuilding embeddings
"""

from typing import Any, Optional, TYPE_CHECKING
from crewai_tools import BaseTool
import chromadb
from chromadb.config import Settings
from langchain_openai import OpenAIEmbeddings
import time

from config import CHROMADB_DIR, OPENAI_API_KEY, EmbeddingConfig

# Global RAG query log (shared with txt_search_tools)
_rag_query_log = []

# Global embedding cache to avoid redundant API calls
_embedding_cache = {}

if TYPE_CHECKING:
    from chromadb import Collection


def create_chromadb_search_tool(collection_name: str) -> BaseTool:
    """
    Factory function to create a ChromaDB search tool WITHOUT rebuilding embeddings.

    This avoids Pydantic field validation issues by creating the tool dynamically.
    """
    # Initialize ChromaDB client
    client = chromadb.PersistentClient(
        path=str(CHROMADB_DIR),
        settings=Settings(anonymized_telemetry=False)
    )

    # Get existing collection
    collection = client.get_collection(name=collection_name)

    # Initialize OpenAI embeddings
    embeddings = OpenAIEmbeddings(
        model=EmbeddingConfig.MODEL,
        openai_api_key=OPENAI_API_KEY
    )

    class _ChromaDBSearchTool(BaseTool):
        """Search tool for pre-built ChromaDB collection"""
        name: str = f"Search {collection_name}"
        description: str = "Search the knowledge base for relevant information"

        def _run(self, query: str) -> str:
            """Search the collection"""
            # Log query
            global _rag_query_log, _embedding_cache
            _rag_query_log.append({
                'tool': collection_name,
                'query': query,
                'timestamp': time.time()
            })

            # Generate embedding for query (with cache)
            query_lower = query.lower().strip()
            if query_lower in _embedding_cache:
                query_embedding = _embedding_cache[query_lower]
            else:
                query_embedding = embeddings.embed_query(query)
                _embedding_cache[query_lower] = query_embedding

            # Search ChromaDB
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=3
            )

            # Format results
            if not results['documents'] or not results['documents'][0]:
                return "No relevant information found."

            combined_results = "\n\n---\n\n".join(results['documents'][0])
            return f"Relevant Content:\n{combined_results}"

    return _ChromaDBSearchTool()


# Factory functions for each knowledge base
def create_methodology_search_tool() -> BaseTool:
    """Search Dana's methodology without rebuilding embeddings"""
    return create_chromadb_search_tool(EmbeddingConfig.COLLECTIONS["methodology"])


def create_voice_examples_search_tool() -> BaseTool:
    """Search voice examples without rebuilding embeddings"""
    return create_chromadb_search_tool(EmbeddingConfig.COLLECTIONS["voice"])


def create_style_guide_search_tool() -> BaseTool:
    """Search style guide without rebuilding embeddings"""
    return create_chromadb_search_tool(EmbeddingConfig.COLLECTIONS["style"])


def create_platform_specs_search_tool() -> BaseTool:
    """Search platform specifications without rebuilding embeddings"""
    return create_chromadb_search_tool(EmbeddingConfig.COLLECTIONS["platform"])


def create_post_archetypes_search_tool() -> BaseTool:
    """Search post archetypes without rebuilding embeddings"""
    return create_chromadb_search_tool(EmbeddingConfig.COLLECTIONS["archetype"])


def get_chromadb_query_log():
    """
    Get the current RAG query log from ChromaDB tools.

    Returns:
        List of RAG queries with tool names and timestamps
    """
    global _rag_query_log
    return _rag_query_log.copy()


def clear_chromadb_query_log():
    """Clear the ChromaDB RAG query log."""
    global _rag_query_log
    _rag_query_log = []


def clear_embedding_cache():
    """Clear the embedding cache to free memory."""
    global _embedding_cache
    _embedding_cache = {}


def get_cache_stats():
    """Get embedding cache statistics."""
    global _embedding_cache
    return {
        'cached_queries': len(_embedding_cache),
        'memory_saved': len(_embedding_cache) * 0.5  # Rough estimate: 0.5s per API call
    }
