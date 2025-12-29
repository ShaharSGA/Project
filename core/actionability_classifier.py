"""
Actionability Classifier - LLM-Based Feedback Quality Assessment

This module uses an LLM to determine if feedback is actionable (specific and useful)
or vague (needs refinement in the Lab).

Replaces the naive word-count heuristic with semantic analysis.

Part of the Refinement Lab system for Dana's Brain.
"""

import os
from openai import OpenAI
from typing import Tuple

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")


def classify_feedback_actionability(
    feedback_text: str,
    category: str,
    rating: int
) -> Tuple[bool, float, str]:
    """
    Classify if feedback is actionable using LLM semantic analysis

    Actionable feedback contains:
    - Specific critique (mentions exact words, phrases, or elements)
    - Platform-specific issues (e.g., "too long for Instagram")
    - Structural problems (e.g., "missing hook", "weak CTA")
    - Clear alternatives or suggestions

    Vague feedback is general, emotional, or unclear:
    - "זה לא טוב" (this is bad)
    - "לא אהבתי" (didn't like it)
    - "משהו לא בסדר" (something's wrong)

    Args:
        feedback_text: The user's feedback text
        category: Feedback category (Tone, Message, etc.)
        rating: User's rating (1-5)

    Returns:
        Tuple of:
        - is_actionable (bool): True if feedback is specific enough
        - confidence_score (float): 0.0-1.0 confidence in classification
        - reason (str): Short explanation (for debugging)

    Examples:
        >>> classify_feedback_actionability("חסר הוק", "Structure", 2)
        (True, 0.95, "Specific element mentioned: hook")

        >>> classify_feedback_actionability("זה לא טוב", "Tone", 2)
        (False, 0.85, "Vague - no specific critique")
    """

    if not feedback_text or not feedback_text.strip():
        # Empty feedback has zero actionability - cannot learn from it
        return (False, 0.0, "Empty feedback")

    # If feedback is very short (< 2 words), it's probably vague
    word_count = len(feedback_text.split())
    if word_count < 2:
        # Very short feedback has very low actionability
        return (False, 0.1, "Too short - likely vague")

    # Build classification prompt
    prompt = f"""
Analyze this feedback for ACTIONABILITY.

Context:
- Category: {category}
- Rating: {rating}/5
- Feedback: "{feedback_text}"

ACTIONABLE feedback contains at least ONE of:
✓ Specific words/phrases that are problematic (e.g., "הפתיח חלש", "המילה X מכירתית מדי")
✓ Missing elements (e.g., "חסר CTA", "אין הוק", "חסרה תועלת ברורה")
✓ Structural issues (e.g., "ארוך מדי לאינסטגרם", "לא מתאים לפלטפורמה")
✓ Tone problems with specifics (e.g., "פורמלי מדי לפייסבוק", "לא נשמע כמו דנה")
✓ Alternatives or suggestions (e.g., "צריך להתחיל בשאלה", "להדגיש את התועלת")

VAGUE feedback is general/emotional:
✗ "זה לא טוב" / "this is bad"
✗ "לא אהבתי" / "didn't like it"
✗ "משהו לא בסדר" / "something's wrong"
✗ "כך כך" / "so-so"
✗ Single-word reactions: "חלש", "רע" (without context)

Answer in JSON format:
{{
  "is_actionable": true/false,
  "confidence": 0.0-1.0,
  "reason": "Short explanation in English (max 10 words)"
}}

Examples:
- "חסר הוק פותח" → {{"is_actionable": true, "confidence": 0.95, "reason": "Specific missing element: opening hook"}}
- "זה ממש לא טוב בכלל" → {{"is_actionable": false, "confidence": 0.9, "reason": "Vague emotional reaction"}}
- "המילה 'מבצע' מכירתית מדי" → {{"is_actionable": true, "confidence": 0.98, "reason": "Specific word critique"}}
- "לא מרגיש נכון" → {{"is_actionable": false, "confidence": 0.85, "reason": "Vague feeling, no specifics"}}
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a feedback quality classifier. Always respond in valid JSON format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # Low temperature for consistent classification
            max_tokens=150,
            response_format={"type": "json_object"}
        )

        # Parse JSON response
        import json
        result = json.loads(response.choices[0].message.content)

        is_actionable = result.get("is_actionable", False)
        confidence = float(result.get("confidence", 0.5))
        reason = result.get("reason", "No reason provided")

        return (is_actionable, confidence, reason)

    except Exception as e:
        # Fallback: If LLM fails, use simple heuristic
        # (Better to be conservative and send to Lab)
        print(f"[WARNING] Actionability classifier failed: {str(e)}")
        print(f"[FALLBACK] Using word-count heuristic")

        # Fallback: Word count heuristic (conservative)
        if word_count >= 5:
            return (True, 0.5, f"Fallback: {word_count} words - probably actionable")
        else:
            return (False, 0.5, f"Fallback: {word_count} words - probably vague")


# Simple test
if __name__ == "__main__":
    # Test cases
    test_cases = [
        ("חסר הוק פותח", "Structure", 2),
        ("זה לא טוב", "Tone", 2),
        ("המילה 'מבצע' מכירתית מדי", "Words", 3),
        ("לא מרגיש נכון", "Tone", 2),
        ("ארוך מדי לאינסטגרם - צריך לקצר ל-60 מילים", "Length", 3),
        ("כך כך", "Other", 3),
    ]

    print("Testing Actionability Classifier:\n")
    for text, category, rating in test_cases:
        is_actionable, confidence, reason = classify_feedback_actionability(text, category, rating)
        status = "ACTIONABLE" if is_actionable else "VAGUE"
        print(f"[{status}] (conf={confidence:.2f}) '{text}'")
        print(f"          Reason: {reason}\n")
