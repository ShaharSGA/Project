"""
Feedback Manager - CRUD Operations and Data Sanitization (Supabase Only)

This module handles all database operations for the feedback loop system.
It provides functions for:
- Feedback sanitization (PII removal, prompt injection prevention)
- CRUD operations (Create, Read, Update, Delete)
- Pattern retrieval with filtering

Part of the Three-Tier Closed-Loop Feedback System for BDyuk.AI

NOTE: This module now uses Supabase exclusively for cloud deployment.
SQLite code has been removed (see git history for SQLite implementation).
"""

# NOTE: SQLite imports removed - using Supabase only
# import sqlite3  # OLD - Removed for Supabase-only deployment

import re
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple

# Supabase imports (required)
from supabase import create_client, Client

# Import configuration
from config import SUPABASE_URL, SUPABASE_KEY

# Supabase client (initialized lazily)
_supabase_client: Optional[Client] = None


def _get_supabase_client() -> Client:
    """
    Get or create Supabase client (singleton pattern).

    Returns:
        Supabase client instance

    Raises:
        ValueError: If SUPABASE_URL or SUPABASE_KEY are not configured
    """
    global _supabase_client
    if _supabase_client is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY must be set in environment/secrets. "
                "Please configure these in Streamlit Cloud secrets or .env file."
            )
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_client


# NOTE: init_db() removed - Supabase table is managed via Supabase dashboard
# SQLite version (for reference):
# def init_db(db_path: str = None) -> None:
#     """Initialize SQLite database with schema if not exists"""
#     conn = sqlite3.connect(db_path)
#     cursor = conn.cursor()
#     cursor.executescript(schema_sql)
#     conn.commit()
#     conn.close()


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
    db_path: str = None,  # Kept for API compatibility (ignored)
    # Refinement Lab fields (optional)
    refinement_data: Dict = None,
    lab_entry_date: str = None,
    actionability_score: float = None,
    status: str = None  # NEW: Allow explicit status override
) -> int:
    """
    Save feedback to Supabase database with auto-status assignment or explicit status

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
        db_path: (Ignored - kept for API compatibility)
        status: Optional explicit status (overrides confidence-based logic)
        refinement_data: Optional refinement Q&A data (dict)
        lab_entry_date: Optional timestamp for lab entry
        actionability_score: Optional actionability score (0-1)

    Returns:
        feedback_id: ID of inserted record

    Raises:
        ValueError: If feedback data is invalid
        Exception: If save operation fails
    """
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

    # Get Supabase client
    supabase = _get_supabase_client()

    # Prepare data for Supabase (JSONB fields stay as dict/list)
    feedback_data = {
        'post_id': post_id,
        'content': content,
        'rating': rating,
        'category': category,
        'raw_text_feedback': sanitized_text,
        'client_id': client_id,
        'agent_type': agent_type,
        'persona': persona,
        'platform': platform,
        'archetype': archetype,
        'rag_queries_used': rag_queries_used,  # Supabase handles JSONB automatically
        'metadata': metadata,  # Supabase handles JSONB automatically
        'status': status,
        'confidence_score': confidence_score,
        'refinement_data': refinement_data,  # JSONB or None
        'lab_entry_date': lab_entry_date,  # Timestamp or None
        'actionability_score': actionability_score,  # Float or None
        'created_at': datetime.now().isoformat()
    }

    try:
        # Insert into Supabase
        response = supabase.table('feedback').insert(feedback_data).execute()

        # Get inserted record ID
        if response.data and len(response.data) > 0:
            feedback_id = response.data[0]['id']
            return feedback_id
        else:
            raise Exception("Insert succeeded but no data returned")

    except Exception as e:
        # Map Supabase errors to appropriate exceptions
        error_msg = str(e).lower()
        if 'unique' in error_msg or 'constraint' in error_msg or 'duplicate' in error_msg:
            raise ValueError(f"Invalid feedback data (constraint violation): {str(e)}")
        raise Exception(f"Failed to save feedback to Supabase: {str(e)}")


# SQLite version (for reference):
# def save_feedback(...) -> int:
#     conn = sqlite3.connect(db_path)
#     cursor = conn.cursor()
#     cursor.execute("INSERT INTO feedback (...) VALUES (...)", (...))
#     feedback_id = cursor.lastrowid
#     conn.commit()
#     conn.close()
#     return feedback_id


