# -*- coding: utf-8 -*-
"""
Dana's Brain - The Handshake
Entry point: Authentication & project selection
"""

import streamlit as st
from core.auth import authenticate
from ui.styles import load_custom_css

# Page config
st.set_page_config(
    page_title="The Handshake - Dana's Brain",
    page_icon="🤝",
    layout="wide"
)

# Load custom styles
load_custom_css()


def main():
    """The Handshake - Authentication screen."""

    # Full width layout
    st.markdown("<div class='fade-in'>", unsafe_allow_html=True)

    # Hero section - full width
    st.title("🧠 Dana's Brain")
    st.subheader("Autonomous Marketing AI System")

    st.divider()

    # Check if already authenticated
    if st.session_state.get("authenticated", False):
        st.success("✅ Already authenticated!")

        # Client selector in a container - wider layout
        st.markdown("### 📁 בחר לקוח / Select Client")

        col1, col2 = st.columns([1, 3])
        with col1:
            client_options = ["Lierac"]  # Future: load from Data/Clients/
            selected_client = st.radio(
                "לקוח פעיל / Active Client:",
                options=client_options,
                index=0,
                help="Future: support for multiple clients"
            )
            st.session_state.selected_client = selected_client

        with col2:
            st.info(f"**Project:** {st.session_state.get('selected_client', 'Lierac')}")
            st.info("You're ready to start creating marketing content.")

        st.divider()

        # Navigation buttons - equal width with spacing
        st.markdown("### 🚀 Quick Actions")
        col_nav1, col_nav2, col_nav3, col_nav4 = st.columns([2, 2, 2, 1])

        with col_nav1:
            if st.button("📐 Go to Architect's Table", type="primary", use_container_width=True, key="nav_architect"):
                st.session_state.current_workflow_stage = "architects_table"
                st.switch_page("pages/1_📐_Architects_Table.py")

        with col_nav2:
            if st.button("📚 Feedback Guide", type="secondary", use_container_width=True, key="nav_guide"):
                st.switch_page("pages/5_📚_Feedback_Guide.py")

        with col_nav3:
            if st.button("🔄 Logout", use_container_width=True, key="nav_logout"):
                from core.auth import logout
                logout()
                st.rerun()

        # Empty column for spacing
        with col_nav4:
            pass

        st.divider()

        # Quick Links in two columns for better layout
        col_links1, col_links2 = st.columns(2)

        with col_links1:
            st.markdown("""
            ### 📖 Quick Links
            - **📐 Architect's Table** - תכנן קמפיין חדש
            - **🏭 Factory Floor** - ייצר תוכן
            - **✍️ Editor's Desk** - סקור ותן פידבק
            """)

        with col_links2:
            st.markdown("""
            ###
            - **⚗️ Refinement Lab** - שפר פידבקים
            - **📚 Feedback Guide** - למד על מערכת הפידבק
            """)

    else:
        # Authentication form - centered for better UX
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.markdown("### 🔐 Enter Access Code")

            with st.form("auth_form"):
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your access code",
                    help="Default password: dana2025"
                )

                submit = st.form_submit_button("Enter", use_container_width=True)

                if submit:
                    if password:
                        if authenticate(password):
                            st.success("✅ Authentication successful!")
                            st.info("Redirecting to Architect's Table...")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("❌ Incorrect password. Please try again.")
                    else:
                        st.warning("Please enter a password")

            st.divider()

            # Help section
            with st.expander("ℹ️ About This System"):
                st.markdown("""
                **Dana's Brain** is an autonomous AI system that generates Hebrew marketing content in Dana's unique writing style.

                ### Five-Screen Workflow:

                1. **🤝 The Handshake** (Current) - Authentication & access
                2. **📐 The Architect's Table** - Strategic planning & inputs
                3. **🏭 The Factory Floor** - AI content generation
                4. **✍️ The Editor's Desk** - Review, refine, & learn
                5. **⚗️ Refinement Lab** - Improve feedback quality
                6. **📚 Feedback Guide** - Learn about the feedback system

                ### How It Works:

                - Enter product information and select a persona
                - AI agents analyze and generate 9 social media posts (LinkedIn, Facebook, Instagram)
                - Review content, provide feedback to improve future outputs
                - System learns from your preferences over time

                ### Technical Note:

                This Streamlit interface runs in parallel with the existing Chainlit app.
                Both share the same backend and knowledge base.
                """)

            st.caption("v1.0.0 - The Handshake")

        # Initialize default client (before authentication)
        if 'selected_client' not in st.session_state:
            st.session_state.selected_client = "Lierac"

    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
