"""
Unit tests for YAML-first enforcement middleware
=================================================
Tests enforcement that all plans must be YAML before implementation.

Author: GitHub Copilot (for CORTEX)
Created: 2026-01-08
Feature: feat04-core-orchestration
Task: 1.3
TDD Phase: RED
"""

import pytest
from pathlib import Path
from src.orchestrators.middleware.yaml_first_enforcement import (
    YAMLFirstEnforcer,
    YAMLFirstViolation,
    EnforcementResult
)


class TestYAMLFirstEnforcement:
    """Test YAML-first enforcement"""
    
    @pytest.fixture
    def enforcer(self, tmp_path):
        """Create enforcer with temp directory"""
        return YAMLFirstEnforcer(planning_root=tmp_path)
    
    # -------------------------------------------------------------------------
    # Detection Tests
    # -------------------------------------------------------------------------
    
    def test_detects_plan_request_without_yaml(self, enforcer):
        """Should detect when user requests plan implementation without YAML"""
        request = "implement the planning system"
        
        result = enforcer.check_request(request)
        
        assert result.violation_detected is True
        assert result.violation_type == "missing_yaml"
        assert "YAML plan required" in result.message
    
    def test_allows_plan_creation_request(self, enforcer):
        """Should allow requests to create YAML plans"""
        request = "create a plan for the planning system"
        
        result = enforcer.check_request(request)
        
        assert result.violation_detected is False
    
    def test_detects_direct_implementation_keywords(self, enforcer):
        """Should detect direct implementation keywords"""
        requests = [
            "implement the feature",
            "build the component",
            "create the class",
            "write the function"
        ]
        
        for request in requests:
            result = enforcer.check_request(request)
            assert result.violation_detected is True, f"Failed for: {request}"
    
    def test_allows_with_existing_yaml(self, enforcer, tmp_path):
        """Should allow implementation if YAML plan exists"""
        # Create a complete YAML plan file
        plan_file = tmp_path / "plans" / "test-plan.yaml"
        plan_file.parent.mkdir(parents=True, exist_ok=True)
        plan_file.write_text("""
feature:
  id: test-feature
  name: Test Feature
phases:
  - id: 1
    name: Phase 1
tasks:
  - id: 1.1
    name: Task 1
""")
        
        request = "implement test-plan"
        
        result = enforcer.check_request(request, plan_file=plan_file)
        
        assert result.violation_detected is False
    
    # -------------------------------------------------------------------------
    # Validation Tests
    # -------------------------------------------------------------------------
    
    def test_validates_yaml_exists(self, enforcer, tmp_path):
        """Should validate YAML file exists"""
        plan_file = tmp_path / "missing.yaml"
        
        result = enforcer.validate_yaml_exists(plan_file)
        
        assert result.valid is False
        assert "not found" in result.message.lower()
    
    def test_validates_yaml_format(self, enforcer, tmp_path):
        """Should validate YAML is properly formatted"""
        plan_file = tmp_path / "invalid.yaml"
        plan_file.write_text("invalid: yaml: content: [")
        
        result = enforcer.validate_yaml_format(plan_file)
        
        assert result.valid is False
        assert "invalid" in result.message.lower()
    
    def test_validates_yaml_has_required_fields(self, enforcer, tmp_path):
        """Should validate YAML has required plan fields"""
        plan_file = tmp_path / "incomplete.yaml"
        plan_file.write_text("feature: test")  # Missing phases, tasks, etc.
        
        result = enforcer.validate_yaml_structure(plan_file)
        
        assert result.valid is False
        assert "required fields" in result.message.lower()
    
    # -------------------------------------------------------------------------
    # Prevention Tests
    # -------------------------------------------------------------------------
    
    def test_prevents_execution_without_yaml(self, enforcer):
        """Should prevent execution if YAML doesn't exist"""
        request = "implement the feature"
        
        with pytest.raises(YAMLFirstViolation) as exc_info:
            enforcer.enforce(request)
        
        assert "YAML plan required" in str(exc_info.value)
    
    def test_allows_execution_with_valid_yaml(self, enforcer, tmp_path):
        """Should allow execution with valid YAML plan"""
        plan_file = tmp_path / "valid-plan.yaml"
        plan_file.write_text("""
feature:
  id: test-feature
  name: Test Feature
  phases:
    - id: 1
      name: Phase 1
      tasks:
        - id: 1.1
          name: Task 1
""")
        
        request = "implement test-feature"
        result = enforcer.enforce(request, plan_file=plan_file)
        
        assert result.allowed is True
    
    # -------------------------------------------------------------------------
    # Guidance Tests
    # -------------------------------------------------------------------------
    
    def test_provides_guidance_on_violation(self, enforcer):
        """Should provide clear guidance when violation detected"""
        request = "implement the feature"
        
        result = enforcer.check_request(request)
        
        assert result.guidance is not None
        # Check for key phrases in guidance (case-insensitive)
        guidance_lower = result.guidance.lower()
        assert "yaml" in guidance_lower
        assert "plan" in guidance_lower
        assert "cortex" in guidance_lower
    
    def test_guidance_includes_example_structure(self, enforcer):
        """Should include example YAML structure in guidance"""
        result = enforcer.get_yaml_guidance()
        
        assert "feature:" in result
        assert "phases:" in result
        assert "tasks:" in result
    
    # -------------------------------------------------------------------------
    # Integration with Intelligence Layer
    # -------------------------------------------------------------------------
    
    def test_integrates_with_intelligence_middleware(self, enforcer):
        """Should integrate with intelligence middleware"""
        # This test validates the enforcer can be used independently
        # Full integration tested in test_intelligence_middleware.py
        request = "implement the feature"
        
        result = enforcer.check_request(request)
        
        assert result.violation_detected is True
        assert result.audit_logged is True
    
    def test_logs_violations_to_audit(self, enforcer):
        """Should log violations to audit log"""
        request = "implement the feature"
        
        result = enforcer.check_request(request)
        
        # Should have audit entry
        assert result.audit_logged is True
        assert result.correlation_id is not None


class TestYAMLFirstViolation:
    """Test YAMLFirstViolation exception"""
    
    def test_exception_contains_guidance(self):
        """Should include guidance in exception"""
        violation = YAMLFirstViolation(
            message="YAML required",
            guidance="Create YAML plan first"
        )
        
        assert "YAML required" in str(violation)
        assert violation.guidance == "Create YAML plan first"
    
    def test_exception_includes_context(self):
        """Should include context about the violation"""
        violation = YAMLFirstViolation(
            message="YAML required",
            request="implement feature",
            suggested_plan_path=Path("plans/feature.yaml")
        )
        
        assert violation.request == "implement feature"
        assert violation.suggested_plan_path.name == "feature.yaml"


class TestEnforcementResult:
    """Test EnforcementResult data class"""
    
    def test_result_structure(self):
        """Should have correct structure"""
        result = EnforcementResult(
            violation_detected=True,
            violation_type="missing_yaml",
            message="YAML required",
            guidance="Create plan first",
            allowed=False,
            audit_logged=True,
            correlation_id="TEST-001"
        )
        
        assert result.violation_detected is True
        assert result.allowed is False
        assert result.correlation_id == "TEST-001"
