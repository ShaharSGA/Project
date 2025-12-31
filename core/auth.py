# -*- coding: utf-8 -*-
"""
Dana's Brain - Authentication Module
Simple password-based authentication for pilot phase
"""

import streamlit as st


def check_password() -> bool:
    """
    Simple password check using Streamlit secrets.

    Returns:
        bool: True if password is correct, False otherwise
    """
    try:
        correct_password = st.secrets.get("app_password", "dana2025")
        return st.session_state.get("password_attempt", "") == correct_password
    except Exception as e:
        st.error(f"Error reading secrets: {e}")
        return False


def authenticate(password: str) -> bool:
    """
    Authenticate user with password.

    Args:
        password: Password attempt

    Returns:
        bool: True if authenticated successfully
    """
    st.session_state.password_attempt = password

    if check_password():
        st.session_state.authenticated = True
        st.session_state.current_workflow_stage = "architects_table"
        return True

    return False


def logout():
    """Log out the current user and clear session state to prevent memory leaks."""
    # Clear large data structures to free memory
    keys_to_clear = [
        'factory_result',
        'generation_history',
        'editor_post_edits',
        'editor_post_feedback',
        'tools',
        'tools_initialized',
        'architect_inputs',
        'factory_status',
        'last_output_file',
        'lab_nudge_dismissed',
    ]

    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

    # Reset auth state
    st.session_state.authenticated = False
    st.session_state.current_workflow_stage = "handshake"
    st.session_state.password_attempt = ""


def require_authentication():
    """
    Decorator/helper to require authentication for a page.
    Redirects to Handshake if not authenticated.
    """
    if not st.session_state.get("authenticated", False):
        st.warning("🔒 Please authenticate first")
        st.info("👈 Navigate to **The Handshake** page to log in")
        st.stop()
