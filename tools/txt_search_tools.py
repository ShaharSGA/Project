# -*- coding: utf-8 -*-
"""
TXTSearchTool initialization for Dana's Brain
Creates separate tools for each knowledge base with ChromaDB storage
"""

from pathlib import Path
from crewai_tools import TXTSearchTool

# Base directory for the project
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "Data"

# Embedding configuration (OpenAI text-embedding-3-small is cost-effective)
EMBEDDING_CONFIG = {
    "provider": "openai",
    "config": {
        "model": "text-embedding-3-small",  # 1536 dimensions, cost-effective
        # OpenAI embeddings handle RTL Hebrew well
    }
}

# ChromaDB configuration
VECTORDB_CONFIG = {
    "provider": "chroma",
    "config": {
        "collection_name": None  # Will be set per tool
    }
}


def create_methodology_tool():
    """
    Tool for Strategy Architect to search Dana's methodology
    """
    collection_config = VECTORDB_CONFIG.copy()
    collection_config["config"]["collection_name"] = "dana_methodology"

    return TXTSearchTool(
        txt=str(DATA_DIR / "Dana_Brain_Methodology.txt"),
        config={
            "llm": {
                "provider": "openai",
                "config": {
                    "model": "gpt-4o-mini",
                    "temperature": 0.3
                }
            },
            "embedder": EMBEDDING_CONFIG,
            "vectordb": collection_config
        }
    )


def create_voice_examples_tool():
    """
    Tool for Dana Copywriter to search voice examples
    """
    collection_config = VECTORDB_CONFIG.copy()
    collection_config["config"]["collection_name"] = "dana_voice_lierac"

    return TXTSearchTool(
        txt=str(DATA_DIR / "Dana_Voice_Examples_Lierac.txt"),
        config={
            "llm": {
                "provider": "openai",
                "config": {
                    "model": "gpt-4o-mini",
                    "temperature": 0.3
                }
            },
            "embedder": EMBEDDING_CONFIG,
            "vectordb": collection_config
        }
    )


def create_style_guide_tool():
    """
    Tool for Dana Copywriter to search style guide
    """
    collection_config = VECTORDB_CONFIG.copy()
    collection_config["config"]["collection_name"] = "style_guide_lierac"

    return TXTSearchTool(
        txt=str(DATA_DIR / "style_guide_customer_Lierac.txt"),
        config={
            "llm": {
                "provider": "openai",
                "config": {
                    "model": "gpt-4o-mini",
                    "temperature": 0.3
                }
            },
            "embedder": EMBEDDING_CONFIG,
            "vectordb": collection_config
        }
    )


def initialize_all_tools():
    """
    Initialize all tools at startup
    Returns dict of tools for easy access
    """
    print("🔧 Initializing TXTSearchTools with ChromaDB...")

    tools = {
        "methodology": create_methodology_tool(),
        "voice_examples": create_voice_examples_tool(),
        "style_guide": create_style_guide_tool()
    }

    print("✅ All TXTSearchTools initialized successfully!")
    return tools
