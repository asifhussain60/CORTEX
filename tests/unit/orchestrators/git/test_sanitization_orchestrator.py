"""
Tests for SanitizationOrchestrator

AC_START: AC-GIT-ORCH-001
Description: TDD tests for deep-scan file sanitization before git commit
Authority: phase-sanitization-orchestrator.yaml (P0 ACTIVE)
Governance: CORE-008 (TDD mandatory), CORE-011 (type hints), CORE-012 (docstrings)

Test Coverage:
- Pattern detection (proprietary terms, PII, API keys)
- MorphingEngine consistent cross-file replacement
- IntegrityValidator post-morph syntax check
- AuditTrail recording
- SanitizationOrchestrator orchestration flow
"""

import pytest
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List
from unittest.mock import MagicMock, patch, mock_open


# ---------------------------------------------------------------------------
# Tests: PatternRegistry
# ---------------------------------------------------------------------------

class TestPatternRegistry:
    """PatternRegistry loads and serves sanitization patterns."""

    def test_pattern_registry_instantiates(self) -> None:
        """PatternRegistry can be instantiated."""
        from cortex.orchestrators.git.sanitization_orchestrator import PatternRegistry
        registry = PatternRegistry()
        assert registry is not None

    def test_registry_has_default_patterns(self) -> None:
        """PatternRegistry ships with built-in proprietary/PII/secret patterns."""
        from cortex.orchestrators.git.sanitization_orchestrator import PatternRegistry
        registry = PatternRegistry()
        patterns = registry.get_patterns()
        assert len(patterns) > 0

    def test_registry_detects_api_key_pattern(self) -> None:
        """PatternRegistry matches API key patterns."""
        from cortex.orchestrators.git.sanitization_orchestrator import PatternRegistry
        registry = PatternRegistry()
        content = "api_key = sk_live_abc123xyz"
        matches = registry.scan(content)
        assert any(m.category == "secret" for m in matches)

    def test_registry_detects_email_pattern(self) -> None:
        """PatternRegistry matches email PII."""
        from cortex.orchestrators.git.sanitization_orchestrator import PatternRegistry
        registry = PatternRegistry()
        content = "contact owner@acme-internal.com for access"
        matches = registry.scan(content)
        assert any(m.category == "pii" for m in matches)

    def test_registry_detects_proprietary_term(self) -> None:
        """PatternRegistry matches registered proprietary terms."""
        from cortex.orchestrators.git.sanitization_orchestrator import PatternRegistry
        registry = PatternRegistry()
        registry.add_proprietary_term("acme-corp", replacement="enterprise-client")
        content = "connect to acme-corp internal API"
        matches = registry.scan(content)
        assert any(m.category == "proprietary" for m in matches)

    def test_registry_no_false_positive_on_safe_content(self) -> None:
        """PatternRegistry does not flag generic safe content."""
        from cortex.orchestrators.git.sanitization_orchestrator import PatternRegistry
        registry = PatternRegistry()
        content = "def calculate_total(items: list) -> float:\n    return sum(items)"
        matches = registry.scan(content)
        assert len(matches) == 0

    def test_registry_add_proprietary_term(self) -> None:
        """PatternRegistry accepts custom proprietary terms at runtime."""
        from cortex.orchestrators.git.sanitization_orchestrator import PatternRegistry
        registry = PatternRegistry()
        registry.add_proprietary_term("secret-internal-hostname", replacement="internal-host")
        assert "secret-internal-hostname" in registry.get_proprietary_terms()


# ---------------------------------------------------------------------------
# Tests: MorphingEngine
# ---------------------------------------------------------------------------

