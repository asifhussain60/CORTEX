# =============================================================================
# TestClassifierOrchestrator — Phase 49
# Deterministic, zero-dependency module path → TestDecision classifier.
# =============================================================================
#
# AC-ID: AC-P49-IMPL-001
# Authority: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings),
#            CORE-028 (kebab naming), CORE-035 (single canonical impl),
#            CORE-055 (Golden Test Tier Contract)
# Author: Asif Hussain
# Created: 2026-02-18
#
# Coverage Matrix:
# P0: classify() returns correct TestTier for all golden path patterns
# P1: TestDecision fields are fully populated (concerns, target, markers, floor)
# P2: Edge cases — unknown paths, empty input, idempotency
# =============================================================================

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List


# =============================================================================
# ENUMS
# =============================================================================

class TestTier(Enum):
    """Classification tier for a test module.

    Attributes:
        GOLDEN: High-blast-radius module. Tests must live in tests/golden/.
                Coverage floor: 95%. Mandatory concern annotations required.
        STANDARD: Standard module. Tests may live anywhere under tests/.
                  Coverage floor: 80%. No mandatory concern markers.
    """

    GOLDEN = "GOLDEN"
    STANDARD = "STANDARD"


class TestConcern(Enum):
    """Required test concern categories for GOLDEN-tier modules.

    Each value maps to a mandatory test class annotation comment
    (e.g., ``# SECURITY CONCERN: ...``).
    """

    SECURITY = "SECURITY"
    QUALITY = "QUALITY"
    CCL = "CCL"          # Correctness, Completeness, Lineage
    PERF = "PERF"
    CONTRACT = "CONTRACT"


# =============================================================================
# DATA CONTRACTS
# =============================================================================

@dataclass
class TestDecision:
    """Immutable result from TestClassifierOrchestrator.classify().

    Attributes:
        tier: The test tier for the source module (GOLDEN or STANDARD).
        concerns: Ordered list of TestConcern values required for this tier.
                  Empty list if tier == STANDARD.
        target_folder: Recommended location for the test file under tests/.
        required_markers: List of string markers that must appear in the
                          test file (e.g., 'AC-ID:', '# P0', '# P1').
        coverage_floor: Minimum coverage percentage (95 for GOLDEN, 80 for STANDARD).
    """

    tier: TestTier
    concerns: List[TestConcern]
    target_folder: str
    required_markers: List[str]
    coverage_floor: int


# =============================================================================
# CLASSIFICATION RULES
# =============================================================================

# Paths matched against the start of a normalised module path.
# Order matters: first match wins.
_GOLDEN_PATH_RULES: list[tuple[str, list[TestConcern]]] = [
    ("cortex/orchestrators/",  [TestConcern.SECURITY, TestConcern.QUALITY, TestConcern.CCL]),
    ("cortex/mcp/tools/",      [TestConcern.SECURITY, TestConcern.CONTRACT]),
    ("cortex/governance/",     [TestConcern.SECURITY, TestConcern.QUALITY]),
    ("cortex/brain/",          [TestConcern.CCL, TestConcern.QUALITY]),
    ("cortex/intelligence/",   [TestConcern.CCL, TestConcern.SECURITY]),
    ("cortex/domain_brain/",   [TestConcern.CCL]),
    ("cortex/agents/",         [TestConcern.SECURITY, TestConcern.CONTRACT]),
]

GOLDEN_COVERAGE_FLOOR: int = 95
STANDARD_COVERAGE_FLOOR: int = 80
MAX_TARGET_PATH_LENGTH: int = 120

_GOLDEN_REQUIRED_MARKERS: list[str] = ["AC-ID:", "# P0", "# P1"]


# =============================================================================
# ORCHESTRATOR
# =============================================================================

class TestClassifierOrchestrator:
    """Deterministic, stateless classifier: module path → TestDecision.

    Pure read-only. No network I/O, no disk I/O, no ML inference.
    Classifies any Python module path string and returns a complete
    TestDecision describing where its tests must live and what they
    must contain (CORE-055 contract).

    Usage::

        classifier = TestClassifierOrchestrator()
        decision = classifier.classify("cortex/orchestrators/support/health_orchestrator.py")
        # decision.tier == TestTier.GOLDEN
        # decision.coverage_floor == 95
        # TestConcern.SECURITY in decision.concerns
    """

    def classify(self, module_path: str) -> TestDecision:
        """Classify a module path and return a full TestDecision.

        Args:
            module_path: Absolute or relative path to a Python module.
                         Accepts forward-slash or backslash separators.

        Returns:
            TestDecision: Fully populated decision record. Never raises.
        """
        normalised = module_path.replace("\\", "/")

        for prefix, concerns in _GOLDEN_PATH_RULES:
            if normalised.startswith(prefix) or f"/{prefix.lstrip('/')}" in normalised:
                target = self._derive_target_folder(normalised, "tests/golden/")
                return TestDecision(
                    tier=TestTier.GOLDEN,
                    concerns=list(concerns),
                    target_folder=target,
                    required_markers=list(_GOLDEN_REQUIRED_MARKERS),
                    coverage_floor=GOLDEN_COVERAGE_FLOOR,
                )

        # Default: STANDARD
        target = self._derive_target_folder(normalised, "tests/unit/")
        return TestDecision(
            tier=TestTier.STANDARD,
            concerns=[],
            target_folder=target,
            required_markers=[],
            coverage_floor=STANDARD_COVERAGE_FLOOR,
        )

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    @staticmethod
    def _derive_target_folder(module_path: str, base: str) -> str:
        """Derive the recommended test folder from the module path.

        Strips the leading 'cortex/' segment and the filename, then
        prepends the appropriate base (tests/golden/ or tests/unit/).

        Args:
            module_path: Normalised module path with forward slashes.
            base: The base folder prefix ('tests/golden/' or 'tests/unit/').

        Returns:
            Target folder string, guaranteed ≤ MAX_TARGET_PATH_LENGTH.
        """
        # Drop leading 'cortex/' if present
        stripped = module_path
        for prefix in ("cortex/", "cortex_intelligence/", "cortex_lens/"):
            if stripped.startswith(prefix):
                stripped = stripped[len(prefix):]
                break

        # Drop filename
        parts = stripped.rsplit("/", 1)
        folder_part = parts[0] if len(parts) > 1 else ""

        target = f"{base}{folder_part}" if folder_part else base
        # Enforce max path length per CORE-028
        if len(target) > MAX_TARGET_PATH_LENGTH:
            target = target[:MAX_TARGET_PATH_LENGTH]
        return target
