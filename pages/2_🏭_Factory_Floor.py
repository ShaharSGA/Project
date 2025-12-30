# -*- coding: utf-8 -*-
"""
Dana's Brain - The Factory Floor
Multi-agent production pipeline for content generation
"""

import streamlit as st
import asyncio
from datetime import datetime

from core.auth import require_authentication
from core.state_manager import update_workflow_stage, save_generation_to_history, create_session_id
from core.crew_executor import execute_crew_async, CrewExecutionResult
from core.file_manager import save_markdown_output
from tools.txt_search_tools import initialize_all_tools
from ui.styles import load_custom_css
from config import AgentConfig

# Page config
st.set_page_config(
    page_title="The Factory Floor - Dana's Brain",
    page_icon="🏭",
    layout="wide"
)

# Load custom styles
load_custom_css()

# Require authentication
require_authentication()


def initialize_tools_if_needed():
    """Initialize RAG tools if not already initialized."""
    if not st.session_state.get('tools_initialized', False):
        with st.spinner("מאתחל כלי RAG (פעם ראשונה - 10-15 שניות)..."):
            try:
                tools = initialize_all_tools()
                st.session_state.tools = tools
                st.session_state.tools_initialized = True
                st.success("✅ כלי RAG מוכנים!")
                return True
            except Exception as e:
                error_msg = str(e)
                st.error(f"❌ שגיאה באתחול כלי RAG: {error_msg}")

                # Check if it's a ChromaDB error
                if "chromadb" in error_msg.lower() or "_type" in error_msg or "vector" in error_msg.lower():
                    st.warning("⚠️ נראה שיש בעיה עם ChromaDB")

                    # Offer automatic fix
                    if st.button("🔧 מחק ChromaDB ונסה שוב", type="primary"):
                        import shutil
                        from pathlib import Path

                        chromadb_dir = Path(".chromadb")
                        if chromadb_dir.exists():
                            try:
                                shutil.rmtree(chromadb_dir)
                                st.success("✅ ChromaDB נמחק! מרענן...")
                                st.rerun()
                            except Exception as del_error:
                                st.error(f"לא הצלחתי למחוק: {del_error}")
                                st.info("אנא הפעל: reset_chromadb.bat")
                        else:
                            st.info("ChromaDB כבר לא קיים")

                st.info("אנא ודאו ש:")
                st.info("1. קבצי Data/ קיימים ונגישים")
                st.info("2. OPENAI_API_KEY מוגדר ב-.env")
                st.info("3. אין בעיות הרשאות עם .chromadb/")
                st.info("4. או הפעל: reset_chromadb.bat")
                return False
    return True


async def run_generation(inputs: dict, tools: dict, progress_placeholder, status_placeholder, rag_log_placeholder):
    """
    Run crew generation with real-time progress updates.

    Args:
        inputs: Campaign inputs
        tools: RAG tools
        progress_placeholder: Streamlit placeholder for progress bar
        status_placeholder: Streamlit placeholder for status messages
        rag_log_placeholder: Streamlit placeholder for RAG query log

    Returns:
        CrewExecutionResult
    """
    from tools.txt_search_tools import get_rag_query_log

    def progress_callback(message: str, progress: float):
        """Update UI with progress."""
        progress_placeholder.progress(progress, text=message)
        status_placeholder.info(message)

    def update_rag_log():
        """Update RAG log display."""
        rag_queries = get_rag_query_log()
        if rag_queries:
            log_text = ""
            for query in rag_queries[-10:]:  # Show last 10 queries
                tool = query.get('tool', 'unknown')
                search = query.get('query', '')[:60]
                log_text += f"**{tool}:** {search}...\n\n"
            rag_log_placeholder.markdown(log_text)
        else:
            rag_log_placeholder.caption("חיפושי RAG יופיעו כאן...")

    # Create a task to periodically update RAG log
    async def poll_rag_log():
        while True:
            update_rag_log()
            await asyncio.sleep(1)  # Update every second

    # Start RAG log polling
    poll_task = asyncio.create_task(poll_rag_log())

    try:
        # Execute crew
        result = await execute_crew_async(inputs, tools, progress_callback)
        return result
    finally:
        # Stop polling
        poll_task.cancel()
        # Final update
        update_rag_log()


