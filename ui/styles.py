# -*- coding: utf-8 -*-
"""
Dana's Brain - Custom CSS Styles
Purple/Magenta dark theme with Hebrew RTL support
"""

import streamlit as st


@st.cache_data(show_spinner=False)
def _get_css_content():
    """Get CSS content (cached to avoid re-rendering)."""
    return """
    <style>
    /* ====================
       GLOBAL STYLES
       ==================== */

    .main {
        background: linear-gradient(135deg, #1E1E2E 0%, #2D2D44 100%);
    }

    /* ====================
       CARD STYLES
       ==================== */

    .card {
        background: #2D2D44;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(155, 77, 202, 0.1);
        border-left: 4px solid #9B4DCA;
    }

    .card:hover {
        box-shadow: 0 6px 12px rgba(155, 77, 202, 0.2);
        transform: translateY(-2px);
        transition: all 0.3s ease;
    }

    /* ====================
       RTL SUPPORT (Hebrew) - ENHANCED
       ==================== */

    /* Global RTL for Hebrew content */
    .main .block-container {
        direction: rtl;
        text-align: right;
    }

    /* Keep LTR for specific elements that need it */
    .stMetric, .stProgress, code, pre, .stCodeBlock {
        direction: ltr;
        text-align: left;
    }

    /* RTL for markdown content */
    .stMarkdown, .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        direction: rtl;
        text-align: right;
        font-family: 'Segoe UI', 'Arial', 'Tahoma', sans-serif;
        line-height: 1.8;
    }

    /* RTL container class */
    .rtl-container {
        direction: rtl;
        text-align: right;
        unicode-bidi: bidi-override;
    }

    .rtl-text {
        font-family: 'Segoe UI', 'Arial', 'Tahoma', sans-serif;
        line-height: 1.8;
        direction: rtl;
        text-align: right;
    }

    /* Force RTL for all text inputs and textareas */
    textarea, input[type="text"], .stTextInput input, .stTextArea textarea {
        direction: rtl;
        text-align: right;
        font-family: 'Segoe UI', 'Arial', 'Tahoma', sans-serif;
        color: #FFFFFF !important;
        background-color: #2D2D44 !important;
    }

    /* RTL for selectbox and dropdown */
    .stSelectbox > div > div {
        direction: rtl;
        text-align: right;
    }

    /* RTL for expanders */
    .streamlit-expanderHeader {
        direction: rtl;
        text-align: right;
    }

    .streamlit-expanderContent {
        direction: rtl;
        text-align: right;
    }

    /* RTL for alerts/info boxes */
    .stAlert > div {
        direction: rtl;
        text-align: right;
    }

    /* Fix column order for RTL (reverse) */
    .stHorizontalBlock {
        flex-direction: row-reverse;
    }

    /* Keep metrics LTR but labels RTL */
    [data-testid="stMetricValue"] {
        direction: ltr;
    }

    [data-testid="stMetricLabel"] {
        direction: rtl;
        text-align: right;
    }

    /* ====================
       BUTTON STYLES
       ==================== */

    .stButton > button {
        background: linear-gradient(90deg, #9B4DCA 0%, #C44DCA 100%);
        color: white !important;
        border: none;
        border-radius: 8px;
        padding: 16px 24px !important;
        font-weight: 600;
        transition: all 0.3s ease;
        min-height: 60px !important;
        height: 60px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        white-space: normal !important;
        line-height: 1.4 !important;
    }

    .stButton > button:hover {
        background: linear-gradient(90deg, #8A3CB9 0%, #B33CB9 100%);
        box-shadow: 0 4px 12px rgba(155, 77, 202, 0.4);
        transform: translateY(-2px);
    }

    .stButton > button:active {
        transform: translateY(0px);
    }

    /* Primary button style */
    .stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #9B4DCA 0%, #C44DCA 100%) !important;
    }

    /* Secondary button style */
    .stButton > button[kind="secondary"] {
        background: linear-gradient(90deg, #6B3D9A 0%, #8B3DAA 100%) !important;
    }

    /* ====================
       PROGRESS INDICATOR
       ==================== */

    .step-indicator {
        display: flex;
        align-items: center;
        margin: 15px 0;
        padding: 10px;
        border-radius: 8px;
        background: #2D2D44;
    }

    .step-indicator.active {
        color: #9B4DCA;
        font-weight: bold;
        border-left: 4px solid #9B4DCA;
    }

    .step-indicator.completed {
        color: #4CAF50;
        border-left: 4px solid #4CAF50;
    }

    .step-indicator.pending {
        color: #666;
        opacity: 0.6;
    }

    /* ====================
       METRIC CARDS
       ==================== */

    .metric-card {
        background: linear-gradient(135deg, #2D2D44 0%, #3D3D54 100%);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        margin: 10px 0;
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #9B4DCA;
        margin: 10px 0;
    }

    .metric-label {
        font-size: 0.9rem;
        color: #B0B0B0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .metric-delta {
        font-size: 0.85rem;
        margin-top: 5px;
    }

    .metric-delta.positive {
        color: #4CAF50;
    }

    .metric-delta.negative {
        color: #F44336;
    }

    /* ====================
       POST CARDS
       ==================== */

    .post-card {
        background: #2D2D44;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        border-left: 4px solid #9B4DCA;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    }

    .post-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
    }

    .platform-badge {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .platform-badge.linkedin {
        background: #0077B5;
        color: white;
    }

    .platform-badge.facebook {
        background: #1877F2;
        color: white;
    }

    .platform-badge.instagram {
        background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%);
        color: white;
    }

    .archetype-badge {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-left: 8px;
    }

    .archetype-badge.Heart {
        background: #E91E63;
        color: white;
    }

    .archetype-badge.Head {
        background: #2196F3;
        color: white;
    }

    .archetype-badge.Hands {
        background: #4CAF50;
        color: white;
    }

    .post-content {
        background: #1E1E2E;
        border-radius: 8px;
        padding: 15px;
        margin: 15px 0;
        line-height: 1.8;
        direction: rtl;
        text-align: right;
        font-family: 'Arial', 'Segoe UI', 'Tahoma', sans-serif;
    }

    /* ====================
       WORKFLOW STATUS
       ==================== */

    .workflow-status {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 15px 20px;
        background: #2D2D44;
        border-radius: 10px;
        margin: 20px 0;
    }

    .workflow-status .stage {
        flex: 1;
        text-align: center;
        padding: 10px;
        border-right: 1px solid #444;
    }

    .workflow-status .stage:last-child {
        border-right: none;
    }

    .workflow-status .stage.active {
        background: rgba(155, 77, 202, 0.2);
        border-radius: 8px;
    }

    .workflow-status .stage.completed {
        opacity: 0.6;
    }

    /* ====================
       SIDEBAR CUSTOMIZATION
       ==================== */

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1E1E2E 0%, #2D2D44 100%);
    }

    [data-testid="stSidebar"] .element-container {
        margin-bottom: 10px;
    }

    /* Sidebar navigation text visibility - FORCE WHITE TEXT */
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }

    [data-testid="stSidebar"] a {
        color: #FFFFFF !important;
        text-decoration: none !important;
    }

    [data-testid="stSidebar"] a:hover {
        color: #9B4DCA !important;
        background-color: rgba(155, 77, 202, 0.1) !important;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #FFFFFF !important;
    }

    /* Navigation items - CRITICAL: Force white text on navigation links */
    [data-testid="stSidebarNav"] {
        color: #FFFFFF !important;
    }

    [data-testid="stSidebarNav"] li {
        color: #FFFFFF !important;
    }

    [data-testid="stSidebarNav"] a {
        color: #FFFFFF !important;
    }

    [data-testid="stSidebarNav"] a span {
        color: #FFFFFF !important;
    }

    [data-testid="stSidebarNav"] [data-testid="stMarkdownContainer"] p {
        color: #FFFFFF !important;
    }

    /* ====================
       TABS CUSTOMIZATION
       ==================== */

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #2D2D44;
        border-radius: 8px;
        padding: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 6px;
        color: #B0B0B0;
        padding: 10px 20px;
        font-weight: 500;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(155, 77, 202, 0.1);
        color: #E0E0E0;
    }

    .stTabs [aria-selected="true"] {
        background-color: #9B4DCA !important;
        color: white !important;
    }

    /* ====================
       EXPANDER CUSTOMIZATION
       ==================== */

    .streamlit-expanderHeader {
        background-color: #2D2D44;
        border-radius: 8px;
        font-weight: 600;
    }

    .streamlit-expanderHeader:hover {
        background-color: rgba(155, 77, 202, 0.1);
    }

    /* ====================
       ALERTS & INFO BOXES
       ==================== */

    .stAlert {
        border-radius: 8px;
        border-left-width: 4px;
    }

    /* ====================
       SCROLLBAR CUSTOMIZATION
       ==================== */

    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }

    ::-webkit-scrollbar-track {
        background: #1E1E2E;
    }

    ::-webkit-scrollbar-thumb {
        background: #9B4DCA;
        border-radius: 5px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #8A3CB9;
    }

    /* ====================
       ANIMATIONS
       ==================== */

    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .fade-in {
        animation: fadeIn 0.3s ease-in;
    }

    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.5;
        }
    }

    .pulse {
        animation: pulse 2s infinite;
    }

    /* ====================
       UTILITY CLASSES
       ==================== */

    .text-center {
        text-align: center;
    }

    .text-right {
        text-align: right;
    }

    .text-purple {
        color: #9B4DCA;
    }

    .text-success {
        color: #4CAF50;
    }

    .text-error {
        color: #F44336;
    }

    .text-warning {
        color: #FF9800;
    }

    .mt-1 { margin-top: 10px; }
    .mt-2 { margin-top: 20px; }
    .mt-3 { margin-top: 30px; }

    .mb-1 { margin-bottom: 10px; }
    .mb-2 { margin-bottom: 20px; }
    .mb-3 { margin-bottom: 30px; }

    .p-1 { padding: 10px; }
    .p-2 { padding: 20px; }
    .p-3 { padding: 30px; }

    </style>
    """
    return css_content


