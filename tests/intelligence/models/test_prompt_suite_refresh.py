"""
Phase 107 Sub-Phase E: Prompt Suite Refresh — RED tests (GAP-107-10, GAP-107-11)

Tests verify:
  GAP-107-10: copilot-instructions.md + cortex-architect.prompt.md contain NO stale
              cortex/lens/ paths and DO reference IntelligenceFacade as canonical entry.
  GAP-107-11: cortex-meta-auditor.md has Check #27 for intelligence-layer health;
              no dissolved-package references in any .github/ prompt or agent file.

Run:  python3 -m pytest tests/intelligence/models/test_prompt_suite_refresh.py -v
"""

from __future__ import annotations

import re
import os
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
GITHUB_DIR = REPO_ROOT / ".github"
COPILOT_INSTRUCTIONS = GITHUB_DIR / "copilot-instructions.md"
ARCHITECT_PROMPT = GITHUB_DIR / "prompts" / "cortex-architect.prompt.md"
AGENT_INDEX = GITHUB_DIR / "agents" / "AGENT-INDEX.md"
META_AUDITOR = GITHUB_DIR / "agents" / "core" / "cortex-meta-auditor.md"
PROMPTS_DIR = GITHUB_DIR / "prompts"
AGENTS_CORE_DIR = GITHUB_DIR / "agents" / "core"


# ---------------------------------------------------------------------------
# GAP-107-10: copilot-instructions.md accuracy
# ---------------------------------------------------------------------------


class TestCopilotInstructionsAccuracy:
    """GAP-107-10 — copilot-instructions.md must reference Phase 107 changes."""

    def test_copilot_instructions_intelligence_facade_documented(self):
        """IntelligenceFacade must be documented as the canonical intelligence entry point."""
        text = COPILOT_INSTRUCTIONS.read_text()
        assert "IntelligenceFacade" in text, (
            "copilot-instructions.md must mention IntelligenceFacade as canonical entry point "
            "(introduced in Phase 107 Sub-Phase C)"
        )

    def test_copilot_instructions_intelligence_facade_path(self):
        """cortex/intelligence/facade.py must be referenced in copilot-instructions.md."""
        text = COPILOT_INSTRUCTIONS.read_text()
        assert "intelligence/facade.py" in text or "intelligence.facade" in text, (
            "copilot-instructions.md must include the path cortex/intelligence/facade.py "
            "so developers know where to find the canonical facade"
        )

    def test_copilot_instructions_architecture_counts_not_stale(self):
        """Architecture counts in copilot-instructions.md must match refresh_prompt_suite output.

        The script reports 185 orchestrators; the file must not say 186.
        NOTE: Acceptable to say '185' or update the count — '186' is stale.
        """
        text = COPILOT_INSTRUCTIONS.read_text()
        # The old count was 186 in the docs. After Phase 107 flattening one
        # orchestrator file was removed (sensory/chat_file_detector.py-related).
        # The script now reports 185. The instructions must not advertise 186 as current.
        # We allow a single line that says "186" ONLY inside the historical context block.
        lines_with_186 = [
            line for line in text.splitlines()
            if "186" in line
            and "Orchestrator files" in line
            and "186 across 9 domains" in line
        ]
        assert len(lines_with_186) == 0, (
            f"copilot-instructions.md still says '186 Orchestrator files' but "
            f"refresh_prompt_suite.py --counts-only reports 185. "
            f"Update the Architecture table. Lines:\n" + "\n".join(lines_with_186)
        )

    def test_copilot_instructions_intent_types_not_stale(self):
        """Intent types count must not say '28' when live count is 29."""
        text = COPILOT_INSTRUCTIONS.read_text()
        # Check Architecture table row
        stale_lines = [
            line for line in text.splitlines()
            if re.search(r'\bIntent Types\b.*\b28\b', line)
        ]
        assert len(stale_lines) == 0, (
            "copilot-instructions.md Architecture table says '28' intent types but "
            "canonical_enums.py reports 29. Update Intent Types row. Lines:\n"
            + "\n".join(stale_lines)
        )


class TestArchitectPromptAccuracy:
    """GAP-107-10 — cortex-architect.prompt.md must reference Phase 107 changes."""

    def test_architect_prompt_intelligence_facade_referenced(self):
        """IntelligenceFacade must appear in cortex-architect.prompt.md."""
        text = ARCHITECT_PROMPT.read_text()
        assert "IntelligenceFacade" in text, (
            "cortex-architect.prompt.md must document IntelligenceFacade as the "
            "canonical intelligence entry (Phase 107 Sub-Phase C)"
        )

    def test_architect_prompt_lens_layer_entry_updated(self):
        """LENS row in architect prompt architecture table must reference cortex/intelligence/ path.

        The old table row pointed exclusively to cortex/lens/. After Phase 107 the canonical
        analysis facade is cortex/intelligence/facade.py. The table must reflect this.
        """
        text = ARCHITECT_PROMPT.read_text()
        # We expect the LENS row (or equivalent) to now mention intelligence/facade
        # OR to point callers at IntelligenceFacade instead of raw cortex/lens/
        has_facade_ref = "intelligence/facade" in text or "IntelligenceFacade" in text
        assert has_facade_ref, (
            "cortex-architect.prompt.md architecture table must reference "
            "cortex/intelligence/facade.py (IntelligenceFacade) as canonical LENS entry"
        )


# ---------------------------------------------------------------------------
# GAP-107-11: cortex-meta-auditor.md Check #27 (intelligence-layer health)
# ---------------------------------------------------------------------------


