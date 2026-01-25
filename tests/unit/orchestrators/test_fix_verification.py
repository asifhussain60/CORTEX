"""
CORTEX AC-PERMANENT-FIX Verification Tests

AC-ID: AC-PERMANENT-FIX-002
Purpose: Automated tests to ensure AC-PERMANENT-FIX commits remain active.

These tests run as part of the CI pipeline to detect any regression
of permanent fixes.

Entry Point: tests.unit.orchestrators.test_fix_verification
"""

import pytest
from pathlib import Path

from tests.unit.orchestrators.verify_registry import (
    verify_registry_template_locked,
    verify_orchestrator_wiring,
    verify_wiring_status_section,
    verify_all,
)


class TestACPermanentFix001:
    """Tests for AC-PERMANENT-FIX-001: Orchestrator Registry Unwiring Fix."""
    
    def test_registry_template_is_locked(self) -> None:
        """
        AC-PERMANENT-FIX-001: registry_template must be false.
        
        This prevents automatic regeneration of the registry which would
        wipe all orchestrator wiring on git pull.
        """
        is_valid, message = verify_registry_template_locked()
        
        assert is_valid, f"AC-PERMANENT-FIX-001 REGRESSION: {message}"
    
    def test_minimum_orchestrators_wired(self) -> None:
        """
        AC-PERMANENT-FIX-001: At least 18 orchestrators must be wired.
        
        This ensures the registry has proper orchestrator wiring
        and hasn't been reset to an empty state.
        """
        is_valid, message = verify_orchestrator_wiring(min_wired=18)
        
        assert is_valid, f"AC-PERMANENT-FIX-001 REGRESSION: {message}"
    
    def test_full_wiring_status(self) -> None:
        """
        AC-PERMANENT-FIX-001: Wiring status section must show healthy state.
        """
        is_valid, message = verify_wiring_status_section()
        
        assert is_valid, f"Wiring status check failed: {message}"


class TestACPermanentFix002:
    """Tests for AC-PERMANENT-FIX-002: Verification Mechanisms."""
    
    def test_verify_registry_script_exists(self) -> None:
        """
        AC-PERMANENT-FIX-002: verify_registry.py must exist.
        """
        verify_script = Path(__file__).parent / "verify_registry.py"
        
        assert verify_script.exists(), (
            "AC-PERMANENT-FIX-002 REGRESSION: verify_registry.py not found"
        )
    
    def test_verify_all_returns_results(self) -> None:
        """
        AC-PERMANENT-FIX-002: verify_all() must return valid results.
        """
        results = verify_all()
        
        assert isinstance(results, dict), "verify_all() must return a dict"
        assert len(results) >= 3, "verify_all() must check at least 3 items"
        
        for check_name, result in results.items():
            assert "valid" in result, f"{check_name} missing 'valid' key"
            assert "message" in result, f"{check_name} missing 'message' key"
            assert "critical" in result, f"{check_name} missing 'critical' key"


class TestACPermanentFix003:
    """Tests for AC-PERMANENT-FIX-003: Executive Summary Documentation."""
    
    def test_permanent_solution_doc_exists(self) -> None:
        """
        AC-PERMANENT-FIX-003: ORCHESTRATOR-UNWIRING-FIX-PERMANENT-SOLUTION.md must exist.
        """
        doc_path = (
            Path(__file__).parents[3] / 
            "docs" / 
            "ORCHESTRATOR-UNWIRING-FIX-PERMANENT-SOLUTION.md"
        )
        
        assert doc_path.exists(), (
            "AC-PERMANENT-FIX-003 REGRESSION: "
            "ORCHESTRATOR-UNWIRING-FIX-PERMANENT-SOLUTION.md not found"
        )
    
    def test_permanent_solution_doc_has_content(self) -> None:
        """
        AC-PERMANENT-FIX-003: Documentation must have meaningful content.
        """
        doc_path = (
            Path(__file__).parents[3] / 
            "docs" / 
            "ORCHESTRATOR-UNWIRING-FIX-PERMANENT-SOLUTION.md"
        )
        
        if not doc_path.exists():
            pytest.skip("Documentation file not found")
        
        content = doc_path.read_text(encoding="utf-8")
        
        # Check for key sections
        assert "AC-PERMANENT-FIX-001" in content, "Missing AC-PERMANENT-FIX-001 reference"
        assert "registry_template" in content, "Missing registry_template explanation"


class TestACPermanentFix004:
    """Tests for AC-PERMANENT-FIX-004: Registry Persistence."""
    
    def test_registry_file_exists(self) -> None:
        """
        AC-PERMANENT-FIX-004: repo-registry.yaml must exist.
        """
        registry_path = (
            Path(__file__).parents[3] / 
            "cortex_brain" / "tier0" / "repo-registry.yaml"
        )
        
        assert registry_path.exists(), (
            "AC-PERMANENT-FIX-004 REGRESSION: repo-registry.yaml not found"
        )
    
    def test_registry_has_production_status(self) -> None:
        """
        AC-PERMANENT-FIX-004: Registry must have production status.
        """
        import yaml
        
        registry_path = (
            Path(__file__).parents[3] / 
            "cortex_brain" / "tier0" / "repo-registry.yaml"
        )
        
        if not registry_path.exists():
            pytest.skip("Registry file not found")
        
        content = registry_path.read_text(encoding="utf-8")
        registry = yaml.safe_load(content)
        
        metadata = registry.get("metadata", {})
        status = metadata.get("status", "")
        
        assert "PRODUCTION" in status or "WIRED" in status, (
            f"Registry not in production state: {status}"
        )


class TestAllACPermanentFixes:
    """Integration test for all AC-PERMANENT-FIX commits."""
    
    def test_all_critical_fixes_active(self) -> None:
        """
        All critical AC-PERMANENT-FIX commits must be active.
        
        This is the main CI gate test that ensures no permanent fix
        has regressed.
        """
        results = verify_all()
        
        critical_failures = [
            (name, result) 
            for name, result in results.items()
            if result["critical"] and not result["valid"]
        ]
        
        if critical_failures:
            failure_msgs = [
                f"{name}: {result['message']}" 
                for name, result in critical_failures
            ]
            pytest.fail(
                f"AC-PERMANENT-FIX REGRESSIONS DETECTED:\n" + 
                "\n".join(failure_msgs)
            )
