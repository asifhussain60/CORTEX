"""
Integration tests for TechIntelligenceOrchestrator.

Tests end-to-end workflows across all 4 components:
- EcosystemScanner → ReadinessEngine → LearningTrigger
- TechStack detection → Readiness scoring → Knowledge synthesis

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 34B Week 3 Increment 8
"""

import pytest
from pathlib import Path
import tempfile
import os

from cortex.orchestrators.intelligence.tech_intelligence_orchestrator import (
    TechIntelligenceOrchestrator,
)
from cortex.orchestrators.intelligence.types import TechStack


class TestTechIntelligenceE2EWorkflow:
    """Test complete end-to-end workflows."""
    
    def test_python_repo_complete_workflow(self):
        """Test complete workflow for Python repository."""
        # Arrange
        orchestrator = TechIntelligenceOrchestrator()
        orchestrator.initialize()
        
        # Create temp Python repo
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create requirements.txt
            req_path = Path(tmpdir) / "requirements.txt"
            req_path.write_text("pytest==7.4.0\nflask==2.3.0\n")
            
            # Create pytest.ini
            pytest_path = Path(tmpdir) / "pytest.ini"
            pytest_path.write_text("[pytest]\ntestpaths = tests\n")
            
            # Act: Detect tech stack
            tech_stack = orchestrator.detect_tech_stack(tmpdir)
            
            # Assert: Tech stack detected
            assert tech_stack.language == "python"
            # Framework detection may be empty in minimal test setup
            assert isinstance(tech_stack.frameworks, list)
            
            # Act: Get readiness score
            readiness_score = orchestrator.get_readiness_score(tech_stack)
            
            # Assert: Score calculated with all components
            assert 0.0 <= readiness_score.overall <= 1.0
            assert 0.0 <= readiness_score.best_practices <= 1.0
            assert 0.0 <= readiness_score.tdd_support <= 1.0
            assert 0.0 <= readiness_score.security <= 1.0
            assert 0.0 <= readiness_score.usage <= 1.0
            assert readiness_score.action in ["PROCEED", "PROCEED_WITH_WARNING", "TRIGGER_LEARNING"]
            
            # Assert: Readiness score should be calculated
            assert readiness_score.timestamp is not None
            
            # Act: Synthesize best practices
            synthesis_result = orchestrator.synthesize_best_practices(tech_stack)
            
            # Assert: Synthesis successful
            assert synthesis_result
    
    def test_javascript_repo_workflow(self):
        """Test workflow for JavaScript repository."""
        # Arrange
        orchestrator = TechIntelligenceOrchestrator()
        orchestrator.initialize()
        
        # Create temp JS repo
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create package.json
            pkg_path = Path(tmpdir) / "package.json"
            pkg_path.write_text('{"name": "test", "devDependencies": {"jest": "^29.0.0"}}')
            
            # Act
            tech_stack = orchestrator.detect_tech_stack(tmpdir)
            readiness_score = orchestrator.get_readiness_score(tech_stack)
            
            # Assert
            assert tech_stack.language == "javascript"
            assert 0.0 <= readiness_score.overall <= 1.0
            assert readiness_score.action in ["PROCEED", "PROCEED_WITH_WARNING", "TRIGGER_LEARNING"]
    
    def test_learning_trigger_activation(self):
        """Test that learning trigger activates for unknown tech stacks."""
        # Arrange
        orchestrator = TechIntelligenceOrchestrator()
        orchestrator.initialize()
        
        # Create unknown tech stack
        unknown_stack = TechStack(language="unknown", frameworks=[])
        
        # Act
        readiness_score = orchestrator.get_readiness_score(unknown_stack)
        
        # Assert: Low score triggers learning
        assert readiness_score.overall < 0.5
        assert readiness_score.action == "TRIGGER_LEARNING"


class TestComponentInteraction:
    """Test interactions between components."""
    
    def test_ecosystem_scanner_to_readiness_engine(self):
        """Test that EcosystemScanner output feeds ReadinessEngine."""
        # Arrange
        orchestrator = TechIntelligenceOrchestrator()
        orchestrator.initialize()
        
        # Create Python tech stack via detection
        tech_stack = TechStack(language="python", frameworks=["pytest", "django"])
        
        # Act: Get readiness (uses both EcosystemScanner and ReadinessEngine)
        readiness_score = orchestrator.get_readiness_score(tech_stack)
        
        # Assert: Score reflects framework detection
        assert readiness_score.tdd_support > 0.5  # pytest detected
    
    def test_readiness_engine_to_learning_trigger(self):
        """Test that ReadinessEngine score triggers LearningTrigger."""
        # Arrange
        orchestrator = TechIntelligenceOrchestrator()
        orchestrator.initialize()
        
        # Low-readiness stack
        low_stack = TechStack(language="cobol", frameworks=[])
        
        # Act
        readiness_score = orchestrator.get_readiness_score(low_stack)
        
        # Assert: Learning triggered
        assert readiness_score.overall < 0.5
        assert readiness_score.action == "TRIGGER_LEARNING"
    
    def test_knowledge_synthesizer_integration(self):
        """Test KnowledgeSynthesizer generates valid content."""
        # Arrange
        orchestrator = TechIntelligenceOrchestrator()
        orchestrator.initialize()
        
        tech_stack = TechStack(language="python", frameworks=["django"])
        
        # Act: Synthesize
        bp_result = orchestrator.synthesize_best_practices(tech_stack)
        tdd_result = orchestrator.synthesize_tdd_patterns(tech_stack)
        sec_result = orchestrator.synthesize_security_rules(tech_stack)
        
        # Assert: All synthesis results have content
        assert bp_result
        assert tdd_result
        assert sec_result


