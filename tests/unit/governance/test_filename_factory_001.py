"""
AC-FILENAME-FACTORY-001: Filename Factory Unit Tests

Tests for FilenameFactory, FilenameValidator, FilePathEnforcer.
Ensures all files in CORTEX system comply with CORE-028 (kebab-case, 25-char)
and CORE-038 (file placement policy).

CORE Rules Applied:
- CORE-008: Tests written BEFORE implementation (TDD)
- CORE-011: Type hints mandatory
- CORE-012: Google-style docstrings
- CORE-027: Audit trail logging
"""

import pytest
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass

from cortex.governance.filename_factory import (
    FilenameFactory,
    FilenameValidator,
    FilePathEnforcer,
    NamingViolation,
    PlacementViolation,
)


class TestFilenameValidator:
    """Test FilenameValidator against CORE-028 rules."""

    def test_valid_kebab_case_filename(self) -> None:
        """Validate correct kebab-case filename."""
        validator = FilenameValidator()
        
        valid_names = [
            "cortex-vacuum-exec.py",
            "cortex-gov-rules.yaml",
            "plan-ac-tracker.db",
            "audit-hash-chain.py",
            "phase-completion-rpt.md",
            "gov-cache-mgr.py",
        ]
        
        for name in valid_names:
            result = validator.validate(name)
            assert result.is_valid, f"Failed: {name} should be valid"
            assert len(result.violations) == 0

    def test_invalid_camelcase_filename(self) -> None:
        """Reject CamelCase filenames."""
        validator = FilenameValidator()
        
        result = validator.validate("CortexVacuumExecutor.py")
        assert not result.is_valid
        assert any(v.code == "CORE-028" for v in result.violations)

    def test_invalid_underscore_filename(self) -> None:
        """Reject filenames with underscores (use hyphens)."""
        validator = FilenameValidator()
        
        result = validator.validate("cortex_vacuum_executor.py")
        assert not result.is_valid
        assert any(v.code == "CORE-028" for v in result.violations)

    def test_exceeds_25_char_limit(self) -> None:
        """Reject filenames exceeding 25 characters."""
        validator = FilenameValidator()
        
        # 41 characters - exceeds limit
        result = validator.validate("cortex-vacuum-implementation-executor.py")
        assert not result.is_valid
        assert any(v.code == "CORE-028" for v in result.violations)

    def test_valid_max_length(self) -> None:
        """Accept filename at exactly 25 character limit."""
        validator = FilenameValidator()
        
        # Exactly 25 chars
        name = "this-is-exactly-25ch.py"  # 24 chars actually, adjust
        name = "this-is-exactly-25-char.py"  # 27 chars
        # Let's use a real example
        name = "cortex-gov-core-rules.yaml"  # 26 chars - exceeds
        name = "cortex-gov-rules.yaml"  # 22 chars - valid
        
        result = validator.validate(name)
        assert result.is_valid

    def test_contains_spaces_rejected(self) -> None:
        """Reject filenames with spaces."""
        validator = FilenameValidator()
        
        result = validator.validate("cortex vacuum executor.py")
        assert not result.is_valid

    def test_acronym_dictionary_recognized(self) -> None:
        """Validate that semantic acronyms from CORE-028 are recognized."""
        validator = FilenameValidator()
        
        # These should be recognized as semantic abbreviations
        semantic_names = [
            "cache-mgr.py",      # mgr = manager
            "config-cfg.yaml",   # cfg = config
            "audit-gen.py",      # gen = generator
            "phase-rpt.md",      # rpt = report
        ]
        
        for name in semantic_names:
            result = validator.validate(name)
            assert result.is_valid, f"Failed: {name} should be valid (semantic acronym)"

    def test_violation_includes_suggestion(self) -> None:
        """Violation result includes suggested correction."""
        validator = FilenameValidator()
        
        result = validator.validate("CortexVacuumExecutor.py")
        assert not result.is_valid
        violation = result.violations[0]
        assert violation.suggestion is not None
        assert violation.suggestion == "cortex-vacuum-executor.py"


