"""Tests for 3-layer response template architecture (ENH-TEMPLATE-001).

Phase 1 Tests (AC-TEMPLATE-001, AC-TEMPLATE-002):
- Directory structure validation
- YAML syntax validation
- Layer 1 (mandatory header) validation
- Layer 2 (executive summary) validation
- Layer 3 (orchestrator templates) validation

Author: Asif Hussain
Phase: 9.7
"""

import pytest
import yaml
from pathlib import Path


class TestLayerDirectoryStructure:
    """Test AC-TEMPLATE-001: Layer directory structure exists."""
    
    def test_response_templates_directory_exists(self):
        """Verify cortex-brain/response-templates/ exists."""
        templates_dir = Path("cortex-brain/response-templates")
        assert templates_dir.exists(), "response-templates directory must exist"
        assert templates_dir.is_dir(), "response-templates must be a directory"
    
    def test_orchestrators_subdirectory_exists(self):
        """Verify cortex-brain/response-templates/orchestrators/ exists."""
        orch_dir = Path("cortex-brain/response-templates/orchestrators")
        assert orch_dir.exists(), "orchestrators subdirectory must exist"
        assert orch_dir.is_dir(), "orchestrators must be a directory"


class TestLayer1MandatoryHeader:
    """Test AC-TEMPLATE-001: Layer 1 (mandatory header) structure."""
    
    def test_mandatory_header_yaml_exists(self):
        """Verify mandatory-header.yaml exists."""
        header_file = Path("cortex-brain/response-templates/mandatory-header.yaml")
        assert header_file.exists(), "mandatory-header.yaml must exist"
    
    def test_mandatory_header_yaml_valid_syntax(self):
        """Verify mandatory-header.yaml has valid YAML syntax."""
        header_file = Path("cortex-brain/response-templates/mandatory-header.yaml")
        with open(header_file, 'r') as f:
            data = yaml.safe_load(f)
        
        assert data is not None, "YAML must parse successfully"
        assert isinstance(data, dict), "YAML root must be dictionary"
    
    def test_mandatory_header_has_required_fields(self):
        """Verify mandatory-header.yaml has required fields."""
        header_file = Path("cortex-brain/response-templates/mandatory-header.yaml")
        with open(header_file, 'r') as f:
            data = yaml.safe_load(f)
        
        assert 'schema_version' in data, "Must have schema_version"
        assert 'layer' in data, "Must have layer field"
        assert data['layer'] == 1, "Layer must be 1"
        assert 'enforcement' in data, "Must specify enforcement rule"
        assert data['enforcement'] == 'CORE-026', "Must enforce CORE-026"
        assert 'header_template' in data, "Must have header_template"
    
    def test_mandatory_header_template_format(self):
        """Verify header template has CORTEX-4.0 format."""
        header_file = Path("cortex-brain/response-templates/mandatory-header.yaml")
        with open(header_file, 'r') as f:
            data = yaml.safe_load(f)
        
        template = data['header_template']
        assert "## 🧠 CORTEX" in template, "Must start with CORTEX header"
        assert "{operation_type}" in template, "Must have operation_type placeholder"
        assert "{phase}" in template, "Must have phase placeholder"
        assert "{orchestrator}" in template, "Must have orchestrator placeholder"
        assert "**Author:** Asif Hussain" in template, "Must have author attribution"
        assert "✅" in template, "Must have checkmark"


