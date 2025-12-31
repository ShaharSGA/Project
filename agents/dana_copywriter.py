"""
Dana Copywriter Agent
Creates Hebrew marketing content in Dana's unique voice for social media platforms
"""

from crewai import Agent
from crewai_tools import BaseTool
from langchain_openai import ChatOpenAI
from config import AgentConfig


def create_dana_copywriter_agent(
    voice_tool: BaseTool,
    style_tool: BaseTool,
    platform_tool: BaseTool,
    archetype_tool: BaseTool,
    temperature: float = None,
    persona: str = None
) -> Agent:
    """
    Factory function to create Dana Copywriter agent with RAG tools.

    Args:
        voice_tool: ChromaDB search tool for Dana's voice examples
        style_tool: ChromaDB search tool for style guide and writing rules
        platform_tool: ChromaDB search tool for platform specifications
        archetype_tool: ChromaDB search tool for post archetype definitions
        temperature: Optional temperature override (persona-specific)
        persona: Optional persona name for customized behavior

    Returns:
        Agent configured with all necessary search tools
    """
    # Use provided temperature or default
    agent_temp = temperature if temperature is not None else AgentConfig.COPYWRITER_TEMPERATURE

    return Agent(
        role='Dana Copywriter',
        goal='Write 9 Hebrew social media posts based on the Campaign Bible.',
        backstory=f'''Hebrew copywriter in Dana's voice. Persona: {persona or "Professional Dana"}.
SEARCH tools before writing: "Dana voice", "platform specifications", "post archetypes".
Output: 9 posts (3 per platform), 100% Hebrew.''',
        tools=[voice_tool, style_tool, platform_tool, archetype_tool],
        llm=ChatOpenAI(
            model=AgentConfig.COPYWRITER_MODEL,
            temperature=agent_temp
        ),
        verbose=AgentConfig.COPYWRITER_VERBOSE,
        allow_delegation=AgentConfig.ALLOW_DELEGATION
    )