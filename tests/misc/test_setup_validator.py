"""
Tests for setup validation framework
Validates CORTEX installation integrity: directories, configs, databases, dependencies

TDD Phase: RED - Tests written first, expected to fail
"""

import pytest
from pathlib import Path
import json
import tempfile
import shutil
from unittest.mock import patch, MagicMock

from src.validators.setup_validator import (
    SetupValidator,
    ValidationResult,
    ValidationIssue,
    IssueSeverity
)


class TestSetupValidator:
    """Test setup validation framework"""
    
    @pytest.fixture
    def temp_cortex_dir(self):
        """Create temporary CORTEX directory structure"""
        temp_dir = tempfile.mkdtemp()
        cortex_dir = Path(temp_dir) / "CORTEX"
        cortex_dir.mkdir()
        
        # Create brain directory
        brain_dir = cortex_dir / "cortex-brain"
        brain_dir.mkdir()
        
        yield cortex_dir
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def valid_config(self):
        """Valid cortex.config.json structure"""
        return {
            "machines": {
                "test-machine": {
                    "rootPath": "/path/to/CORTEX",
                    "brainPath": "/path/to/CORTEX/cortex-brain"
                }
            },
            "version": "3.2.0"
        }
    
    def test_validator_initialization(self, temp_cortex_dir):
        """Test SetupValidator can be initialized"""
        validator = SetupValidator(root_path=temp_cortex_dir)
        
        assert validator is not None
        assert validator.root_path == temp_cortex_dir
    
    def test_validate_brain_directories_all_present(self, temp_cortex_dir):
        """Test validation passes when all brain directories exist"""
        brain_dir = temp_cortex_dir / "cortex-brain"
        
        # Create all required directories
        (brain_dir / "tier0").mkdir()
        (brain_dir / "tier1").mkdir()
        (brain_dir / "tier2").mkdir()
        (brain_dir / "tier3").mkdir()
        (brain_dir / "documents").mkdir()
        (brain_dir / "admin").mkdir()
        (brain_dir / "agents").mkdir()
        
        validator = SetupValidator(root_path=temp_cortex_dir)
        result = validator.validate_brain_directories()
        
        assert result.is_valid is True
        assert len(result.issues) == 0
    
    def test_validate_brain_directories_missing_tier(self, temp_cortex_dir):
        """Test validation detects missing tier directories"""
        brain_dir = temp_cortex_dir / "cortex-brain"
        
        # Create only some tier directories
        (brain_dir / "tier0").mkdir()
        (brain_dir / "tier1").mkdir()
        # Missing tier2, tier3
        
        validator = SetupValidator(root_path=temp_cortex_dir)
        result = validator.validate_brain_directories()
        
        assert result.is_valid is False
        assert len(result.issues) >= 2
        
        # Check for tier2 and tier3 issues
        missing_dirs = [issue.description for issue in result.issues]
        assert any("tier2" in desc for desc in missing_dirs)
        assert any("tier3" in desc for desc in missing_dirs)
    
    def test_validate_config_file_valid(self, temp_cortex_dir, valid_config):
        """Test validation passes for valid config file"""
        config_path = temp_cortex_dir / "cortex.config.json"
        config_path.write_text(json.dumps(valid_config, indent=2))
        
        validator = SetupValidator(root_path=temp_cortex_dir)
        result = validator.validate_config_file()
        
        assert result.is_valid is True
        assert len(result.issues) == 0
    
    def test_validate_config_file_missing(self, temp_cortex_dir):
        """Test validation detects missing config file"""
        validator = SetupValidator(root_path=temp_cortex_dir)
        result = validator.validate_config_file()
        
        assert result.is_valid is False
        assert len(result.issues) == 1
        assert "cortex.config.json" in result.issues[0].description
        assert result.issues[0].severity == IssueSeverity.CRITICAL
    
    def test_validate_config_file_malformed_json(self, temp_cortex_dir):
        """Test validation detects malformed JSON"""
        config_path = temp_cortex_dir / "cortex.config.json"
        config_path.write_text("{ invalid json }")
        
        validator = SetupValidator(root_path=temp_cortex_dir)
        result = validator.validate_config_file()
        
        assert result.is_valid is False
        assert any("JSON" in issue.description for issue in result.issues)
    
    def test_validate_config_file_missing_machines(self, temp_cortex_dir):
        """Test validation detects missing machines key"""
        config_path = temp_cortex_dir / "cortex.config.json"
        config_path.write_text(json.dumps({"version": "3.2.0"}))
        
        validator = SetupValidator(root_path=temp_cortex_dir)
        result = validator.validate_config_file()
        
        assert result.is_valid is False
        assert any("machines" in issue.description.lower() for issue in result.issues)
    
    def test_validate_database_schemas_tier1(self, temp_cortex_dir):
        """Test validation checks tier1 working memory database"""
        brain_dir = temp_cortex_dir / "cortex-brain"
        tier1_dir = brain_dir / "tier1"
        tier1_dir.mkdir(parents=True)
        
        # Create empty database file
        db_path = tier1_dir / "working_memory.db"
        db_path.touch()
        
        validator = SetupValidator(root_path=temp_cortex_dir)
        result = validator.validate_database_schemas()
        
        # Should detect database exists but may need schema validation
        assert result is not None
    
    def test_validate_database_schemas_missing(self, temp_cortex_dir):
        """Test validation detects missing databases"""
        brain_dir = temp_cortex_dir / "cortex-brain"
        tier1_dir = brain_dir / "tier1"
        tier1_dir.mkdir(parents=True)
        
        validator = SetupValidator(root_path=temp_cortex_dir)
        result = validator.validate_database_schemas()
        
        assert result.is_valid is False
        assert any("database" in issue.description.lower() for issue in result.issues)
    
    def test_validate_python_dependencies(self, temp_cortex_dir):
        """Test validation checks Python dependencies"""
        validator = SetupValidator(root_path=temp_cortex_dir)
        
        with patch('importlib.import_module') as mock_import:
            # Simulate all dependencies available
            mock_import.return_value = MagicMock()
            
            result = validator.validate_python_dependencies()
            
            assert result is not None
    
    def test_validate_python_dependencies_missing(self, temp_cortex_dir):
        """Test validation detects missing Python packages"""
        validator = SetupValidator(root_path=temp_cortex_dir)
        
        with patch('importlib.import_module') as mock_import:
            # Simulate missing dependency
            mock_import.side_effect = ImportError("Module not found")
            
            result = validator.validate_python_dependencies()
            
            assert result.is_valid is False
    
    def test_validate_all_comprehensive(self, temp_cortex_dir, valid_config):
        """Test comprehensive validation runs all checks"""
        # Setup valid environment
        brain_dir = temp_cortex_dir / "cortex-brain"
        for tier in ["tier0", "tier1", "tier2", "tier3", "documents"]:
            (brain_dir / tier).mkdir(parents=True)
        
        config_path = temp_cortex_dir / "cortex.config.json"
        config_path.write_text(json.dumps(valid_config, indent=2))
        
        validator = SetupValidator(root_path=temp_cortex_dir)
        result = validator.validate_all()
        
        assert result is not None
        assert hasattr(result, 'is_valid')
        assert hasattr(result, 'issues')
    
    def test_validation_result_severity_levels(self):
        """Test ValidationResult handles different severity levels"""
        issues = [
            ValidationIssue(
                severity=IssueSeverity.CRITICAL,
                category="config",
                description="Critical issue",
                fix_suggestion="Fix this now"
            ),
            ValidationIssue(
                severity=IssueSeverity.WARNING,
                category="performance",
                description="Warning issue",
                fix_suggestion="Consider fixing"
            ),
            ValidationIssue(
                severity=IssueSeverity.INFO,
                category="info",
                description="Info issue",
                fix_suggestion="Optional"
            )
        ]
        
        result = ValidationResult(is_valid=False, issues=issues)
        
        # Should be invalid due to CRITICAL issue
        assert result.is_valid is False
        assert len(result.issues) == 3
        
        # Check severity filtering
        critical_issues = [i for i in result.issues if i.severity == IssueSeverity.CRITICAL]
        assert len(critical_issues) == 1
    
    def test_validation_issue_creation(self):
        """Test ValidationIssue can be created with all fields"""
        issue = ValidationIssue(
            severity=IssueSeverity.ERROR,
            category="database",
            description="Database schema mismatch",
            fix_suggestion="Run schema migration",
            affected_path="/path/to/database"
        )
        
        assert issue.severity == IssueSeverity.ERROR
        assert issue.category == "database"
        assert "schema" in issue.description
        assert issue.fix_suggestion is not None
        assert issue.affected_path is not None
    
    def test_validator_reports_formatted_output(self, temp_cortex_dir):
        """Test validator can generate formatted report"""
        validator = SetupValidator(root_path=temp_cortex_dir)
        result = validator.validate_all()
        
        # Should be able to generate report
        report = validator.generate_report(result)
        
        assert report is not None
        assert isinstance(report, str)
        assert len(report) > 0
    
    def test_validate_brain_protection_rules_file(self, temp_cortex_dir):
        """Test validation checks brain-protection-rules.yaml exists"""
        brain_dir = temp_cortex_dir / "cortex-brain"
        brain_dir.mkdir(exist_ok=True)
        
        validator = SetupValidator(root_path=temp_cortex_dir)
        result = validator.validate_brain_files()
        
        # Should detect missing brain-protection-rules.yaml
        assert result.is_valid is False
        assert any("brain-protection-rules" in issue.description.lower() 
                  for issue in result.issues)
    
    def test_validate_response_templates_file(self, temp_cortex_dir):
        """Test validation checks response-templates.yaml exists"""
        brain_dir = temp_cortex_dir / "cortex-brain"
        brain_dir.mkdir(exist_ok=True)
        
        validator = SetupValidator(root_path=temp_cortex_dir)
        result = validator.validate_brain_files()
        
        # Should detect missing response-templates.yaml
        assert result.is_valid is False
        assert any("response-templates" in issue.description.lower() 
                  for issue in result.issues)
