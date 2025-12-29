"""
Tests for WorkspaceOperationValidator

Tests workspace-aware operation validation.

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from src.tier0.workspace_operation_validator import (
    WorkspaceOperationValidator,
    OperationType,
    ValidationResult,
    get_workspace_validator
)
from src.core.workspace_detector import WorkspaceInfo, WorkspaceDetectionMethod
from src.core.ide_detector import IDEType


@pytest.fixture
def temp_cortex_root(tmp_path):
    """Create temporary CORTEX root structure."""
    cortex_root = tmp_path / "CORTEX"
    cortex_root.mkdir()
    
    # Create cortex-brain
    (cortex_root / "cortex-brain").mkdir()
    
    # Create core directories
    src = cortex_root / "src"
    src.mkdir()
    (src / "tier0").mkdir()
    (src / "tier1").mkdir()
    (src / "tier2").mkdir()
    (src / "tier3").mkdir()
    (src / "cortex_agents").mkdir()
    (src / "orchestrators").mkdir()
    
    (cortex_root / "cortex-brain" / "tier0").mkdir(parents=True)
    
    return cortex_root


@pytest.fixture
def temp_user_workspace(tmp_path):
    """Create temporary user workspace."""
    workspace = tmp_path / "UserApp"
    workspace.mkdir()
    
    src = workspace / "src"
    src.mkdir()
    
    tests = workspace / "tests"
    tests.mkdir()
    
    return workspace


@pytest.fixture
def mock_workspace_info(temp_user_workspace):
    """Create mock WorkspaceInfo for user workspace."""
    return WorkspaceInfo(
        workspace_id="test-workspace-uuid",
        path=temp_user_workspace,
        name="UserApp",
        project_type="python",
        ide_type=IDEType.VSCODE,
        detection_method=WorkspaceDetectionMethod.CWD_SEARCH
    )


@pytest.fixture
def validator(temp_cortex_root, mock_workspace_info):
    """Create WorkspaceOperationValidator with mocked workspace."""
    with patch('src.tier0.workspace_operation_validator.detect_active_workspace', return_value=mock_workspace_info):
        return WorkspaceOperationValidator(cortex_root=temp_cortex_root)


class TestValidatorInitialization:
    """Test WorkspaceOperationValidator initialization."""
    
    def test_initialization(self, validator, temp_cortex_root):
        """Test validator initializes with correct paths."""
        assert validator.cortex_root == temp_cortex_root
        assert validator.active_workspace is not None
        assert len(validator.cortex_core_paths) > 0
    
    def test_cortex_core_paths_protected(self, validator, temp_cortex_root):
        """Test CORTEX core paths are registered as protected."""
        expected_paths = [
            temp_cortex_root / "src" / "tier0",
            temp_cortex_root / "src" / "tier1",
            temp_cortex_root / "src" / "tier2",
            temp_cortex_root / "src" / "tier3",
        ]
        
        for expected in expected_paths:
            assert expected in validator.cortex_core_paths


class TestReadOperations:
    """Test READ operation validation."""
    
    def test_read_from_active_workspace_allowed(self, validator, temp_user_workspace):
        """Test reading from active workspace is allowed."""
        target = temp_user_workspace / "src" / "feature.py"
        
        result = validator.validate(target, OperationType.READ)
        
        assert result == ValidationResult.ALLOWED
    
    def test_read_from_cortex_allowed(self, validator, temp_cortex_root):
        """Test reading from CORTEX is allowed."""
        target = temp_cortex_root / "src" / "tier0" / "some_file.py"
        
        result = validator.validate(target, OperationType.READ)
        
        assert result == ValidationResult.ALLOWED
    
    def test_read_from_any_path_allowed(self, validator, tmp_path):
        """Test reading from any path is allowed."""
        target = tmp_path / "random" / "file.txt"
        
        result = validator.validate(target, OperationType.READ)
        
        assert result == ValidationResult.ALLOWED


class TestWriteOperations:
    """Test WRITE operation validation."""
    
    def test_write_to_active_workspace_allowed(self, validator, temp_user_workspace):
        """Test writing to active workspace is allowed."""
        target = temp_user_workspace / "src" / "new_feature.py"
        
        result = validator.validate(target, OperationType.WRITE)
        
        assert result == ValidationResult.ALLOWED
    
    def test_write_to_cortex_non_core_allowed(self, validator, temp_cortex_root):
        """Test writing to CORTEX non-core paths is allowed."""
        target = temp_cortex_root / "temp" / "output.txt"
        
        result = validator.validate(target, OperationType.WRITE)
        
        assert result == ValidationResult.ALLOWED
    
    def test_write_to_cortex_core_denied(self, validator, temp_cortex_root):
        """Test writing to CORTEX core paths is denied."""
        target = temp_cortex_root / "src" / "tier0" / "protected.py"
        
        result = validator.validate(target, OperationType.WRITE)
        
        assert result == ValidationResult.DENIED
    
    def test_write_to_inactive_workspace_warning(self, validator, tmp_path):
        """Test writing to non-active workspace returns warning."""
        other_workspace = tmp_path / "OtherApp"
        other_workspace.mkdir()
        target = other_workspace / "src" / "file.py"
        
        result = validator.validate(target, OperationType.WRITE)
        
        assert result == ValidationResult.WARNING


class TestCreateOperations:
    """Test CREATE operation validation."""
    
    def test_create_in_active_workspace_allowed(self, validator, temp_user_workspace):
        """Test creating files in active workspace is allowed."""
        target = temp_user_workspace / "tests" / "test_new_feature.py"
        
        result = validator.validate(target, OperationType.CREATE)
        
        assert result == ValidationResult.ALLOWED
    
    def test_create_in_cortex_core_denied(self, validator, temp_cortex_root):
        """Test creating files in CORTEX core is denied."""
        target = temp_cortex_root / "src" / "tier1" / "new_file.py"
        
        result = validator.validate(target, OperationType.CREATE)
        
        assert result == ValidationResult.DENIED


class TestDeleteOperations:
    """Test DELETE operation validation."""
    
    def test_delete_from_active_workspace_allowed(self, validator, temp_user_workspace):
        """Test deleting from active workspace is allowed."""
        target = temp_user_workspace / "src" / "old_feature.py"
        
        result = validator.validate(target, OperationType.DELETE)
        
        assert result == ValidationResult.ALLOWED
    
    def test_delete_from_cortex_non_core_allowed(self, validator, temp_cortex_root):
        """Test deleting from CORTEX non-core is allowed."""
        target = temp_cortex_root / "temp" / "cache.db"
        
        result = validator.validate(target, OperationType.DELETE)
        
        assert result == ValidationResult.ALLOWED
    
    def test_delete_from_cortex_core_denied(self, validator, temp_cortex_root):
        """Test deleting from CORTEX core is denied."""
        target = temp_cortex_root / "src" / "tier0" / "critical.py"
        
        result = validator.validate(target, OperationType.DELETE)
        
        assert result == ValidationResult.DENIED
    
    def test_delete_from_inactive_workspace_denied(self, validator, tmp_path):
        """Test deleting from non-active workspace is denied."""
        other_workspace = tmp_path / "OtherApp"
        other_workspace.mkdir()
        target = other_workspace / "src" / "file.py"
        
        result = validator.validate(target, OperationType.DELETE)
        
        assert result == ValidationResult.DENIED


class TestValidateOrRaise:
    """Test validate_or_raise functionality."""
    
    def test_allowed_operation_no_exception(self, validator, temp_user_workspace):
        """Test allowed operation doesn't raise exception."""
        target = temp_user_workspace / "src" / "file.py"
        
        # Should not raise
        validator.validate_or_raise(target, OperationType.WRITE)
    
    def test_denied_operation_raises_exception(self, validator, temp_cortex_root):
        """Test denied operation raises PermissionError."""
        target = temp_cortex_root / "src" / "tier0" / "protected.py"
        
        with pytest.raises(PermissionError) as exc_info:
            validator.validate_or_raise(target, OperationType.WRITE)
        
        assert "Workspace operation denied" in str(exc_info.value)


