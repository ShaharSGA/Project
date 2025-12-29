"""
Feedback Triage - Intelligent Routing Logic

This module decides where feedback should go:
- APPROVED → Directly to ChromaDB/training
- PENDING_REFINEMENT → Refinement Lab for clarification
- (Status can later be updated to SKIPPED or DISCARDED)

Part of the two-phase Refinement Lab architecture.
"""

from datetime import datetime
from typing import Dict
from .actionability_classifier import classify_feedback_actionability


def evaluate_feedback_quality(
    score: int,
    text: str,
    category: str
) -> Dict[str, any]:
    """
    Evaluate feedback quality and determine routing

    Logic (in priority order):
    1. Category "Strategic Miss" → Always PENDING_REFINEMENT (critical learning, overrides everything)
    2. Score 5 → Always APPROVED (high satisfaction)
    3. Score 4 → Check actionability → APPROVED or PENDING_REFINEMENT
    4. Score 1-3 → Check actionability → APPROVED or PENDING_REFINEMENT

    Args:
        score: User rating (1-5)
        text: Feedback text
        category: Feedback category

    Returns:
        Dict with:
        - status: 'APPROVED' or 'PENDING_REFINEMENT'
        - actionability_score: 0.0-1.0 (from LLM classifier)
        - reason: Short explanation
        - lab_entry_date: Timestamp if sent to Lab (else None)

    Examples:
        >>> evaluate_feedback_quality(5, "מעולה!", "Tone")
        {'status': 'APPROVED', 'actionability_score': 1.0, 'reason': 'Score 5 auto-approved', ...}

        >>> evaluate_feedback_quality(2, "זה לא טוב", "Tone")
        {'status': 'PENDING_REFINEMENT', 'actionability_score': 0.2, 'reason': 'Vague feedback', ...}
    """

    # Rule 1: Strategic Miss → Always needs refinement (HIGHEST PRIORITY - critical learning opportunity)
    # This rule runs FIRST, even before Score 5 check, because strategic errors must be analyzed
    if category == "Strategic Miss / DNA Mismatch":
        return {
            'status': 'PENDING_REFINEMENT',
            'actionability_score': 0.0,  # Overridden by category
            'reason': 'Strategic Miss - Mandatory Lab review (overrides all other rules)',
            'lab_entry_date': datetime.now().isoformat()
        }

    # Rule 2: Score 5 → Always approve (user is very happy)
    if score == 5:
        return {
            'status': 'APPROVED',
            'actionability_score': 1.0,
            'reason': 'Score 5 - Auto-approved (high satisfaction)',
            'lab_entry_date': None
        }

    # Rule 3 & 4: Check actionability via LLM
    is_actionable, confidence, classifier_reason = classify_feedback_actionability(text, category, score)

    if is_actionable:
        # Feedback is specific enough → Approve
        return {
            'status': 'APPROVED',
            'actionability_score': confidence,
            'reason': f'Actionable - {classifier_reason}',
            'lab_entry_date': None
        }
    else:
        # Feedback is vague → Send to Lab for clarification
        return {
            'status': 'PENDING_REFINEMENT',
            'actionability_score': confidence,
            'reason': f'Vague - {classifier_reason}',
            'lab_entry_date': datetime.now().isoformat()
        }


def get_toast_message(status: str) -> Dict[str, str]:
    """
    Get user-friendly toast message for feedback status

    Args:
        status: 'APPROVED' or 'PENDING_REFINEMENT'

    Returns:
        Dict with 'icon', 'title', 'message'
    """

    if status == 'APPROVED':
        return {
            'icon': '✅',
            'title': 'הפידבק נשמר!',
            'message': 'התובנות שלך נוספו למערכת הלמידה'
        }
    elif status == 'PENDING_REFINEMENT':
        return {
            'icon': '⚗️',
            'title': 'הועבר למעבדת השיפור',
            'message': 'נשמח לעזרתך בהבהרת הפידבק (אופציונלי)'
        }
    else:
        return {
            'icon': 'ℹ️',
            'title': 'הפידבק נשמר',
            'message': ''
        }


# Simple test
if __name__ == "__main__":
    print("Testing Feedback Triage Logic:\n")

    test_cases = [
        (5, "מעולה! בדיוק מה שצריך", "Tone"),
        (4, "טוב, אבל...", "Message"),
        (4, "חסר הוק פותח חזק", "Structure"),
        (2, "זה לא טוב", "Tone"),
        (2, "המילה 'מבצע' מכירתית מדי", "Words"),
        (3, "משהו לא מרגיש נכון", "Platform_Fit"),
        (1, "שגוי לחלוטין - ארכיטייפ לא מתאים", "Strategic Miss / DNA Mismatch"),
    ]

    for score, text, category in test_cases:
        result = evaluate_feedback_quality(score, text, category)
        print(f"Score: {score}/5 | Category: {category}")
        print(f"Text: \"{text}\"")
        print(f"→ Status: {result['status']}")
        print(f"  Actionability: {result['actionability_score']:.2f}")
        print(f"  Reason: {result['reason']}")
        if result['lab_entry_date']:
            print(f"  Lab Entry: {result['lab_entry_date']}")
        print()
