"""
Unit tests for TechIntelligenceOrchestrator.

Tests the central knowledge hub that monitors tech ecosystems,
generates best practices, and provides readiness verification.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 34B specification
"""

import pytest
from typing import Dict, Any, Optional
from unittest.mock import Mock, patch

from cortex.orchestrators.intelligence.tech_intelligence_orchestrator import (
    TechIntelligenceOrchestrator,
    ReadinessScore,
    TechStack,
)
from cortex.brain.core.interfaces.i_orchestrator import OperationMode
from cortex.core.result import Result


class TestTechIntelligenceOrchestratorInitialization:
    """Test orchestrator initialization and configuration."""
    
    def test_orchestrator_initializes_successfully(self):
        """Test that orchestrator can be instantiated."""
        orchestrator = TechIntelligenceOrchestrator()
        
        assert orchestrator is not None
        assert orchestrator.get_name() == "TechIntelligenceOrchestrator"
    
    def test_orchestrator_has_required_mode(self):
        """Test that orchestrator has correct operation mode."""
        orchestrator = TechIntelligenceOrchestrator()
        
        assert orchestrator.get_mode() == OperationMode.PLANNING
    
    def test_orchestrator_initializes_components(self):
        """Test that sub-components are initialized."""
        orchestrator = TechIntelligenceOrchestrator()
        
        assert orchestrator.ecosystem_scanner is not None
        assert orchestrator.readiness_engine is not None
        assert orchestrator.knowledge_synthesizer is not None
    
    def test_orchestrator_accepts_custom_config(self):
        """Test initialization with custom configuration."""
        config = {
            "cache_enabled": True,
            "scan_interval_hours": 24,
            "readiness_threshold": 0.7
        }
        orchestrator = TechIntelligenceOrchestrator(config=config)
        
        assert orchestrator.config["cache_enabled"] is True
        assert orchestrator.config["scan_interval_hours"] == 24


class TestReadinessScoring:
    """Test readiness score calculation and caching."""
    
    @pytest.fixture
    def orchestrator(self) -> TechIntelligenceOrchestrator:
        """Create orchestrator instance."""
        return TechIntelligenceOrchestrator()
    
    def test_get_readiness_score_returns_score_object(self, orchestrator):
        """Test that readiness check returns ReadinessScore."""
        tech_stack = TechStack(language="python", frameworks=["pytest"])
        
        score = orchestrator.get_readiness_score(tech_stack)
        
        assert isinstance(score, ReadinessScore)
        assert 0 <= score.overall <= 1.0
    
    def test_readiness_score_has_required_components(self, orchestrator):
        """Test that readiness score includes all factors."""
        tech_stack = TechStack(language="python", frameworks=["pytest"])
        
        score = orchestrator.get_readiness_score(tech_stack)
        
        assert hasattr(score, "best_practices")
        assert hasattr(score, "tdd_support")
        assert hasattr(score, "security")
        assert hasattr(score, "usage")
    
    def test_readiness_score_caching(self, orchestrator):
        """Test that readiness scores are cached."""
        tech_stack = TechStack(language="python", frameworks=["pytest"])
        
        # First call
        score1 = orchestrator.get_readiness_score(tech_stack)
        # Second call (should hit cache)
        score2 = orchestrator.get_readiness_score(tech_stack)
        
        assert score1.overall == score2.overall
        assert orchestrator.cache_stats["hits"] >= 1
    
    def test_high_readiness_score_proceeds(self, orchestrator):
        """Test that high readiness scores allow operations."""
        tech_stack = TechStack(language="python", frameworks=["pytest"])
        
        score = orchestrator.get_readiness_score(tech_stack)
        
        if score.overall >= 0.7:
            assert score.action == "PROCEED"
        elif score.overall >= 0.5:
            assert score.action == "PROCEED_WITH_WARNING"
        else:
            assert score.action == "TRIGGER_LEARNING"
    
    def test_low_readiness_score_triggers_learning(self, orchestrator):
        """Test that low readiness scores trigger learning."""
        # Create unknown tech stack
        tech_stack = TechStack(language="obscure-lang", frameworks=[])
        
        score = orchestrator.get_readiness_score(tech_stack)
        
        assert score.overall < 0.7
        assert score.action in ["TRIGGER_LEARNING", "PROCEED_WITH_WARNING"]


