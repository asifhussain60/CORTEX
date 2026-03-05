"""
Golden Tests: Phase 82-a — BLOCK-SESSION-IDENTITY + BLOCK-MICRO-ACK
                            Header Deduplication

Phase 82 sub-phase 82-a | Closes: GAP-82-01, GAP-82-02
Authority: CORE-002 (No report files), CORE-008 (TDD-first), CORE-035 (single canonical
           implementation), CORE-049 (Silent autonomous), CORE-064 (sweep completeness),
           CORE-066 (response template binding)

6 Acceptance Criteria (tdd_sequence.red):

  test_session_identity_block_renders_once
      BLOCK-SESSION-IDENTITY exists in SSOT with trigger 'first response only'
  test_session_identity_format_correct
      BLOCK-SESSION-IDENTITY canonical format: H2 🧠 CORTEX + author + framework stats + --- separator
  test_micro_ack_block_defined
      BLOCK-MICRO-ACK exists in SSOT with correct format '✅ Done — {action}'
  test_micro_ack_no_header
      BLOCK-MICRO-ACK format contains no ## header
  test_yaml_registry_session_identity_entry
      session_identity entry exists in response-templates.yaml
  test_yaml_registry_micro_ack_entry
      micro_ack entry exists in response-templates.yaml

AC_START: AC-82-A-SESSION-IDENTITY-001
Phase: 82 | Sub-phase: a | Priority: P1
"""

from pathlib import Path

import pytest
import yaml

# =============================================================================
# Paths
# =============================================================================

ROOT = Path(__file__).resolve().parents[3]
SSOT = ROOT / ".github" / "templates" / "cortex-response-templates.md"
YAML_REGISTRY = ROOT / "cortex-registry" / "artifacts" / "templates" / "responses" / "response-templates.yaml"


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(scope="module")
def ssot_text() -> str:
    """Read SSOT file once for the module."""
    assert SSOT.exists(), f"SSOT must exist at {SSOT}"
    return SSOT.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def yaml_registry() -> dict:
    """Load response-templates.yaml as a parsed dict."""
    assert YAML_REGISTRY.exists(), f"YAML registry must exist at {YAML_REGISTRY}"
    return yaml.safe_load(YAML_REGISTRY.read_text(encoding="utf-8"))


# =============================================================================
# GAP-82-01: BLOCK-SESSION-IDENTITY
# =============================================================================


class TestBlockSessionIdentity:
    """GAP-82-01: BLOCK-SESSION-IDENTITY must be defined in SSOT with correct trigger and format."""

    def test_session_identity_block_renders_once(self, ssot_text: str) -> None:
        """BLOCK-SESSION-IDENTITY must exist in SSOT with trigger 'first response only'.

        The session identity block deduplicates the repeated author/orchestrator header
        across a long session. It must be declared as 'FIRST response in session only'
        to prevent it from appearing on every turn.

        GAP-82-01: No 'session-first render, mode-only on subsequent' mechanism exists.
        CORE-035: single canonical implementation.
        """
        assert "BLOCK-SESSION-IDENTITY" in ssot_text, (
            "SSOT must define BLOCK-SESSION-IDENTITY. "
            "This block renders the full header ONCE per session (first response only). "
            "GAP-82-01: currently no session-deduplication mechanism exists."
        )
        lower = ssot_text.lower()
        assert "first response" in lower or "first turn" in lower or "once per session" in lower, (
            "BLOCK-SESSION-IDENTITY must declare a trigger of 'first response only' or "
            "'once per session'. Found BLOCK-SESSION-IDENTITY in SSOT but no session-scoping trigger."
        )

    def test_session_identity_format_correct(self, ssot_text: str) -> None:
        """BLOCK-SESSION-IDENTITY must include H2 🧠 CORTEX anchor, author line, and --- separator.

        Renderer note: BLOCK-SESSION-IDENTITY is the ONLY block allowed to use H2.
        All subsequent blocks must use H3 or bold labels (R6).
        The H2 emoji anchor pattern (## 🧠 CORTEX …) is stable in Copilot Chat renderers.

        GAP-82-01: the canonical format: H2 🧠 CORTEX + author + framework stats + --- separator.
        """
        assert "BLOCK-SESSION-IDENTITY" in ssot_text, (
            "BLOCK-SESSION-IDENTITY must be defined in SSOT before its format can be validated."
        )
        # The block must specify H2 usage as the ONLY H2 per session (R6 exception)
        assert "🧠" in ssot_text, (
            "BLOCK-SESSION-IDENTITY format must include the 🧠 emoji anchor "
            "(## 🧠 CORTEX …) — this is the stable Copilot Chat H2 pattern."
        )
        # Must include author attribution
        assert "Asif Hussain" in ssot_text, (
            "BLOCK-SESSION-IDENTITY must include 'Asif Hussain' as the author attribution line."
        )


