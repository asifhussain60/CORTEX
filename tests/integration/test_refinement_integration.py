"""
Integration test for Refinement Orchestrator routing and execution.
Tests end-to-end workflow via Master Orchestrator pattern matching.

Author: GitHub Copilot (Asif Hussain)
Created: January 4, 2026
Part of: CORTEX-5.0 Sub-Plan C50-01
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from src.orchestrators.pattern_router import PatternRouter, OrchestratorMatch
from src.orchestrators.refinement_orchestrator import RefinementOrchestrator


class TestRefinementOrchestrationIntegration:
    """Integration tests for Refinement Orchestrator routing and execution."""
    
    @pytest.fixture
    def pattern_router(self):
        """Create PatternRouter with master config."""
        config_path = "cortex-brain/config/master-orchestrator.yaml"
        router = PatternRouter(config_path)
        return router
    
    def test_pattern_matching_refine(self, pattern_router):
        """Test 'refine' command routes to refinement_orchestrator."""
        match = pattern_router.match_intent("refine src/module.py")
        
        assert match.is_matched
        assert match.orchestrator_id == "refinement_orchestrator"
        assert match.confidence == 1.0
        assert "refine" in match.matched_pattern.lower()
    
    def test_pattern_matching_improve(self, pattern_router):
        """Test 'improve' command routes to refinement_orchestrator."""
        match = pattern_router.match_intent("improve code quality")
        
        assert match.is_matched
        assert match.orchestrator_id == "refinement_orchestrator"
        assert match.confidence == 1.0
    
    def test_pattern_matching_optimize(self, pattern_router):
        """Test 'optimize' command routes to refinement_orchestrator."""
        match = pattern_router.match_intent("optimize performance")
        
        assert match.is_matched
        assert match.orchestrator_id == "refinement_orchestrator"
        assert match.confidence == 1.0
    
    def test_pattern_matching_code_quality(self, pattern_router):
        """Test 'code quality' command routes to refinement_orchestrator."""
        match = pattern_router.match_intent("code quality check")
        
        assert match.is_matched
        assert match.orchestrator_id == "refinement_orchestrator"
        assert match.confidence == 1.0
    
    def test_pattern_matching_refactor(self, pattern_router):
        """Test 'refactor' command routes to refinement_orchestrator."""
        match = pattern_router.match_intent("refactor authentication module")
        
        assert match.is_matched
        assert match.orchestrator_id == "refinement_orchestrator"
        assert match.confidence == 1.0
    
    @pytest.mark.integration
    def test_end_to_end_dry_run(self, tmp_path):
        """Test complete workflow: routing → orchestrator → execution."""
        # 1. Pattern matching
        router = PatternRouter("cortex-brain/config/master-orchestrator.yaml")
        match = router.match_intent("refine tests/")
        
        assert match.is_matched
        assert match.orchestrator_id == "refinement_orchestrator"
        
        # 2. Orchestrator initialization
        from src.database.planning_state_db import PlanningStateDB
        
        db_path = tmp_path / "integration_test.db"
        state_db = PlanningStateDB(str(db_path))
        
        orchestrator = RefinementOrchestrator(state_db=state_db)
        
        # 3. Execute (dry run)
        result = orchestrator.execute(
            user_request="refine tests/",
            target_path=Path("tests/"),
            severity_threshold="medium",
            dry_run=True
        )
        
        # 4. Verify results
        assert result.success is True
        assert "code_analysis" in result.data
        assert "refactoring_plan" in result.data
        assert result.data.get("dry_run") is True
    
    @pytest.mark.integration
    def test_real_path_analysis(self, tmp_path):
        """Test orchestrator analyzes real Python files."""
        # Create test file
        test_file = tmp_path / "sample.py"
        test_file.write_text("""
def complex_function(a, b, c, d, e, f, g):
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    if e > 0:
                        if f > 0:
                            return g
    return 0

def long_method():
    \"\"\"This is a very long method.\"\"\"
    line1 = 1
    line2 = 2
    # ... imagine 50+ lines here
    return line1 + line2
""")
        
        from src.database.planning_state_db import PlanningStateDB
        
        db_path = tmp_path / "real_analysis.db"
        state_db = PlanningStateDB(str(db_path))
        
        orchestrator = RefinementOrchestrator(state_db=state_db)
        
        # Execute analysis
        result = orchestrator.execute(
            user_request=f"refine {test_file}",
            target_path=test_file,
            severity_threshold="low",
            dry_run=True
        )
        
        # Verify analysis detected issues
        assert result.success is True
        assert result.data["issues_identified"] > 0  # Should find high complexity
        
        # Check code analysis
        code_analysis = result.data.get("code_analysis", {})
        assert "complexity" in code_analysis
        
        # Should detect complex_function as complex
        complexity_funcs = list(code_analysis["complexity"].keys())
        assert len(complexity_funcs) > 0
    
    def test_pattern_priority(self, pattern_router):
        """Test refinement pattern has correct priority (60)."""
        # Find refinement rule
        refinement_rule = next(
            (r for r in pattern_router.rules if r.orchestrator_id == "refinement_orchestrator"),
            None
        )
        
        assert refinement_rule is not None
        assert refinement_rule.priority == 60
        
        # Verify it doesn't conflict with higher priority rules
        higher_priority_rules = [
            r for r in pattern_router.rules 
            if r.priority < refinement_rule.priority
        ]
        
        # Ensure no pattern overlap with higher priority rules
        test_inputs = [
            "refine module.py",
            "improve code quality",
            "optimize performance"
        ]
        
        for input_text in test_inputs:
            match = pattern_router.match_intent(input_text)
            assert match.orchestrator_id == "refinement_orchestrator"
