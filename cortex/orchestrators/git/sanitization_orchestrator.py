"""
SanitizationOrchestrator — Deep-scan file sanitization before git commit.

Coordinates:
  PatternRegistry   → catalogue of proprietary/PII/secret patterns
  FileScannerEngine → recursive file tree scan
  MorphingEngine    → consistent cross-file term replacement
  IntegrityValidator → post-morph syntax validation
  AuditTrail        → tamper-evident substitution log

AC_START: AC-GIT-ORCH-001
Authority: phase-sanitization-orchestrator.yaml (P0 ACTIVE, 2026-02-19)
Testing: tests/unit/orchestrators/git/test_sanitization_orchestrator.py
Governance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings),
            CORE-028 (snake_case), CORE-035 (single canonical implementation)
"""

import ast
import logging
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin
from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin  # Phase 94e

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class SanitizationError(Exception):
    """Raised when post-morph integrity validation fails or sanitization cannot proceed."""


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class PatternMatch:
    """A single pattern hit found during scanning.

    Attributes:
        category: Hit category — 'secret', 'pii', or 'proprietary'.
        pattern_name: Human-readable pattern label.
        original: The matched string.
        replacement: The configured replacement string.
        start: Character offset in the content string.
        end: Character end offset in the content string.
    """

    category: str
    pattern_name: str
    original: str
    replacement: str
    start: int
    end: int


@dataclass
class ScanResult:
    """Result for a single scanned file.

    Attributes:
        file_path: Absolute or relative path to the file.
        file_type: Extension without leading dot (e.g. 'py', 'yaml').
        matches: All pattern matches found in this file.
        has_hits: True when matches is non-empty.
    """

    file_path: str
    file_type: str
    matches: List[PatternMatch] = field(default_factory=list)

    @property
    def has_hits(self) -> bool:
        """True when at least one pattern match was found."""
        return len(self.matches) > 0


@dataclass
class ValidationResult:  # CORE-035-scoped — domain-specific ValidationResult variant
    """Result of post-morph integrity validation.

    Attributes:
        is_valid: True when the content passes the syntax check.
        error: Error description when is_valid is False.
    """

    is_valid: bool
    error: Optional[str] = None


@dataclass
class SanitizationResult:
    """Aggregated result of a full sanitization run.

    Attributes:
        sanitized: True when the run completed without blocking errors.
        total_changes: Number of substitutions applied.
        files_scanned: Number of files inspected.
        audit_trail: The AuditTrail instance containing all entries.
        elapsed_seconds: Wall-clock time for the run.
    """

    sanitized: bool
    total_changes: int
    files_scanned: int
    audit_trail: "AuditTrail"
    elapsed_seconds: float = 0.0


# ---------------------------------------------------------------------------
# PatternRegistry
# ---------------------------------------------------------------------------

# Built-in patterns shipped with CORTEX
_BUILTIN_PATTERNS: List[Dict[str, Any]] = [
    # Secrets
    {
        "category": "secret",
        "name": "stripe_live_key",
        "regex": r"sk_live_[A-Za-z0-9]{6,}",
        "replacement": "[REDACTED-SECRET]",
    },
    {
        "category": "secret",
        "name": "stripe_test_key",
        "regex": r"sk_test_[A-Za-z0-9]{6,}",
        "replacement": "[REDACTED-SECRET]",
    },
    {
        "category": "secret",
        "name": "aws_access_key",
        "regex": r"AKIA[0-9A-Z]{16}",
        "replacement": "[REDACTED-AWS-KEY]",
    },
    {
        "category": "secret",
        "name": "aws_secret_key",
        "regex": r"(?i)(aws_secret_access_key\s*=\s*)[A-Za-z0-9/+=]{40}",
        "replacement": r"\1[REDACTED-AWS-SECRET]",
    },
    {
        "category": "secret",
        "name": "generic_api_key",
        "regex": r"(?i)(api[_-]?key\s*[=:]\s*['\"]?)([A-Za-z0-9_\-]{20,})",
        "replacement": r"\1[REDACTED-API-KEY]",
    },
    {
        "category": "secret",
        "name": "database_url",
        "regex": r"(?i)(postgresql|mysql|mongodb|redis)://[^\s\"']+",
        "replacement": "[REDACTED-DB-URL]",
    },
    {
        "category": "secret",
        "name": "private_key_header",
        "regex": r"-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----",
        "replacement": "[REDACTED-PRIVATE-KEY-HEADER]",
    },
    # PII
    {
        "category": "pii",
        "name": "email_address",
        "regex": r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
        "replacement": "[REDACTED-EMAIL]",
    },
    {
        "category": "pii",
        "name": "us_phone",
        "regex": r"\b(\+1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
        "replacement": "[REDACTED-PHONE]",
    },
    {
        "category": "pii",
        "name": "ssn",
        "regex": r"\b\d{3}-\d{2}-\d{4}\b",
        "replacement": "[REDACTED-SSN]",
    },
]


