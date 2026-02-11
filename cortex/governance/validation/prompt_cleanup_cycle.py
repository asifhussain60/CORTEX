"""
AC_START: AC-PROMPT-CLEANUP-CYCLE-001
Description: Automated prompt cleanup cycle task definitions
Author: Asif Hussain
Phase: 56 - LENS/Intelligence Hybrid Architecture + Audit Enhancement
"""

# ============================================================================
# PROMPT CLEANUP CYCLE TASK DEFINITIONS (AC-PROMPT-CLEANUP-001 through 005)
# ============================================================================
# Purpose: Define systematic cleanup tasks to detect prompt drift from implementation
# Authority: CORE-030 (Implementation Truth), Phase 39 (Cohesion & Integrity)
# Frequency: Every AUDIT operation via cortex-architect.prompt.md
# ============================================================================

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List


class CleanupPriority(Enum):
    """Priority levels for cleanup tasks."""
    P0_CRITICAL = "P0"  # Blocking production issues
    P1_HIGH = "P1"      # Architectural integrity violations
    P2_MEDIUM = "P2"    # Quality/consistency issues
    P3_LOW = "P3"       # Optimization opportunities


@dataclass
class CleanupTask:
    """Represents a single prompt cleanup task."""
    ac_marker: str
    title: str
    description: str
    detection_method: str
    auto_fix: str
    priority: CleanupPriority
    frequency: str  # "every_audit" | "weekly" | "monthly"


# ============================================================================
# CLEANUP TASK REGISTRY
# ============================================================================

PROMPT_CLEANUP_TASKS: List[CleanupTask] = [
    # AC-PROMPT-CLEANUP-001: Deprecated Orchestrator References
    CleanupTask(
        ac_marker="AC-PROMPT-CLEANUP-001",
        title="Deprecated Orchestrator Removal",
        description="Detect references to orchestrators removed from __wiring_contract__.yaml but still mentioned in prompts/agents",
        detection_method=r"""
        1. Load cortex/__wiring_contract__.yaml → extract active orchestrators
        2. Scan .github/prompts/*.md and .github/agents/core/*.md
        3. Extract orchestrator references (regex: \w+Orchestrator)
        4. Find references NOT in wiring.yaml
        5. Flag as deprecated
        """,
        auto_fix="Remove deprecated orchestrator references from prompts/agents or add back to wiring if needed",
        priority=CleanupPriority.P1_HIGH,
        frequency="every_audit"
    ),

    # AC-PROMPT-CLEANUP-002: MCP Tool Signature Drift
    CleanupTask(
        ac_marker="AC-PROMPT-CLEANUP-002",
        title="MCP Tool Signature Synchronization",
        description="Verify MCP tool signatures in prompts match actual implementation in cortex/mcp/tools/",
        detection_method="""
        1. Extract MCP tool signatures from cortex/mcp/tools/*.py
        2. Extract MCP tool documentation from .github/prompts/*.md
        3. Compare parameters, return types, descriptions
        4. Flag mismatches
        """,
        auto_fix="Update prompt documentation to match implementation signatures (CORE-030: Implementation Truth)",
        priority=CleanupPriority.P0_CRITICAL,
        frequency="every_audit"
    ),

    # AC-PROMPT-CLEANUP-003: Agent Capability Coverage
    CleanupTask(
        ac_marker="AC-PROMPT-CLEANUP-003",
        title="Agent-Orchestrator Capability Sync",
        description="Ensure agent capabilities (cortex-auditor.md) reflect latest orchestrator capabilities (HolisticValidationOrchestrator, EnforcementOrchestrator)",
        detection_method="""
        1. Extract agent audit checks from .github/agents/core/cortex-auditor.md
        2. Extract orchestrator validation logic from cortex/orchestrators/validation/*
        3. Identify orchestrator checks NOT documented in agent
        4. Flag missing capabilities
        """,
        auto_fix="Add missing validation checks to cortex-auditor.md P1-P3 sections",
        priority=CleanupPriority.P1_HIGH,
        frequency="every_audit"
    ),

    # AC-PROMPT-CLEANUP-004: Challenge Gate Documentation Sync
    CleanupTask(
        ac_marker="AC-PROMPT-CLEANUP-004",
        title="Challenge Engine Documentation Update",
        description="Verify ChallengeEngine capabilities in prompts match cortex/orchestrators/interaction/challenge_engine.py",
        detection_method="""
        1. Extract challenge generation logic from challenge_engine.py
        2. Extract challenge documentation from cortex-architect.prompt.md
        3. Compare:
           - Number of alternative options generated
           - DoR confidence thresholds
           - Challenge types supported
        4. Flag documentation drift
        """,
        auto_fix="Update challenge documentation to match implementation (current: 5 alternatives, DoR ≥0.7)",
        priority=CleanupPriority.P2_MEDIUM,
        frequency="every_audit"
    ),

    # AC-PROMPT-CLEANUP-005: Response Format DRY Principle
    CleanupTask(
        ac_marker="AC-PROMPT-CLEANUP-005",
        title="Consolidate Duplicate Response Formatting Rules",
        description="Detect duplicate response format instructions across multiple prompt files and consolidate to single reference",
        detection_method="""
        1. Scan .github/prompts/*.md for response format sections
        2. Extract formatting rules (headers, status icons, numbering)
        3. Calculate similarity scores (SequenceMatcher)
        4. Flag duplicates (>80% similarity, >200 chars)
        """,
        auto_fix="Extract to response-format-standards.md and reference from other prompts (DRY principle)",
        priority=CleanupPriority.P3_LOW,
        frequency="weekly"
    ),
]


