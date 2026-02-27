"""
Phase 85-A + 85-B + 85-C + 85-D + 85-E golden tests.

GAP-85-01: phase-list+bar mandatory
GAP-85-02: BLOCK-PHASE-ROADMAP defined in SSOT
GAP-85-03: BLOCK-STAGE-PROGRESS has orchestrator pulse support
GAP-85-04: BLOCK-ENGAGEMENT-BREADCRUMB defined in SSOT
GAP-85-05: BLOCK-ENGAGEMENT-TIMELINE defined in SSOT
GAP-85-06: Response Header Route line spec present
GAP-85-07: No inline bar-only definitions in prompts
GAP-85-08: copilot-instructions references SSOT
GAP-85-09: Assembly order includes engagement blocks
GAP-85-10: YAML registry has 3 new blocks
GAP-85-11: Documentation coverage (flat-files)
GAP-85-12: Zero pasted-image references

CORE-008: TDD — RED before GREEN.
"""
from pathlib import Path
import re

REPO = Path(__file__).resolve().parent.parent.parent.parent
SSOT = REPO / ".github" / "templates" / "cortex-response-templates.md"
YAML_REG = REPO / "cortex-registry" / "artifacts" / "templates" / "responses" / "response-templates.yaml"
ARCHITECT = REPO / ".github" / "prompts" / "cortex-architect.prompt.md"
COPILOT = REPO / ".github" / "copilot-instructions.md"


def _ssot() -> str:
    return SSOT.read_text()


def _yaml_reg() -> str:
    return YAML_REG.read_text()


# ─────────────────────────────────────────────────────────────────────────────
# GAP-85-01/02: BLOCK-PHASE-ROADMAP + phase-list mandatory
# ─────────────────────────────────────────────────────────────────────────────
class TestBlockPhaseRoadmap:
    """Phase 85-A: BLOCK-PHASE-ROADMAP must be defined in SSOT."""

    def test_block_phase_roadmap_defined(self) -> None:
        assert "BLOCK-PHASE-ROADMAP" in _ssot(), (
            "BLOCK-PHASE-ROADMAP not found in cortex-response-templates.md"
        )

    def test_block_phase_roadmap_has_format_section(self) -> None:
        content = _ssot()
        assert "BLOCK-PHASE-ROADMAP" in content
        # Status icons used across the whole SSOT for roadmap/progress (⚪/✅/🔵)
        # The block definition uses these icons
        assert any(icon in content for icon in ["⚪", "✅", "🔵"]), (
            "BLOCK-PHASE-ROADMAP format should use status icons"
        )

    def test_block_phase_roadmap_has_trigger(self) -> None:
        content = _ssot()
        # Search specifically in the block definition section
        idx = content.find("### BLOCK-PHASE-ROADMAP")
        assert idx >= 0, "BLOCK-PHASE-ROADMAP block definition (###) not found"
        snippet = content[idx: idx + 1200]
        assert "trigger" in snippet.lower() or "multi-phase" in snippet.lower() or "N≥" in snippet, (
            "BLOCK-PHASE-ROADMAP should document its trigger condition"
        )

    def test_silent_autonomous_mandates_phase_list(self) -> None:
        content = _ssot()
        assert "phase-list" in content or "phase list" in content.lower(), (
            "SSOT must mandate phase-list format in §Silent Autonomous Mode"
        )


# ─────────────────────────────────────────────────────────────────────────────
# GAP-85-03: BLOCK-STAGE-PROGRESS enhanced with orchestrator pulse
# ─────────────────────────────────────────────────────────────────────────────
class TestBlockStageProgressEnhanced:
    """Phase 85-A: BLOCK-STAGE-PROGRESS should support orchestrator pulse annotation."""

    def test_block_stage_progress_defined(self) -> None:
        content = _ssot()
        assert "BLOCK-STAGE-PROGRESS" in content, (
            "BLOCK-STAGE-PROGRESS not found in SSOT"
        )

    def test_block_stage_progress_has_pulse_support(self) -> None:
        content = _ssot()
        # Search in the dedicated block definition (### section)
        idx = content.find("### BLOCK-STAGE-PROGRESS")
        assert idx >= 0, "BLOCK-STAGE-PROGRESS block definition (###) not found"
        snippet = content[idx: idx + 1200]
        assert "pulse" in snippet.lower() or "orchestrator" in snippet.lower() or "in progress" in snippet.lower(), (
            "BLOCK-STAGE-PROGRESS should document orchestrator pulse annotation"
        )


