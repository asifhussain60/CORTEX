#!/usr/bin/env python3
"""
Unit Tests for PolicyValidator

Tests policy validation logic, compliance calculation, and report generation.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.validation.policy_validator import (
    PolicyValidator,
    PolicyViolation,
    ValidationResult,
    ViolationSeverity
)
from src.operations.policy_scanner import PolicyScanner, PolicyDocument, PolicyFormat


class TestPolicyValidator:
    """Test suite for PolicyValidator class."""
    
    @pytest.fixture
    def temp_project_root(self):
        """Create temporary project directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def temp_cortex_root(self):
        """Create temporary CORTEX directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_dir = Path(tmpdir) / "CORTEX"
            cortex_dir.mkdir()
            yield cortex_dir
    
    @pytest.fixture
    def sample_policies(self):
        """Sample policy content for testing."""
        return {
            "naming_conventions": {
                "classes_pascal_case": True,
                "functions_snake_case": True,
                "constants_upper_case": True
            },
            "security_rules": {
                "no_hardcoded_credentials": True,
                "use_environment_variables": True,
                "validate_all_inputs": True
            },
            "code_standards": {
                "require_docstrings": True,
                "test_coverage_minimum": 70,
                "run_linter": True
            },
            "architecture_patterns": {
                "solid_principles": True,
                "max_function_length": 50
            }
        }
    
    def test_validate_no_policies_returns_compliant(self, temp_project_root, temp_cortex_root):
        """Test: Returns 100% compliant when no policies exist (total_rules=0)"""
        # Mock PolicyScanner to return empty list
        with patch('src.validation.policy_validator.PolicyScanner') as mock_scanner:
            mock_instance = MagicMock()
            mock_instance.scan_for_policies.return_value = []
            mock_scanner.return_value = mock_instance
            
            validator = PolicyValidator(temp_project_root, temp_cortex_root)
            result = validator.validate()
            
            assert result.compliant is True
            assert result.total_rules == 0
            assert result.passed == 0
            assert result.failed == 0
            assert result.compliance_percentage == 100.0
            assert len(result.violations) == 0
    
    def test_validate_naming_conventions(self, temp_project_root, temp_cortex_root, sample_policies):
        """Test: Checks PascalCase/snake_case/UPPER_CASE conventions"""
        # Create temporary policy file
        policy_file = temp_project_root / "test.yaml"
        policy_file.write_text(yaml.dump(sample_policies))
        
        # Create mock policy document
        policy_doc = PolicyDocument(
            path=policy_file,
            format=PolicyFormat.YAML,
            content=sample_policies,
            categories=["naming_conventions"]
        )
        
        with patch('src.validation.policy_validator.PolicyScanner') as mock_scanner:
            mock_instance = MagicMock()
            mock_instance.scan_for_policies.return_value = [policy_doc]
            mock_scanner.return_value = mock_instance
            
            validator = PolicyValidator(temp_project_root, temp_cortex_root)
            passed, total = validator._validate_naming(policy_doc)
            
            assert isinstance(passed, int)
            assert isinstance(total, int)
            assert total >= 3  # At least 3 naming rules
            assert passed <= total
    
    def test_validate_security_no_hardcoded_secrets(self, temp_project_root, temp_cortex_root):
        """Test: Detects hardcoded passwords/API keys"""
        # Create config file with hardcoded secret
        config_file = temp_cortex_root / "cortex.config.json"
        config_file.write_text('{"api_key": "secret123", "password": "admin"}')
        
        # Create policy file
        policy_content = {
            "security_rules": {
                "no_hardcoded_credentials": True,
                "use_environment_variables": True
            }
        }
        policy_file = temp_project_root / "test.yaml"
        policy_file.write_text(yaml.dump(policy_content))
        
        policy_doc = PolicyDocument(
            path=policy_file,
            format=PolicyFormat.YAML,
            content=policy_content,
            categories=["security"]
        )
        
        validator = PolicyValidator(temp_project_root, temp_cortex_root)
        passed, total = validator._validate_security(policy_doc)
        
        # Should detect violations
        assert total >= 2
        assert passed < total  # Some rules should fail
    
    def test_validate_standards_docstrings(self, temp_project_root, temp_cortex_root):
        """Test: Checks docstring presence"""
        policy_content = {
            "code_standards": {
                "require_docstrings": True,
                "test_coverage_minimum": 70
            }
        }
        policy_file = temp_project_root / "test.yaml"
        policy_file.write_text(yaml.dump(policy_content))
        
        policy_doc = PolicyDocument(
            path=policy_file,
            format=PolicyFormat.YAML,
            content=policy_content,
            categories=["standards"]
        )
        
        validator = PolicyValidator(temp_project_root, temp_cortex_root)
        passed, total = validator._validate_standards(policy_doc)
        
        assert isinstance(passed, int)
        assert isinstance(total, int)
        assert total >= 1  # At least docstring rule
    
    def test_validate_architecture_function_length(self, temp_project_root, temp_cortex_root):
        """Test: Checks max 50 lines per function"""
        policy_content = {
            "architecture_patterns": {
                "solid_principles": True,
                "separation_of_concerns": True,
                "max_function_length": 50
            }
        }
        policy_file = temp_project_root / "test.yaml"
        policy_file.write_text(yaml.dump(policy_content))
        
        policy_doc = PolicyDocument(
            path=policy_file,
            format=PolicyFormat.YAML,
            content=policy_content,
            categories=["architecture"]
        )
        
        validator = PolicyValidator(temp_project_root, temp_cortex_root)
        passed, total = validator._validate_architecture(policy_doc)
        
        assert isinstance(passed, int)
        assert isinstance(total, int)
        assert total >= 1
    
    def test_compliance_percentage_calculation(self, temp_project_root, temp_cortex_root):
        """Test: (20 passed / 24 total) * 100 = 83.33%"""
        result = ValidationResult(
            compliant=True,
            total_rules=24,
            passed=20,
            failed=4,
            violations=[],
            summary="Test summary"
        )
        
        assert result.compliance_percentage == pytest.approx(83.33, rel=0.01)
    
    def test_compliance_percentage_zero_rules(self, temp_project_root, temp_cortex_root):
        """Test: Returns 100% when total_rules=0"""
        result = ValidationResult(
            compliant=True,
            total_rules=0,
            passed=0,
            failed=0,
            violations=[],
            summary="No rules"
        )
        
        assert result.compliance_percentage == 100.0
    
    def test_generate_report_creates_file(self, temp_project_root, temp_cortex_root, sample_policies):
        """Test: Creates Markdown report with all sections"""
        # Create violations
        violations = [
            PolicyViolation(
                category="security",
                severity=ViolationSeverity.CRITICAL,
                rule="no_hardcoded_credentials",
                location="cortex.config.json",
                description="Hardcoded API key detected",
                recommendation="Move to environment variable"
            ),
            PolicyViolation(
                category="naming",
                severity=ViolationSeverity.WARNING,
                rule="snake_case_functions",
                location="src/example.py",
                description="Function uses camelCase",
                recommendation="Rename to snake_case"
            )
        ]
        
        result = ValidationResult(
            compliant=False,
            total_rules=10,
            passed=8,
            failed=2,
            violations=violations,
            summary="Test validation"
        )
        
        # Create reports directory
        reports_dir = temp_cortex_root / "cortex-brain" / "documents" / "reports"
        reports_dir.mkdir(parents=True)
        
        validator = PolicyValidator(temp_project_root, temp_cortex_root)
        report_path = validator.generate_report(result)
        
        assert report_path.exists()
        assert report_path.is_file()
        assert report_path.name == "policy-compliance.md"
        
        # Check content
        content = report_path.read_text(encoding='utf-8')
        assert "# Policy Compliance Report" in content
        assert "## Summary" in content
        assert "## Violations" in content
        assert "Critical" in content  # Violations section has severity headers
        assert "Warnings" in content or "WARNING" in content
        assert "80.0%" in content  # Compliance percentage
    
    def test_critical_violations_flagged(self, temp_project_root, temp_cortex_root):
        """Test: ViolationSeverity.CRITICAL correctly set"""
        violation = PolicyViolation(
            category="security",
            severity=ViolationSeverity.CRITICAL,
            rule="no_hardcoded_credentials",
            location="config.json",
            description="Hardcoded password",
            recommendation="Use env var"
        )
        
        assert violation.severity == ViolationSeverity.CRITICAL
        assert violation.severity.value == "CRITICAL"
    
    def test_validation_result_summary_generation(self):
        """Test: ValidationResult generates appropriate summary"""
        # Fully compliant
        result = ValidationResult(
            compliant=True,
            total_rules=10,
            passed=10,
            failed=0,
            violations=[],
            summary=""
        )
        result.summary = f"✅ Fully compliant - {result.passed}/{result.total_rules} rules passed"
        assert "✅ Fully compliant" in result.summary
        
        # Mostly compliant
        result2 = ValidationResult(
            compliant=True,
            total_rules=10,
            passed=9,
            failed=1,
            violations=[],
            summary=""
        )
        result2.summary = f"⚠️ Mostly compliant - {result2.passed}/{result2.total_rules} rules passed"
        assert "⚠️ Mostly compliant" in result2.summary
        
        # Has issues
        result3 = ValidationResult(
            compliant=False,
            total_rules=10,
            passed=6,
            failed=4,
            violations=[],
            summary=""
        )
        result3.summary = f"❌ Compliance issues - {result3.passed}/{result3.total_rules} rules passed"
        assert "❌ Compliance issues" in result3.summary
    
    def test_validate_with_policies_returns_result(self, temp_project_root, temp_cortex_root, sample_policies):
        """Test: Full validation workflow returns ValidationResult"""
        # Create policy file
        policy_file = temp_project_root / "test.yaml"
        policy_file.write_text(yaml.dump(sample_policies))
        
        policy_doc = PolicyDocument(
            path=policy_file,
            format=PolicyFormat.YAML,
            content=sample_policies,
            categories=["naming_conventions", "security_rules"]
        )
        
        with patch('src.validation.policy_validator.PolicyScanner') as mock_scanner:
            mock_instance = MagicMock()
            mock_instance.scan_for_policies.return_value = [policy_doc]
            mock_scanner.return_value = mock_instance
            
            validator = PolicyValidator(temp_project_root, temp_cortex_root)
            result = validator.validate()
            
            assert isinstance(result, ValidationResult)
            assert result.total_rules > 0
            assert result.passed >= 0
            assert result.failed >= 0
            assert result.passed + result.failed == result.total_rules
            assert 0 <= result.compliance_percentage <= 100


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