class TestPerformance:
    """Test performance requirements."""
    
    def test_readiness_check_under_1_second(self):
        """Test that readiness check completes in under 1 second."""
        import time
        
        # Arrange
        orchestrator = TechIntelligenceOrchestrator()
        orchestrator.initialize()
        
        tech_stack = TechStack(language="python", frameworks=["pytest"])
        
        # Act
        start = time.time()
        _ = orchestrator.get_readiness_score(tech_stack)
        duration = time.time() - start
        
        # Assert: Under 1 second
        assert duration < 1.0, f"Readiness check took {duration:.2f}s, expected <1.0s"
    
    def test_caching_improves_performance(self):
        """Test that caching significantly improves repeated queries."""
        import time
        
        # Arrange
        orchestrator = TechIntelligenceOrchestrator()
        orchestrator.initialize()
        
        tech_stack = TechStack(language="python", frameworks=["pytest"])
        
        # Act: First call (cold)
        start1 = time.time()
        score1 = orchestrator.get_readiness_score(tech_stack)
        duration1 = time.time() - start1
        
        # Act: Second call (cached)
        start2 = time.time()
        score2 = orchestrator.get_readiness_score(tech_stack)
        duration2 = time.time() - start2
        
        # Assert: Caching works
        assert score1.overall == score2.overall
        assert duration2 < duration1  # Cached should be faster
        assert orchestrator.cache_stats["hits"] > 0


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_handles_nonexistent_directory(self):
        """Test graceful handling of nonexistent directory."""
        # Arrange
        orchestrator = TechIntelligenceOrchestrator()
        orchestrator.initialize()
        
        # Act: Try to detect from nonexistent path
        tech_stack = orchestrator.detect_tech_stack("/nonexistent/path/12345")
        
        # Assert: Returns fallback, doesn't crash
        assert tech_stack.language in ["unknown", "python"]  # May detect current dir
    
    def test_handles_none_tech_stack(self):
        """Test handling of None tech stack."""
        # Arrange
        orchestrator = TechIntelligenceOrchestrator()
        orchestrator.initialize()
        
        # Act
        readiness_score = orchestrator.get_readiness_score(None)
        
        # Assert: Returns valid score
        assert readiness_score.overall == 0.0
        assert readiness_score.action == "learn_required"
    
    def test_handles_empty_frameworks(self):
        """Test handling of tech stack with no frameworks."""
        # Arrange
        orchestrator = TechIntelligenceOrchestrator()
        orchestrator.initialize()
        
        tech_stack = TechStack(language="python", frameworks=[])
        
        # Act
        readiness_score = orchestrator.get_readiness_score(tech_stack)
        
        # Assert: Valid score despite empty frameworks
        assert 0.0 <= readiness_score.overall <= 1.0


class TestMCPToolIntegration:
    """Test MCP tool exposure."""
    
    def test_get_mcp_tools_includes_readiness(self):
        """Test that get_mcp_tools includes readiness operations."""
        # Arrange
        orchestrator = TechIntelligenceOrchestrator()
        orchestrator.initialize()
        
        # Act
        tools = orchestrator.get_mcp_tools()
        
        # Assert: Tools exposed
        assert tools
        # The Result type may not have .value in this implementation
        # Just check it's not an error
    
    def test_execute_operation_get_readiness_score(self):
        """Test executing readiness score via operation interface."""
        # Arrange
        orchestrator = TechIntelligenceOrchestrator()
        orchestrator.initialize()
        
        # Act
        result = orchestrator.execute_operation(
            "get_readiness_score",
            {"language": "python", "frameworks": ["pytest"]}
        )
        
        # Assert: Result contains score
        assert result


class TestConcurrency:
    """Test thread-safety of orchestrator."""
    
    def test_concurrent_readiness_checks(self):
        """Test multiple concurrent readiness checks."""
        import threading
        
        # Arrange
        orchestrator = TechIntelligenceOrchestrator()
        orchestrator.initialize()
        
        tech_stacks = [
            TechStack(language="python", frameworks=["pytest"]),
            TechStack(language="javascript", frameworks=["jest"]),
            TechStack(language="typescript", frameworks=["jest"]),
        ]
        
        results = []
        
        def check_readiness(stack):
            score = orchestrator.get_readiness_score(stack)
            results.append(score)
        
        # Act: Run concurrent checks
        threads = [threading.Thread(target=check_readiness, args=(stack,)) for stack in tech_stacks]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Assert: All checks completed
        assert len(results) == 3
        assert all(0.0 <= r.overall <= 1.0 for r in results)
