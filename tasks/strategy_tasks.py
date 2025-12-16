from crewai import Task

def create_strategy_task(agent, inputs):
    """
    Create a strategic analysis task with English instructions but Hebrew output.
    Uses RAG tool to search for relevant methodology information.
    """
    return Task(
        description=f"""
Analyze the following raw product data:
Product Name: {inputs['product']}
Key Benefits: {inputs['benefits']}
Target Audience: {inputs['audience']}
The Offer: {inputs['offer']}
Selected Persona: {inputs['persona']}

**IMPORTANT: USE YOUR SEARCH TOOL** to find relevant methodology and frameworks from Dana's knowledge base.
Search for:
- "שאלות אבחון" (diagnostic questions)
- "GAP Analysis" (gap analysis methodology)
- "פרוטוקול השקה" (launch protocol)
- "ארכיטיפים" (post archetypes)

Based on your search results, create a comprehensive 'Campaign Bible' document.

STRICT LANGUAGE REQUIREMENT: The final output must be written 100% in HEBREW. Do not use English in the final response.

The document must follow this exact structure:

PART A: THE DEEP DIVE (Business Analysis)
- **Product Philosophy**: Why does this exist? What is the 'Magic' or unique value?
- **Simplified Science**: Explain the technology/method simply (how the benefits serve the audience).
- **Sensory Experience**: How does it feel/smell/look?

PART B: STRATEGIC LENS (Gaps & Psychology)
- **The Gap**: Define the customer's current pain vs. the relief this product offers.
- **Buying Barriers**: What is the main objection or hesitation preventing the purchase? (Crucial).
- **Psychological Trigger**: What is the main emotion? (FOMO, Relief, Pride?).

PART C: CREATIVE TOOLKIT (Ingredients for the Copywriter)
- **Hooks Bank**: Provide 3 different opening lines (Emotional, Rational, Sales-focused).
- **Storytelling Angles**: Suggest 2-3 specific stories, analogies, or examples that demonstrate the value.
- **Feature-to-Benefit Table**: Translate 3 key features into "Dana-style" deep benefits.
- **The Offer Framing**: How to present the price/gift to make it irresistible.

PART D: PLATFORM STRATEGY (Tailored Insights)
- **LinkedIn**: Specific tone instructions and content focus for professional framing.
- **Facebook**: Recommendations for community-oriented or engagement-focused content.
- **Instagram**: Visual angles and lifestyle messaging recommendations.
""",
        expected_output="""A fully structured 'Campaign Bible' document in Hebrew, containing:
1. Deep Dive (Philosophy, Science, Senses)
2. Strategic Lens (Gap, Barriers, Triggers)
3. Creative Toolkit (Hooks, Stories, Benefits)
4. Platform Strategy (LinkedIn, FB, Insta)""",
        agent=agent
    )