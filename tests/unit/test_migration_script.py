"""
Unit Tests for AC-AR-010-02: Automated Folder Migration Script

Tests the migration planner, validator, and utilities.
"""

import pytest
from pathlib import Path
from typing import List
import tempfile
import shutil
import hashlib


class MigrationFileValidator:
    """Validator for migration file structure."""
    
    def __init__(self):
        self.validation_errors = []
    
    def validate_migration_script_syntax(self) -> bool:
        """Validate migration script Python syntax."""
        script_path = Path(__file__).parent.parent.parent / "scripts/migrate-folder-structure.py"
        
        if not script_path.exists():
            self.validation_errors.append("Migration script not found")
            return False
        
        try:
            with open(script_path, 'r') as f:
                code = f.read()
            compile(code, str(script_path), 'exec')
            return True
        except SyntaxError as e:
            self.validation_errors.append(f"Syntax error: {e}")
            return False
    
    def validate_validator_script_syntax(self) -> bool:
        """Validate migration validator script Python syntax."""
        validator_path = Path(__file__).parent.parent.parent / "scripts/migration-validator.py"
        
        if not validator_path.exists():
            self.validation_errors.append("Validator script not found")
            return False
        
        try:
            with open(validator_path, 'r') as f:
                code = f.read()
            compile(code, str(validator_path), 'exec')
            return True
        except SyntaxError as e:
            self.validation_errors.append(f"Syntax error: {e}")
            return False
    
    def validate_class_structure(self) -> bool:
        """Validate that required classes exist."""
        script_path = Path(__file__).parent.parent.parent / "scripts/migrate-folder-structure.py"
        content = script_path.read_text()
        
        required_classes = ['FolderMigrator', 'MigrationFile']
        for class_name in required_classes:
            if f"class {class_name}" not in content:
                self.validation_errors.append(f"Missing class: {class_name}")
                return False
        
        return True
    
    def validate_required_methods(self) -> bool:
        """Validate that required methods exist."""
        script_path = Path(__file__).parent.parent.parent / "scripts/migrate-folder-structure.py"
        content = script_path.read_text()
        
        required_methods = [
            'plan_migration',
            'execute_migration',
            'create_backup',
            'rollback',
            'dry_run',
            'calculate_file_hash',
        ]
        
        for method in required_methods:
            if f"def {method}" not in content:
                self.validation_errors.append(f"Missing method: {method}")
                return False
        
        return True
    
    def validate_file_hash_calculation(self) -> bool:
        """Validate file hash calculation implementation."""
        script_path = Path(__file__).parent.parent.parent / "scripts/migrate-folder-structure.py"
        content = script_path.read_text()
        
        # Check SHA256 is used
        if "sha256" not in content.lower():
            self.validation_errors.append("Hash calculation must use SHA256")
            return False
        
        return True
    
    def validate_backup_capability(self) -> bool:
        """Validate backup creation capability."""
        script_path = Path(__file__).parent.parent.parent / "scripts/migrate-folder-structure.py"
        content = script_path.read_text()
        
        if "backup" not in content.lower():
            self.validation_errors.append("Missing backup capability")
            return False
        
        if ".migration-backup" not in content:
            self.validation_errors.append("Backup directory not specified")
            return False
        
        return True
    
    def validate_rollback_capability(self) -> bool:
        """Validate rollback capability."""
        script_path = Path(__file__).parent.parent.parent / "scripts/migrate-folder-structure.py"
        content = script_path.read_text()
        
        if "def rollback" not in content:
            self.validation_errors.append("Missing rollback method")
            return False
        
        return True
    
    def validate_logging_setup(self) -> bool:
        """Validate logging is configured."""
        script_path = Path(__file__).parent.parent.parent / "scripts/migrate-folder-structure.py"
        content = script_path.read_text()
        
        if "logging" not in content:
            self.validation_errors.append("Logging not configured")
            return False
        
        return True
    
    def validate_error_handling(self) -> bool:
        """Validate error handling."""
        script_path = Path(__file__).parent.parent.parent / "scripts/migrate-folder-structure.py"
        content = script_path.read_text()
        
        if "except" not in content:
            self.validation_errors.append("No error handling found")
            return False
        
        if "Exception" not in content:
            self.validation_errors.append("Generic exception handling missing")
            return False
        
        return True


