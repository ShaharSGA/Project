"""
Configuration management for Dana's Brain.

This module centralizes all configuration settings to avoid hardcoding values
throughout the codebase. Settings can be overridden via environment variables.
"""

import os
from pathlib import Path
from typing import Literal
import streamlit as st

# Environment detection (Streamlit Cloud vs Local)
def is_streamlit_cloud() -> bool:
    """Detect if running on Streamlit Cloud."""
    return os.getenv("STREAMLIT_RUNTIME_ENV") is not None or hasattr(st, "runtime")

# Base directories
BASE_DIR = Path(__file__).parent

# Cloud-aware paths: use /tmp on Streamlit Cloud, local paths otherwise
if is_streamlit_cloud():
    DATA_DIR = BASE_DIR / "Data"  # Data files are committed to git, so they're accessible
    OUTPUT_DIR = Path("/tmp/outputs")  # Ephemeral storage on cloud
    CHROMADB_DIR = BASE_DIR / ".chromadb"  # Use pre-built ChromaDB from git (committed for performance)
else:
    DATA_DIR = BASE_DIR / "Data"
    OUTPUT_DIR = BASE_DIR / "outputs"
    CHROMADB_DIR = BASE_DIR / ".chromadb"

# Ensure output directories exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CHROMADB_DIR.mkdir(parents=True, exist_ok=True)

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")

# Supabase Configuration (for Streamlit Cloud deployment)
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
USE_SUPABASE = is_streamlit_cloud() and SUPABASE_URL and SUPABASE_KEY

# Agent Configuration
class AgentConfig:
    """Configuration for agent behavior and LLM settings."""

    # Strategy Architect Agent
    STRATEGY_MODEL = os.getenv("STRATEGY_MODEL", "gpt-4o-mini")
    STRATEGY_TEMPERATURE = float(os.getenv("STRATEGY_TEMP", "0.3"))
    STRATEGY_VERBOSE = os.getenv("STRATEGY_VERBOSE", "True").lower() == "true"

    # Dana Copywriter Agent
    COPYWRITER_MODEL = os.getenv("COPYWRITER_MODEL", "gpt-4o-mini")
    COPYWRITER_TEMPERATURE = float(os.getenv("COPYWRITER_TEMP", "0.7"))
    COPYWRITER_VERBOSE = os.getenv("COPYWRITER_VERBOSE", "True").lower() == "true"

    # Persona-specific temperature overrides
    PERSONA_TEMPERATURES = {
        "Professional Dana": 0.4,
        "Friendly Dana": 0.8,
        "Inspirational Dana": 0.7,
        "Mentor Dana": 0.5
    }

    # Agent execution settings
    ALLOW_DELEGATION = False
    MAX_ITERATIONS = 15


# Embedding Configuration
class EmbeddingConfig:
    """Configuration for text embeddings and vector storage."""

    MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    DIMENSIONS = int(os.getenv("EMBEDDING_DIMENSIONS", "1536"))
    PROVIDER = "openai"

    # ChromaDB configuration (using direct chroma provider, not CrewAI RAG)
    CHROMADB_PERSIST_DIR = str(CHROMADB_DIR)

    # Collection names
    COLLECTIONS = {
        "methodology": "dana_methodology",
        "voice": "dana_voice_lierac",
        "style": "style_guide_lierac",
        "platform": "platform_specifications",
        "archetype": "post_archetypes"
    }


# Tool Configuration
class ToolConfig:
    """Configuration for RAG tools and search behavior."""

    # Search tool LLM settings (used for processing search results)
    LLM_PROVIDER = "openai"
    LLM_MODEL = os.getenv("TOOL_LLM_MODEL", "gpt-4o-mini")
    LLM_TEMPERATURE = float(os.getenv("TOOL_LLM_TEMP", "0.3"))

    # Search parameters
    TOP_K_RESULTS = int(os.getenv("SEARCH_TOP_K", "5"))
    MIN_SIMILARITY = float(os.getenv("SEARCH_MIN_SIMILARITY", "0.7"))


# Execution Configuration
class ExecutionConfig:
    """Configuration for crew execution and timeouts."""

    # Timeout settings (in seconds)
    CREW_TIMEOUT = int(os.getenv("CREW_TIMEOUT", "300"))  # 5 minutes (allows time for RAG queries with verbose logging)
    TOOL_INIT_TIMEOUT = int(os.getenv("TOOL_INIT_TIMEOUT", "30"))  # 30 seconds

    # CrewAI process type
    PROCESS_TYPE = "sequential"  # Could be "hierarchical" for parallel

    # Verbose output
    VERBOSE = os.getenv("VERBOSE", "True").lower() == "true"


