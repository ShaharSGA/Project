"""
Confidence Score Calculator

Calculates confidence scores for feedback using a multi-factor algorithm:
- Context score (30%): Quality of feedback context
- Consistency score (40%): Alignment with historical patterns
- Specificity score (30%): Detail level of feedback

Formula: confidence = (context × 0.3) + (consistency × 0.4) + (specificity × 0.3)

Part of the Three-Tier Closed-Loop Feedback System for BDyuk.AI
"""

import math
from typing import Dict, List


def calculate_confidence(
    feedback_data: Dict,
    historical_data: List[Dict]
) -> float:
    """
    Main confidence calculation

    Args:
        feedback_data: Current feedback being scored with keys:
            - rating: 1-5
            - category: str
            - raw_text_feedback: str
            - persona: str
            - platform: str
        historical_data: Recent feedback for same context (last 30 days)

    Returns:
        Confidence score 0.0-1.0
    """
    context = calc_context_score(feedback_data)
    consistency = calc_consistency_score(feedback_data, historical_data)
    specificity = calc_specificity_score(feedback_data)

    # Weighted average
    confidence = (context * 0.3) + (consistency * 0.4) + (specificity * 0.3)

    # Ensure within bounds
    return max(0.0, min(1.0, confidence))


def calc_context_score(feedback_data: Dict) -> float:
    """
    Context score (0-1)

    Scoring:
    - Base: 0.5
    - +0.2 if category != 'Other'
    - +0.2 if text feedback length > 20 chars
    - +0.1 if rating is extreme (1 or 5)
    - CRITICAL: If feedback is empty/whitespace only → return 0.2 (very low)

    Max: 1.0

    Args:
        feedback_data: Feedback dict with rating, category, raw_text_feedback

    Returns:
        Context score 0.0-1.0
    """
    # Check if feedback text is empty or whitespace only
    text_feedback = feedback_data.get('raw_text_feedback', '')
    if not text_feedback or not text_feedback.strip():
        # Empty feedback = very low context score
        return 0.2

    score = 0.5

    # Specific category (not 'Other')
    if feedback_data.get('category', 'Other') != 'Other':
        score += 0.2

    # Sufficient text feedback
    if len(text_feedback) > 20:
        score += 0.2

    # Extreme rating (strong signal)
    rating = feedback_data.get('rating', 3)
    if rating in [1, 5]:
        score += 0.1

    return min(score, 1.0)


def calc_consistency_score(
    feedback_data: Dict,
    historical_data: List[Dict]
) -> float:
    """
    Consistency score (0-1)

    Compare new rating to historical average for same:
    - persona
    - platform

    If no history: return 0.7 (neutral)

    Scoring:
    - diff <= 1 → 1.0 (consistent)
    - diff = 2 → 0.6 (somewhat inconsistent)
    - diff >= 3 → 0.3 (flag for review)

    Args:
        feedback_data: Current feedback with rating, persona, platform
        historical_data: List of historical feedback dicts

    Returns:
        Consistency score 0.0-1.0
    """
    if not historical_data:
        return 0.7  # Neutral for first feedback

    # Filter for same context
    persona = feedback_data.get('persona')
    platform = feedback_data.get('platform')

    same_context = [
        h for h in historical_data
        if (h.get('persona') == persona and h.get('platform') == platform)
    ]

    if not same_context:
        return 0.7  # Neutral if no matching context

    # Calculate average rating for same context
    avg_rating = sum(h.get('rating', 3) for h in same_context) / len(same_context)

    # Calculate difference from average
    current_rating = feedback_data.get('rating', 3)
    diff = abs(current_rating - avg_rating)

    # Score based on difference
    if diff <= 1:
        return 1.0  # Highly consistent
    elif diff <= 2:
        return 0.6  # Somewhat consistent
    else:
        return 0.3  # Inconsistent - flag for review


