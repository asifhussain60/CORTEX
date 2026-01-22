"""Test suite for TDD Enhancement Layer 3 - Tier0 Governance Validation.

Tests Tier0 validation layer for governance compliance including:
- Enhanced violation detection with governance context
- CORE-* rule validation via AST analysis
- Violation registry (SQLite/in-memory)
- Compliance report generation
"""

from typing import List, Dict
import sqlite3
import tempfile
from pathlib import Path
import pytest


class TestTier0ValidationLayer:
    """Test Tier0 validation layer basics."""

    def test_tier0_validator_initialization(self) -> None:
        """Test Tier0Validator can be instantiated."""
        from cortex.testing.tdd_enhancement_layer3_validation import Tier0Validator
        
        validator = Tier0Validator()
        assert validator is not None

    def test_validator_has_required_methods(self) -> None:
        """Test Tier0Validator has all required methods."""
        from cortex.testing.tdd_enhancement_layer3_validation import Tier0Validator
        
        validator = Tier0Validator()
        assert hasattr(validator, "validate_code")
        assert hasattr(validator, "validate_governance")
        assert hasattr(validator, "get_violations")

    def test_validator_enhanced_detection(self) -> None:
        """Test validator uses enhanced violation detection."""
        from cortex.testing.tdd_enhancement_layer3_validation import Tier0Validator
        
        validator = Tier0Validator()
        
        code = """
def process():
    try:
        work()
    except:
        pass
"""
        violations = validator.validate_code(code, "test.py")
        
        assert len(violations) > 0


class TestCoreRuleValidation:
    """Test validation of CORE-* governance rules."""

    def test_validate_core_013_no_bare_except(self) -> None:
        """Test CORE-013: No bare except clauses."""
        from cortex.testing.tdd_enhancement_layer3_validation import Tier0Validator
        
        validator = Tier0Validator()
        
        code = """
try:
    work()
except:
    pass
"""
        violations = validator.validate_governance(code, rules=["CORE-013"])
        
        core_013_violations = [
            v for v in violations
            if "CORE-013" in v.get("rule", "")
        ]
        assert len(core_013_violations) > 0

    def test_validate_core_011_type_hints(self) -> None:
        """Test CORE-011: All functions must have type hints."""
        from cortex.testing.tdd_enhancement_layer3_validation import Tier0Validator
        
        validator = Tier0Validator()
        
        code = """
def process(data):
    return data.upper()
"""
        violations = validator.validate_governance(code, rules=["CORE-011"])
        
        core_011_violations = [
            v for v in violations
            if "CORE-011" in v.get("rule", "")
        ]
        assert len(core_011_violations) > 0

    def test_validate_core_012_docstrings(self) -> None:
        """Test CORE-012: Google-style docstrings required."""
        from cortex.testing.tdd_enhancement_layer3_validation import Tier0Validator
        
        validator = Tier0Validator()
        
        code = """
def process(data: str) -> str:
    return data.upper()
"""
        violations = validator.validate_governance(code, rules=["CORE-012"])
        
        core_012_violations = [
            v for v in violations
            if "CORE-012" in v.get("rule", "")
        ]
        assert len(core_012_violations) > 0

    def test_validate_core_008_tdd(self) -> None:
        """Test CORE-008: Tests must be written first."""
        from cortex.testing.tdd_enhancement_layer3_validation import Tier0Validator
        
        validator = Tier0Validator()
        
        # CORE-008 is enforced via process, not per-file
        assert hasattr(validator, "validate_tdd_order")

    def test_validate_multiple_rules(self) -> None:
        """Test validation of multiple CORE rules together."""
        from cortex.testing.tdd_enhancement_layer3_validation import Tier0Validator
        
        validator = Tier0Validator()
        
        bad_code = """
def bad_func():
    try:
        work()
    except:
        pass
"""
        violations = validator.validate_governance(
            bad_code,
            rules=["CORE-011", "CORE-012", "CORE-013"]
        )
        
        # Should have violations for all three rules
        assert len(violations) >= 3