def get_patterns(
    client_id: str,
    agent_type: str,
    persona: Optional[str] = None,
    platform: Optional[str] = None,
    rating_range: Optional[Tuple[int, int]] = None,
    status: str = 'approved',
    min_confidence: float = 0.7,
    limit: int = 50,
    db_path: str = None  # Kept for API compatibility (ignored)
) -> List[Dict]:
    """
    Query feedback patterns from Supabase with filters

    Args:
        client_id: Client identifier
        agent_type: Agent type (e.g., 'copywriter')
        persona: Optional persona filter
        platform: Optional platform filter
        rating_range: Optional tuple (min_rating, max_rating)
        status: Status filter (default: 'approved')
        min_confidence: Minimum confidence score
        limit: Maximum number of results
        db_path: (Ignored - kept for API compatibility)

    Returns:
        List of dicts with feedback data
    """
    supabase = _get_supabase_client()

    try:
        # Build Supabase query
        query = supabase.table('feedback').select(
            'id, post_id, content, rating, category, raw_text_feedback, '
            'client_id, agent_type, persona, platform, archetype, '
            'confidence_score, created_at, status'
        )

        # Apply filters
        query = query.eq('client_id', client_id)\
                     .eq('agent_type', agent_type)\
                     .eq('status', status)\
                     .gte('confidence_score', min_confidence)

        # Optional filters
        if persona:
            query = query.eq('persona', persona)

        if platform:
            query = query.eq('platform', platform)

        if rating_range:
            min_rating, max_rating = rating_range
            query = query.gte('rating', min_rating).lte('rating', max_rating)

        # Order and limit
        query = query.order('confidence_score', desc=True)\
                     .order('created_at', desc=True)\
                     .limit(limit)

        # Execute query
        response = query.execute()

        return response.data if response.data else []

    except Exception as e:
        raise Exception(f"Failed to retrieve patterns from Supabase: {str(e)}")


# SQLite version (for reference):
# def get_patterns(...) -> List[Dict]:
#     conn = sqlite3.connect(db_path)
#     cursor = conn.cursor()
#     cursor.execute("SELECT ... FROM feedback WHERE ... ORDER BY ... LIMIT ?", params)
#     rows = cursor.fetchall()
#     return [dict(row) for row in rows]


def update_status(
    feedback_id: int,
    new_status: str,
    notes: Optional[str] = None,
    refinement_data: Optional[Dict] = None,
    db_path: str = None  # Kept for API compatibility (ignored)
) -> None:
    """
    Update feedback status in Supabase (for manual review or Lab processing)

    Args:
        feedback_id: Feedback record ID
        new_status: New status ('approved', 'rejected', 'flagged', 'pending',
                    'pending_refinement', 'skipped', 'discarded')
        notes: Optional notes about the status change
        refinement_data: Optional refinement Q&A data (dict)
        db_path: (Ignored - kept for API compatibility)
    """
    valid_statuses = ['pending', 'approved', 'rejected', 'flagged',
                      'pending_refinement', 'skipped', 'discarded']
    # Normalize input status to lowercase
    new_status = new_status.lower()
    if new_status not in valid_statuses:
        raise ValueError(f"Invalid status: {new_status}. Must be one of: {valid_statuses}")

    supabase = _get_supabase_client()

    try:
        # Prepare update data
        update_data = {
            'status': new_status,
            'reviewed_at': datetime.now().isoformat(),
            'notes': notes
        }

        # Add refinement_data if provided (Supabase handles JSONB automatically)
        if refinement_data:
            update_data['refinement_data'] = refinement_data

        # Execute update
        supabase.table('feedback')\
            .update(update_data)\
            .eq('id', feedback_id)\
            .execute()

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
        raise Exception(f"Failed to update status in Supabase: {str(e)}")


# SQLite version (for reference):
# def update_status(feedback_id, new_status, notes, refinement_data, db_path) -> None:
#     conn = sqlite3.connect(db_path)
#     cursor = conn.cursor()
#     cursor.execute("UPDATE feedback SET status = ?, ... WHERE id = ?", (new_status, ..., feedback_id))
#     conn.commit()
#     conn.close()


def get_feedback_by_id(
    feedback_id: int,
    db_path: str = None  # Kept for API compatibility (ignored)
) -> Optional[Dict]:
    """
    Get single feedback record by ID from Supabase

    Args:
        feedback_id: Feedback record ID
        db_path: (Ignored - kept for API compatibility)

    Returns:
        Feedback dict or None if not found
    """
    supabase = _get_supabase_client()

    try:
        response = supabase.table('feedback')\
            .select('*')\
            .eq('id', feedback_id)\
            .execute()

        if response.data and len(response.data) > 0:
            return response.data[0]
        return None

    except Exception as e:
        raise Exception(f"Failed to retrieve feedback from Supabase: {str(e)}")


# SQLite version (for reference):
# def get_feedback_by_id(feedback_id, db_path) -> Optional[Dict]:
#     conn = sqlite3.connect(db_path)
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM feedback WHERE id = ?", (feedback_id,))
#     row = cursor.fetchone()
#     return dict(row) if row else None


def get_recent_feedback(
    client_id: str,
    agent_type: str,
    days: int = 30,
    min_confidence: float = 0.0,
    db_path: str = None  # Kept for API compatibility (ignored)
) -> List[Dict]:
    """
    Get recent feedback from Supabase for consistency scoring

    Args:
        client_id: Client identifier
        agent_type: Agent type
        days: Number of days to look back
        min_confidence: Minimum confidence score
        db_path: (Ignored - kept for API compatibility)

    Returns:
        List of feedback dicts
    """
    supabase = _get_supabase_client()

    try:
        # Calculate cutoff date
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()

        response = supabase.table('feedback')\
            .select('id, rating, category, raw_text_feedback, persona, platform, '
                   'archetype, confidence_score, created_at')\
            .eq('client_id', client_id)\
            .eq('agent_type', agent_type)\
            .gte('confidence_score', min_confidence)\
            .gte('created_at', cutoff)\
            .order('created_at', desc=True)\
            .execute()

        return response.data if response.data else []

    except Exception as e:
        raise Exception(f"Failed to retrieve recent feedback from Supabase: {str(e)}")


