#!/usr/bin/env python3
"""
Enhanced Response Template Generator

⚠️ DEPRECATED: This module is deprecated as of 2026-02-13 (Phase 53).
Use cortex/orchestrators/response/simple_response_formatter.py instead.

Reason: Simpler one-function approach provides same user value.
- Old: Multiple classes, color detection, pattern matching
- New: format_response(title, sections, metrics, next_steps)
- Result: Same chat01.md clarity with 90% less code

This file remains for backward compatibility with existing orchestrators.

Purpose: Semantic color-coded response headers for CORTEX
Version: 2.0 - SSOT Compliance (40-char separators)
Integration: cortex-architect.prompt.md + agents

Response Flow:
  ┌──────────────────────────────────────────────────────┐
  │  1. User request → MasterOrchestrator                │
  ├──────────────────────────────────────────────────────┤
  │  2. Detect section status from title keywords        │
  │     (complete, blocked, pending, etc.)               │
  ├──────────────────────────────────────────────────────┤
  │  3. Assign semantic emoji + color                    │
  │     ✅ Complete | 🔵 In Progress | 🔴 Blocked       │
  ├──────────────────────────────────────────────────────┤
  │  4. Generate markdown header with status emoji       │
  ├──────────────────────────────────────────────────────┤
  │  5. Render to chat (Copilot processes markdown)      │
  └──────────────────────────────────────────────────────┘

Status Mappings:
  • Complete/Success: ✅ (Green) - Done, passed, ready
  • In Progress: 🔵 (Orange) - Pending, next, todo
  • Blocked: 🔴 (Red) - Failed, error, critical
  • Planned: ➡️ (Orange) - Upcoming work
  • Design/Info: 🎨 (Blue) - Analysis, information
  • Warning: ⚠️ (Yellow) - Caution, attention needed
  • Critical: 🚨 (Red) - Emergency, blocker

Usage Examples:
  # Auto-detect status from title
  header = ResponseTemplate.create_header("Refactoring Complete")
  # → "## ✅ Refactoring Complete"
  
  # Create box-framed section with 40-char border
  box = ResponseTemplate.create_box_section("Summary", "Implementation done")
  # → ────────────────────────────────────────
  #   Summary
  #   ────────────────────────────────────────
  #   Implementation done
  #   ────────────────────────────────────────
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


# SSOT Constants (response-format-standards.md)
BOX_SEPARATOR = "-" * 40  # Exactly 40 chars per SSOT
BOX_WIDTH = 40


class SectionStatus(Enum):
    """
    Section status types with semantic emoji mappings.
    
    Format: (emoji, color, keywords)
    
    Status Types:
      COMPLETE (✅):
        • Visual: Green checkmark
        • Usage: Finished operations, passed tests, ready states
        • Keywords: complete, completed, success, passed, ready, done
        • Example: "## ✅ Testing Complete"
        
      IN_PROGRESS (🔵):
        • Visual: Blue circle
        • Usage: Current work, pending operations, next steps
        • Keywords: in progress, pending, next, todo, working
        • Example: "## 🔵 Implementation In Progress"
        
      BLOCKED (🔴):
        • Visual: Red circle
        • Usage: Critical failures, blocked operations
        • Keywords: blocked, failed, error, critical
        • Example: "## 🔴 Test Execution Blocked"
        
      PLANNED (➡️):
        • Visual: Right arrow (orange)
        • Usage: Upcoming work, future steps, planning
        • Keywords: planned, upcoming, next steps
        • Example: "## ➡️ Planned Refactoring"
        
      DESIGN (🎨):
        • Visual: Artist palette (blue)
        • Usage: Analysis, design docs, informational content
        • Keywords: design, analysis, information, overview
        • Example: "## 🎨 Architecture Analysis"
        
      WARNING (⚠️):
        • Visual: Warning triangle (yellow)
        • Usage: Caution needed, attention required
        • Keywords: warning, caution, attention
        • Example: "## ⚠️ Deprecation Warning"
        
      CRITICAL (🚨):
        • Visual: Siren/emergency (red)
        • Usage: Emergency situations, critical blockers
        • Keywords: critical, emergency, blocker
        • Example: "## 🚨 Critical Security Issue"
    """
    COMPLETE = ("✅", "green", "Completion, success, PASSED, READY")
    IN_PROGRESS = ("🔵", "orange", "In Progress, PENDING, NEXT, TODO")
    BLOCKED = ("🔴", "red", "Critical, BLOCKED, FAILED, ERROR")
    PLANNED = ("➡️", "orange", "Next steps, upcoming work, planning")
    DESIGN = ("🎨", "blue", "Analysis, design, information")
    WARNING = ("⚠️", "yellow", "Warning, caution, attention needed")
    CRITICAL = ("🚨", "red", "Critical blocker, emergency")

@dataclass
class EnhancedHeader:
    """Enhanced header with status color coding."""
    title: str
    status: SectionStatus
    level: int = 2  # H2 by default

    def render(self) -> str:
        """Render header with status emoji and markdown."""
        emoji, color, _ = self.status.value
        markdown_level = "#" * self.level
        return f"{markdown_level} {emoji} {self.title}"

class ResponseTemplate:
    """Response template manager with semantic headers."""

    # Header color rules based on common patterns
    HEADER_PATTERNS = {
        "complete": SectionStatus.COMPLETE,
        "completed": SectionStatus.COMPLETE,
        "success": SectionStatus.COMPLETE,
        "passed": SectionStatus.COMPLETE,
        "ready": SectionStatus.COMPLETE,

        "in progress": SectionStatus.IN_PROGRESS,
        "pending": SectionStatus.IN_PROGRESS,
        "next": SectionStatus.IN_PROGRESS,
        "todo": SectionStatus.IN_PROGRESS,

        "blocked": SectionStatus.BLOCKED,
        "critical": SectionStatus.CRITICAL,
        "failed": SectionStatus.BLOCKED,
        "error": SectionStatus.BLOCKED,

        "planned": SectionStatus.PLANNED,
        "upcoming": SectionStatus.PLANNED,

        "design": SectionStatus.DESIGN,
        "analysis": SectionStatus.DESIGN,
        "information": SectionStatus.DESIGN,

        "warning": SectionStatus.WARNING,
        "caution": SectionStatus.WARNING,
    }

    @staticmethod
    def detect_status(title: str) -> SectionStatus:
        """Detect section status from title keywords."""
        title_lower = title.lower()

        for pattern, status in ResponseTemplate.HEADER_PATTERNS.items():
            if pattern in title_lower:
                return status

        # Default to design/info if no match
        return SectionStatus.DESIGN

    @staticmethod
    def create_header(title: str, auto_detect: bool = True) -> str:
        """Create color-coded header."""
        if auto_detect:
            status = ResponseTemplate.detect_status(title)
        else:
            status = SectionStatus.DESIGN

        header = EnhancedHeader(title=title, status=status)
        return header.render()

    @staticmethod
    def create_box_header(title: str, status: Optional[SectionStatus] = None) -> str:
        """Create box-framed header with separator lines (SSOT compliant)."""
        if status is None:
            status = ResponseTemplate.detect_status(title)
        emoji, _, _ = status.value
        return f"""{BOX_SEPARATOR}
{emoji} {title}
{BOX_SEPARATOR}"""

    @staticmethod
    def create_box_section(title: str, content: str) -> str:
        """Create box-framed section with content."""
        return f"""{BOX_SEPARATOR}
{title}
{BOX_SEPARATOR}

