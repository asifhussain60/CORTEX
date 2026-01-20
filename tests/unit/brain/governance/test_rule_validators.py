"""
Unit tests for Rule Validators

AC-GOV-CTX-001-03: Rule validators implement condition checks for all 29 CORE rules
"""

import pytest
from pathlib import Path
from cortex.brain.core.governance.rule_validators import (
    validate_core_001_incremental,
    validate_core_008_tdd,
    validate_core_011_type_hints,
    validate_core_012_docstrings,
    validate_core_013_error_handling,
    validate_core_022_kebab_case,
    validate_core_028_file_length,
    RuleViolation
)
from cortex.brain.core.governance.context_extractor import GovernanceContext


class TestCoreRuleValidators:
    """Test suite for CORE rule validators"""
    
    # CORE-001: Incremental execution <500 lines per turn
    
    def test_core_001_pass_small_operation(self) -> None:
        """Test CORE-001 passes for small operations"""
        context = GovernanceContext(
            file_path="cortex/module.py",
            file_type="python",
            operation_type="implement",
            development_phase="production",
            code_classification="production"
        )
        
        violation = validate_core_001_incremental(context, lines_changed=250)
        assert violation is None
    
    def test_core_001_violation_large_operation(self) -> None:
        """Test CORE-001 violations for large operations"""
        context = GovernanceContext(
            file_path="cortex/module.py",
            file_type="python",
            operation_type="implement",
            development_phase="production",
            code_classification="production"
        )
        
        violation = validate_core_001_incremental(context, lines_changed=600)
        assert violation is not None
        assert violation.rule_id == "CORE-001"
        assert "500" in violation.message
    
    # CORE-008: TDD - Tests before code
    
    def test_core_008_pass_test_exists(self) -> None:
        """Test CORE-008 passes when test file exists"""
        context = GovernanceContext(
            file_path="cortex/core/module.py",
            file_type="python",
            operation_type="implement",
            development_phase="production",
            code_classification="production"
        )
        
        violation = validate_core_008_tdd(context, test_file_exists=True)
        assert violation is None
    
    def test_core_008_violation_no_test(self) -> None:
        """Test CORE-008 violations when test missing"""
        context = GovernanceContext(
            file_path="cortex/core/module.py",
            file_type="python",
            operation_type="implement",
            development_phase="production",
            code_classification="production"
        )
        
        violation = validate_core_008_tdd(context, test_file_exists=False)
        assert violation is not None
        assert violation.rule_id == "CORE-008"
        assert "test" in violation.message.lower()
    
    # CORE-011: Type hints required
    
    def test_core_011_pass_full_type_hints(self) -> None:
        """Test CORE-011 passes with complete type hints"""
        context = GovernanceContext(
            file_path="cortex/module.py",
            file_type="python",
            operation_type="implement",
            development_phase="production",
            code_classification="production"
        )
        
        violation = validate_core_011_type_hints(
            context,
            functions_analyzed=10,
            functions_with_hints=10
        )
        assert violation is None
    
    def test_core_011_violation_missing_hints(self) -> None:
        """Test CORE-011 violations for missing type hints"""
        context = GovernanceContext(
            file_path="cortex/module.py",
            file_type="python",
            operation_type="implement",
            development_phase="production",
            code_classification="production"
        )
        
        violation = validate_core_011_type_hints(
            context,
            functions_analyzed=10,
            functions_with_hints=7
        )
        assert violation is not None
        assert violation.rule_id == "CORE-011"
        assert "type hint" in violation.message.lower()
    
    # CORE-012: Docstrings required
    
    def test_core_012_pass_all_documented(self) -> None:
        """Test CORE-012 passes with complete docstrings"""
        context = GovernanceContext(
            file_path="cortex/module.py",
            file_type="python",
            operation_type="implement",
            development_phase="production",
            code_classification="production"
        )
        
        violation = validate_core_012_docstrings(
            context,
            public_apis=5,
            documented_apis=5
        )
        assert violation is None
    
    def test_core_012_violation_missing_docstrings(self) -> None:
        """Test CORE-012 violations for missing docstrings"""
        context = GovernanceContext(
            file_path="cortex/module.py",
            file_type="python",
            operation_type="implement",
            development_phase="production",
            code_classification="production"
        )
        
        violation = validate_core_012_docstrings(
            context,
            public_apis=5,
            documented_apis=2
        )
        assert violation is not None
        assert violation.rule_id == "CORE-012"
        assert "docstring" in violation.message.lower()
    
    # CORE-013: No bare except
    
    def test_core_013_pass_no_bare_except(self) -> None:
        """Test CORE-013 passes without bare except"""
        context = GovernanceContext(
            file_path="cortex/module.py",
            file_type="python",
            operation_type="implement",
            development_phase="production",
            code_classification="production"
        )
        
        violation = validate_core_013_error_handling(
            context,
            bare_except_count=0
        )
        assert violation is None
    
    def test_core_013_violation_bare_except(self) -> None:
        """Test CORE-013 violations for bare except"""
        context = GovernanceContext(
            file_path="cortex/module.py",
            file_type="python",
            operation_type="implement",
            development_phase="production",
            code_classification="production"
        )
        
        violation = validate_core_013_error_handling(
            context,
            bare_except_count=2
        )
        assert violation is not None
        assert violation.rule_id == "CORE-013"
        assert "except" in violation.message.lower()
    
    # CORE-022: Kebab-case naming
    
    def test_core_022_pass_kebab_case(self) -> None:
        """Test CORE-022 passes for kebab-case names"""
        context = GovernanceContext(
            file_path="docs/user-guide.md",
            file_type="markdown",
            operation_type="implement",
            development_phase="production",
            code_classification="production"
        )
        
        violation = validate_core_022_kebab_case(
            context,
            filename="user-guide.md"
        )
        assert violation is None
    
    def test_core_022_violation_snake_case(self) -> None:
        """Test CORE-022 violations for non-kebab-case"""
        context = GovernanceContext(
            file_path="docs/user_guide.md",
            file_type="markdown",
            operation_type="implement",
            development_phase="production",
            code_classification="production"
        )
        
        violation = validate_core_022_kebab_case(
            context,
            filename="user_guide.md"
        )
        assert violation is not None
        assert violation.rule_id == "CORE-022"
        assert "kebab" in violation.message.lower()
    
    # CORE-028: File length limits
    
    def test_core_028_pass_reasonable_length(self) -> None:
        """Test CORE-028 passes for reasonable file lengths"""
        context = GovernanceContext(
            file_path="cortex/module.py",
            file_type="python",
            operation_type="implement",
            development_phase="production",
            code_classification="production"
        )
        
        violation = validate_core_028_file_length(
            context,
            line_count=300
        )
        assert violation is None
    
    def test_core_028_violation_excessive_length(self) -> None:
        """Test CORE-028 violations for excessive file length"""
        context = GovernanceContext(
            file_path="cortex/module.py",
            file_type="python",
            operation_type="implement",
            development_phase="production",
            code_classification="production"
        )
        
        violation = validate_core_028_file_length(
            context,
            line_count=800
        )
        assert violation is not None
        assert violation.rule_id == "CORE-028"
        assert "500" in violation.message or "length" in violation.message.lower()
    
    # RuleViolation dataclass
    
    def test_rule_violation_creation(self) -> None:
        """Test creating RuleViolation instance"""
        violation = RuleViolation(
            rule_id="CORE-999",
            message="Test violation",
            severity="blocked",
            file_path="test.py",
            context={"test": "data"}
        )
        
        assert violation.rule_id == "CORE-999"
        assert violation.message == "Test violation"
        assert violation.severity == "blocked"
        assert violation.file_path == "test.py"
        assert violation.context["test"] == "data"
    
    def test_rule_violation_string_representation(self) -> None:
        """Test RuleViolation string representation"""
        violation = RuleViolation(
            rule_id="CORE-001",
            message="Test message",
            severity="blocked",
            file_path="test.py"
        )
        
        str_repr = str(violation)
        assert "CORE-001" in str_repr
        assert "test.py" in str_repr


class TestValidatorEdgeCases:
    """Test edge cases for validators"""
    
    def test_validators_handle_none_context(self) -> None:
        """Test validators handle missing optional parameters"""
        context = GovernanceContext(
            file_path="",
            file_type="unknown",
            operation_type="implement",
            development_phase="development",
            code_classification="production"
        )
        
        # Should not crash
        violation = validate_core_011_type_hints(context, 0, 0)
        assert violation is None  # No functions to validate
    
    def test_validators_with_zero_values(self) -> None:
        """Test validators with zero counts"""
        context = GovernanceContext(
            file_path="cortex/empty.py",
            file_type="python",
            operation_type="implement",
            development_phase="production",
            code_classification="production"
        )
        
        # Empty file should pass
        violation = validate_core_011_type_hints(context, 0, 0)
        assert violation is None
        
        violation = validate_core_012_docstrings(context, 0, 0)
        assert violation is None