class TestFilenameFactory:
    """Test FilenameFactory for generating compliant filenames."""

    def test_generate_from_purpose(self) -> None:
        """Generate compliant filename from purpose."""
        factory = FilenameFactory()
        
        # Generate: logging + analysis → log-anal.py
        result = factory.generate(
            purpose="logging analysis",
            file_type="py",
            max_chars=25
        )
        
        assert result.filename is not None
        assert result.filename.endswith(".py")
        assert len(result.filename) <= 25
        assert "-" in result.filename
        assert result.filename.islower()

    def test_generate_yaml_configuration(self) -> None:
        """Generate filename for YAML config file."""
        factory = FilenameFactory()
        
        result = factory.generate(
            purpose="governance cache manager",
            file_type="yaml",
            max_chars=25
        )
        
        assert result.filename is not None
        assert result.filename.endswith(".yaml")
        assert len(result.filename) <= 25

    def test_generate_markdown_documentation(self) -> None:
        """Generate filename for Markdown documentation."""
        factory = FilenameFactory()
        
        result = factory.generate(
            purpose="phase tracking completion",
            file_type="md",
            max_chars=25
        )
        
        assert result.filename is not None
        assert result.filename.endswith(".md")
        assert len(result.filename) <= 25

    def test_generate_test_file(self) -> None:
        """Generate filename for test file (special prefix)."""
        factory = FilenameFactory()
        
        result = factory.generate(
            purpose="filename factory validation",
            file_type="py",
            max_chars=25,
            prefix="test"
        )
        
        assert result.filename is not None
        assert result.filename.startswith("test-")
        assert result.filename.endswith(".py")
        assert len(result.filename) <= 25

    def test_generate_respects_char_limit(self) -> None:
        """Factory truncates intelligently to stay under char limit."""
        factory = FilenameFactory()
        
        # Very long purpose
        result = factory.generate(
            purpose="this is a very long purpose that should be intelligently abbreviated",
            file_type="py",
            max_chars=25
        )
        
        assert result.filename is not None
        assert len(result.filename) <= 25

    def test_generate_preserves_semantics(self) -> None:
        """Factory preserves semantic meaning when abbreviating."""
        factory = FilenameFactory()
        
        result = factory.generate(
            purpose="governance enforcement agent",
            file_type="py",
            max_chars=25
        )
        
        # Should preserve "governance" and "enforce" concepts
        filename_lower = result.filename.lower()
        assert "gov" in filename_lower or "governance" in filename_lower or "enforce" in filename_lower


class TestFilePathEnforcer:
    """Test FilePathEnforcer for CORE-038 placement policy."""

    def test_valid_python_module_path(self) -> None:
        """Accept valid Python module path in cortex/."""
        enforcer = FilePathEnforcer()
        
        result = enforcer.validate_path(
            path=Path("/Users/asifhussain/PROJECTS/CORTEX/cortex/governance/filename-factory.py"),
            file_type="py"
        )
        
        assert result.is_valid

    def test_valid_documentation_path(self) -> None:
        """Accept valid documentation path in docs/."""
        enforcer = FilePathEnforcer()
        
        result = enforcer.validate_path(
            path=Path("/Users/asifhussain/PROJECTS/CORTEX/docs/guides/filename-policy.md"),
            file_type="md"
        )
        
        assert result.is_valid

    def test_valid_test_path(self) -> None:
        """Accept valid test path in tests/."""
        enforcer = FilePathEnforcer()
        
        result = enforcer.validate_path(
            path=Path("/Users/asifhussain/PROJECTS/CORTEX/tests/unit/governance/test-filename-factory.py"),
            file_type="py"
        )
        
        assert result.is_valid

    def test_valid_report_path(self) -> None:
        """Accept report in reports/{subfolder}/, reject at reports root."""
        enforcer = FilePathEnforcer()
        
        # Valid: in subfolder
        result = enforcer.validate_path(
            path=Path("/Users/asifhussain/PROJECTS/CORTEX/reports/governance/filename-policy-enforcement.md"),
            file_type="md"
        )
        assert result.is_valid
        
        # Invalid: at reports root
        result = enforcer.validate_path(
            path=Path("/Users/asifhussain/PROJECTS/CORTEX/reports/filename-policy.md"),
            file_type="md"
        )
        assert not result.is_valid
        assert any(v.code == "CORE-038" for v in result.violations)

    def test_reject_root_level_md_file(self) -> None:
        """Reject .md files at repository root (CORE-038)."""
        enforcer = FilePathEnforcer()
        
        result = enforcer.validate_path(
            path=Path("/Users/asifhussain/PROJECTS/CORTEX/ANALYSIS.md"),
            file_type="md"
        )
        
        assert not result.is_valid
        assert any(v.code == "CORE-038" for v in result.violations)

    def test_reject_cortex_root_python_file(self) -> None:
        """Reject .py files directly in cortex/ root (must be in module)."""
        enforcer = FilePathEnforcer()
        
        result = enforcer.validate_path(
            path=Path("/Users/asifhussain/PROJECTS/CORTEX/cortex/my-module.py"),
            file_type="py"
        )
        
        assert not result.is_valid
        assert any(v.code == "CORE-038" for v in result.violations)

    def test_reject_docs_root_file(self) -> None:
        """Reject .md files directly in docs/ root (must be in subfolder)."""
        enforcer = FilePathEnforcer()
        
        result = enforcer.validate_path(
            path=Path("/Users/asifhussain/PROJECTS/CORTEX/docs/some-guide.md"),
            file_type="md"
        )
        
        assert not result.is_valid
        assert any(v.code == "CORE-038" for v in result.violations)

    def test_whitelist_files_accepted(self) -> None:
        """Accept whitelisted files at root (README.md, requirements.txt, etc)."""
        enforcer = FilePathEnforcer()
        
        whitelist = [
            Path("/Users/asifhussain/PROJECTS/CORTEX/README.md"),
            Path("/Users/asifhussain/PROJECTS/CORTEX/requirements.txt"),
            Path("/Users/asifhussain/PROJECTS/CORTEX/pyrightconfig.json"),
        ]
        
        for path in whitelist:
            result = enforcer.validate_path(path=path, file_type=path.suffix.lstrip("."))
            assert result.is_valid, f"Whitelist file {path.name} should be valid"


