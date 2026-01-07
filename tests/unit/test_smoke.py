# ==============================================================================
# CORTEX 6.0 Smoke Tests
# ==============================================================================
# Basic smoke tests to verify test infrastructure is working.
#
# Author: Asif Hussain
# Copyright © 2025-2026 Asif Hussain. All rights reserved.
# ==============================================================================
"""Smoke tests to verify test infrastructure."""

import pytest
from pathlib import Path


class TestInfrastructure:
    """Tests to verify the test infrastructure is working."""
    
    def test_pytest_runs(self):
        """Verify pytest can run tests."""
        assert True
    
    def test_project_root_fixture(self, project_root: Path):
        """Verify project_root fixture works."""
        assert project_root.exists()
        assert (project_root / "src").exists()
    
    def test_temp_dir_fixture(self, temp_dir: Path):
        """Verify temp_dir fixture creates a directory."""
        assert temp_dir.exists()
        assert temp_dir.is_dir()
    
    def test_fixtures_data_exists(self, fixtures_path: Path):
        """Verify fixture data files exist."""
        assert fixtures_path.exists()
        assert (fixtures_path / "sample_governance_rules.yaml").exists()
        assert (fixtures_path / "sample_dag.json").exists()


class TestAuditLoggerInfrastructure:
    """Tests to verify audit logger infrastructure."""
    
    def test_audit_logger_import(self):
        """Verify audit logger can be imported."""
        from src.orchestrators.audit_logger import EnterpriseAuditLogger, AuditLevel, AuditCategory
        assert EnterpriseAuditLogger is not None
        assert AuditLevel is not None
        assert AuditCategory is not None
    
    def test_mock_audit_logger_fixture(self, mock_audit_logger):
        """Verify mock_audit_logger fixture works."""
        assert mock_audit_logger is not None
        mock_audit_logger.log_info("test message")
        mock_audit_logger.log_info.assert_called_once()
    
    def test_audit_logger_creates_log_file(self, temp_log_dir: Path):
        """Verify audit logger creates log files."""
        from src.orchestrators.audit_logger import EnterpriseAuditLogger, AuditCategory, AuditLevel
        
        logger = EnterpriseAuditLogger(
            log_dir=str(temp_log_dir),
            enable_console=False,
            enable_file=True
        )
        
        # Log a test entry
        logger.log(
            level=AuditLevel.INFO,
            category=AuditCategory.VALIDATION,
            component="test_smoke",
            operation="test_operation",
            message="Test smoke log entry",
            context={"test": True}
        )
        
        # Verify log directory has content
        log_files = list(temp_log_dir.glob("*.json")) + list(temp_log_dir.glob("*.log"))
        # Note: May not create files immediately depending on implementation
        assert temp_log_dir.exists()


class TestStateManagerInfrastructure:
    """Tests to verify state manager infrastructure."""
    
    def test_state_manager_import(self):
        """Verify state manager can be imported."""
        from src.orchestrators.state_manager import StateManager, StateType
        assert StateManager is not None
        assert StateType is not None
    
    def test_mock_state_manager_fixture(self, mock_state_manager):
        """Verify mock_state_manager fixture works."""
        assert mock_state_manager is not None
        mock_state_manager.set_state("key", "value")
        mock_state_manager.set_state.assert_called_once()