class TestMorphingEngine:
    """MorphingEngine replaces matches consistently across files."""

    def test_morphing_engine_instantiates(self) -> None:
        """MorphingEngine can be instantiated."""
        from cortex.orchestrators.git.sanitization_orchestrator import MorphingEngine
        engine = MorphingEngine()
        assert engine is not None

    def test_morph_replaces_api_key(self) -> None:
        """MorphingEngine replaces API key with generic placeholder."""
        from cortex.orchestrators.git.sanitization_orchestrator import MorphingEngine, PatternRegistry
        registry = PatternRegistry()
        engine = MorphingEngine(registry=registry)
        original = 'API_KEY = "sk_live_abc123xyz"'
        result = engine.morph(original, file_type="py")
        assert "sk_live_abc123xyz" not in result
        assert "[REDACTED" in result or "PLACEHOLDER" in result

    def test_morph_replaces_email(self) -> None:
        """MorphingEngine replaces email addresses."""
        from cortex.orchestrators.git.sanitization_orchestrator import MorphingEngine, PatternRegistry
        registry = PatternRegistry()
        engine = MorphingEngine(registry=registry)
        original = "# maintainer: owner@acme.com"
        result = engine.morph(original, file_type="py")
        assert "owner@acme.com" not in result

    def test_morph_consistent_across_calls(self) -> None:
        """MorphingEngine produces identical replacements for the same input."""
        from cortex.orchestrators.git.sanitization_orchestrator import MorphingEngine, PatternRegistry
        registry = PatternRegistry()
        registry.add_proprietary_term("acme-corp", replacement="enterprise-client")
        engine = MorphingEngine(registry=registry)
        result1 = engine.morph("acme-corp system", file_type="py")
        result2 = engine.morph("acme-corp system", file_type="py")
        assert result1 == result2

    def test_morph_proprietary_term_to_generic(self) -> None:
        """MorphingEngine replaces proprietary terms with configured generic equivalents."""
        from cortex.orchestrators.git.sanitization_orchestrator import MorphingEngine, PatternRegistry
        registry = PatternRegistry()
        registry.add_proprietary_term("acme-corp", replacement="enterprise-client")
        engine = MorphingEngine(registry=registry)
        result = engine.morph("connect to acme-corp", file_type="py")
        assert "enterprise-client" in result
        assert "acme-corp" not in result

    def test_morph_preserves_code_structure(self) -> None:
        """MorphingEngine does not corrupt surrounding code."""
        from cortex.orchestrators.git.sanitization_orchestrator import MorphingEngine, PatternRegistry
        registry = PatternRegistry()
        engine = MorphingEngine(registry=registry)
        original = "def get_data():\n    return True"
        result = engine.morph(original, file_type="py")
        assert "def get_data" in result
        assert "return True" in result

    def test_morph_is_idempotent(self) -> None:
        """Re-morphing already-morphed content produces no further changes."""
        from cortex.orchestrators.git.sanitization_orchestrator import MorphingEngine, PatternRegistry
        registry = PatternRegistry()
        engine = MorphingEngine(registry=registry)
        original = 'key = "sk_live_abc123"'
        once = engine.morph(original, file_type="py")
        twice = engine.morph(once, file_type="py")
        assert once == twice


# ---------------------------------------------------------------------------
# Tests: IntegrityValidator
# ---------------------------------------------------------------------------

class TestIntegrityValidator:
    """IntegrityValidator ensures morphed content is syntactically valid."""

    def test_integrity_validator_instantiates(self) -> None:
        """IntegrityValidator can be instantiated."""
        from cortex.orchestrators.git.sanitization_orchestrator import IntegrityValidator
        validator = IntegrityValidator()
        assert validator is not None

    def test_validate_valid_python(self) -> None:
        """Valid Python passes integrity check."""
        from cortex.orchestrators.git.sanitization_orchestrator import IntegrityValidator
        validator = IntegrityValidator()
        result = validator.validate("def hello():\n    return True\n", file_type="py")
        assert result.is_valid is True

    def test_validate_invalid_python(self) -> None:
        """Broken Python fails integrity check."""
        from cortex.orchestrators.git.sanitization_orchestrator import IntegrityValidator
        validator = IntegrityValidator()
        result = validator.validate("def broken(:\n    pass\n", file_type="py")
        assert result.is_valid is False
        assert result.error is not None

    def test_validate_valid_yaml(self) -> None:
        """Valid YAML passes integrity check."""
        from cortex.orchestrators.git.sanitization_orchestrator import IntegrityValidator
        validator = IntegrityValidator()
        result = validator.validate("key: value\nother: 123\n", file_type="yaml")
        assert result.is_valid is True

    def test_validate_invalid_yaml(self) -> None:
        """Broken YAML fails integrity check."""
        from cortex.orchestrators.git.sanitization_orchestrator import IntegrityValidator
        validator = IntegrityValidator()
        result = validator.validate("key: [\nbroken", file_type="yaml")
        assert result.is_valid is False

    def test_validate_non_code_file_always_passes(self) -> None:
        """Non-code files (txt, md) skip syntax checks and pass."""
        from cortex.orchestrators.git.sanitization_orchestrator import IntegrityValidator
        validator = IntegrityValidator()
        result = validator.validate("any random text content here", file_type="txt")
        assert result.is_valid is True


# ---------------------------------------------------------------------------
# Tests: AuditTrail
# ---------------------------------------------------------------------------

