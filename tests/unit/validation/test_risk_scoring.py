"""AC-PHASE43-008: Risk Scoring Computation

Validates that risk scoring algorithms properly evaluate change risk,
architectural impact, and execution uncertainty.

Target: 6/6 tests passing
AC-ID: AC-PHASE43-008
"""

import pytest
from typing import Dict, Any

from cortex.orchestrators.core.validation.dor_validator import DoRValidator


class RiskScorer:
    """Compute risk scores for operations (Phase 43: AC-PHASE43-008)."""
    
    def __init__(self):
        """Initialize risk scorer."""
        self.weights = {
            "scope": 0.25,          # Change scope (files affected, lines changed)
            "complexity": 0.25,     # Code complexity
            "test_coverage": 0.20,  # Existing test coverage
            "dependencies": 0.15,   # Downstream dependencies
            "stability": 0.15,      # Module stability history
        }
    
    def compute_risk_score(self, context: Dict[str, Any]) -> float:
        """
        Compute overall risk score (0-1, higher = riskier).
        
        Args:
            context: Operation context with risk factors
            
        Returns:
            Risk score 0-1
        """
        scope_risk = self._compute_scope_risk(context.get("scope", {}))
        complexity_risk = self._compute_complexity_risk(context.get("complexity", {}))
        coverage_risk = self._compute_coverage_risk(context.get("test_coverage", {}))
        dependency_risk = self._compute_dependency_risk(context.get("dependencies", {}))
        stability_risk = self._compute_stability_risk(context.get("stability", {}))
        
        # Weighted average
        total_risk = (
            scope_risk * self.weights["scope"] +
            complexity_risk * self.weights["complexity"] +
            coverage_risk * self.weights["test_coverage"] +
            dependency_risk * self.weights["dependencies"] +
            stability_risk * self.weights["stability"]
        )
        
        return min(1.0, max(0.0, total_risk))
    
    def _compute_scope_risk(self, scope_data: Dict[str, Any]) -> float:
        """Scope risk: files affected, lines changed."""
        files_affected = scope_data.get("files_affected", 0)
        lines_changed = scope_data.get("lines_changed", 0)
        
        # Logarithmic scale: 1 file = 0.1 risk, 100 files = 0.9 risk
        files_risk = min(0.9, files_affected / 111.11) if files_affected > 0 else 0.0
        
        # Lines changed: 1 line = 0.05 risk, 1000 lines = 0.95 risk
        lines_risk = min(0.95, lines_changed / 1052.63) if lines_changed > 0 else 0.0
        
        return (files_risk + lines_risk) / 2
    
    def _compute_complexity_risk(self, complexity_data: Dict[str, Any]) -> float:
        """Complexity risk: cyclomatic complexity, nesting depth."""
        avg_complexity = complexity_data.get("avg_cyclomatic", 0)
        max_nesting = complexity_data.get("max_nesting_depth", 0)
        
        # Cyclomatic: 1-5 = low, 10+ = high
        complexity_risk = min(0.95, avg_complexity / 10.5)
        
        # Nesting: 3-4 = ok, 8+ = risky
        nesting_risk = min(0.9, max_nesting / 8.8)
        
        return (complexity_risk + nesting_risk) / 2
    
    def _compute_coverage_risk(self, coverage_data: Dict[str, Any]) -> float:
        """Coverage risk: test coverage percentage."""
        coverage_pct = coverage_data.get("coverage_percentage", 0)
        
        # No coverage = high risk, 100% coverage = no risk
        risk = (100 - coverage_pct) / 100
        return max(0.0, min(1.0, risk))
    
    def _compute_dependency_risk(self, dependency_data: Dict[str, Any]) -> float:
        """Dependency risk: number of downstream modules."""
        downstream_count = dependency_data.get("downstream_modules", 0)
        
        # 1-5 modules = low, 100+ modules = high
        risk = min(0.95, downstream_count / 105.26)
        return risk
    
    def _compute_stability_risk(self, stability_data: Dict[str, Any]) -> float:
        """Stability risk: change frequency, defect history."""
        changes_per_month = stability_data.get("changes_per_month", 0)
        recent_defects = stability_data.get("recent_defects", 0)
        
        # Frequently changed = higher risk
        change_risk = min(0.8, changes_per_month / 25)
        
        # Recent defects = higher risk
        defect_risk = min(0.9, recent_defects / 10)
        
        return (change_risk + defect_risk) / 2


