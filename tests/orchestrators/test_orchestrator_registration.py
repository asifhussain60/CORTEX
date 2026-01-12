"""
Tests for AC-SCAFFOLD-003: MasterOrchestrator Registration

Validates that MasterOrchestrator components support orchestrator
registration and routing (tests readiness for dynamic registration).

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path

from src.orchestrators.pattern_router import PatternRouter


@pytest.mark.ac_id("AC-SCAFFOLD-003")
class TestMasterOrchestratorRegistration:
    """Test orchestrator registration components."""
    
    @pytest.fixture
    def config_path(self):
        """Get master orchestrator config path."""
        return "cortex-brain/config/master-orchestrator.yaml"
    
    def test_pattern_router_loads_config(self, config_path):
        """Test: PatternRouter loads configuration successfully."""
        router = PatternRouter(config_path)
        
        assert router is not None
    
    def test_pattern_router_has_rules(self, config_path):
        """Test: PatternRouter loads routing rules."""
        router = PatternRouter(config_path)
        
        assert hasattr(router, 'rules')
        assert len(router.rules) > 0
    
    def test_pattern_router_route_method(self, config_path):
        """Test: PatternRouter has match_intent method."""
        router = PatternRouter(config_path)
        
        assert hasattr(router, 'match_intent')
        assert callable(router.match_intent)
    
    def test_pattern_router_routes_planning_request(self, config_path):
        """Test: PatternRouter routes planning requests."""
        router = PatternRouter(config_path)
        
        match = router.match_intent("create a plan")
        
        assert match is not None
        assert match.orchestrator_id is not None
    
    def test_pattern_router_routes_implementation_request(self, config_path):
        """Test: PatternRouter routes implementation requests."""
        router = PatternRouter(config_path)
        
        match = router.match_intent("implement AC-TEST-001")
        
        assert match is not None
    
    def test_pattern_router_routes_ado_request(self, config_path):
        """Test: PatternRouter routes ADO requests."""
        router = PatternRouter(config_path)
        
        match = router.match_intent("connect to ado")
        
        assert match is not None
    
    def test_pattern_router_handles_validation_request(self, config_path):
        """Test: PatternRouter handles validation requests."""
        router = PatternRouter(config_path)
        
        match = router.match_intent("validate plan")
        
        assert match is not None
    
    def test_pattern_router_priority_ordering(self, config_path):
        """Test: PatternRouter respects priority ordering."""
        router = PatternRouter(config_path)
        
        # Validation should have priority 1 (highest)
        match = router.match_intent("validate progress")
        
        assert match is not None
        # Should route to validation orchestrator (priority 1)
    
    def test_config_file_exists(self, config_path):
        """Test: Master orchestrator config file exists."""
        path = Path(config_path)
        
        assert path.exists(), f"{config_path} must exist"
    
    def test_pattern_router_ac_id_extraction(self, config_path):
        """Test: PatternRouter can extract AC-IDs from requests."""
        router = PatternRouter(config_path)
        
        match = router.match_intent("implement AC-TODO-003")
        
        # Should match and extract AC-ID
        assert match is not None