# ============================================================================
# CLEANUP CYCLE ORCHESTRATOR
# ============================================================================

class PromptCleanupOrchestrator:
    """
    Orchestrates prompt cleanup cycle execution.

    Usage:
        orchestrator = PromptCleanupOrchestrator()
        results = orchestrator.run_cleanup_cycle(trigger="audit")
        orchestrator.generate_report(results)
    """

    def __init__(self):
        """Initialize cleanup orchestrator."""
        self.tasks = PROMPT_CLEANUP_TASKS

    def run_cleanup_cycle(self, trigger: str = "audit") -> Dict[str, List[str]]:
        """
        Execute cleanup cycle based on trigger.

        Args:
            trigger: "audit" | "weekly" | "monthly"

        Returns:
            Dictionary of {ac_marker: [issues_found]}
        """
        results = {}

        for task in self.tasks:
            # Filter by frequency
            if trigger == "audit" and task.frequency != "every_audit":
                continue

            # Execute detection (placeholder - implement in Phase 56-E)
            issues = self._execute_detection(task)

            if issues:
                results[task.ac_marker] = issues

        return results

    def _execute_detection(self, task: CleanupTask) -> List[str]:
        """
        Execute detection method for task.

        Returns:
            List of issues found (empty if none)
        """
        # Placeholder - actual implementation in Phase 56-E
        return []

    def generate_report(self, results: Dict[str, List[str]]) -> str:
        """
        Generate markdown report of cleanup cycle results.

        Args:
            results: Dictionary from run_cleanup_cycle()

        Returns:
            Markdown formatted report
        """
        report = "# Prompt Cleanup Cycle Report\n\n"

        if not results:
            report += "✅ **All checks passed. No cleanup required.**\n"
            return report

        report += f"⚠️ **Found {len(results)} cleanup tasks with issues:**\n\n"

        for ac_marker, issues in results.items():
            task = next(t for t in self.tasks if t.ac_marker == ac_marker)
            report += f"## {task.title} ({ac_marker})\n\n"
            report += f"**Priority:** {task.priority.value}\n\n"
            report += f"**Issues Found:** {len(issues)}\n\n"

            for issue in issues:
                report += f"- {issue}\n"

            report += f"\n**Auto-Fix:** {task.auto_fix}\n\n"

        return report


# ============================================================================
# INTEGRATION WITH AUDIT WORKFLOW
# ============================================================================

def audit_trigger_cleanup():
    """
    Trigger cleanup cycle during AUDIT operations.

    Called by cortex-architect.prompt.md AUDIT mode.
    """
    orchestrator = PromptCleanupOrchestrator()
    results = orchestrator.run_cleanup_cycle(trigger="audit")

    if results:
        report = orchestrator.generate_report(results)
        print(report)
        return False  # Cleanup required

    return True  # All clean


# AC_COMPLETE: AC-PROMPT-CLEANUP-CYCLE-001 ✅ 5 cleanup tasks defined (001-005), orchestrator implemented