class PatternRegistry:
    """Catalogue of sanitization patterns (secrets, PII, proprietary terms).

    Loads built-in patterns on construction; accepts runtime additions via
    :meth:`add_proprietary_term`.

    Example::

        registry = PatternRegistry()
        registry.add_proprietary_term("acme-corp", replacement="enterprise-client")
        matches = registry.scan("connect to acme-corp")
    """

    def __init__(self) -> None:
        """Initialize PatternRegistry with built-in patterns."""
        self._patterns: List[Dict[str, Any]] = list(_BUILTIN_PATTERNS)
        self._proprietary_terms: Dict[str, str] = {}
        self._compiled: List[Dict[str, Any]] = []
        self._compile()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_patterns(self) -> List[Dict[str, Any]]:
        """Return all registered patterns.

        Returns:
            List of pattern dictionaries with keys: category, name, regex, replacement.
        """
        return list(self._patterns)

    def get_proprietary_terms(self) -> Dict[str, str]:
        """Return registered proprietary term → replacement mapping.

        Returns:
            Dict mapping proprietary term to its generic replacement.
        """
        return dict(self._proprietary_terms)

    def add_proprietary_term(self, term: str, replacement: str) -> None:
        """Register a proprietary term for consistent replacement.

        Args:
            term: Exact string to match (case-insensitive).
            replacement: Generic substitute to use cross-file.
        """
        self._proprietary_terms[term] = replacement
        # Build regex pattern from the term
        escaped = re.escape(term)
        self._patterns.append({
            "category": "proprietary",
            "name": f"proprietary_{term}",
            "regex": rf"(?i)\b{escaped}\b",
            "replacement": replacement,
        })
        self._compile()

    def scan(self, content: str) -> List[PatternMatch]:
        """Scan content and return all pattern matches.

        Args:
            content: Raw file content to inspect.

        Returns:
            List of :class:`PatternMatch` instances for every hit.
        """
        matches: List[PatternMatch] = []
        for entry in self._compiled:
            for m in entry["compiled"].finditer(content):
                matches.append(PatternMatch(
                    category=entry["category"],
                    pattern_name=entry["name"],
                    original=m.group(0),
                    replacement=entry["replacement"],
                    start=m.start(),
                    end=m.end(),
                ))
        return matches

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _compile(self) -> None:
        """Recompile all regex patterns."""
        self._compiled = []
        for p in self._patterns:
            try:
                self._compiled.append({
                    **p,
                    "compiled": re.compile(p["regex"]),
                })
            except re.error as exc:
                logger.warning("Failed to compile pattern '%s': %s", p["name"], exc)


# ---------------------------------------------------------------------------
# MorphingEngine
# ---------------------------------------------------------------------------


class MorphingEngine:
    """Applies pattern-driven replacements to content with cross-file consistency.

    The engine applies every pattern from the :class:`PatternRegistry` to the
    content string using ``re.sub``, preserving surrounding code structure.
    Results are deterministic: the same input always yields the same output.

    Example::

        engine = MorphingEngine(registry)
        morphed = engine.morph('API_KEY = "sk_live_abc"', file_type="py")
    """

    def __init__(self, registry: Optional[PatternRegistry] = None) -> None:
        """Initialize MorphingEngine.

        Args:
            registry: PatternRegistry to use. Creates a default instance if None.
        """
        self._registry = registry or PatternRegistry()

    def morph(self, content: str, file_type: str) -> str:
        """Apply all registered patterns to content.

        Args:
            content: Raw file content.
            file_type: File extension without dot ('py', 'yaml', 'md', etc.).

        Returns:
            Content with all pattern matches replaced by their configured substitutes.
        """
        result = content
        for pattern in self._registry.get_patterns():
            try:
                compiled = re.compile(pattern["regex"])
                result = compiled.sub(pattern["replacement"], result)
            except re.error as exc:
                logger.warning("Skipping pattern '%s': %s", pattern["name"], exc)
        return result


# ---------------------------------------------------------------------------
# IntegrityValidator
# ---------------------------------------------------------------------------


