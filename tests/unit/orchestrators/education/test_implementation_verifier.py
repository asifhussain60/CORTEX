"""
Tests for ImplementationVerifier - Phase 22 ASK Mode System.

The ImplementationVerifier ensures implementations match specifications,
verifies DoR completion, and validates test coverage.

TDD Approach:
- RED: Write tests first (this file)
- GREEN: Implement to pass tests
- REFACTOR: Optimize after passing
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from cortex.orchestrators.education.implementation_verifier import (
    ImplementationVerifier,
    VerificationResult,
    SpecCompliance,
    ComplianceLevel
)


class TestDoRVerification:
    """Test Definition of Ready (DoR) verification."""
    
    def test_verifies_complete_dor(self, tmp_path):
        """Should verify DoR is complete when all criteria met."""
        verifier = ImplementationVerifier(repo_root=tmp_path)
        
        # Create mock DoR with all criteria
        dor = {
            "intent": "IMPLEMENT",
            "target": "TestOrchestrator",
            "test_file": "tests/unit/test_orchestrator.py",
            "challenge_complete": True,
            "extensibility_validated": True,
            "scalability_validated": True,
            "security_validated": True
        }
        
        result = verifier.verify_dor(dor)
        
        assert result.is_complete is True
        assert result.missing_criteria == []
        assert result.compliance_level == ComplianceLevel.FULL
        
    def test_detects_missing_dor_criteria(self, tmp_path):
        """Should detect when DoR criteria are missing."""
        verifier = ImplementationVerifier(repo_root=tmp_path)
        
        # Incomplete DoR
        dor = {
            "intent": "IMPLEMENT",
            "target": "TestOrchestrator"
            # Missing: test_file, challenge_complete, etc.
        }
        
        result = verifier.verify_dor(dor)
        
        assert result.is_complete is False
        assert "test_file" in result.missing_criteria
        assert "challenge_complete" in result.missing_criteria
        assert result.compliance_level == ComplianceLevel.PARTIAL


class TestSpecCompliance:
    """Test specification compliance verification."""
    
    def test_verifies_implementation_matches_spec(self, tmp_path):
        """Should verify implementation matches specification."""
        verifier = ImplementationVerifier(repo_root=tmp_path)
        
        # Create spec file
        spec_file = tmp_path / "spec.yaml"
        spec_file.write_text("""
required_methods:
  - initialize
  - execute
  - cleanup
required_attributes:
  - name
  - version
""")
        
        # Create implementation file
        impl_file = tmp_path / "implementation.py"
        impl_file.write_text("""
class TestClass:
    def __init__(self):
        self.name = "test"
        self.version = "1.0"
    
    def initialize(self): pass
    def execute(self): pass
    def cleanup(self): pass
""")
        
        result = verifier.verify_spec_compliance(
            spec_file=spec_file,
            impl_file=impl_file
        )
        
        assert result.compliance_level == ComplianceLevel.FULL
        assert result.missing_requirements == []
        assert result.confidence >= 0.9
        
required_methods:
  - initialize
  - execute
  - cleanup
""")
        
        impl_file = tmp_path / "implementation.py"
        impl_file.write_text("""
class TestClass:
    def initialize(self): pass
    # Missing: execute, cleanup
""")
        
        result = verifier.verify_spec_compliance(
            spec_file=spec_file,
            impl_file=impl_file
        )
        
        assert result.compliance_level == ComplianceLevel.PARTIAL
        assert "execute" in result.missing_requirements
        assert "cleanup" in result.missing_requirements
        assert result.confidence < 0.5


