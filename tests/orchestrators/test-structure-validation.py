"""
Test Structure Validation

Verifies golden test framework structure meets CORE-028 requirements.

Authority: AC-GOLDEN-FRAMEWORK-001
Governance: CORE-028 (kebab-case file naming)
"""
from pathlib import Path

import pytest


class TestGoldenTestStructure:
    """Validate golden test framework directory structure."""
    
    def test_core_directories_exist(self):
        """Should have core orchestrator test directories."""
        base = Path("tests/orchestrators/core")
        
        assert (base / "positive").exists(), "Missing core/positive directory"
        assert (base / "negative").exists(), "Missing core/negative directory"
        assert (base / "edge-cases").exists(), "Missing core/edge-cases directory"
        assert (base / "recovery").exists(), "Missing core/recovery directory"
    
    def test_domain_directories_exist(self):
        """Should have domain orchestrator test directories."""
        base = Path("tests/orchestrators/domain")
        
        assert (base / "positive").exists(), "Missing domain/positive directory"
        assert (base / "negative").exists(), "Missing domain/negative directory"
        assert (base / "edge-cases").exists(), "Missing domain/edge-cases directory"
        assert (base / "recovery").exists(), "Missing domain/recovery directory"
    
    def test_support_directories_exist(self):
        """Should have support orchestrator test directories."""
        base = Path("tests/orchestrators/support")
        
        assert (base / "positive").exists(), "Missing support/positive directory"
        assert (base / "negative").exists(), "Missing support/negative directory"
        assert (base / "edge-cases").exists(), "Missing support/edge-cases directory"
        assert (base / "recovery").exists(), "Missing support/recovery directory"
    
    def test_fixtures_directory_exists(self):
        """Should have fixtures directory structure."""
        base = Path("tests/fixtures")
        
        assert (base / "orchestrator-configs").exists(), "Missing orchestrator-configs"
        assert (base / "sample-repos").exists(), "Missing sample-repos"
        assert (base / "knowledge-bases").exists(), "Missing knowledge-bases"
    
    def test_e2e_directory_exists(self):
        """Should have e2e test directory."""
        assert Path("tests/e2e").exists(), "Missing e2e directory"
    
    def test_base_test_classes_exist(self):
        """Should have all 4 base test classes."""
        base = Path("tests/orchestrators")
        
        assert (base / "base_orchestrator_test.py").exists(), "Missing base_orchestrator_test.py"
        assert (base / "base_negative_test.py").exists(), "Missing base_negative_test.py"
        assert (base / "base_edge_case_test.py").exists(), "Missing base_edge_case_test.py"
        assert (base / "base_recovery_test.py").exists(), "Missing base_recovery_test.py"
    
    def test_kebab_case_file_naming(self):
        """Should use kebab-case for all test files (CORE-028)."""
        base = Path("tests/orchestrators")
        
        for test_file in base.rglob("*.py"):
            filename = test_file.name
            
            # Skip __init__.py and base classes
            if filename.startswith("__") or filename.startswith("base-"):
                continue
            
            # Check kebab-case: no underscores except test_ prefix
            if filename.startswith("test-"):
                name_part = filename[5:-3]  # Remove test- prefix and .py suffix
                assert "_" not in name_part, \
                    f"CORE-028 VIOLATION: {filename} uses snake_case, should be kebab-case"
                assert not any(c.isupper() for c in name_part), \
                    f"CORE-028 VIOLATION: {filename} has uppercase, should be lowercase"
    
    def test_no_screaming_case(self):
        """Should have no SCREAMING_CASE files (CORE-028)."""
        base = Path("tests/orchestrators")
        
        for test_file in base.rglob("*.py"):
            filename = test_file.name
            
            # Skip __init__.py
            if filename.startswith("__"):
                continue
            
            assert not filename.isupper(), \
                f"CORE-028 VIOLATION: {filename} is SCREAMING_CASE"
    
    def test_no_version_suffixes(self):
        """Should have no _v2, _v3 version suffixes (CORE-066)."""
        base = Path("tests/orchestrators")
        
        for test_file in base.rglob("*.py"):
            filename = test_file.stem  # Without .py
            
            assert not any(filename.endswith(f"_v{i}") for i in range(2, 10)), \
                f"CORE-066 VIOLATION: {test_file.name} has version suffix"
            assert not any(filename.endswith(f"-v{i}") for i in range(2, 10)), \
                f"CORE-066 VIOLATION: {test_file.name} has version suffix"