def load_custom_css():
    """Load custom CSS for purple/magenta theme and RTL support (cached for performance)."""
    css_content = _get_css_content()
    st.markdown(css_content, unsafe_allow_html=True)


def rtl_text(text: str, tag="p", class_name="rtl-text"):
    """
    Display Hebrew text with RTL directionality.

    Args:
        text: The Hebrew text to display
        tag: HTML tag to use (p, div, span, etc.)
        class_name: CSS class name
    """
    st.markdown(
        f'<{tag} class="{class_name}" dir="rtl">{text}</{tag}>',
        unsafe_allow_html=True
    )


def metric_card(title: str, value: str, delta: str = None, delta_color: str = "positive"):
    """
    Display a custom metric card with purple theme.

    Args:
        title: Metric label
        value: Metric value (as string for formatting)
        delta: Optional delta/change indicator
        delta_color: "positive" or "negative"
    """
    delta_html = ""
    if delta:
        delta_class = f"metric-delta {delta_color}"
        delta_html = f'<div class="{delta_class}">{delta}</div>'

    st.markdown(f"""
    <div class="metric-card fade-in">
        <div class="metric-label">{title}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def platform_badge(platform: str):
    """Display a platform badge (LinkedIn, Facebook, Instagram)."""
    platform_lower = platform.lower()
    st.markdown(
        f'<span class="platform-badge {platform_lower}">{platform}</span>',
        unsafe_allow_html=True
    )


def archetype_badge(archetype: str):
    """Display an archetype badge (Heart, Head, Hands)."""
    st.markdown(
        f'<span class="archetype-badge {archetype}">{archetype}</span>',
        unsafe_allow_html=True
    )
