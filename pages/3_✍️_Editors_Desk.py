# -*- coding: utf-8 -*-
"""
Dana's Brain - The Editor's Desk
Quality control and content review workspace
"""

import streamlit as st
from pathlib import Path

from core.auth import require_authentication
from core.content_parser import parse_generated_content, get_posts_by_platform, get_post_emoji, get_archetype_description
from ui.styles import load_custom_css

# Page config
st.set_page_config(
    page_title="The Editor's Desk - Dana's Brain",
    page_icon="✍️",
    layout="wide"
)

# Load custom styles
load_custom_css()

# Require authentication
require_authentication()


def display_post_card(post, post_id: str):
    """Display a single post as a card with actions."""

    # Get or initialize edit state
    if 'editor_post_edits' not in st.session_state:
        st.session_state.editor_post_edits = {}

    is_editing = st.session_state.get(f'editing_{post_id}', False)

    # Card container with improved styling
    st.markdown("""
    <div style="background: linear-gradient(135deg, #2D2D44 0%, #1E1E2E 100%);
                border-left: 4px solid #9B4DCA;
                border-radius: 12px;
                padding: 24px;
                margin-bottom: 24px;
                box-shadow: 0 4px 6px rgba(155, 77, 202, 0.1);">
    """, unsafe_allow_html=True)

    with st.container():
        # Header
        col_h1, col_h2, col_h3 = st.columns([3, 1, 2])

        with col_h1:
            emoji = get_post_emoji(post.archetype)
            st.markdown(f"**{emoji} {post.platform} • Post #{post.number} • {post.archetype}**")

        with col_h2:
            # Calculate current word count (updates in real-time if editing)
            if is_editing:
                current_content = st.session_state.editor_post_edits.get(post_id, post.content)
                current_word_count = len(current_content.split())
            else:
                current_word_count = post.word_count
            st.caption(f"📊 {current_word_count} מילים")

        with col_h3:
            st.caption(get_archetype_description(post.archetype))

        st.divider()

        # Content (editable or display)
        if is_editing:
            # Edit mode - callback updates session state on every change
            def update_edit_content():
                """Update session state when text changes."""
                st.session_state.editor_post_edits[post_id] = st.session_state[f"edit_area_{post_id}"]

            edited_content = st.text_area(
                "ערוך תוכן:",
                value=st.session_state.editor_post_edits.get(post_id, post.content),
                height=200,
                key=f"edit_area_{post_id}",
                on_change=update_edit_content
            )

            # Show live word count while editing
            live_word_count = len(edited_content.split())

            # Platform-specific word count limits
            platform_limits = {
                "LinkedIn": (150, 250),
                "Facebook": (120, 180),
                "Instagram": (50, 80)
            }

            min_words, max_words = platform_limits.get(post.platform, (0, 999))

            # Show status with color coding
            if live_word_count < min_words:
                st.warning(f"⚠️ מילים כרגע: **{live_word_count}** (מומלץ: {min_words}-{max_words})")
            elif live_word_count > max_words:
                st.error(f"🔴 מילים כרגע: **{live_word_count}** (מומלץ: {min_words}-{max_words})")
            else:
                st.success(f"✅ מילים כרגע: **{live_word_count}** (מומלץ: {min_words}-{max_words})")

            col_save, col_cancel = st.columns(2)

            with col_save:
                if st.button("💾 שמור", key=f"save_{post_id}", use_container_width=True):
                    st.session_state.editor_post_edits[post_id] = edited_content
                    st.session_state[f'editing_{post_id}'] = False
                    st.rerun()

            with col_cancel:
                if st.button("❌ ביטול", key=f"cancel_{post_id}", use_container_width=True):
                    st.session_state[f'editing_{post_id}'] = False
                    st.rerun()

        else:
            # Display mode
            display_content = st.session_state.editor_post_edits.get(post_id, post.content)

            # Display with RTL support
            st.markdown(f'<div class="rtl-text" style="background: #2D2D44; padding: 15px; border-radius: 8px; white-space: pre-wrap;">{display_content}</div>', unsafe_allow_html=True)

            st.divider()

            # Action buttons
            btn_col1, btn_col2 = st.columns(2)

            with btn_col1:
                if st.button("✏️ ערוך", key=f"edit_btn_{post_id}", use_container_width=True, type="secondary"):
                    st.session_state[f'editing_{post_id}'] = True
                    st.rerun()

            with btn_col2:
                if st.button("📋 העתק", key=f"copy_{post_id}", use_container_width=True, type="secondary"):
                    st.code(display_content, language=None)
                    st.success("✅ מוכן להעתקה!")

            # Enhanced feedback system (always visible)
            st.markdown("---")
            col_header, col_help = st.columns([3, 1])

            with col_header:
                st.markdown("#### 📊 דרג ושתף משוב / Rate & Provide Feedback")
                st.caption("💾 **זה מה שנשמר במערכת ומשפיע על הלמידה** - דירוג + קטגוריה + משוב בכתב")

            with col_help:
                if st.button("📚 מדריך פידבק", key=f"guide_btn_{post_id}", type="secondary", use_container_width=True):
                    st.switch_page("pages/5_📚_Feedback_Guide.py")

            col_rating, col_category = st.columns([1, 2])

            with col_rating:
                rating = st.select_slider(
                    "דירוג / Rating:",
                    options=[1, 2, 3, 4, 5],
                    value=3,
                    key=f"rating_slider_{post_id}",
                    help="1 = לא מתאים, 5 = מעולה"
                )

            with col_category:
                category = st.selectbox(
                    "קטגוריה / Category:",
                    options=[
                        "Tone",
                        "Length",
                        "Words",
                        "Structure",
                        "Platform_Fit",
                        "Strategic Miss / DNA Mismatch",  # NEW: Critical category
                        "Other"
                    ],
                    index=0,
                    key=f"category_select_{post_id}",
                    help="בחר את ההיבט המרכזי של המשוב. 'Strategic Miss' = אי-התאמה בסיסית לשיטת דנה או DNA של הלקוח"
                )

            feedback_text = st.text_area(
                "משוב ספציפי (אופציונלי) / Specific Feedback:",
                placeholder="למשל: 'הפתיחה רשמית מדי' או 'שימוש מצוין במילה \"מעבדה\"'",
                key=f"feedback_text_{post_id}",
                height=80,
                help="משוב ספציפי יותר = ציון אמינות גבוה יותר"
            )

            if st.button("💾 שלח משוב / Submit Feedback", key=f"submit_feedback_{post_id}", type="primary", use_container_width=True):
                try:
                    # Import feedback modules
                    from core.confidence_calculator import calculate_confidence, get_confidence_explanation
                    from core.feedback_manager import get_recent_feedback, save_feedback, sanitize_feedback
                    from core.feedback_triage import evaluate_feedback_quality, get_toast_message

                    # Get context
                    client_id = st.session_state.get('selected_client', 'Lierac')
                    persona = st.session_state.get('architect_inputs', {}).get('persona', 'Unknown')

                    # Map platform to correct agent_type (for new architecture)
                    platform_to_agent_type = {
                        'LinkedIn': 'linkedin_copywriter',
                        'Facebook': 'facebook_copywriter',
                        'Instagram': 'instagram_copywriter'
                    }
                    agent_type = platform_to_agent_type.get(post.platform, 'copywriter')  # Fallback to old type

                    # Get RAG queries from generation
                    rag_queries = st.session_state.get('factory_result', {}).get('rag_queries_log', [])
                    if isinstance(rag_queries, dict):
                        rag_queries = list(rag_queries.keys())

                    # Get historical data for consistency scoring (use correct agent_type)
                    historical = get_recent_feedback(
                        client_id=client_id,
                        agent_type=agent_type,  # Use platform-specific agent type
                        days=30
                    )

                    # Prepare feedback data for confidence calculation
                    feedback_data = {
                        'rating': rating,
                        'category': category,
                        'raw_text_feedback': feedback_text,
                        'persona': persona,
                        'platform': post.platform
                    }

                    # Calculate confidence
                    confidence = calculate_confidence(feedback_data, historical)

                    # === NEW: Triage Logic ===
                    # Determine routing: APPROVED or PENDING_REFINEMENT
                    triage_result = evaluate_feedback_quality(
                        score=rating,
                        text=feedback_text,
                        category=category
                    )

                    # Extract triage results
                    feedback_status = triage_result['status']
                    actionability_score = triage_result['actionability_score']
                    lab_entry_date = triage_result.get('lab_entry_date')

                    # Sanitize feedback text
                    sanitized_text = sanitize_feedback(feedback_text)

                    # Generate unique post_id (session + platform + archetype)
                    session_id = st.session_state.get('session_id', 'unknown')
                    unique_post_id = f"{session_id}_{post.platform}_{post.archetype}_{post.number}"

                    # Normalize status to lowercase for database consistency
                    # (save_feedback will also normalize, but doing it here for clarity)
                    normalized_status = feedback_status.lower() if feedback_status else None

                    # Save to database with triage results
                    feedback_id = save_feedback(
                        post_id=unique_post_id,
                        content=post.content[:200],  # First 200 chars as preview
                        rating=rating,
                        category=category,
                        raw_text_feedback=sanitized_text,
                        client_id=client_id,
                        agent_type=agent_type,  # Use platform-specific agent type (linkedin_copywriter, etc.)
                        persona=persona,
                        platform=post.platform,
                        archetype=post.archetype,
                        rag_queries_used=rag_queries[:10] if rag_queries else [],  # Limit to 10
                        metadata={
                            'session_id': session_id,
                            'generation_time': st.session_state.get('factory_result', {}).get('execution_time', 0),
                            'word_count': post.word_count
                        },
                        confidence_score=confidence,
                        # Refinement Lab fields
                        refinement_data=None,  # Will be filled in Lab
                        lab_entry_date=lab_entry_date,
                        actionability_score=actionability_score,
                        status=normalized_status  # CRITICAL: Use triage-determined status (normalized to lowercase)
                    )

                    # Show smart toast message based on triage status
                    toast = get_toast_message(feedback_status)

                    if feedback_status == 'APPROVED':
                        st.success(f"{toast['icon']} {toast['title']}\n\n{toast['message']}\n\n(ציון actionability: {actionability_score:.2f})")
                    elif feedback_status == 'PENDING_REFINEMENT':
                        st.info(f"{toast['icon']} {toast['title']}\n\n{toast['message']}\n\n(ציון actionability: {actionability_score:.2f})")

                    # Show detailed explanation in expander
                    with st.expander("🔍 מידע נוסף על ציון האמינות"):
                        from core.confidence_calculator import calc_context_score, calc_consistency_score, calc_specificity_score

                        context_score = calc_context_score(feedback_data)
                        consistency_score = calc_consistency_score(feedback_data, historical)
                        specificity_score = calc_specificity_score(feedback_data)

                        explanation = get_confidence_explanation(context_score, consistency_score, specificity_score)
                        st.text(explanation)

                        st.caption(f"Feedback ID: {feedback_id}")

                except Exception as e:
                    st.error(f"❌ שגיאה בשמירת משוב: {str(e)}")
                    st.caption("המערכת תמשיך לעבוד גם ללא משוב")

    # Close the card div
    st.markdown("</div>", unsafe_allow_html=True)


