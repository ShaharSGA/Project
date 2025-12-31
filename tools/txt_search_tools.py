# -*- coding: utf-8 -*-
"""
RAG Tool initialization for Dana's Brain
Uses pre-built ChromaDB collections for fast performance on Streamlit Cloud

IMPORTANT: This uses ChromaDBSearchTool which queries existing embeddings
instead of rebuilding them. This reduces Streamlit Cloud startup from 15+ minutes to seconds.
"""

from pathlib import Path
from typing import Dict

import streamlit as st

# Use direct ChromaDB search instead of TXTSearchTool to avoid rebuilding embeddings
from crewai_tools import BaseTool
from tools.chromadb_search_tool import (
    create_methodology_search_tool,
    create_voice_examples_search_tool,
    create_style_guide_search_tool,
    create_platform_specs_search_tool,
    create_post_archetypes_search_tool,
    # Use centralized RAG logging from chromadb_search_tool
    get_chromadb_query_log,
    clear_chromadb_query_log
)

from config import DataFiles
from models import ToolInitError


def create_methodology_tool() -> BaseTool:
    """
    Tool for Strategy Architect to search Dana's methodology.
    Uses pre-built ChromaDB - NO embedding regeneration!

    Returns:
        ChromaDB search tool configured for methodology search
    """
    return create_methodology_search_tool()


def create_voice_examples_tool() -> BaseTool:
    """Tool for Dana Copywriter to search voice examples - uses pre-built ChromaDB"""
    return create_voice_examples_search_tool()


def create_style_guide_tool() -> BaseTool:
    """Tool for Dana Copywriter to search style guide - uses pre-built ChromaDB"""
    return create_style_guide_search_tool()


def create_platform_specs_tool() -> BaseTool:
    """Tool for Dana Copywriter to search platform specs - uses pre-built ChromaDB"""
    return create_platform_specs_search_tool()


def create_post_archetypes_tool() -> BaseTool:
    """Tool for Dana Copywriter to search post archetypes - uses pre-built ChromaDB"""
    return create_post_archetypes_search_tool()


@st.cache_resource
def initialize_all_tools() -> Dict[str, BaseTool]:
    """
    Initialize all tools at startup with proper error handling.
    Uses pre-built ChromaDB - NO embedding regeneration!

    Cached with @st.cache_resource to ensure tools are created once
    and reused across all sessions and page navigations.

    Returns:
        Dictionary of initialized ChromaDBSearchTool instances

    Raises:
        RuntimeError: If ChromaDB collections don't exist
    """
    print("🔧 Loading pre-built ChromaDB tools (no embedding regeneration)...")

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

    print("✅ All ChromaDB tools loaded successfully (using pre-built embeddings)!")
    return tools


# RAG Query Logging - Redirect to centralized logging in chromadb_search_tool
# This prevents duplicate logging systems and memory leaks

def get_rag_query_log():
    """
    Get the current RAG query log (redirects to centralized log).

    Returns:
        List of RAG queries with tool names and timestamps
    """
    return get_chromadb_query_log()


def clear_rag_query_log():
    """Clear the RAG query log (redirects to centralized clear)."""
    clear_chromadb_query_log()
