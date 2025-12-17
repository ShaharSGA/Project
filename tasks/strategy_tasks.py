from crewai import Task, Agent
from typing import Dict


def create_strategy_task(agent: Agent, inputs: Dict[str, str]) -> Task:
    """
    Create a strategic analysis task that relies entirely on RAG searches.
    The agent must search for methodology and structure - nothing is hardcoded.

    Args:
        agent: The Strategy Architect agent
        inputs: Dictionary containing product, benefits, audience, offer, persona

    Returns:
        Task configured for strategic analysis with RAG
    """
    return Task(
        description=f"""
Analyze this product data and create a comprehensive 'Campaign Bible' strategy document:

**Product Data:**
- Product Name: {inputs['product']}
- Key Benefits: {inputs['benefits']}
- Target Audience: {inputs['audience']}
- The Offer: {inputs['offer']}
- Selected Persona: {inputs['persona']}

**YOUR TASK:**
Create a strategic "Campaign Bible" document that will guide the copywriter.

**MANDATORY - SEARCH FIRST:**
Before writing anything, USE YOUR SEARCH TOOL to find:
1. Dana's strategic frameworks: Search "שאלות אבחון", "GAP Analysis", "פרוטוקול השקה"
2. Campaign structure methodology: Search "מבנה מסע פרסום", "ארכיטיפים"
3. Feature-to-benefit translation method: Search "תרגום פיצ'רים לתועלות"
4. Platform strategy guidelines: Search "אסטרטגיה לפלטפורמות"

**WORKFLOW:**
1. SEARCH for Dana's methodology documents
2. UNDERSTAND the frameworks you found
3. APPLY those frameworks to analyze the product data
4. CREATE the Campaign Bible following the structure you discovered

**OUTPUT REQUIREMENTS:**
- Language: 100% Hebrew (עברית)
- Structure: Follow the Campaign Bible format found in your searches
- Content: Based on product data + Dana's methodology
- Purpose: Provide strategic foundation for the copywriter agent

NEVER invent methodologies - only use what you find through searches.
""",
        expected_output="""A comprehensive 'Campaign Bible' document in Hebrew following Dana's methodology structure discovered through searches. Should include strategic analysis, gap identification, creative toolkit, and platform-specific recommendations.""",
        agent=agent
    )