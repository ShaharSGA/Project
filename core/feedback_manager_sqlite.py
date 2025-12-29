"""
Feedback Manager - CRUD Operations and Data Sanitization

This module handles all database operations for the feedback loop system.
It provides functions for:
- Database initialization
- Feedback sanitization (PII removal, prompt injection prevention)
- CRUD operations (Create, Read, Update, Delete)
- Pattern retrieval with filtering

Part of the Three-Tier Closed-Loop Feedback System for BDyuk.AI
"""

import sqlite3
import re
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple

# Database path
BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "feedback" / "feedback.db"
SCHEMA_PATH = BASE_DIR / "feedback" / "schema.sql"


def init_db(db_path: str = None) -> None:
    """
    Initialize database with schema if not exists

    Args:
        db_path: Optional custom database path (default: feedback/feedback.db)
    """
    if db_path is None:
        db_path = str(DB_PATH)

    # Create feedback directory if needed
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    try:
        # Read schema
        with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        # Execute schema
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.executescript(schema_sql)
        conn.commit()
        conn.close()

        print(f"[OK] Database initialized successfully at {db_path}")

    except Exception as e:
        raise Exception(f"Failed to initialize database: {str(e)}")


def sanitize_feedback(text: str) -> str:
    """
    Remove PII and prompt injection attempts

    Patterns detected:
    - Prompt injection keywords
    - Phone numbers
    - Email addresses
    - Credit card patterns

    Args:
        text: Raw feedback text

    Returns:
        Sanitized text or warning message if suspicious content detected
        Max length: 1000 chars (truncated if longer)
    """
    if not text or not text.strip():
        return ""

    # Truncate if too long
    if len(text) > 1000:
        text = text[:1000]

    # Prompt injection patterns (case-insensitive)
    injection_patterns = [
        r'ignore\s+previous',
        r'new\s+instructions?',
        r'system\s+prompt',
        r'forget\s+everything',
        r'override',
        r'disregard',
        r'reset\s+instructions?',
        r'you\s+are\s+now',
        r'act\s+as\s+if'
    ]

    for pattern in injection_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return "[SANITIZED: Suspicious content removed]"

    # PII patterns
    # Phone numbers (US format)
    text = re.sub(r'\d{3}[-.]?\d{3}[-.]?\d{4}', '[PHONE_REDACTED]', text)

    # Email addresses
    text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[EMAIL_REDACTED]', text)

    # Credit card patterns (basic - groups of 4 digits)
    text = re.sub(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', '[CARD_REDACTED]', text)

    return text.strip()


def save_feedback(
    post_id: str,
    content: str,
    rating: int,
    category: str,
    raw_text_feedback: str,
    client_id: str,
    agent_type: str,
    persona: str,
    platform: str,
    archetype: str,
    rag_queries_used: List[str],
    metadata: Dict,
    confidence_score: float,
    db_path: str = None,
    # Refinement Lab fields (optional)
    refinement_data: Dict = None,
    lab_entry_date: str = None,
    actionability_score: float = None,
    status: str = None  # NEW: Allow explicit status override
) -> int:
    """
    Save feedback to database with auto-status assignment or explicit status

    Status logic (if status not explicitly provided):
    - confidence >= 0.8 → status='approved'
    - confidence 0.5-0.8 → status='pending'
    - confidence < 0.5 → status='flagged'

    If status is explicitly provided (e.g., from triage logic), it will be used instead.

    Args:
        post_id: Unique identifier for the post
        content: Preview of the post (first 200 chars)
        rating: 1-5 rating
        category: Feedback category
        raw_text_feedback: User's feedback text (will be sanitized)
        client_id: Client identifier
        agent_type: Agent that generated the content
        persona: Persona used
        platform: Platform (LinkedIn/Facebook/Instagram)
        archetype: Archetype (Heart/Head/Hands)
        rag_queries_used: List of RAG queries
        metadata: Additional metadata (dict)
        confidence_score: Calculated confidence (0-1)
        db_path: Optional custom database path
        status: Optional explicit status (overrides confidence-based logic)

    Returns:
        feedback_id: ID of inserted record
    """
    if db_path is None:
        db_path = str(DB_PATH)

    # Determine status: use explicit status if provided, otherwise calculate from confidence
    # Normalize status to lowercase for consistency
    if status is None:
        if confidence_score >= 0.8:
            status = 'approved'
        elif confidence_score >= 0.5:
            status = 'pending'
        else:
            status = 'flagged'
    else:
        # Normalize status to lowercase (APPROVED -> approved, PENDING_REFINEMENT -> pending_refinement)
        status = status.lower()

    # Sanitize feedback text
    sanitized_text = sanitize_feedback(raw_text_feedback)

    # Convert lists/dicts to JSON
    rag_queries_json = json.dumps(rag_queries_used, ensure_ascii=False)
    metadata_json = json.dumps(metadata, ensure_ascii=False)
    refinement_data_json = json.dumps(refinement_data, ensure_ascii=False) if refinement_data else None

    # Get current timestamp for created_at
    from datetime import datetime
    created_at = datetime.now().isoformat()

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO feedback (
                post_id, content, rating, category, raw_text_feedback,
                client_id, agent_type, persona, platform, archetype,
                rag_queries_used, metadata, status, confidence_score,
                refinement_data, lab_entry_date, actionability_score, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            post_id, content, rating, category, sanitized_text,
            client_id, agent_type, persona, platform, archetype,
            rag_queries_json, metadata_json, status, confidence_score,
            refinement_data_json, lab_entry_date, actionability_score, created_at
        ))

        feedback_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return feedback_id

    except sqlite3.IntegrityError as e:
        raise ValueError(f"Invalid feedback data: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to save feedback: {str(e)}")