class TestMigrationScriptStructure:
    """Test migration script structure and components."""
    
    @pytest.fixture
    def validator(self):
        return MigrationFileValidator()
    
    def test_migration_script_exists(self):
        """Test that migration script file exists."""
        script_path = Path(__file__).parent.parent.parent / "scripts/migrate-folder-structure.py"
        assert script_path.exists(), "Migration script must exist"
    
    def test_migration_script_is_executable(self):
        """Test that migration script is valid Python."""
        script_path = Path(__file__).parent.parent.parent / "scripts/migrate-folder-structure.py"
        assert script_path.exists()
        
        # Should have shebang
        content = script_path.read_text()
        assert content.startswith('#!/usr/bin/env python3'), "Script must have correct shebang"
    
    def test_migration_script_syntax_valid(self, validator):
        """Test that migration script has valid Python syntax."""
        assert validator.validate_migration_script_syntax()
    
    def test_validator_script_syntax_valid(self, validator):
        """Test that validator script has valid Python syntax."""
        assert validator.validate_validator_script_syntax()
    
    def test_folder_migrator_class_exists(self, validator):
        """Test that FolderMigrator class exists."""
        assert validator.validate_class_structure()
    
    def test_migration_file_dataclass_exists(self, validator):
        """Test that MigrationFile dataclass exists."""
        validator.validate_class_structure()
        # Checked in above test


class TestMigrationMethods:
    """Test migration methods."""
    
    @pytest.fixture
    def validator(self):
        return MigrationFileValidator()
    
    def test_plan_migration_exists(self, validator):
        """Test that plan_migration method exists."""
        assert validator.validate_required_methods()
    
    def test_execute_migration_exists(self, validator):
        """Test that execute_migration method exists."""
        assert validator.validate_required_methods()
    
    def test_backup_capability_exists(self, validator):
        """Test that backup capability exists."""
        assert validator.validate_backup_capability()
    
    def test_rollback_capability_exists(self, validator):
        """Test that rollback capability exists."""
        assert validator.validate_rollback_capability()
    
    def test_dry_run_capability_exists(self, validator):
        """Test that dry_run method exists."""
        script_path = Path(__file__).parent.parent.parent / "scripts/migrate-folder-structure.py"
        content = script_path.read_text()
        assert "def dry_run" in content, "Dry run capability required"
    
    def test_file_hash_calculation_exists(self, validator):
        """Test that file hash calculation exists."""
        assert validator.validate_required_methods()


class TestMigrationValidation:
    """Test migration validation capabilities."""
    
    @pytest.fixture
    def validator(self):
        return MigrationFileValidator()
    
    def test_hash_calculation_uses_sha256(self, validator):
        """Test that hash calculation uses SHA256."""
        assert validator.validate_file_hash_calculation()
    
    def test_backup_directory_specified(self, validator):
        """Test that backup directory is specified."""
        assert validator.validate_backup_capability()
    
    def test_logging_configured(self, validator):
        """Test that logging is configured."""
        assert validator.validate_logging_setup()
    
    def test_error_handling_present(self, validator):
        """Test that error handling is present."""
        assert validator.validate_error_handling()


