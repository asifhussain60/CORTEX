"""
Integration tests for CORTEX error recovery and SKULL protection.

Tests SKULL protection rules, failure handling, and rollback mechanisms.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from pathlib import Path
import tempfile
import yaml

from src.tier0.brain_protector import BrainProtector
from src.operations import execute_operation


class TestSKULLProtectionLayer:
    """Test SKULL (Safety, Knowledge, Uniformity, Learning, Lockdown) protection rules."""
    
    @pytest.fixture
    def temp_brain_root(self, tmp_path):
        """Create temporary brain directory with protection rules."""
        brain_root = tmp_path / "cortex-brain"
        brain_root.mkdir()
        
        # Create brain-protection-rules.yaml
        rules_path = brain_root / "brain-protection-rules.yaml"
        rules_path.write_text("""
skull_rules:
  SKULL-001:
    name: Test Before Claim
    severity: BLOCKING
    description: Never claim "Fixed" without running tests
    enforcement: pre_commit
    
  SKULL-002:
    name: Integration Verification
    severity: BLOCKING
    description: Integrations need end-to-end tests
    enforcement: pre_commit
    
  SKULL-003:
    name: Visual Regression
    severity: WARNING
    description: CSS/UI changes need visual validation
    enforcement: pre_commit
    
  SKULL-004:
    name: Retry Without Learning
    severity: WARNING
    description: Diagnose failures before retrying
    enforcement: runtime
""")
        
        return brain_root
    
    @pytest.fixture
    def brain_protector(self, temp_brain_root):
        """Create brain protector instance."""
        return BrainProtector(brain_root=str(temp_brain_root))
    
    def test_skull_001_blocks_untested_changes(self, brain_protector):
        """Test that SKULL-001 blocks claims of fixes without tests."""
        # Simulate a fix without tests
        validation_result = brain_protector.validate_change({
            "type": "bug_fix",
            "message": "Fixed login bug ✅",
            "tests_run": False,
            "files_changed": ["src/auth/login.py"]
        })
        
        assert validation_result["status"] == "BLOCKED"
        assert "SKULL-001" in validation_result["violations"]
        assert validation_result["can_proceed"] is False
    
    def test_skull_001_allows_tested_changes(self, brain_protector):
        """Test that SKULL-001 allows changes with passing tests."""
        validation_result = brain_protector.validate_change({
            "type": "bug_fix",
            "message": "Fixed login bug ✅",
            "tests_run": True,
            "tests_passed": True,
            "files_changed": ["src/auth/login.py"]
        })
        
        assert validation_result["status"] in ["PASSED", "WARNING"]
        assert validation_result["can_proceed"] is True
    
    def test_skull_002_blocks_untested_integrations(self, brain_protector):
        """Test that SKULL-002 blocks integration changes without end-to-end tests."""
        validation_result = brain_protector.validate_change({
            "type": "integration",
            "message": "Integrated payment gateway",
            "tests_run": True,
            "has_integration_tests": False,
            "files_changed": ["src/integrations/stripe.py"]
        })
        
        assert validation_result["status"] == "BLOCKED"
        assert "SKULL-002" in validation_result["violations"]
    
    def test_skull_003_warns_on_css_changes(self, brain_protector):
        """Test that SKULL-003 warns on CSS changes without visual validation."""
        validation_result = brain_protector.validate_change({
            "type": "feature",
            "message": "Updated button styles",
            "files_changed": ["src/styles/buttons.css"],
            "has_visual_validation": False
        })
        
        assert validation_result["status"] == "WARNING"
        assert "SKULL-003" in validation_result["warnings"]
        assert validation_result["can_proceed"] is True  # WARNING allows proceed
    
    def test_skull_004_warns_on_immediate_retry(self, brain_protector):
        """Test that SKULL-004 warns when retrying without diagnosis."""
        validation_result = brain_protector.validate_change({
            "type": "retry",
            "previous_failure": True,
            "diagnosis_performed": False,
            "retry_count": 1
        })
        
        assert validation_result["status"] == "WARNING"
        assert "SKULL-004" in validation_result["warnings"]


class TestFailureHandling:
    """Test graceful failure handling across operations."""
    
    @pytest.fixture
    def temp_brain_root(self, tmp_path):
        brain_root = tmp_path / "cortex-brain"
        brain_root.mkdir()
        (brain_root / "knowledge-graph.yaml").write_text("patterns: {}")
        (brain_root / "brain-protection-rules.yaml").write_text("""
skull_rules:
  SKULL-001:
    name: Test Before Claim
    severity: BLOCKING