def get_patterns(
    client_id: str,
    agent_type: str,
    persona: Optional[str] = None,
    platform: Optional[str] = None,
    rating_range: Optional[Tuple[int, int]] = None,
    status: str = 'approved',
    min_confidence: float = 0.7,
    limit: int = 50,
    db_path: str = None
) -> List[Dict]:
    """
    Query feedback patterns with filters

    Args:
        client_id: Client identifier
        agent_type: Agent type (e.g., 'copywriter')
        persona: Optional persona filter
        platform: Optional platform filter
        rating_range: Optional tuple (min_rating, max_rating)
        status: Status filter (default: 'approved')
        min_confidence: Minimum confidence score
        limit: Maximum number of results
        db_path: Optional custom database path

    Returns:
        List of dicts with feedback data
    """
    if db_path is None:
        db_path = str(DB_PATH)

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dicts
        cursor = conn.cursor()

        # Build query
        query = """
            SELECT id, post_id, content, rating, category, raw_text_feedback,
                   client_id, agent_type, persona, platform, archetype,
                   confidence_score, created_at, status
            FROM feedback
            WHERE client_id = ?
              AND agent_type = ?
              AND status = ?
              AND confidence_score >= ?
        """
        params = [client_id, agent_type, status, min_confidence]

        # Add optional filters
        if persona:
            query += " AND persona = ?"
            params.append(persona)

        if platform:
            query += " AND platform = ?"
            params.append(platform)

        if rating_range:
            min_rating, max_rating = rating_range
            query += " AND rating BETWEEN ? AND ?"
            params.extend([min_rating, max_rating])

        # Order by confidence (highest first) and limit
        query += " ORDER BY confidence_score DESC, created_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        # Convert to list of dicts
        results = []
        for row in rows:
            results.append(dict(row))

        return results

    except Exception as e:
        raise Exception(f"Failed to retrieve patterns: {str(e)}")


