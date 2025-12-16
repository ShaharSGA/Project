from crewai import Task

def create_copywriting_task(agent, inputs, context_task):
    """
    Create a copywriting task that combines strict platform rules with strategic content pillars.
    Uses RAG tools to search for voice examples and style guide.
    """
    return Task(
        description=f"""
You are an expert copywriter creating content for the Israeli market.
Based on the Strategy Campaign Bible provided, create **9 distinct social media posts** in HEBREW.

**Target Persona:** {inputs['persona']}
**Goal:** Create 3 posts for LinkedIn, 3 for Facebook, and 3 for Instagram.

**IMPORTANT: USE YOUR SEARCH TOOLS** to find Dana's voice and style:
1. Search for "פתיחים" or "היי גורג'ס" or "היי אהובה" to find opening hook examples
2. Search for "כללי כתיבה" or "מבנה פוסט" to find writing rules
3. Search for "מילים אסורות" to find words to avoid
4. Search for "אימוג'ים" to find emoji usage rules
5. Search for "טון הדיבור" to understand the voice tone

---

### CONTENT STRATEGY (Apply this to ALL platforms)
For each platform, you must write 3 specific types of posts:
1.  **OPTION 1: THE EMOTIONAL POST (Heart)**
    * Focus: Pain points, empathy, vulnerability, "Best Friend" tone.
    * Goal: Create connection and trust.
2.  **OPTION 2: THE EXPERT POST (Head)**
    * Focus: Simplified science, proof, authority, educational value.
    * Goal: Establish authority and credibility.
3.  **OPTION 3: THE SALES POST (Hands)**
    * Focus: The Offer, Urgency (FOMO), Clear Benefit.
    * Goal: Drive action/sales.

---

### PLATFORM RULES & SPECS

#### 1. LINKEDIN (Professional & Thought Leadership)
* **Length:** 150-200 words.
* **Tone:** Professional yet warm.
* **Structure:** Insight/Stat -> Personal Story -> Practical Value -> Professional CTA.
* **Formatting:** Double spacing between paragraphs. 1 emoji max.
* **Output:** 3 Posts (Heart, Head, Hands).

#### 2. FACEBOOK (Community & Storytelling)
* **Length:** 100-150 words.
* **Tone:** Conversational, authentic, "Coffee with a friend".
* **Structure:** Hook (Question) -> Body (Story) -> Value -> Soft CTA ("Tell me in comments...").
* **Formatting:** Short lines (1-3 lines per block).
* **Allowed Emojis:** Only use ✅ 💬 🎁.
* **Output:** 3 Posts (Heart, Head, Hands).

#### 3. INSTAGRAM (Visual & Punchy)
* **Length:** 50-80 words (Short Caption).
* **Tone:** High energy, inspirational.
* **Structure:** Strong Hook (first 2 lines must sell!) -> One Core Point -> Clear CTA ("Save this").
* **Formatting:** Very short lines.
* **Output:** 3 Posts (Heart, Head, Hands).

---

### CRITICAL INSTRUCTIONS
1.  **LANGUAGE:** The final output (the posts) must be **100% in HEBREW**. Do not use English in the posts.
2.  **VOICE:** Use your search tools to find Dana's voice examples and match her unique style.
3.  **FORMAT:** Strict adherence to the word counts and formatting rules above.
""",

        expected_output="""
# FINAL CONTENT OUTPUT (All in Hebrew)

## LINKEDIN SERIES
### Post 1 (Emotional/Heart)
[Hebrew Content: 150-200 words]
**CTA:** [Hebrew CTA]
**Hashtags:** #tag1 #tag2

### Post 2 (Expert/Head)
[Hebrew Content: 150-200 words]
**CTA:** [Hebrew CTA]
**Hashtags:** #tag1 #tag2

### Post 3 (Sales/Hands)
[Hebrew Content: 150-200 words]
**CTA:** [Hebrew CTA]
**Hashtags:** #tag1 #tag2

---

## FACEBOOK SERIES
### Post 1 (Emotional/Heart)
[Hebrew Content: 100-150 words]
**CTA:** [Hebrew CTA]

### Post 2 (Expert/Head)
[Hebrew Content: 100-150 words]
**CTA:** [Hebrew CTA]

### Post 3 (Sales/Hands)
[Hebrew Content: 100-150 words]
**CTA:** [Hebrew CTA]

---

## INSTAGRAM SERIES
### Post 1 (Emotional/Heart)
[Hebrew Content: 50-80 words]
**CTA:** [Hebrew CTA]

### Post 2 (Expert/Head)
[Hebrew Content: 50-80 words]
**CTA:** [Hebrew CTA]

### Post 3 (Sales/Hands)
[Hebrew Content: 50-80 words]
**CTA:** [Hebrew CTA]
""",
        agent=agent,
        context=[context_task] if context_task else []
    )