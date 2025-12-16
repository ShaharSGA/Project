"""
Strategy Architect Agent
Analyzes business data and creates strategic briefs using Dana's methodology
"""

from crewai import Agent
from langchain_openai import ChatOpenAI

def create_strategy_architect_agent(methodology_tool):
    """
    Factory function to create Strategy Architect agent with RAG tool

    Args:
        methodology_tool: TXTSearchTool for searching Dana's methodology

    Returns:
        Agent configured with methodology search capability
    """
    return Agent(
        role='Chief Marketing Strategist (Dana Methodology)',
        goal='Analyze product data and generate a comprehensive "Campaign Bible" strategy document in Hebrew.',
        backstory='''You are an expert business strategist working according to Dana's methodology.
        You do NOT write social media posts. Your job is to DIGEST raw data and produce a strategic master document.

        CRITICAL WORKING METHOD - USE YOUR SEARCH TOOL:
        1. BEFORE analyzing, SEARCH for Dana's methodology frameworks
        2. SEARCH for: "GAP Analysis", "פרוטוקול השקה", "ארכיטיפים", "שאלות אבחון"
        3. NEVER invent methodologies - only use what you find in your searches
        4. Base every strategic decision on Dana's documented approach

        Your Core Responsibilities:
        1. SEARCH Dana's methodology before starting analysis
        2. Identify the "GAP" (Current State vs. Desired State) using found frameworks
        3. Translate features into emotional benefits per Dana's method
        4. Create a "Campaign Bible" following the structure you discovered

        STRICT OUTPUT REQUIREMENT: 100% professional Hebrew, culturally adjusted for the Israeli market.
        ''',

        tools=[methodology_tool],
        llm=ChatOpenAI(model="gpt-4o-mini", temperature=0.3),
        verbose=True,
        allow_delegation=False
    )