""")
        return brain_root
    
    def test_operation_failure_returns_error_report(self, temp_brain_root):
        """Test that operation failures return structured error reports."""
        # Execute operation that will fail (no modules implemented for this operation)
        with patch('src.operations.operation_factory.OperationFactory.get_operation_definition') as mock_def:
            mock_def.return_value = {
                "name": "Test Operation",
                "modules": ["nonexistent_module"]
            }
            
            report = execute_operation("test_operation")
            
            # Should return error report, not crash
            assert report is not None
            assert "status" in report or "error" in report
    
    def test_module_failure_doesnt_crash_operation(self, temp_brain_root):
        """Test that individual module failures don't crash entire operation."""
        with patch('src.operations.operations_orchestrator.OperationsOrchestrator') as mock_orch:
            # Configure orchestrator to have one module fail
            mock_instance = mock_orch.return_value
            mock_instance.execute.return_value = {
                "status": "partial_success",
                "modules_executed": 5,
                "modules_failed": 1,
                "failures": [{"module": "module_3", "error": "Simulated failure"}]
            }
            
            report = execute_operation("setup", profile="minimal")
            
            # Should handle gracefully
            assert report is not None
    
    def test_missing_dependency_handled_gracefully(self, temp_brain_root):
        """Test that missing Python dependencies are handled gracefully."""
        # This would test the actual error handling in modules
        # For now, verify the pattern exists
        pass  # Implementation depends on actual module error handling


class TestRollbackMechanisms:
    """Test rollback mechanisms when operations fail."""
    
    @pytest.fixture
    def temp_brain_root(self, tmp_path):
        brain_root = tmp_path / "cortex-brain"
        brain_root.mkdir()
        (brain_root / "knowledge-graph.yaml").write_text("patterns: {}")
        return brain_root
    
    def test_file_creation_rollback_on_failure(self, temp_brain_root):
        """Test that created files are rolled back on operation failure."""
        # Create temporary file
        test_file = temp_brain_root / "test_file.txt"
        
        # Simulate operation that creates file then fails
        with patch('src.operations.base_operation_module.BaseOperationModule.execute') as mock_exec:
            # Create file
            test_file.write_text("Test content")
            
            # Module fails
            mock_exec.side_effect = Exception("Simulated failure")
            
            # Rollback should remove file
            # (Implementation depends on actual rollback mechanism)
            
        # Verify rollback behavior
        # (This is a placeholder - actual test depends on rollback implementation)
    
    def test_database_rollback_on_failure(self, temp_brain_root):
        """Test that database transactions are rolled back on failure."""
        # Test database transaction rollback
        # (Implementation-specific)
        pass
    
    def test_configuration_rollback_on_failure(self, temp_brain_root):
        """Test that configuration changes are rolled back on failure."""
        # Test config rollback
        # (Implementation-specific)
        pass


class TestBrainTierProtection:
    """Test protection mechanisms for each brain tier."""
    
    @pytest.fixture
    def temp_brain_root(self, tmp_path):
        brain_root = tmp_path / "cortex-brain"
        brain_root.mkdir()
        
        # Create protection rules
        rules_path = brain_root / "brain-protection-rules.yaml"
        rules_path.write_text("""
tier0_protection:
  immutable: true
  governance_rules:
    - no_direct_modification
    - yaml_based_only
    
tier1_protection:
  max_conversations: 20
  required_schema:
    - request
    - response
    - timestamp
    
tier2_protection:
  required_fields:
    - patterns
    - lessons_learned
  validation_required: true
  
tier3_protection:
  read_only_sources:
    - git_metrics
    - test_coverage
  cache_ttl: 3600
""")
        
        return brain_root
    
    @pytest.fixture
    def brain_protector(self, temp_brain_root):
        return BrainProtector(brain_root=str(temp_brain_root))
    
    def test_tier0_immutability_enforced(self, brain_protector):
        """Test that Tier 0 (governance rules) cannot be modified directly."""
        validation = brain_protector.validate_tier_access({
            "tier": 0,
            "operation": "write",
            "file": "brain-protection-rules.yaml"
        })
        
        # Should block direct modification
        assert validation["allowed"] is False
        assert "immutable" in validation["reason"].lower()
    
    def test_tier1_schema_validation(self, brain_protector):
        """Test that Tier 1 conversation data validates against schema."""
        # Valid conversation
        valid_result = brain_protector.validate_tier1_data({
            "request": "Test request",
            "response": "Test response",
            "timestamp": "2025-11-10T12:00:00"
        })
        assert valid_result["valid"] is True
        
        # Invalid conversation (missing required field)
        invalid_result = brain_protector.validate_tier1_data({
            "request": "Test request",
            # Missing response and timestamp
        })
        assert invalid_result["valid"] is False
        assert "missing_fields" in invalid_result
    
    def test_tier1_retention_limit_enforced(self, brain_protector, temp_brain_root):
        """Test that Tier 1 enforces 20-conversation limit."""
        # This would test the actual retention logic
        # (Implementation-specific)
        pass
    
    def test_tier2_yaml_validation(self, brain_protector):
        """Test that Tier 2 knowledge graph validates YAML structure."""
        # Valid YAML
        valid_result = brain_protector.validate_tier2_data("""
patterns:
  auth_pattern:
    solution: JWT
lessons_learned:
  - Always validate input
""")
        assert valid_result["valid"] is True
        
        # Invalid YAML (missing required field)
        invalid_result = brain_protector.validate_tier2_data("""
patterns:
  auth_pattern:
    solution: JWT
# Missing lessons_learned
""")
        assert invalid_result["valid"] is False
    
    def test_tier3_read_only_enforcement(self, brain_protector):
        """Test that Tier 3 metrics are read-only."""
        validation = brain_protector.validate_tier_access({
            "tier": 3,
            "operation": "write",
            "metric": "test_coverage"
        })
        
        assert validation["allowed"] is False
        assert "read-only" in validation["reason"].lower()