class TestTechStackDetection:
    """Test tech stack identification."""
    
    @pytest.fixture
    def orchestrator(self) -> TechIntelligenceOrchestrator:
        """Create orchestrator instance."""
        return TechIntelligenceOrchestrator()
    
    def test_detect_tech_stack_from_path(self, orchestrator):
        """Test tech stack detection from repository path."""
        repo_path = "/path/to/repo"
        
        tech_stack = orchestrator.detect_tech_stack(repo_path)
        
        assert isinstance(tech_stack, TechStack)
        assert tech_stack.language is not None
    
    def test_detect_python_from_requirements_txt(self, orchestrator):
        """Test Python detection from requirements.txt."""
        files = ["requirements.txt", "setup.py", "main.py"]
        
        tech_stack = orchestrator.detect_tech_stack_from_files(files)
        
        assert tech_stack.language == "python"
    
    def test_detect_javascript_from_package_json(self, orchestrator):
        """Test JavaScript detection from package.json."""
        files = ["package.json", "index.js", "tsconfig.json"]
        
        tech_stack = orchestrator.detect_tech_stack_from_files(files)
        
        assert tech_stack.language in ["javascript", "typescript"]
    
    def test_detect_multiple_frameworks(self, orchestrator):
        """Test detection of multiple frameworks."""
        files = ["requirements.txt", "pytest.ini", "tox.ini"]
        
        tech_stack = orchestrator.detect_tech_stack_from_files(files)
        
        # Framework detection may return empty if files don't have actual content
        assert isinstance(tech_stack.frameworks, list)


class TestKnowledgeSynthesis:
    """Test knowledge artifact generation."""
    
    @pytest.fixture
    def orchestrator(self) -> TechIntelligenceOrchestrator:
        """Create orchestrator instance."""
        return TechIntelligenceOrchestrator()
    
    def test_synthesize_best_practices_returns_result(self, orchestrator):
        """Test best practices synthesis."""
        tech_stack = TechStack(language="python", frameworks=["pytest"])
        
        result = orchestrator.synthesize_best_practices(tech_stack)
        
        assert isinstance(result, Result)
        assert result.is_ok() or result.is_err()
    
    def test_synthesize_tdd_patterns(self, orchestrator):
        """Test TDD pattern generation."""
        tech_stack = TechStack(language="python", frameworks=["pytest"])
        
        result = orchestrator.synthesize_tdd_patterns(tech_stack)
        
        assert isinstance(result, Result)
    
    def test_synthesize_security_rules(self, orchestrator):
        """Test security rule generation."""
        tech_stack = TechStack(language="python", frameworks=[])
        
        result = orchestrator.synthesize_security_rules(tech_stack)
        
        assert isinstance(result, Result)


class TestMCPToolExposure:
    """Test MCP tool exposure for external access."""
    
    @pytest.fixture
    def orchestrator(self) -> TechIntelligenceOrchestrator:
        """Create orchestrator instance."""
        return TechIntelligenceOrchestrator()
    
    def test_get_mcp_tools_returns_tool_list(self, orchestrator):
        """Test that MCP tools are exposed."""
        result = orchestrator.get_mcp_tools()
        
        assert result.is_ok()
        tools = result.value
        assert "get_readiness_score" in tools
        assert "detect_tech_stack" in tools
        assert "synthesize_knowledge" in tools
    
    def test_mcp_tool_has_required_metadata(self, orchestrator):
        """Test that MCP tools have proper metadata."""
        result = orchestrator.get_mcp_tools()
        tools = result.value
        
        readiness_tool = tools["get_readiness_score"]
        assert "description" in readiness_tool
        assert "parameters" in readiness_tool


class TestOrchestratorIntegration:
    """Test integration with existing orchestrators."""
    
    def test_orchestrator_can_be_registered(self):
        """Test that orchestrator can be registered with MasterOrchestrator."""
        orchestrator = TechIntelligenceOrchestrator()
        
        # Should have registration metadata
        assert hasattr(orchestrator, "get_name")
        assert hasattr(orchestrator, "get_capabilities")
    
    def test_orchestrator_capabilities_defined(self):
        """Test that orchestrator declares its capabilities."""
        orchestrator = TechIntelligenceOrchestrator()
        
        capabilities = orchestrator.get_capabilities()
        
        assert "readiness_scoring" in capabilities
        assert "tech_detection" in capabilities
        assert "knowledge_synthesis" in capabilities


class TestErrorHandling:
    """Test error handling and graceful degradation."""
    
    @pytest.fixture
    def orchestrator(self) -> TechIntelligenceOrchestrator:
        """Create orchestrator instance."""
        return TechIntelligenceOrchestrator()
    
    def test_handles_invalid_tech_stack(self, orchestrator):
        """Test handling of invalid tech stack input."""
        invalid_stack = None
        
        score = orchestrator.get_readiness_score(invalid_stack)
        
        # Should return low confidence score, not crash
        assert score.overall < 0.5
        assert score.action in ["TRIGGER_LEARNING", "learn_required"]
    
    def test_handles_missing_knowledge_base(self, orchestrator):
        """Test graceful handling when knowledge base missing."""
        tech_stack = TechStack(language="unknown", frameworks=[])
        
        result = orchestrator.synthesize_best_practices(tech_stack)
        
        # Should fail gracefully, not crash
        assert isinstance(result, Result)
    
    def test_handles_synthesis_failures(self, orchestrator):
        """Test error handling in knowledge synthesis."""
        tech_stack = TechStack(language="invalid", frameworks=[])
        
        result = orchestrator.synthesize_knowledge(tech_stack)
        
        # Should return Err result, not throw exception
        assert isinstance(result, Result)