def main():
    """The Factory Floor - AI generation pipeline."""

    st.title("🏭 The Factory Floor")
    st.subheader("Multi-Agent Production Pipeline")

    # Check if we have validated inputs
    if not st.session_state.get('architect_validated', False):
        st.warning("⚠️ לא נמצאו נתוני קלט מאומתים")
        st.info("אנא מלא את הטופס ב-Architect's Table תחילה")

        if st.button("← חזרה ל-Architect's Table"):
            st.switch_page("pages/1_📐_Architects_Table.py")
        st.stop()

    # Get inputs
    inputs = st.session_state.architect_inputs

    # Display campaign info
    st.markdown("### 📋 Campaign Overview")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"**מוצר:** {inputs.get('product', 'N/A')}")
    with col2:
        st.info(f"**פרסונה:** {inputs.get('persona', 'N/A')}")
    with col3:
        persona = inputs.get('persona', '')
        temp = AgentConfig.PERSONA_TEMPERATURES.get(persona, 0.7)
        st.info(f"**Temperature:** {temp}")

    st.divider()

    # Initialize tools
    if not initialize_tools_if_needed():
        st.stop()

    # Check if already generated
    if st.session_state.get('factory_status') == 'completed':
        st.success("✅ יצירה הושלמה!")
        st.info("התוכן מוכן לסקירה ב-Editor's Desk")

        # Show summary
        result = st.session_state.get('factory_result', {})
        if result:
            col_a, col_b, col_c, col_d = st.columns(4)
            with col_a:
                st.metric("⏱️ זמן ביצוע", f"{result.get('execution_time', 0):.1f}s")
            with col_b:
                rag_summary = result.get('rag_summary', {})
                total_queries = rag_summary.get('total_queries', 0)
                st.metric("🔍 חיפושי RAG", total_queries)
            with col_c:
                token_usage = result.get('token_usage', {})
                # Handle both dict and UsageMetrics object
                if hasattr(token_usage, 'get'):
                    total_tokens = token_usage.get('total_tokens', 0)
                else:
                    total_tokens = getattr(token_usage, 'total_tokens', 0)
                st.metric("🎯 טוקנים", f"{total_tokens:,}")
            with col_d:
                # Handle both dict and UsageMetrics object
                if hasattr(token_usage, 'get'):
                    total_cost = token_usage.get('total_cost_usd', 0)
                else:
                    total_cost = getattr(token_usage, 'total_cost', 0)
                st.metric("💰 עלות", f"${total_cost:.4f}")

        # Token usage breakdown (expandable)
        if result.get('token_usage'):
            with st.expander("📊 פירוט טוקנים ועלות"):
                token_usage = result['token_usage']

                # Handle both dict and UsageMetrics object
                if hasattr(token_usage, 'get'):
                    # It's a dict
                    breakdown = token_usage.get('cost_breakdown', {})
                    prompt_tokens = token_usage.get('prompt_tokens', 0)
                    completion_tokens = token_usage.get('completion_tokens', 0)
                    total_tokens = token_usage.get('total_tokens', 0)
                    total_cost = token_usage.get('total_cost_usd', 0)
                    prompt_cost = breakdown.get('prompt_cost_usd', 0)
                    completion_cost = breakdown.get('completion_cost_usd', 0)
                else:
                    # It's a UsageMetrics object
                    prompt_tokens = getattr(token_usage, 'prompt_tokens', 0)
                    completion_tokens = getattr(token_usage, 'completion_tokens', 0)
                    total_tokens = getattr(token_usage, 'total_tokens', 0)
                    total_cost = getattr(token_usage, 'total_cost', 0)
                    prompt_cost = getattr(token_usage, 'prompt_cost', 0)
                    completion_cost = getattr(token_usage, 'completion_cost', 0)

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**טוקנים:**")
                    st.write(f"- Input (Prompt): {prompt_tokens:,}")
                    st.write(f"- Output (Completion): {completion_tokens:,}")
                    st.write(f"- **סה\"כ:** {total_tokens:,}")

                with col2:
                    st.markdown("**עלות:**")
                    st.write(f"- Input: ${prompt_cost:.4f}")
                    st.write(f"- Output: ${completion_cost:.4f}")
                    st.write(f"- **סה\"כ:** ${total_cost:.4f}")

                st.caption("💡 מחירים: gpt-4o-mini - $0.150/1M input, $0.600/1M output")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🔄 יצירה חדשה"):
                # Reset everything for a new generation
                st.session_state.factory_status = 'idle'
                st.session_state.architect_validated = False
                st.session_state.factory_result = {}
                st.switch_page("pages/1_📐_Architects_Table.py")

        with col2:
            if st.button("← עריכת פרטים"):
                # Go back to edit inputs AND reset completion status
                # This allows re-running with changed inputs
                st.session_state.factory_status = 'idle'
                st.session_state.factory_result = {}
                st.switch_page("pages/1_📐_Architects_Table.py")

        with col3:
            if st.button("Next: Editor's Desk →"):
                update_workflow_stage("editors_desk")
                st.switch_page("pages/3_✍️_Editors_Desk.py")

        st.stop()

    # Assembly line visualization
    st.markdown("### 🏭 Assembly Line")

    # Step indicators
    steps = [
        {"name": "Strategy Architect", "icon": "🎯", "desc": "מנתח מוצר ומתודולוגיה"},
        {"name": "LinkedIn Content Specialist", "icon": "💼", "desc": "כותב 3 פוסטים ל-LinkedIn"},
        {"name": "Facebook Community Builder", "icon": "👥", "desc": "כותב 3 פוסטים ל-Facebook"},
        {"name": "Instagram Storyteller", "icon": "📸", "desc": "כותב 3 פוסטים ל-Instagram"},
        {"name": "Visual Design", "icon": "🎨", "desc": "בקרוב: הצעות תמונות"},
        {"name": "Funnel Architect", "icon": "📊", "desc": "בקרוב: משפך מכירות"}
    ]

    for i, step in enumerate(steps):
        with st.container():
            col1, col2 = st.columns([1, 4])
            with col1:
                if i < 4:  # Active steps (Strategy + 3 platform copywriters)
                    st.markdown(f"**{i+1}. {step['icon']} {step['name']}**")
                else:  # Future steps
                    st.markdown(f"*{i+1}. {step['icon']} {step['name']}* (Future)")
            with col2:
                if i < 4:
                    st.progress(0, text=step['desc'])
                else:
                    st.progress(0, text=step['desc'])

    st.divider()

    # Start generation button
    if st.button("🚀 Start Generation", type="primary", use_container_width=True):
        st.session_state.factory_status = 'running'
        st.rerun()

    # Generation in progress
    if st.session_state.get('factory_status') == 'running':
        st.info("⏳ יצירת תוכן בתהליך...")

        # Progress indicators
        progress_placeholder = st.empty()
        status_placeholder = st.empty()

        # RAG log
        with st.expander("🔍 RAG Query Log (Real-time)", expanded=True):
            rag_log_placeholder = st.empty()

        # Run generation
        try:
            # Import RAG query log functions
            from tools.txt_search_tools import get_rag_query_log

            # Display initial message
            rag_log_placeholder.caption("חיפושי RAG יופיעו כאן...")
            # Get tools
            tools = st.session_state.tools

            # Run async generation
            result = asyncio.run(run_generation(
                inputs,
                tools,
                progress_placeholder,
                status_placeholder,
                rag_log_placeholder
            ))

            if result.success:
                # Get RAG queries that were used during generation
                rag_queries = get_rag_query_log()

                # Save results
                st.session_state.factory_result = {
                    'strategy_output': result.strategy_output,
                    'copy_output': result.copy_output,
                    'combined_output': result.combined_output,
                    'execution_time': result.execution_time,
                    'rag_summary': result.rag_summary,
                    'token_usage': result.token_usage,
                    'rag_queries_log': rag_queries  # Add RAG queries for Editor's Desk
                }
                st.session_state.factory_status = 'completed'

                # Save to history
                session_id = create_session_id()
                save_generation_to_history(
                    session_id=session_id,
                    product=inputs['product'],
                    persona=inputs['persona'],
                    execution_time=result.execution_time,
                    posts_count=9,
                    strategy_output=result.strategy_output,
                    copy_output=result.copy_output,
                    rag_summary=result.rag_summary
                )

                # Save to file
                persona = inputs['persona']
                temp = AgentConfig.PERSONA_TEMPERATURES.get(persona, 0.7)

                filepath = save_markdown_output(
                    product=inputs['product'],
                    persona=persona,
                    strategy_output=result.strategy_output,
                    copy_output=result.copy_output,
                    execution_time=result.execution_time,
                    rag_summary=result.rag_summary,
                    temperature=temp,
                    inputs=inputs,
                    token_usage=result.token_usage
                )

                st.session_state.last_output_file = filepath

                st.success(f"✅ יצירה הושלמה! ({result.execution_time:.1f}s)")
                st.balloons()
                st.rerun()

            else:
                st.error(f"❌ שגיאה: {result.error}")
                st.session_state.factory_status = 'error'

        except Exception as e:
            st.error(f"❌ שגיאה לא צפויה: {str(e)}")
            st.session_state.factory_status = 'error'


if __name__ == "__main__":
    main()
