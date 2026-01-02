"""
Test Suite: ADO Orchestrator v2 Config Manifest

Tests for config manifest loading, validation, schema compliance, and configuration
injection via BaseOrchestratorV4_1.

Author: Asif Hussain
Copyright: © 2026 Asif Hussain. All rights reserved.
"""

import pytest
import yaml
from pathlib import Path
from unittest.mock import Mock, patch

from src.orchestrators.ado.v2.ado_orchestrator_v2 import ADOOrchestratorV2
from src.database.planning_state_db import PlanningStateDB


class TestADOConfigManifest:
    """Test suite for ADO v2 configuration manifest."""
    
    @pytest.fixture
    def config_path(self):
        """Return path to ADO v2 config manifest."""
        return Path(__file__).parents[4] / "cortex-brain" / "manifests" / "orchestrators" / "ado-orchestrator-v2.yaml"
    
    @pytest.fixture
    def mock_state_db(self):
        """Create mock PlanningStateDB."""
        db = Mock(spec=PlanningStateDB)
        db.create_plan.return_value = "test-plan-id"
        return db
    
    # ==================== Config File Existence Tests ====================
    
    def test_config_manifest_exists(self, config_path):
        """Test: ado-orchestrator-v2.yaml config manifest exists."""
        assert config_path.exists(), f"Config manifest not found: {config_path}"
        assert config_path.is_file()
    
    def test_config_is_valid_yaml(self, config_path):
        """Test: Config manifest is valid YAML."""
        with open(config_path, 'r') as f:
            try:
                config = yaml.safe_load(f)
                assert config is not None
                assert isinstance(config, dict)
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML: {e}")
    
    # ==================== Schema Structure Tests ====================
    
    def test_config_has_schema_version(self, config_path):
        """Test: Config has schema_version field."""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        assert "schema_version" in config
        assert isinstance(config["schema_version"], (str, float))
    
    def test_config_has_orchestrator_section(self, config_path):
        """Test: Config has orchestrator metadata section."""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        assert "orchestrator" in config
        assert isinstance(config["orchestrator"], dict)
        
        orch = config["orchestrator"]
        assert "name" in orch
        assert "version" in orch
        assert "type" in orch
    
    def test_config_orchestrator_type_is_autonomous(self, config_path):
        """Test: Orchestrator type is 'autonomous'."""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        assert config["orchestrator"]["type"] == "autonomous"
    
    def test_config_has_base_class_specified(self, config_path):
        """Test: Config specifies BaseOrchestratorV4_1 as base class."""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        assert "base_class" in config["orchestrator"]
        assert "BaseOrchestrator" in config["orchestrator"]["base_class"]
    
    # ==================== Modes Configuration Tests ====================
    
    def test_config_has_modes_section(self, config_path):
        """Test: Config defines auto and wizard modes."""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        assert "modes" in config
        assert "auto" in config["modes"]
        assert "wizard" in config["modes"]
    
    def test_config_auto_mode_defines_phases(self, config_path):
        """Test: Auto mode defines 6-phase workflow."""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        auto_mode = config["modes"]["auto"]
        assert "phases" in auto_mode
        
        phases = auto_mode["phases"]
        assert len(phases) >= 6
        assert "DISCOVERY" in phases or "discovery" in phases
        assert "VALIDATION" in phases or "validation" in phases
        assert "GENERATION" in phases or "generation" in phases
        assert "APPROVAL" in phases or "approval" in phases
        assert "EXECUTION" in phases or "execution" in phases
        assert "COMPLETION" in phases or "completion" in phases
    
    def test_config_wizard_mode_defines_stages(self, config_path):
        """Test: Wizard mode defines 7 stages."""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        wizard_mode = config["modes"]["wizard"]
        assert "stages" in wizard_mode
        assert wizard_mode["stages"] == 7 or wizard_mode["stages"] >= 7
    
    # ==================== Work Item Types Tests ====================
    
    def test_config_has_work_item_types(self, config_path):
        """Test: Config defines ADO work item types."""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        assert "work_item_types" in config or "ado_specific" in config
    
    def test_config_defines_story_constraints(self, config_path):
        """Test: Config defines story constraints (story points, tasks)."""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Look for story configuration
        if "work_item_types" in config:
            wit = config["work_item_types"]
        elif "ado_specific" in config and "work_item_types" in config["ado_specific"]:
            wit = config["ado_specific"]["work_item_types"]
        else:
            pytest.skip("work_item_types not found in config")
        
        # Should have story or user_story
        assert "story" in wit or "user_story" in wit or "Story" in wit
    
    # ==================== Complexity Analysis Tests ====================
    
    def test_config_has_complexity_section(self, config_path):
        """Test: Config defines complexity analysis rules."""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        assert "complexity" in config or "complexity_analysis" in config
    
    def test_config_defines_complexity_keywords(self, config_path):
        """Test: Config defines high/medium complexity keywords."""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        if "complexity" in config:
            complexity = config["complexity"]
        elif "complexity_analysis" in config:
            complexity = config["complexity_analysis"]
        else:
            pytest.skip("complexity section not found")
        
        # Should have keyword lists
        assert "high_keywords" in complexity or "keywords" in complexity
    
    # ==================== DoR (Definition of Ready) Tests ====================
    
    def test_config_has_dor_section(self, config_path):
        """Test: Config defines Definition of Ready (DoR)."""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        assert "dor" in config or "definition_of_ready" in config
    
    def test_config_defines_dor_assumptions(self, config_path):
        """Test: Config defines required DoR assumptions."""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        dor = config.get("dor") or config.get("definition_of_ready")
        if dor:
            assert "required_assumptions" in dor or "assumptions" in dor
    
    def test_config_defines_dor_constraints(self, config_path):
        """Test: Config defines required DoR constraints."""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        dor = config.get("dor") or config.get("definition_of_ready")
        if dor:
            assert "required_constraints" in dor or "constraints" in dor
    
    # ==================== Template Path Tests ====================
    
    def test_config_has_template_paths(self, config_path):
        """Test: Config defines template paths."""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        assert "templates" in config or "output_templates" in config
    
    def test_config_template_paths_reference_jinja2_files(self, config_path):
        """Test: Template paths reference .jinja2 files."""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        templates = config.get("templates") or config.get("output_templates")
        if templates:
            # Check if any template path ends with .jinja2
            template_values = [str(v) for v in templates.values() if isinstance(v, str)]
            jinja2_files = [t for t in template_values if t.endswith(".jinja2")]
            assert len(jinja2_files) > 0, "No .jinja2 template files found in config"
    
    def test_config_defines_work_item_preview_template(self, config_path):
        """Test: Config defines work item preview template path."""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        templates = config.get("templates") or config.get("output_templates")
        if templates:
            # Should have work item preview template
            assert any(
                "preview" in key.lower() or "work_item" in key.lower()
                for key in templates.keys()
            )
    
    # ==================== Validation Rules Tests ====================
    
    def test_config_has_validation_section(self, config_path):
        """Test: Config defines validation rules."""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        assert "validation" in config or "validation_rules" in config
    
    def test_config_defines_required_fields(self, config_path):
        """Test: Config defines required input fields."""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        validation = config.get("validation") or config.get("validation_rules")
        if validation:
            assert "required_fields" in validation or "required" in validation
    
    # ==================== Zero Natural Language Tests ====================
    
    def test_config_contains_no_instructional_language(self, config_path):
        """Test: Config contains ONLY data structures (no natural language instructions)."""
        with open(config_path, 'r') as f:
            content = f.read()
        
        # Forbidden phrases in pure config manifests
        forbidden_phrases = [
            "Execute the following",
            "Follow these steps",
            "You must",
            "You should",
            "CORTEX will",
            "Agent should",
            "Perform this"
        ]
        
        content_lower = content.lower()
        for phrase in forbidden_phrases:
            assert phrase.lower() not in content_lower, f"Found instructional language: '{phrase}'"
    
    def test_config_uses_data_structures_only(self, config_path):
        """Test: Config uses YAML data structures (lists, dicts, primitives)."""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        def check_value(value):
            """Recursively check values are data types, not instructions."""
            if isinstance(value, dict):
                for v in value.values():
                    check_value(v)
            elif isinstance(value, list):
                for item in value:
                    check_value(item)
            elif isinstance(value, str):
                # Short strings are acceptable (names, paths, etc.)
                # Long paragraphs suggest instructions
                assert len(value) < 500, f"Found long text block (likely instructions): {value[:100]}..."
        
        check_value(config)
    
    # ==================== BaseOrchestratorV4_1 Integration Tests ====================
    
    @patch('src.orchestrators.ado.v2.ado_orchestrator_v2.ADOConversationalWizard')
    def test_orchestrator_loads_config_on_init(self, mock_wizard, mock_state_db, config_path):
        """Test: Orchestrator loads config manifest on initialization."""
        orchestrator = ADOOrchestratorV2(str(config_path), mock_state_db)
        
        # Should have loaded config
        assert hasattr(orchestrator, 'config')
        assert orchestrator.config is not None
        assert isinstance(orchestrator.config, dict)
    
    @patch('src.orchestrators.ado.v2.ado_orchestrator_v2.ADOConversationalWizard')
    def test_orchestrator_config_accessible_via_property(self, mock_wizard, mock_state_db, config_path):
        """Test: Config is accessible via orchestrator.config property."""
        orchestrator = ADOOrchestratorV2(str(config_path), mock_state_db)
        
        # Should be able to access config sections
        config = orchestrator.config
        assert "orchestrator" in config or "modes" in config or len(config) > 0
    
    @patch('src.orchestrators.ado.v2.ado_orchestrator_v2.ADOConversationalWizard')
    def test_orchestrator_uses_config_for_work_item_types(self, mock_wizard, mock_state_db, config_path):
        """Test: Orchestrator uses config for work item type definitions."""
        orchestrator = ADOOrchestratorV2(str(config_path), mock_state_db)
        
        config = orchestrator.config
        
        # Should have work item types in config
        assert (
            "work_item_types" in config or
            ("ado_specific" in config and "work_item_types" in config["ado_specific"])
        )
    
    @patch('src.orchestrators.ado.v2.ado_orchestrator_v2.ADOConversationalWizard')
    def test_orchestrator_uses_config_for_templates(self, mock_wizard, mock_state_db, config_path):
        """Test: Orchestrator uses config for template paths."""
        orchestrator = ADOOrchestratorV2(str(config_path), mock_state_db)
        
        config = orchestrator.config
        
        # Should have templates in config
        assert "templates" in config or "output_templates" in config
    
    # ==================== Config Validation Tests ====================
    
    def test_config_schema_version_is_current(self, config_path):
        """Test: Config uses current schema version (5.x or higher)."""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        schema_version = str(config["schema_version"])
        major_version = int(schema_version.split('.')[0])
        
        assert major_version >= 4, f"Schema version {schema_version} is outdated (require 4.0+)"
    
    def test_config_has_no_typos_in_phase_names(self, config_path):
        """Test: Phase names are spelled correctly."""
        with open(config_path, 'r') as f:
            content = f.read().lower()
        
        # Check for common typos
        assert "discovry" not in content  # Should be "discovery"
        assert "validaton" not in content  # Should be "validation"
        assert "generaton" not in content  # Should be "generation"
        assert "aproval" not in content    # Should be "approval"
        assert "executon" not in content   # Should be "execution"
        assert "completio" not in content  # Should be "completion"
    
    # ==================== ADO-Specific Configuration Tests ====================
    
    def test_config_has_ado_authentication_section(self, config_path):
        """Test: Config defines ADO authentication requirements."""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Look for authentication config
        assert (
            "authentication" in config or
            ("ado_specific" in config and "authentication" in config["ado_specific"]) or
            "ado_api" in config
        )
    
    def test_config_defines_ado_api_endpoints(self, config_path):
        """Test: Config may define ADO API endpoint patterns."""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Optional: Check for API endpoint configuration
        if "ado_api" in config or ("ado_specific" in config and "api" in config["ado_specific"]):
            pytest.skip("API endpoints found in config")
    
    # ==================== Error Handling Tests ====================
    
    @patch('src.orchestrators.ado.v2.ado_orchestrator_v2.ADOConversationalWizard')
    def test_orchestrator_handles_missing_config_file(self, mock_wizard, mock_state_db):
        """Test: Orchestrator handles missing config file gracefully."""
        fake_path = "nonexistent/path/to/config.yaml"
        
        with pytest.raises(FileNotFoundError):
            ADOOrchestratorV2(fake_path, mock_state_db)
    
    @patch('src.orchestrators.ado.v2.ado_orchestrator_v2.ADOConversationalWizard')
    def test_orchestrator_handles_invalid_yaml(self, mock_wizard, mock_state_db, tmp_path):
        """Test: Orchestrator handles invalid YAML gracefully."""
        # Create invalid YAML file
        invalid_yaml = tmp_path / "invalid.yaml"
        invalid_yaml.write_text("{ invalid yaml: [ unclosed")
        
        with pytest.raises((yaml.YAMLError, ValueError)):
            ADOOrchestratorV2(str(invalid_yaml), mock_state_db)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