# Chainlit Configuration
class ChainlitConfig:
    """Configuration for Chainlit UI."""

    PORT = int(os.getenv("CHAINLIT_PORT", "8000"))
    HOST = os.getenv("CHAINLIT_HOST", "localhost")

    # UI messages
    WELCOME_MESSAGE = "chainlit.md"
    ERROR_RETRY_PROMPT = "Would you like to try again with different inputs?"


# Data File Paths
class DataFiles:
    """Paths to all data files in the knowledge base."""

    METHODOLOGY = DATA_DIR / "Dana_Brain_Methodology.txt"
    VOICE_EXAMPLES = DATA_DIR / "Dana_Voice_Examples_Lierac.txt"
    STYLE_GUIDE = DATA_DIR / "style_guide_customer_Lierac.txt"
    PLATFORM_SPECS = DATA_DIR / "platform_specifications.txt"
    POST_ARCHETYPES = DATA_DIR / "post_archetypes.txt"

    @classmethod
    def validate_all_exist(cls) -> list[str]:
        """
        Validate that all required data files exist.

        Returns:
            List of missing file paths (empty if all exist)
        """
        missing = []
        for name, path in cls.__dict__.items():
            if isinstance(path, Path) and not name.startswith('_'):
                if not path.exists():
                    missing.append(str(path))
        return missing


# Persona Configuration
class PersonaConfig:
    """Configuration for different Dana personas."""

    VALID_PERSONAS = [
        "Professional Dana",
        "Friendly Dana",
        "Inspirational Dana",
        "Mentor Dana"
    ]

    # Persona-specific search terms
    PERSONA_SEARCH_TERMS = {
        "Professional Dana": {
            "tone": ["מקצועי", "thought leadership", "אקספרטיזה"],
            "style": ["פורמלי", "עסקי", "מנהיגות מחשבה"]
        },
        "Friendly Dana": {
            "tone": ["חברותי", "היי גורג'ס", "קליל"],
            "style": ["שיחה", "בין חברות", "חם"]
        },
        "Inspirational Dana": {
            "tone": ["השראתי", "מוטיבציה", "העצמה"],
            "style": ["מעורר השראה", "חזון", "שאיפות"]
        },
        "Mentor Dana": {
            "tone": ["מנטורינג", "הדרכה", "חונכות"],
            "style": ["מלמד", "מנחה", "תומך"]
        }
    }


# Logging Configuration
class LoggingConfig:
    """Configuration for logging and debugging."""

    LEVEL = os.getenv("LOG_LEVEL", "INFO")
    FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Log search transparency
    LOG_SEARCHES = os.getenv("LOG_SEARCHES", "True").lower() == "true"
    LOG_TOOL_CALLS = os.getenv("LOG_TOOL_CALLS", "True").lower() == "true"


# Version tracking
class VersionConfig:
    """Version information for the system."""

    VERSION = "1.1.0"
    LAST_UPDATED = "2025-12-17"
    CHANGELOG = """
    v1.1.0 (2025-12-17):
    - Added centralized configuration management
    - Implemented input validation with Pydantic
    - Added thread-safe tool initialization
    - Improved error handling with specific exceptions
    - Added execution timeouts
    - Persona differentiation support
    """


def get_embedding_config() -> dict:
    """
    Get embedding configuration in the format expected by TXTSearchTool.

    Returns:
        Dictionary with embedding configuration
    """
    return {
        "provider": EmbeddingConfig.PROVIDER,
        "config": {
            "model": EmbeddingConfig.MODEL
            # Note: dimensions are auto-detected by the embedding model
        }
    }


def get_llm_config(model: str = None, temperature: float = None) -> dict:
    """
    Get LLM configuration in the format expected by TXTSearchTool.

    Args:
        model: Optional model override
        temperature: Optional temperature override

    Returns:
        Dictionary with LLM configuration
    """
    return {
        "provider": ToolConfig.LLM_PROVIDER,
        "config": {
            "model": model or ToolConfig.LLM_MODEL,
            "temperature": temperature or ToolConfig.LLM_TEMPERATURE
        }
    }


def get_vectordb_config(collection_name: str) -> dict:
    """
    Get vector database configuration in the format expected by TXTSearchTool.

    Args:
        collection_name: Name of the ChromaDB collection

    Returns:
        Dictionary with vector DB configuration
    """
    return {
        "provider": "chroma",  # Use direct ChromaDB, not CrewAI RAG factory
        "config": {
            "collection_name": collection_name,
            "dir": str(CHROMADB_DIR)  # Persist directory for ChromaDB
        }
    }
