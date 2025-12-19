"""
Unit tests for Feature Auto-Registrar

Tests the FeatureAutoRegistrar class for CORTEX Align v2.0.

Author: Asif Hussain
Date: December 3, 2025
"""

import pytest
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from datetime import datetime
from src.operations.modules.realignment.feature_auto_registrar import (
    FeatureAutoRegistrar,
    OperationMetadata,
    RegistrationResult
)


@pytest.fixture
def mock_project_structure(tmp_path):
    """Create mock CORTEX project structure with sample operations."""
    # Create directory structure
    operations_dir = tmp_path / "src" / "operations"
    operations_dir.mkdir(parents=True)
    
    modules_dir = operations_dir / "modules"
    modules_dir.mkdir()
    
    # Create sample operation file with docstring
    planning_content = '''"""
Planning Operation

Complete feature planning workflow with DoR/DoD validation.

Commands:
- plan feature X
- create plan
- validate plan

Examples:
- Plan authentication feature
- Create ADO work item
"""

def execute_planning():
    """Execute planning workflow."""
    pass
'''
    
    (operations_dir / "planning.py").write_text(planning_content)
    
    # Create operation without docstring
    (operations_dir / "test_op.py").write_text("def test(): pass")
    
    # Create admin operation
    (operations_dir / "deploy.py").write_text('"""Deploy utility."""\ndef deploy(): pass')
    
    # Create module directories
    planning_module = modules_dir / "planning"
    planning_module.mkdir()
    (planning_module / "planning_utility.py").touch()
    
    # Create cortex-operations.yaml
    operations_yaml = tmp_path / "cortex-operations.yaml"
    yaml_content = {
        'operations': {
            'existing_op': {
                'name': 'Existing Operation',
                'modules': ['existing_utility']
            }
        },
        'statistics': {
            'total_operations': 1,
            'total_modules': 1
        },
        'changelog': []
    }
    
    with open(operations_yaml, 'w') as f:
        yaml.dump(yaml_content, f)
    
    return tmp_path


@pytest.fixture
def registrar(mock_project_structure):
    """Create registrar instance with mock project structure."""
    return FeatureAutoRegistrar(project_root=mock_project_structure)