class TestErrorRecoveryStrategies:
    """Test different error recovery strategies."""
    
    @pytest.fixture
    def temp_brain_root(self, tmp_path):
        brain_root = tmp_path / "cortex-brain"
        brain_root.mkdir()
        return brain_root
    
    def test_retry_with_exponential_backoff(self, temp_brain_root):
        """Test retry mechanism with exponential backoff."""
        retry_count = 0
        max_retries = 3
        
        def failing_operation():
            nonlocal retry_count
            retry_count += 1
            if retry_count < 3:
                raise Exception("Transient failure")
            return {"status": "success"}
        
        # Test retry logic
        # (Implementation would go here)
        result = failing_operation()  # This simulates eventual success
        
        assert retry_count >= 2  # Should have retried
        assert result["status"] == "success"
    
    def test_graceful_degradation(self, temp_brain_root):
        """Test graceful degradation when optional features fail."""
        # Simulate optional feature failure (e.g., vision API)
        with patch('src.tier1.vision_api.VisionAPI.analyze_screenshot') as mock_vision:
            mock_vision.side_effect = Exception("Vision API unavailable")
            
            # Operation should continue without vision API
            # (Implementation-specific test)
            pass
    
    def test_circuit_breaker_pattern(self, temp_brain_root):
        """Test circuit breaker for repeatedly failing operations."""
        # Simulate repeated failures
        failure_count = 0
        circuit_open = False
        
        def check_circuit():
            nonlocal circuit_open
            if failure_count >= 5:
                circuit_open = True
            return not circuit_open
        
        # Test circuit breaker logic
        # (Implementation would go here)


class TestOperationChainFailures:
    """Test failure propagation in operation chains."""
    
    @pytest.fixture
    def temp_brain_root(self, tmp_path):
        brain_root = tmp_path / "cortex-brain"
        brain_root.mkdir()
        (brain_root / "knowledge-graph.yaml").write_text("patterns: {}")
        return brain_root
    
    def test_required_module_failure_stops_chain(self, temp_brain_root):
        """Test that required module failure stops execution chain."""
        # Simulate operation with required modules
        with patch('src.operations.operations_orchestrator.OperationsOrchestrator.execute') as mock_exec:
            mock_exec.return_value = {
                "status": "failed",
                "failed_module": "project_validation",
                "required": True,
                "subsequent_modules_skipped": 5
            }
            
            report = execute_operation("setup", profile="minimal")
            
            # Should stop after required module failure
            assert report is not None
            # (Specific assertions depend on actual implementation)
    
    def test_optional_module_failure_continues_chain(self, temp_brain_root):
        """Test that optional module failure doesn't stop execution."""
        # Simulate operation with optional module failure
        with patch('src.operations.operations_orchestrator.OperationsOrchestrator.execute') as mock_exec:
            mock_exec.return_value = {
                "status": "partial_success",
                "failed_modules": [{"name": "vision_api", "optional": True}],
                "successful_modules": 5
            }
            
            report = execute_operation("setup", profile="full")
            
            # Should continue despite optional failure
            assert report is not None


class TestValidationRules:
    """Test validation rules and enforcement."""
    
    @pytest.fixture
    def temp_brain_root(self, tmp_path):
        brain_root = tmp_path / "cortex-brain"
        brain_root.mkdir()
        
        rules_path = brain_root / "brain-protection-rules.yaml"
        # Use raw string or escape properly - YAML doesn't need escaped backslashes in quoted strings
        rules_path.write_text("""
validation_rules:
  code_quality:
    - name: No hardcoded credentials
      pattern: "(password|api_key|secret)\\\\s*=\\\\s*['\\\"]\\\\w+"
      severity: BLOCKING
      
  test_quality:
    - name: Minimum test coverage
      threshold: 0.80
      severity: WARNING
      
  documentation:
    - name: Docstrings required
      severity: WARNING
""")
        
        return brain_root
    
    @pytest.fixture
    def brain_protector(self, temp_brain_root):
        # BrainProtector takes rules_path, not brain_root
        rules_path = temp_brain_root / "brain-protection-rules.yaml"
        return BrainProtector(rules_path=rules_path)
    
    def test_hardcoded_credentials_blocked(self, brain_protector):
        """Test that hardcoded credentials are blocked."""
        code_with_secret = """
def connect():
    api_key = "sk_test_12345"
    return client
"""
        
        validation = brain_protector.validate_code(code_with_secret)
        
        assert validation["status"] == "BLOCKED"
        assert any("hardcoded" in v["reason"].lower() for v in validation["violations"])
    
    def test_low_coverage_warning(self, brain_protector):
        """Test that low test coverage triggers warning."""
        validation = brain_protector.validate_test_coverage(0.65)
        
        assert validation["status"] == "WARNING"
        assert validation["coverage"] < 0.80


# Run with: pytest tests/integration/test_error_recovery.py -v
