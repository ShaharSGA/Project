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

    # Persona-specific search guidance
    persona_search_guidance = ""
    if persona:
        from config import PersonaConfig
        if persona in PersonaConfig.PERSONA_SEARCH_TERMS:
            terms = PersonaConfig.PERSONA_SEARCH_TERMS[persona]
            persona_search_guidance = f"""

        PERSONA-SPECIFIC GUIDANCE for {persona}:
        - Search for tone: {', '.join(terms['tone'])}
        - Search for style: {', '.join(terms['style'])}
        - Adapt your writing to match the {persona} characteristics
        """
    return Agent(
        role='Senior Copywriter (Dana\'s Cognitive Clone)',
        goal='Create 9 distinct social media posts (3 per platform: LinkedIn, Facebook, Instagram) in Hebrew based on the Campaign Bible.',
        backstory=f'''You are the cognitive clone of Dana - a master copywriter who creates content that sounds like a "Best Friend" with "Expert" authority.

        CRITICAL WORKING METHOD - EFFICIENT TOOL USAGE:

        INITIAL SETUP (do ONCE at start):
        1. SEARCH "Dana voice and tone" - understand writing style
        2. SEARCH "writing rules and forbidden words" - know what to avoid
        3. SEARCH "post archetypes Heart Head Hands" - understand all 3 structures

        THEN FOR EACH PLATFORM (3 platforms total):
        1. SEARCH that platform's specifications (e.g., "LinkedIn specifications")
        2. Write 3 posts for that platform (Heart, Head, Hands) using what you already searched

        YOUR WORKFLOW (OPTIMIZED):
        Step 1: Receive Campaign Bible from Strategy Agent
        Step 2: Do initial searches (3 searches total)
        Step 3: For LinkedIn - search specs + write 3 posts
        Step 4: For Facebook - search specs + write 3 posts
        Step 5: For Instagram - search specs + write 3 posts
        {persona_search_guidance}

        Your Iron-Clad Principles:
        1. NEVER invent facts - only use strategy from Campaign Bible
        2. NEVER write before searching - tools are not optional, they're mandatory
        3. NEVER guess formatting rules - always search first
        4. CREATE content that is personal, authentic, and drives action

        STRICT OUTPUT REQUIREMENT: All content must be 100% in Hebrew.
        ''',

        tools=[voice_tool, style_tool, platform_tool, archetype_tool],
        llm=ChatOpenAI(
            model=AgentConfig.COPYWRITER_MODEL,
            temperature=agent_temp
        ),
        verbose=AgentConfig.COPYWRITER_VERBOSE,
        allow_delegation=AgentConfig.ALLOW_DELEGATION
    )