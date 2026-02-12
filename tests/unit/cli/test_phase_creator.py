"""
Tests for Phase Creator CLI Tool

AC_START: AC-WAVE-I-002
Description: Comprehensive test suite for ENH-084 Phase Creator
Authority: WAVE-I execution plan
Testing: cortex/cli/phase_creator.py

Tests: 15 total (CLI operations, validation rules, templates)
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml
from click.testing import CliRunner

from cortex.cli.phase_creator import (
    PhaseCreator,
    PhaseTemplate,
    PhaseValidator,
    cli,
)


@pytest.fixture
def runner():
    """CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_workspace(tmp_path):
    """Temporary workspace for testing."""
    # Create directory structure
    registry = tmp_path / "cortex-registry" / "_cortex-master"
    registry.mkdir(parents=True)
    
    templates = tmp_path / "cortex" / "templates" / "phases"
    templates.mkdir(parents=True)
    
    return tmp_path


@pytest.fixture
def phase_creator(temp_workspace):
    """Phase creator instance."""
    return PhaseCreator(cortex_root=temp_workspace)


@pytest.fixture
def valid_spec():
    """Valid phase specification."""
    return {
        "version": "1.0",
        "enhancement_id": "ENH-999",
        "title": "Test Enhancement",
        "created": "2026-02-12T10:00:00",
        "problem": {
            "current_state": "Current issue",
            "gaps": ["Gap 1", "Gap 2"],
            "impact": "Significant"
        },
        "solution": {
            "approach": "Strategic solution",
            "benefits": ["Benefit 1", "Benefit 2"]
        },
        "deliverables": ["Deliverable 1", "Deliverable 2"],
        "tests": {
            "target": 15,
            "coverage_minimum": 0.85
        },
        "roi": 8.5
    }


# =============================================================================
# TEMPLATE TESTS (3 tests)
# =============================================================================

class TestPhaseTemplates:
    """Tests for phase templates."""
    
    def test_standard_template_structure(self):
        """Standard template has required fields."""
        template = PhaseTemplate.STANDARD
        
        assert "enhancement_id" in template
        assert "title" in template
        assert "problem" in template
        assert "solution" in template
        assert "deliverables" in template
        assert "tests" in template
    
    def test_enhancement_template_has_waves(self):
        """Enhancement template includes waves structure."""
        template = PhaseTemplate.ENHANCEMENT
        
        assert "waves" in template
        assert "cleanup_requirements" in template
        assert template["cleanup_requirements"]["vacuum_per_wave"] is True
    
    def test_wave_template_structure(self):
        """Wave template has wave-specific fields."""
        template = PhaseTemplate.WAVE
        
        assert "wave_id" in template
        assert "name" in template
        assert "release" in template
        assert "requires" in template
        assert "deliverables" in template


# =============================================================================
# VALIDATOR TESTS (5 tests)
# =============================================================================

class TestPhaseValidator:
    """Tests for phase validator."""
    
    def test_validator_accepts_valid_spec(self, valid_spec):
        """Validator accepts valid specification."""
        validator = PhaseValidator()
        
        result = validator.validate(valid_spec)
        
        assert result is True
        assert len(validator.errors) == 0
    
    def test_validator_rejects_missing_required_fields(self):
        """Validator rejects spec with missing required fields."""
        validator = PhaseValidator()
        spec = {"title": "Test"}  # Missing enhancement_id
        
        result = validator.validate(spec)
        
        assert result is False
        assert len(validator.errors) > 0
        assert any("enhancement_id" in err for err in validator.errors)
    
    def test_validator_checks_naming_convention(self):
        """Validator checks CORE-028 naming conventions."""
        validator = PhaseValidator()
        spec = {
            "enhancement_id": "INVALID-ID",  # Wrong prefix
            "title": "Test",
            "problem": {"current_state": "x"},
            "solution": {"approach": "x"},
            "deliverables": ["x"]
        }
        
        result = validator.validate(spec)
        
        assert result is False
        assert any("enhancement_id" in err for err in validator.errors)
    
    def test_validator_enforces_test_coverage_minimum(self):
        """Validator enforces 80% minimum test coverage."""
        validator = PhaseValidator()
        spec = {
            "enhancement_id": "ENH-999",
            "title": "Test",
            "problem": {"current_state": "x"},
            "solution": {"approach": "x"},
            "deliverables": ["x"],
            "tests": {
                "coverage_minimum": 0.50  # Too low
            }
        }
        
        result = validator.validate(spec)
        
        assert result is False
        assert any("coverage" in err.lower() for err in validator.errors)
    
    def test_validator_warns_on_high_roi_without_justification(self, valid_spec):
        """Validator warns when high ROI lacks justification."""
        validator = PhaseValidator()
        spec = valid_spec.copy()
        spec["roi"] = 9.5  # High ROI
        # No roi_justification field
        
        result = validator.validate(spec)
        
        # Should pass but have warnings
        assert result is True
        assert len(validator.warnings) > 0