def show_lab_nudge():
    """Show smart nudge to refine lab items"""
    from core.feedback_manager import get_lab_queue
    import random

    client_id = st.session_state.get('selected_client', 'Lierac')

    try:
        # Check if there are items in the lab
        queue = get_lab_queue(client_id=client_id, limit=5)

        if queue and not st.session_state.get('lab_nudge_dismissed', False):
            # Pick random item to show
            random_item = random.choice(queue)

            # Show nudge in info box
            st.info(f"""
            **💡 יש לך 2 דקות?**

            יש {len(queue)} פידבקים במעבדת השיפור שממתינים לליטוש.

            **דוגמה:**
            - קטגוריה: {random_item.get('category')}
            - ציון: {random_item.get('rating')}⭐
            - משוב: "{random_item.get('raw_text_feedback', '(ריק)')[:50]}..."

            שיפור פידבק אחד לוקח ~30 שניות ועוזר למערכת ללמוד!
            """)

            col_n1, col_n2 = st.columns(2)

            with col_n1:
                if st.button("⚗️ בוא נשפר!", key="nudge_goto_lab", type="primary"):
                    st.switch_page("pages/4_⚗️_Refinement_Lab.py")

            with col_n2:
                if st.button("✖️ אחר כך", key="nudge_dismiss"):
                    st.session_state.lab_nudge_dismissed = True
                    st.rerun()

            st.divider()

    except Exception as e:
        # Silently fail if lab query doesn't work
        pass