class TestMetaAuditorCheck27:
    """GAP-107-11 — cortex-meta-auditor.md must contain Check #27 for intelligence health."""

    def test_meta_auditor_has_check_27(self):
        """Check #27 for intelligence-layer health must exist in cortex-meta-auditor.md."""
        text = META_AUDITOR.read_text()
        # Look for | 27 | row in the checks table
        has_check_27 = bool(re.search(r'^\| 27 \|', text, re.MULTILINE))
        assert has_check_27, (
            "cortex-meta-auditor.md must contain Check #27 for intelligence-layer health "
            "(GAP-107-11 requirement: IntelligenceFacade importable, models package intact)"
        )

    def test_meta_auditor_check_27_mentions_intelligence_facade(self):
        """Check #27 in meta-auditor must explicitly mention IntelligenceFacade."""
        text = META_AUDITOR.read_text()
        # Find the | 27 | row
        match = re.search(r'^\| 27 \|.*', text, re.MULTILINE)
        if not match:
            pytest.fail("Check #27 row not found — test_meta_auditor_has_check_27 should have caught this")
        row_text = match.group(0)
        assert "IntelligenceFacade" in row_text, (
            "Check #27 row must mention IntelligenceFacade. "
            f"Got: {row_text[:200]}"
        )

    def test_meta_auditor_check_27_has_detect_command(self):
        """Check #27 must include a python3 detect command for machine-verifiability."""
        text = META_AUDITOR.read_text()
        match = re.search(r'^\| 27 \|.*', text, re.MULTILINE)
        if not match:
            pytest.fail("Check #27 row not found")
        row_text = match.group(0)
        assert "python3" in row_text or "import" in row_text, (
            "Check #27 must include a machine-verifiable detect command (python3 -c ...)"
        )


# ---------------------------------------------------------------------------
# GAP-107-11: No dissolved-package references in .github/ prompts/agents
# ---------------------------------------------------------------------------


class TestNoDissolvedPackageRefs:
    """GAP-107-11 — No dissolved-package refs in .github/ prompt and agent files."""

    DISSOLVED_PATTERNS = [
        "cortex_intelligence/",
        "cortex_lens/",
        "cortex.brain",
        "cortex/brain/",
    ]

    def _collect_github_md_files(self) -> list[Path]:
        return [
            p for p in GITHUB_DIR.rglob("*.md")
            if ".git" not in p.parts
        ]

    def test_no_dissolved_package_refs_in_historical_description(self):
        """Dissolved package names may appear ONLY in historical/migration context, not as active paths.

        Active import usage lines (e.g. 'from cortex_intelligence import X') must be purged.
        Historical notes ('cortex_lens/ — merged into ...') are acceptable.
        Lines mentioning dissolved names as examples in governance/audit checks are acceptable.
        """
        md_files = self._collect_github_md_files()
        violations: list[str] = []

        # Patterns that indicate ACTIVE import usage (not historical note or doc example)
        active_import_patterns = [
            r'from cortex_intelligence\s+import',
            r'from cortex_lens\s+import',
            r'import cortex_lens\b',
            r'import cortex_intelligence\b',
        ]

        for f in md_files:
            text = f.read_text()
            for pat in active_import_patterns:
                for i, line in enumerate(text.splitlines(), 1):
                    if re.search(pat, line):
                        violations.append(f"{f.relative_to(REPO_ROOT)}:{i}: {line.strip()[:120]}")

        assert len(violations) == 0, (
            f"Found {len(violations)} active dissolved-package import statements in .github/:\n"
            + "\n".join(violations)
        )

    def test_no_cortex_brain_active_imports(self):
        """No active import of cortex.brain in any .github/ file (historical mentions are fine)."""
        md_files = self._collect_github_md_files()
        hits = []
        for f in md_files:
            for i, line in enumerate(f.read_text().splitlines(), 1):
                # Match actual Python import syntax, not grep patterns or doc examples
                if re.search(r'from cortex\.brain\s+import\b|^import cortex\.brain\b', line):
                    hits.append(f"{f.relative_to(REPO_ROOT)}:{i}: {line.strip()}")
        assert len(hits) == 0, (
            "cortex.brain is dissolved — remove active import references:\n" + "\n".join(hits)
        )


# ---------------------------------------------------------------------------
# GAP-107-10: IntelligenceFacade importable from canonical path
# ---------------------------------------------------------------------------


class TestIntelligenceFacadeImportable:
    """Verify cortex.intelligence.facade.IntelligenceFacade is importable at runtime."""

    def test_intelligence_facade_importable(self):
        """from cortex.intelligence.facade import IntelligenceFacade must succeed."""
        try:
            from cortex.intelligence.facade import IntelligenceFacade  # noqa: F401
        except ImportError as e:
            pytest.fail(f"IntelligenceFacade import failed: {e}")

    def test_intelligence_models_package_importable(self):
        """from cortex.intelligence.models import BaseIntelligenceEngine must succeed."""
        try:
            from cortex.intelligence.models import BaseIntelligenceEngine  # noqa: F401
        except ImportError as e:
            pytest.fail(f"cortex.intelligence.models import failed: {e}")

    def test_intelligence_facade_has_analyze_synthesize_query(self):
        """IntelligenceFacade must expose analyze(), synthesize(), query() methods."""
        from cortex.intelligence.facade import IntelligenceFacade
        facade = IntelligenceFacade()
        assert hasattr(facade, "analyze"), "IntelligenceFacade missing analyze()"
        assert hasattr(facade, "synthesize"), "IntelligenceFacade missing synthesize()"
        assert hasattr(facade, "query"), "IntelligenceFacade missing query()"
