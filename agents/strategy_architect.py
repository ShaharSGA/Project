"""
Strategy Architect Agent
Analyzes business data and creates strategic briefs using Dana's methodology
"""

from crewai import Agent
from crewai_tools import BaseTool
from langchain_openai import ChatOpenAI
from config import AgentConfig


def create_strategy_architect_agent(methodology_tool: BaseTool) -> Agent:
    """
    Factory function to create Strategy Architect agent with RAG tool.

    Args:
        methodology_tool: ChromaDB search tool for searching Dana's methodology

    Returns:
        Agent configured with methodology search capability
    """
    return Agent(
        role='Marketing Strategist',
        goal='Create a Campaign Bible strategy document in Hebrew.',
        backstory='''Expert strategist using Dana's methodology.
SEARCH your tool for "GAP Analysis" and "ארכיטיפים" before writing.
Output: Strategic analysis only, NO posts. 100% Hebrew.''',
        tools=[methodology_tool],
        llm=ChatOpenAI(
            model=AgentConfig.STRATEGY_MODEL,
            temperature=AgentConfig.STRATEGY_TEMPERATURE
        ),
        verbose=AgentConfig.STRATEGY_VERBOSE,
        allow_delegation=AgentConfig.ALLOW_DELEGATION
    )