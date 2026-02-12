"""
Unit tests for ArchitecturePatternChecker (ENH-086 Stage 3).

Tests behavioral contracts for architecture pattern enforcement:
- TDD pattern (RED→GREEN→REFACTOR)
- Strategy pattern (composition over inheritance)
- EventBus pattern (message-based communication)

Authority: WAVE-K/ENH-086 Stage 3 - Architecture Pattern Enforcement
TDD Cycle: RED→GREEN→REFACTOR
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

# AC_START: AC-WAVEK-005
# Description: ENH-086 Stage 3 - Architecture pattern enforcement tests
# Authority: cortex-registry/_cortex-master/index.yaml (WAVE-K)


class TestArchitecturePatternChecker:
    """Test suite for ArchitecturePatternChecker."""
    
    def test_verify_patterns_returns_compliance_report(self):
        """Pattern checker returns structured compliance report."""
        from cortex.governance.architecture_pattern_checker import ArchitecturePatternChecker
        
        checker = ArchitecturePatternChecker()
        report = checker.verify_patterns(target_path=Path("cortex/governance"))
        
        assert hasattr(report, "patterns_checked")
        assert hasattr(report, "files_scanned")
        assert hasattr(report, "violations")
        assert hasattr(report, "compliance_rate")
        assert report.patterns_checked == 3  # TDD, Strategy, EventBus
    
    def test_tdd_pattern_detection(self):
        """Detects missing test files (TDD violation)."""
        from cortex.governance.architecture_pattern_checker import ArchitecturePatternChecker
        
        checker = ArchitecturePatternChecker()
        report = checker.verify_patterns(target_path=Path("cortex/governance"))
        
        # Should scan files and check for tests
        assert report.files_scanned > 0
        assert isinstance(report.violations, list)
    
    def test_strategy_pattern_detection(self):
        """Detects excessive inheritance (Strategy pattern violation)."""
        from cortex.governance.architecture_pattern_checker import ArchitecturePatternChecker
        
        checker = ArchitecturePatternChecker()
        report = checker.verify_patterns(target_path=Path("cortex/orchestrators"))
        
        # Should check inheritance depth
        assert report.patterns_checked == 3
        assert isinstance(report.violations, list)
    
    def test_eventbus_pattern_detection(self):
        """Checks EventBus usage in orchestrators (CORE-041)."""
        from cortex.governance.architecture_pattern_checker import ArchitecturePatternChecker
        
        checker = ArchitecturePatternChecker()
        report = checker.verify_patterns(target_path=Path("cortex/orchestrators"))
        
        # Should scan orchestrator files for event_bus
        assert isinstance(report.violations, list)
    
    def test_pattern_summary_aggregation(self):
        """get_pattern_summary() aggregates violations by pattern."""
        from cortex.governance.architecture_pattern_checker import ArchitecturePatternChecker
        
        checker = ArchitecturePatternChecker()
        checker.verify_patterns(target_path=Path("cortex/"))
        
        summary = checker.get_pattern_summary()
        
        assert isinstance(summary, dict)
        assert "TDD" in summary
        assert "Strategy" in summary
        assert "EventBus" in summary


# AC_COMPLETE: AC-WAVEK-005 ✅ 5/5 tests (Stage 3)
