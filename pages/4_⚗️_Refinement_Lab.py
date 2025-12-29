# -*- coding: utf-8 -*-
"""
Dana's Brain - The Refinement Lab
Structured feedback refinement workspace

This page processes PENDING_REFINEMENT feedback items with
structured micro-prompts instead of free-form text.
"""

import streamlit as st
import json
from datetime import datetime
from pathlib import Path

from core.auth import require_authentication
from core.feedback_manager import (
    get_lab_queue,
    update_status,
    get_feedback_by_id,
    auto_age_lab_items
)
from ui.styles import load_custom_css

# Page config
st.set_page_config(
    page_title="The Refinement Lab - Dana's Brain",
    page_icon="⚗️",
    layout="wide"
)

# Load custom styles
load_custom_css()

# Require authentication
require_authentication()


def get_structured_prompts(category: str) -> dict:
    """
    Get category-specific structured micro-prompts

    Returns dict with:
    - question: The main question
    - options: List of checkbox options
    - followup_prompt: Short text input prompt
    """

    prompts = {
        "Tone": {
            "question": "❓ איזה חלק הרגיש לא נכון?",
            "options": [
                "שורת הפתיחה",
                "משפטי המעבר",
                "קריאה לפעולה (CTA)",
                "האווירה הכללית"
            ],
            "followup_question": "❓ מה הבעיה?",
            "followup_options": [
                "מכירתי מדי",
                "פורמלי מדי",
                "חסר חום/אישיות",
                "ארכיטייפ לא נכון (Head/Heart/Hands)",
                "לא נשמע כמו דנה"
            ],
            "text_prompt": "💬 הסבר קצר (עד 10 מילים):"
        },

        "Structure": {
            "question": "❓ מה חסר או לא תקין במבנה?",
            "options": [
                "חסר הוק פותח חזק",
                "אין CTA ברור",
                "חסרה הצעת ערך מרכזית",
                "סדר לא הגיוני (פותח->גוף->CTA)",
                "חסרה סגירה/מסקנה"
            ],
            "followup_question": "❓ מה צריך להיות במקום?",
            "followup_options": [],  # No followup for this category
            "text_prompt": "💬 הצעה לשיפור (עד 10 מילים):"
        },

        "Words": {
            "question": "❓ אילו מילים או ביטויים בעייתיים?",
            "options": [],  # No checkboxes - goes straight to text
            "followup_question": "",
            "followup_options": [],
            "text_prompt": "💬 רשמי את המילה/ביטוי הבעייתי ואת ההחלפה המוצעת (עד 15 מילים):"
        },

        "Length": {
            "question": "❓ מה הבעיה באורך?",
            "options": [
                "ארוך מדי לפלטפורמה",
                "קצר מדי - חסרה פיתוח",
                "לא מתאים לארכיטייפ (Heart=קצר, Head=ארוך)"
            ],
            "followup_question": "",
            "followup_options": [],
            "text_prompt": "💬 איזה אורך מתאים? (למשל: '50-60 מילים'):"
        },

        "Platform_Fit": {
            "question": "❓ למה הפוסט לא מתאים לפלטפורמה?",
            "options": [
                "לא מתאים לטון של הפלטפורמה",
                "אורך לא נכון לפלטפורמה",
                "מבנה לא מתאים (למשל: לינקדאין צריך insight)",
                "שפה פורמלית/לא פורמלית מדי"
            ],
            "followup_question": "",
            "followup_options": [],
            "text_prompt": "💬 מה צריך להשתנות? (עד 10 מילים):"
        },

        "Strategic Miss / DNA Mismatch": {
            "question": "⚠️ איזה כלל אסטרטגי בסיסי נשבר?",
            "options": [
                "התאמה שגויה לפלטפורמה (פוסט נשמע כמו פלטפורמה אחרת)",
                "ארכיטייפ שגוי (Head במקום Heart או להיפך)",
                "חסרה תועלת מרכזית/ברורה",
                "טון שגוי לחלוטין לקהל יעד",
                "לא מתיישר עם ההצעה/המבצע",
                "לא משקף את DNA של הלקוח"
            ],
            "followup_question": "",
            "followup_options": [],
            "text_prompt": "💬 מה היה צריך להיות במקום? (עד 15 מילים):"
        },

        "Other": {
            "question": "❓ מה הבעיה?",
            "options": [],
            "followup_question": "",
            "followup_options": [],
            "text_prompt": "💬 הסבר את הבעיה (עד 20 מילים):"
        }
    }

    return prompts.get(category, prompts["Other"])


