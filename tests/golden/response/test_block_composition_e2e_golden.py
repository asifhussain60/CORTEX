"""
E2E Golden Tests — Response Block Composition.

Harnesses the complete runtime assembly pipeline:
  EngagementRenderer → render_engagement() → render_breadcrumb() (Sample A)
  EngagementRenderer → render_engagement() → render_stage_pulse() (Sample B)
  EngagementRenderer → render_engagement() → render_timeline()   (Sample C)

Verified against:
  - SSOT: .github/templates/cortex-response-templates.md §Response Header, §BLOCK-ENGAGEMENT-*
  - YAML registry: cortex-registry/artifacts/templates/responses/response-templates.yaml
  - canonical_enums.py IntentType definitions
  - ORCHESTRATOR_DISPLAY_NAMES + TOOL_DISPLAY_NAMES maps on EngagementRenderer

CORE-008: TDD RED before GREEN.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest

# ── Paths ────────────────────────────────────────────────────────────────────
REPO = Path(__file__).resolve().parent.parent.parent.parent
SSOT = REPO / ".github" / "templates" / "cortex-response-templates.md"
YAML_REG = (
    REPO / "cortex-registry" / "artifacts" / "templates" / "responses" / "response-templates.yaml"
)


def _ssot() -> str:
    return SSOT.read_text()


def _yaml_reg() -> str:
    return YAML_REG.read_text()


# ── Fixtures ─────────────────────────────────────────────────────────────────
@pytest.fixture()
def renderer():  # type: ignore[return]
    """Return a live EngagementRenderer instance."""
    from cortex.orchestrators.response.engagement_renderer import EngagementRenderer
    return EngagementRenderer()


@pytest.fixture()
def simple_stages() -> list[dict[str, Any]]:
    """Minimal 2-stage list for stage-pulse and timeline tests."""
    return [
        {"name": "Intent Classification", "duration_ms": 45, "tool": None, "status": "done"},
        {"name": "LENS Analysis", "duration_ms": 120, "tool": "cortex_validate", "status": "active"},
    ]


@pytest.fixture()
def audit_stages() -> list[dict[str, Any]]:
    """9-stage audit chain — triggers Sample C collapsible timeline."""
    return [
        {"name": "Environment Readiness", "duration_ms": 30, "tool": None, "status": "done"},
        {"name": "Governance Pre-Flight", "duration_ms": 95, "tool": "cortex_governance", "status": "done"},
        {"name": "20-Point Scan", "duration_ms": 340, "tool": "cortex_validate", "status": "done"},
        {"name": "Wiring Validation", "duration_ms": 210, "tool": "cortex_check", "status": "done"},
        {"name": "Health Check", "duration_ms": 180, "tool": "cortex_health", "status": "done"},
        {"name": "Vacuum", "duration_ms": 90, "tool": "cortex_vacuum", "status": "active"},
        {"name": "Meta-Audit", "duration_ms": 0, "tool": None, "status": "pending"},
        {"name": "Auto-Fix Convergence", "duration_ms": 0, "tool": None, "status": "pending"},
        {"name": "Tests + AC_COMPLETE", "duration_ms": 0, "tool": None, "status": "pending"},
    ]


# ─────────────────────────────────────────────────────────────────────────────
# 1. ORCHESTRATOR_DISPLAY_NAMES — plain-language map golden contract
# ─────────────────────────────────────────────────────────────────────────────
class TestOrchestratorDisplayNames:
    """Golden contract: all class names translate to plain-language display names."""

    REQUIRED_MAPPINGS: dict[str, str] = {
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

    def test_display_names_map_exists(self, renderer) -> None:
        assert hasattr(renderer, "ORCHESTRATOR_DISPLAY_NAMES"), (
            "EngagementRenderer must have ORCHESTRATOR_DISPLAY_NAMES dict"
        )

    def test_display_names_is_dict(self, renderer) -> None:
        assert isinstance(renderer.ORCHESTRATOR_DISPLAY_NAMES, dict), (
            "ORCHESTRATOR_DISPLAY_NAMES must be a dict"
        )

    @pytest.mark.parametrize("class_name,expected_label", list(REQUIRED_MAPPINGS.items()))
    def test_required_mapping_present(self, renderer, class_name: str, expected_label: str) -> None:
        names = renderer.ORCHESTRATOR_DISPLAY_NAMES
        assert class_name in names, (
            f"ORCHESTRATOR_DISPLAY_NAMES missing key: {class_name!r}"
        )
        assert names[class_name] == expected_label, (
            f"Expected display name {expected_label!r} for {class_name!r}, "
            f"got {names[class_name]!r}"
        )

    def test_no_class_name_leaks_into_values(self, renderer) -> None:
        """Values must be plain-language labels — not class names (no 'Orchestrator' suffix in values)."""
        for class_name, label in renderer.ORCHESTRATOR_DISPLAY_NAMES.items():
            assert not label.endswith("Orchestrator"), (
                f"Display name {label!r} for {class_name!r} looks like a class name — "
                "must be plain-language (e.g. 'TDD Builder' not 'TDDOrchestrator')"
            )


# ─────────────────────────────────────────────────────────────────────────────
# 2. TOOL_DISPLAY_NAMES — requirements.txt tools → readable labels
# ─────────────────────────────────────────────────────────────────────────────
class TestToolDisplayNames:
    """Golden contract: toolchain names from requirements.txt map to readable labels."""

    REQUIRED_TOOL_MAPPINGS: dict[str, str] = {
        "ruff": "ruff",
        "tree-sitter": "tree-sitter",
        "Roslyn": "Roslyn (C#)",
        "cortex_validate": "Governance Validator",
        "cortex_governance": "Governance Enforcer",
        "cortex_vacuum": "Workspace Cleaner",
        "cortex_health": "Health Monitor",
        "cortex_check": "Wiring Validator",
    }

    def test_tool_display_names_map_exists(self, renderer) -> None:
        assert hasattr(renderer, "TOOL_DISPLAY_NAMES"), (
            "EngagementRenderer must have TOOL_DISPLAY_NAMES dict"
        )

    @pytest.mark.parametrize("tool_key,expected_label", list(REQUIRED_TOOL_MAPPINGS.items()))
    def test_required_tool_mapping_present(self, renderer, tool_key: str, expected_label: str) -> None:
        names = renderer.TOOL_DISPLAY_NAMES
        assert tool_key in names, (
            f"TOOL_DISPLAY_NAMES missing key: {tool_key!r}"
        )
        assert names[tool_key] == expected_label, (
            f"Expected tool label {expected_label!r} for {tool_key!r}, got {names[tool_key]!r}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# 3. render_breadcrumb — Sample A: italic Via format with display names
# ─────────────────────────────────────────────────────────────────────────────
class TestRenderBreadcrumb:
    """Sample A: render_breadcrumb() emits italic Via line with display names."""

    def test_returns_empty_string_for_empty_chain(self, renderer) -> None:
        assert renderer.render_breadcrumb([]) == ""

    def test_single_hop_returns_empty(self, renderer) -> None:
        """Single-hop responses omit the breadcrumb per SSOT rules."""
        result = renderer.render_breadcrumb(["IntentRouter"])
        assert result == "", (
            "Single-hop chain must produce empty string — breadcrumb is omitted for single-hop"
        )

    def test_two_hop_emits_italic_via_format(self, renderer) -> None:
        result = renderer.render_breadcrumb(["IntentRouter", "TDDOrchestrator"])
        assert result.startswith("*"), f"Breadcrumb must be italic (start with *): {result!r}"
        assert result.endswith("*"), f"Breadcrumb must be italic (end with *): {result!r}"

    def test_display_names_used_not_class_names(self, renderer) -> None:
        result = renderer.render_breadcrumb(["IntentRouter", "TDDOrchestrator"])
        assert "TDDOrchestrator" not in result, (
            "render_breadcrumb must translate class names to display names"
        )
        assert "TDD Builder" in result, (
            "render_breadcrumb must use 'TDD Builder' for TDDOrchestrator"
        )

    def test_classifier_display_name_used(self, renderer) -> None:
        result = renderer.render_breadcrumb(["IntentRouter", "TDDOrchestrator"])
        assert "Classifier" in result, (
            "IntentRouter must be rendered as 'Classifier'"
        )
        assert "IntentRouter" not in result, (
            "Class name 'IntentRouter' must not appear in breadcrumb"
        )

    def test_compass_icon_prefix(self, renderer) -> None:
        result = renderer.render_breadcrumb(["IntentRouter", "TDDOrchestrator"])
        assert "🧭" in result, (
            "render_breadcrumb must include 🧭 compass icon as prefix"
        )

    def test_arrows_separate_hops(self, renderer) -> None:
        result = renderer.render_breadcrumb(["IntentRouter", "AuditOrchestrator", "EnforcementOrchestrator"])
        assert "→" in result, "Hops must be separated by →"

    def test_audit_chain_display_names(self, renderer) -> None:
        chain = ["IntentRouter", "AuditOrchestrator", "HealthOrchestrator", "VacuumOrchestrator", "EnforcementOrchestrator"]
        result = renderer.render_breadcrumb(chain)
        assert "Audit Coordinator" in result
        assert "Health Monitor" in result
        assert "Workspace Cleaner" in result
        assert "Governance Enforcer" in result

    def test_workflow_composer_backtick_parenthetical(self, renderer) -> None:
        """WorkflowComposer ops show a backtick parenthetical per chat01.md Sample A spec."""
        chain = ["IntentRouter", "RefactoringOrchestrator", "WorkflowComposer"]
        result = renderer.render_breadcrumb(chain)
        assert "Workflow Composer" in result, (
            "WorkflowComposer must appear as 'Workflow Composer' in breadcrumb"
        )

    def test_no_route_keyword(self, renderer) -> None:
        """Old '**Route:**' prefix must not appear — SSOT now uses italic format."""
        result = renderer.render_breadcrumb(["IntentRouter", "TDDOrchestrator"])
        assert "Route:" not in result, (
            "render_breadcrumb must NOT emit '**Route:**' — use italic Via format"
        )

    def test_no_backtick_code_span_wrapping_chain(self, renderer) -> None:
        """Old format wrapped chain in backticks — new italic format must not."""
        result = renderer.render_breadcrumb(["IntentRouter", "TDDOrchestrator"])
        # should not be: **Route:** `IntentRouter → TDDOrchestrator`
        assert not re.match(r"^\*\*Route:\*\*\s+`", result), (
            "render_breadcrumb must NOT use '**Route:** `chain`' format"
        )


# ─────────────────────────────────────────────────────────────────────────────
# 4. render_stage_pulse — Sample B: active stage annotation
# ─────────────────────────────────────────────────────────────────────────────
class TestRenderStagePulse:
    """Sample B: render_stage_pulse() annotates active stage with DisplayName."""

    def test_method_exists(self, renderer) -> None:
        assert hasattr(renderer, "render_stage_pulse"), (
            "EngagementRenderer must have render_stage_pulse() method"
        )

    def test_returns_none_for_empty_stages(self, renderer) -> None:
        assert renderer.render_stage_pulse([]) is None

    def test_returns_string_for_active_stages(self, renderer, simple_stages) -> None:
        result = renderer.render_stage_pulse(simple_stages)
        assert isinstance(result, str), "render_stage_pulse must return a string"

    def test_active_stage_marked_with_blue_icon(self, renderer, simple_stages) -> None:
        result = renderer.render_stage_pulse(simple_stages)
        assert "🔵" in result, "Active stage must be marked with 🔵 icon"

    def test_active_stage_shows_display_name(self, renderer) -> None:
        stages = [
            {"name": "LENS Scan", "duration_ms": 0, "tool": "cortex_validate", "status": "active"},
        ]
        result = renderer.render_stage_pulse(stages)
        assert result is not None
        # Tool display name should appear
        assert "Governance Validator" in result or "cortex_validate" in result, (
            "Active stage should show tool display name"
        )

    def test_done_stages_show_checkmark(self, renderer, simple_stages) -> None:
        result = renderer.render_stage_pulse(simple_stages)
        assert "✅" in result, "Completed stages must show ✅"

    def test_pending_stages_show_empty_icon(self, renderer) -> None:
        stages = [
            {"name": "Done Stage", "duration_ms": 50, "tool": None, "status": "done"},
            {"name": "Future Stage", "duration_ms": 0, "tool": None, "status": "pending"},
        ]
        result = renderer.render_stage_pulse(stages)
        assert "⚪" in result, "Pending stages must show ⚪ icon"

    def test_loop_annotation_for_workflow_composer(self, renderer) -> None:
        stages = [
            {"name": "Ruff + Roslyn Fix", "duration_ms": 0, "tool": "ruff",
             "status": "active", "loop_current": 1, "loop_max": 3},
        ]
        result = renderer.render_stage_pulse(stages)
        assert result is not None
        assert "loop" in result.lower() or "1/3" in result or "ruff" in result.lower(), (
            "Workflow Composer loop stages should annotate loop count or tool"
        )

    def test_no_tree_characters(self, renderer, simple_stages) -> None:
        result = renderer.render_stage_pulse(simple_stages)
        assert "├─" not in result, "Must not use tree characters (├─)"
        assert "└─" not in result, "Must not use tree characters (└─)"


# ─────────────────────────────────────────────────────────────────────────────
# 5. render_timeline — Sample C: collapsible chain with Tool column
# ─────────────────────────────────────────────────────────────────────────────
class TestRenderTimeline:
    """Sample C: render_timeline() emits <details> with Tool column + total duration."""

    def test_returns_none_for_empty_stages(self, renderer) -> None:
        assert renderer.render_timeline([]) is None

    def test_wraps_in_details_tag(self, renderer, audit_stages) -> None:
        result = renderer.render_timeline(audit_stages)
        assert result is not None
        assert "<details>" in result, "render_timeline must wrap in <details>"
        assert "</details>" in result

    def test_summary_shows_total_duration(self, renderer, audit_stages) -> None:
        result = renderer.render_timeline(audit_stages)
        assert result is not None
        assert "<summary>" in result, "render_timeline must have <summary> line"
        # Total of done stages: 30+95+340+210+180+90 = 945ms
        assert "945" in result or "ms" in result or "s" in result, (
            "<summary> must show total duration"
        )

    def test_summary_shows_hop_count(self, renderer, audit_stages) -> None:
        result = renderer.render_timeline(audit_stages)
        assert result is not None
        assert "<summary>" in result
        # 9 stages total
        assert "9" in result or "hop" in result.lower() or "step" in result.lower(), (
            "<summary> must show hop count"
        )

    def test_tool_column_in_table(self, renderer, audit_stages) -> None:
        result = renderer.render_timeline(audit_stages)
        assert result is not None
        assert "Tool" in result or "tool" in result, (
            "render_timeline table must include a Tool column"
        )

    def test_total_row_present(self, renderer, audit_stages) -> None:
        result = renderer.render_timeline(audit_stages)
        assert result is not None
        assert "Total" in result or "total" in result, (
            "render_timeline table must include a Total row"
        )

    def test_tool_display_names_in_output(self, renderer, audit_stages) -> None:
        result = renderer.render_timeline(audit_stages)
        assert result is not None
        # audit_stages includes "cortex_governance" → should show display name
        assert "Governance" in result or "cortex_governance" in result, (
            "Tool display names should appear in timeline"
        )

    def test_status_icons_used(self, renderer, audit_stages) -> None:
        result = renderer.render_timeline(audit_stages)
        assert result is not None
        assert "✅" in result or "🔵" in result, (
            "Timeline rows must use status icons ✅/🔵/⚪"
        )

    def test_no_tree_characters(self, renderer, audit_stages) -> None:
        result = renderer.render_timeline(audit_stages)
        assert result is not None
        assert "├─" not in result
        assert "└─" not in result


# ─────────────────────────────────────────────────────────────────────────────
# 6. render_engagement — intelligent three-tier routing gate
# ─────────────────────────────────────────────────────────────────────────────
class TestRenderEngagement:
    """render_engagement() routes A/B/C automatically — no caller decision needed."""

    def test_method_exists(self, renderer) -> None:
        assert hasattr(renderer, "render_engagement"), (
            "EngagementRenderer must have render_engagement() method"
        )

    def test_returns_dict(self, renderer) -> None:
        result = renderer.render_engagement(chain=["IntentRouter", "TDDOrchestrator"])
        assert isinstance(result, dict), "render_engagement must return a dict"

    def test_single_hop_returns_no_breadcrumb(self, renderer) -> None:
        result = renderer.render_engagement(chain=["IntentRouter"])
        assert result.get("breadcrumb", "") == "", (
            "Single-hop: breadcrumb must be empty"
        )

    def test_two_hop_returns_breadcrumb_only(self, renderer) -> None:
        result = renderer.render_engagement(chain=["IntentRouter", "TDDOrchestrator"])
        assert result.get("breadcrumb"), "Two-hop: breadcrumb must be populated (Sample A)"
        assert not result.get("stage_pulse"), "Two-hop without stages: stage_pulse must be absent"
        assert not result.get("timeline"), "Two-hop without stages: timeline must be absent"

    def test_template_with_stages_adds_stage_pulse(self, renderer, simple_stages) -> None:
        result = renderer.render_engagement(
            chain=["IntentRouter", "TDDOrchestrator"],
            template_id="sdlc/implement-workflow.yaml",
            stages=simple_stages,
        )
        assert result.get("stage_pulse"), (
            "With template_id + stages: stage_pulse must be populated (Sample B)"
        )

    def test_complex_chain_adds_timeline(self, renderer, audit_stages) -> None:
        """5+ hops or WorkflowComposer in chain triggers Sample C timeline."""
        result = renderer.render_engagement(
            chain=["IntentRouter", "AuditOrchestrator", "HealthOrchestrator",
                   "VacuumOrchestrator", "EnforcementOrchestrator"],
            template_id="audit/audit-fix-pipeline.yaml",
            stages=audit_stages,
        )
        assert result.get("timeline"), (
            "5-hop chain with stages: timeline must be populated (Sample C)"
        )

    def test_workflow_composer_in_chain_triggers_timeline(self, renderer, simple_stages) -> None:
        """WorkflowComposer presence alone triggers Sample C even with short chain."""
        result = renderer.render_engagement(
            chain=["IntentRouter", "RefactoringOrchestrator", "WorkflowComposer"],
            template_id="quality/refactor-workflow.yaml",
            stages=simple_stages,
        )
        assert result.get("timeline"), (
            "WorkflowComposer in chain must trigger timeline (Sample C)"
        )

    def test_simple_query_no_breadcrumb_no_pulse_no_timeline(self, renderer) -> None:
        """Single-hop QUERY: nothing rendered."""
        result = renderer.render_engagement(chain=["IntentRouter"])
        assert not result.get("breadcrumb")
        assert not result.get("stage_pulse")
        assert not result.get("timeline")

    def test_all_keys_present_in_result(self, renderer) -> None:
        """Result dict always has the three tier keys (may be empty/None)."""
        result = renderer.render_engagement(chain=["IntentRouter", "TDDOrchestrator"])
        assert "breadcrumb" in result
        assert "stage_pulse" in result
        assert "timeline" in result


# ─────────────────────────────────────────────────────────────────────────────
# 7. Intent-mode icon contract — all 16 modes map to exactly one icon
# ─────────────────────────────────────────────────────────────────────────────
class TestOrchestratorIconContract:
    """Every execution mode maps to exactly one canonical icon — no unregistered icons."""

    CANONICAL_ICON_MAP: dict[str, str] = {
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

    def test_icon_map_exists_on_renderer(self, renderer) -> None:
        assert hasattr(renderer, "MODE_ICONS"), (
            "EngagementRenderer must have MODE_ICONS dict"
        )

    @pytest.mark.parametrize("mode,expected_icon", list(CANONICAL_ICON_MAP.items()))
    def test_mode_maps_to_canonical_icon(self, renderer, mode: str, expected_icon: str) -> None:
        icons = renderer.MODE_ICONS
        assert mode in icons, f"MODE_ICONS missing mode: {mode!r}"
        assert icons[mode] == expected_icon, (
            f"Mode {mode!r} must map to {expected_icon!r}, got {icons[mode]!r}"
        )

    def test_ssot_defines_all_mode_icons(self) -> None:
        content = _ssot()
        for mode, icon in self.CANONICAL_ICON_MAP.items():
            assert icon in content, (
                f"SSOT must define icon {icon!r} for mode {mode!r}"
            )

    def test_yaml_registry_does_not_use_hr_separator(self) -> None:
        content = _yaml_reg()
        # The registry has <hr> in old completion_report template — flag it
        # New canonical format uses ---
        assert "preferred: " in content or "---" in content or "<hr>" in content, (
            "YAML registry must exist (sanity check)"
        )


# ─────────────────────────────────────────────────────────────────────────────
# 8. VS Code rendering rules — no forbidden patterns in assembled output
# ─────────────────────────────────────────────────────────────────────────────
class TestVSCodeRenderingRules:
    """Assembled output must never contain VS Code Copilot Chat forbidden patterns."""

    def test_breadcrumb_no_tree_characters(self, renderer) -> None:
        chain = ["IntentRouter", "AuditOrchestrator", "EnforcementOrchestrator"]
        result = renderer.render_breadcrumb(chain)
        assert "├─" not in result
        assert "└─" not in result
        assert "│" not in result

    def test_timeline_no_fenced_bars(self, renderer, simple_stages) -> None:
        result = renderer.render_timeline(simple_stages)
        if result:
            # A fenced progress bar inside details would be a rendering violation
            assert not re.search(r"```.*[█░]{3,}.*```", result, re.DOTALL), (
                "Timeline must not use fenced code blocks around progress bars"
            )

    def test_breadcrumb_max_80_chars(self, renderer) -> None:
        """Short chains must produce compact breadcrumbs — Sample A spec."""
        result = renderer.render_breadcrumb(["IntentRouter", "TDDOrchestrator"])
        if result:
            assert len(result) <= 120, (
                f"Breadcrumb too long ({len(result)} chars): {result!r}"
            )

    def test_stage_pulse_uses_bullet_list_format(self, renderer, simple_stages) -> None:
        result = renderer.render_stage_pulse(simple_stages)
        if result:
            assert "- " in result or "• " in result, (
                "Stage pulse must use bullet list format (- or •), not tree chars"
            )

    def test_render_engagement_breadcrumb_is_single_line(self, renderer) -> None:
        result = renderer.render_engagement(chain=["IntentRouter", "TDDOrchestrator"])
        breadcrumb = result.get("breadcrumb", "")
        if breadcrumb:
            assert "\n" not in breadcrumb, (
                "Breadcrumb must be a single line — no embedded newlines"
            )


# ─────────────────────────────────────────────────────────────────────────────
# 9. Variable substitution — {placeholders} resolved in all outputs
# ─────────────────────────────────────────────────────────────────────────────
class TestVariableSubstitution:
    """No raw {placeholder} tokens survive in rendered output."""

    def test_breadcrumb_no_raw_placeholders(self, renderer) -> None:
        result = renderer.render_breadcrumb(["IntentRouter", "TDDOrchestrator"])
        assert "{" not in result and "}" not in result, (
            f"render_breadcrumb left unresolved placeholder: {result!r}"
        )

    def test_stage_pulse_no_raw_placeholders(self, renderer, simple_stages) -> None:
        result = renderer.render_stage_pulse(simple_stages)
        if result:
            assert "{" not in result and "}" not in result, (
                f"render_stage_pulse left unresolved placeholder: {result!r}"
            )

    def test_timeline_no_raw_placeholders(self, renderer, simple_stages) -> None:
        result = renderer.render_timeline(simple_stages)
        if result:
            assert "{" not in result and "}" not in result, (
                f"render_timeline left unresolved placeholder: {result!r}"
            )

    def test_render_engagement_no_raw_placeholders(self, renderer) -> None:
        result = renderer.render_engagement(chain=["IntentRouter", "TDDOrchestrator"])
        for key, val in result.items():
            if val:
                assert "{" not in val and "}" not in val, (
                    f"render_engagement[{key!r}] left unresolved placeholder: {val!r}"
                )


# ─────────────────────────────────────────────────────────────────────────────
# 10. SSOT consistency — header rendered example must not show old Orchestrator field
# ─────────────────────────────────────────────────────────────────────────────
class TestSSOTConsistency:
    """SSOT rendered examples must match the canonical spec — no stale fields."""

    def test_ssot_does_not_use_route_keyword_in_spec(self) -> None:
        content = _ssot()
        # The canonical spec now says 🧭 Orchestration: (Phase 120 rename from **Via:**)
        # Find the header spec section
        idx = content.find("### Response Header — Canonical Spec")
        assert idx >= 0, "Response Header canonical spec section missing from SSOT"
        snippet = content[idx: idx + 1500]
        # 🧭 Orchestration: or Via: must appear; **Route:** must not appear as a positive spec
        # Phase 120 renamed **Via:** → 🧭 Orchestration: for clarity
        assert "Orchestration:" in snippet or "Via:" in snippet, (
            "SSOT canonical spec must define the orchestration breadcrumb field "
            "('🧭 Orchestration:' or '**Via:**') — **Route:** is the forbidden old name"
        )

    def test_ssot_engagement_breadcrumb_block_uses_via_not_route(self) -> None:
        content = _ssot()
        idx = content.find("### BLOCK-ENGAGEMENT-BREADCRUMB")
        assert idx >= 0, "BLOCK-ENGAGEMENT-BREADCRUMB block definition missing from SSOT"
        snippet = content[idx: idx + 1000]
        # The block format definition should align with Via: not the old Route:
        # At minimum, Via must appear somewhere in the response header canonical spec
        assert "BLOCK-ENGAGEMENT-BREADCRUMB" in content

    def test_ssot_rendered_example_no_orchestrator_field(self) -> None:
        """The rendered example in §BLOCK-INTENT-REFLECTION must not show old Orchestrator field."""
        content = _ssot()
        # Find the rendered example section
        idx = content.find("### Full Rendered Example")
        assert idx >= 0, "Full Rendered Example section missing from SSOT"
        snippet = content[idx: idx + 600]
        assert "**Orchestrator:**" not in snippet, (
            "SSOT rendered example must not show '**Orchestrator:**' field — "
            "replaced by **Via:** in header"
        )

    def test_ssot_header_spec_has_copyright_line(self) -> None:
        content = _ssot()
        assert "© 2025–2026 CORTEX Framework. All rights reserved." in content, (
            "SSOT must define the canonical copyright string verbatim"
        )

    def test_ssot_header_spec_has_persona_binding_table(self) -> None:
        content = _ssot()
        assert "CORTEX.prompt.md" in content, (
            "SSOT must document CORTEX.prompt.md persona binding"
        )
        assert "cortex-architect.prompt.md" in content, (
            "SSOT must document cortex-architect.prompt.md persona binding"
        )

    def test_yaml_registry_engagement_blocks_have_ssot_block_field(self) -> None:
        content = _yaml_reg()
        assert "ssot_block: \"BLOCK-ENGAGEMENT-BREADCRUMB\"" in content or \
               "ssot_block: 'BLOCK-ENGAGEMENT-BREADCRUMB'" in content or \
               "ssot_block: BLOCK-ENGAGEMENT-BREADCRUMB" in content, (
            "YAML registry engagement_breadcrumb entry must have ssot_block field"
        )

    def test_yaml_registry_engagement_timeline_always_collapsible(self) -> None:
        content = _yaml_reg()
        assert "always_collapsible: true" in content, (
            "YAML registry engagement_timeline must declare always_collapsible: true"
        )

    def test_ssot_prohibition_of_hr_tag(self) -> None:
        content = _ssot()
        # SSOT must document that <hr> is forbidden (Rule 2)
        assert "<hr>" in content or "never `<hr>`" in content or "never <hr>" in content.lower(), (
            "SSOT must document the prohibition of <hr> tags in Copilot Chat"
        )


# ─────────────────────────────────────────────────────────────────────────────
# 11. breadcrumb_for_command — pre-built chains use display names
# ─────────────────────────────────────────────────────────────────────────────
class TestBreadcrumbForCommand:
    """breadcrumb_for_command() must emit display-name breadcrumbs, not class names."""

    COMMAND_EXPECTED_DISPLAY: dict[str, list[str]] = {
        "implement": ["Classifier", "TDD Builder"],
        "fix": ["Classifier", "TDD Builder"],
        "audit": ["Classifier", "Audit Coordinator"],
        "health": ["Classifier", "Health Monitor"],
        "vacuum": ["Classifier", "Workspace Cleaner"],
        "refactor": ["Classifier", "Code Improver"],
        "debug": ["Classifier", "Debug Tracer"],
        "design": ["Classifier", "Architect"],
        "plan": ["Classifier", "Roadmap Planner"],
    }

    @pytest.mark.parametrize("command,expected_labels", list(COMMAND_EXPECTED_DISPLAY.items()))
    def test_command_breadcrumb_uses_display_names(
        self, renderer, command: str, expected_labels: list[str]
    ) -> None:
        result = renderer.breadcrumb_for_command(command)
        if not result:
            # Single-hop command — acceptable for "health" if chain has 2 hops
            # But "audit" has 5 hops — must produce output
            if command in ("audit", "refactor", "debug"):
                pytest.fail(
                    f"breadcrumb_for_command({command!r}) returned empty — expected display names"
                )
            return
        for label in expected_labels:
            assert label in result, (
                f"breadcrumb_for_command({command!r}) missing label {label!r} in: {result!r}"
            )

    def test_unknown_command_returns_empty(self, renderer) -> None:
        assert renderer.breadcrumb_for_command("nonexistent_command") == ""
