"""Engagement Renderer — BLOCK-ENGAGEMENT-BREADCRUMB, BLOCK-ENGAGEMENT-TIMELINE, Stage Pulse.

Implements the three-tier intelligent engagement rendering system:

  Sample A — render_breadcrumb()   : italic Via line, plain-language display names (always)
  Sample B — render_stage_pulse()  : active-stage annotation with tool label (during execution)
  Sample C — render_timeline()     : collapsible <details> table with Tool column (complex ops)

Routing gate: render_engagement() selects the correct tier(s) automatically based on:
  - chain length (≥5 hops triggers Sample C)
  - WorkflowComposer presence (triggers Sample C regardless of chain length)
  - template_id + stages presence (triggers Sample B)

SSOT: .github/templates/cortex-response-templates.md §Response Header, §BLOCK-ENGAGEMENT-*
Phase 85 defined templates; chat01.md session (2026-03-01) completed the implementation.

GAP-89-07: BLOCK-ENGAGEMENT-BREADCRUMB rendering
GAP-89-08: BLOCK-ENGAGEMENT-TIMELINE rendering
"""

from __future__ import annotations

from typing import Any


class EngagementRenderer:
    """Renders engagement breadcrumb, stage pulse, and timeline for MCP responses.

    Thread-safe, stateless renderer. All three tier methods are independently
    callable; render_engagement() is the recommended entry point — it routes
    to the correct tier(s) automatically based on operation complexity signals.
    """

    ORCHESTRATOR_DISPLAY_NAMES: dict[str, str] = {
        "IntentRouter": "Classifier",
        "MasterOrchestrator": "Mission Control",
        "TDDOrchestrator": "TDD Builder",
        "AuditOrchestrator": "Audit Coordinator",
        "AuditCoordinator": "Audit Coordinator",
        "EnforcementOrchestrator": "Governance Enforcer",
        "HealthOrchestrator": "Health Monitor",
        "VacuumOrchestrator": "Workspace Cleaner",
        "RefactoringOrchestrator": "Code Improver",
        "DebuggerOrchestrator": "Debug Tracer",
        "DigestSessionOrchestrator": "Content Ingestor",
        "DesignCoordinator": "Architect",
        "PlanningOrchestrator": "Roadmap Planner",
        "RCAEngine": "Root Cause Analyst",
        "MarkerInjectionEngine": "Debug Injector",
        "WorkflowComposer": "Workflow Composer",
        "LearningOrchestrator": "Learning Engine",
        "GitOrchestrator": "Git Manager",
        "WorkflowOrchestrator": "Workflow Engine",
        "TrainerOrchestrator": "Template Trainer",
    }

    TOOL_DISPLAY_NAMES: dict[str, str] = {
        "ruff": "ruff",
        "tree-sitter": "tree-sitter",
        "Roslyn": "Roslyn (C#)",
        "cortex_validate": "Governance Validator",
        "cortex_governance": "Governance Enforcer",
        "cortex_vacuum": "Workspace Cleaner",
        "cortex_health": "Health Monitor",
        "cortex_check": "Wiring Validator",
    }

    MODE_ICONS: dict[str, str] = {
        "IMPLEMENT": "⚡",
        "FIX": "🔧",
        "REFACTOR": "♻️",
        "AUDIT": "🔎",
        "QUERY": "�",
        "DESIGN": "🎨",
        "PLAN": "📋",
        "DIGEST": "📚",
        "HEALTH": "🩺",
        "VACUUM": "🧹",
        "DEBUG": "🐛",
        "INVESTIGATE": "🔬",
        "RCA": "🔬",
        "TOTALRECALL": "🔁",
        "SYNC": "🔄",
        "TRAIN": "🎓",
    }

    COMMAND_CHAINS: dict[str, list[str]] = {
        "health": ["IntentRouter", "HealthOrchestrator"],
        "vacuum": ["IntentRouter", "VacuumOrchestrator"],
        "audit": [
            "IntentRouter", "AuditOrchestrator",
            "HealthOrchestrator", "VacuumOrchestrator",
            "EnforcementOrchestrator",
        ],
        "debug": ["IntentRouter", "DebuggerOrchestrator", "MarkerInjectionEngine"],
        "totalrecall": [
            "IntentRouter", "MasterOrchestrator",
            "AuditOrchestrator", "RefactoringOrchestrator",
        ],
        "implement": ["IntentRouter", "TDDOrchestrator"],
        "fix": ["IntentRouter", "TDDOrchestrator"],
        "refactor": ["IntentRouter", "RefactoringOrchestrator"],
        "rca": ["IntentRouter", "LearningOrchestrator", "RCAEngine"],
        "sync": ["IntentRouter", "GitOrchestrator", "WorkflowOrchestrator"],
        "train": ["IntentRouter", "TrainerOrchestrator"],
        "digest": ["IntentRouter", "DigestSessionOrchestrator"],
        "design": ["IntentRouter", "DesignCoordinator"],
        "plan": ["IntentRouter", "PlanningOrchestrator"],
    }

    def _display_name(self, class_name: str) -> str:
        return self.ORCHESTRATOR_DISPLAY_NAMES.get(class_name, class_name)

    def _tool_label(self, tool_key: str | None) -> str:
        if not tool_key:
            return "—"
        return self.TOOL_DISPLAY_NAMES.get(tool_key, tool_key)

    def _stage_icon(self, status: str) -> str:
        icons = {
            "done": "✅",
            "completed": "✅",
            "active": "🔵",
            "in_progress": "🔵",
            "pending": "⚪",
            "failed": "🔴",
        }
        return icons.get(status.lower(), "⚪")

    def render_breadcrumb(self, chain: list[str]) -> str:
        if len(chain) <= 1:
            return ""

        display_chain = " → ".join(self._display_name(n) for n in chain)
        return f"*🧭 {display_chain}*"

    def render_stage_pulse(self, stages: list[dict[str, Any]]) -> str | None:
        if not stages:
            return None

        lines: list[str] = []
        for idx, stage in enumerate(stages, start=1):
            name = stage.get("name", f"Stage {idx}")
            status = stage.get("status", "pending")
            tool = stage.get("tool")
            icon = self._stage_icon(status)

            if status in ("active", "in_progress"):
                tool_label = self._tool_label(tool)
                loop_current = stage.get("loop_current")
                loop_max = stage.get("loop_max")
                if loop_current is not None and loop_max is not None:
                    annotation = f"`← {tool_label} · loop {loop_current}/{loop_max}`"
                elif tool:
                    annotation = f"`← {tool_label}`"
                else:
                    annotation = "(in progress)"
                lines.append(f"- {icon} S{idx}: {name} {annotation}")
            else:
                lines.append(f"- {icon} S{idx}: {name}")

        return "\n".join(lines)

    def render_timeline(self, stages: list[dict[str, Any]]) -> str | None:
        if not stages:
            return None

        total_ms = sum(s.get("duration_ms", 0) for s in stages if s.get("status") in ("done", "completed"))
        hop_count = len(stages)
        total_display = f"{total_ms / 1000:.1f}s" if total_ms >= 1000 else f"{total_ms}ms"

        rows: list[str] = []
        for idx, stage in enumerate(stages, start=1):
            name = stage.get("name", f"Stage {idx}")
            status = stage.get("status", "pending")
            tool_key = stage.get("tool")
            duration_ms = stage.get("duration_ms", 0)
            icon = self._stage_icon(status)
            tool_label = self._tool_label(tool_key)
            dur_display = f"{duration_ms}ms" if duration_ms else "—"
            rows.append(f"| {name} | {tool_label} | {dur_display} | {icon} |")

        table_body = "\n".join(rows)

        return (
            f"<details>\n"
            f"<summary>⏱️ {hop_count} hops · {total_display} — "
            f"Classifier → ... (expand for full chain)</summary>\n\n"
            f"| Stage | Tool | Duration | Status |\n"
            f"|---|---|---|---|\n"
            f"{table_body}\n"
            f"| **Total** | — | **{total_display}** | ✅ |\n\n"
            f"</details>"
        )

    def render_engagement(
        self,
        chain: list[str],
        template_id: str | None = None,
        stages: list[dict[str, Any]] | None = None,
    ) -> dict[str, str | None]:
        _stages = stages or []
        hop_count = len(chain)
        has_composer = "WorkflowComposer" in chain

        breadcrumb = self.render_breadcrumb(chain)

        stage_pulse: str | None = None
        if template_id is not None and _stages:
            stage_pulse = self.render_stage_pulse(_stages)

        timeline: str | None = None
        if (hop_count >= 5 or has_composer) and _stages:
            timeline = self.render_timeline(_stages)

        return {
            "breadcrumb": breadcrumb,
            "stage_pulse": stage_pulse,
            "timeline": timeline,
        }