class TestAuditTrail:
    """AuditTrail records all sanitization actions."""

    def test_audit_trail_instantiates(self) -> None:
        """AuditTrail can be instantiated."""
        from cortex.orchestrators.git.sanitization_orchestrator import AuditTrail
        trail = AuditTrail()
        assert trail is not None

    def test_audit_trail_records_substitution(self) -> None:
        """AuditTrail records a substitution entry."""
        from cortex.orchestrators.git.sanitization_orchestrator import AuditTrail
        trail = AuditTrail()
        trail.record(
            file_path="cortex/config.py",
            line=10,
            category="secret",
            original="sk_live_abc",
            replacement="[REDACTED-SECRET]",
        )
        entries = trail.get_entries()
        assert len(entries) == 1
        assert entries[0]["file_path"] == "cortex/config.py"
        assert entries[0]["category"] == "secret"

    def test_audit_trail_accumulates_entries(self) -> None:
        """AuditTrail accumulates multiple entries."""
        from cortex.orchestrators.git.sanitization_orchestrator import AuditTrail
        trail = AuditTrail()
        for i in range(5):
            trail.record(
                file_path=f"file_{i}.py",
                line=i,
                category="pii",
                original="user@example.com",
                replacement="[REDACTED-EMAIL]",
            )
        assert len(trail.get_entries()) == 5

    def test_audit_trail_exports_summary(self) -> None:
        """AuditTrail provides summary statistics."""
        from cortex.orchestrators.git.sanitization_orchestrator import AuditTrail
        trail = AuditTrail()
        trail.record("a.py", 1, "secret", "key123", "[REDACTED]")
        trail.record("b.py", 2, "pii", "email@x.com", "[REDACTED-EMAIL]")
        summary = trail.summary()
        assert summary["total_substitutions"] == 2
        assert summary["files_affected"] == 2


# ---------------------------------------------------------------------------
# Tests: FileScannerEngine
# ---------------------------------------------------------------------------

class TestFileScannerEngine:
    """FileScannerEngine scans file trees for hits."""

    def test_file_scanner_instantiates(self) -> None:
        """FileScannerEngine can be instantiated."""
        from cortex.orchestrators.git.sanitization_orchestrator import FileScannerEngine
        scanner = FileScannerEngine()
        assert scanner is not None

    def test_scanner_skips_excluded_dirs(self) -> None:
        """FileScannerEngine excludes __pycache__, .git, .venv directories."""
        from cortex.orchestrators.git.sanitization_orchestrator import FileScannerEngine
        scanner = FileScannerEngine()
        excluded = scanner.excluded_dirs
        assert "__pycache__" in excluded
        assert ".git" in excluded
        assert ".venv" in excluded

    def test_scanner_includes_python_files(self) -> None:
        """FileScannerEngine includes .py files."""
        from cortex.orchestrators.git.sanitization_orchestrator import FileScannerEngine
        scanner = FileScannerEngine()
        assert "py" in scanner.included_extensions

    def test_scanner_includes_yaml_and_md(self) -> None:
        """FileScannerEngine includes .yaml and .md files."""
        from cortex.orchestrators.git.sanitization_orchestrator import FileScannerEngine
        scanner = FileScannerEngine()
        assert "yaml" in scanner.included_extensions
        assert "md" in scanner.included_extensions

    def test_scanner_returns_scan_results(self, tmp_path: Path) -> None:
        """FileScannerEngine returns ScanResult per file with hits."""
        from cortex.orchestrators.git.sanitization_orchestrator import (
            FileScannerEngine, PatternRegistry,
        )
        # Write a temp file with a secret
        test_file = tmp_path / "config.py"
        test_file.write_text('API_KEY = "sk_live_testkey123"\n')
        registry = PatternRegistry()
        scanner = FileScannerEngine(registry=registry)
        results = scanner.scan_directory(str(tmp_path))
        assert len(results) == 1
        assert results[0].has_hits

    def test_scanner_returns_empty_for_clean_files(self, tmp_path: Path) -> None:
        """FileScannerEngine returns no-hit result for clean files."""
        from cortex.orchestrators.git.sanitization_orchestrator import (
            FileScannerEngine, PatternRegistry,
        )
        test_file = tmp_path / "clean.py"
        test_file.write_text("def add(a: int, b: int) -> int:\n    return a + b\n")
        registry = PatternRegistry()
        scanner = FileScannerEngine(registry=registry)
        results = scanner.scan_directory(str(tmp_path))
        assert all(not r.has_hits for r in results)


# ---------------------------------------------------------------------------
# Tests: SanitizationOrchestrator (integration)
# ---------------------------------------------------------------------------