class TestViolationRegistry:
    """Test violation registry storage and retrieval."""

    def test_registry_initialization(self) -> None:
        """Test violation registry can be initialized."""
        from cortex.testing.tdd_enhancement_layer3_validation import ViolationRegistry
        
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = ViolationRegistry(db_path=f"{tmpdir}/violations.db")
            assert registry is not None

    def test_registry_stores_violations(self) -> None:
        """Test registry can store violations."""
        from cortex.testing.tdd_enhancement_layer3_validation import ViolationRegistry, Violation
        
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = ViolationRegistry(db_path=f"{tmpdir}/violations.db")
            
            violation = Violation(
                file_path="test.py",
                line_number=5,
                rule="CORE-013",
                message="Bare except clause",
                severity="error"
            )
            
            registry.store_violation(violation)
            
            # Should be able to retrieve
            violations = registry.get_violations(file_path="test.py")
            assert len(violations) > 0

    def test_registry_retrieves_by_rule(self) -> None:
        """Test retrieving violations by rule."""
        from cortex.testing.tdd_enhancement_layer3_validation import ViolationRegistry, Violation
        
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = ViolationRegistry(db_path=f"{tmpdir}/violations.db")
            
            v1 = Violation("a.py", 1, "CORE-013", "Error 1", "error")
            v2 = Violation("b.py", 2, "CORE-011", "Error 2", "error")
            
            registry.store_violation(v1)
            registry.store_violation(v2)
            
            core_013_violations = registry.get_violations(rule="CORE-013")
            assert len(core_013_violations) == 1

    def test_registry_in_memory_mode(self) -> None:
        """Test registry in in-memory mode."""
        from cortex.testing.tdd_enhancement_layer3_validation import ViolationRegistry
        
        registry = ViolationRegistry(mode="memory")
        assert registry.mode == "memory"

    def test_registry_sqlite_mode(self) -> None:
        """Test registry in SQLite mode."""
        from cortex.testing.tdd_enhancement_layer3_validation import ViolationRegistry
        
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = ViolationRegistry(
                mode="sqlite",
                db_path=f"{tmpdir}/violations.db"
            )
            assert registry.mode == "sqlite"


class TestComplianceReporting:
    """Test compliance report generation."""

    def test_generate_compliance_report(self) -> None:
        """Test generating compliance report."""
        from cortex.testing.tdd_enhancement_layer3_validation import Tier0Validator
        
        validator = Tier0Validator()
        
        code = """
def process():
    try:
        work()
    except:
        pass
"""
        violations = validator.validate_code(code, "test.py")
        report = validator.generate_compliance_report(violations)
        
        assert report is not None
        assert isinstance(report, dict)

    def test_report_includes_summary(self) -> None:
        """Test report includes summary statistics."""
        from cortex.testing.tdd_enhancement_layer3_validation import Tier0Validator
        
        validator = Tier0Validator()
        
        code = """
def func1():
    pass
def func2():
    try:
        pass
    except:
        pass
"""
        violations = validator.validate_code(code, "test.py")
        report = validator.generate_compliance_report(violations)
        
        assert "summary" in report
        assert "total_violations" in report["summary"]
        assert "by_rule" in report["summary"]

    def test_report_includes_violations(self) -> None:
        """Test report includes detailed violations."""
        from cortex.testing.tdd_enhancement_layer3_validation import Tier0Validator
        
        validator = Tier0Validator()
        
        code = """
def func(data):
    pass
"""
        violations = validator.validate_code(code, "test.py")
        report = validator.generate_compliance_report(violations)
        
        assert "violations" in report
        assert isinstance(report["violations"], list)

    def test_report_export_to_json(self) -> None:
        """Test exporting report to JSON."""
        from cortex.testing.tdd_enhancement_layer3_validation import Tier0Validator
        import json
        
        validator = Tier0Validator()
        
        code = """
def func():
    pass
"""
        violations = validator.validate_code(code, "test.py")
        report = validator.generate_compliance_report(violations)
        
        # Should be JSON serializable
        json_str = json.dumps(report)
        assert len(json_str) > 0

    def test_report_compliance_score(self) -> None:
        """Test report includes compliance score."""
        from cortex.testing.tdd_enhancement_layer3_validation import Tier0Validator
        
        validator = Tier0Validator()
        
        # Clean code
        clean_code = '''
def process(data: str) -> str:
    """Process data.
    
    Args:
        data: Input string.
        
    Returns:
        Processed string.
    """
    return data.upper()
'''
        violations = validator.validate_code(clean_code, "test.py")
        report = validator.generate_compliance_report(violations)
        
        assert "compliance_score" in report
        # Clean code should have high score
        assert report["compliance_score"] >= 90


