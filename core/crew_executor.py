# -*- coding: utf-8 -*-
"""
Crew Executor Module
Handles CrewAI execution with async support and progress tracking
"""

import asyncio
import time
from typing import Dict, Callable, Optional
from dataclasses import dataclass
from crewai import Crew, Process

from agents.strategy_architect import create_strategy_architect_agent
from agents.dana_copywriter import create_dana_copywriter_agent
from tasks.strategy_tasks import create_strategy_task
from tasks.copywriting_tasks import create_copywriting_task
from config import AgentConfig, ExecutionConfig


@dataclass
class CrewExecutionResult:
    """Result of crew execution"""
    success: bool
    strategy_output: str = ""
    copy_output: str = ""
    combined_output: str = ""
    execution_time: float = 0.0
    error: Optional[str] = None
    rag_summary: Optional[Dict] = None
    token_usage: Optional[Dict] = None


def summarize_campaign_bible(full_text: str, max_tokens: int = 500) -> str:
    """
    Summarize Campaign Bible to ~500 tokens for context efficiency.
    Extracts key sections while preserving strategic essence.

    Args:
        full_text: Full Campaign Bible output from strategy agent
        max_tokens: Target token count (~4 chars = 1 token)

    Returns:
        Condensed summary (~500 tokens / ~2000 chars)
    """
    if not full_text:
        return ""

    # Rough token estimation: 4 chars ≈ 1 token
    max_chars = max_tokens * 4

    # If already small enough, return as-is
    if len(full_text) <= max_chars:
        return full_text

    # Extract key sections (common Hebrew headers in Campaign Bible)
    key_sections = []
    lines = full_text.split('\n')

    # Priority headers to preserve
    priority_headers = [
        'GAP', 'פער',
        'קהל', 'audience', 'טרגט',
        'הבטחה', 'promise', 'הצעה',
        'ארכיטיפ', 'archetype',
        'מסר', 'message', 'תובנה',
        'טון', 'tone', 'קול'
    ]

    current_section = []
    for line in lines:
        line_lower = line.lower().strip()

        # Check if line is a header
        is_header = any(header in line_lower for header in priority_headers)

        if is_header:
            # Save previous section if exists
            if current_section:
                section_text = '\n'.join(current_section)
                if len(section_text) > 20:  # Skip very short sections
                    key_sections.append(section_text)
            # Start new section with header
            current_section = [line]
        elif current_section:
            # Add content to current section
            current_section.append(line)

    # Add last section
    if current_section:
        section_text = '\n'.join(current_section)
        if len(section_text) > 20:
            key_sections.append(section_text)

    # Combine sections until we hit char limit
    summary_parts = []
    current_length = 0

    for section in key_sections:
        if current_length + len(section) + 2 < max_chars:  # +2 for \n\n
            summary_parts.append(section)
            current_length += len(section) + 2
        else:
            # Truncate last section to fit
            remaining = max_chars - current_length - 50  # Reserve 50 for ellipsis
            if remaining > 100:
                summary_parts.append(section[:remaining] + "...")
            break

    if not summary_parts:
        # Fallback: just truncate to char limit
        return full_text[:max_chars] + "\n\n[...המשך Campaign Bible...]"

    return '\n\n'.join(summary_parts)


