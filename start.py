# -*- coding: utf-8 -*-
"""
Dana's Brain - Autonomous Marketing AI Agents
Main Chainlit application with full UI implementation
Version: 1.1 - Enhanced with thread safety, timeouts, and validation
"""

import sys
import io
import chainlit as cl
from chainlit.input_widget import Select, TextInput
from crewai import Crew, Process
import os
import asyncio
import threading
import time
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional, Dict
from pydantic import ValidationError

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Load environment variables
load_dotenv()

# Import agent factory functions and task creators
from agents.strategy_architect import create_strategy_architect_agent
from agents.dana_copywriter import create_dana_copywriter_agent
from tasks.strategy_tasks import create_strategy_task
from tasks.copywriting_tasks import create_copywriting_task

# Import TXTSearchTool initialization
from tools.txt_search_tools import initialize_all_tools

# Import configuration and models
from config import ExecutionConfig, ChainlitConfig, AgentConfig
from models import CampaignInput, OutputMetadata
from datetime import datetime

# Initialize tools ONCE at startup (global state) with thread safety
TOOLS: Optional[Dict] = None
TOOLS_LOCK = threading.Lock()


@cl.on_chat_start
async def start():
    """Initialize chat with form inputs and tools (thread-safe)"""
    global TOOLS

    # Initialize TXTSearchTools on first run (with thread safety)
    if TOOLS is None:
        with TOOLS_LOCK:
            # Double-check after acquiring lock
            if TOOLS is None:
                await cl.Message(content="🔧 מאתחל כלי חיפוש במאגר הידע...").send()
                try:
                    TOOLS = await cl.make_async(initialize_all_tools)()
                    await cl.Message(content="✅ כלי החיפוש מוכנים! מאגר הידע הופעל בהצלחה.").send()

                except FileNotFoundError as e:
                    await cl.Message(content=str(e)).send()
                    return

                except UnicodeDecodeError as e:
                    await cl.Message(content=f"❌ **שגיאת קידוד קובץ**\n\n{e.reason}\n\n**המלצה:** שמרו את כל קבצי Data/ בקידוד UTF-8.").send()
                    return

                except RuntimeError as e:
                    await cl.Message(content=str(e)).send()
                    return

                except Exception as e:
                    await cl.Message(content=f"❌ **שגיאה בלתי צפויה**\n\n{str(e)}\n\n**המלצה:** בדקו את הלוגים או הפעילו מחדש את האפליקציה.").send()
                    return

    settings = await cl.ChatSettings([
        TextInput(
            id="product",
            label="Product Name / Service (Max 200 chars)",
            placeholder="Example: Lierac Hydragenist Serum",
            description="Product or service name (1-200 characters)"
        ),
        TextInput(
            id="benefits",
            label="Key Benefits (Max 1000 chars)",
            placeholder="Example: Deep hydration, instant glow, natural ingredients, clinically tested formula...",
            description="List the main benefits - be concise but thorough (10-1000 characters)"
        ),
        TextInput(
            id="audience",
            label="Target Audience (Max 500 chars)",
            placeholder="Example: Women 35-50, interested in anti-aging, skincare enthusiasts",
            description="Describe your target audience (5-500 characters)"
        ),
        TextInput(
            id="offer",
            label="The Offer (Max 300 chars)",
            placeholder="Example: 25% discount + free shipping on first order",
            description="Your promotional offer or call-to-action (1-300 characters)"
        ),
        Select(
            id="persona",
            label="Select Dana Persona",
            values=[
                "Professional Dana - Professional tone, data-driven, emphasizing benefits and facts, thought leadership style",
                "Friendly Dana - Warm conversational tone, 'best friend' voice, personal stories, casual yet expert",
                "Inspirational Dana - Motivational and empowering, aspirational messaging, emotional connection, transformative focus",
                "Mentor Dana - Guiding and educational tone, supportive advice, teaching approach, nurturing expertise"
            ],
            initial_value="Friendly Dana - Warm conversational tone, 'best friend' voice, personal stories, casual yet expert"
        )
    ]).send()

    cl.user_session.set("settings", settings)

    await cl.Message(content="""# 🧠 Welcome to "Dana's Brain" (RAG-Powered)

I'm an AI system that creates Hebrew marketing content in Dana's unique style.

## 📱 What I Create:

**9 Ready-to-Publish Posts:**
- 3 LinkedIn posts (professional & warm)
- 3 Facebook posts (personal & storytelling)
- 3 Instagram posts (short & catchy)

## 🚀 How It Works:

1. **Fill the form above** ↑ with your product details
2. **Choose a persona** - which Dana style suits you?
3. **Send any message** (e.g., "Let's start")
4. **Wait 2-3 minutes** - my agents are working with RAG search!

## ✨ What You'll Get:

✅ Strategic brief in Hebrew
✅ 9 posts tailored for each platform
✅ Transparent agent workflow
✅ **NEW:** Dynamic search through Dana's knowledge base
✅ **NEW:** Saved MD file in outputs/ folder

---

**Let's begin!** 💪""").send()


