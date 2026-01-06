"""
Unit tests for Setup Verification Middleware.

Test-first approach per CORTEX SKULL rules.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from typing import Dict, Any
from src.orchestrators.middleware.setup_verification import (
    SetupVerificationMiddleware,
    VerificationResult,
    VerificationLevel,
    VerificationError
)


class TestSetupVerificationMiddleware:
    """Test suite for SetupVerificationMiddleware."""
    
    @pytest.fixture
    def middleware(self, tmp_path):
        """Create middleware instance."""
        return SetupVerificationMiddleware(workspace_root=tmp_path)
    
    def test_initialization(self, middleware):
        """Test middleware initializes correctly."""
        assert middleware is not None
        assert hasattr(middleware, 'workspace_root')
        assert hasattr(middleware, 'verifications')
    
    def test_verify_directory_exists(self, middleware, tmp_path):
        """Test directory existence verification."""
        test_dir = tmp_path / "test_directory"
        test_dir.mkdir()
        
        result = middleware.verify_directory_exists(str(test_dir))
        
        assert result.passed is True
        assert result.level == VerificationLevel.REQUIRED
    
    def test_verify_directory_missing_fails(self, middleware, tmp_path):
        """Test missing directory fails verification."""
        missing_dir = tmp_path / "missing_directory"
        
        result = middleware.verify_directory_exists(str(missing_dir))
        
        assert result.passed is False
        assert "does not exist" in result.message.lower()
    
    def test_verify_file_exists(self, middleware, tmp_path):
        """Test file existence verification."""
        test_file = tmp_path / "test_file.txt"
        test_file.write_text("test content")
        
        result = middleware.verify_file_exists(str(test_file))
        
        assert result.passed is True
    
    def test_verify_python_environment(self, middleware):
        """Test Python environment verification."""
        result = middleware.verify_python_environment()
        
        assert result.passed is True
        assert "Python" in result.message
    
    def test_verify_dependencies(self, middleware):
        """Test dependency verification."""
        dependencies = ["os", "sys", "json"]
        
        result = middleware.verify_dependencies(dependencies)
        
        assert result.passed is True
    
    def test_verify_missing_dependencies_fails(self, middleware):
        """Test missing dependencies fail verification."""
        dependencies = ["nonexistent_module_xyz"]
        
        result = middleware.verify_dependencies(dependencies)
        
        assert result.passed is False
    
    def test_verify_brain_structure(self, middleware, tmp_path):
        """Test brain structure verification."""
        # Create brain structure
        brain_dir = tmp_path / "cortex-brain"
        brain_dir.mkdir()
        (brain_dir / "tier0").mkdir()
        (brain_dir / "tier1").mkdir()
        
        result = middleware.verify_brain_structure()
        
        assert result.passed is True
    
    def test_verify_permissions(self, middleware, tmp_path):
        """Test file permissions verification."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        
        result = middleware.verify_permissions(str(test_file), readable=True)
        
        assert result.passed is True
    
    def test_run_all_verifications(self, middleware, tmp_path):
        """Test running all verifications."""
        # Setup minimal structure
        (tmp_path / "cortex-brain").mkdir()
        
        results = middleware.run_all_verifications()
        
        assert isinstance(results, list)
        assert len(results) > 0
        assert all(isinstance(r, VerificationResult) for r in results)
    
    def test_verification_summary(self, middleware, tmp_path):
        """Test verification summary generation."""
        (tmp_path / "cortex-brain").mkdir()
        
        results = middleware.run_all_verifications()
        summary = middleware.get_summary(results)
        
        assert "total" in summary
        assert "passed" in summary
        assert "failed" in summary
    
    def test_critical_failure_raises_error(self, middleware):
        """Test critical verification failure raises error."""
        result = VerificationResult(
            name="critical_check",
            passed=False,
            level=VerificationLevel.CRITICAL,
            message="Critical failure"
        )
        
        with pytest.raises(VerificationError):
            middleware.enforce_critical([result])
    
    def test_warning_doesnt_raise_error(self, middleware):
        """Test warning level doesn't raise error."""
        result = VerificationResult(
            name="warning_check",
            passed=False,
            level=VerificationLevel.WARNING,
            message="Warning only"
        )
        
        # Should not raise
        middleware.enforce_critical([result])
    
    def test_add_custom_verification(self, middleware):
        """Test adding custom verification."""
        def custom_check() -> VerificationResult:
            return VerificationResult(
                name="custom",
                passed=True,
                level=VerificationLevel.OPTIONAL,
                message="Custom check passed"
            )
        
        middleware.add_verification("custom", custom_check)
        
        assert "custom" in middleware.verifications
    
    def test_skip_optional_verifications(self, middleware):
        """Test skipping optional verifications."""
        results = middleware.run_all_verifications(
            skip_optional=True
        )
        
        optional_results = [
            r for r in results 
            if r.level == VerificationLevel.OPTIONAL
        ]
        
        assert len(optional_results) == 0
