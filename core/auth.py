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
    """Log out the current user."""
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