class TestValidationReport:
    """Test validation report generation."""
    
    def test_report_structure(self, validator, temp_user_workspace):
        """Test validation report has correct structure."""
        target = temp_user_workspace / "src" / "file.py"
        
        report = validator.get_validation_report(target, OperationType.WRITE)
        
        assert 'target_path' in report
        assert 'operation' in report
        assert 'result' in report
        assert 'active_workspace' in report
        assert 'checks' in report
    
    def test_report_active_workspace_info(self, validator, mock_workspace_info):
        """Test report includes active workspace information."""
        target = mock_workspace_info.path / "src" / "file.py"
        
        report = validator.get_validation_report(target, OperationType.WRITE)
        
        assert report['active_workspace']['name'] == "UserApp"
        assert report['active_workspace']['id'] == "test-workspace-uuid"
    
    def test_report_checks_details(self, validator, temp_cortex_root):
        """Test report includes detailed check results."""
        target = temp_cortex_root / "src" / "tier0" / "file.py"
        
        report = validator.get_validation_report(target, OperationType.WRITE)
        
        assert report['checks']['is_cortex_core'] is True
        assert report['checks']['in_cortex_root'] is True


class TestGlobalValidatorInstance:
    """Test global validator singleton."""
    
    def test_get_workspace_validator_returns_instance(self):
        """Test get_workspace_validator returns WorkspaceOperationValidator."""
        validator = get_workspace_validator()
        
        assert isinstance(validator, WorkspaceOperationValidator)
    
    def test_get_workspace_validator_singleton(self):
        """Test get_workspace_validator returns same instance."""
        validator1 = get_workspace_validator()
        validator2 = get_workspace_validator()
        
        assert validator1 is validator2