class TestFeatureAutoRegistrar:
    """Test suite for FeatureAutoRegistrar."""
    
    def test_init_with_project_root(self, mock_project_structure):
        """Test initialization with explicit project root."""
        registrar = FeatureAutoRegistrar(project_root=mock_project_structure)
        
        assert registrar.project_root == mock_project_structure
        assert registrar.operations_dir == mock_project_structure / "src" / "operations"
        assert registrar.modules_dir == mock_project_structure / "src" / "operations" / "modules"
    
    def test_extract_module_docstring_success(self, registrar):
        """Test extracting module docstring from valid Python."""
        content = '"""This is a docstring"""\ndef func(): pass'
        
        docstring = registrar.extract_module_docstring(content)
        
        assert docstring == "This is a docstring"
    
    def test_extract_module_docstring_no_docstring(self, registrar):
        """Test extracting docstring when none exists."""
        content = 'def func(): pass'
        
        docstring = registrar.extract_module_docstring(content)
        
        assert docstring == ""
    
    def test_extract_module_docstring_invalid_syntax(self, registrar):
        """Test docstring extraction with invalid syntax."""
        content = 'def func(: invalid syntax'
        
        docstring = registrar.extract_module_docstring(content)
        
        assert docstring == ""  # Should handle gracefully
    
    def test_extract_natural_language_triggers_from_quotes(self, registrar):
        """Test extracting triggers from quoted strings."""
        content = '''
def execute():
    cmd = "plan feature"
    cmd2 = "start workflow"
'''
        
        triggers = registrar.extract_natural_language_triggers(content, "")
        
        assert "plan feature" in triggers
        assert "start workflow" in triggers
    
    def test_extract_natural_language_triggers_from_docstring(self, registrar):
        """Test extracting triggers from docstring."""
        docstring = '''
Operation documentation.

Commands:
- plan feature
- create plan
- validate plan
'''
        
        triggers = registrar.extract_natural_language_triggers("", docstring)
        
        assert "plan feature" in triggers or "create plan" in triggers
    
    def test_extract_natural_language_triggers_limit(self, registrar):
        """Test that triggers are limited to top 5."""
        content = '''
"plan a" "plan b" "plan c" "plan d" "plan e" "plan f" "plan g"
'''
        
        triggers = registrar.extract_natural_language_triggers(content, "")
        
        assert len(triggers) <= 5
    
    def test_infer_deployment_tier_admin(self, registrar):
        """Test tier inference for admin operations."""
        file_path = Path("/src/operations/deploy.py")
        content = "Deploy to production"
        
        tier = registrar.infer_deployment_tier(file_path, content)
        
        assert tier == "admin_only"
    
    def test_infer_deployment_tier_dual_context(self, registrar):
        """Test tier inference for dual-context operations."""
        file_path = Path("/src/operations/ado.py")
        content = "Azure DevOps integration"
        
        tier = registrar.infer_deployment_tier(file_path, content)
        
        assert tier == "dual_context"
    
    def test_infer_deployment_tier_user_facing(self, registrar):
        """Test tier inference for user-facing operations."""
        file_path = Path("/src/operations/planning.py")
        content = "Feature planning workflow"
        
        tier = registrar.infer_deployment_tier(file_path, content)
        
        assert tier == "user_facing"
    
    def test_infer_category_planning(self, registrar):
        """Test category inference for planning operations."""
        file_path = Path("/src/operations/planning.py")
        
        category = registrar.infer_category(file_path)
        
        assert category == "planning"
    
    def test_infer_category_git(self, registrar):
        """Test category inference for git operations."""
        file_path = Path("/src/operations/commit.py")
        
        category = registrar.infer_category(file_path)
        
        assert category == "git"
    
    def test_infer_category_default(self, registrar):
        """Test category inference returns default for unknown."""
        file_path = Path("/src/operations/unknown_op.py")
        
        category = registrar.infer_category(file_path)
        
        assert category == "general"
    
    def test_extract_usage_examples(self, registrar):
        """Test extracting usage examples from docstring."""
        docstring = '''
Operation description.

Examples:
- Example 1: Plan a feature
- Example 2: Create work item
'''
        
        examples = registrar.extract_usage_examples(docstring)
        
        assert len(examples) >= 1
        assert any("plan" in ex.lower() for ex in examples)
    
    def test_extract_usage_examples_no_examples(self, registrar):
        """Test example extraction when none exist."""
        docstring = "Just a description"
        
        examples = registrar.extract_usage_examples(docstring)
        
        assert examples == []
    
    def test_find_related_modules_exact_match(self, registrar):
        """Test finding modules with exact name match."""
        modules = registrar.find_related_modules("planning")
        
        assert "planning_utility" in modules
    
    def test_find_related_modules_no_match(self, registrar):
        """Test finding modules when no match exists."""
        modules = registrar.find_related_modules("nonexistent")
        
        # Should return default utility name
        assert "nonexistent_utility" in modules
    
    def test_analyze_operation_file(self, registrar):
        """Test analyzing a complete operation file."""
        file_path = registrar.operations_dir / "planning.py"
        
        metadata = registrar.analyze_operation_file(file_path)
        
        assert metadata.name == "planning"
        assert metadata.display_name == "Planning"
        assert "Planning Operation" in metadata.description
        assert len(metadata.natural_language) > 0
        assert metadata.category == "planning"
        assert len(metadata.modules) > 0
    
    def test_analyze_operation_file_minimal(self, registrar):
        """Test analyzing file with minimal content."""
        file_path = registrar.operations_dir / "test_op.py"
        
        metadata = registrar.analyze_operation_file(file_path)
        
        assert metadata.name == "test_op"
        assert metadata.display_name == "Test Op"
        assert metadata.description == "Description needed"
    
    def test_format_triggers(self, registrar):
        """Test YAML formatting of triggers."""
        triggers = ["plan feature", "create plan"]
        
        formatted = registrar.format_triggers(triggers)
        
        assert '- "plan feature"' in formatted
        assert '- "create plan"' in formatted
    
    def test_format_triggers_empty(self, registrar):
        """Test YAML formatting with no triggers."""
        formatted = registrar.format_triggers([])
        
        assert '- "operation name"' in formatted
    
    def test_format_examples(self, registrar):
        """Test YAML formatting of examples."""
        examples = ["Example 1", "Example 2"]
        
        formatted = registrar.format_examples(examples)
        
        assert '- "Example 1"' in formatted
        assert '- "Example 2"' in formatted
    
    def test_generate_yaml_entry(self, registrar):
        """Test generating complete YAML entry."""
        metadata = OperationMetadata(
            name="test_op",
            display_name="Test Operation",
            description="Test description",
            deployment_tier="user_facing",
            natural_language=["test command"],
            category="testing",
            modules=["test_utility"],
            examples=["Test example"]
        )
        
        yaml_entry = registrar.generate_yaml_entry(metadata)
        
        assert "test_op:" in yaml_entry
        assert "Test Operation" in yaml_entry
        assert "test_utility" in yaml_entry
        assert "user_facing" in yaml_entry
        assert "test command" in yaml_entry
    
    def test_generate_yaml_entry_includes_metadata(self, registrar):
        """Test YAML entry includes all required metadata."""
        metadata = OperationMetadata(
            name="sample",
            display_name="Sample",
            description="Sample op",
            deployment_tier="admin_only",
            modules=["sample_utility"]
        )
        
        yaml_entry = registrar.generate_yaml_entry(metadata)
        
        assert "deployment_tier: admin_only" in yaml_entry
        assert "implementation_status:" in yaml_entry
        assert "status: ready" in yaml_entry
        assert "completion_percentage: 100" in yaml_entry
    
    def test_register_feature_dry_run(self, registrar):
        """Test registration in dry-run mode."""
        result = registrar.register_feature("planning", dry_run=True)
        
        assert result.success is True
        assert result.dry_run is True
        assert result.operation_name == "planning"
        assert len(result.yaml_entry) > 0
        assert "planning:" in result.yaml_entry
    
    def test_register_feature_file_not_found(self, registrar):
        """Test registration when operation file doesn't exist."""
        result = registrar.register_feature("nonexistent", dry_run=True)
        
        assert result.success is False
        assert "not found" in result.error_message.lower()
    
    def test_batch_register_multiple_operations(self, registrar):
        """Test batch registration of multiple operations."""
        operations = ["planning", "test_op"]
        
        results = registrar.batch_register(operations, dry_run=True)
        
        assert len(results) == 2
        assert results["planning"].success is True
        assert results["test_op"].success is True
    
    def test_batch_register_includes_failures(self, registrar):
        """Test batch registration handles failures gracefully."""
        operations = ["planning", "nonexistent"]
        
        results = registrar.batch_register(operations, dry_run=True)
        
        assert len(results) == 2
        assert results["planning"].success is True
        assert results["nonexistent"].success is False


