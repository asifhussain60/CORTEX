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

    # ── Display name maps (SSOT for plain-language labels) ───────────────────

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
        "cortex_lens": "LENS Analyser",
        "cortex_check": "Wiring Validator",
    }

    # ── Mode icon registry (SSOT §Mode Icons) ────────────────────────────────

    MODE_ICONS: dict[str, str] = {
        "IMPLEMENT": "⚡",
        "FIX": "🔧",
        "REFACTOR": "♻️",
        "AUDIT": "🔎",
        "QUERY": "📖",
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

    # ── Phase 91: Pre-built routing chains for common commands ───────────────

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

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _display_name(self, class_name: str) -> str:
        """Translate an orchestrator class name to its plain-language display name.

        Args:
            class_name: Python class name (e.g. ``"TDDOrchestrator"``).

        Returns:
            Plain-language display name, or the original name if not mapped.
        """
        return self.ORCHESTRATOR_DISPLAY_NAMES.get(class_name, class_name)

    def _tool_label(self, tool_key: str | None) -> str:
        """Translate a tool key to its readable label.

        Args:
            tool_key: Tool identifier (e.g. ``"cortex_lens"``), or ``None``.

        Returns:
            Readable label, or empty string for None.
        """
        if not tool_key:
            return "—"
        return self.TOOL_DISPLAY_NAMES.get(tool_key, tool_key)

    def _stage_icon(self, status: str) -> str:
        """Return the status icon for a stage entry.

        Args:
            status: One of ``"done"``, ``"active"``, ``"pending"``, ``"failed"``.

        Returns:
            Matching status icon string.
        """
        icons = {
            "done": "✅",
            "completed": "✅",
            "active": "🔵",
            "in_progress": "🔵",
            "pending": "⚪",
            "failed": "🔴",
        }
        return icons.get(status.lower(), "⚪")

    # ── Sample A — render_breadcrumb ─────────────────────────────────────────

    def render_breadcrumb(self, chain: list[str]) -> str:
        """Render BLOCK-ENGAGEMENT-BREADCRUMB — Sample A: italic Via line with display names.

        Single-hop responses return empty string (omitted per SSOT rules).
        Multi-hop responses return an italic line with 🧭 prefix and → separators.

        Args:
            chain: Ordered list of orchestrator/engine class names.

        Returns:
            Single-line italic markdown string, or ``""`` for 0–1 hop chains.

        Example:
            >>> renderer = EngagementRenderer()
            >>> renderer.render_breadcrumb(["IntentRouter", "TDDOrchestrator"])
            '*🧭 Classifier → TDD Builder*'
        """
        if len(chain) <= 1:
            return ""

        display_chain = " → ".join(self._display_name(n) for n in chain)
        return f"*🧭 {display_chain}*"

    # ── Sample B — render_stage_pulse ────────────────────────────────────────

    def render_stage_pulse(self, stages: list[dict[str, Any]]) -> str | None:
        """Render BLOCK-STAGE-PROGRESS — Sample B: active-stage pulse annotation.

        Each stage appears as a bullet with its status icon. The active stage
        is annotated with the tool display name (and loop count when available).

        Args:
            stages: List of stage dicts with keys:
                - ``name`` (str): Human-readable stage name.
                - ``status`` (str): ``"done"`` | ``"active"`` | ``"pending"`` | ``"failed"``.
                - ``tool`` (str | None): Tool key for active-stage annotation.
                - ``duration_ms`` (int): Elapsed duration for done stages.
                - ``loop_current`` (int, optional): Current loop number (Workflow Composer).
                - ``loop_max`` (int, optional): Maximum loops (Workflow Composer).

        Returns:
            Formatted bullet-list string, or ``None`` for empty stage lists.
        """
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

    # ── Sample C — render_timeline ───────────────────────────────────────────

    def render_timeline(self, stages: list[dict[str, Any]]) -> str | None:
        """Render BLOCK-ENGAGEMENT-TIMELINE — Sample C: collapsible <details> with Tool column.

        The <summary> line shows total hop count and cumulative duration of
        completed stages. The inner table includes Orchestrator/Stage, Tool,
        Duration, and Status columns plus a Total row.

        Args:
            stages: Same format as ``render_stage_pulse()``.

        Returns:
            HTML ``<details>`` block string, or ``None`` for empty stage lists.
        """
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

    # ── Routing gate — render_engagement ─────────────────────────────────────

    def render_engagement(
        self,
        chain: list[str],
        template_id: str | None = None,
        stages: list[dict[str, Any]] | None = None,
    ) -> dict[str, str | None]:
        """Intelligent three-tier routing gate.

        Selects the correct rendering tier(s) automatically — callers do not
        need to decide which sample to use:

        - **Sample A** (breadcrumb): Always, when chain has 2+ hops.
        - **Sample B** (stage_pulse): When ``template_id`` is provided AND ``stages`` present.
        - **Sample C** (timeline): When chain has ≥5 hops OR ``WorkflowComposer`` is in chain,
          AND ``stages`` is present.

        Args:
            chain: Ordered list of orchestrator class names (routing path).
            template_id: Workflow template resolved by WorkflowGateway, or ``None``.
            stages: Stage list for pulse/timeline rendering, or ``None``.

        Returns:
            Dict with keys ``"breadcrumb"``, ``"stage_pulse"``, ``"timeline"``
            (each is a string or ``None``).
        """
        _stages = stages or []
        hop_count = len(chain)
        has_composer = "WorkflowComposer" in chain

        # Sample A — italic breadcrumb (always for 2+ hops)
        breadcrumb = self.render_breadcrumb(chain)

        # Sample B — stage pulse (template looping + stages present)
        stage_pulse: str | None = None
        if template_id is not None and _stages:
            stage_pulse = self.render_stage_pulse(_stages)

        # Sample C — collapsible timeline (complex ops: 5+ hops or Composer present)
        timeline: str | None = None
        if (hop_count >= 5 or has_composer) and _stages:
            timeline = self.render_timeline(_stages)

        return {
            "breadcrumb": breadcrumb,
            "stage_pulse": stage_pulse,
            "timeline": timeline,
        }

    # ── Convenience helper ───────────────────────────────────────────────────

    def breadcrumb_for_command(self, command: str) -> str:
        """Render Sample A breadcrumb for a known CORTEX command.

        Args:
            command: Command name (e.g. ``"audit"``, ``"health"``, ``"debug"``).

        Returns:
            Italic breadcrumb string with display names, or ``""`` if unknown.
        """
        chain = self.COMMAND_CHAINS.get(command.lower(), [])
        return self.render_breadcrumb(chain)