class TestASTContextAnalysis:
    """Test AST-based context analysis."""

    def test_ast_module_analysis(self) -> None:
        """Test AST module-level analysis."""
        from cortex.testing.tdd_enhancement_layer3_validation import ASTAnalyzer
        
        analyzer = ASTAnalyzer()
        
        code = """
def func1(): pass
def func2(): pass
"""
        analysis = analyzer.analyze(code)
        
        assert analysis is not None
        assert "functions" in analysis

    def test_ast_function_context(self) -> None:
        """Test AST function context extraction."""
        from cortex.testing.tdd_enhancement_layer3_validation import ASTAnalyzer
        
        analyzer = ASTAnalyzer()
        
        code = """
def process(data: str) -> str:
    return data.upper()
"""
        analysis = analyzer.analyze(code)
        
        assert "functions" in analysis
        functions = analysis["functions"]
        assert any(f["name"] == "process" for f in functions)

    def test_ast_class_context(self) -> None:
        """Test AST class context extraction."""
        from cortex.testing.tdd_enhancement_layer3_validation import ASTAnalyzer
        
        analyzer = ASTAnalyzer()
        
        code = """
class Processor:
    def process(self, data: str) -> str:
        return data.upper()
"""
        analysis = analyzer.analyze(code)
        
        assert "classes" in analysis
        classes = analysis["classes"]
        assert any(c["name"] == "Processor" for c in classes)


class TestGovernanceContextAwareness:
    """Test governance context awareness."""

    def test_context_aware_violation_detection(self) -> None:
        """Test violations are context-aware."""
        from cortex.testing.tdd_enhancement_layer3_validation import Tier0Validator
        
        validator = Tier0Validator()
        
        # Bare except in test is OK (different context)
        test_code = """
def test_something():
    try:
        do_test()
    except:
        pass
"""
        # Bare except in production is NOT OK
        prod_code = """
def process():
    try:
        do_work()
    except:
        pass
"""
        
        test_violations = validator.validate_code(test_code, "test_file.py")
        prod_violations = validator.validate_code(prod_code, "prod_file.py")
        
        # May have different severity levels based on context


class TestPerformance:
    """Test Tier0 validation performance."""

    def test_validation_completes_quickly(self) -> None:
        """Test validation completes within reasonable time."""
        from cortex.testing.tdd_enhancement_layer3_validation import Tier0Validator
        import time
        
        validator = Tier0Validator()
        
        large_code = "\n".join([
            f"def func_{i}(data: str) -> str: return data"
            for i in range(500)
        ])
        
        start = time.time()
        violations = validator.validate_code(large_code, "test.py")
        elapsed = time.time() - start
        
        assert elapsed < 5.0, f"Validation took {elapsed}s, expected <5s"


class TestErrorHandling:
    """Test error handling in Tier0 validation."""

    def test_handle_syntax_errors(self) -> None:
        """Test handling of Python syntax errors."""
        from cortex.testing.tdd_enhancement_layer3_validation import Tier0Validator
        
        validator = Tier0Validator()
        
        bad_code = "def func(\n    invalid python"
        
        violations = validator.validate_code(bad_code, "test.py")
        
        # Should handle and report
        assert len(violations) > 0

    def test_handle_empty_code(self) -> None:
        """Test handling of empty code."""
        from cortex.testing.tdd_enhancement_layer3_validation import Tier0Validator
        
        validator = Tier0Validator()
        
        violations = validator.validate_code("", "test.py")
        
        # Should handle gracefully
        assert isinstance(violations, list)


class TestRegistryPersistence:
    """Test violation registry persistence."""

    def test_registry_persists_to_disk(self) -> None:
        """Test registry persists violations to disk."""
        from cortex.testing.tdd_enhancement_layer3_validation import ViolationRegistry, Violation
        
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = f"{tmpdir}/violations.db"
            
            # Create and populate registry with sqlite mode
            registry1 = ViolationRegistry(mode="sqlite", db_path=db_path)
            v = Violation("test.py", 5, "CORE-013", "Bare except", "error")
            registry1.store_violation(v)
            del registry1
            
            # Reopen and verify
            registry2 = ViolationRegistry(mode="sqlite", db_path=db_path)
            violations = registry2.get_violations(file_path="test.py")
            
            assert len(violations) > 0

    def test_registry_clear_violations(self) -> None:
        """Test clearing violations from registry."""
        from cortex.testing.tdd_enhancement_layer3_validation import ViolationRegistry, Violation
        
        with tempfile.TemporaryDirectory() as tmpdir:
            registry = ViolationRegistry(db_path=f"{tmpdir}/violations.db")
            
            v = Violation("test.py", 5, "CORE-013", "Error", "error")
            registry.store_violation(v)
            
            violations_before = registry.get_violations(file_path="test.py")
            assert len(violations_before) > 0
            
            registry.clear_violations(file_path="test.py")
            
            violations_after = registry.get_violations(file_path="test.py")
            assert len(violations_after) == 0