def get_lab_queue(
    client_id: str,
    agent_type: str = None,
    limit: int = 100,
    db_path: str = None  # Kept for API compatibility (ignored)
) -> List[Dict]:
    """
    Get feedback items pending refinement in the Lab from Supabase

    Args:
        client_id: Client identifier
        agent_type: Optional agent type filter
        limit: Maximum number of results (default: 100)
        db_path: (Ignored - kept for API compatibility)

    Returns:
        List of feedback dicts awaiting refinement, ordered by entry date (oldest first)
    """
    supabase = _get_supabase_client()

    try:
        query = supabase.table('feedback')\
            .select('id, post_id, content, rating, category, raw_text_feedback, '
                   'client_id, agent_type, persona, platform, archetype, '
                   'confidence_score, actionability_score, lab_entry_date, created_at')\
            .eq('client_id', client_id)\
            .eq('status', 'pending_refinement')

        if agent_type:
            query = query.eq('agent_type', agent_type)

        # Order by lab entry date (oldest first - FIFO)
        response = query.order('lab_entry_date', desc=False)\
                       .order('created_at', desc=False)\
                       .limit(limit)\
                       .execute()

        return response.data if response.data else []

    except Exception as e:
        raise Exception(f"Failed to retrieve lab queue from Supabase: {str(e)}")


def auto_age_lab_items(
    days_threshold: int = 7,
    db_path: str = None  # Kept for API compatibility (ignored)
) -> int:
    """
    Auto-promote old lab items to SKIPPED status in Supabase

    Items that have been in PENDING_REFINEMENT for > days_threshold
    are automatically marked as SKIPPED to prevent backlog buildup.

    Args:
        days_threshold: Number of days before auto-skipping (default: 7)
        db_path: (Ignored - kept for API compatibility)

    Returns:
        Number of items auto-aged
    """
    supabase = _get_supabase_client()

    try:
        # Calculate cutoff date
        cutoff = (datetime.now() - timedelta(days=days_threshold)).isoformat()

        # First, get items to update (to count them)
        items_to_age = supabase.table('feedback')\
            .select('id')\
            .eq('status', 'pending_refinement')\
            .lt('lab_entry_date', cutoff)\
            .execute()

        count = len(items_to_age.data) if items_to_age.data else 0

        if count > 0:
            # Update items to 'skipped' status
            supabase.table('feedback')\
                .update({
                    'status': 'skipped',
                    'notes': f'Auto-aged: No refinement after {days_threshold} days'
                })\
                .eq('status', 'pending_refinement')\
                .lt('lab_entry_date', cutoff)\
                .execute()

        return count

    except Exception as e:
        raise Exception(f"Failed to auto-age lab items in Supabase: {str(e)}")


def get_feedback_stats(
    client_id: str,
    agent_type: str = None,
    db_path: str = None  # Kept for API compatibility (ignored)
) -> Dict:
    """
    Get aggregate statistics for feedback from Supabase

    Args:
        client_id: Client identifier
        agent_type: Optional agent type filter
        db_path: (Ignored - kept for API compatibility)

    Returns:
        Dict with statistics
    """
    supabase = _get_supabase_client()

    try:
        # Build base query
        query = supabase.table('feedback').select('*').eq('client_id', client_id)

        if agent_type:
            query = query.eq('agent_type', agent_type)

        # Get all feedback records
        response = query.execute()
        all_feedback = response.data if response.data else []

        # Calculate statistics
        total = len(all_feedback)

        # By status
        by_status = {}
        for item in all_feedback:
            status = item.get('status', 'unknown')
            by_status[status] = by_status.get(status, 0) + 1

        # Average confidence
        confidence_scores = [item.get('confidence_score', 0) for item in all_feedback if item.get('confidence_score') is not None]
        avg_confidence = round(sum(confidence_scores) / len(confidence_scores), 2) if confidence_scores else 0.0

        # Average rating
        ratings = [item.get('rating', 0) for item in all_feedback if item.get('rating') is not None]
        avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else 0.0

        return {
            'total': total,
            'by_status': by_status,
            'avg_confidence': avg_confidence,
            'avg_rating': avg_rating
        }

    except Exception as e:
        raise Exception(f"Failed to retrieve stats from Supabase: {str(e)}")


# NOTE: Database initialization removed - Supabase table is managed via Supabase dashboard
# SQLite auto-init code (for reference):
# if SCHEMA_PATH.exists() and not DB_PATH.exists():
#     try:
#         init_db()
#     except Exception as e:
#         logging.warning(f"Could not auto-initialize database: {e}")
