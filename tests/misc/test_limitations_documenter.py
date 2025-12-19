"""
Tests for Limitations Documentation Template - Feature 7
Tests template structure, YAML parsing, auto-generation, and validation

Author: Asif Hussain
GitHub: github.com/asifhussain60/CORTEX
Version: 1.0.0
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile
import shutil
import yaml
from src.orchestrators.limitations_documenter import (
    LimitationsDocumenter,
    LimitationEntry,
    LimitationType,
    ValidationResult
)


class TestTemplateStructure:
    """Test YAML template structure and loading"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests"""
        temp = Path(tempfile.mkdtemp())
        yield temp
        shutil.rmtree(temp)
    
    def test_loads_yaml_template(self, temp_dir):
        """Should load YAML template from file"""
        template_file = temp_dir / "template.yaml"
        template_file.write_text("""
orchestrator_name: "TestOrchestrator"
version: "1.0.0"
limitations:
  - type: "blocker"
    title: "Missing SDK"
    description: "SDK not installed"
""")
        
        documenter = LimitationsDocumenter(template_path=template_file)
        template = documenter.load_template()
        
        assert template['orchestrator_name'] == "TestOrchestrator"
        assert template['version'] == "1.0.0"
        assert len(template['limitations']) == 1
    
    def test_validates_required_fields(self, temp_dir):
        """Should validate required template fields"""
        template_file = temp_dir / "invalid_template.yaml"
        template_file.write_text("""
orchestrator_name: "TestOrchestrator"
# Missing version and limitations
""")
        
        documenter = LimitationsDocumenter(template_path=template_file)
        validation = documenter.validate_template()
        
        assert validation.is_valid is False
        assert any("version" in error for error in validation.errors)
        assert any("limitations" in error for error in validation.errors)
    
    def test_creates_default_template_if_not_exists(self, temp_dir):
        """Should create default template if file doesn't exist"""
        template_file = temp_dir / "new_template.yaml"
        
        documenter = LimitationsDocumenter(template_path=template_file)
        documenter.create_default_template(orchestrator_name="NewOrchestrator")
        
        assert template_file.exists()
        with open(template_file, 'r') as f:
            data = yaml.safe_load(f)
        
        assert data['orchestrator_name'] == "NewOrchestrator"
        assert 'limitations' in data


class TestYAMLParsing:
    """Test YAML parsing and structure validation"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests"""
        temp = Path(tempfile.mkdtemp())
        yield temp
        shutil.rmtree(temp)
    
    def test_parses_limitation_types(self, temp_dir):
        """Should parse different limitation types"""
        template_file = temp_dir / "template.yaml"
        template_file.write_text("""
orchestrator_name: "TestOrchestrator"
version: "1.0.0"
limitations:
  - type: "blocker"
    title: "Blocker 1"
  - type: "constraint"
    title: "Constraint 1"
  - type: "workaround"
    title: "Workaround 1"
""")
        
        documenter = LimitationsDocumenter(template_path=template_file)
        limitations = documenter.parse_limitations()
        
        assert len(limitations) == 3
        assert limitations[0].type == LimitationType.BLOCKER
        assert limitations[1].type == LimitationType.CONSTRAINT
        assert limitations[2].type == LimitationType.WORKAROUND
    
    def test_validates_limitation_structure(self, temp_dir):
        """Should validate individual limitation structure"""
        limitation_data = {
            'type': 'blocker',
            'title': 'Missing SDK',
            'description': 'SDK not installed',
            'impact': 'high',
            'workaround': 'Install SDK manually'
        }
        
        documenter = LimitationsDocumenter()
        validation = documenter.validate_limitation(limitation_data)
        
        assert validation.is_valid is True
        assert len(validation.errors) == 0
    
    def test_detects_invalid_limitation_type(self, temp_dir):
        """Should detect invalid limitation type"""
        limitation_data = {
            'type': 'invalid_type',
            'title': 'Test'
        }
        
        documenter = LimitationsDocumenter()
        validation = documenter.validate_limitation(limitation_data)
        
        assert validation.is_valid is False
        assert any("type" in error for error in validation.errors)


class TestAutoGeneration:
    """Test auto-generation from phase metadata"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests"""
        temp = Path(tempfile.mkdtemp())
        yield temp
        shutil.rmtree(temp)
    
    def test_generates_from_phase_metadata(self, temp_dir):
        """Should generate limitations from phase metadata"""
        metadata = {
            'orchestrator_name': 'TDDEnvironmentGate',
            'version': '1.0.0',
            'blockers': [
                {
                    'title': 'Missing pytest',
                    'description': 'pytest not found in environment',
                    'impact': 'high'
                }
            ]
        }
        
        documenter = LimitationsDocumenter()
        template = documenter.generate_from_metadata(metadata)
        
        assert template['orchestrator_name'] == 'TDDEnvironmentGate'
        assert len(template['limitations']) == 1
        assert template['limitations'][0]['type'] == 'blocker'
    
    def test_formats_as_yaml_string(self, temp_dir):
        """Should format limitations as YAML string"""
        limitations = [
            LimitationEntry(
                type=LimitationType.BLOCKER,
                title="Missing SDK",
                description="SDK not installed",
                impact="high"
            )
        ]
        
        documenter = LimitationsDocumenter()
        yaml_string = documenter.format_as_yaml(
            orchestrator_name="TestOrchestrator",
            version="1.0.0",
            limitations=limitations
        )
        
        assert "orchestrator_name: TestOrchestrator" in yaml_string
        assert "type: blocker" in yaml_string
        assert "Missing SDK" in yaml_string
    
    def test_saves_generated_template(self, temp_dir):
        """Should save generated template to file"""
        output_file = temp_dir / "generated.yaml"
        metadata = {
            'orchestrator_name': 'TestOrchestrator',
            'version': '1.0.0',
            'blockers': [{'title': 'Test blocker'}]
        }
        
        documenter = LimitationsDocumenter()
        documenter.generate_and_save(metadata, output_file)
        
        assert output_file.exists()
        with open(output_file, 'r') as f:
            data = yaml.safe_load(f)
        
        assert data['orchestrator_name'] == 'TestOrchestrator'


