"""
Dana Copywriter Agent
Creates Hebrew marketing content in Dana's unique voice for social media platforms
"""

from crewai import Agent
from crewai_tools import TXTSearchTool
from langchain_openai import ChatOpenAI
from config import AgentConfig


def create_dana_copywriter_agent(
    voice_tool: TXTSearchTool,
    style_tool: TXTSearchTool,
    platform_tool: TXTSearchTool,
    archetype_tool: TXTSearchTool,
    temperature: float = None,
    persona: str = None
) -> Agent:
    """
    Factory function to create Dana Copywriter agent with RAG tools.

    Args:
        voice_tool: TXTSearchTool for Dana's voice examples
        style_tool: TXTSearchTool for style guide and writing rules
        platform_tool: TXTSearchTool for platform specifications
        archetype_tool: TXTSearchTool for post archetype definitions
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

        CRITICAL WORKING METHOD - EXTENSIVE TOOL USAGE REQUIRED:

        BEFORE writing ANY post, you MUST search for:
        1. Platform specifications (word count, tone, formatting) - use your platform tool
        2. Post archetype structure (Heart/Head/Hands) - use your archetype tool
        3. Dana's voice examples matching that style - use your voice tool
        4. Writing rules and forbidden words - use your style guide tool

        YOUR WORKFLOW (MANDATORY):
        Step 1: Receive Campaign Bible from Strategy Agent
        Step 2: For each post you're about to write:
           a. SEARCH platform specifications (e.g., "LinkedIn specifications")
           b. SEARCH post archetype (e.g., "Heart archetype" or "Head archetype")
           c. SEARCH Dana's voice examples (e.g., "פתיחים" or "טון דיבור")
           d. SEARCH writing rules (e.g., "אימוג'ים" or "מילים אסורות")
        Step 3: ONLY THEN write the post using what you found
        Step 4: Repeat for all 9 posts (3 platforms × 3 archetypes)
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