async def execute_crew_async(
    inputs: Dict,
    tools: Dict,
    progress_callback: Optional[Callable[[str, float], None]] = None
) -> CrewExecutionResult:
    """
    Execute CrewAI marketing content generation asynchronously.

    Args:
        inputs: Campaign inputs (product, persona, benefits, audience, offer, tone)
        tools: RAG tools dictionary (methodology, voice_examples, style_guide, etc.)
        progress_callback: Optional callback for progress updates (message, progress_float)

    Returns:
        CrewExecutionResult with outputs and metadata
    """
    start_time = time.time()

    try:
        # Progress update helper
        def update_progress(message: str, progress: float):
            if progress_callback:
                progress_callback(message, progress)

        # Extract persona
        persona = inputs.get('persona', 'Professional Dana')

        update_progress("🎯 מאתחל סוכנים...", 0.1)

        # Create agents
        strategy_architect = create_strategy_architect_agent(
            methodology_tool=tools["methodology"]
        )

        # Get persona-specific temperature
        persona_temp = AgentConfig.PERSONA_TEMPERATURES.get(
            persona,
            AgentConfig.COPYWRITER_TEMPERATURE
        )

        dana_copywriter = create_dana_copywriter_agent(
            voice_tool=tools["voice_examples"],
            style_tool=tools["style_guide"],
            platform_tool=tools["platform_specs"],
            archetype_tool=tools["post_archetypes"],
            temperature=persona_temp,
            persona=persona
        )

        update_progress("📋 יוצר משימות...", 0.2)

        # Create tasks
        strategy_task = create_strategy_task(strategy_architect, inputs)
        copywriting_task = create_copywriting_task(
            dana_copywriter,
            inputs,
            strategy_task
        )

        update_progress("🚀 מפעיל צוות AI...", 0.3)

        # Define synchronous crew execution
        def run_crew():
            """Create and run the marketing crew"""
            crew = Crew(
                agents=[strategy_architect, dana_copywriter],
                tasks=[strategy_task, copywriting_task],
                process=Process.sequential,
                verbose=ExecutionConfig.CREW_VERBOSE  # WARNING: verbose=True uses MANY extra tokens!
            )
            return crew.kickoff(inputs=inputs)

        # Run crew with timeout
        result = await asyncio.wait_for(
            asyncio.to_thread(run_crew),
            timeout=ExecutionConfig.CREW_TIMEOUT
        )

        execution_time = time.time() - start_time

        update_progress("📊 מעבד תוצאות...", 0.9)

        # Extract task outputs
        task_outputs = getattr(result, "tasks_output", []) or []

        def safe_attr(obj, names, default=""):
            """Safely extract attribute from object"""
            for name in names:
                if hasattr(obj, name):
                    val = getattr(obj, name)
                    if val:
                        return val
            return default

        # Map outputs by agent role
        agent_outputs = {}
        for t in task_outputs:
            agent_name = safe_attr(t, ["agent_role", "agent_name"])
            if not agent_name and hasattr(t, "agent") and hasattr(t.agent, "role"):
                agent_name = t.agent.role
            agent_name = agent_name or "Task"

            agent_outputs[agent_name] = {
                "task_description": safe_attr(t, ["description", "task_description"]),
                "output": safe_attr(t, ["output", "raw", "result", "final_answer"], default="(no output captured)")
            }

        # Extract outputs
        def first_non_empty(*vals):
            for v in vals:
                if v:
                    return v
            return "(no output captured)"

        def get_result_payload(res):
            """Get the main result from crew output"""
            for attr in ("raw", "output", "result", "final_answer", "text"):
                if hasattr(res, attr):
                    val = getattr(res, attr)
                    if val:
                        return val
            return None

        strategy_output = first_non_empty(
            agent_outputs.get(strategy_architect.role, {}).get("output"),
            getattr(strategy_task, "output", None)
        )

        result_payload = get_result_payload(result)

        copy_output = first_non_empty(
            agent_outputs.get(dana_copywriter.role, {}).get("output"),
            getattr(copywriting_task, "output", None)
        )

        combined_output = first_non_empty(
            result_payload,
            copy_output,
            getattr(copywriting_task, "output", None)
        )

        # Get RAG summary from ChromaDB tools
        rag_summary = {}
        try:
            from tools.chromadb_search_tool import get_chromadb_query_log
            rag_queries = get_chromadb_query_log()
            rag_summary = {
                'total_queries': len(rag_queries),
                'queries': rag_queries
            }
        except:
            pass

        # Extract token usage if available
        token_usage = None
        if hasattr(result, 'token_usage'):
            token_usage = result.token_usage
        elif hasattr(result, 'usage_metrics'):
            token_usage = result.usage_metrics

        update_progress("✅ הושלם!", 1.0)

        return CrewExecutionResult(
            success=True,
            strategy_output=strategy_output,
            copy_output=copy_output,
            combined_output=combined_output,
            execution_time=execution_time,
            rag_summary=rag_summary,
            token_usage=token_usage
        )

    except asyncio.TimeoutError:
        execution_time = time.time() - start_time
        return CrewExecutionResult(
            success=False,
            error=f"Timeout after {execution_time:.1f}s (limit: {ExecutionConfig.CREW_TIMEOUT}s)",
            execution_time=execution_time
        )

    except Exception as e:
        execution_time = time.time() - start_time
        return CrewExecutionResult(
            success=False,
            error=str(e),
            execution_time=execution_time
        )