class TestCoverageVerification:
    """Test test coverage verification."""
    
    def test_verifies_adequate_coverage(self, tmp_path):
        """Should verify test coverage meets threshold."""
        verifier = ImplementationVerifier(repo_root=tmp_path)
        
        # Mock coverage data
        coverage_data = {
            "files": {
                "test_module.py": {
                    "summary": {
                        "percent_covered": 92.5,
                        "num_statements": 100,
                        "missing_lines": 8
                    }
                }
            }
        }
        
        result = verifier.verify_coverage(
            coverage_data=coverage_data,
            threshold=0.85
        )
        
        assert result.is_adequate is True
        assert result.coverage_percent >= 0.85
        assert result.compliance_level == ComplianceLevel.FULL
        
    def test_detects_insufficient_coverage(self, tmp_path):
        """Should detect when coverage is below threshold."""
        verifier = ImplementationVerifier(repo_root=tmp_path)
        
        coverage_data = {
            "files": {
                "test_module.py": {
                    "summary": {
                        "percent_covered": 65.0,
                        "num_statements": 100,
                        "missing_lines": 35
                    }
                }
            }
        }
        
        result = verifier.verify_coverage(
            coverage_data=coverage_data,
            threshold=0.85
        )
        
        assert result.is_adequate is False
        assert result.coverage_percent < 0.85
        assert result.compliance_level == ComplianceLevel.PARTIAL
        assert len(result.uncovered_critical_paths) > 0


class TestArchitecturalAlignment:
    """Test architectural alignment verification."""
    
    def test_verifies_wiring_alignment(self, tmp_path):
        """Should verify component is properly wired."""
        verifier = ImplementationVerifier(repo_root=tmp_path)
        
        # Create wiring.yaml
        wiring_file = tmp_path / "wiring.yaml"
        wiring_file.write_text("""
orchestrators:
  core:
    - name: TestOrchestrator
      module: cortex.orchestrators.test_orchestrator
      tier: 1
      priority: 10
""")
        
        result = verifier.verify_architectural_alignment(
            component_name="TestOrchestrator",
            wiring_file=wiring_file
        )
        
        assert result.is_aligned is True
        assert result.wiring_found is True
        assert result.compliance_level == ComplianceLevel.FULL
        
    def test_detects_missing_wiring(self, tmp_path):
        """Should detect when component is not wired."""
        verifier = ImplementationVerifier(repo_root=tmp_path)
        
        wiring_file = tmp_path / "wiring.yaml"
        wiring_file.write_text("""
orchestrators:
  core:
    - name: OtherOrchestrator
      module: cortex.orchestrators.other
""")
        
        result = verifier.verify_architectural_alignment(
            component_name="TestOrchestrator",
            wiring_file=wiring_file
        )
        
        assert result.is_aligned is False
        assert result.wiring_found is False
        assert result.compliance_level == ComplianceLevel.NONE


class TestSecurityCompliance:
    """Test security compliance verification."""
    
    def test_verifies_no_security_issues(self, tmp_path):
        """Should verify no security issues in implementation."""
        verifier = ImplementationVerifier(repo_root=tmp_path)
        
        impl_file = tmp_path / "secure.py"
        impl_file.write_text("""
import os
from pathlib import Path

def process_file(file_path):
    # Proper validation
    path = Path(file_path).resolve()
    if not path.is_file():
        raise ValueError("Invalid file")
    return path.read_text()
""")
        
        result = verifier.verify_security_compliance(impl_file)
        
        assert result.has_issues is False
        assert result.security_score >= 0.9
        assert result.compliance_level == ComplianceLevel.FULL
        
    def test_detects_security_vulnerabilities(self, tmp_path):
        """Should detect security vulnerabilities."""
        verifier = ImplementationVerifier(repo_root=tmp_path)
        
        impl_file = tmp_path / "insecure.py"
        impl_file.write_text("""
import pickle
import subprocess

def load_data(data):
    # SECURITY ISSUE: Unsafe deserialization
    return pickle.loads(data)

def run_command(cmd):
    # SECURITY ISSUE: Command injection
    subprocess.call(cmd, shell=True)
""")
        
        result = verifier.verify_security_compliance(impl_file)
        
        assert result.has_issues is True
        assert len(result.vulnerabilities) > 0
        assert any("pickle" in v.lower() for v in result.vulnerabilities)
        assert result.compliance_level == ComplianceLevel.PARTIAL