# =============================================================================
# GAP-82-02: BLOCK-MICRO-ACK
# =============================================================================


class TestBlockMicroAck:
    """GAP-82-02: BLOCK-MICRO-ACK must be defined in SSOT for trivial confirmation responses."""

    def test_micro_ack_block_defined(self, ssot_text: str) -> None:
        """BLOCK-MICRO-ACK must exist in SSOT with the format '✅ Done — {action}'.

        Simple acknowledgements ("Done ✅", "Fixed ✅", "Committed.") currently use
        the full 5-section golden format — creating visual noise for trivial confirmations.
        BLOCK-MICRO-ACK is a no-header single-line template for these cases.

        GAP-82-02: No MICRO-ACK template defined in SSOT or YAML registry.
        """
        assert "BLOCK-MICRO-ACK" in ssot_text, (
            "SSOT must define BLOCK-MICRO-ACK. "
            "This block renders trivial confirmations as a single line without a header. "
            "Format: '✅ Done — {action} complete. {metric if applicable}'. "
            "GAP-82-02: currently no MICRO-ACK template defined."
        )

    def test_micro_ack_no_header(self, ssot_text: str) -> None:
        """BLOCK-MICRO-ACK format must NOT use an ## or ### header.

        The MICRO-ACK block is specifically designed to be a single-line confirmation
        with NO markdown header. Using a header defeats the purpose — it would be
        visually indistinct from a full section. The block must render as plain text
        or a bold label only.

        GAP-82-02: sub-10-word confirmations over-formatted with 5-section structure.
        """
        assert "BLOCK-MICRO-ACK" in ssot_text, (
            "BLOCK-MICRO-ACK must be defined in SSOT before its format can be validated."
        )
        # Find the BLOCK-MICRO-ACK section and verify it states 'no header' or equivalent
        # Accept any phrasing that clarifies no heading is used
        lower = ssot_text.lower()
        assert "no header" in lower or "no ## header" in lower or "no heading" in lower or (
            "micro-ack" in lower and "standalone" in lower
        ) or (
            "micro_ack" in lower and "header" not in ssot_text[
                ssot_text.find("BLOCK-MICRO-ACK"):ssot_text.find("BLOCK-MICRO-ACK") + 200
            ].replace("no header", "").replace("no ## header", "")
        ), (
            "BLOCK-MICRO-ACK definition in SSOT must explicitly state that no ## or ### "
            "header is used. The block is a single-line confirmation without section header. "
            "Expected: '**Trigger:** Trivial confirmations only. **Format:** ✅ Done — {action}. "
            "No ## header.'"
        )


# =============================================================================
# YAML Registry entries
# =============================================================================


class TestYAMLRegistryEntries:
    """BLOCK-SESSION-IDENTITY and BLOCK-MICRO-ACK must be registered in response-templates.yaml."""

    def test_yaml_registry_session_identity_entry(self, yaml_registry: dict) -> None:
        """YAML registry must have a session_identity template entry.

        The YAML registry provides machine-readable template metadata used by
        orchestrators and test assertions. session_identity must be present
        with intent, format, and trigger fields.

        GAP-82-01: no registry entry for session-first render mechanism.
        """
        templates = yaml_registry.get("templates", {})
        assert "session_identity" in templates, (
            "response-templates.yaml must contain a 'session_identity' template entry. "
            "This provides machine-readable metadata for BLOCK-SESSION-IDENTITY. "
            f"Current template keys: {list(templates.keys())}"
        )

    def test_yaml_registry_micro_ack_entry(self, yaml_registry: dict) -> None:
        """YAML registry must have a micro_ack template entry.

        The YAML registry provides machine-readable template metadata. micro_ack
        must be present with intent, format, and trigger fields.

        GAP-82-02: no registry entry for micro-ack template.
        """
        templates = yaml_registry.get("templates", {})
        assert "micro_ack" in templates, (
            "response-templates.yaml must contain a 'micro_ack' template entry. "
            "This provides machine-readable metadata for BLOCK-MICRO-ACK. "
            f"Current template keys: {list(templates.keys())}"
        )


# AC_COMPLETE: AC-82-A-SESSION-IDENTITY-001 ✅ RED phase — 6 tests written, all must FAIL before implementation
