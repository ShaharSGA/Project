# -*- coding: utf-8 -*-
"""
Dana's Brain - Streamlit Multi-Page App
Main entry point - redirects to The Handshake page
"""

import streamlit as st

# Page config
st.set_page_config(
    page_title="Dana's Brain",
    page_icon="🧠",
    layout="wide"
)

# Redirect to The Handshake page
st.switch_page("pages/0_🤝_Handshake.py")