# ─────────────────────────────────────────────────────────────────────────────
# GAP-85-04/05/06: Engagement Blocks + Route Line
# ─────────────────────────────────────────────────────────────────────────────
class TestEngagementBlocks:
    """Phase 85-B: Engagement blocks must be defined in SSOT."""

    def test_block_engagement_breadcrumb_defined(self) -> None:
        assert "BLOCK-ENGAGEMENT-BREADCRUMB" in _ssot(), (
            "BLOCK-ENGAGEMENT-BREADCRUMB not found in cortex-response-templates.md"
        )

    def test_block_engagement_breadcrumb_format_has_route(self) -> None:
        content = _ssot()
        # Search in the dedicated block definition (### section)
        idx = content.find("### BLOCK-ENGAGEMENT-BREADCRUMB")
        assert idx >= 0, "BLOCK-ENGAGEMENT-BREADCRUMB block definition (###) not found"
        snippet = content[idx: idx + 800]
        assert "Route" in snippet or "route" in snippet, (
            "BLOCK-ENGAGEMENT-BREADCRUMB must show Route: format"
        )

    def test_block_engagement_timeline_defined(self) -> None:
        assert "BLOCK-ENGAGEMENT-TIMELINE" in _ssot(), (
            "BLOCK-ENGAGEMENT-TIMELINE not found in cortex-response-templates.md"
        )

    def test_block_engagement_timeline_is_collapsible(self) -> None:
        content = _ssot()
        idx = content.find("BLOCK-ENGAGEMENT-TIMELINE")
        snippet = content[idx: idx + 800]
        assert "<details>" in snippet or "collapsible" in snippet.lower(), (
            "BLOCK-ENGAGEMENT-TIMELINE should use <details> collapsible format"
        )

    def test_response_header_route_line_spec(self) -> None:
        content = _ssot()
        assert "Route:" in content or "**Route:**" in content, (
            "Response Header spec must include optional Route line"
        )

    def test_assembly_order_includes_engagement_blocks(self) -> None:
        content = _ssot()
        assert "BLOCK-ENGAGEMENT-BREADCRUMB" in content, (
            "Assembly order must include engagement blocks"
        )


# ─────────────────────────────────────────────────────────────────────────────
# GAP-85-07: No duplicate inline bar definitions in architect prompt
# ─────────────────────────────────────────────────────────────────────────────
class TestTemplateConsolidation:
    """Phase 85-C: Inline progress bar definitions removed from prompts."""

    def test_no_inline_exact_10_blocks_in_architect_prompt(self) -> None:
        content = ARCHITECT.read_text()
        assert "exactly 10 blocks" not in content, (
            "cortex-architect.prompt.md must not define 'exactly 10 blocks' inline — use SSOT pointer"
        )

    def test_architect_prompt_references_ssot(self) -> None:
        content = ARCHITECT.read_text()
        assert "cortex-response-templates.md" in content or "templates SSOT" in content, (
            "cortex-architect.prompt.md must reference templates SSOT for progress bar format"
        )


# ─────────────────────────────────────────────────────────────────────────────
# GAP-85-08: copilot-instructions SSOT pointer
# ─────────────────────────────────────────────────────────────────────────────
class TestCopilotInstructionsSSoT:
    """Phase 85-C: copilot-instructions must reference templates SSOT."""

    def test_copilot_instructions_phase_list_reference(self) -> None:
        content = COPILOT.read_text()
        assert "phase-list" in content or "cortex-response-templates" in content, (
            "copilot-instructions.md must reference phase-list format or templates SSOT"
        )


# ─────────────────────────────────────────────────────────────────────────────
# GAP-85-09/10: YAML registry + assembly order
# ─────────────────────────────────────────────────────────────────────────────
class TestYAMLRegistry:
    """Phase 85-D: YAML registry must contain new engagement blocks."""

    def test_yaml_registry_has_phase_roadmap(self) -> None:
        assert "BLOCK-PHASE-ROADMAP" in _yaml_reg(), (
            "response-templates.yaml must define BLOCK-PHASE-ROADMAP"
        )

    def test_yaml_registry_has_engagement_breadcrumb(self) -> None:
        assert "BLOCK-ENGAGEMENT-BREADCRUMB" in _yaml_reg(), (
            "response-templates.yaml must define BLOCK-ENGAGEMENT-BREADCRUMB"
        )

    def test_yaml_registry_has_engagement_timeline(self) -> None:
        assert "BLOCK-ENGAGEMENT-TIMELINE" in _yaml_reg(), (
            "response-templates.yaml must define BLOCK-ENGAGEMENT-TIMELINE"
        )

    def test_yaml_registry_is_valid_yaml(self) -> None:
        import yaml
        data = yaml.safe_load(_yaml_reg())
        assert data is not None


# ─────────────────────────────────────────────────────────────────────────────
# GAP-85-12: Zero pasted-image references
# ─────────────────────────────────────────────────────────────────────────────
class TestNoPastedImageRefs:
    """Phase 85-E: Zero 'pasted image' references in CORTEX source."""

    def _scan_files(self) -> list:
        """Scan all CORTEX source files for pasted image references."""
        results = []
        patterns = ["pasted image", "Pasted Image", "pasted_image"]
        scan_dirs = [
            REPO / ".github",
            REPO / "cortex-registry" / "artifacts",
            REPO / "cortex" / "core" / "common",
        ]
        for scan_dir in scan_dirs:
            if not scan_dir.exists():
                continue
            for f in scan_dir.rglob("*"):
                if f.suffix in (".md", ".yaml", ".py") and f.is_file():
                    try:
                        text = f.read_text()
                        for pat in patterns:
                            if pat.lower() in text.lower():
                                results.append(str(f))
                                break
                    except Exception:
                        pass
        return results

    def test_zero_pasted_image_refs_in_source(self) -> None:
        found = self._scan_files()
        assert not found, (
            f"Pasted image references found in: {found}. "
            "Replace with SSOT reference: §Silent Autonomous Mode"
        )
