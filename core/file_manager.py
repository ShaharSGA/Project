# -*- coding: utf-8 -*-
"""
File Manager Module
Handles saving generated content to markdown files
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Optional


def get_temperature_description_hebrew(temperature: float) -> str:
    """Get Hebrew description of temperature setting"""
    if temperature <= 0.3:
        return "שמרנית (יותר עקבי ומדויק)"
    elif temperature <= 0.5:
        return "מאוזנת (איזון בין דיוק ליצירתיות)"
    elif temperature <= 0.7:
        return "יצירתית (מגוון וספונטניות)"
    else:
        return "יצירתית מאוד (נועז ומפתיע)"


def save_markdown_output(
    product: str,
    persona: str,
    strategy_output: str,
    copy_output: str,
    execution_time: float,
    rag_summary: Dict,
    temperature: float,
    inputs: Dict,
    token_usage: Optional[Dict] = None
) -> str:
    """
    Save generated content to markdown file with metadata.

    Args:
        product: Product name
        persona: Selected persona
        strategy_output: Strategy architect output
        copy_output: Copywriter output
        execution_time: Total execution time in seconds
        rag_summary: RAG query summary
        temperature: Temperature setting
        inputs: Original campaign inputs
        token_usage: Optional token usage statistics

    Returns:
        Path to saved file
    """
    try:
        # Create outputs directory
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_product = "".join(c for c in product if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
        filename = f"{timestamp}_{safe_product}_{persona.replace(' ', '_')}.md"
        filepath = output_dir / filename

        # Get persona details
        persona_description = ""
        search_terms_display = ""

        # Get persona-specific search terms and description from config
        try:
            from config import PersonaConfig
            if persona in PersonaConfig.PERSONA_SEARCH_TERMS:
                terms = PersonaConfig.PERSONA_SEARCH_TERMS[persona]
                tone_terms = ', '.join(terms.get('tone', []))
                style_terms = ', '.join(terms.get('style', []))
                search_terms_display = f"""**מונחי חיפוש שנעשה שימוש בהם:**
- **טון (Tone):** {tone_terms}
- **סגנון (Style):** {style_terms}
"""

                # Get persona description
                persona_descriptions = {
                    "Professional Dana": "טון מקצועי וממוקד, דאטה-דריבן, מדגיש תועלות ועובדות, סגנון של מנהיגות מחשבתית (Thought Leadership)",
                    "Friendly Dana": "טון חברותי ושיחתי, קול של 'חברה הכי טובה', סיפורים אישיים, קז'ואל אבל מקצועי",
                    "Inspirational Dana": "מוטיבציה והעצמה, מסרים שאפתניים, חיבור רגשי, פוקוס על טרנספורמציה",
                    "Mentor Dana": "טון מנחה וחינוכי, עצות תומכות, גישה לימודית, מומחיות מטפחת"
                }
                persona_description = persona_descriptions.get(persona, "")
        except (ImportError, AttributeError, KeyError) as e:
            # ImportError: config module not available
            # AttributeError: PersonaConfig not in config
            # KeyError: persona not in PERSONA_SEARCH_TERMS
            pass

        # Format temperature
        temp_hebrew = get_temperature_description_hebrew(temperature)
        temperature_display = f"**רמת יצירתיות:** {temp_hebrew} (Temperature: {temperature})\n"

        # Format execution time
        minutes = int(execution_time // 60)
        seconds = execution_time % 60
        if minutes > 0:
            exec_time_display = f"**זמן ביצוע:** {minutes} דקות ו-{seconds:.1f} שניות ({execution_time:.1f} שניות סה\"כ)\n"
        else:
            exec_time_display = f"**זמן ביצוע:** {execution_time:.1f} שניות\n"

        # Format RAG summary
        rag_display = ""
        if rag_summary:
            total_queries = rag_summary.get('total_queries', 0)
            rag_display = f"**חיפושי RAG:** {total_queries}\n"

        # Format token usage
        token_display = ""
        if token_usage:
            # Handle both dict and UsageMetrics object
            if hasattr(token_usage, 'get'):
                # It's a dict
                total_tokens = token_usage.get('total_tokens', 0)
                prompt_tokens = token_usage.get('prompt_tokens', 0)
                completion_tokens = token_usage.get('completion_tokens', 0)
                total_cost = token_usage.get('total_cost_usd', 0)
            else:
                # It's a UsageMetrics object
                total_tokens = getattr(token_usage, 'total_tokens', 0)
                prompt_tokens = getattr(token_usage, 'prompt_tokens', 0)
                completion_tokens = getattr(token_usage, 'completion_tokens', 0)
                total_cost = getattr(token_usage, 'total_cost', 0)

            token_display = f"""**שימוש בטוקנים:**
- Input: {prompt_tokens:,}
- Output: {completion_tokens:,}
- סה"כ: {total_tokens:,}
- עלות: ${total_cost:.4f}

"""

        # Combined output (use copy_output as the main content)
        combined_output = copy_output if copy_output else "(no content generated)"

        # Format markdown content
        md_content = f"""# תוכן שיווקי - Dana's Brain

**נוצר בתאריך:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**מוצר:** {product}
**פרסונה:** {persona}

---

## 📊 מטא-נתונים על הפקת התוכן

{temperature_display}{exec_time_display}{rag_display}{token_display}**מספר פוסטים שנוצרו:** 9 (3 LinkedIn + 3 Facebook + 3 Instagram)
**מאגר ידע:** 5 קבצי ידע של דנה (מתודולוגיה, דוגמאות כתיבה, מפרט סגנון, מפרט פלטפורמות, ארכיטייפים)

---

## 🎯 אודות הפרסונה שנבחרה

**{persona}** - {persona_description}

{search_terms_display}
---

## 🎯 תקציר אסטרטגי (Campaign Bible)

{strategy_output}

---

## ✍️ פוסטים למדיה חברתית

{combined_output}

---

## 💡 הערות לשימוש

- **העתקה מהירה:** כל פוסט מסומן בפלטפורמה שלו (LinkedIn/Facebook/Instagram)
- **עריכה:** ניתן לערוך את הפוסטים בהתאם לצרכים ספציפיים
- **פרסום:** כל פוסט מותאם לפורמט ולטון של הפלטפורמה שלו

---

**🤖 נוצר על ידי Dana's Brain** - מערכת AI לייצור תוכן שיווקי
מופעל באמצעות Streamlit + CrewAI עם RAG (Retrieval-Augmented Generation)
"""

        # Write to file with UTF-8 encoding (for Hebrew)
        filepath.write_text(md_content, encoding='utf-8')

        return str(filepath)

    except Exception as e:
        raise Exception(f"Failed to save markdown file: {str(e)}")
