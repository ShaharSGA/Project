# -*- coding: utf-8 -*-
"""
Dana's Brain - The Architect's Table
Strategic planning workspace for campaign inputs
"""

import streamlit as st
from pydantic import ValidationError
from datetime import datetime

from core.auth import require_authentication
from core.state_manager import update_workflow_stage
from ui.styles import load_custom_css
from models import CampaignInput, WebScrapingResult
from tools.web_scraper import scrape_and_extract

# Page config
st.set_page_config(
    page_title="The Architect's Table - Dana's Brain",
    page_icon="📐",
    layout="wide"
)

# Load custom styles
load_custom_css()

# Require authentication
require_authentication()


def get_temperature_description(temp: float) -> str:
    """Get Hebrew description for temperature value."""
    if temp <= 0.4:
        return f"נמוכה (ממוקד ומדויק) 🎯 - {temp}"
    elif temp <= 0.6:
        return f"בינונית (איזון בין דיוק ליצירתיות) ⚖️ - {temp}"
    elif temp <= 0.7:
        return f"בינונית-גבוהה (יצירתי ומגוון) 🎨 - {temp}"
    else:
        return f"גבוהה (מאוד יצירתי וחופשי) 🌈 - {temp}"


def main():
    """The Architect's Table - Strategic planning workspace."""

    # Initialize session_id if not exists
    if 'session_id' not in st.session_state:
        st.session_state.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    st.title("📐 The Architect's Table")
    st.subheader("Strategic Planning & Gap Analysis")

    st.markdown("""
    <div class="fade-in">
    הזן את פרטי הקמפיין למטה. המערכת תנתח את המוצר ותיצור תוכן שיווקי מותאם.
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Initialize architect_inputs if not exists
    if 'architect_inputs' not in st.session_state:
        st.session_state.architect_inputs = {
            "product": "",
            "benefits": "",
            "audience": "",
            "offer": "",
            "persona": "Friendly Dana"
        }

    # Persona selection OUTSIDE form (so it updates in real-time)
    st.markdown("### 👤 Select Dana Persona")

    persona_options = {
        "Professional Dana": {
            "temp": 0.4,
            "desc": "מקצועי, ממוקד, מבוסס נתונים",
            "icon": "🎯"
        },
        "Friendly Dana": {
            "temp": 0.8,
            "desc": "חברותי, יצירתי, \"חברה הכי טובה\"",
            "icon": "💜"
        },
        "Inspirational Dana": {
            "temp": 0.7,
            "desc": "מעורר השראה, מוטיבציה, העצמה",
            "icon": "✨"
        },
        "Mentor Dana": {
            "temp": 0.5,
            "desc": "מנטורינג, הדרכה, תומך",
            "icon": "🤝"
        }
    }

    # Get current persona from session state
    current_persona = st.session_state.architect_inputs.get("persona", "Friendly Dana")

    # Find index of current persona
    persona_names = list(persona_options.keys())
    try:
        current_index = persona_names.index(current_persona)
    except ValueError:
        current_index = 1  # Default to Friendly Dana

    col_persona_1, col_persona_2 = st.columns([2, 1])

    with col_persona_1:
        # Create persona selection
        persona_choice = st.radio(
            "בחרו פרסונה:",
            options=persona_names,
            index=current_index,
            format_func=lambda x: f"{persona_options[x]['icon']} {x}",
            help="כל פרסונה משנה את הטון והסגנון של התוכן",
            key="persona_radio",
            horizontal=True
        )

        # Update session state when persona changes
        if persona_choice != st.session_state.architect_inputs.get("persona"):
            st.session_state.architect_inputs["persona"] = persona_choice

    with col_persona_2:
        # Show persona details - NOW UPDATES AUTOMATICALLY
        selected_persona = persona_options[persona_choice]
        st.info(f"""
        **{persona_choice}**

        {selected_persona['desc']}

        **רמת יצירתיות:**
        {get_temperature_description(selected_persona['temp'])}
        """)

    st.divider()

    # Web Scraping Section
    st.markdown("### 🌐 Auto-Fill from Website")
    st.markdown("הזן URL של אתר המוצר כדי למלא אוטומטית את השדות")

    col_url, col_scrape = st.columns([3, 1])

    with col_url:
        scrape_url = st.text_input(
            "כתובת אתר (URL)",
            placeholder="https://example.com/product",
            help="הזן כתובת אתר המוצר. המערכת תחלץ מידע אוטומטית",
            key="scrape_url_input",
            label_visibility="collapsed"
        )

    with col_scrape:
        scrape_button = st.button(
            "🔍 חלץ מידע",
            use_container_width=True,
            type="secondary",
            disabled=not scrape_url or len(scrape_url.strip()) < 10
        )

    # Process scraping
    if scrape_button and scrape_url:
        with st.spinner("סורק אתר וחולץ מידע... (עשוי לקחת 10-20 שניות)"):
            result: WebScrapingResult = scrape_and_extract(scrape_url)

            if result.success:
                # Success - merge extracted data into session state
                filled_fields = result.get_filled_fields()
                empty_fields = result.get_empty_fields()

                # Update session state with non-empty fields
                if result.product and result.product.strip():
                    st.session_state.architect_inputs['product'] = result.product
                if result.benefits and result.benefits.strip():
                    st.session_state.architect_inputs['benefits'] = result.benefits
                if result.audience and result.audience.strip():
                    st.session_state.architect_inputs['audience'] = result.audience
                if result.offer and result.offer.strip():
                    st.session_state.architect_inputs['offer'] = result.offer

                # Save the source URL for potential agent use
                st.session_state.architect_inputs['source_url'] = scrape_url

                # Show success message
                lang_emoji = {'he': '🇮🇱', 'en': '🇺🇸', 'fr': '🇫🇷'}.get(result.detected_language, '🌐')
                st.success(f"✅ חולץ בהצלחה! {lang_emoji} שפה: {result.detected_language}")

                col_success1, col_success2 = st.columns(2)
                with col_success1:
                    st.info(f"**שדות שנמלאו:** {len(filled_fields)}/4")
                    for field in filled_fields:
                        field_names = {
                            'product': '✓ שם מוצר',
                            'benefits': '✓ יתרונות',
                            'audience': '✓ קהל יעד',
                            'offer': '✓ הצעה'
                        }
                        st.caption(field_names.get(field, field))

                with col_success2:
                    st.metric(
                        "רמת ביטחון בחילוץ",
                        f"{result.extraction_confidence * 100:.0f}%"
                    )

                # Show warning for empty fields
                if empty_fields:
                    st.warning(result.format_warning_message())
                    st.caption("תוכל למלא את השדות החסרים ידנית בטופס למטה")

                # Rerun to update form
                st.rerun()

            else:
                # Error occurred
                st.error(f"❌ שגיאה בחילוץ מידע")
                st.error(result.error_message)

                st.info("**טיפים לפתרון בעיות:**")
                st.caption("• ודא שהכתובת תקינה ומתחילה ב-https://")
                st.caption("• ודא שהאתר נגיש (לא חסום)")
                st.caption("• נסה URL אחר של אותו מוצר")

    st.divider()

    # Create form
    with st.form("architect_form", clear_on_submit=False):
        st.markdown("### 📝 קלט קמפיין")

        # Product name
        product = st.text_input(
            "🏷️ שם מוצר/שירות",
            max_chars=200,
            placeholder="לדוגמה: Lierac Hydragenist Serum",
            help="שם המוצר או השירות (1-200 תווים)",
            value=st.session_state.architect_inputs.get("product", "")
        )

        # Benefits
        benefits = st.text_area(
            "💎 יתרונות עיקריים",
            max_chars=1000,
            height=120,
            placeholder="רשמו את היתרונות העיקריים של המוצר...\nלמשל: לחות עמוקה, זוהר מיידי, מרכיבים טבעיים...",
            help="יתרונות עיקריים (10-1000 תווים)",
            value=st.session_state.architect_inputs.get("benefits", "")
        )

        # Target audience
        audience = st.text_area(
            "🎯 קהל יעד",
            max_chars=500,
            height=100,
            placeholder="תארו את קהל היעד...\nלמשל: נשים בגילאי 35-50, מעוניינות באנטי-אייג'ינג...",
            help="תיאור קהל היעד (5-500 תווים)",
            value=st.session_state.architect_inputs.get("audience", "")
        )

        # Offer (optional)
        offer = st.text_input(
            "🎁 ההצעה (אופציונלי)",
            max_chars=300,
            placeholder="הנחה, מתנה, קידום מכירות...",
            help="ההצעה השיווקית (אופציונלי, עד 300 תווים)",
            value=st.session_state.architect_inputs.get("offer", "")
        )

        st.divider()

        # Advanced options - Allow agent to access source URL
        if st.session_state.architect_inputs.get('source_url'):
            allow_url_access = st.checkbox(
                "🌐 אפשר לסוכן האסטרטגי לגשת לאתר המקור למידע נוסף",
                value=False,
                help="אם מסומן, הסוכן האסטרטגי יוכל לגשת לאתר המקור ולקבל מידע נוסף מעבר לטופס"
            )

            if allow_url_access:
                st.caption(f"🔗 האתר: {st.session_state.architect_inputs.get('source_url')}")
        else:
            allow_url_access = False

        st.divider()

        # Character counters
        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a:
            st.caption(f"מוצר: {len(product)}/200")
        with col_b:
            st.caption(f"יתרונות: {len(benefits)}/1000")
        with col_c:
            st.caption(f"קהל יעד: {len(audience)}/500")
        with col_d:
            st.caption(f"הצעה: {len(offer)}/300")

        # Submit button
        submitted = st.form_submit_button(
            "⚡ Send to Factory Floor",
            use_container_width=True,
            type="primary"
        )

        if submitted:
            # Validate inputs
            try:
                # Convert empty offer to None (optional field)
                offer_value = offer.strip() if offer and offer.strip() else None
                
                validated_input = CampaignInput(
                    product=product,
                    benefits=benefits,
                    audience=audience,
                    offer=offer_value,
                    persona=persona_choice
                )

                # Save to session state
                inputs_dict = validated_input.to_dict()

                # Keep source_url from previous session state if it exists
                old_source_url = st.session_state.architect_inputs.get('source_url')
                if old_source_url:
                    inputs_dict['source_url'] = old_source_url

                # Save URL access permission
                inputs_dict['allow_url_access'] = allow_url_access

                st.session_state.architect_inputs = inputs_dict
                st.session_state.architect_validated = True

                # Update workflow stage
                update_workflow_stage("factory_floor")

                # Success message
                success_msg = "✅ הקלט אושר! מעביר לרצפת הייצור..."
                if allow_url_access and old_source_url:
                    success_msg += f"\n\n🌐 הסוכן האסטרטגי יוכל לגשת לאתר המקור"
                st.success(success_msg)

                # Navigate to Factory Floor
                st.switch_page("pages/2_🏭_Factory_Floor.py")

            except ValidationError as e:
                # Display validation errors
                st.error("❌ שגיאת אימות")

                for error in e.errors():
                    field = error['loc'][0]
                    msg = error['msg']

                    # Add character count for string length errors
                    if field in ['product', 'benefits', 'audience', 'offer']:
                        current_value = locals()[field]
                        char_count = len(current_value)

                        limits = {
                            'product': 200,
                            'benefits': 1000,
                            'audience': 500,
                            'offer': 300
                        }

                        if 'at most' in msg or 'at least' in msg:
                            st.warning(f"**{field}**: {msg}\n- תווים נוכחיים: {char_count} (מקסימום: {limits.get(field, '?')})")
                        else:
                            st.warning(f"**{field}**: {msg}")

            except Exception as e:
                st.error(f"❌ שגיאה: {str(e)}")

    st.divider()

    # Show last generation if available
    if st.session_state.get('factory_status') == 'completed':
        st.success("✅ יש לך יצירה קיימת!")

        result = st.session_state.get('factory_result', {})
        inputs = st.session_state.get('architect_inputs', {})

        col_info1, col_info2, col_info3 = st.columns(3)
        with col_info1:
            st.info(f"**מוצר:** {inputs.get('product', 'N/A')}")
        with col_info2:
            st.info(f"**פרסונה:** {inputs.get('persona', 'N/A')}")
        with col_info3:
            exec_time = result.get('execution_time', 0)
            st.info(f"**זמן יצירה:** {exec_time:.1f}s")

        with st.expander("📋 תצוגה מקדימה של תקציר אסטרטגי"):
            strategy = result.get('strategy_output', '')
            if strategy:
                st.markdown(f'<div class="rtl-text">{strategy[:500]}...</div>', unsafe_allow_html=True)

        col_resume1, col_resume2 = st.columns(2)

        with col_resume1:
            if st.button("🔄 צור קמפיין חדש", type="secondary", use_container_width=True):
                # Reset everything
                st.session_state.factory_status = 'idle'
                st.session_state.architect_validated = False
                st.session_state.factory_result = {}
                st.rerun()

        with col_resume2:
            if st.button("📝 המשך לעריכה →", type="primary", use_container_width=True):
                # Go directly to Editor's Desk
                update_workflow_stage("editors_desk")
                st.switch_page("pages/3_✍️_Editors_Desk.py")

        st.divider()

    # Navigation
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("← חזרה ל-Handshake"):
            st.switch_page("pages/0_🤝_Handshake.py")

    with col3:
        if st.session_state.get('architect_validated', False):
            if st.button("Next: Factory Floor →"):
                st.switch_page("pages/2_🏭_Factory_Floor.py")


if __name__ == "__main__":
    main()