{content}

{BOX_SEPARATOR}"""

    @staticmethod
    def session_summary(
        session_name: str,
        completed_items: list,
        in_progress_items: list,
        blocked_items: list,
        next_steps: list,
        token_usage: Optional[tuple] = None
    ) -> str:
        """Generate semantic session summary with color-coded headers."""

        # Determine overall status
        if blocked_items:
            overall_status = SectionStatus.BLOCKED
        elif in_progress_items:
            overall_status = SectionStatus.IN_PROGRESS
        else:
            overall_status = SectionStatus.COMPLETE

        emoji, _, _ = overall_status.value

        summary = f"""{BOX_SEPARATOR}
## {emoji} SESSION SUMMARY
**Session:** {session_name} | **Status:** {emoji} {overall_status.name}
{BOX_SEPARATOR}

"""

        # Token usage section (if provided)
        if token_usage:
            used, total = token_usage
            pct = int((used / total) * 100)
            status_emoji = "🟢" if pct < 75 else "🟠" if pct < 90 else "🔴"
            summary += f"""## 📊 Token Usage
**Used:** {used}k / {total}k ({pct}%)
**Status:** {status_emoji} {'Optimal' if pct < 75 else 'Caution' if pct < 90 else 'Critical'}

"""

        # Completed items
        if completed_items:
            summary += "## ✅ COMPLETED\n"
            for item in completed_items:
                summary += f"- ✅ {item}\n"
            summary += "\n"

        # In Progress items
        if in_progress_items:
            summary += "## 🔵 IN PROGRESS\n"
            for item in in_progress_items:
                summary += f"- 🔵 {item}\n"
            summary += "\n"

        # Blocked items
        if blocked_items:
            summary += "## 🔴 BLOCKED\n"
            for item in blocked_items:
                summary += f"- 🔴 {item}\n"
            summary += "\n"

        # Next steps
        if next_steps:
            summary += "## ➡️ NEXT STEPS\n"
            for i, step in enumerate(next_steps, 1):
                summary += f"{i}. {step}\n"
            summary += "\n"

        summary += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

        return summary

# Example usage in agents
if __name__ == "__main__":
    # Example 1: Create headers with auto-detection
    print("=== EXAMPLE 1: Auto-Detected Headers ===\n")
    print(ResponseTemplate.create_header("FIX 1: Comprehensive MCP Governance Tools"))
    print(ResponseTemplate.create_header("FIX 2: YAML Loader Enhancement"))
    print(ResponseTemplate.create_header("DEPLOY: Critical Database Issue"))
    print(ResponseTemplate.create_header("NEXT: Source Code Consolidation"))
    print()

    # Example 2: Generate session summary
    print("=== EXAMPLE 2: Session Summary ===\n")
    summary = ResponseTemplate.session_summary(
        session_name="FIX SESSION 1-3",
        completed_items=[
            "5 production-grade MCP governance tools (23/23 tests)",
            "YAML loader enhancement with Tier 1/2 support (33/33 tests)",
        ],
        in_progress_items=[
            "Source code consolidation analysis",
        ],
        blocked_items=[],
        next_steps=[
            "Integrate enhanced template into cortex-architect.prompt.md",
            "Update all agent response generators",
            "Document color coding standards",
        ],
        token_usage=(160, 200)
    )
    print(summary)

    # Example 3: Manual status selection
    print("=== EXAMPLE 3: Manual Status Selection ===\n")
    header = EnhancedHeader(
        title="Critical Infrastructure Issue",
        status=SectionStatus.CRITICAL
    )
    print(header.render())