@cl.on_settings_update
async def update_settings(settings):
    """Update settings when user changes them"""
    cl.user_session.set("settings", settings)


def get_temperature_description_hebrew(temp: float) -> str:
    """Convert temperature value to user-friendly Hebrew description"""
    if temp <= 0.4:
        return "נמוכה (ממוקד ומדויק) 🎯"
    elif temp <= 0.6:
        return "בינונית (איזון בין דיוק ליצירתיות) ⚖️"
    elif temp <= 0.7:
        return "בינונית-גבוהה (יצירתי ומגוון) 🎨"
    else:
        return "גבוהה (מאוד יצירתי וחופשי) 🌈"


async def save_output_to_file(product, persona, content, strategy, temperature=None, execution_time=None):
    """
    Save the generated content to a markdown file with comprehensive metadata
    """
    try:
        # Create outputs directory if not exists
        output_dir = Path(__file__).parent / "outputs"
        output_dir.mkdir(exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_product = "".join(c for c in product if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
        filename = f"{timestamp}_{safe_product}_{persona.replace(' ', '_')}.md"
        filepath = output_dir / filename

        # Get persona details from config
        persona_description = ""
        search_terms_display = ""
        temperature_display = ""

        if temperature is not None:
            temp_hebrew = get_temperature_description_hebrew(temperature)
            temperature_display = f"**רמת יצירתיות:** {temp_hebrew} (Temperature: {temperature})\n"

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

                # Get persona description based on persona name
                persona_descriptions = {
                    "Professional Dana": "טון מקצועי וממוקד, דאטה-דריבן, מדגיש תועלות ועובדות, סגנון של מנהיגות מחשבתית (Thought Leadership)",
                    "Friendly Dana": "טון חברותי ושיחתי, קול של 'חברה הכי טובה', סיפורים אישיים, קז'ואל אבל מקצועי",
                    "Inspirational Dana": "מוטיבציה והעצמה, מסרים שאפתניים, חיבור רגשי, פוקוס על טרנספורמציה",
                    "Mentor Dana": "טון מנחה וחינוכי, עצות תומכות, גישה לימודית, מומחיות מטפחת"
                }
                persona_description = persona_descriptions.get(persona, "")
        except:
            pass

        # Format execution time
        exec_time_display = ""
        if execution_time:
            minutes = int(execution_time // 60)
            seconds = execution_time % 60
            if minutes > 0:
                exec_time_display = f"**זמן ביצוע:** {minutes} דקות ו-{seconds:.1f} שניות ({execution_time:.1f} שניות סה\"כ)\n"
            else:
                exec_time_display = f"**זמן ביצוע:** {execution_time:.1f} שניות\n"

        # Format markdown content with enhanced metadata
        md_content = f"""# תוכן שיווקי - Dana's Brain

**נוצר בתאריך:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**מוצר:** {product}
**פרסונה:** {persona}

---

## 📊 מטא-נתונים על הפקת התוכן

{temperature_display}{exec_time_display}**מספר פוסטים שנוצרו:** 9 (3 LinkedIn + 3 Facebook + 3 Instagram)
**מאגר ידע:** 5 קבצי ידע של דנה (מתודולוגיה, דוגמאות כתיבה, מפרט סגנון, מפרט פלטפורמות, ארכיטייפים)

---

## 🎯 אודות הפרסונה שנבחרה

**{persona}** - {persona_description}

{search_terms_display}
---

## 🎯 תקציר אסטרטגי (Campaign Bible)

{strategy}

---

## ✍️ פוסטים למדיה חברתית

{content}

---

## 💡 הערות לשימוש

- **העתקה מהירה:** כל פוסט מסומן בפלטפורמה שלו (LinkedIn/Facebook/Instagram)
- **עריכה:** ניתן לערוך את הפוסטים בהתאם לצרכים ספציפיים
- **פרסום:** כל פוסט מותאם לפורמט ולטון של הפלטפורמה שלו

---

**🤖 נוצר על ידי Dana's Brain** - מערכת AI לייצור תוכן שיווקי
מופעל באמצעות Chainlit + CrewAI עם RAG (Retrieval-Augmented Generation)
"""

        # Write to file with UTF-8 encoding (for Hebrew)
        filepath.write_text(md_content, encoding='utf-8')

        await cl.Message(content=f"💾 **הקובץ נשמר:** `{filepath}`").send()
        return filename

    except Exception as e:
        await cl.Message(content=f"⚠️ לא ניתן לשמור את הקובץ: {str(e)}").send()
        return None


@cl.on_message
async def main(message: cl.Message):
    """Process user request with CrewAI (with validation and timeout)"""
    settings = cl.user_session.get("settings")

    # Extract inputs
    product = settings.get("product", "").strip()
    benefits = settings.get("benefits", "").strip()
    audience = settings.get("audience", "").strip()
    offer = settings.get("offer", "").strip()
    persona_full = settings.get("persona", "Friendly Dana - Warm conversational tone, 'best friend' voice, personal stories, casual yet expert")

    # Extract just the persona name (before the dash)
    persona = persona_full.split(" - ")[0] if " - " in persona_full else persona_full

    # Validate inputs with Pydantic
    try:
        validated_input = CampaignInput(
            product=product,
            benefits=benefits,
            audience=audience,
            offer=offer,
            persona=persona
        )
        # Use validated data
        inputs = validated_input.to_dict()

    except ValidationError as e:
        # Format validation errors for user with helpful details
        error_messages = []
        for error in e.errors():
            field = error['loc'][0]
            msg = error['msg']

            # Add character count for string length errors
            if field in ['product', 'benefits', 'audience', 'offer']:
                current_value = settings.get(field, "")
                char_count = len(current_value)

                # Character limits
                limits = {
                    'product': 200,
                    'benefits': 1000,
                    'audience': 500,
                    'offer': 300
                }

                if 'at most' in msg or 'at least' in msg:
                    error_messages.append(f"- **{field}**: {msg}\n  → Current: {char_count} characters (Limit: {limits.get(field, '?')} chars)")
                else:
                    error_messages.append(f"- **{field}**: {msg}")
            else:
                error_messages.append(f"- **{field}**: {msg}")

        await cl.Message(content=f"""❌ **Input Validation Error**

Please fix the following issues:

{chr(10).join(error_messages)}

**Then send another message to continue.**""").send()
        return

    except Exception as e:
        await cl.Message(content=f"""❌ **Validation Error**

{str(e)}

Please check all form fields and try again.""").send()
        return

    # Show loading message with persona details
    persona_temp = AgentConfig.PERSONA_TEMPERATURES.get(persona, AgentConfig.COPYWRITER_TEMPERATURE)
    temp_description = get_temperature_description_hebrew(persona_temp)

    msg = cl.Message(content=f"""🔄 **צוות דנה התחיל לעבוד!**

**מוצר:** {inputs['product']}
**קהל יעד:** {inputs['audience']}
**פרסונה:** {inputs['persona']}
**רמת יצירתיות:** {temp_description}

⏳ התהליך עשוי לקחת 2-3 דקות...

**מה קורה עכשיו:**
1. 🎯 האסטרטג מחפש במתודולוגיה ומנתח את נתוני המוצר
2. 🔍 חיפושי RAG ימצאו דוגמאות רלוונטיות ממאגר הידע של דנה
3. ✍️ דנה כותבת 9 פוסטים מותאמים בסגנון {inputs['persona']}
4. 🎨 מתאימה את התוכן לכל פלטפורמה (LinkedIn, Facebook, Instagram)

**שקיפות חיפוש:**
- חיפוש מתודולוגיה עבור מסגרות אסטרטגיות
- חיפוש דוגמאות כתיבה עבור טון {inputs['persona']}
- חיפוש מפרטי פלטפורמה עבור כללי עיצוב
- חיפוש ארכיטייפים עבור מבני Heart/Head/Hands

אנא המתינו...""")
    await msg.send()

    # Send search transparency update
    await cl.Message(content="""🔍 **פעילות חיפוש דינמית:**

הסוכנים מחפשים כעת באופן דינמי ב:
- 📚 Dana_Brain_Methodology.txt (12KB - מסגרות אסטרטגיות)
- 📚 Dana_Voice_Examples_Lierac.txt (27KB - דוגמאות כתיבה)
- 📚 style_guide_customer_Lierac.txt (6KB - כללי עיצוב)
- 📚 platform_specifications.txt (6KB - מפרטי LinkedIn/FB/IG)
- 📚 post_archetypes.txt (9KB - מסגרת Heart/Head/Hands)

זהו RAG (Retrieval-Augmented Generation) בפעולה - ללא הנחיות קבועות, רק חיפושים דינמיים!""").send()

    # Ensure tools initialized before agent creation
    global TOOLS
    if TOOLS is None:
        await cl.Message(content="❌ הכלים לא אותחלו. אנא הפעילו מחדש את הצ'אט.").send()
        return

    strategy_architect = create_strategy_architect_agent(
        methodology_tool=TOOLS["methodology"]
    )

    # Get persona-specific temperature
    persona_temp = AgentConfig.PERSONA_TEMPERATURES.get(
        persona,
        AgentConfig.COPYWRITER_TEMPERATURE
    )

    dana_copywriter = create_dana_copywriter_agent(
        voice_tool=TOOLS["voice_examples"],
        style_tool=TOOLS["style_guide"],
        platform_tool=TOOLS["platform_specs"],
        archetype_tool=TOOLS["post_archetypes"],
        temperature=persona_temp,
        persona=persona
    )

    # Create tasks - agents will use RAG tools to search for relevant information
    strategy_task = create_strategy_task(strategy_architect, inputs)
    copywriting_task = create_copywriting_task(
        dana_copywriter,
        inputs,
        strategy_task
    )

    # Define synchronous crew execution function
    def run_crew():
        """Create and run the marketing crew"""
        try:
            # Assemble crew
            crew = Crew(
                agents=[strategy_architect, dana_copywriter],
                tasks=[strategy_task, copywriting_task],
                process=Process.sequential,
                verbose=False  # Reduced verbosity - RAG search happens in background
            )

            # Execute crew
            result = crew.kickoff(inputs=inputs)
            return result
        except Exception as e:
            raise Exception(f"Error running crew: {str(e)}")

    try:
        # Run crew asynchronously with timeout (CRITICAL: wrap sync function with cl.make_async)
        start_time = time.time()

        result = await asyncio.wait_for(
            cl.make_async(run_crew)(),
            timeout=ExecutionConfig.CREW_TIMEOUT
        )

        execution_time = time.time() - start_time

        # Extract per-task outputs for transparency
        task_outputs = getattr(result, "tasks_output", []) or []

        def safe_attr(obj, names, default=""):
            for name in names:
                if hasattr(obj, name):
                    val = getattr(obj, name)
                    if val:
                        return val
            return default

        # Map task outputs by agent role for easier display
        agent_outputs = {}
        for t in task_outputs:
            agent_name = safe_attr(t, ["agent_role", "agent_name"])
            if not agent_name and hasattr(t, "agent") and hasattr(t.agent, "role"):
                agent_name = t.agent.role
            agent_name = agent_name or "Task"

            agent_outputs[agent_name] = {
                "task_description": safe_attr(t, ["description", "task_description"]),
                "output": safe_attr(t, ["output", "raw", "result", "final_answer"], default="(no output captured)")
            }

        # Fallback: pull outputs directly from task objects if tasks_output is empty
        def first_non_empty(*vals):
            for v in vals:
                if v:
                    return v
            return "(no output captured)"

        def get_result_payload(res):
            """Prefer the fields that contain the crew final answer."""
            for attr in ("raw", "output", "result", "final_answer", "text"):
                if hasattr(res, attr):
                    val = getattr(res, attr)
                    if val:
                        return val
            return None

        strategy_output = first_non_empty(
            agent_outputs.get(strategy_architect.role, {}).get("output"),
            getattr(strategy_task, "output", None)
        )
        result_payload = get_result_payload(result)

        # Keep copy_output focused on the copywriting task only
        copy_output = first_non_empty(
            agent_outputs.get(dana_copywriter.role, {}).get("output"),
            getattr(copywriting_task, "output", None)
        )

        # Combined output prefers overall crew payload, then copy, then task output
        final_combined_output = first_non_empty(
            result_payload,
            copy_output,
            getattr(copywriting_task, "output", None)
        )

        # Save output to MD file with metadata
        filename = await save_output_to_file(
            inputs['product'],
            inputs['persona'],
            final_combined_output,
            strategy_output,
            temperature=persona_temp,
            execution_time=execution_time
        )

        # Quick success confirmation message
        temp_hebrew = get_temperature_description_hebrew(persona_temp)
        await cl.Message(content=f"""✅ **הצלחה! התוכן הושלם בהצלחה**

📝 **נוצרו 9 פוסטים:**
- 3 פוסטים LinkedIn (מקצועי וממוקד)
- 3 פוסטים Facebook (אישי ומעניין)
- 3 פוסטים Instagram (קצר ותמציתי)

🎨 **פרסונה:** {inputs['persona']}
🌡️ **רמת יצירתיות:** {temp_hebrew}

💾 **הקובץ נשמר:** `{filename if filename else 'outputs/[filename].md'}`
⏱️ **זמן ביצוע:** {execution_time:.1f} שניות

---

**⬇️ מטה תמצאו את הפרטים המלאים**""").send()

        # Simplified output display with full content in MD file
        output = f"""# 📄 תוכן מלא

## ✍️ תוכן סופי - 9 פוסטים
{final_combined_output}

---

## 🎯 תקציר אסטרטגי
{strategy_output[:500]}...

*[התקציר המלא נמצא בקובץ MD]*

---

## 📊 סיכום ביצוע

**מוצר:** {inputs['product']}
**פרסונה:** {inputs['persona']}
**זמן ביצוע:** {execution_time:.1f} שניות

**מה קרה:**
1. ✅ האסטרטג ניתח את המוצר ויצר תקציר אסטרטגי
2. ✅ דנה כתבה 9 פוסטים מותאמים (3 LinkedIn, 3 Facebook, 3 Instagram)
3. ✅ כל פוסט הותאם לפלטפורמה ולטון המבוקש

**כלים שנעשה בהם שימוש:**
- 📚 מתודולוגיה של דנה
- 📚 דוגמאות כתיבה
- 📚 מפרט סגנון
- 📚 מפרטי פלטפורמות
- 📚 ארכיטייפים (Heart/Head/Hands)

---

## 💡 שימוש בתוכן

**קובץ MD מלא:** `{filename if filename else 'outputs/[filename].md'}`
הקובץ כולל את כל הפרטים הטכניים, מטא-נתונים, והסבר מפורט על הפרסונה.

---

## 🎉 סיימנו! התוכן מוכן לשימוש

**מה לעשות עכשיו:**
1. עברו על התוכן למעלה ↑
2. העתיקו את הפוסטים שאתם אוהבים
3. פרסמו בפלטפורמות הרלוונטיות
4. **בדקו את קובץ MD השמור בתיקיית outputs/**

💡 **טיפ:** שלחו הודעה נוספת עם נתונים שונים כדי לקבל עוד תוכן!"""

        msg.content = output
        await msg.update()

    except asyncio.TimeoutError:
        # Timeout-specific error handling
        error_msg = f"""❌ **תם הזמן המוקצב**

ייצור התוכן ארך יותר מ-{ExecutionConfig.CREW_TIMEOUT} שניות והופסק.

---

## 💡 סיבות אפשריות:

1. **API של OpenAI איטי** - נסו שוב בעוד כמה רגעים
2. **בקשה מורכבת** - נסו לפשט את הקלט
3. **בעיות רשת** - בדקו את חיבור האינטרנט

---

**המלצה:** המתינו רגע ונסו שוב. אם הבעיה נמשכת, ייתכן שהמערכת חווה עומס גבוה."""

        msg.content = error_msg
        await msg.update()

    except Exception as e:
        # Error handling with clear messages
        error_details = str(e)
        error_msg = f"""❌ **System Error**

**Error details:**
{error_details}

---

## 🔍 Recommended Checks:

1. **Check API Key:**
   - Open the `.env` file
   - Verify `OPENAI_API_KEY` is set correctly
   - Format: `OPENAI_API_KEY=sk-...`

2. **Check Data files:**
   - Dana_Brain_Methodology.txt
   - Dana_Voice_Examples_Lierac.txt
   - style_guide_customer_Lierac.txt
   - platform_specifications.txt
   - post_archetypes.txt

3. **Check internet connection**

---

**Need help?** Try again or check the logs for more info."""

        msg.content = error_msg
        await msg.update()


if __name__ == "__main__":
    from chainlit.cli import run_chainlit
    run_chainlit(__file__)
