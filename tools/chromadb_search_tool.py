# -*- coding: utf-8 -*-
"""
Direct ChromaDB Search Tool - Query existing collections without rebuilding embeddings
"""

from typing import Any, Optional, TYPE_CHECKING
from crewai_tools import BaseTool
import chromadb
from chromadb.config import Settings
from langchain_openai import OpenAIEmbeddings

from config import CHROMADB_DIR, OPENAI_API_KEY, EmbeddingConfig

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
            # Generate embedding for query
            query_embedding = embeddings.embed_query(query)

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