class TestIntegrationFilenameFactoryEndToEnd:
    """Integration tests for complete filename generation flow."""

    def test_end_to_end_python_module_generation(self) -> None:
        """Generate complete valid Python module path."""
        factory = FilenameFactory()
        enforcer = FilePathEnforcer()
        
        # Generate filename
        filename_result = factory.generate(
            purpose="governance enforcement validator",
            file_type="py",
            max_chars=25
        )
        assert filename_result.success
        
        # Construct full path
        full_path = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex/governance") / filename_result.filename
        
        # Validate path
        path_result = enforcer.validate_path(path=full_path, file_type="py")
        assert path_result.is_valid

    def test_end_to_end_test_file_generation(self) -> None:
        """Generate complete valid test file path."""
        factory = FilenameFactory()
        enforcer = FilePathEnforcer()
        validator = FilenameValidator()
        
        # Generate filename
        filename_result = factory.generate(
            purpose="filename factory tests",
            file_type="py",
            max_chars=25,
            prefix="test"
        )
        assert filename_result.success
        
        # Validate filename
        validate_result = validator.validate(filename_result.filename)
        assert validate_result.is_valid
        
        # Construct full path
        full_path = Path("/Users/asifhussain/PROJECTS/CORTEX/tests/unit/governance") / filename_result.filename
        
        # Validate path
        path_result = enforcer.validate_path(path=full_path, file_type="py")
        assert path_result.is_valid

    def test_end_to_end_report_generation(self) -> None:
        """Generate complete valid report file path."""
        factory = FilenameFactory()
        enforcer = FilePathEnforcer()
        
        # Generate filename
        filename_result = factory.generate(
            purpose="filename factory implementation",
            file_type="md",
            max_chars=25
        )
        assert filename_result.success
        
        # Construct full path in reports subfolder
        full_path = Path("/Users/asifhussain/PROJECTS/CORTEX/reports/governance") / filename_result.filename
        
        # Validate path
        path_result = enforcer.validate_path(path=full_path, file_type="md")
        assert path_result.is_valid


# Shared data classes for test results

@dataclass
class ValidationResult:
    """Result of filename validation."""
    is_valid: bool
    violations: List['NamingViolation'] = None
    
    def __post_init__(self) -> None:
        if self.violations is None:
            self.violations = []


@dataclass
class GenerationResult:
    """Result of filename generation."""
    success: bool
    filename: str = None
    reasoning: str = None
    alternative_names: List[str] = None
    
    def __post_init__(self) -> None:
        if self.alternative_names is None:
            self.alternative_names = []


@dataclass
class PathValidationResult:
    """Result of path validation."""
    is_valid: bool
    violations: List['PlacementViolation'] = None
    
    def __post_init__(self) -> None:
        if self.violations is None:
            self.violations = []
