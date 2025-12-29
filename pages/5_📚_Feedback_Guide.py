# -*- coding: utf-8 -*-
"""
Dana's Brain - Feedback System Guide
Educational page explaining how the feedback loop works
"""

import streamlit as st
from pathlib import Path

from core.auth import require_authentication
from ui.styles import load_custom_css

# Page config
st.set_page_config(
    page_title="Feedback Guide - Dana's Brain",
    page_icon="📚",
    layout="wide"
)

# Load custom styles
load_custom_css()

# Require authentication
require_authentication()


def main():
    """Feedback System Guide - Educational page."""

    st.title("📚 מדריך מערכת הפידבק")
    st.subheader("איך דנה לומדת מהמשוב שלך?")

    st.markdown("---")

    # Overview
    st.markdown("## 🎯 מה זה מערכת הפידבק?")

    st.markdown("""
    מערכת הפידבק של דנה היא **לב מנוע הלמידה** - היא הופכת את המשוב שלך לידע שדנה משתמשת בו בכל ייצור תוכן.

    **העיקרון המרכזי:** ככל שתיתן יותר פידבק איכותי, כך דנה תשתפר ותתאים עצמה בדיוק למה שאתה צריך.
    """)

    st.info("""
    💡 **זכור:** דנה לא משנה את עצמה אוטומטית - היא **לומדת מהפידבקים המאושרים** שלך ומשתמשת בהם בייצורים הבאים.
    """)

    st.markdown("---")

    # Journey of feedback
    st.markdown("## 🚀 מסע הפידבק: מרגע ההגשה ועד הלמידה")

    # Create 3-stage flow
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### שלב 1️⃣: הגשה")
        st.markdown("""
        **אתה ממלא בעמוד Editor's Desk:**
        - ⭐ **דירוג** (1-5): כמה טוב הפוסט?
        - 🏷️ **קטגוריה**: מה ההיבט שאתה מדרג?
          - `Tone` = טון ואופי הכתיבה
          - `Length` = אורך הפוסט
          - `Words` = בחירת מילים ספציפיות
          - `Structure` = מבנה הפוסט (פתיחה/גוף/סיום)
          - `Platform_Fit` = התאמה לפלטפורמה
          - `Strategic Miss` = אי-התאמה אסטרטגית בסיסית
          - `Other` = אחר
        - ✍️ **משוב בכתיבה** (אופציונלי): הסבר ספציפי

        **מה קורה ברגע ההגשה?**
        1. המערכת מנקה את הטקסט (מסירה PII, בודקת prompt injection)
        2. מחשבת **ציון אמינות** (0-1) - כמה המשוב אמין?
        3. מעריכה **ציון actionability** (0-1) - כמה המשוב ניתן לפעולה?
        4. מחליטה לאן לנתב את הפידבק
        """)

    with col2:
        st.markdown("### שלב 2️⃣: ניתוב (Triage)")
        st.markdown("""
        **המערכת מחליטה אוטומטית:**

        ✅ **APPROVED** (ישירות ללמידה)
        - דירוג קיצוני (1-2 או 4-5)
        - משוב ארוך (>20 תווים)
        - קטגוריה ברורה
        - ציון actionability גבוה (>0.7)

        ⚗️ **PENDING_REFINEMENT** (מעבדת שיפור)
        - דירוג ביניים (3)
        - משוב קצר או ריק
        - צריך הבהרה נוספת
        - ציון actionability נמוך (<0.7)

        **למה זה חשוב?**
        אנחנו רוצים רק פידבקים **איכותיים וברורים** במאגר הלמידה.
        פידבק עמום מזיק יותר מאשר עוזר!
        """)

    with col3:
        st.markdown("### שלב 3️⃣: למידה")
        st.markdown("""
        **פידבקים מאושרים → קובץ ידע:**

        1. **צבירה אוטומטית**
           - פידבקים עם `status='approved'` נאספים
           - מקובצים לפי פלטפורמה (LinkedIn/FB/IG)

        2. **המרה לדפוסי למידה**
           - "דירוג 5 + Tone = נשמר הסגנון"
           - "דירוג 1 + Words = נמנע מהמילים האלה"

        3. **שמירה ב-Data/feedback_learnings_copywriter.txt**
           - הקובץ שדנה קוראת בכל ייצור!

        4. **בייצור הבא**
           - דנה משתמשת ב-RAG לחפש בקובץ
           - מוצאת דפוסים רלוונטיים
           - מיישמת אותם בכתיבה
        """)

    st.markdown("---")

    # Confidence score explanation
    st.markdown("## 🎯 מה זה ציון האמינות?")

    st.markdown("""
    **ציון האמינות (Confidence Score)** הוא ציון 0-1 שמעריך כמה אפשר לסמוך על הפידבק שלך.

    הציון מחושב על בסיס **3 גורמים**:
    """)

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.markdown("### 📊 Context (30%)")
        st.markdown("""
        **האם יש מספיק הקשר?**

        ✅ **ציון גבוה:**
        - משוב טקסטואלי מפורט
        - דירוג קיצוני (1-2 או 4-5)
        - קטגוריה ספציפית (לא "Other")

        ❌ **ציון נמוך:**
        - משוב ריק
        - דירוג ביניים (3)
        - קטגוריה "Other"
        """)

    with col_b:
        st.markdown("### 🔄 Consistency (40%)")
        st.markdown("""
        **האם עקבי עם פידבקים קודמים?**

        ✅ **ציון גבוה:**
        - דפוס חוזר (למשל תמיד מעדיף טון מקצועי)
        - קטגוריה שכבר נתת עליה משוב
        - פרסונה שאתה מכיר

        ❌ **ציון נמוך:**
        - סותר פידבקים קודמים
        - קטגוריה חדשה לחלוטין
        - אין היסטוריה
        """)

    with col_c:
        st.markdown("### ✍️ Specificity (30%)")
        st.markdown("""
        **האם הפידבק ספציפי?**

        ✅ **ציון גבוה:**
        - משוב ארוך (>50 תווים)
        - מכיל דוגמאות קונקרטיות
        - ברור מה צריך לשפר

        ❌ **ציון נמוך:**
        - משוב קצר (<10 תווים)
        - כללי מדי
        - לא ברור מה צריך לעשות
        """)

    st.markdown("---")

    # Actionability score
    st.markdown("## ⚡ מה זה ציון Actionability?")

    st.markdown("""
    **ציון Actionability** (0-1) מודד **עד כמה הפידבק ניתן לפעולה** - האם דנה יכולה ללמוד ממנו משהו קונקרטי?

    המערכת משתמשת ב-LLM כדי להעריך:
    """)

    col_x, col_y = st.columns(2)

    with col_x:
        st.success("""
        ✅ **Actionability גבוה (>0.7)**

        דוגמאות:
        - "הפתיחה רשמית מדי, צריך להתחיל ב-hook רגשי"
        - "מילה 'מהפכני' לא מתאימה לפרסונה של דנה"
        - "הפוסט ארוך מדי - 200 מילים במקום 150"
        - "חסר CTA ברור בסוף"

        **למה זה טוב?**
        - ברור מה הבעיה
        - ברור איך לתקן
        - ניתן למדידה
        """)

    with col_y:
        st.warning("""
        ⚠️ **Actionability נמוך (<0.7)**

        דוגמאות:
        - "לא מספיק טוב"
        - "משהו לא מרגיש נכון"
        - "אפשר יותר טוב"
        - (משוב ריק)

        **למה זה בעייתי?**
        - לא ברור מה הבעיה
        - אי אפשר לדעת מה לשנות
        - לא ניתן ללמוד ממנו
        """)

    st.markdown("---")

    # Refinement Lab
    st.markdown("## ⚗️ מעבדת השיפור (Refinement Lab)")

    st.markdown("""
    **מה קורה לפידבקים עם status='pending_refinement'?**

    פידבקים שזקוקים להבהרה נשלחים ל**מעבדת השיפור** - שם תוכל לשפר אותם בצורה מודרכת.
    """)

    col_1, col_2 = st.columns(2)

    with col_1:
        st.markdown("### 🔍 למה צריך שיפור?")
        st.markdown("""
        - **משוב עמום** - "לא אהבתי" (מה בדיוק?)
        - **דירוג ביניים** - 3/5 (טוב או רע?)
        - **ללא הסבר** - רק דירוג ללא טקסט
        - **סתירה** - סותר פידבקים קודמים
        """)

    with col_2:
        st.markdown("### ✨ איך זה עובד?")
        st.markdown("""
        1. **שאלון קצר** - 2-3 שאלות מכוונות
        2. **דוגמאות** - המערכת נותנת אפשרויות
        3. **הקשר** - שאלות ספציפיות לקטגוריה
        4. **שמירה** - לאחר השיפור → status='approved'
        """)

    st.info("""
    💡 **טיפ:** אם אתה רואה "nudge" (תזכורת) במסך Editor's Desk - יש לך פידבקים שממתינים למעבדה!
    שיפור פידבק אחד לוקח ~30 שניות ועוזר מאוד למערכת ללמוד.
    """)

    st.markdown("---")

    # Status flow diagram
    st.markdown("## 📊 תרשים זרימת סטטוסים")

    st.markdown("""
    ```
    📝 הגשת פידבק
         ↓
    🤖 ניתוב אוטומטי (Triage)
         ↓
         ├─→ ✅ APPROVED ────────────→ 📚 Data/feedback_learnings_copywriter.txt
         │                                   ↓
         │                            🧠 דנה קוראת בייצור הבא
         │
         ├─→ ⚗️ PENDING_REFINEMENT ──→ 🔧 מעבדת השיפור
         │         ↓                      ↓
         │    (ממתין)               ✍️ משתמש משפר
         │         ↓                      ↓
         │    ⏰ לאחר 7 ימים        ✅ APPROVED → למידה
         │         ↓
         │    🗑️ SKIPPED (לא רלוונטי יותר)
         │
         └─→ 🚩 FLAGGED ───────────→ 👤 בדיקה ידנית
                                         ↓
                                    ✅/🗑️ החלטה סופית
    ```
    """)

    st.markdown("---")

    # Best practices
    st.markdown("## 🌟 מומלץ: איך לתת פידבק איכותי?")

    col_i, col_ii = st.columns(2)

    with col_i:
        st.success("""
        ### ✅ DO - כן לעשות

        1. **היה ספציפי**
           - "הפתיחה רשמית מדי" ✓
           - במקום: "לא טוב" ✗

        2. **תן דוגמאות**
           - "מילה 'innovative' לא מתאימה, תשתמש ב-'חדשני'" ✓
           - במקום: "מילים לא טובות" ✗

        3. **הסבר למה**
           - "הפוסט ארוך מדי ל-Instagram (80 מילים במקום 50)" ✓
           - במקום: "ארוך" ✗

        4. **בחר קטגוריה מדויקת**
           - אם זה עניין של מילים → `Words`
           - אל תבחר `Other` אלא אם אין אפשרות אחרת

        5. **דרג בקיצוניות**
           - 1-2 = ממש לא עבד
           - 4-5 = עבד מצוין
           - הימנע מ-3 (אמביוולנטי)
        """)

    with col_ii:
        st.error("""
        ### ❌ DON'T - אל תעשה

        1. **אל תהיה עמום**
           - ✗ "לא אהבתי"
           - ✗ "אפשר יותר טוב"
           - ✗ "משהו לא מרגיש נכון"

        2. **אל תסתור את עצמך**
           - אתמול: "אוהב טון מקצועי" ⭐⭐⭐⭐⭐
           - היום: "טון מקצועי מדי" ⭐
           - → המערכת תסמן בציון אמינות נמוך

        3. **אל תשכח הסבר**
           - משוב ריק = ציון actionability נמוך
           - ישלח למעבדה במקום ללמידה

        4. **אל תשתמש ב-"Other" אם לא חייב**
           - קטגוריה ספציפית = ציון גבוה יותר

        5. **אל תדרג 3 ללא הסבר**
           - 3 = אמביוולנטי
           - צריך הסבר מה טוב ומה רע
        """)

    st.markdown("---")

    # Statistics
    st.markdown("## 📈 כמה פידבקים יש כרגע?")

    try:
        from core.feedback_manager import get_feedback_stats

        client_id = st.session_state.get('selected_client', 'Lierac')
        stats = get_feedback_stats(client_id=client_id)

        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)

        with col_stat1:
            st.metric("סה\"כ פידבקים", stats['total'])

        with col_stat2:
            approved = stats['by_status'].get('approved', 0)
            st.metric("מאושרים (ללמידה)", approved)

        with col_stat3:
            pending_ref = stats['by_status'].get('pending_refinement', 0)
            st.metric("במעבדת שיפור", pending_ref)

        with col_stat4:
            st.metric("ציון ממוצע", f"{stats['avg_rating']:.1f}/5")

        # Show status breakdown
        st.markdown("### פילוח לפי סטטוס:")
        status_names = {
            'approved': '✅ מאושר',
            'pending': '⏳ ממתין',
            'pending_refinement': '⚗️ מעבדה',
            'flagged': '🚩 מסומן',
            'skipped': '⏭️ דולג',
            'rejected': '❌ נדחה',
            'discarded': '🗑️ הושלך'
        }

        for status, count in stats['by_status'].items():
            status_label = status_names.get(status, status)
            st.caption(f"{status_label}: {count}")

    except Exception as e:
        st.warning(f"לא ניתן לטעון סטטיסטיקות: {str(e)}")

    st.markdown("---")

    # Update learning file
    st.markdown("## 🔄 עדכון קובץ הלמידה")

    st.markdown("""
    **מתי צריך לעדכן?**
    - לאחר שאישרת פידבקים חדשים
    - לאחר שסיימת עבודה במעבדת השיפור
    - לפני ייצור תוכן חדש (כדי שדנה תלמד מהפידבקים האחרונים)

    **איך זה עובד?**
    1. לוחץ על "עדכן מאגר למידה" (בעמוד Editor's Desk)
    2. המערכת אוספת את כל הפידבקים עם `status='approved'`
    3. ממירה אותם לדפוסי למידה
    4. שומרת ב-`Data/feedback_learnings_copywriter.txt`
    5. ⚠️ **הפעל מחדש את Streamlit** כדי שהשינויים ייכנסו לתוקף (ChromaDB)
    """)

    st.info("""
    💡 **לידע:** ChromaDB (מנוע ה-RAG) טוען את הקבצים ב-`Data/` בזמן אתחול האפליקציה.
    לכן צריך להפעיל מחדש את Streamlit אחרי עדכון קובץ הלמידה.
    """)

    st.markdown("---")

    # FAQ
    st.markdown("## ❓ שאלות נפוצות")

    with st.expander("❓ למה הפידבק שלי נשלח למעבדה ולא אושר ישירות?"):
        st.markdown("""
        **סיבות אפשריות:**
        - דירוג ביניים (3) ללא הסבר מפורט
        - משוב קצר מדי (<20 תווים)
        - ציון actionability נמוך
        - קטגוריה "Other" עם משוב עמום

        **מה לעשות?**
        גש למעבדת השיפור ושפר את הפידבק עם השאלון המודרך.
        """)

    with st.expander("❓ מה ההבדל בין Confidence ל-Actionability?"):
        st.markdown("""
        - **Confidence (אמינות)**: עד כמה אפשר לסמוך על הפידבק? (בהתבסס על הקשר, עקביות, ספציפיות)
        - **Actionability (ניתן לפעולה)**: עד כמה ניתן ללמוד ממנו משהו קונקרטי? (בהתבסס על ניתוח LLM)

        **דוגמה:**
        - "לא טוב" = Confidence גבוה (אם עקבי) + Actionability נמוך (לא ברור מה לשנות)
        - "הפתיחה רשמית מדי, תתחיל ב-hook" = Confidence גבוה + Actionability גבוה
        """)

    with st.expander("❓ מה קורה אם אני לא משפר פידבק שבמעבדה?"):
        st.markdown("""
        **אחרי 7 ימים** הפידבק משתנה אוטומטית ל-`status='skipped'` (דולג).

        **למה?**
        - מונע הצטברות של פידבקים ישנים
        - שומר על המעבדה רלוונטית
        - פידבק שלא שופרו תוך שבוע כנראה לא רלוונטיים יותר

        **האם אפשר לשחזר?**
        כן, אפשר לשנות ידנית את הסטטוס בבסיס הנתונים (רק למפתחים).
        """)

    with st.expander("❓ איך דנה משתמשת בפידבק בפועל?"):
        st.markdown("""
        **תהליך הלמידה:**
        1. **בזמן ייצור תוכן** - דנה מחפשת בקובץ `Data/feedback_learnings_copywriter.txt`
        2. **RAG Search** - מוצאת דפוסים רלוונטיים (לפי פלטפורמה, ארכיטייפ, פרסונה)
        3. **יישום** - משלבת את הדפוסים בכתיבה

        **דוגמה:**
        - פידבק: "אל תשתמש במילה 'מהפכני' - תגיד 'חדשני'" (LinkedIn, Tone, ⭐⭐⭐⭐⭐)
        - נשמר כדפוס: "LinkedIn + Tone → נמנע מ-'מהפכני', משתמש ב-'חדשני'"
        - בייצור הבא: דנה רואה את הדפוס ונמנעת מהמילה 'מהפכני' בפוסטים ל-LinkedIn
        """)

    with st.expander("❓ האם אפשר למחוק פידבק?"):
        st.markdown("""
        **כרגע לא ישירות מהממשק.**

        אבל אפשר לשנות status ל-`discarded` (מושלך):
        ```python
        from core.feedback_manager import update_status
        update_status(feedback_id=123, new_status='discarded', notes='לא רלוונטי')
        ```

        פידבקים עם `status='discarded'` לא משתתפים בלמידה.
        """)

    st.markdown("---")

    # Footer
    st.markdown("## 🎓 סיכום")

    st.success("""
    **זכור את 3 העקרונות המרכזיים:**

    1. **ספציפיות > כמות** - פידבק איכותי אחד שווה יותר מ-10 עמומים
    2. **הסבר > דירוג** - משוב טקסטואלי עוזר יותר מסתם מספר
    3. **עקביות > שינויים** - דפוסים חוזרים עוזרים לדנה ללמוד

    **המטרה:** ללמד את דנה מה עובד עבורך ומה לא, בצורה ברורה וניתנת לפעולה.
    """)

    st.markdown("---")

    # Navigation
    col_back, col_lab = st.columns(2)

    with col_back:
        if st.button("← חזרה ל-Editor's Desk", use_container_width=True):
            st.switch_page("pages/3_✍️_Editors_Desk.py")

    with col_lab:
        if st.button("⚗️ מעבדת השיפור →", use_container_width=True, type="primary"):
            st.switch_page("pages/4_⚗️_Refinement_Lab.py")


if __name__ == "__main__":
    main()