class TestComprehensiveVerification:
    """Test comprehensive verification combining all checks."""
    
    def test_performs_comprehensive_verification(self, tmp_path):
        """Should perform all verification checks in sequence."""
        verifier = ImplementationVerifier(repo_root=tmp_path)
        
        # Create minimal valid setup
        spec_file = tmp_path / "spec.yaml"
        spec_file.write_text("required_methods: [execute]")
        
        impl_file = tmp_path / "impl.py"
        impl_file.write_text("class Test:\n    def execute(self): pass")
        
        wiring_file = tmp_path / "wiring.yaml"
        wiring_file.write_text("""
orchestrators:
  core:
    - name: TestOrchestrator
""")
        
        dor = {
            "intent": "IMPLEMENT",
            "target": "TestOrchestrator",
            "test_file": "tests/test.py",
            "challenge_complete": True,
            "extensibility_validated": True,
            "scalability_validated": True,
            "security_validated": True
        }
        
        result = verifier.verify_comprehensive(
            dor=dor,
            spec_file=spec_file,
            impl_file=impl_file,
            wiring_file=wiring_file
        )
        
        assert result.overall_compliance in [ComplianceLevel.PARTIAL, ComplianceLevel.FULL]
        assert result.dor_verified is True
        assert result.spec_compliant is True
        assert result.architecturally_aligned is True
        
    def test_fails_when_critical_checks_fail(self, tmp_path):
        """Should fail overall when critical checks fail."""
        verifier = ImplementationVerifier(repo_root=tmp_path)
        
        # Incomplete DoR
        dor = {"intent": "IMPLEMENT"}
        
        # Missing spec
        spec_file = tmp_path / "spec.yaml"
        spec_file.write_text("")
        
        impl_file = tmp_path / "impl.py"
        impl_file.write_text("")
        
        wiring_file = tmp_path / "wiring.yaml"
        wiring_file.write_text("")
        
        result = verifier.verify_comprehensive(
            dor=dor,
            spec_file=spec_file,
            impl_file=impl_file,
            wiring_file=wiring_file
        )
        
        assert result.overall_compliance == ComplianceLevel.NONE
        assert result.critical_failures > 0


class TestVerificationReport:
    """Test verification report generation."""
    
    def test_generates_detailed_report(self, tmp_path):
        """Should generate detailed verification report."""
        verifier = ImplementationVerifier(repo_root=tmp_path)
        
        # Create verification result
        dor = {
            "intent": "IMPLEMENT",
            "target": "TestOrchestrator",
            "test_file": "tests/test.py"
        }
        
        report = verifier.generate_report(dor=dor)
        
        assert "DoR Status" in report
        assert "Spec Compliance" in report
        assert "Test Coverage" in report
        assert "Architectural Alignment" in report
        assert "Security Compliance" in report
        
class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_handles_missing_files_gracefully(self, tmp_path):
        """Should handle missing files without crashing."""
        verifier = ImplementationVerifier(repo_root=tmp_path)
        
        nonexistent_file = tmp_path / "nonexistent.py"
        
        result = verifier.verify_security_compliance(nonexistent_file)
        
        assert result.has_issues is False  # No issues found in nonexistent file
        assert result.compliance_level == ComplianceLevel.NONE
        
    def test_handles_malformed_yaml(self, tmp_path):
        """Should handle malformed YAML gracefully."""
        verifier = ImplementationVerifier(repo_root=tmp_path)
        
        bad_yaml = tmp_path / "bad.yaml"
        bad_yaml.write_text("{ malformed: yaml: content")
        
        result = verifier.verify_spec_compliance(
            spec_file=bad_yaml,
            impl_file=tmp_path / "impl.py"
        )
        
        assert result.compliance_level == ComplianceLevel.NONE
        
    def test_handles_empty_dor(self, tmp_path):
        """Should handle empty DoR."""
        verifier = ImplementationVerifier(repo_root=tmp_path)
        
        result = verifier.verify_dor({})
        
        assert result.is_complete is False
        assert len(result.missing_criteria) > 0
