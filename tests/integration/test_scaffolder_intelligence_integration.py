"""Integration tests for OrchestratorScaffolder + ScaffolderIntelligenceAdapter.

AC_START: AC-WAVE2-S3-002
Description: Validate scaffolder intelligence integration
Authority: WAVE-2 Stage 3
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from cortex.tools.orchestrator_scaffolder import (
    OrchestratorScaffolder,
    ScaffoldConfig,
    ScaffoldType,
)
from cortex.tools.template_parser import TemplateParser


class TestScaffolderIntelligenceIntegration:
    """Test intelligence adapter integration with scaffolder."""
    
    @pytest.fixture
    def sample_template(self, tmp_path):
        """Create a sample orchestrator template."""
        template_content = """
name: TestOrchestrator
domain: testing
version: 1.0.0
tier: 1
description: Test orchestrator for intelligence integration

stages:
  - name: stage_1
    description: First stage
  - name: stage_2
    description: Second stage

hooks:
  pre_execute: []
  post_execute: []

integrations:
  mcp: true
  lens: true
"""
        template_file = tmp_path / "test_orchestrator.yaml"
        template_file.write_text(template_content)
        
        parser = TemplateParser()
        return parser.parse_file(str(template_file))
    
    @pytest.fixture
    def scaffolder(self):
        """Create scaffolder instance."""
        return OrchestratorScaffolder()
    
    def test_intelligence_adapter_flag_disabled(self, scaffolder, sample_template, tmp_path):
        """Test scaffolding WITHOUT intelligence adapter (template mode).
        
        Validates: Default behavior uses template-based generation
        """
        # AC_START: AC-WAVE2-S3-TEST-001
        
        config = ScaffoldConfig(
            output_dir=tmp_path,
            domain="testing",
            tier=1,
            include_tests=True,
            scaffold_type=ScaffoldType.TEST,
        )
        
        # Execute scaffolding (default: template mode)
        result = scaffolder.scaffold(sample_template, config)
        
        # Validate: Success
        assert result.success, f"Scaffolding failed: {result.errors}"
        
        # Validate: Test file generated
        assert len(result.files) > 0, "No files generated"
        test_file = result.files[0]
        
        assert "TestTestOrchestrator" in test_file.content
        assert "test_creation" in test_file.content  # Template-based test
        
        # AC_COMPLETE: AC-WAVE2-S3-TEST-001 ✅
    
    def test_intelligence_adapter_flag_enabled(self, scaffolder, sample_template, tmp_path):
        """Test scaffolding WITH intelligence adapter enabled.
        
        Validates: Intelligence mode generates different tests
        """
        # AC_START: AC-WAVE2-S3-TEST-002
        
        config = ScaffoldConfig(
            output_dir=tmp_path,
            domain="testing",
            tier=1,
            include_tests=True,
            scaffold_type=ScaffoldType.TEST,
            metadata={'use_intelligence_adapter': True},
        )
        
        # Execute scaffolding (intelligence mode)
        result = scaffolder.scaffold(sample_template, config)
        
        # Validate: Success
        assert result.success, f"Scaffolding failed: {result.errors}"
        
        # Validate: Test file generated with intelligence patterns
        assert len(result.files) > 0, "No files generated"
        test_file = result.files[0]
        
        # Intelligence-generated tests have different patterns
        assert "TestTestOrchestrator" in test_file.content
        assert "AC-" in test_file.content  # AC markers from intelligent generation
        assert "DEMAND:" in test_file.content  # Demand-based tests
        
        # AC_COMPLETE: AC-WAVE2-S3-TEST-002 ✅
    
    def test_intelligence_adapter_fallback(self, scaffolder, sample_template, tmp_path):
        """Test fallback to template mode if intelligence adapter fails.
        
        Validates: Graceful degradation when adapter unavailable
        """
        # AC_START: AC-WAVE2-S3-TEST-003
        
        config = ScaffoldConfig(
            output_dir=tmp_path,
            domain="testing",
            tier=1,
            include_tests=True,
            scaffold_type=ScaffoldType.TEST,
            metadata={'use_intelligence_adapter': True},
        )
        
        # Mock import failure
        with patch('cortex.tools.orchestrator_scaffolder.ScaffolderIntelligenceAdapter', 
                   side_effect=ImportError("Module not found")):
            result = scaffolder.scaffold(sample_template, config)
        
        # Validate: Still succeeds (fallback to template)
        assert result.success, "Should fallback gracefully"
        assert len(result.files) > 0
        
        # Should have template-based tests
        test_file = result.files[0]
        assert "test_creation" in test_file.content
        
        # AC_COMPLETE: AC-WAVE2-S3-TEST-003 ✅
    
    def test_generated_tests_structure(self, scaffolder, sample_template, tmp_path):
        """Test structure of generated test files.
        
        Validates: Tests have proper class structure, fixtures, AC markers
        """
        # AC_START: AC-WAVE2-S3-TEST-004
        
        config = ScaffoldConfig(
            output_dir=tmp_path,
            domain="testing",
            tier=1,
            include_tests=True,
            scaffold_type=ScaffoldType.TEST,
            metadata={'use_intelligence_adapter': True},
        )
        
        result = scaffolder.scaffold(sample_template, config)
        
        assert result.success
        test_file = result.files[0]
        
        # Validate structure
        assert "class Test" in test_file.content
        assert "@pytest.fixture" in test_file.content
        assert "def setup(self)" in test_file.content
        assert "self.orchestrator_class" in test_file.content
        
        # Validate imports
        assert "import pytest" in test_file.content
        assert "from pathlib import Path" in test_file.content
        assert "import yaml" in test_file.content
        
        # AC_COMPLETE: AC-WAVE2-S3-TEST-004 ✅

# AC_COMPLETE: AC-WAVE2-S3-002 ✅
