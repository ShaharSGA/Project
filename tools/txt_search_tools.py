# -*- coding: utf-8 -*-
"""
TXTSearchTool initialization for Dana's Brain
Creates separate tools for each knowledge base with ChromaDB storage

This module handles all RAG tool initialization with proper error handling,
type safety, and configuration management.
"""

from pathlib import Path
from typing import Dict
from crewai_tools import TXTSearchTool

# Import centralized configuration
from config import (
    DataFiles,
    get_embedding_config,
    get_llm_config,
    get_vectordb_config,
    EmbeddingConfig
)
from models import ToolInitError


def create_methodology_tool() -> TXTSearchTool:
    """
    Tool for Strategy Architect to search Dana's methodology.

    Returns:
        TXTSearchTool configured for methodology search

    Raises:
        FileNotFoundError: If methodology file doesn't exist
        UnicodeDecodeError: If file has encoding issues
    """
    file_path = DataFiles.METHODOLOGY

    if not file_path.exists():
        raise FileNotFoundError(f"Missing required file: {file_path}")

    try:
        return TXTSearchTool(
            txt=str(file_path),
            config={
                "llm": get_llm_config(),
                "embedder": get_embedding_config(),
                "vectordb": get_vectordb_config(EmbeddingConfig.COLLECTIONS["methodology"])
            }
        )
    except UnicodeDecodeError as e:
        raise UnicodeDecodeError(
            e.encoding,
            e.object,
            e.start,
            e.end,
            f"File {file_path} must be UTF-8 encoded. Please save it with UTF-8 encoding."
        )


def create_voice_examples_tool() -> TXTSearchTool:
    """
    Tool for Dana Copywriter to search voice examples.

    Returns:
        TXTSearchTool configured for voice examples search

    Raises:
        FileNotFoundError: If voice examples file doesn't exist
    """
    file_path = DataFiles.VOICE_EXAMPLES

    if not file_path.exists():
        raise FileNotFoundError(f"Missing required file: {file_path}")

    return TXTSearchTool(
        txt=str(file_path),
        config={
            "llm": get_llm_config(),
            "embedder": get_embedding_config(),
            "vectordb": get_vectordb_config(EmbeddingConfig.COLLECTIONS["voice"])
        }
    )


def create_style_guide_tool() -> TXTSearchTool:
    """
    Tool for Dana Copywriter to search style guide.

    Returns:
        TXTSearchTool configured for style guide search

    Raises:
        FileNotFoundError: If style guide file doesn't exist
    """
    file_path = DataFiles.STYLE_GUIDE

    if not file_path.exists():
        raise FileNotFoundError(f"Missing required file: {file_path}")

    return TXTSearchTool(
        txt=str(file_path),
        config={
            "llm": get_llm_config(),
            "embedder": get_embedding_config(),
            "vectordb": get_vectordb_config(EmbeddingConfig.COLLECTIONS["style"])
        }
    )


def create_platform_specs_tool() -> TXTSearchTool:
    """
    Tool for Dana Copywriter to search platform specifications
    (LinkedIn, Facebook, Instagram rules).

    Returns:
        TXTSearchTool configured for platform specs search

    Raises:
        FileNotFoundError: If platform specs file doesn't exist
    """
    file_path = DataFiles.PLATFORM_SPECS

    if not file_path.exists():
        raise FileNotFoundError(f"Missing required file: {file_path}")

    return TXTSearchTool(
        txt=str(file_path),
        config={
            "llm": get_llm_config(),
            "embedder": get_embedding_config(),
            "vectordb": get_vectordb_config(EmbeddingConfig.COLLECTIONS["platform"])
        }
    )


def create_post_archetypes_tool() -> TXTSearchTool:
    """
    Tool for Dana Copywriter to search post archetype definitions
    (Heart/Head/Hands framework).

    Returns:
        TXTSearchTool configured for post archetypes search

    Raises:
        FileNotFoundError: If post archetypes file doesn't exist
    """
    file_path = DataFiles.POST_ARCHETYPES

    if not file_path.exists():
        raise FileNotFoundError(f"Missing required file: {file_path}")

    return TXTSearchTool(
        txt=str(file_path),
        config={
            "llm": get_llm_config(),
            "embedder": get_embedding_config(),
            "vectordb": get_vectordb_config(EmbeddingConfig.COLLECTIONS["archetype"])
        }
    )


def initialize_all_tools() -> Dict[str, TXTSearchTool]:
    """
    Initialize all tools at startup with proper error handling.

    Returns:
        Dictionary of initialized TXTSearchTool instances

    Raises:
        FileNotFoundError: If any required data files are missing
        UnicodeDecodeError: If any files have encoding issues
        RuntimeError: If ChromaDB initialization fails
    """
    print("🔧 Initializing TXTSearchTools with ChromaDB...")

    # First, validate all files exist
    missing_files = DataFiles.validate_all_exist()
    if missing_files:
        error = ToolInitError(
            error_type="Missing Data Files",
            message=f"Cannot initialize tools: {len(missing_files)} required file(s) not found",
            missing_files=missing_files,
            suggestion="Please ensure all Data/ files exist and are in the correct location"
        )
        raise FileNotFoundError(error.format_for_user())

    # Initialize tools with specific error handling
    tools = {}
    try:
        tools["methodology"] = create_methodology_tool()
        tools["voice_examples"] = create_voice_examples_tool()
        tools["style_guide"] = create_style_guide_tool()
        tools["platform_specs"] = create_platform_specs_tool()
        tools["post_archetypes"] = create_post_archetypes_tool()

    except FileNotFoundError as e:
        # Specific file missing
        error = ToolInitError(
            error_type="File Not Found",
            message=str(e),
            missing_files=[str(e)],
            suggestion="Check that the file exists in the Data/ directory"
        )
        raise FileNotFoundError(error.format_for_user())

    except UnicodeDecodeError as e:
        # File encoding issue
        error = ToolInitError(
            error_type="File Encoding Error",
            message=f"File encoding issue: {str(e)}",
            missing_files=None,
            suggestion="Save all Data/ files with UTF-8 encoding (not UTF-8 BOM or other encodings)"
        )
        raise UnicodeDecodeError(
            e.encoding, e.object, e.start, e.end,
            error.format_for_user()
        )

    except Exception as e:
        # ChromaDB or other initialization error
        error = ToolInitError(
            error_type="ChromaDB Initialization Failed",
            message=f"Could not initialize vector database: {str(e)}",
            missing_files=None,
            suggestion="Try deleting the .chromadb/ directory and restarting the application"
        )
        raise RuntimeError(error.format_for_user())

    print("✅ All TXTSearchTools initialized successfully!")
    return tools


# RAG Query Logging (for monitoring and debugging)
_rag_query_log = []


def log_rag_query(tool_name: str, query: str):
    """
    Log a RAG query for monitoring purposes.

    Args:
        tool_name: Name of the tool used
        query: Query text
    """
    global _rag_query_log
    _rag_query_log.append({
        'tool': tool_name,
        'query': query,
        'timestamp': str(Path(__file__).stat().st_mtime)  # Simple timestamp
    })


def get_rag_query_log():
    """
    Get the current RAG query log.

    Returns:
        List of RAG queries with tool names and timestamps
    """
    global _rag_query_log
    return _rag_query_log.copy()


def clear_rag_query_log():
    """Clear the RAG query log."""
    global _rag_query_log
    _rag_query_log = []