# =============================================================================
# PHASE CREATOR TESTS (4 tests)
# =============================================================================

class TestPhaseCreator:
    """Tests for phase creator."""
    
    def test_creator_initialization(self, phase_creator):
        """Phase creator initializes correctly."""
        assert phase_creator.cortex_root is not None
        assert phase_creator.registry_path is not None
        assert phase_creator.validator is not None
    
    def test_create_from_standard_template(self, phase_creator):
        """Can create spec from standard template."""
        spec = phase_creator.create_from_template(
            "standard",
            enhancement_id="ENH-100",
            title="Test Enhancement"
        )
        
        assert spec["enhancement_id"] == "ENH-100"
        assert spec["title"] == "Test Enhancement"
        assert "created" in spec
    
    def test_create_from_enhancement_template(self, phase_creator):
        """Can create spec from enhancement template."""
        spec = phase_creator.create_from_template(
            "enhancement",
            enhancement_id="ENH-200",
            title="Complex Enhancement"
        )
        
        assert spec["enhancement_id"] == "ENH-200"
        assert "waves" in spec
        assert "cleanup_requirements" in spec
    
    def test_save_spec_creates_file(self, phase_creator, valid_spec, tmp_path):
        """Saving spec creates YAML file."""
        output_path = tmp_path / "test-phase.yaml"
        
        phase_creator.save_spec(valid_spec, output_path)
        
        assert output_path.exists()
        
        # Verify content
        with open(output_path) as f:
            loaded = yaml.safe_load(f)
        
        assert loaded["enhancement_id"] == valid_spec["enhancement_id"]


# =============================================================================
# CLI TESTS (3 tests)
# =============================================================================

class TestCLI:
    """Tests for CLI commands."""
    
    def test_create_command_with_required_args(self, runner, tmp_path):
        """Create command works with required arguments."""
        output = tmp_path / "test.yaml"
        
        result = runner.invoke(cli, [
            'create',
            '--template', 'standard',
            '--id', 'ENH-TEST',
            '--title', 'Test Phase',
            '--output', str(output)
        ], input='y\n')  # Confirm creation despite validation warnings
        
        assert result.exit_code == 0
        assert output.exists()
    
    def test_validate_command_accepts_valid_spec(self, runner, valid_spec, tmp_path):
        """Validate command accepts valid specification."""
        spec_file = tmp_path / "valid.yaml"
        with open(spec_file, 'w') as f:
            yaml.dump(valid_spec, f)
        
        result = runner.invoke(cli, [
            'validate',
            str(spec_file)
        ])
        
        assert result.exit_code == 0
        assert "passed" in result.output.lower()
    
    def test_lint_command_provides_detailed_report(self, runner, valid_spec, tmp_path):
        """Lint command provides detailed validation report."""
        spec_file = tmp_path / "test.yaml"
        with open(spec_file, 'w') as f:
            yaml.dump(valid_spec, f)
        
        result = runner.invoke(cli, [
            'lint',
            str(spec_file)
        ])
        
        assert result.exit_code == 0
        assert "linting" in result.output.lower()
        assert valid_spec["title"] in result.output


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestPhaseCreatorIntegration:
    """Integration tests for full workflow."""
    
    def test_end_to_end_phase_creation(self, runner, tmp_path):
        """Complete workflow: create → validate → test stub."""
        output = tmp_path / "enh-integration.yaml"
        
        # Create with confirmation
        result = runner.invoke(cli, [
            'create',
            '--template', 'standard',
            '--id', 'ENH-INTEGRATION',
            '--title', 'Integration Test Phase',
            '--output', str(output)
        ], input='y\nn\n')  # Confirm validation, decline test stub
        
        assert output.exists()
        
        # Validate
        result = runner.invoke(cli, [
            'validate',
            str(output)
        ])
        
        # May have warnings but should load
        assert "enhancement_id" in result.output.lower() or "missing" in result.output.lower()


# AC_COMPLETE: AC-WAVE-I-002 ✅ 15 tests complete
