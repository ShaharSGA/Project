from crewai import Task, Agent
from typing import Dict, Optional


def create_copywriting_task(
    agent: Agent,
    inputs: Dict[str, str],
    context_task: Optional[Task] = None
) -> Task:
    """
    Create a copywriting task that relies entirely on RAG searches.
    The agent must search for platform specs, archetypes, voice examples, and style rules.

    Args:
        agent: The Dana Copywriter agent
        inputs: Dictionary containing product, benefits, audience, offer, persona
        context_task: Strategy task that provides context (Campaign Bible)

    Returns:
        Task configured for content creation with RAG
    """
    return Task(
        description=f"""
Create 9 social media posts in Hebrew based on the Campaign Bible from the strategy agent.

**Assignment:**
- Target Persona: {inputs['persona']}
- Platforms: LinkedIn (3 posts), Facebook (3 posts), Instagram (3 posts)
- Post Types: Each platform needs Heart (Emotional), Head (Expert), Hands (Sales)

**CRITICAL - EXTENSIVE SEARCHING REQUIRED:**

You have 4 search tools. You MUST use them before writing each post:

**For EVERY post, search in this order:**
1. **Platform specifications:** Search "LinkedIn specifications" / "Facebook specifications" / "Instagram specifications"
   - Find: word count, tone, structure, formatting rules
2. **Post archetype:** Search "Heart archetype" / "Head archetype" / "Hands archetype"
   - Find: purpose, focus, triggers, structure for that post type
3. **Dana's voice:** Search "פתיחים" / "טון דיבור" / "היי גורג'ס"
   - Find: opening hooks, voice patterns, authentic examples
4. **Writing rules:** Search "כללי כתיבה" / "אימוג'ים" / "מילים אסורות"
   - Find: formatting rules, emoji usage, forbidden words

**YOUR WORKFLOW (Repeat 9 times - once per post):**
Step 1: Decide which post you're writing (e.g., "LinkedIn Heart")
Step 2: Search platform specifications for that platform
Step 3: Search post archetype for that type (Heart/Head/Hands)
Step 4: Search Dana's voice examples
Step 5: Search writing and formatting rules
Step 6: ONLY NOW write the post using all the information you found
Step 7: Move to next post

**IRON-CLAD RULES:**
- NEVER write before searching
- NEVER guess platform specs - always search
- NEVER invent Dana's voice - find examples
- ALWAYS follow word counts from your searches
- ALL output must be 100% Hebrew

This is not optional. Search -> Understand -> Write (in that order, every time).
""",

        expected_output="""
# תוכן סופי (All in Hebrew)

## סדרת LINKEDIN
### פוסט 1 (Heart - רגשי)
[תוכן בעברית לפי המפרטים שנמצאו]

### פוסט 2 (Head - מומחה)
[תוכן בעברית לפי המפרטים שנמצאו]

### פוסט 3 (Hands - מכירתי)
[תוכן בעברית לפי המפרטים שנמצאו]

---

## סדרת FACEBOOK
### פוסט 1 (Heart - רגשי)
[תוכן בעברית לפי המפרטים שנמצאו]

### פוסט 2 (Head - מומחה)
[תוכן בעברית לפי המפרטים שנמצאו]

### פוסט 3 (Hands - מכירתי)
[תוכן בעברית לפי המפרטים שנמצאו]

---

## סדרת INSTAGRAM
### פוסט 1 (Heart - רגשי)
[תוכן בעברית לפי המפרטים שנמצאו]

### פוסט 2 (Head - מומחה)
[תוכן בעברית לפי המפרטים שנמצאו]

### פוסט 3 (Hands - מכירתי)
[תוכן בעברית לפי המפרטים שנמצאו]
""",
        agent=agent,
        context=[context_task] if context_task else []
    )