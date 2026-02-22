"""
RefactoringOrchestrator - Unified API for all refactoring tool adapters.

AC_START: AC-PHASE24.6-002
Description: Orchestrator for coordinating all refactoring tool adapters
Authority: Phase 24.6 - Orchestration + MCP Exposure
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings), CORE-027 (audit)

Coordinates:
    - Adapter registration and discovery
    - Language-based routing
    - Unified refactoring API
    - Statistics and reporting

Integrates:
    - Python (Rope) - 11 operations
    - C# (Roslyn) - 8 operations
    - TypeScript/JavaScript - 5 operations
    Total: 24 operations across 3 languages
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Phase 51: Enhanced response template with semantic color coding
# REMOVED: ResponseTemplate import (deprecated, unused - Phase 53 cleanup)
from cortex.core.result import Err, Ok
from cortex.orchestrators.domain.refactoring.adapters.adapter_base import RefactoringToolAdapter
from cortex.orchestrators.domain.refactoring.adapters.rope_adapter import RopeAdapter
from cortex.orchestrators.domain.refactoring.adapters.typescript_adapter import TypeScriptAdapter
from cortex.orchestrators.domain.refactoring.refactoring_models import (
    RefactoringLanguage,
    RefactoringRequest,
    RefactoringResult,
)
from cortex.orchestrators.domain.refactoring.refactoring_registry import RefactoringToolRegistry

logger = logging.getLogger(__name__)


class RefactoringOrchestrator:
    """Orchestrator for coordinating all refactoring tool adapters.

    Provides a unified API for executing refactoring operations across multiple
    programming languages. Automatically registers all available adapters and
    routes requests to the appropriate tool.

    Supported Languages:
        - Python (via Rope): 11 operations
        - C# (via Roslyn): 8 operations
        - TypeScript/JavaScript: 5 operations

    Features:
        - Automatic adapter discovery and registration
        - Language-based routing
        - Graceful degradation when tools unavailable
        - Statistics and status reporting
        - Full audit logging (CORE-027)

    Example:
        >>> orchestrator = RefactoringOrchestrator()
        >>>
        >>> # Get supported languages
        >>> languages = orchestrator.get_supported_languages()
        >>>
        >>> # Execute refactoring
        >>> request = RefactoringRequest(
        ...     operation="rename",
        ...     file_path=Path("app.py"),
        ...     language=RefactoringLanguage.PYTHON,
        ...     parameters={"offset": 100, "new_name": "process_data"}
        ... )
        >>> result = orchestrator.execute_refactoring(request)
    """

    def __init__(self) -> None:
        """Initialize RefactoringOrchestrator with all available adapters."""
        self.registry = RefactoringToolRegistry()
        self._registered_count = 0

        # Auto-register all available adapters
        self._register_adapters()

        logger.info(
            f"RefactoringOrchestrator initialized with {self._registered_count} adapters"
        )

    def _register_adapters(self) -> None:
        """Register all available refactoring tool adapters.

        Attempts to register:
            - RopeAdapter (Python)
            - RoslynAdapter (C#) - if available
            - TypeScriptAdapter (TypeScript/JavaScript)

        Gracefully handles registration failures.
        """
        adapters_to_register: List[RefactoringToolAdapter] = [
            RopeAdapter(),
            TypeScriptAdapter(),
        ]

        # Try to register RoslynAdapter (may not be imported in all environments)
        try:
            from cortex.orchestrators.domain.refactoring.adapters.roslyn_adapter import (
                RoslynAdapter,
            )
            adapters_to_register.append(RoslynAdapter())
        except ImportError:
            logger.debug("RoslynAdapter not available - skipping registration")

        for adapter in adapters_to_register:
            result = self.registry.register(adapter)
            if result.is_ok():
                self._registered_count += 1
            else:
                logger.warning(f"Failed to register adapter: {result.unwrap_err()}")

    def get_supported_languages(self) -> List[RefactoringLanguage]:
        """Get list of all supported languages (adapters registered).

        Returns:
            List of RefactoringLanguage enums for registered adapters
        """
        return self.registry.get_supported_languages()

    def get_available_languages(self) -> List[RefactoringLanguage]:
        """Get list of currently available languages (tools installed and accessible).

        Returns:
            List of RefactoringLanguage enums where adapter.is_available() is True
        """
        return self.registry.get_available_languages()

    def get_operations_for_language(
        self, language: RefactoringLanguage
    ) -> Union[Ok[List[str]], Err]:
        """Get supported operations for a specific language.

        Args:
            language: RefactoringLanguage to query

        Returns:
            Ok[List[str]] with operation names, or Err if language not supported
        """
        adapter_result = self.registry.get_adapter(language)

        if adapter_result.is_err():
            return adapter_result  # type: ignore

        adapter = adapter_result.unwrap()
        operations = adapter.get_supported_operations()

        return Ok(operations)

    def get_all_operations(self) -> Dict[RefactoringLanguage, List[str]]:
        """Get all operations for all supported languages.

        Returns:
            Dictionary mapping RefactoringLanguage to list of operation names
        """
        operations_map = {}

        for language in self.get_supported_languages():
            result = self.get_operations_for_language(language)
            if result.is_ok():
                operations_map[language] = result.unwrap()

        return operations_map

    def execute_refactoring(
        self, request: RefactoringRequest
    ) -> Union[Ok[RefactoringResult], Err]:
        """Execute a refactoring operation.

        Routes the request to the appropriate adapter based on language,
        executes the refactoring, and returns the result.

        Args:
            request: RefactoringRequest containing operation details

        Returns:
            Ok[RefactoringResult] if successful, Err with error message if failed

        Example:
            >>> request = RefactoringRequest(
            ...     operation="extract_function",
            ...     file_path=Path("app.py"),
            ...     language=RefactoringLanguage.PYTHON,
            ...     parameters={
            ...         "start_offset": 100,
            ...         "end_offset": 200,
            ...         "new_name": "helper"
            ...     }
            ... )
            >>> result = orchestrator.execute_refactoring(request)
        """
        # Map JavaScript to TypeScript adapter (since TypeScript handles both)
        language = request.language
        if language == RefactoringLanguage.JAVASCRIPT:
            language = RefactoringLanguage.TYPESCRIPT

        # Get adapter for language
        adapter_result = self.registry.get_adapter(language)

        if adapter_result.is_err():
            error_msg = adapter_result.unwrap_err()
            logger.error(f"Adapter retrieval failed: {error_msg}")
            return Err(error_msg)

        adapter = adapter_result.unwrap()

        # Log refactoring attempt
        logger.info(
            f"Executing {request.operation} on {request.file_path.name} "
            f"(language={request.language.value})"
        )

        # Execute refactoring
        result = adapter.execute_refactoring(request)

        # Log result
        if result.is_ok():
            refactoring_result = result.unwrap()
            logger.info(
                f"Refactoring succeeded: {refactoring_result.description} "
                f"(modified {len(refactoring_result.modified_files)} file(s))"
            )
        else:
            error_msg = result.unwrap_err()
            logger.error(f"Refactoring failed: {error_msg}")

        return result

    def get_adapter_status(self) -> Dict[RefactoringLanguage, Dict[str, Any]]:
        """Get status information for all registered adapters.

        Returns:
            Dictionary mapping language to status dict with:
                - available: bool (is tool installed and accessible)
                - operations_count: int (number of supported operations)
                - operations: List[str] (operation names)
        """
        status = {}

        for language in self.get_supported_languages():
            adapter_result = self.registry.get_adapter(language)

            if adapter_result.is_ok():
                adapter = adapter_result.unwrap()
                operations = adapter.get_supported_operations()

                status[language] = {
                    "available": adapter.is_available(),
                    "operations_count": len(operations),
                    "operations": operations,
                }

        return status

    def get_total_operations_count(self) -> int:
        """Get total number of operations across all languages.

        Returns:
            Total count of unique operations
        """
        all_operations = self.get_all_operations()

        # Count all operations (may include duplicates across languages)
        total = sum(len(ops) for ops in all_operations.values())

        return total

    # ------------------------------------------------------------------
    # ENH-STS-01 — Functional Completeness Gate
    # ------------------------------------------------------------------

    def check_functional_completeness(
        self,
        source_items: List[str],
        target_items: List[str],
    ) -> Union[Ok[Dict[str, Any]], Err]:
        """Verify that all source endpoints/functions are present in target.

        Prevents functional regression during refactoring — ensures no business
        capability is silently dropped without an ADR justification.

        Args:
            source_items: Endpoint or function names enumerated from source codebase.
            target_items: Endpoint or function names enumerated from target codebase.

        Returns:
            Ok with report dict: {gaps, gap_count, complete}
            Err on unexpected failure.
        """
        try:
            target_set = set(target_items)
            gaps = [item for item in source_items if item not in target_set]
            report: Dict[str, Any] = {
                "gaps": gaps,
                "gap_count": len(gaps),
                "complete": len(gaps) == 0,
                "source_count": len(source_items),
                "target_count": len(target_items),
            }
            if gaps:
                logger.warning(
                    f"Functional completeness gap: {len(gaps)} item(s) missing from target: {gaps}"
                )
            return Ok(report)
        except Exception as exc:
            logger.error(f"check_functional_completeness failed: {exc}")
            return Err(str(exc))

    # ------------------------------------------------------------------
    # ENH-STS-02 — Session Traceability
    # ------------------------------------------------------------------

    _VALID_TRACE_ACTIONS = frozenset({"AC_START", "AC_COMPLETE"})

    def write_refactor_session_trace(
        self,
        action: str,
        source_repo: str,
        target_repo: str,
        session_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Union[Ok[None], Err]:
        """Write a refactoring session boundary record to the audit trace DB.

        Implements ENH-STS-02: every REFACTOR session must emit AC_START at
        inception and AC_COMPLETE at conclusion so CORTEX can audit its own work.

        Args:
            action: "AC_START" or "AC_COMPLETE".
            source_repo: Relative path to the source codebase.
            target_repo: Relative path to the target (refactored) codebase.
            session_id: Unique ID shared between AC_START and AC_COMPLETE.
            metadata: Arbitrary key/value pairs (smells_catalogued, test_delta, etc.).

        Returns:
            Ok(None) on success, Err with reason on failure.
        """
        if action not in self._VALID_TRACE_ACTIONS:
            return Err(
                f"Invalid trace action '{action}'. Must be one of {sorted(self._VALID_TRACE_ACTIONS)}."
            )

        try:
            from cortex.infrastructure.orchestrator_trace_logger import (
                OrchestratorTraceLogger,
                TraceEntry,
                TraceLevel,
            )

            entry = TraceEntry(
                trace_id=str(uuid.uuid4()),
                timestamp=datetime.utcnow(),
                orchestrator_id="RefactoringOrchestrator",
                orchestrator_class="RefactoringOrchestrator",
                action=action,
                level=TraceLevel.ACTION,
                correlation_id=session_id,
                request_id=session_id,
                context={
                    "source_repo": source_repo,
                    "target_repo": target_repo,
                    "session_id": session_id,
                    **(metadata or {}),
                },
                result="OK",
            )

            logger_instance = OrchestratorTraceLogger()
            result = logger_instance.record_trace(entry)

            if result.is_ok():
                logger.info(
                    f"Refactor session trace written: action={action} session={session_id}"
                )
            else:
                logger.warning(f"Trace write returned non-Ok: {result.unwrap_err()}")

            return result
        except Exception as exc:
            logger.error(f"write_refactor_session_trace failed: {exc}")
            return Err(str(exc))

    # ------------------------------------------------------------------
    # ENH-STS-06 — Scorecard Generation
    # ------------------------------------------------------------------

    _SCORECARD_WEIGHTS: Dict[str, float] = {
        "architecture": 0.25,
        "security": 0.25,
        "testing": 0.20,
        "documentation": 0.15,
        "frontend": 0.10,
        "traceability": 0.05,
    }

    def generate_scorecard(
        self, scores: Dict[str, float]
    ) -> Union[Ok[Dict[str, Any]], Err]:
        """Generate a weighted refactoring quality scorecard.

        Implements ENH-STS-06: auto-produce a scored summary at REFACTOR
        completion so every session is immediately measurable.

        Args:
            scores: Dict mapping category name to a score 0–10.
                    Required keys: architecture, security, testing,
                    documentation, frontend, traceability.

        Returns:
            Ok with scorecard dict containing:
                categories, weighted_total (0–100), grade (A/B/C/D/F)
            Err if scores are invalid or categories are missing.
        """
        required = set(self._SCORECARD_WEIGHTS.keys())
        provided = set(scores.keys())

        missing = required - provided
        if missing:
            return Err(f"Missing required scorecard categories: {sorted(missing)}")

        for category, value in scores.items():
            if category in self._SCORECARD_WEIGHTS and not (0 <= value <= 10):
                return Err(
                    f"Score for '{category}' is {value} — must be in range 0–10."
                )

        weighted_sum = sum(
            scores[cat] * weight for cat, weight in self._SCORECARD_WEIGHTS.items()
        )
        weighted_total = round(weighted_sum * 10, 1)  # scale to 0–100

        if weighted_total >= 90:
            grade = "A"
        elif weighted_total >= 80:
            grade = "B"
        elif weighted_total >= 70:
            grade = "C"
        elif weighted_total >= 60:
            grade = "D"
        else:
            grade = "F"

        card: Dict[str, Any] = {
            "categories": {
                cat: {
                    "score": scores[cat],
                    "weight": self._SCORECARD_WEIGHTS[cat],
                    "weighted": round(scores[cat] * self._SCORECARD_WEIGHTS[cat] * 10, 2),
                }
                for cat in self._SCORECARD_WEIGHTS
            },
            "weighted_total": weighted_total,
            "grade": grade,
            "generated_at": datetime.utcnow().isoformat(),
        }

        logger.info(f"Refactoring scorecard generated: {weighted_total}/100 ({grade})")
        return Ok(card)

    # ------------------------------------------------------------------
    # ENH-STS-03 — Security Hardening Checks
    # ------------------------------------------------------------------

    _SUPPORTED_SECURITY_LANGUAGES = frozenset({"csharp", "typescript", "json", "python"})

    # Patterns: (rule_id, severity, regex_pattern, description)
    _SECURITY_PATTERNS: List[tuple] = [
        # Weak password hashing — C#/Python
        (
            "weak_password_hash",
            "P1",
            r"(?i)(SHA256|SHA512|MD5|SHA1)[\s\S]{0,120}(password|passwd|pwd|hash)",
            "Weak hash function used in password context. Use BCrypt or Argon2.",
        ),
        (
            "weak_password_hash",
            "P1",
            r"(?i)(password|passwd|pwd|hash)[\s\S]{0,120}(SHA256|SHA512|MD5|SHA1)",
            "Weak hash function used in password context. Use BCrypt or Argon2.",
        ),
        # JWT stored in localStorage — TypeScript
        (
            "localstorage_token",
            "P1",
            r"localStorage\.setItem\s*\(\s*['\"].*token",
            "JWT stored in localStorage is vulnerable to XSS. Use HttpOnly cookies.",
        ),
    ]

    # Context-hint driven checks (not regex — supplied via caller)
    _CONTEXT_HINT_CHECKS: List[tuple] = [
        (
            "incomplete_jwt",
            "P0",
            "has_jwt_config",
            "has_jwt_middleware",
            "JWT config present but no middleware/token generation wired. Complete auth or remove config.",
        ),
        (
            "missing_rate_limiting",
            "P1",
            "has_sensitive_endpoints",
            "has_rate_limiting",
            "Sensitive endpoints (login/payment) present without rate limiting middleware.",
        ),
    ]

    def check_security_hardening(
        self,
        source_code: str,
        language: str,
        context_hints: Optional[Dict[str, Any]] = None,
    ) -> Union[Ok[Dict[str, Any]], Err]:
        """Run security hardening checks on source code for a given language.

        Implements ENH-STS-03: detect weak crypto, incomplete auth infrastructure,
        and missing rate limiting. Surfaces violations by severity (P0/P1) so
        REFACTOR completion gate can block on unresolved issues.

        Args:
            source_code: Raw source text to scan.
            language: Target language ('csharp', 'typescript', 'json', 'python').
            context_hints: Optional dict supplying boolean context flags that
                cannot be inferred from source text alone, e.g.:
                    has_jwt_config, has_jwt_middleware,
                    has_sensitive_endpoints, has_rate_limiting.

        Returns:
            Ok with report dict: {violations, clean, violation_count, language}
            Err if language is unsupported.
        """
        import re as _re

        if language not in self._SUPPORTED_SECURITY_LANGUAGES:
            return Err(
                f"Unsupported language '{language}' for security checks. "
                f"Supported: {sorted(self._SUPPORTED_SECURITY_LANGUAGES)}"
            )

        violations: List[Dict[str, Any]] = []
        hints = context_hints or {}

        # --- Regex pattern checks ---
        for rule, severity, pattern, description in self._SECURITY_PATTERNS:
            match = _re.search(pattern, source_code)
            if match:
                violations.append(
                    {
                        "rule": rule,
                        "severity": severity,
                        "description": description,
                        "match": match.group(0)[:120],
                    }
                )

        # --- Context-hint checks ---
        for rule, severity, flag_present, flag_ok, description in self._CONTEXT_HINT_CHECKS:
            if hints.get(flag_present) and not hints.get(flag_ok):
                violations.append(
                    {
                        "rule": rule,
                        "severity": severity,
                        "description": description,
                        "match": f"context: {flag_present}=True, {flag_ok}=False",
                    }
                )

        clean = len(violations) == 0
        if violations:
            logger.warning(
                f"Security hardening check found {len(violations)} violation(s) "
                f"[{language}]: {[v['rule'] for v in violations]}"
            )

        return Ok(
            {
                "violations": violations,
                "clean": clean,
                "violation_count": len(violations),
                "language": language,
            }
        )

    # ------------------------------------------------------------------
    # ENH-STS-04 — Test Coverage Density Gate
    # ------------------------------------------------------------------

    def check_test_coverage_density(
        self,
        service_dir: Path,
        test_dir: Path,
        service_suffix: str = "Service",
        test_suffix: str = "Tests",
    ) -> Union[Ok[Dict[str, Any]], Err]:
        """Verify every service class has a matching test class.

        Implements ENH-STS-04: prevents thin test suites from going undetected
        after refactoring. Checks by file-name convention — each
        XxxService.{ext} must have a corresponding XxxServiceTests.{ext}.

        Args:
            service_dir: Directory containing service implementation files.
            test_dir: Directory containing test files.
            service_suffix: Filename suffix identifying service files (e.g. 'Service').
            test_suffix: Filename suffix to append for expected test file (e.g. 'Tests').

        Returns:
            Ok with report: {complete, missing_test_classes, coverage_pct, checked}
            Err if service_dir does not exist.
        """
        if not service_dir.exists():
            return Err(f"service_dir does not exist: {service_dir}")

        # Collect all service file stems (any extension)
        service_files = [
            f for f in service_dir.iterdir()
            if f.is_file() and service_suffix in f.stem
        ]

        if not service_files:
            return Ok(
                {
                    "complete": True,
                    "missing_test_classes": [],
                    "coverage_pct": 100.0,
                    "checked": 0,
                }
            )

        # Build set of existing test stems (strip extension)
        test_stems: set = set()
        if test_dir.exists():
            test_stems = {f.stem for f in test_dir.iterdir() if f.is_file()}

        missing: List[str] = []
        for svc_file in service_files:
            expected_test = svc_file.stem + test_suffix
            if expected_test not in test_stems:
                missing.append(expected_test)

        covered = len(service_files) - len(missing)
        coverage_pct = round((covered / len(service_files)) * 100, 1)
        complete = len(missing) == 0

        if missing:
            logger.warning(
                f"Test coverage density gap: {len(missing)} service(s) missing test class: {missing}"
            )

        return Ok(
            {
                "complete": complete,
                "missing_test_classes": missing,
                "coverage_pct": coverage_pct,
                "checked": len(service_files),
            }
        )

    # ------------------------------------------------------------------
    # Health Check (IOrchestrator protocol)
    # ------------------------------------------------------------------

    def health_check(self) -> Dict[str, Any]:
        """Return health status for wiring-contract validation."""
        return {
            "status": "healthy",
            "orchestrator": "RefactoringOrchestrator",
            "adapters_registered": self.registry.get_adapter_count(),
            "total_operations": self.get_total_operations_count(),
        }


# AC_COMPLETE: AC-PHASE24.6-002 ✅ RefactoringOrchestrator implementation complete