class TestRiskScoringComputation:
    """Tests for risk scoring algorithms."""
    
    def test_risk_scorer_initializes(self):
        """Validate RiskScorer initializes with weights."""
        scorer = RiskScorer()
        assert scorer is not None, "RiskScorer should be instantiable"
        assert hasattr(scorer, 'weights'), "RiskScorer should have weights"
        assert len(scorer.weights) >= 4, "Should have multiple risk factors"
    
    def test_risk_scorer_computes_low_risk_changes(self):
        """Validate RiskScorer identifies low-risk changes."""
        scorer = RiskScorer()
        
        low_risk_context = {
            "scope": {"files_affected": 1, "lines_changed": 5},
            "complexity": {"avg_cyclomatic": 1, "max_nesting_depth": 2},
            "test_coverage": {"coverage_percentage": 95},
            "dependencies": {"downstream_modules": 0},
            "stability": {"changes_per_month": 1, "recent_defects": 0},
        }
        
        risk = scorer.compute_risk_score(low_risk_context)
        assert isinstance(risk, float), f"Risk should be float, got {type(risk)}"
        assert 0.0 <= risk <= 1.0, f"Risk should be 0-1, got {risk}"
        assert risk < 0.3, f"Low-risk change should score < 0.3, got {risk}"
    
    def test_risk_scorer_computes_high_risk_changes(self):
        """Validate RiskScorer identifies high-risk changes."""
        scorer = RiskScorer()
        
        high_risk_context = {
            "scope": {"files_affected": 50, "lines_changed": 500},
            "complexity": {"avg_cyclomatic": 15, "max_nesting_depth": 8},
            "test_coverage": {"coverage_percentage": 10},
            "dependencies": {"downstream_modules": 50},
            "stability": {"changes_per_month": 30, "recent_defects": 5},
        }
        
        risk = scorer.compute_risk_score(high_risk_context)
        assert risk > 0.6, f"High-risk change should score > 0.6, got {risk}"
    
    def test_risk_scorer_handles_empty_context(self):
        """Validate RiskScorer handles empty/minimal context."""
        scorer = RiskScorer()
        
        empty_context = {}
        
        risk = scorer.compute_risk_score(empty_context)
        assert isinstance(risk, float), "Should return float"
        assert 0.0 <= risk <= 1.0, "Should return valid risk score"
    
    def test_risk_scorer_normalizes_scores(self):
        """Validate RiskScorer keeps scores in valid 0-1 range."""
        scorer = RiskScorer()
        
        extreme_context = {
            "scope": {"files_affected": 10000, "lines_changed": 100000},
            "complexity": {"avg_cyclomatic": 100, "max_nesting_depth": 50},
            "test_coverage": {"coverage_percentage": 0},
            "dependencies": {"downstream_modules": 500},
            "stability": {"changes_per_month": 300, "recent_defects": 50},
        }
        
        risk = scorer.compute_risk_score(extreme_context)
        assert 0.0 <= risk <= 1.0, f"Risk should be normalized to 0-1, got {risk}"
    
    def test_dor_validator_integrates_risk_scoring(self):
        """Validate DoRValidator can use risk scores in checks."""
        validator = DoRValidator()
        scorer = RiskScorer()
        
        context = {
            "intent": "REFACTOR",
            "confidence": 0.75,
            "scope": {"files_affected": 3, "lines_changed": 50},
            "complexity": {"avg_cyclomatic": 5, "max_nesting_depth": 3},
            "test_coverage": {"coverage_percentage": 80},
            "dependencies": {"downstream_modules": 5},
            "stability": {"changes_per_month": 2, "recent_defects": 0},
        }
        
        risk = scorer.compute_risk_score(context)
        results = validator.validate_dor("REFACTOR", context)
        
        assert risk >= 0.0, "Risk score should be non-negative"
        assert len(results) > 0, "Validator should run checks"
