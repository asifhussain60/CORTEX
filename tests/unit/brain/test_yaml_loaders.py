"""
Unit tests for YAML loaders (ENH-048 Phase 1).

Tests the loading and validation of machine-readable YAML files:
- core-rules.yaml
- audit-checklist.yaml
- modes.yaml
- response-format.yaml

Authority: ENH-048 (Prompt Unbloating System)
"""

import pytest
from pathlib import Path
from typing import Dict, List, Any
import yaml


# Test fixtures
@pytest.fixture
def cortex_registry_root():
    """Get the cortex-registry/_cortex-master root path."""
    return Path(__file__).parent.parent.parent.parent / "cortex-registry" / "_cortex-master"


@pytest.fixture
def governance_path(cortex_registry_root):
    """Get the governance directory path."""
    return cortex_registry_root / "governance"


@pytest.fixture
def meta_path(cortex_registry_root):
    """Get the meta directory path."""
    return cortex_registry_root / "meta"


# Core Rules YAML Tests
class TestCoreRulesYAML:
    """Test core-rules.yaml loading and structure."""
    
    def test_core_rules_file_exists(self, governance_path):
        """Test that core-rules.yaml exists."""
        core_rules_file = governance_path / "core-rules.yaml"
        assert core_rules_file.exists(), "core-rules.yaml not found"
    
    def test_core_rules_valid_yaml(self, governance_path):
        """Test that core-rules.yaml is valid YAML."""
        core_rules_file = governance_path / "core-rules.yaml"
        with open(core_rules_file, 'r') as f:
            data = yaml.safe_load(f)
        assert data is not None, "core-rules.yaml is empty"
        assert isinstance(data, dict), "core-rules.yaml must be a dictionary"
    
    def test_core_rules_has_meta(self, governance_path):
        """Test that core-rules.yaml has meta section."""
        core_rules_file = governance_path / "core-rules.yaml"
        with open(core_rules_file, 'r') as f:
            data = yaml.safe_load(f)
        assert 'meta' in data, "Missing meta section"
        assert 'version' in data['meta'], "Missing version in meta"
        assert 'updated' in data['meta'], "Missing updated in meta"
    
    def test_core_rules_has_rules(self, governance_path):
        """Test that core-rules.yaml has core_rules section."""
        core_rules_file = governance_path / "core-rules.yaml"
        with open(core_rules_file, 'r') as f:
            data = yaml.safe_load(f)
        assert 'core_rules' in data, "Missing core_rules section"
        assert isinstance(data['core_rules'], list), "core_rules must be a list"
        assert len(data['core_rules']) >= 14, "Expected at least 14 core rules"
    
    def test_core_rule_structure(self, governance_path):
        """Test that each core rule has required fields."""
        core_rules_file = governance_path / "core-rules.yaml"
        with open(core_rules_file, 'r') as f:
            data = yaml.safe_load(f)
        
        required_fields = ['id', 'name', 'category', 'priority', 'description', 'enforcement']
        
        for rule in data['core_rules']:
            for field in required_fields:
                assert field in rule, f"Rule {rule.get('id', 'UNKNOWN')} missing {field}"
    
    def test_core_rule_ids_unique(self, governance_path):
        """Test that all core rule IDs are unique."""
        core_rules_file = governance_path / "core-rules.yaml"
        with open(core_rules_file, 'r') as f:
            data = yaml.safe_load(f)
        
        rule_ids = [rule['id'] for rule in data['core_rules']]
        assert len(rule_ids) == len(set(rule_ids)), "Duplicate rule IDs detected"
    
    def test_enforcement_levels_defined(self, governance_path):
        """Test that enforcement_levels section exists."""
        core_rules_file = governance_path / "core-rules.yaml"
        with open(core_rules_file, 'r') as f:
            data = yaml.safe_load(f)
        
        assert 'enforcement_levels' in data, "Missing enforcement_levels section"
        levels = data['enforcement_levels']
        assert 'BLOCKED' in levels, "Missing BLOCKED enforcement level"
        assert 'WARNING' in levels, "Missing WARNING enforcement level"


