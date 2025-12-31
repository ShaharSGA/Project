from crewai import Task, Agent
from typing import Dict


def create_strategy_task(agent: Agent, inputs: Dict[str, str]) -> Task:
    """
    Create a strategic analysis task using RAG searches.

    Args:
        agent: The Strategy Architect agent
        inputs: Dictionary containing product, benefits, audience, offer, persona

    Returns:
        Task configured for strategic analysis with RAG
    """
    return Task(
        description=f"""
Create a Campaign Bible strategy document for this product:

**Product:** {inputs['product']}
**Benefits:** {inputs['benefits']}
**Audience:** {inputs['audience']}
**Offer:** {inputs['offer']}
**Persona:** {inputs['persona']}

**SEARCH FIRST** for Dana's methodology: "GAP Analysis", "ארכיטיפים", "פרוטוקול השקה"

**OUTPUT (Hebrew only):**
1. GAP Analysis (מצב נוכחי vs מצב רצוי)
2. Target Audience Profile
3. Core Message & Promise
4. Recommended Archetypes (Heart/Head/Hands)
5. Platform Strategy Notes

DO NOT write posts. Only strategic analysis for the copywriter.
""",
        expected_output="Campaign Bible in Hebrew: GAP analysis, audience profile, core message, archetype recommendations.",
        agent=agent
    )