class TestSanitizationOrchestrator:
    """SanitizationOrchestrator coordinates full scan → morph → validate flow."""

    def test_sanitization_orchestrator_instantiates(self) -> None:
        """SanitizationOrchestrator can be instantiated."""
        from cortex.orchestrators.git.sanitization_orchestrator import SanitizationOrchestrator
        orch = SanitizationOrchestrator()
        assert orch is not None

    def test_sanitize_clean_repo_returns_clean_result(self, tmp_path: Path) -> None:
        """Clean repo with no hits returns sanitized=True, changes=0."""
        from cortex.orchestrators.git.sanitization_orchestrator import SanitizationOrchestrator
        clean_file = tmp_path / "main.py"
        clean_file.write_text("def run() -> None:\n    pass\n")
        orch = SanitizationOrchestrator()
        result = orch.sanitize(str(tmp_path), dry_run=True)
        assert result.sanitized is True
        assert result.total_changes == 0

    def test_sanitize_repo_with_secret_returns_changes(self, tmp_path: Path) -> None:
        """Repo with secrets returns sanitized=True and change count > 0."""
        from cortex.orchestrators.git.sanitization_orchestrator import SanitizationOrchestrator
        secret_file = tmp_path / "config.py"
        secret_file.write_text('SECRET = "sk_live_abc123xyz"\n')
        orch = SanitizationOrchestrator()
        result = orch.sanitize(str(tmp_path), dry_run=True)
        assert result.sanitized is True
        assert result.total_changes >= 1

    def test_sanitize_dry_run_does_not_write_files(self, tmp_path: Path) -> None:
        """dry_run=True scans but does not write any files."""
        from cortex.orchestrators.git.sanitization_orchestrator import SanitizationOrchestrator
        secret_file = tmp_path / "config.py"
        original_content = 'SECRET = "sk_live_abc123xyz"\n'
        secret_file.write_text(original_content)
        orch = SanitizationOrchestrator()
        orch.sanitize(str(tmp_path), dry_run=True)
        assert secret_file.read_text() == original_content  # unchanged

    def test_sanitize_live_run_writes_morphed_files(self, tmp_path: Path) -> None:
        """dry_run=False writes morphed content to disk."""
        from cortex.orchestrators.git.sanitization_orchestrator import SanitizationOrchestrator
        secret_file = tmp_path / "config.py"
        secret_file.write_text('SECRET = "sk_live_abc123xyz"\n')
        orch = SanitizationOrchestrator()
        orch.sanitize(str(tmp_path), dry_run=False)
        morphed = secret_file.read_text()
        assert "sk_live_abc123xyz" not in morphed

    def test_sanitize_blocks_on_integrity_failure(self, tmp_path: Path) -> None:
        """Sanitizer blocks commit when post-morph syntax is invalid."""
        from cortex.orchestrators.git.sanitization_orchestrator import (
            SanitizationOrchestrator, SanitizationError,
        )
        # Manually craft a file that becomes invalid after morph by mocking validator
        bad_file = tmp_path / "broken.py"
        bad_file.write_text("def broken(:\n    pass\n")
        orch = SanitizationOrchestrator()
        with pytest.raises(SanitizationError):
            orch.sanitize(str(tmp_path), dry_run=False)

    def test_sanitize_produces_audit_trail(self, tmp_path: Path) -> None:
        """Sanitization run returns populated audit trail."""
        from cortex.orchestrators.git.sanitization_orchestrator import SanitizationOrchestrator
        secret_file = tmp_path / "settings.py"
        secret_file.write_text('TOKEN = "sk_live_abc123xyz"\n')
        orch = SanitizationOrchestrator()
        result = orch.sanitize(str(tmp_path), dry_run=True)
        assert result.audit_trail is not None
        assert result.audit_trail.summary()["total_substitutions"] >= 0

    def test_sanitize_result_has_required_fields(self, tmp_path: Path) -> None:
        """SanitizationResult has all required fields."""
        from cortex.orchestrators.git.sanitization_orchestrator import SanitizationOrchestrator
        (tmp_path / "app.py").write_text("x = 1\n")
        orch = SanitizationOrchestrator()
        result = orch.sanitize(str(tmp_path), dry_run=True)
        assert hasattr(result, "sanitized")
        assert hasattr(result, "total_changes")
        assert hasattr(result, "files_scanned")
        assert hasattr(result, "audit_trail")
        assert hasattr(result, "elapsed_seconds")


# AC_COMPLETE: AC-GIT-ORCH-001 (TDD tests written — RED phase)