def calc_specificity_score(feedback_data: Dict) -> float:
    """
    Specificity score (0-1)

    Count specific keywords in Hebrew:
    ["מילה", "ביטוי", "משפט", "פתיחה", "סגירה",
     "רשמי", "קליל", "ארוך", "קצר", "טון", "סגנון"]

    Also check for English keywords:
    ["word", "phrase", "sentence", "opening", "closing",
     "formal", "casual", "long", "short", "tone", "style"]

    Scoring:
    - 2+ matches → 1.0 (very specific)
    - 1 match → 0.7 (somewhat specific)
    - 0 matches → 0.4 (vague)

    Args:
        feedback_data: Feedback dict with raw_text_feedback

    Returns:
        Specificity score 0.0-1.0
    """
    # Hebrew keywords
    hebrew_keywords = [
        "מילה", "ביטוי", "משפט", "פתיחה", "סגירה",
        "רשמי", "קליל", "ארוך", "קצר", "טון", "סגנון",
        "מבנה", "תוכן", "סיום", "התחלה", "אורך", "קצרה"
    ]

    # English keywords (for mixed feedback)
    english_keywords = [
        "word", "phrase", "sentence", "opening", "closing",
        "formal", "casual", "long", "short", "tone", "style",
        "structure", "content", "ending", "beginning", "length"
    ]

    text = feedback_data.get('raw_text_feedback', '').lower()

    # Count matches
    matches = 0
    for kw in hebrew_keywords:
        if kw in text:
            matches += 1

    for kw in english_keywords:
        if kw in text:
            matches += 1

    # Score based on number of specific keywords
    if matches >= 2:
        return 1.0  # Very specific
    elif matches == 1:
        return 0.7  # Somewhat specific
    else:
        return 0.4  # Vague


def get_confidence_explanation(
    context: float,
    consistency: float,
    specificity: float
) -> str:
    """
    Generate human-readable explanation of confidence score in Hebrew

    Args:
        context: Context score (0-1)
        consistency: Consistency score (0-1)
        specificity: Specificity score (0-1)

    Returns:
        Hebrew explanation string
    """
    total = (context * 0.3) + (consistency * 0.4) + (specificity * 0.3)

    explanation = f"ציון אמינות: {total:.2f}\n\n"

    # Context explanation
    if context >= 0.9:
        explanation += "✅ הקשר: מצוין - משוב מפורט עם קטגוריה ברורה\n"
    elif context >= 0.7:
        explanation += "✓ הקשר: טוב - משוב עם פרטים מספיקים\n"
    elif context <= 0.3:
        explanation += "⚠️ הקשר: חלש מאוד - משוב ריק או חסר פרטים\n"
    else:
        explanation += "⚠️ הקשר: חלש - חסרים פרטים\n"

    # Consistency explanation
    if consistency >= 0.9:
        explanation += "✅ עקביות: גבוהה - תואם למשובים קודמים\n"
    elif math.isclose(consistency, 0.7) and math.isclose(specificity, 0.0):
        explanation += "ℹ️ עקביות: אין היסטוריה - משוב ראשון בהקשר זה\n"
    elif consistency >= 0.7:
        explanation += "✓ עקביות: בינונית - עקביות סבירה\n"
    else:
        explanation += "⚠️ עקביות: נמוכה - שונה ממשובים קודמים\n"

    # Specificity explanation
    if specificity >= 0.9:
        explanation += "✅ ספציפיות: גבוהה - משוב מאד מפורט\n"
    elif specificity >= 0.7:
        explanation += "✓ ספציפיות: בינונית - פרטים סבירים\n"
    else:
        explanation += "⚠️ ספציפיות: נמוכה - משוב כללי\n"

    return explanation


def get_confidence_category(confidence: float) -> str:
    """
    Get confidence category label

    Args:
        confidence: Confidence score (0-1)

    Returns:
        Category label in Hebrew
    """
    if confidence >= 0.8:
        return "גבוהה - אושר אוטומטית"
    elif confidence >= 0.5:
        return "בינונית - ממתין לבדיקה"
    else:
        return "נמוכה - מסומן לבדיקה"


def should_auto_approve(confidence: float) -> bool:
    """
    Determine if feedback should be auto-approved

    Args:
        confidence: Confidence score (0-1)

    Returns:
        True if should auto-approve (confidence >= 0.8)
    """
    return confidence >= 0.8