# Audit Checklist YAML Tests
class TestAuditChecklistYAML:
    """Test audit-checklist.yaml loading and structure."""
    
    def test_audit_checklist_file_exists(self, governance_path):
        """Test that audit-checklist.yaml exists."""
        checklist_file = governance_path / "audit-checklist.yaml"
        assert checklist_file.exists(), "audit-checklist.yaml not found"
    
    def test_audit_checklist_valid_yaml(self, governance_path):
        """Test that audit-checklist.yaml is valid YAML."""
        checklist_file = governance_path / "audit-checklist.yaml"
        with open(checklist_file, 'r') as f:
            data = yaml.safe_load(f)
        assert data is not None, "audit-checklist.yaml is empty"
        assert isinstance(data, dict), "audit-checklist.yaml must be a dictionary"
    
    def test_audit_checklist_has_priorities(self, governance_path):
        """Test that audit-checklist.yaml has all priority levels."""
        checklist_file = governance_path / "audit-checklist.yaml"
        with open(checklist_file, 'r') as f:
            data = yaml.safe_load(f)
        
        assert 'priority_checks' in data, "Missing priority_checks section"
        priorities = data['priority_checks']
        assert 'P0' in priorities, "Missing P0 priority"
        assert 'P1' in priorities, "Missing P1 priority"
        assert 'P2' in priorities, "Missing P2 priority"
        assert 'P3' in priorities, "Missing P3 priority"
    
    def test_audit_check_structure(self, governance_path):
        """Test that each audit check has required fields."""
        checklist_file = governance_path / "audit-checklist.yaml"
        with open(checklist_file, 'r') as f:
            data = yaml.safe_load(f)
        
        required_fields = ['id', 'name', 'description', 'tool', 'evidence_required', 'severity']
        
        for priority in ['P0', 'P1', 'P2', 'P3']:
            checks = data['priority_checks'][priority]['checks']
            for check in checks:
                for field in required_fields:
                    assert field in check, f"Check {check.get('id', 'UNKNOWN')} missing {field}"
    
    def test_audit_check_ids_unique(self, governance_path):
        """Test that all audit check IDs are unique."""
        checklist_file = governance_path / "audit-checklist.yaml"
        with open(checklist_file, 'r') as f:
            data = yaml.safe_load(f)
        
        all_check_ids = []
        for priority in ['P0', 'P1', 'P2', 'P3']:
            checks = data['priority_checks'][priority]['checks']
            all_check_ids.extend([check['id'] for check in checks])
        
        assert len(all_check_ids) == len(set(all_check_ids)), "Duplicate check IDs detected"


# Modes YAML Tests
class TestModesYAML:
    """Test modes.yaml loading and structure."""
    
    def test_modes_file_exists(self, meta_path):
        """Test that modes.yaml exists."""
        modes_file = meta_path / "modes.yaml"
        assert modes_file.exists(), "modes.yaml not found"
    
    def test_modes_valid_yaml(self, meta_path):
        """Test that modes.yaml is valid YAML."""
        modes_file = meta_path / "modes.yaml"
        with open(modes_file, 'r') as f:
            data = yaml.safe_load(f)
        assert data is not None, "modes.yaml is empty"
        assert isinstance(data, dict), "modes.yaml must be a dictionary"
    
    def test_modes_has_all_modes(self, meta_path):
        """Test that modes.yaml has all HEXA-MODE definitions."""
        modes_file = meta_path / "modes.yaml"
        with open(modes_file, 'r') as f:
            data = yaml.safe_load(f)
        
        assert 'modes' in data, "Missing modes section"
        modes = data['modes']
        
        expected_modes = ['PRE-FLIGHT', 'AUDIT', 'DESIGN', 'PLAN', 'DIGEST', 'INTERACTIVE', 'META-AUDIT']
        for mode in expected_modes:
            assert mode in modes, f"Missing {mode} mode definition"
    
    def test_mode_structure(self, meta_path):
        """Test that each mode has required fields."""
        modes_file = meta_path / "modes.yaml"
        with open(modes_file, 'r') as f:
            data = yaml.safe_load(f)
        
        required_fields = ['name', 'trigger', 'agent', 'priority', 'description', 'flow']
        
        for mode_name, mode_spec in data['modes'].items():
            for field in required_fields:
                assert field in mode_spec, f"Mode {mode_name} missing {field}"
    
    def test_mode_priorities_unique(self, meta_path):
        """Test that mode priorities are mostly unique (except parallel modes)."""
        modes_file = meta_path / "modes.yaml"
        with open(modes_file, 'r') as f:
            data = yaml.safe_load(f)
        
        priorities = [mode['priority'] for mode in data['modes'].values()]
        # Allow some duplicate priorities (for parallel modes)
        assert len(set(priorities)) >= 5, "Too many duplicate priorities"