class TestOperationMetadataDataclass:
    """Test OperationMetadata dataclass."""
    
    def test_metadata_creation(self):
        """Test OperationMetadata instantiation."""
        metadata = OperationMetadata(
            name="test",
            display_name="Test",
            description="Test operation",
            deployment_tier="user_facing"
        )
        
        assert metadata.name == "test"
        assert metadata.display_name == "Test"
        assert metadata.deployment_tier == "user_facing"
    
    def test_metadata_default_values(self):
        """Test OperationMetadata default field values."""
        metadata = OperationMetadata(
            name="test",
            display_name="Test",
            description="Test",
            deployment_tier="user_facing"
        )
        
        assert metadata.natural_language == []
        assert metadata.category == "general"
        assert metadata.modules == []
        assert metadata.examples == []
        assert metadata.version == "1.0.0"


class TestRegistrationResultDataclass:
    """Test RegistrationResult dataclass."""
    
    def test_result_creation_success(self):
        """Test RegistrationResult for successful registration."""
        result = RegistrationResult(
            success=True,
            operation_name="test_op",
            yaml_entry="test: yaml"
        )
        
        assert result.success is True
        assert result.operation_name == "test_op"
        assert result.yaml_entry == "test: yaml"
    
    def test_result_creation_failure(self):
        """Test RegistrationResult for failed registration."""
        result = RegistrationResult(
            success=False,
            operation_name="test_op",
            error_message="Test error"
        )
        
        assert result.success is False
        assert result.error_message == "Test error"
    
    def test_result_dry_run_flag(self):
        """Test RegistrationResult dry_run flag."""
        result = RegistrationResult(
            success=True,
            operation_name="test",
            dry_run=True
        )
        
        assert result.dry_run is True


class TestStandaloneExecution:
    """Test standalone CLI execution."""
    
    @patch('src.operations.modules.realignment.feature_auto_registrar.FeatureAutoRegistrar')
    def test_main_success_dry_run(self, mock_registrar_class, capsys):
        """Test main function with successful dry-run."""
        mock_registrar = Mock()
        mock_registrar_class.return_value = mock_registrar
        
        mock_result = RegistrationResult(
            success=True,
            operation_name="test_op",
            yaml_entry="test: yaml",
            dry_run=True
        )
        mock_registrar.register_feature.return_value = mock_result
        
        from src.operations.modules.realignment.feature_auto_registrar import main
        
        with patch('sys.argv', ['script', 'test_op', '--dry-run']):
            # Main doesn't raise SystemExit on success, just returns normally
            main()
            
            captured = capsys.readouterr()
            assert "✅ DRY RUN" in captured.out
            assert "test_op" in captured.out
    
    @patch('src.operations.modules.realignment.feature_auto_registrar.FeatureAutoRegistrar')
    def test_main_failure(self, mock_registrar_class):
        """Test main function with failed registration."""
        mock_registrar = Mock()
        mock_registrar_class.return_value = mock_registrar
        
        mock_result = RegistrationResult(
            success=False,
            operation_name="test_op",
            error_message="Test error"
        )
        mock_registrar.register_feature.return_value = mock_result
        
        from src.operations.modules.realignment.feature_auto_registrar import main
        
        with patch('sys.argv', ['script', 'test_op']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            assert exc_info.value.code == 1
    
    def test_main_missing_arguments(self):
        """Test main function with missing arguments."""
        from src.operations.modules.realignment.feature_auto_registrar import main
        
        with patch('sys.argv', ['script']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            assert exc_info.value.code == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