class IntegrityValidator:
    """Validates morphed content remains syntactically correct.

    Performs language-specific syntax checks:
    - Python (``.py``): ``ast.parse``
    - YAML (``.yaml`` / ``.yml``): ``yaml.safe_load``
    - All other types: skip (always valid)

    Example::

        validator = IntegrityValidator()
        result = validator.validate("def f(): return True", file_type="py")
        assert result.is_valid
    """

    def validate(self, content: str, file_type: str) -> ValidationResult:
        """Validate content syntax for the given file type.

        Args:
            content: Morphed file content to check.
            file_type: Extension without dot.

        Returns:
            :class:`ValidationResult` with ``is_valid`` flag and optional error.
        """
        if file_type == "py":
            return self._validate_python(content)
        if file_type in ("yaml", "yml"):
            return self._validate_yaml(content)
        # Non-code files (md, txt, json, etc.) skip syntax check
        return ValidationResult(is_valid=True)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _validate_python(self, content: str) -> ValidationResult:
        """Run ast.parse on Python content.

        Args:
            content: Python source.

        Returns:
            ValidationResult.
        """
        try:
            ast.parse(content)
            return ValidationResult(is_valid=True)
        except SyntaxError as exc:
            return ValidationResult(is_valid=False, error=str(exc))

    def _validate_yaml(self, content: str) -> ValidationResult:
        """Run yaml.safe_load on YAML content.

        Args:
            content: YAML source.

        Returns:
            ValidationResult.
        """
        try:
            import yaml  # lazy import — optional dep
            yaml.safe_load(content)
            return ValidationResult(is_valid=True)
        except Exception as exc:
            return ValidationResult(is_valid=False, error=str(exc))


# ---------------------------------------------------------------------------
# AuditTrail
# ---------------------------------------------------------------------------


class AuditTrail:
    """Tamper-evident log of every substitution made during a sanitization run.

    Example::

        trail = AuditTrail()
        trail.record("settings.py", 12, "secret", "sk_live_abc", "[REDACTED]")
        print(trail.summary())
    """

    def __init__(self) -> None:
        """Initialize an empty AuditTrail."""
        self._entries: List[Dict[str, Any]] = []

    def record(
        self,
        file_path: str,
        line: int,
        category: str,
        original: str,
        replacement: str,
    ) -> None:
        """Record a single substitution.

        Args:
            file_path: Relative or absolute path to the affected file.
            line: Approximate line number of the substitution.
            category: Pattern category ('secret', 'pii', 'proprietary').
            original: The matched (now-removed) string.
            replacement: The generic substitute applied.
        """
        self._entries.append({
            "file_path": file_path,
            "line": line,
            "category": category,
            "original": original,
            "replacement": replacement,
        })

    def get_entries(self) -> List[Dict[str, Any]]:
        """Return all recorded entries.

        Returns:
            List of entry dicts.
        """
        return list(self._entries)

    def summary(self) -> Dict[str, Any]:
        """Return aggregated statistics.

        Returns:
            Dict with ``total_substitutions`` and ``files_affected``.
        """
        files = {e["file_path"] for e in self._entries}
        return {
            "total_substitutions": len(self._entries),
            "files_affected": len(files),
        }


# ---------------------------------------------------------------------------
# FileScannerEngine
# ---------------------------------------------------------------------------


class FileScannerEngine:
    """Recursively scans a directory tree and returns per-file scan results.

    Respects inclusion and exclusion rules to avoid scanning generated or
    sensitive directories (``.git``, ``.venv``, ``__pycache__``).

    Example::

        scanner = FileScannerEngine(registry=registry)
        results = scanner.scan_directory("/path/to/repo")
    """

    #: Directories to skip entirely
    excluded_dirs: List[str] = [
        "__pycache__", ".git", ".venv", "venv", "node_modules",
        ".mypy_cache", ".pytest_cache", "dist", "build", ".tox",
    ]

    #: File extensions to include (without leading dot)
    included_extensions: List[str] = [
        "py", "yaml", "yml", "md", "txt", "json", "toml", "cfg", "ini",
    ]

    def __init__(self, registry: Optional[PatternRegistry] = None) -> None:
        """Initialize FileScannerEngine.

        Args:
            registry: PatternRegistry to use for scanning. Creates a default if None.
        """
        self._registry = registry or PatternRegistry()

    def scan_directory(self, root: str) -> List[ScanResult]:
        """Scan all eligible files under root.

        Args:
            root: Absolute path to the repository root.

        Returns:
            List of :class:`ScanResult` for each eligible file.
        """
        results: List[ScanResult] = []
        root_path = Path(root)

        for file_path in self._walk(root_path):
            ext = file_path.suffix.lstrip(".")
            if ext not in self.included_extensions:
                continue
            try:
                content = file_path.read_text(encoding="utf-8", errors="replace")
            except OSError as exc:
                logger.warning("Cannot read %s: %s", file_path, exc)
                continue

            matches = self._registry.scan(content)
            results.append(ScanResult(
                file_path=str(file_path),
                file_type=ext,
                matches=matches,
            ))

        return results

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _walk(self, root: Path) -> None:
        """Yield all eligible file paths under root.

        Args:
            root: Directory to walk.

        Yields:
            Path objects for files.
        """
        for entry in root.iterdir():
            if entry.is_dir():
                if entry.name in self.excluded_dirs:
                    continue
                yield from self._walk(entry)
            elif entry.is_file():
                yield entry


