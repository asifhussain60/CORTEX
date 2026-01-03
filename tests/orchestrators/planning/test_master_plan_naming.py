"""
Tests for meaningful master plan filename generation.

Tests the fix for: Master plan files should have meaningful names
derived from plan folder, not generic "00-master-plan.md"
"""

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path


class TestMasterPlanNaming:
    """Test master plan filename generation."""
    
    def _get_orchestrator_instance(self):
        """Create minimal orchestrator instance for testing."""
        from src.orchestrators.planning.planning_orchestrator_v5 import PlanningOrchestratorV5
        
        # Create with required config_path
        manifest_path = "cortex-brain/manifests/orchestrators/planning-system-5.0-manifest.yaml"
        
        # Mock state_db
        mock_db = MagicMock()
        
        return PlanningOrchestratorV5(
            config_path=manifest_path,
            state_db=mock_db
        )
    
    def test_simple_name(self):
        """Test simple plan name without hyphens."""
        orch = self._get_orchestrator_instance()
        result = orch._generate_master_plan_filename("authentication")
        assert result == "00-authentication.md"
        assert len(result) <= 25
    
    def test_with_version_suffix(self):
        """Test plan name with version suffix."""
        orch = self._get_orchestrator_instance()
        result = orch._generate_master_plan_filename("vacuum-v2-migration")
        assert result == "00-vacuum-v2.md"
        assert len(result) <= 25
    
    def test_long_name_truncation(self):
        """Test that long names are truncated properly."""
        orch = self._get_orchestrator_instance()
        result = orch._generate_master_plan_filename(
            "glassmorphism-css-standardization-refactor-system"
        )
        # Should take first word + system suffix, then truncate
        assert result.startswith("00-glassmorphism")
        assert len(result) <= 25
        assert result.endswith(".md")
    
    def test_glassmorphism_example(self):
        """Test real-world example: glassmorphism-css-standardization."""
        orch = self._get_orchestrator_instance()
        result = orch._generate_master_plan_filename(
            "glassmorphism-css-standardization"
        )
        # Should be "00-glassmorphism.md" (17 chars)
        assert result == "00-glassmorphism.md"
        assert len(result) == 19  # 00-glassmorphism.md
    
    def test_ado_v2_example(self):
        """Test real-world example: ado-v2-migration."""
        orch = self._get_orchestrator_instance()
        result = orch._generate_master_plan_filename("ado-v2-migration")
        assert result == "00-ado-v2.md"
        assert len(result) == 12
    
    def test_vacuum_example(self):
        """Test real-world example: vacuum-v2-migration."""
        orch = self._get_orchestrator_instance()
        result = orch._generate_master_plan_filename("vacuum-v2-migration")
        assert result == "00-vacuum-v2.md"
        assert len(result) == 15
    
    def test_single_word(self):
        """Test single-word plan name."""
        orch = self._get_orchestrator_instance()
        result = orch._generate_master_plan_filename("cleanup")
        assert result == "00-cleanup.md"
        assert len(result) <= 25
    
    def test_with_refactor_suffix(self):
        """Test plan name with 'refactor' suffix (version takes priority)."""
        orch = self._get_orchestrator_instance()
        result = orch._generate_master_plan_filename("cortex-v5-refactor")
        # Algorithm prioritizes version suffixes over 'refactor'
        assert result == "00-cortex-v5.md"
        assert len(result) <= 25
    
    def test_with_system_suffix(self):
        """Test plan name with 'system' suffix."""
        orch = self._get_orchestrator_instance()
        result = orch._generate_master_plan_filename("planning-system-v5")
        assert result == "00-planning-system.md"
        assert len(result) <= 25
    
    def test_no_duplicate_hyphens(self):
        """Test that result doesn't have duplicate hyphens."""
        orch = self._get_orchestrator_instance()
        result = orch._generate_master_plan_filename("test--plan--v2")
        assert "--" not in result
    
    def test_no_trailing_hyphen(self):
        """Test that result doesn't end with hyphen before .md."""
        orch = self._get_orchestrator_instance()
        result = orch._generate_master_plan_filename("test-plan-")
        assert not result.endswith("-.md")
        assert result.endswith(".md")
    
    def test_maximum_length_constraint(self):
        """Test all generated names respect 25-char limit."""
        orch = self._get_orchestrator_instance()
        
        test_cases = [
            "simple",
            "authentication-system-v2",
            "glassmorphism-css-standardization-refactor",
            "very-long-plan-name-that-exceeds-limits-significantly",
            "a-b-c-d-e-f-g-h-i-j-k-l-m-n-o-p-q-r-s-t-u-v-w-x-y-z"
        ]
        
        for plan_name in test_cases:
            result = orch._generate_master_plan_filename(plan_name)
            assert len(result) <= 25, f"Failed for: {plan_name} -> {result}"
            assert result.startswith("00-")
            assert result.endswith(".md")
