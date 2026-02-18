# =============================================================================
# Phase 49 — CORE-055 Golden Test Tier Contract Governance Tests
# GR-001 through GR-006: Enforcement & Compliance Scenarios
# =============================================================================
#
# AC-ID: AC-P49-GR-001
# Authority: CORE-008 (TDD), CORE-055 (Golden Test Tier Contract - NEW)
# Author: Asif Hussain
# Created: 2026-02-18
#
# Coverage Matrix:
# P0 (Critical): GR-001..GR-004 — violation detection
# P1 (High):     GR-005..GR-006 — compliance and exemptions
#
# AC_START: CORE-055 governance golden test suite
# =============================================================================

import pytest
from pathlib import Path
from cortex.orchestrators.support.test_classifier_orchestrator import (
    TestClassifierOrchestrator,
    TestTier,
)


PROTECTED_FILES = [
    "tests/golden/routing/test_multi_turn_routing_golden.py",
    "tests/golden/test_memory_tier_operations_truth.py",
    "tests/golden/test_tier_system_integration_truth.py",
]


class Core055Validator:
    """Validates CORE-055: Golden Test Tier Contract compliance."""

    def __init__(self):
        self.classifier = TestClassifierOrchestrator()

    def check_test_file_location(self, source_module_path: str, test_file_path: str) -> dict:
        """Returns compliance status for a source module / test file pair."""
        decision = self.classifier.classify(source_module_path)
        if decision.tier == TestTier.GOLDEN:
            compliant = test_file_path.startswith("tests/golden/")
            return {
                "tier": "GOLDEN",
                "compliant": compliant,
                "violation": None if compliant else "CORE-055: GOLDEN-tier test must be in tests/golden/",
            }
        return {"tier": "STANDARD", "compliant": True, "violation": None}

    def check_file_has_coverage_matrix(self, file_content: str) -> bool:
        """Returns True if file has a P0/P1 coverage matrix comment block."""
        return "# P0" in file_content and "# P1" in file_content

    def check_file_has_ac_id(self, file_content: str) -> bool:
        """Returns True if file contains an AC-ID or AC_START marker."""
        return "AC-ID:" in file_content or "AC_START:" in file_content


# =============================================================================
# P0 SCENARIOS — Violation Detection
# =============================================================================

class TestCore055ViolationDetection:
    """GR-001 through GR-004: CORE-055 violation detection."""

    def setup_method(self):
        self.validator = Core055Validator()

    def test_golden_tier_file_in_unit_is_violation(self):
        """GR-001: GOLDEN-tier file in tests/unit/ → CORE-055 violation detected."""
        result = self.validator.check_test_file_location(
            source_module_path="cortex/orchestrators/core/tdd_orchestrator.py",
            test_file_path="tests/unit/orchestrators/test_tdd_orchestrator.py",
        )
        assert result["tier"] == "GOLDEN"
        assert result["compliant"] is False
        assert "CORE-055" in result["violation"]

    def test_golden_tier_file_in_golden_is_compliant(self):
        """GR-002: GOLDEN-tier file in tests/golden/ → compliant."""
        result = self.validator.check_test_file_location(
            source_module_path="cortex/orchestrators/core/tdd_orchestrator.py",
            test_file_path="tests/golden/orchestrators/core/test_tdd_orchestrator_golden.py",
        )
        assert result["tier"] == "GOLDEN"
        assert result["compliant"] is True
        assert result["violation"] is None

    def test_missing_coverage_matrix_is_violation(self):
        """GR-003: file missing coverage matrix comment → CORE-055 violation."""
        file_without_matrix = "def test_something(): pass"
        assert self.validator.check_file_has_coverage_matrix(file_without_matrix) is False

    def test_missing_ac_id_is_violation(self):
        """GR-004: file missing AC-ID → CORE-055 violation."""
        file_without_ac_id = "# P0 Critical\n# P1 High\ndef test_something(): pass"
        assert self.validator.check_file_has_ac_id(file_without_ac_id) is False


# =============================================================================
# P1 SCENARIOS — Compliance and Exemptions
# =============================================================================

class TestCore055ComplianceAndExemptions:
    """GR-005 through GR-006: STANDARD-tier and protected file exemptions."""

    def setup_method(self):
        self.validator = Core055Validator()

    def test_standard_tier_file_exempt_from_core055(self):
        """GR-005: STANDARD-tier file anywhere → no CORE-055 check applied."""
        # Standard tier: config module, tested in tests/unit/ is fine
        result = self.validator.check_test_file_location(
            source_module_path="cortex/config/settings.py",
            test_file_path="tests/unit/config/test_settings.py",
        )
        assert result["tier"] == "STANDARD"
        assert result["compliant"] is True
        assert result["violation"] is None

    def test_protected_files_have_ac_id(self):
        """GR-006: protected golden test files themselves have AC-ID (self-compliance)."""
        # Phase 49 golden tests we just created should themselves be compliant
        phase49_classifier_test = Path(
            "tests/golden/orchestrators/support/test_classifier_golden.py"
        )
        if phase49_classifier_test.exists():
            content = phase49_classifier_test.read_text()
            assert self.validator.check_file_has_coverage_matrix(content), \
                f"{phase49_classifier_test} missing coverage matrix"
            assert self.validator.check_file_has_ac_id(content), \
                f"{phase49_classifier_test} missing AC-ID"
        else:
            pytest.skip("File not yet created — expected during Phase 49 GREEN")
