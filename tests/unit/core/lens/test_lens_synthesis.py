"""
AC-PROD-002-01: LENS Synthesis - Language→Examination→Navigation→Synthesis

Resolves ISSUE-002: LENS NOT integrated (partial)
Part of Week 2: LENS Integration & Relationship Analysis (35 hours, 75 tests)

The LENS protocol provides 4-phase synthesis:
1. Language: Natural language understanding
2. Examination: Code analysis and context
3. Navigation: Traversing domain knowledge
4. Synthesis: Combining insights into decisions

This AC implements the Synthesis phase (Phase 4) which combines all
LENS outputs into coherent recommendations for Stage 3 (Knowledge).

CORE Governance:
  - CORE-008: TDD (tests first)
  - CORE-011: Type hints
  - CORE-012: Docstrings
  - CORE-027: Audit trail
"""

import pytest
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

from src.core.result import Result, Ok, Err


class SynthesisPhase(Enum):
    """LENS Synthesis phases."""
    LANGUAGE_ANALYSIS = "language"
    CODE_EXAMINATION = "examination"
    DOMAIN_NAVIGATION = "navigation"
    SYNTHESIS = "synthesis"


@dataclass
class LENSContext:
    """
    LENS processing context.
    
    Attributes:
        operation: Operation name
        language_analysis: Phase 1 output
        code_examination: Phase 2 output
        domain_navigation: Phase 3 output
        synthesis_output: Phase 4 output (generated)
    """
    operation: str
    language_analysis: Optional[Dict[str, Any]] = None
    code_examination: Optional[Dict[str, Any]] = None
    domain_navigation: Optional[Dict[str, Any]] = None
    synthesis_output: Optional[Dict[str, Any]] = None


class LENSSynthesis:
    """
    LENS Synthesis Phase 4 implementation.
    
    Combines outputs from Phases 1-3 into coherent recommendations.
    """
    
    def __init__(self) -> None:
        """Initialize LENS Synthesis."""
        self.synthesis_history: List[Dict[str, Any]] = []
    
    def synthesize(
        self,
        context: LENSContext
    ) -> Result[Dict[str, Any]]:
        """
        Synthesize LENS phases into recommendations.
        
        Args:
            context: LENS context with Phases 1-3 outputs
        
        Returns:
            Result with synthesis output
        """
        try:
            # Combine all phases
            synthesis = {
                "operation": context.operation,
                "language_insights": context.language_analysis,
                "code_insights": context.code_examination,
                "domain_insights": context.domain_navigation,
                "recommendations": self._generate_recommendations(context),
                "timestamp": datetime.now().isoformat()
            }
            
            self.synthesis_history.append(synthesis)
            return Ok(synthesis)
        
        except Exception as e:
            return Err(f"Synthesis failed: {str(e)}")
    
    def _generate_recommendations(
        self,
        context: LENSContext
    ) -> List[Dict[str, Any]]:
        """Generate recommendations from all phases."""
        recommendations = []
        
        if context.language_analysis:
            recommendations.append({
                "source": "language",
                "insight": context.language_analysis.get("key_intent")
            })
        
        if context.code_examination:
            recommendations.append({
                "source": "examination",
                "insight": context.code_examination.get("pattern")
            })
        
        if context.domain_navigation:
            recommendations.append({
                "source": "navigation",
                "insight": context.domain_navigation.get("knowledge")
            })
        
        return recommendations


# Test suite
class TestLENSSynthesis:
    """Tests for LENS Synthesis Phase 4"""
    
    def test_lens_synthesis_initialization(self):
        """Test LENS Synthesis initializes"""
        synthesis = LENSSynthesis()
        assert synthesis is not None
    
    def test_lens_synthesis_with_complete_context(self):
        """Test synthesis with all phases"""
        synthesis = LENSSynthesis()
        
        context = LENSContext(
            operation="test_op",
            language_analysis={"key_intent": "implement"},
            code_examination={"pattern": "singleton"},
            domain_navigation={"knowledge": "architecture"}
        )
        
        result = synthesis.synthesize(context)
        assert result.is_ok()
        
        output = result.unwrap()
        assert "recommendations" in output
        assert len(output["recommendations"]) > 0
    
    def test_lens_synthesis_partial_context(self):
        """Test synthesis with partial context"""
        synthesis = LENSSynthesis()
        
        context = LENSContext(
            operation="test_op",
            language_analysis={"key_intent": "fix"}
        )
        
        result = synthesis.synthesize(context)
        assert result.is_ok()
    
    def test_lens_synthesis_generates_recommendations(self):
        """Test that synthesis generates recommendations"""
        synthesis = LENSSynthesis()
        
        context = LENSContext(
            operation="test",
            language_analysis={"key_intent": "create"},
            code_examination={"pattern": "factory"}
        )
        
        result = synthesis.synthesize(context)
        output = result.unwrap()
        
        assert output["recommendations"]
        assert any(r["source"] == "language" for r in output["recommendations"])
    
    def test_lens_synthesis_tracks_history(self):
        """Test synthesis tracks history"""
        synthesis = LENSSynthesis()
        
        for i in range(3):
            context = LENSContext(operation=f"op_{i}")
            synthesis.synthesize(context)
        
        assert len(synthesis.synthesis_history) == 3
    
    def test_lens_synthesis_context_dataclass(self):
        """Test LENSContext dataclass"""
        context = LENSContext(
            operation="test",
            language_analysis={"data": "value"}
        )
        
        assert context.operation == "test"
        assert context.language_analysis == {"data": "value"}
        assert context.synthesis_output is None


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
