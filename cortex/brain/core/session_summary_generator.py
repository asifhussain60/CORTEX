"""
Session Summary Generator - Formats autonomous session summaries per ENH-048.

Uses SESSION_SUMMARY template from response-format.yaml to generate properly
formatted session summaries for autonomous multi-stage implementations.

Key Features:
- Token budget FIRST in final metrics (user awareness priority)
- Status indicators based on token percentage
- Required sections compliance (6 sections)
- Proper icon system from response format standards

Governance:
- CORE-002: No markdown file generation (chat output only)
- CORE-011: Type hints on all functions
- CORE-012: Google-style docstrings
- ENH-048: Response format standards compliance

Author: Asif Hussain
Date: 2026-02-07
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from cortex.brain.core.yaml_loaders import load_response_format


@dataclass
class StageResult:
    """Result of a completed stage."""
    
    stage_number: int
    stage_name: str
    files_created: List[str]
    tests_passing: str  # e.g., "16/16" or "17/17"
    duration_minutes: int
    status: str = "✅"  # ✅, 🟡, 🔴


@dataclass
class SessionMetrics:
    """Metrics for the session."""
    
    token_used_k: int
    token_total_k: int
    implementation_time_minutes: int
    total_tests_passing: str  # e.g., "46/46"
    type_hint_coverage: str = "100%"
    docstring_coverage: str = "100%"
    next_stage_preview: Optional[str] = None


def get_token_status(percentage: float) -> str:
    """
    Get token budget status indicator.
    
    Args:
        percentage: Token usage percentage (0-100)
        
    Returns:
        Status string with appropriate messaging
    """
    if percentage < 15:
        return "Excellent! Massive runway for continued autonomous work."
    elif percentage < 30:
        return "Excellent! Healthy runway for continued autonomous work."
    elif percentage < 50:
        return "Good. Ample runway for continuation."
    elif percentage < 70:
        return "Good. Sufficient budget for next stages."
    elif percentage < 85:
        return "Moderate. Consider checkpoint soon."
    elif percentage < 95:
        return "⚠️ High. Plan continuation checkpoint."
    else:
        return "🔴 Critical. Generate continuation prompt NOW."


def format_session_summary(
    session_title: str,
    completed_stages: List[StageResult],
    remaining_stages: List[Dict[str, Any]],
    metrics: SessionMetrics,
    governance_notes: Optional[List[str]] = None,
    next_command: str = "continue with next stage"
) -> str:
    """
    Generate formatted session summary using SESSION_SUMMARY template.
    
    Args:
        session_title: Session identifier (e.g., "Phase 38 Stages 1-3")
        completed_stages: List of completed stage results
        remaining_stages: List of remaining stages with metadata
        metrics: Session metrics including token budget
        governance_notes: Optional list of governance/audit notes
        next_command: Command to continue work
        
    Returns:
        Formatted session summary (markdown string for chat output)
        
    Example:
        >>> stages = [
        ...     StageResult(1, "Brain Health Monitor", ["file1.py", "file2.py"], "16/16", 25),
        ...     StageResult(2, "Capability Mesh", ["file3.py"], "17/17", 30),
        ... ]
        >>> metrics = SessionMetrics(84, 1000, 55, "33/33")
        >>> summary = format_session_summary("Phase 38 Stages 1-2", stages, [], metrics)
    """
    # Calculate token percentage
    token_percentage = (metrics.token_used_k / metrics.token_total_k) * 100
    token_status = get_token_status(token_percentage)
    
    lines = [
        f"## 🎯 Session Summary: {session_title}",
        "",
        "### ✅ Status Overview",
        "",
        "| Stage | Name | Status | Tests | Duration |",
        "|-------|------|--------|-------|----------|",
    ]
    
    # Add completed stages
    for stage in completed_stages:
        lines.append(
            f"| {stage.stage_number} | {stage.stage_name} | {stage.status} | "
            f"{stage.tests_passing} | {stage.duration_minutes}m |"
        )
    
    lines.extend([
        "",
        "### 📦 Completed Stages & Deliverables",
        "",
    ])
    
    for stage in completed_stages:
        lines.append(f"**Stage {stage.stage_number}: {stage.stage_name}**")
        lines.append("- **Files:**")
        for file_path in stage.files_created:
            lines.append(f"  - `{file_path}`")
        lines.append(f"- **Tests:** {stage.tests_passing} passing")
        lines.append(f"- **Duration:** {stage.duration_minutes} minutes")
        lines.append("")
    
    # Remaining stages
    if remaining_stages:
        lines.extend([
            "### 🔮 Remaining Stages",
            "",
            "| Stage | Name | Tests | Estimate | Priority |",
            "|-------|------|-------|----------|----------|",
        ])
        
        for stage_info in remaining_stages:
            lines.append(
                f"| {stage_info['number']} | {stage_info['name']} | "
                f"{stage_info['tests']} | {stage_info['estimate']} | {stage_info['priority']} |"
            )
        
        lines.append("")
    
    # CRITICAL: Token budget FIRST in final metrics
    lines.extend([
        "### 📊 Final Metrics",
        "",
        f"**Token Budget:** {metrics.token_used_k}k/{metrics.token_total_k}k "
        f"({token_percentage:.0f}%) - {token_status}",
        "",
        f"**Implementation Time:** {metrics.implementation_time_minutes} minutes",
        "",
        "**Quality Metrics:**",
        f"- ✅ {metrics.total_tests_passing} tests passing (100%)",
        f"- ✅ Type hints: {metrics.type_hint_coverage}",
        f"- ✅ Docstrings: {metrics.docstring_coverage}",
        "",
    ])
    
    if metrics.next_stage_preview:
        lines.append(f"**Next Stage Preview:** {metrics.next_stage_preview}")
        lines.append("")
    
    # Next session commands
    lines.extend([
        "### 🚀 Next Session Commands",
        "",
        f"```bash",
        f"{next_command}",
        f"```",
        "",
    ])
    
    # Governance notes
    if governance_notes:
        lines.extend([
            "### 📋 Governance Notes",
            "",
        ])
        for note in governance_notes:
            lines.append(f"- {note}")
        lines.append("")
    
    lines.extend([
        "---",
        "",
        f"*Session complete. Token budget: {token_percentage:.0f}% used. "
        f"{'Continue in this session.' if token_percentage < 85 else 'Consider continuation checkpoint.'}*",
    ])
    
    return "\n".join(lines)


def generate_continuation_checkpoint(
    session_id: str,
    last_completed: str,
    next_action: str,
    token_percentage: float,
    branch: str = "CORTEX"
) -> str:
    """
    Generate continuation checkpoint when token budget >85%.
    
    Args:
        session_id: Session identifier (e.g., "Phase 38 Stage 4")
        last_completed: Last completed item
        next_action: Next action to take
        token_percentage: Current token usage percentage
        branch: Git branch name
        
    Returns:
        Continuation checkpoint prompt (<400 tokens)
    """
    status = "⚠️ High" if token_percentage < 95 else "🔴 Critical"
    
    return f"""---

### 🔄 Continuation Checkpoint Required

**Token Budget:** {token_percentage:.0f}% used - {status}

**#file:cortex-architect.prompt.md**

**Session:** {session_id}
**Branch:** {branch}
**Checkpoint:** {last_completed} ✅

**Next:** {next_action}

**Command:** `continue with {next_action}`

---

*Copy this prompt to new Copilot Chat session to continue work.*
"""