class TestLayer2ExecutiveSummary:
    """Test AC-TEMPLATE-002: Layer 2 (executive summary) structure."""
    
    def test_executive_summary_yaml_exists(self):
        """Verify executive-summary.yaml exists."""
        exec_file = Path("cortex-brain/response-templates/executive-summary.yaml")
        assert exec_file.exists(), "executive-summary.yaml must exist"
    
    def test_executive_summary_yaml_valid_syntax(self):
        """Verify executive-summary.yaml has valid YAML syntax."""
        exec_file = Path("cortex-brain/response-templates/executive-summary.yaml")
        with open(exec_file, 'r') as f:
            data = yaml.safe_load(f)
        
        assert data is not None, "YAML must parse successfully"
        assert isinstance(data, dict), "YAML root must be dictionary"
    
    def test_executive_summary_has_required_fields(self):
        """Verify executive-summary.yaml has required fields."""
        exec_file = Path("cortex-brain/response-templates/executive-summary.yaml")
        with open(exec_file, 'r') as f:
            data = yaml.safe_load(f)
        
        assert 'schema_version' in data, "Must have schema_version"
        assert 'layer' in data, "Must have layer field"
        assert data['layer'] == 2, "Layer must be 2"
        assert 'sections' in data, "Must have sections list"
        assert isinstance(data['sections'], list), "Sections must be list"
    
    def test_executive_summary_has_standard_sections(self):
        """Verify executive summary has 4 standard sections."""
        exec_file = Path("cortex-brain/response-templates/executive-summary.yaml")
        with open(exec_file, 'r') as f:
            data = yaml.safe_load(f)
        
        sections = data['sections']
        section_names = [s['name'] for s in sections]
        
        assert "Outcomes" in section_names, "Must have Outcomes section"
        assert "In Progress" in section_names, "Must have In Progress section"
        assert "Risks" in section_names, "Must have Risks section"
        assert "Impact" in section_names, "Must have Impact section"
    
    def test_executive_sections_have_markers(self):
        """Verify all sections have emoji markers."""
        exec_file = Path("cortex-brain/response-templates/executive-summary.yaml")
        with open(exec_file, 'r') as f:
            data = yaml.safe_load(f)
        
        sections = data['sections']
        for section in sections:
            assert 'marker' in section, f"Section {section['name']} must have marker"
            assert section['marker'] in ['✅', '⚙️', '⚠️', '🎯'], \
                f"Section {section['name']} marker must be valid emoji"


class TestLayer3OrchestratorTemplates:
    """Test AC-TEMPLATE-002: Layer 3 (orchestrator templates) structure."""
    
    def test_generic_orchestrator_yaml_exists(self):
        """Verify generic.yaml fallback exists."""
        generic_file = Path("cortex-brain/response-templates/orchestrators/generic.yaml")
        assert generic_file.exists(), "generic.yaml must exist as fallback"
    
    def test_generic_yaml_valid_syntax(self):
        """Verify generic.yaml has valid YAML syntax."""
        generic_file = Path("cortex-brain/response-templates/orchestrators/generic.yaml")
        with open(generic_file, 'r') as f:
            data = yaml.safe_load(f)
        
        assert data is not None, "YAML must parse successfully"
        assert isinstance(data, dict), "YAML root must be dictionary"
    
    def test_generic_yaml_has_required_fields(self):
        """Verify generic.yaml has required fields."""
        generic_file = Path("cortex-brain/response-templates/orchestrators/generic.yaml")
        with open(generic_file, 'r') as f:
            data = yaml.safe_load(f)
        
        assert 'schema_version' in data, "Must have schema_version"
        assert 'layer' in data, "Must have layer field"
        assert data['layer'] == 3, "Layer must be 3"
        assert 'orchestrator' in data, "Must specify orchestrator name"
        assert 'inherits' in data, "Must declare inheritance"
        assert 'templates' in data, "Must have templates dict"
    
    def test_generic_yaml_inherits_layer_1_and_2(self):
        """Verify generic.yaml inherits mandatory-header and executive-summary."""
        generic_file = Path("cortex-brain/response-templates/orchestrators/generic.yaml")
        with open(generic_file, 'r') as f:
            data = yaml.safe_load(f)
        
        inherits = data['inherits']
        assert 'mandatory-header.yaml' in inherits, "Must inherit Layer 1"
        assert 'executive-summary.yaml' in inherits, "Must inherit Layer 2"
    
    def test_generic_yaml_has_success_template(self):
        """Verify generic.yaml has at least one success template."""
        generic_file = Path("cortex-brain/response-templates/orchestrators/generic.yaml")
        with open(generic_file, 'r') as f:
            data = yaml.safe_load(f)
        
        templates = data['templates']
        assert len(templates) > 0, "Must have at least one template"
        
        # Check first template has content
        first_template = list(templates.values())[0]
        assert 'content' in first_template, "Template must have content"