# Response Format YAML Tests
class TestResponseFormatYAML:
    """Test response-format.yaml loading and structure."""
    
    def test_response_format_file_exists(self, meta_path):
        """Test that response-format.yaml exists."""
        format_file = meta_path / "response-format.yaml"
        assert format_file.exists(), "response-format.yaml not found"
    
    def test_response_format_valid_yaml(self, meta_path):
        """Test that response-format.yaml is valid YAML."""
        format_file = meta_path / "response-format.yaml"
        with open(format_file, 'r') as f:
            data = yaml.safe_load(f)
        assert data is not None, "response-format.yaml is empty"
        assert isinstance(data, dict), "response-format.yaml must be a dictionary"
    
    def test_response_format_has_icons(self, meta_path):
        """Test that response-format.yaml has icon definitions."""
        format_file = meta_path / "response-format.yaml"
        with open(format_file, 'r') as f:
            data = yaml.safe_load(f)
        
        assert 'icons' in data, "Missing icons section"
        assert 'status' in data['icons'], "Missing status icons"
        
        required_status_icons = ['completed', 'planned', 'critical', 'warning', 'in_progress']
        for icon in required_status_icons:
            assert icon in data['icons']['status'], f"Missing {icon} status icon"
    
    def test_response_format_has_structure(self, meta_path):
        """Test that response-format.yaml has structure requirements."""
        format_file = meta_path / "response-format.yaml"
        with open(format_file, 'r') as f:
            data = yaml.safe_load(f)
        
        assert 'structure' in data, "Missing structure section"
        assert 'required_sections' in data['structure'], "Missing required_sections"
        assert 'forbidden' in data['structure'], "Missing forbidden patterns"
    
    def test_response_format_has_header(self, meta_path):
        """Test that response-format.yaml has header definition."""
        format_file = meta_path / "response-format.yaml"
        with open(format_file, 'r') as f:
            data = yaml.safe_load(f)
        
        assert 'header' in data, "Missing header section"
        assert data['header']['required'] == True, "Header must be required"
        assert 'template' in data['header'], "Missing header template"


# Integration Tests
class TestYAMLIntegration:
    """Test integration between YAML files."""
    
    def test_all_yaml_files_loadable(self, governance_path, meta_path):
        """Test that all YAML files can be loaded without errors."""
        yaml_files = [
            governance_path / "core-rules.yaml",
            governance_path / "audit-checklist.yaml",
            meta_path / "modes.yaml",
            meta_path / "response-format.yaml"
        ]
        
        for yaml_file in yaml_files:
            assert yaml_file.exists(), f"{yaml_file.name} not found"
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
            assert data is not None, f"{yaml_file.name} failed to load"
    
    def test_cross_references_valid(self, governance_path, meta_path):
        """Test that cross-references between YAML files are valid."""
        # Load core rules
        with open(governance_path / "core-rules.yaml", 'r') as f:
            core_rules = yaml.safe_load(f)
        
        # Load audit checklist
        with open(governance_path / "audit-checklist.yaml", 'r') as f:
            audit_checklist = yaml.safe_load(f)
        
        # Extract all rule IDs
        rule_ids = {rule['id'] for rule in core_rules['core_rules']}
        
        # Check that related_rules references are valid
        for priority in ['P0', 'P1', 'P2', 'P3']:
            checks = audit_checklist['priority_checks'][priority]['checks']
            for check in checks:
                if 'related_rules' in check:
                    for rule_id in check['related_rules']:
                        assert rule_id in rule_ids, f"Invalid rule reference: {rule_id} in {check['id']}"