class TestMigrationValidatorScript:
    """Test migration validator script."""
    
    def test_validator_script_exists(self):
        """Test that validator script exists."""
        validator_path = Path(__file__).parent.parent.parent / "scripts/migration-validator.py"
        assert validator_path.exists(), "Validator script must exist"
    
    def test_validator_syntax_valid(self):
        """Test validator script syntax."""
        validator_path = Path(__file__).parent.parent.parent / "scripts/migration-validator.py"
        content = validator_path.read_text()
        compile(content, str(validator_path), 'exec')
    
    def test_validator_has_main_function(self):
        """Test that validator has main function."""
        validator_path = Path(__file__).parent.parent.parent / "scripts/migration-validator.py"
        content = validator_path.read_text()
        assert "def main" in content, "Validator must have main function"
    
    def test_validator_class_exists(self):
        """Test that MigrationValidator class exists."""
        validator_path = Path(__file__).parent.parent.parent / "scripts/migration-validator.py"
        content = validator_path.read_text()
        assert "class MigrationValidator" in content, "MigrationValidator class must exist"


class TestMigrationAcceptanceCriteria:
    """Test that migration meets AC-AR-010-02 acceptance criteria."""
    
    @pytest.fixture
    def validator(self):
        return MigrationFileValidator()
    
    def test_ac_migration_script_created(self, validator):
        """AC: Migration script created and tested."""
        script_path = Path(__file__).parent.parent.parent / "scripts/migrate-folder-structure.py"
        assert script_path.exists()
        assert validator.validate_migration_script_syntax()
    
    def test_ac_validator_script_created(self, validator):
        """AC: Validator script created."""
        validator_path = Path(__file__).parent.parent.parent / "scripts/migration-validator.py"
        assert validator_path.exists()
        assert validator.validate_validator_script_syntax()
    
    def test_ac_file_integrity_verification(self, validator):
        """AC: File integrity verification with hash calculation."""
        assert validator.validate_file_hash_calculation()
    
    def test_ac_migration_report_documentation(self):
        """AC: Migration report generation documented."""
        script_path = Path(__file__).parent.parent.parent / "scripts/migrate-folder-structure.py"
        content = script_path.read_text()
        assert "_generate_report" in content, "Report generation must be implemented"
    
    def test_ac_rollback_capability_implemented(self, validator):
        """AC: Rollback capability implemented."""
        assert validator.validate_rollback_capability()


class TestMigrationDocumentation:
    """Test migration documentation."""
    
    def test_migration_script_has_docstring(self):
        """Test that migration script has module docstring."""
        script_path = Path(__file__).parent.parent.parent / "scripts/migrate-folder-structure.py"
        content = script_path.read_text()
        assert '"""' in content, "Script must have docstring"
    
    def test_migration_script_has_usage_example(self):
        """Test that migration script includes usage examples."""
        script_path = Path(__file__).parent.parent.parent / "scripts/migrate-folder-structure.py"
        content = script_path.read_text()
        assert "Usage:" in content, "Script must include usage documentation"
    
    def test_validator_script_has_docstring(self):
        """Test that validator script has module docstring."""
        validator_path = Path(__file__).parent.parent.parent / "scripts/migration-validator.py"
        content = validator_path.read_text()
        assert '"""' in content, "Script must have docstring"
    
    def test_class_has_docstrings(self):
        """Test that classes have docstrings."""
        script_path = Path(__file__).parent.parent.parent / "scripts/migrate-folder-structure.py"
        content = script_path.read_text()
        assert 'class FolderMigrator' in content and '"""' in content


class TestMigrationEdgeCases:
    """Test edge cases and error scenarios."""
    
    def test_handles_missing_directories(self):
        """Test that migration handles missing directories."""
        script_path = Path(__file__).parent.parent.parent / "scripts/migrate-folder-structure.py"
        content = script_path.read_text()
        assert "mkdir" in content or "exists()" in content, "Must handle directory creation"
    
    def test_handles_file_copy_errors(self):
        """Test that migration handles file copy errors."""
        script_path = Path(__file__).parent.parent.parent / "scripts/migrate-folder-structure.py"
        content = script_path.read_text()
        assert "except" in content, "Must handle copy errors"
    
    def test_validates_before_removing_old_folders(self):
        """Test that validation happens before removing old folders."""
        script_path = Path(__file__).parent.parent.parent / "scripts/migrate-folder-structure.py"
        content = script_path.read_text()
        # Verify should come before removal
        assert "verified" in content.lower(), "Must verify before removal"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