def display_feedback_card(feedback: dict, card_index: int):
    """Display a single feedback item for refinement"""

    feedback_id = feedback['id']

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #2D2D44 0%, #1E1E2E 100%);
                border-left: 4px solid #CA4D9B;
                border-radius: 12px;
                padding: 24px;
                margin-bottom: 24px;
                box-shadow: 0 4px 6px rgba(202, 77, 155, 0.1);">
    """, unsafe_allow_html=True)

    with st.container():
        # Header
        col_h1, col_h2, col_h3, col_h4 = st.columns([2, 1, 1, 1])

        with col_h1:
            st.markdown(f"**⚗️ Lab Item #{card_index + 1}**")
            st.caption(f"ID: {feedback_id} | Created: {feedback.get('created_at', 'Unknown')[:10]}")

        with col_h2:
            rating = feedback.get('rating', 0)
            st.markdown(f"**Rating:** {'⭐' * rating}")

        with col_h3:
            platform = feedback.get('platform', 'Unknown')
            # Add emoji based on platform
            platform_emoji = {
                'LinkedIn': '📘',
                'Facebook': '📱',
                'Instagram': '📸'
            }.get(platform, '📄')
            st.markdown(f"**Platform:** {platform_emoji} {platform}")

        with col_h4:
            category = feedback.get('category', 'Unknown')
            st.markdown(f"**Category:** {category}")

        st.divider()

        # Original post content
        platform = feedback.get('platform', 'Unknown')
        platform_emoji = {
            'LinkedIn': '📘',
            'Facebook': '📱',
            'Instagram': '📸'
        }.get(platform, '📄')
        st.markdown(f"### {platform_emoji} התוכן המקורי ({platform})")
        st.markdown(f"""
        <div class="rtl-text" style="background: #2D2D44; padding: 15px; border-radius: 8px; white-space: pre-wrap; direction: rtl;">
        {feedback.get('content', 'No content available')}
        </div>
        """, unsafe_allow_html=True)

        # Original feedback
        st.markdown("### 💬 משוב ראשוני (מעורפל)")
        original_feedback = feedback.get('raw_text_feedback', '(ריק)')
        st.info(f"📝 \"{original_feedback}\"")

        # Actionability info
        actionability = feedback.get('actionability_score', 0)
        st.caption(f"🎯 Actionability Score: {actionability:.2f} (Low = needs refinement)")

        st.markdown("---")

        # === STRUCTURED REFINEMENT ===
        st.markdown("### ⚗️ שיפור מובנה")
        st.caption("✨ עניני על התיבות והשדה הקצר למטה - זה יעזור למערכת ללמוד!")

        # Get category-specific prompts
        prompts = get_structured_prompts(category)

        # Question 1: Main question with checkboxes
        if prompts["options"]:
            st.markdown(f"**{prompts['question']}**")
            selected_options = []
            for option in prompts["options"]:
                if st.checkbox(option, key=f"opt_{feedback_id}_{option}"):
                    selected_options.append(option)
        else:
            selected_options = []

        # Question 2: Followup question (if applicable)
        selected_followup = []
        if prompts["followup_options"]:
            st.markdown(f"**{prompts['followup_question']}**")
            for option in prompts["followup_options"]:
                if st.checkbox(option, key=f"followup_{feedback_id}_{option}"):
                    selected_followup.append(option)

        # Short text explanation
        st.markdown(f"**{prompts['text_prompt']}**")
        short_explanation = st.text_input(
            label="הסבר קצר",
            max_chars=100,
            key=f"text_{feedback_id}",
            label_visibility="collapsed",
            placeholder="מקסימום 10-15 מילים..."
        )

        st.divider()

        # Action buttons
        col_btn1, col_btn2, col_btn3 = st.columns(3)

        with col_btn1:
            if st.button("💾 שמור ואמן", key=f"save_{feedback_id}", type="primary", use_container_width=True):
                # Build refinement data
                refinement_data = {
                    "category": category,
                    "selected_options": selected_options,
                    "selected_followup": selected_followup,
                    "short_explanation": short_explanation,
                    "refined_at": datetime.now().isoformat()
                }

                try:
                    # Update status to APPROVED and save refinement data
                    update_status(
                        feedback_id=feedback_id,
                        new_status='approved',  # Promote to approved
                        notes=f"Refined in Lab: {short_explanation[:50]}",
                        refinement_data=refinement_data
                    )

                    st.success("✅ פידבק שופר ונשמר למערכת הלמידה!")
                    st.balloons()

                    # Remove from session state queue
                    if 'lab_queue' in st.session_state:
                        st.session_state.lab_queue = [f for f in st.session_state.lab_queue if f['id'] != feedback_id]

                    st.rerun()

                except Exception as e:
                    st.error(f"❌ שגיאה בשמירה: {str(e)}")

        with col_btn2:
            if st.button("⏭️ דלג (שמור AS-IS)", key=f"skip_{feedback_id}", use_container_width=True):
                try:
                    update_status(
                        feedback_id=feedback_id,
                        new_status='SKIPPED',
                        notes="Skipped refinement - saved original vague feedback"
                    )

                    st.info("ℹ️ פידבק נשמר ללא שיפור")

                    # Remove from queue
                    if 'lab_queue' in st.session_state:
                        st.session_state.lab_queue = [f for f in st.session_state.lab_queue if f['id'] != feedback_id]

                    st.rerun()

                except Exception as e:
                    st.error(f"❌ שגיאה: {str(e)}")

        with col_btn3:
            if st.button("🗑️ מחק", key=f"discard_{feedback_id}", use_container_width=True):
                try:
                    update_status(
                        feedback_id=feedback_id,
                        new_status='DISCARDED',
                        notes="Discarded - not useful"
                    )

                    st.warning("⚠️ פידבק נמחק")

                    # Remove from queue
                    if 'lab_queue' in st.session_state:
                        st.session_state.lab_queue = [f for f in st.session_state.lab_queue if f['id'] != feedback_id]

                    st.rerun()

                except Exception as e:
                    st.error(f"❌ שגיאה: {str(e)}")

    # Close card div
    st.markdown("</div>", unsafe_allow_html=True)


def main():
    """The Refinement Lab - Structured feedback clarification workspace"""

    st.title("⚗️ The Refinement Lab")
    st.subheader("Structured Feedback Refinement")

    st.markdown("""
    **המעבדה עוזרת לשפר פידבקים מעורפלים למידע actionable שהמערכת יכולה ללמוד ממנו.**

    - ✅ פידבקים שקיבלו ציון 5 או היו ספציפיים מספיק → אושרו אוטומטית
    - ⚗️ פידבקים מעורפלים או קטגוריית "Strategic Miss" → הגיעו לכאן לשיפור
    - ⏭️ פידבקים שנמצאים כאן יותר מ-7 ימים → מתודלגים אוטומטית
    """)

    # Run auto-aging (cleanup old items)
    try:
        aged_count = auto_age_lab_items(days_threshold=7)
        if aged_count > 0:
            st.info(f"🕒 {aged_count} פידבקים ישנים (>7 ימים) דולגו אוטומטית")
    except Exception as e:
        st.caption(f"⚠️ Auto-aging failed: {str(e)}")

    st.divider()

    # Get client context
    client_id = st.session_state.get('selected_client', 'Lierac')

    # Check if we need to refresh (button clicked or client changed or first load)
    should_refresh = st.button("🔄 רענן רשימה")
    current_client = st.session_state.get('lab_queue_client')
    is_first_load = 'lab_queue' not in st.session_state
    client_changed = current_client is not None and current_client != client_id
    
    # Track if this is the first render of this page visit
    # Use a key that resets when navigating away and back
    page_key = f"lab_page_loaded_{client_id}"
    is_page_first_load = page_key not in st.session_state
    
    # Load lab queue if needed
    # Always load on first page visit, refresh button, or client change
    if is_page_first_load or should_refresh or client_changed:
        try:
            queue = get_lab_queue(client_id=client_id, limit=50)
            st.session_state.lab_queue = queue
            st.session_state.lab_queue_client = client_id
            st.session_state[page_key] = True  # Mark that we've loaded for this client
        except Exception as e:
            st.error(f"❌ שגיאה בטעינת התור: {str(e)}")
            st.session_state.lab_queue = []
            st.session_state.lab_queue_client = client_id
            st.session_state[page_key] = True

    queue = st.session_state.get('lab_queue', [])

    # Show queue status
    if not queue:
        st.success("🎉 אין פידבקים הממתינים לשיפור!")
        st.info("כל הפידבקים האחרונים היו ספציפיים מספיק או קיבלו ציון 5.")

        if st.button("← חזרה ל-Editor's Desk"):
            st.switch_page("pages/3_✍️_Editors_Desk.py")

        st.stop()

    # Queue header
    st.markdown(f"### 📋 התור ({len(queue)} פריטים)")
    st.progress(0 if not queue else min(1.0, 1 / len(queue)))

    st.divider()

    # Display first item (FIFO - oldest first)
    st.markdown("### 🔬 פריט נוכחי")
    display_feedback_card(queue[0], 0)

    # Show remaining items in expander
    if len(queue) > 1:
        with st.expander(f"📦 עוד {len(queue) - 1} פריטים ממתינים"):
            for i, item in enumerate(queue[1:], start=1):
                st.caption(f"**#{i+1}**: {item.get('category')} | Rating: {item.get('rating')}⭐ | Created: {item.get('created_at', '')[:10]}")


if __name__ == "__main__":
    main()
