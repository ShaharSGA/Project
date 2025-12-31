from crewai import Task, Agent
from typing import Dict, Optional


def create_copywriting_task(
    agent: Agent,
    inputs: Dict[str, str],
    context_task: Optional[Task] = None
) -> Task:
    """
    Create a copywriting task using RAG searches for platform specs and voice.

    Args:
        agent: The Dana Copywriter agent
        inputs: Dictionary containing product, benefits, audience, offer, persona
        context_task: Strategy task that provides context (Campaign Bible)

    Returns:
        Task configured for content creation with RAG
    """
    return Task(
        description=f"""
Write 9 Hebrew social media posts based on the Campaign Bible.

**Persona:** {inputs['persona']}

**SEARCH ONCE at start:**
- "Dana voice" for tone examples
- "post archetypes" for Heart/Head/Hands structure

**FOR EACH PLATFORM, search its specs then write 3 posts:**
1. LinkedIn: Search "LinkedIn specifications" → write Heart, Head, Hands posts
2. Facebook: Search "Facebook specifications" → write Heart, Head, Hands posts
3. Instagram: Search "Instagram specifications" → write Heart, Head, Hands posts

**OUTPUT FORMAT (Hebrew):**
## LINKEDIN
### פוסט 1 (Heart) / ### פוסט 2 (Head) / ### פוסט 3 (Hands)
## FACEBOOK
### פוסט 1 (Heart) / ### פוסט 2 (Head) / ### פוסט 3 (Hands)
## INSTAGRAM
### פוסט 1 (Heart) / ### פוסט 2 (Head) / ### פוסט 3 (Hands)
""",
        expected_output="9 Hebrew posts: 3 per platform (LinkedIn, Facebook, Instagram), each with Heart/Head/Hands variants.",
        agent=agent,
        context=[context_task] if context_task else []
    )