def update_status(
    feedback_id: int,
    new_status: str,
    notes: Optional[str] = None,
    refinement_data: Optional[Dict] = None,
    db_path: str = None
) -> None:
    """
    Update feedback status (for manual review or Lab processing)

    Args:
        feedback_id: Feedback record ID
        new_status: New status ('approved', 'rejected', 'flagged', 'pending',
                    'PENDING_REFINEMENT', 'SKIPPED', 'DISCARDED')
        notes: Optional notes about the status change
        refinement_data: Optional refinement Q&A data (dict)
        db_path: Optional custom database path
    """
    if db_path is None:
        db_path = str(DB_PATH)

    valid_statuses = ['pending', 'approved', 'rejected', 'flagged',
                      'pending_refinement', 'skipped', 'discarded']
    # Normalize input status to lowercase
    new_status = new_status.lower()
    if new_status not in valid_statuses:
        raise ValueError(f"Invalid status: {new_status}. Must be one of: {valid_statuses}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Convert refinement_data to JSON if provided
        refinement_json = json.dumps(refinement_data, ensure_ascii=False) if refinement_data else None

        if refinement_data:
            cursor.execute("""
                UPDATE feedback
                SET status = ?,
                    reviewed_at = CURRENT_TIMESTAMP,
                    notes = ?,
                    refinement_data = ?
                WHERE id = ?
            """, (new_status, notes, refinement_json, feedback_id))
        else:
            cursor.execute("""
                UPDATE feedback
                SET status = ?,
                    reviewed_at = CURRENT_TIMESTAMP,
                    notes = ?
                WHERE id = ?
            """, (new_status, notes, feedback_id))

        conn.commit()
        conn.close()

        # Auto-update feedback learnings file when status changes to 'approved'
        # Note: new_status is already normalized to lowercase
        if new_status == 'approved':
            try:
                # Import here to avoid circular dependencies
                from scripts.aggregate_feedback import aggregate_feedback_to_rag
                # Update learnings file silently (no verbose output)
                aggregate_feedback_to_rag(verbose=False)
            except Exception as e:
                # Don't fail the status update if learnings update fails
                # Just log it (could be improved with proper logging)
                print(f"[WARNING] Failed to auto-update learnings file: {str(e)}")

    except Exception as e:
        raise Exception(f"Failed to update status: {str(e)}")


def get_feedback_by_id(
    feedback_id: int,
    db_path: str = None
) -> Optional[Dict]:
    """
    Get single feedback record by ID

    Args:
        feedback_id: Feedback record ID
        db_path: Optional custom database path

    Returns:
        Feedback dict or None if not found
    """
    if db_path is None:
        db_path = str(DB_PATH)

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM feedback WHERE id = ?", (feedback_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    except Exception as e:
        raise Exception(f"Failed to retrieve feedback: {str(e)}")


def get_recent_feedback(
    client_id: str,
    agent_type: str,
    days: int = 30,
    min_confidence: float = 0.0,
    db_path: str = None
) -> List[Dict]:
    """
    Get recent feedback for consistency scoring

    Args:
        client_id: Client identifier
        agent_type: Agent type
        days: Number of days to look back
        min_confidence: Minimum confidence score
        db_path: Optional custom database path

    Returns:
        List of feedback dicts
    """
    if db_path is None:
        db_path = str(DB_PATH)

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Calculate cutoff date
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()

        cursor.execute("""
            SELECT id, rating, category, raw_text_feedback, persona, platform,
                   archetype, confidence_score, created_at
            FROM feedback
            WHERE client_id = ?
              AND agent_type = ?
              AND confidence_score >= ?
              AND created_at >= ?
            ORDER BY created_at DESC
        """, (client_id, agent_type, min_confidence, cutoff))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    except Exception as e:
        raise Exception(f"Failed to retrieve recent feedback: {str(e)}")


def get_lab_queue(
    client_id: str,
    agent_type: str = None,
    limit: int = 100,
    db_path: str = None
) -> List[Dict]:
    """
    Get feedback items pending refinement in the Lab

    Args:
        client_id: Client identifier
        agent_type: Optional agent type filter
        limit: Maximum number of results (default: 100)
        db_path: Optional custom database path

    Returns:
        List of feedback dicts awaiting refinement, ordered by entry date (oldest first)
    """
    if db_path is None:
        db_path = str(DB_PATH)

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = """
            SELECT id, post_id, content, rating, category, raw_text_feedback,
                   client_id, agent_type, persona, platform, archetype,
                   confidence_score, actionability_score, lab_entry_date, created_at
            FROM feedback
            WHERE client_id = ?
              AND LOWER(status) = 'pending_refinement'
        """
        params = [client_id]

        if agent_type:
            query += " AND agent_type = ?"
            params.append(agent_type)

        # Order by lab entry date (oldest first - FIFO)
        query += " ORDER BY lab_entry_date ASC, created_at ASC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    except Exception as e:
        raise Exception(f"Failed to retrieve lab queue: {str(e)}")


def auto_age_lab_items(
    days_threshold: int = 7,
    db_path: str = None
) -> int:
    """
    Auto-promote old lab items to SKIPPED status

    Items that have been in PENDING_REFINEMENT for > days_threshold
    are automatically marked as SKIPPED to prevent backlog buildup.

    Args:
        days_threshold: Number of days before auto-skipping (default: 7)
        db_path: Optional custom database path

    Returns:
        Number of items auto-aged
    """
    if db_path is None:
        db_path = str(DB_PATH)

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Calculate cutoff date
        cutoff = (datetime.now() - timedelta(days=days_threshold)).isoformat()

        cursor.execute("""
            UPDATE feedback
            SET status = 'skipped',
                notes = 'Auto-aged: No refinement after ' || ? || ' days'
            WHERE LOWER(status) = 'pending_refinement'
              AND lab_entry_date < ?
        """, (days_threshold, cutoff))

        count = cursor.rowcount
        conn.commit()
        conn.close()

        return count

    except Exception as e:
        raise Exception(f"Failed to auto-age lab items: {str(e)}")


def get_feedback_stats(
    client_id: str,
    agent_type: str = None,
    db_path: str = None
) -> Dict:
    """
    Get aggregate statistics for feedback

    Args:
        client_id: Client identifier
        agent_type: Optional agent type filter
        db_path: Optional custom database path

    Returns:
        Dict with statistics
    """
    if db_path is None:
        db_path = str(DB_PATH)

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Build base query
        base_where = "WHERE client_id = ?"
        params = [client_id]

        if agent_type:
            base_where += " AND agent_type = ?"
            params.append(agent_type)

        # Total count
        cursor.execute(f"SELECT COUNT(*) FROM feedback {base_where}", params)
        total = cursor.fetchone()[0]

        # By status
        cursor.execute(f"""
            SELECT status, COUNT(*) as count
            FROM feedback {base_where}
            GROUP BY status
        """, params)
        by_status = dict(cursor.fetchall())

        # Average confidence
        cursor.execute(f"""
            SELECT AVG(confidence_score) FROM feedback {base_where}
        """, params)
        avg_confidence = cursor.fetchone()[0] or 0.0

        # Average rating
        cursor.execute(f"""
            SELECT AVG(rating) FROM feedback {base_where}
        """, params)
        avg_rating = cursor.fetchone()[0] or 0.0

        conn.close()

        return {
            'total': total,
            'by_status': by_status,
            'avg_confidence': round(avg_confidence, 2),
            'avg_rating': round(avg_rating, 2)
        }

    except Exception as e:
        raise Exception(f"Failed to retrieve stats: {str(e)}")


# Initialize database on module import (if schema exists)
if SCHEMA_PATH.exists() and not DB_PATH.exists():
    try:
        init_db()
    except Exception as e:
        # Log error but don't fail - database will be initialized on first use
        import logging
        logging.warning(f"Could not auto-initialize database: {e}")