def main():
    """The Editor's Desk - Quality control workspace."""

    st.title("✍️ The Editor's Desk")
    st.subheader("Quality Control & Continuous Learning")

    # === SMART NUDGING ===
    # Show lab nudge if there are pending items
    show_lab_nudge()

    # Check if we have results to review
    if not st.session_state.get('factory_status') == 'completed':
        st.warning("⚠️ אין תוכן לסקירה")
        st.info("אנא צור תוכן ב-Factory Floor תחילה")

        if st.button("← חזרה ל-Factory Floor"):
            st.switch_page("pages/2_🏭_Factory_Floor.py")
        st.stop()

    # Get results
    result = st.session_state.get('factory_result', {})
    inputs = st.session_state.get('architect_inputs', {})

    # Session header
    st.markdown("### 📋 Session Overview")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.info(f"**מוצר:** {inputs.get('product', 'N/A')}")
    with col2:
        st.info(f"**פרסונה:** {inputs.get('persona', 'N/A')}")
    with col3:
        exec_time = result.get('execution_time', 0)
        st.info(f"**זמן:** {exec_time:.1f}s")
    with col4:
        rag_summary = result.get('rag_summary', {})
        total_queries = rag_summary.get('total_queries', 0)
        st.info(f"**RAG:** {total_queries} חיפושים")

    st.divider()

    # Parse content
    metadata = {
        'product': inputs.get('product'),
        'persona': inputs.get('persona'),
        'execution_time': result.get('execution_time'),
        'rag_summary': result.get('rag_summary')
    }

    # Debug: Show what we're parsing
    combined_output = result.get('combined_output', '')

    if not combined_output:
        # Try alternative outputs
        combined_output = result.get('copy_output', '') or result.get('strategy_output', '')

    # Parse content FIRST (before debug info)
    parsed_content = parse_generated_content(
        combined_output,
        metadata
    )

    # Show debug info in expander
    with st.expander("🐛 Debug Info (למפתחים)", expanded=False):
        # Source info
        st.markdown("**📊 Output Sources:**")
        st.caption(f"- Combined output: {len(combined_output)} chars")
        st.caption(f"- Copy output: {len(result.get('copy_output', ''))} chars")
        st.caption(f"- Strategy output: {len(result.get('strategy_output', ''))} chars")

        st.divider()

        # Content detection
        st.markdown("**🔍 Content Detection:**")
        st.caption("✅ Has strategy section: " + str('🎯 תקציר אסטרטגי' in combined_output or 'תקציר אסטרטגי' in combined_output))
        st.caption("✅ Has posts section: " + str('✍️ פוסטים למדיה חברתית' in combined_output or '# תוכן סופי' in combined_output))
        st.caption("✅ Has LINKEDIN: " + str('סדרת LINKEDIN' in combined_output or 'LINKEDIN' in combined_output))
        st.caption("✅ Has FACEBOOK: " + str('סדרת FACEBOOK' in combined_output or 'FACEBOOK' in combined_output))
        st.caption("✅ Has INSTAGRAM: " + str('סדרת INSTAGRAM' in combined_output or 'INSTAGRAM' in combined_output))

        st.divider()

        # Parser results
        st.markdown("**🎯 Parser Results:**")
        st.caption(f"Strategy extracted: {len(parsed_content.strategy_output)} chars")
        st.caption(f"Total posts parsed: {len(parsed_content.posts)}")
        if parsed_content.posts:
            linkedin_count = len([p for p in parsed_content.posts if p.platform == 'LinkedIn'])
            facebook_count = len([p for p in parsed_content.posts if p.platform == 'Facebook'])
            instagram_count = len([p for p in parsed_content.posts if p.platform == 'Instagram'])
            st.caption(f"  - LinkedIn: {linkedin_count} posts")
            st.caption(f"  - Facebook: {facebook_count} posts")
            st.caption(f"  - Instagram: {instagram_count} posts")

        st.divider()

        # Show first 500 chars
        st.text_area("First 500 chars of combined_output:", combined_output[:500], height=150)

        # If empty, show what we have
        if not combined_output:
            st.error("⚠️ combined_output is EMPTY!")
            st.text_area("Copy output (first 500):", result.get('copy_output', '')[:500], height=100)
            st.text_area("Strategy output (first 500):", result.get('strategy_output', '')[:500], height=100)

    # Strategic Brief
    with st.expander("📋 Campaign Bible (Strategic Brief)", expanded=False):
        # Try parsed strategy first, fallback to raw strategy_output
        strategy_to_show = parsed_content.strategy_output or result.get('strategy_output', '')

        if strategy_to_show:
            st.markdown(f'<div class="rtl-text">{strategy_to_show}</div>', unsafe_allow_html=True)
        else:
            st.warning("לא נמצא תקציר אסטרטגי")

    st.divider()

    # Content cards
    st.markdown("### ✍️ Generated Posts")

    # Show stats
    total_posts = len(parsed_content.posts)
    st.caption(f"סה״כ {total_posts} פוסטים נוצרו")

    tab1, tab2, tab3 = st.tabs(["📘 LinkedIn", "📱 Facebook", "📸 Instagram"])

    with tab1:
        linkedin_posts = get_posts_by_platform(parsed_content, "LinkedIn")

        if linkedin_posts:
            st.info(f"📊 {len(linkedin_posts)} פוסטים ל-LinkedIn")
            st.divider()

            for post in linkedin_posts:
                post_id = f"linkedin_{post.number}"
                display_post_card(post, post_id)
        else:
            st.warning("לא נמצאו פוסטים ל-LinkedIn")

    with tab2:
        facebook_posts = get_posts_by_platform(parsed_content, "Facebook")

        if facebook_posts:
            st.info(f"📊 {len(facebook_posts)} פוסטים ל-Facebook")
            st.divider()

            for post in facebook_posts:
                post_id = f"facebook_{post.number}"
                display_post_card(post, post_id)
        else:
            st.warning("לא נמצאו פוסטים ל-Facebook")

    with tab3:
        instagram_posts = get_posts_by_platform(parsed_content, "Instagram")

        if instagram_posts:
            st.info(f"📊 {len(instagram_posts)} פוסטים ל-Instagram")
            st.divider()

            for post in instagram_posts:
                post_id = f"instagram_{post.number}"
                display_post_card(post, post_id)
        else:
            st.warning("לא נמצאו פוסטים ל-Instagram")

    st.divider()

    # Actions section - Editor's Desk is the primary workspace
    # Secondary navigation actions in a compact, less prominent layout
    st.markdown("#### 🔗 ניווט מהיר")
    st.caption("Editor's Desk הוא אזור העבודה הראשי שלך - הכפתורים למטה הם לניווט בלבד")
    
    # Compact secondary navigation buttons
    nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 1])
    
    with nav_col1:
        if st.button("← Factory Floor", key="nav_factory", use_container_width=True, type="secondary"):
            st.switch_page("pages/2_🏭_Factory_Floor.py")
    
    with nav_col2:
        filepath = st.session_state.get('last_output_file', '')
        if filepath and Path(filepath).exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                file_content = f.read()
            st.download_button(
                label="💾 Download",
                data=file_content,
                file_name=Path(filepath).name,
                mime="text/markdown",
                use_container_width=True,
                type="secondary"
            )
        else:
            st.button("💾 Download", disabled=True, use_container_width=True, help="לא נמצא קובץ פלט", type="secondary")
    
    with nav_col3:
        if st.button("🔄 יצירה חדשה", key="nav_new", use_container_width=True, type="secondary"):
            st.session_state.factory_status = 'idle'
            st.session_state.architect_validated = False
            st.session_state.factory_result = {}
            st.session_state.editor_post_edits = {}
            st.session_state.editor_post_feedback = {}
            st.switch_page("pages/1_📐_Architects_Table.py")

    # Add feedback learning system controls
    st.divider()
    st.markdown("### 🔄 מערכת למידה מפידבקים")

    # Get last update time from learnings file
    learnings_file_path = Path("Data/feedback_learnings_copywriter.txt")
    last_updated = "לא עודכן"
    total_patterns = 0
    
    if learnings_file_path.exists():
        try:
            # Read first few lines to extract last updated timestamp
            with open(learnings_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:5]
                for line in lines:
                    if "Last Updated:" in line:
                        last_updated = line.split("Last Updated:")[-1].strip()
                    if "Total Patterns:" in line:
                        # Extract number from "Total Patterns: 24 (LinkedIn: 10, ...)"
                        import re
                        match = re.search(r'Total Patterns:\s*(\d+)', line)
                        if match:
                            total_patterns = int(match.group(1))
        except Exception as e:
            last_updated = f"שגיאה בקריאה: {str(e)[:30]}"

    col_a, col_b = st.columns([3, 1])

    with col_a:
        st.caption("""
        לחץ על 'עדכן מאגר למידה' כדי לבנות מחדש את קובץ הידע מכל הפידבקים המאושרים.
        האגנטים ילמדו מקובץ זה בייצור הבא (לאחר הפעלה מחדש של האפליקציה).
        """)
        
        # Show last update indicator
        if last_updated != "לא עודכן":
            st.info(f"📅 **עודכן לאחרונה:** {last_updated} | **דפוסים פעילים:** {total_patterns}")
        else:
            st.warning("⚠️ מאגר הלמידה לא עודכן עדיין")

    with col_b:
        if st.button("🔄 עדכן מאגר למידה", type="secondary", use_container_width=True):
            with st.spinner("מצבר פידבקים..."):
                try:
                    from scripts.aggregate_feedback import aggregate_feedback_to_rag

                    stats = aggregate_feedback_to_rag(verbose=False)

                    st.success(f"""
✅ מאגר הלמידה עודכן בהצלחה!

- סך הכל דפוסים: {stats['total_patterns']}
- LinkedIn: {stats['by_platform'].get('LinkedIn', 0)}
- Facebook: {stats['by_platform'].get('Facebook', 0)}
- Instagram: {stats['by_platform'].get('Instagram', 0)}

עודכן לאחרונה: {stats['last_updated']}
                    """)

                    st.info("""
⚠️ שים לב: הדפוסים החדשים יהיו זמינים לאחר הפעלה מחדש של האפליקציה.
ChromaDB ייבנה מחדש את ה-embeddings בהפעלה הבאה.
                    """)

                except Exception as e:
                    st.error(f"❌ שגיאה בעדכון מאגר למידה: {str(e)}")
                    st.caption("פרטים נוספים:")
                    st.code(str(e), language="text")


if __name__ == "__main__":
    main()
