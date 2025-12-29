# -*- coding: utf-8 -*-
"""
Dana's Brain - State Manager
Session state helpers for Streamlit
"""

import streamlit as st
from datetime import datetime
from typing import Dict, Any, Optional
import uuid


def init_tools_state():
    """Initialize tools in session state (one-time operation)."""
    if 'tools_initialized' not in st.session_state:
        st.session_state.tools_initialized = False
    if 'tools' not in st.session_state:
        st.session_state.tools = None


def get_tools():
    """Get RAG tools from session state."""
    return st.session_state.get('tools', None)


def set_tools(tools: Dict[str, Any]):
    """Store RAG tools in session state."""
    st.session_state.tools = tools
    st.session_state.tools_initialized = True


def create_session_id() -> str:
    """Generate unique session ID for a generation."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"{timestamp}_{unique_id}"


def save_generation_to_history(
    session_id: str,
    product: str,
    persona: str,
    execution_time: float,
    posts_count: int,
    strategy_output: str,
    copy_output: str,
    rag_summary: Dict[str, Any]
):
    """
    Save generation result to session history.

    Args:
        session_id: Unique session identifier
        product: Product name
        persona: Selected persona
        execution_time: Time taken in seconds
        posts_count: Number of posts generated
        strategy_output: Strategy brief
        copy_output: Copywriting output
        rag_summary: RAG usage statistics
    """
    if 'generation_history' not in st.session_state:
        st.session_state.generation_history = []

    generation_record = {
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "product": product,
        "persona": persona,
        "execution_time": execution_time,
        "posts_count": posts_count,
        "strategy_output": strategy_output,
        "copy_output": copy_output,
        "rag_summary": rag_summary
    }

    st.session_state.generation_history.append(generation_record)

    # Keep only last 50 generations in memory
    if len(st.session_state.generation_history) > 50:
        st.session_state.generation_history = st.session_state.generation_history[-50:]


def get_latest_generation() -> Optional[Dict[str, Any]]:
    """Get the most recent generation from history."""
    history = st.session_state.get('generation_history', [])
    return history[-1] if history else None


def clear_current_workflow():
    """Clear current workflow state (for starting a new campaign)."""
    st.session_state.architect_inputs = {
        "product": "",
        "benefits": "",
        "audience": "",
        "offer": "",
        "persona": "Friendly Dana"
    }
    st.session_state.architect_validated = False
    st.session_state.factory_status = "idle"
    st.session_state.factory_progress = []
    st.session_state.factory_result = {}
    st.session_state.rag_queries_log = []


def update_workflow_stage(stage: str):
    """
    Update current workflow stage.

    Args:
        stage: One of: handshake, architects_table, factory_floor, editors_desk
    """
    valid_stages = ["handshake", "architects_table", "factory_floor", "editors_desk"]
    if stage in valid_stages:
        st.session_state.current_workflow_stage = stage