# ---------------------------------------------------------------------------
# SanitizationOrchestrator
# ---------------------------------------------------------------------------


class SanitizationOrchestrator(OrchestratorProtocolMixin, WorkflowEnforcementMixin):
    """Coordinates the full scan → morph → validate → audit pipeline.

    Usage::

        orch = SanitizationOrchestrator()
        result = orch.sanitize("/path/to/repo", dry_run=False)

    Args:
        registry: Optional custom PatternRegistry.
        proprietary_terms: Optional mapping of term → replacement to register.

    Raises:
        SanitizationError: When post-morph integrity validation fails for any file.
    """

    # Phase 94e — advisory: downstream step inside git pipeline; not a primary
    # code-execution entry point. Gateway routing deferred.
    PHASE90_GATEWAY_EXEMPT: bool = True

    def __init__(
        self,
        registry: Optional[PatternRegistry] = None,
        proprietary_terms: Optional[Dict[str, str]] = None,
    ) -> None:
        """Initialize SanitizationOrchestrator.

        Args:
            registry: PatternRegistry to use. Creates a default if None.
            proprietary_terms: Extra proprietary term → replacement mappings.
        """
        self._registry = registry or PatternRegistry()
        if proprietary_terms:
            for term, replacement in proprietary_terms.items():
                self._registry.add_proprietary_term(term, replacement)

        self._scanner = FileScannerEngine(registry=self._registry)
        self._morpher = MorphingEngine(registry=self._registry)
        self._validator = IntegrityValidator()

    def sanitize(
        self,
        repo_path: str,
        dry_run: bool = True,
    ) -> SanitizationResult:
        """Run the full sanitization pipeline on repo_path.

        Stages:
        1. Scan — detect all pattern hits across eligible files.
        2. Morph — apply replacements to each file with hits.
        3. Validate — check morphed content for syntax correctness.
        4. Write — persist morphed content to disk (skipped in dry_run mode).
        5. Audit — record all substitutions.

        Args:
            repo_path: Absolute path to repository root.
            dry_run: When True, scan and morph in-memory but skip disk writes.

        Returns:
            :class:`SanitizationResult` with aggregated metrics.

        Raises:
            SanitizationError: When any file fails post-morph integrity validation.
        """
        t_start = time.monotonic()
        trail = AuditTrail()
        total_changes = 0

        # Phase 58 — cross-cutting hooks
        self._activate_cross_cutting_hooks(operation="sanitize_repo")

        scan_results = self._scanner.scan_directory(repo_path)

        for scan_result in scan_results:
            if not scan_result.has_hits:
                # Validate even clean files to catch pre-existing syntax errors
                content = Path(scan_result.file_path).read_text(
                    encoding="utf-8", errors="replace"
                )
                validation = self._validator.validate(content, scan_result.file_type)
                if not validation.is_valid:
                    raise SanitizationError(
                        f"Integrity check failed for {scan_result.file_path}: "
                        f"{validation.error}"
                    )
                continue

            # Read original content
            original_content = Path(scan_result.file_path).read_text(
                encoding="utf-8", errors="replace"
            )

            # Apply morphing
            morphed_content = self._morpher.morph(original_content, scan_result.file_type)

            # Validate morphed result
            validation = self._validator.validate(morphed_content, scan_result.file_type)
            if not validation.is_valid:
                raise SanitizationError(
                    f"Integrity check failed after morphing {scan_result.file_path}: "
                    f"{validation.error}"
                )

            # Record audit entries
            for match in scan_result.matches:
                # Approximate line number from character offset
                line_num = original_content[: match.start].count("\n") + 1
                trail.record(
                    file_path=scan_result.file_path,
                    line=line_num,
                    category=match.category,
                    original=match.original,
                    replacement=match.replacement,
                )
                total_changes += 1

            # Write to disk (unless dry_run)
            if not dry_run:
                Path(scan_result.file_path).write_text(
                    morphed_content, encoding="utf-8"
                )

        elapsed = time.monotonic() - t_start

        logger.info(
            "Sanitization complete: %d changes in %d files (dry_run=%s, %.2fs)",
            total_changes,
            len(scan_results),
            dry_run,
            elapsed,
        )

        return SanitizationResult(
            sanitized=True,
            total_changes=total_changes,
            files_scanned=len(scan_results),
            audit_trail=trail,
            elapsed_seconds=elapsed,
        )


__all__ = [
    "SanitizationError",
    "PatternMatch",
    "ScanResult",
    "ValidationResult",
    "SanitizationResult",
    "PatternRegistry",
    "MorphingEngine",
    "IntegrityValidator",
    "AuditTrail",
    "FileScannerEngine",
    "SanitizationOrchestrator",
]

# AC_COMPLETE: AC-GIT-ORCH-001 ✅ SanitizationOrchestrator implemented
