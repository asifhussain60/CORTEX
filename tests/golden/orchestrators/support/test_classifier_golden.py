# =============================================================================
# Phase 49 — TestClassifierOrchestrator Golden Tests
# GC-001 through GC-015: Deterministic Classification Scenarios
# =============================================================================
#
# AC-ID: AC-P49-GC-001
# Authority: CORE-008 (TDD), CORE-055 (Golden Test Tier Contract)
# Author: Asif Hussain
# Created: 2026-02-18
#
# Coverage Matrix:
# P0 (Critical): GC-001..GC-007 — tier determination for all path patterns
# P1 (High):     GC-008..GC-012 — TestDecision field validation
# P2 (Medium):   GC-013..GC-015 — edge cases and additional paths
#
# AC_START: TestClassifierOrchestrator golden test suite
# =============================================================================

import pytest
from cortex.orchestrators.support.test_classifier_orchestrator import (
    TestClassifierOrchestrator,
    TestTier,
    TestConcern,
    TestDecision,
)


# =============================================================================
# P0 SCENARIOS — Tier Determination
# =============================================================================

class TestGoldenPathClassification:
    """GC-001 through GC-007: tier determination for all path patterns."""

    def setup_method(self):
        self.classifier = TestClassifierOrchestrator()

    def test_orchestrator_path_golden_tier(self):
        """GC-001: orchestrators/ path → GOLDEN tier with SECURITY+CCL concerns."""
        result = self.classifier.classify("cortex/orchestrators/core/tdd_orchestrator.py")
        assert result.tier == TestTier.GOLDEN
        assert TestConcern.SECURITY in result.concerns
        assert TestConcern.CCL in result.concerns

    def test_mcp_tool_path_golden_tier(self):
        """GC-002: MCP tool path → GOLDEN tier, SECURITY+CONTRACT concerns."""
        result = self.classifier.classify("cortex/mcp/tools/health_orchestrator_tool.py")
        assert result.tier == TestTier.GOLDEN
        assert TestConcern.SECURITY in result.concerns
        assert TestConcern.CONTRACT in result.concerns

    def test_governance_path_golden_tier(self):
        """GC-003: governance path → GOLDEN tier, SECURITY+QUALITY concerns."""
        result = self.classifier.classify("cortex/governance/enforcement/audit_checker.py")
        assert result.tier == TestTier.GOLDEN
        assert TestConcern.SECURITY in result.concerns
        assert TestConcern.QUALITY in result.concerns

    def test_brain_path_golden_tier(self):
        """GC-004: brain/intelligence path → GOLDEN tier, CCL+QUALITY concerns."""
        result = self.classifier.classify("cortex/brain/core/brain_coordinator.py")
        assert result.tier == TestTier.GOLDEN
        assert TestConcern.CCL in result.concerns
        assert TestConcern.QUALITY in result.concerns

    def test_common_utility_path_standard_tier(self):
        """GC-005: common utility path → STANDARD tier, no mandatory golden concerns."""
        result = self.classifier.classify("cortex/common/utils/string_helpers.py")
        assert result.tier == TestTier.STANDARD

    def test_config_path_standard_tier(self):
        """GC-006: config path → STANDARD tier."""
        result = self.classifier.classify("cortex/config/settings.py")
        assert result.tier == TestTier.STANDARD

    def test_unknown_path_standard_tier_safe_default(self):
        """GC-007: unknown path → STANDARD tier (safe default, never GOLDEN)."""
        result = self.classifier.classify("cortex/some/completely/new/module.py")
        assert result.tier == TestTier.STANDARD


# =============================================================================
# P1 SCENARIOS — TestDecision Field Validation
# =============================================================================

class TestDecisionFields:
    """GC-008 through GC-012: TestDecision field contracts."""

    def setup_method(self):
        self.classifier = TestClassifierOrchestrator()

    def test_golden_tier_concerns_never_empty(self):
        """GC-008: TestDecision.concerns list is never empty for GOLDEN tier."""
        result = self.classifier.classify("cortex/orchestrators/support/health_orchestrator.py")
        assert result.tier == TestTier.GOLDEN
        assert len(result.concerns) > 0

    def test_target_folder_mirrors_source_structure(self):
        """GC-009: TestDecision.target_folder mirrors source structure under tests/golden/."""
        result = self.classifier.classify("cortex/orchestrators/support/test_classifier_orchestrator.py")
        assert result.target_folder.startswith("tests/golden/")
        assert "orchestrators" in result.target_folder

    def test_golden_coverage_floor_is_95(self):
        """GC-010: TestDecision.coverage_floor == 95 for GOLDEN tier."""
        result = self.classifier.classify("cortex/orchestrators/core/tdd_orchestrator.py")
        assert result.tier == TestTier.GOLDEN
        assert result.coverage_floor == 95

    def test_standard_coverage_floor_is_80(self):
        """GC-010b: TestDecision.coverage_floor == 80 for STANDARD tier."""
        result = self.classifier.classify("cortex/config/settings.py")
        assert result.tier == TestTier.STANDARD
        assert result.coverage_floor == 80

    def test_classify_raises_no_exceptions_for_valid_path(self):
        """GC-011: classifier raises no exceptions for any valid path string."""
        paths = [
            "cortex/orchestrators/core.py",
            "cortex/mcp/tools/tool.py",
            "cortex/common/utils.py",
            "cortex/config/env.py",
            "cortex/models/base.py",
            "cortex/templates/base.py",
            "some/arbitrary/path.py",
        ]
        for path in paths:
            result = self.classifier.classify(path)
            assert result is not None

    def test_classify_is_idempotent(self):
        """GC-012: classify() is idempotent — same input = same output every time."""
        path = "cortex/orchestrators/support/health_orchestrator.py"
        result1 = self.classifier.classify(path)
        result2 = self.classifier.classify(path)
        result3 = self.classifier.classify(path)
        assert result1.tier == result2.tier == result3.tier
        assert result1.concerns == result2.concerns
        assert result1.coverage_floor == result3.coverage_floor


# =============================================================================
# P2 SCENARIOS — Additional Paths & Edge Cases
# =============================================================================

class TestAdditionalPathClassification:
    """GC-013 through GC-015: edge cases and additional paths."""

    def setup_method(self):
        self.classifier = TestClassifierOrchestrator()

    def test_agents_path_golden_security_contract(self):
        """GC-013: agents/ path → GOLDEN, SECURITY+CONTRACT."""
        result = self.classifier.classify("cortex/agents/security/secrets_agent.py")
        assert result.tier == TestTier.GOLDEN
        assert TestConcern.SECURITY in result.concerns
        assert TestConcern.CONTRACT in result.concerns

    def test_domain_brain_path_golden_ccl(self):
        """GC-014: domain_brain/ path → GOLDEN, CCL concern present."""
        result = self.classifier.classify("cortex/domain_brain/orchestrator.py")
        assert result.tier == TestTier.GOLDEN
        assert TestConcern.CCL in result.concerns

    def test_test_decision_has_required_markers_list(self):
        """GC-015: TestDecision dataclass has required_markers list attribute."""
        result = self.classifier.classify("cortex/orchestrators/core/tdd_orchestrator.py")
        assert hasattr(result, "required_markers")
        assert isinstance(result.required_markers, list)