class TestValidation:
    """Test template validation rules"""
    
    def test_validates_complete_template(self):
        """Should validate complete template with all fields"""
        template = {
            'orchestrator_name': 'TestOrchestrator',
            'version': '1.0.0',
            'limitations': [
                {
                    'type': 'blocker',
                    'title': 'Test',
                    'description': 'Test description',
                    'impact': 'high',
                    'workaround': 'Install SDK'
                }
            ]
        }
        
        documenter = LimitationsDocumenter()
        validation = documenter.validate_template_dict(template)
        
        assert validation.is_valid is True
    
    def test_detects_missing_orchestrator_name(self):
        """Should detect missing orchestrator_name"""
        template = {
            'version': '1.0.0',
            'limitations': []
        }
        
        documenter = LimitationsDocumenter()
        validation = documenter.validate_template_dict(template)
        
        assert validation.is_valid is False
        assert any('orchestrator_name' in error for error in validation.errors)
    
    def test_validates_limitation_impact_values(self):
        """Should validate impact field values"""
        limitation = {
            'type': 'blocker',
            'title': 'Test',
            'impact': 'invalid_impact'
        }
        
        documenter = LimitationsDocumenter()
        validation = documenter.validate_limitation(limitation)
        
        assert validation.is_valid is False
        assert any('impact' in error for error in validation.errors)


class TestOrchestratorIntegration:
    """Test integration with orchestrators"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests"""
        temp = Path(tempfile.mkdtemp())
        yield temp
        shutil.rmtree(temp)
    
    def test_documents_tdd_environment_gate_limitations(self, temp_dir):
        """Should document TDD Environment Gate limitations"""
        documenter = LimitationsDocumenter()
        
        # Simulate TDD Environment Gate reporting limitations
        gate_metadata = {
            'orchestrator_name': 'TDDEnvironmentGate',
            'version': '1.0.0',
            'blockers': [
                {
                    'title': 'Framework not detected',
                    'description': 'pytest/dotnet/jest not found',
                    'impact': 'high',
                    'workaround': 'Install test framework: pip install pytest'
                }
            ]
        }
        
        output_file = temp_dir / "tdd-gate-limitations.yaml"
        documenter.generate_and_save(gate_metadata, output_file)
        
        assert output_file.exists()
        with open(output_file, 'r') as f:
            data = yaml.safe_load(f)
        
        assert data['orchestrator_name'] == 'TDDEnvironmentGate'
        assert len(data['limitations']) >= 1
    
    def test_documents_environment_diagnostics_limitations(self, temp_dir):
        """Should document Environment Diagnostics limitations"""
        documenter = LimitationsDocumenter()
        
        diag_metadata = {
            'orchestrator_name': 'EnvironmentDiagnosticsOrchestrator',
            'version': '1.0.0',
            'constraints': [
                {
                    'title': 'Platform-specific commands',
                    'description': 'Some commands Windows-only',
                    'impact': 'medium',
                    'workaround': 'Use platform detection'
                }
            ]
        }
        
        output_file = temp_dir / "env-diag-limitations.yaml"
        documenter.generate_and_save(diag_metadata, output_file)
        
        assert output_file.exists()
    
    def test_provides_hook_for_orchestrators(self):
        """Should provide hook method for orchestrators"""
        documenter = LimitationsDocumenter()
        
        # Orchestrator calls hook to document limitations
        result = documenter.document_orchestrator_limitations(
            orchestrator_name="TestOrchestrator",
            limitations=[
                {'type': 'blocker', 'title': 'Test blocker'}
            ]
        )
        
        assert result['success'] is True
        assert 'file_path' in result


class TestPerformanceRequirements:
    """Test performance benchmarks"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests"""
        temp = Path(tempfile.mkdtemp())
        yield temp
        shutil.rmtree(temp)
    
    def test_template_generation_under_100ms(self, temp_dir):
        """Should generate template in under 100ms"""
        import time
        
        metadata = {
            'orchestrator_name': 'TestOrchestrator',
            'version': '1.0.0',
            'blockers': [{'title': f'Blocker {i}'} for i in range(10)]
        }
        
        documenter = LimitationsDocumenter()
        
        start = time.time()
        documenter.generate_from_metadata(metadata)
        duration = time.time() - start
        
        assert duration < 0.1  # 100ms
    
    def test_validation_under_50ms(self, temp_dir):
        """Should validate template in under 50ms"""
        import time
        
        template = {
            'orchestrator_name': 'TestOrchestrator',
            'version': '1.0.0',
            'limitations': [
                {'type': 'blocker', 'title': f'Test {i}'}
                for i in range(20)
            ]
        }
        
        documenter = LimitationsDocumenter()
        
        start = time.time()
        documenter.validate_template_dict(template)
        duration = time.time() - start
        
        assert duration < 0.05  # 50ms
