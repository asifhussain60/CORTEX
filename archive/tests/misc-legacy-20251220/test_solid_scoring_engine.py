"""
SOLID Scoring Engine Tests

Tests for 0-100 scoring mechanism with violation deductions.

RED PHASE: Tests written FIRST to define expected behavior.
"""

import pytest
from pathlib import Path
from dataclasses import dataclass
from typing import List

# Import will fail initially (RED phase)
from src.workflows.solid_scoring_engine import (
    SOLIDScoringEngine,
    SOLIDScore
)
from src.workflows.refactoring_intelligence import CodeSmell, CodeSmellType


class TestSOLIDScoringEngine:
    """Test SOLID compliance scoring."""
    
    @pytest.fixture
    def engine(self):
        """Create scoring engine instance."""
        return SOLIDScoringEngine()
    
    def test_perfect_file_scores_100(self, engine):
        """Test: File with no violations scores 100%."""
        # RED: This test MUST fail initially
        
        # No violations = perfect score
        smells = []
        score = engine.score_file(Path("perfect.py"), smells)
        
        assert score.overall_score == 100
        assert score.srp_score == 100
        assert score.ocp_score == 100
        assert score.lsp_score == 100
        assert score.isp_score == 100
        assert score.dip_score == 100
        assert len(score.violations) == 0
        assert len(score.recommendations) == 0
    
    def test_srp_violation_deducts_15_points(self, engine):
        """Test: SRP violation deducts 15 points."""
        # RED: This test MUST fail initially
        
        smells = [
            CodeSmell(
                smell_type=CodeSmellType.SRP_VIOLATION,
                location="test.py:10:0",
                severity="high",
                description="Class has multiple responsibilities",
                confidence=0.90
            )
        ]
        
        score = engine.score_file(Path("test.py"), smells)
        
        assert score.overall_score == 85  # 100 - 15
        assert score.srp_score < 100
        assert len(score.violations) == 1
    
    def test_multiple_violations_compound_deductions(self, engine):
        """Test: Multiple violations compound deductions."""
        # RED: This test MUST fail initially
        
        smells = [
            CodeSmell(
                smell_type=CodeSmellType.SRP_VIOLATION,
                location="test.py:10:0",
                severity="high",
                description="SRP violation",
                confidence=0.90
            ),
            CodeSmell(
                smell_type=CodeSmellType.OCP_VIOLATION,
                location="test.py:20:0",
                severity="high",
                description="OCP violation",
                confidence=0.90
            ),
            CodeSmell(
                smell_type=CodeSmellType.DIP_VIOLATION,
                location="test.py:30:0",
                severity="high",
                description="DIP violation",
                confidence=0.90
            )
        ]
        
        score = engine.score_file(Path("test.py"), smells)
        
        # 100 - 15 (SRP) - 12 (OCP) - 10 (DIP) = 63
        assert score.overall_score == 63
        assert len(score.violations) == 3
    
    def test_score_below_70_triggers_recommendations(self, engine):
        """Test: Score <70% generates recommendations."""
        # RED: This test MUST fail initially
        
        smells = [
            CodeSmell(
                smell_type=CodeSmellType.SRP_VIOLATION,
                location="test.py:10:0",
                severity="high",
                description="Class UserManager has 5 responsibilities",
                confidence=0.90
            ),
            CodeSmell(
                smell_type=CodeSmellType.DIP_VIOLATION,
                location="test.py:25:0",
                severity="high",
                description="Depends on concrete MySQLDatabase",
                confidence=0.90
            ),
            CodeSmell(
                smell_type=CodeSmellType.TIGHT_COUPLING,
                location="test.py:1:0",
                severity="medium",
                description="20 imports detected",
                confidence=0.85
            )
        ]
        
        score = engine.score_file(Path("test.py"), smells)
        
        # Score should be below 70
        assert score.overall_score < 70
        
        # Should generate recommendations
        assert len(score.recommendations) > 0
        assert len(score.recommendations) <= 5  # Top 5 max
    
    def test_minimum_score_is_zero(self, engine):
        """Test: Score never goes below 0."""
        # RED: This test MUST fail initially
        
        # Create many violations (would exceed 100 points deduction)
        smells = [
            CodeSmell(
                smell_type=CodeSmellType.SRP_VIOLATION,
                location=f"test.py:{i*10}:0",
                severity="high",
                description=f"SRP violation {i}",
                confidence=0.90
            )
            for i in range(20)  # 20 x 15 = 300 points deduction
        ]
        
        score = engine.score_file(Path("test.py"), smells)
        
        assert score.overall_score >= 0
        assert score.overall_score == 0  # Minimum
    
    def test_per_principle_subscores(self, engine):
        """Test: Generates per-principle subscores."""
        # RED: This test MUST fail initially
        
        smells = [
            CodeSmell(
                smell_type=CodeSmellType.SRP_VIOLATION,
                location="test.py:10:0",
                severity="high",
                description="SRP violation",
                confidence=0.90
            ),
            CodeSmell(
                smell_type=CodeSmellType.SRP_VIOLATION,
                location="test.py:20:0",
                severity="high",
                description="Another SRP violation",
                confidence=0.90
            )
        ]
        
        score = engine.score_file(Path("test.py"), smells)
        
        # SRP should be affected (2 violations)
        assert score.srp_score < 100
        
        # Other principles should be perfect
        assert score.ocp_score == 100
        assert score.lsp_score == 100
        assert score.isp_score == 100
        assert score.dip_score == 100
    
    def test_coupling_violations_deduct_10_points(self, engine):
        """Test: Coupling violations deduct 10 points."""
        # RED: This test MUST fail initially
        
        smells = [
            CodeSmell(
                smell_type=CodeSmellType.TIGHT_COUPLING,
                location="test.py:1:0",
                severity="high",
                description="Circular dependency",
                confidence=0.95
            )
        ]
        
        score = engine.score_file(Path("test.py"), smells)
        
        assert score.overall_score == 90  # 100 - 10
    
    def test_recommendations_prioritized_by_severity(self, engine):
        """Test: Recommendations prioritized by severity."""
        # RED: This test MUST fail initially
        
        smells = [
            CodeSmell(
                smell_type=CodeSmellType.SRP_VIOLATION,
                location="test.py:10:0",
                severity="high",
                description="Critical SRP violation",
                confidence=0.90
            ),
            CodeSmell(
                smell_type=CodeSmellType.OCP_VIOLATION,
                location="test.py:20:0",
                severity="high",
                description="Critical OCP violation",
                confidence=0.90
            ),
            CodeSmell(
                smell_type=CodeSmellType.TIGHT_COUPLING,
                location="test.py:1:0",
                severity="medium",
                description="Moderate coupling",
                confidence=0.85
            )
        ]
        
        score = engine.score_file(Path("test.py"), smells)
        
        # Score should be below 70 (100 - 15 - 12 - 10 = 63)
        assert score.overall_score < 70
        
        # High severity should appear first
        assert len(score.recommendations) >= 1
        assert "SRP" in score.recommendations[0] or "responsibility" in score.recommendations[0].lower()


class TestScoreDeductionRules:
    """Test specific deduction rules."""
    
    def test_deduction_amounts(self):
        """Test: Verify deduction amounts match spec."""
        engine = SOLIDScoringEngine()
        
        # Verify deduction table
        assert engine.DEDUCTION_SRP == 15
        assert engine.DEDUCTION_OCP == 12
        assert engine.DEDUCTION_LSP == 10
        assert engine.DEDUCTION_ISP == 8
        assert engine.DEDUCTION_DIP == 10
        assert engine.DEDUCTION_COUPLING == 10
        assert engine.DEDUCTION_COHESION == 8


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
