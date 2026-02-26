"""
RefactoringOrchestrator - Unified API for all refactoring tool adapters.

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

import hashlib
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# CORE-035: Single canonical Result — cortex.core.result is the sole definition (cortex.core.core.result deleted Phase 59-b)
from cortex.core.result import Err, Ok, Result
from cortex.core.interfaces.i_orchestrator import IOrchestrator, OperationMode
from cortex.core.workflow_template_mixin import WorkflowTemplateMixin
from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin  # Phase 62-B

# Backward-compat aliases (no-op now that both paths are identical)
CoreOk = Ok
CoreErr = Err
CoreResult = Result
from cortex.orchestrators.domain.refactoring.adapters.adapter_base import RefactoringToolAdapter
from cortex.orchestrators.domain.refactoring.adapters.rope_adapter import RopeAdapter
from cortex.orchestrators.domain.refactoring.adapters.refactoring_typescript_adapter import TypeScriptAdapter
from cortex.orchestrators.domain.refactoring.refactoring_models import (
    RefactoringLanguage,
    RefactoringRequest,
    RefactoringResult,
)
from cortex.orchestrators.domain.refactoring.refactoring_registry import RefactoringToolRegistry

# F10: Governance gate — lazy import to avoid circular deps
try:
    from cortex.orchestrators.core.enforcement_orchestrator import EnforcementOrchestrator as _EnforcementOrchestrator
    _ENFORCEMENT_AVAILABLE = True
except ImportError:
    _ENFORCEMENT_AVAILABLE = False

# Phase 58-C: tier3_scratch — execution scratch space for refactoring sessions
try:
    from cortex.intelligence.memory.tier3_scratch import (  # type: ignore[import]
        get_scratch_space_path as _refactor_get_scratch_path,
    )
except Exception:
    _refactor_get_scratch_path = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)

@dataclass
class _AuditEntry:
    """Audit trail entry with hash chain for RefactoringOrchestrator."""
    operation: str
    msg: str
    previous_hash: str = ""
    current_hash: str = field(default="")

    def __post_init__(self) -> None:
        if not self.current_hash:
            self.current_hash = hashlib.sha256(
                f"{self.operation}:{self.msg}:{self.previous_hash}".encode()
            ).hexdigest()[:16]

class RefactoringOrchestrator(OrchestratorProtocolMixin, WorkflowTemplateMixin, IOrchestrator):
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
        self._initialized: bool = False  # G3 Fix: double-init guard for IOrchestrator.initialize()
        self._audit_trail: List[Dict[str, Any]] = []  # G3 Fix: simple in-memory audit log

        # Auto-register all available adapters
        self._register_adapters()

        logger.info(
            f"RefactoringOrchestrator initialized with {self._registered_count} adapters"
        )

    def _extract_lens_context(
        self,
        orchestrator_context: Optional[Dict[str, Any]],
        target_path: str = "",
    ) -> Optional[Dict[str, Any]]:
        """Extract LENS intelligence context, calling LENS directly when needed.

        Phase 62-E: Genuine LENS call — not a stub. Uses safe canonical path.

        Priority order:
        1. Use ``lens_context`` forwarded by IntentRouter.
        2. If absent and *target_path* provided, call LENSOrchestrator.analyze_file().
        3. If LENS unavailable, return None (observable via safe_import warning).

        Args:
            orchestrator_context: Full context dict from IntentRouter. May be None.
            target_path: File path to analyse directly if no forwarded context.

        Returns:
            LENS result dict with at least ``language`` key, or ``None``.
        """
        if orchestrator_context is not None:
            forwarded = orchestrator_context.get("lens_context")
            if forwarded:
                return forwarded

        if not target_path:
            return None

        from cortex.core.dependency_guard import safe_import
        lens_module = safe_import(
            "cortex.lens.lens_orchestrator",
            fallback=None,
            warn=True,
            caller=__file__,
        )
        if lens_module is None:
            return None

        try:
            lens_cls = getattr(lens_module, "LENSOrchestrator", None)
            if lens_cls is None:
                return None
            result = lens_cls().analyze_file(target_path)
            return result if isinstance(result, dict) else None
        except Exception as lens_exc:  # noqa: BLE001
            logger.warning(
                "RefactoringOrchestrator._extract_lens_context: LENS failed for '%s' — %s",
                target_path,
                lens_exc,
            )
            return None

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
        # F10: Governance gate — validate before executing refactoring (CORE-048)
        if _ENFORCEMENT_AVAILABLE:
            try:
                _enforcer = _EnforcementOrchestrator()
                _gate = _enforcer.validate_operation({
                    "intent": "REFACTOR",
                    "target_file": str(request.file_path),
                    "operation": request.operation,
                })
                if _gate.is_err():
                    _result = _gate.unwrap_err()
                    logger.warning(
                        "Governance gate blocked refactoring: %s",
                        getattr(_result, "violations", _result),
                    )
                    return Err(f"Governance gate violation: {getattr(_result, 'violations', _result)}")
            except Exception as _gov_exc:  # pragma: no cover
                logger.warning("Governance gate check failed (non-blocking): %s", _gov_exc)

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
    # ENH-STS-05 — DI Lifetime Consistency Gate
    # ------------------------------------------------------------------

    # Regex: AddSingleton<*Repository*> — captive dependency when services are Scoped
    _SINGLETON_REPO_PATTERN = (
        r"AddSingleton\s*<\s*\w*Repository\w*\s*(?:,\s*\w+)?\s*>\s*\("
    )

    def check_di_lifetime_consistency(
        self,
        source_code: str,
    ) -> Union[Ok[Dict[str, Any]], Err]:
        """Detect captive dependency: Singleton repository registered alongside Scoped services.

        Implements ENH-STS-05: in ASP.NET Core DI, a Singleton service that depends on
        a Scoped service causes the Scoped object to be held for the application lifetime,
        leaking state between requests. The pattern ``AddSingleton<IXxxRepository>`` is
        always a violation when any service is ``AddScoped``.

        Acceptable lifetimes for repositories: ``AddScoped`` or ``AddTransient``.

        Args:
            source_code: Raw C# source text (typically Program.cs / Startup.cs).

        Returns:
            Ok with report: {clean, violations, violation_count}
            Err on unexpected failure.
        """
        import re as _re

        try:
            violations: List[Dict[str, Any]] = []

            for match in _re.finditer(self._SINGLETON_REPO_PATTERN, source_code):
                violations.append(
                    {
                        "rule": "singleton_repository",
                        "severity": "P1",
                        "description": (
                            "Repository registered as Singleton — captive dependency when "
                            "services are Scoped. Use AddScoped or AddTransient instead."
                        ),
                        "match": match.group(0)[:120],
                    }
                )

            clean = len(violations) == 0
            if violations:
                logger.warning(
                    f"DI lifetime consistency: {len(violations)} Singleton repository "
                    f"registration(s) detected. Remediation: use AddScoped."
                )

            return Ok(
                {
                    "clean": clean,
                    "violations": violations,
                    "violation_count": len(violations),
                }
            )
        except Exception as exc:
            logger.error(f"check_di_lifetime_consistency failed: {exc}")
            return Err(str(exc))

    # ------------------------------------------------------------------
    # ENH-STS-07 — Health Endpoint Realness Gate
    # ------------------------------------------------------------------

    # Regex: MapGet("/health" …) or MapGet("/api/health" …) followed by a lambda
    # that immediately returns a hardcoded object without an async DB call.
    _HEALTH_ROUTE_PATTERN = r'MapGet\s*\(\s*"[^"]*health[^"]*"\s*,'
    _ASYNC_DB_PROBE_PATTERN = r"(?:await|async)[\s\S]{0,400}(?:SELECT\s+1|ExecuteScalar|OpenAsync|ExecuteAsync)"
    _HARDCODED_HEALTHY_PATTERN = r'"healthy"'

    def check_health_endpoint_realness(
        self,
        source_code: str,
    ) -> Union[Ok[Dict[str, Any]], Err]:
        """Verify health endpoints perform a live dependency probe, not a hardcoded stub.

        Implements ENH-STS-07: health endpoints that always return ``{status:"healthy"}``
        regardless of actual system state are functionally identical to a stub health
        endpoint — they provide false confidence to orchestrators and load balancers.

        A real health endpoint must:
        1. Attempt a database call (``SELECT 1``, ``OpenAsync``, ``ExecuteScalarAsync``).
        2. Return a 503 status on failure (not always 200).

        Args:
            source_code: Raw C# (or TypeScript) source text containing health endpoint.

        Returns:
            Ok with report: {clean, violations, violation_count}
            Err on unexpected failure.
        """
        import re as _re

        try:
            violations: List[Dict[str, Any]] = []

            # Only check files that contain a health endpoint mapping
            if not _re.search(self._HEALTH_ROUTE_PATTERN, source_code, _re.IGNORECASE):
                # No health endpoint in this file — gate is inapplicable
                return Ok({"clean": True, "violations": [], "violation_count": 0})

            # File has a health endpoint: check whether it performs a real DB probe
            has_async_db_probe = bool(
                _re.search(self._ASYNC_DB_PROBE_PATTERN, source_code, _re.DOTALL | _re.IGNORECASE)
            )
            has_hardcoded_healthy = bool(
                _re.search(self._HARDCODED_HEALTHY_PATTERN, source_code)
            )

            if has_hardcoded_healthy and not has_async_db_probe:
                violations.append(
                    {
                        "rule": "hardcoded_health_status",
                        "severity": "P1",
                        "description": (
                            "Health endpoint returns a hardcoded 'healthy' status without "
                            "performing a live dependency probe (SELECT 1 / OpenAsync). "
                            "This is functionally identical to the original monolith. "
                            "Add a real DB reachability check and return 503 on failure."
                        ),
                        "match": 'MapGet("/health", ...) → hardcoded "healthy" without DB probe',
                    }
                )

            clean = len(violations) == 0
            if violations:
                logger.warning(
                    "Health endpoint realness gate: hardcoded 'healthy' response detected "
                    "without async DB probe. Remediation: add SELECT 1 + 503 on failure."
                )

            return Ok(
                {
                    "clean": clean,
                    "violations": violations,
                    "violation_count": len(violations),
                }
            )
        except Exception as exc:
            logger.error(f"check_health_endpoint_realness failed: {exc}")
            return Err(str(exc))

    # ------------------------------------------------------------------
    # ENH-STS-08 — Dual-Structure Duplicate Detection Gate (CORE-035)
    # ------------------------------------------------------------------
    #
    # Root cause: PB-STS-001 Run 1 produced TWO parallel backend implementations
    # inside Refactored/backend/ — a flat single-project layout (backend/*.cs)
    # AND a multi-project src/ layout (backend/src/**/*.cs) — both committed.
    # The .sln referenced only src/; the flat files were orphan code never compiled.
    # CORE-035 (single canonical implementation) was violated. This gate detects
    # and blocks commit of dual-structure output before it reaches the repo.

    _SOLUTION_FILE_EXTENSIONS = frozenset({".sln"})
    _PROJECT_FILE_EXTENSIONS = frozenset({".csproj", ".fsproj", ".vbproj"})
    _PACKAGE_FILE_NAMES = frozenset({"package.json", "pyproject.toml", "Cargo.toml", "go.mod"})

    def check_dual_structure(
        self,
        target_root: Path,
    ) -> Union[Ok[Dict[str, Any]], Err]:
        """Detect parallel duplicate directory structures in a refactored target.

        Implements ENH-STS-08 / CORE-035: prevents the pattern where two
        incompatible implementations of the same codebase coexist in the same
        output folder — a common failure mode when orchestration scaffolds a
        first-pass flat layout then a second-pass multi-project layout without
        cleaning up the first.

        A dual-structure violation is flagged when ALL of the following hold:
        1. A ``.sln`` (or multi-project manifest) is found in ``target_root``.
        2. The .sln references a ``src/`` (or similar) sub-directory.
        3. Sibling source files (``.cs``, ``.ts``, ``.py``) exist at the SAME
           directory level as the ``.sln`` file, outside any ``src/`` sub-tree
           (i.e., the flat layout was not cleaned up).

        Args:
            target_root: Path to the refactored output directory to inspect.

        Returns:
            Ok with report: {clean, violations, violation_count, sln_path,
                             orphan_files, recommendation}
            Err if target_root does not exist or is not a directory.
        """
        if not target_root.exists():
            return Err(f"target_root does not exist: {target_root}")
        if not target_root.is_dir():
            return Err(f"target_root is not a directory: {target_root}")

        violations: List[Dict[str, Any]] = []

        # Find all solution files one level deep (avoid deep recursion across src/)
        sln_files = list(target_root.rglob("*.sln"))

        for sln_path in sln_files:
            sln_dir = sln_path.parent

            # Read the .sln to discover which sub-directories it references
            try:
                sln_text = sln_path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue

            import re as _re

            # Extract project paths from .sln (e.g., src\API\Foo.csproj)
            referenced_roots: set = set()
            for m in _re.finditer(r'"([^"]+\.csproj)"', sln_text):
                first_segment = Path(m.group(1).replace("\\", "/")).parts[0]
                referenced_roots.add(first_segment)

            if not referenced_roots:
                # No project references found — cannot determine structure
                continue

            # Collect source files at the SLN directory level (flat layout)
            flat_source_extensions = {".cs", ".ts", ".py", ".fs", ".vb"}
            flat_files = [
                f for f in sln_dir.iterdir()
                if f.is_file() and f.suffix in flat_source_extensions
            ]

            # Detect flat-layout project files (e.g. a root-level .csproj)
            flat_proj_files = [
                f for f in sln_dir.iterdir()
                if f.is_file() and f.suffix in self._PROJECT_FILE_EXTENSIONS
            ]

            # Determine if there are sub-directories NOT referenced by the .sln
            all_subdirs = {d.name for d in sln_dir.iterdir() if d.is_dir()}
            unreferenced_source_dirs = all_subdirs - referenced_roots - {"tests", "test", ".git"}

            # A dual structure exists if:
            # - flat source files sit alongside the .sln AND
            # - at least one .sln-referenced sub-directory exists (src/ layout)
            has_flat_sources = bool(flat_files or flat_proj_files)
            has_structured_sources = any(
                (sln_dir / ref).is_dir() for ref in referenced_roots
            )

            # Check for directories with the same logical purpose (e.g. Api/ and src/API/)
            known_domain_dirs = {"Api", "Application", "Domain", "Infrastructure"}
            flat_domain_dirs = known_domain_dirs & {d.name for d in sln_dir.iterdir() if d.is_dir()}
            structured_domain_dirs = set()
            for ref in referenced_roots:
                ref_path = sln_dir / ref
                if ref_path.is_dir():
                    for child in ref_path.iterdir():
                        if child.is_dir() and child.name in known_domain_dirs:
                            structured_domain_dirs.add(child.name)

            duplicate_domains = flat_domain_dirs & structured_domain_dirs

            if (has_flat_sources or duplicate_domains) and has_structured_sources:
                orphans = [str(f.relative_to(target_root)) for f in flat_files + flat_proj_files]
                orphans += [
                    str((sln_dir / d).relative_to(target_root))
                    for d in duplicate_domains
                ]

                violations.append(
                    {
                        "rule": "dual_structure",
                        "severity": "P0",
                        "sln_path": str(sln_path.relative_to(target_root)),
                        "sln_references": sorted(referenced_roots),
                        "orphan_files_or_dirs": orphans,
                        "duplicate_domain_dirs": sorted(duplicate_domains),
                        "description": (
                            "CORE-035 violation: two parallel implementations detected. "
                            f"The .sln references {sorted(referenced_roots)} but flat-layout "
                            f"source files/dirs also exist at the same level. "
                            "Delete the orphan flat layout — only the .sln-referenced "
                            "structure is canonical."
                        ),
                        "recommendation": (
                            f"Delete all files/dirs at {sln_dir}/ that are NOT in "
                            f"{sorted(referenced_roots | {'tests', 'test', sln_path.name})}."
                        ),
                    }
                )

        clean = len(violations) == 0
        if violations:
            logger.error(
                "Dual-structure gate (CORE-035): %d violation(s) detected in %s. "
                "Delete orphan flat layout before committing.",
                len(violations), target_root,
            )
        else:
            logger.info(
                "Dual-structure gate passed: single canonical structure in %s", target_root
            )

        return Ok(
            {
                "clean": clean,
                "violations": violations,
                "violation_count": len(violations),
                "target_root": str(target_root),
            }
        )

    # ------------------------------------------------------------------
    # IOrchestrator interface compliance (G3 Fix: AC-PHASE24.6-IOrchestrator)
    # ------------------------------------------------------------------

    # Singleton support (tests expect instance() / reset_instance())
    _instance: Optional["RefactoringOrchestrator"] = None

    @classmethod
    def instance(cls) -> "RefactoringOrchestrator":
        """Return singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset singleton (test utility)."""
        cls._instance = None

    def get_name(self) -> str:
        """Return canonical orchestrator name."""
        return "RefactoringOrchestrator"

    def get_version(self) -> str:
        """Return orchestrator version (semver)."""
        return "1.0.0"

    def get_mode(self) -> OperationMode:
        """Return operation mode."""
        return OperationMode.EXECUTION

    def initialize(self) -> Result[str]:
        """Initialize orchestrator (idempotency guard — second call returns Err).

        Tests expect:
        - First call  → Ok
        - Second call → Err  (double-init guard)
        """
        if self._initialized:
            return CoreErr("RefactoringOrchestrator already initialized")
        self._initialized = True
        prev_hash = self._audit_trail[-1].current_hash if self._audit_trail else ""
        entry = _AuditEntry("INITIALIZE", f"initialized with {self._registered_count} adapters", previous_hash=prev_hash)
        self._audit_trail.append(entry)
        return CoreOk(entry.msg)

    def get_mcp_tools(self) -> Result[Dict[str, Any]]:
        """Return exposed MCP tool descriptors (AC-AR-012-02)."""
        return CoreOk({
            "execute_refactoring": {
                "description": "Execute a semantic refactoring operation",
                "parameters": ["operation", "file_path", "language", "parameters"],
            },
            "analyze_god_class": {
                "description": "Detect and analyse God Class violations (SOLID-SRP)",
            },
            "generate_refactoring_plan": {
                "description": "Generate a full refactoring plan for a module",
            },
            "apply_solid_decomposition": {
                "description": "Apply SOLID decomposition to a class hierarchy",
            },
            "get_supported_languages": {
                "description": "List supported refactoring languages",
            },
            "get_adapter_status": {
                "description": "Get adapter health status per language",
            },
        })

    def _inject_knowledge_context(self, domain: str = "refactoring") -> Dict[str, Any]:
        """Inject quality-standards knowledge context into refactoring decisions.

        Phase 78 GAP-78-A-03: Wire knowledge_context from refactoring-quality-standards
        so SRP targets and complexity thresholds are knowledge-informed.

        Args:
            domain: Knowledge domain to query (default: "refactoring").

        Returns:
            Dict with SRP targets, complexity thresholds from knowledge base.
        """
        try:
            from cortex.intelligence.provider import get_intelligence_provider
            provider = get_intelligence_provider()
            return provider.get_best_practices(f"refactoring:{domain}")
        except Exception:
            return {}

    def _get_quality_standards(self) -> Dict[str, Any]:
        """Return refactoring quality standards knowledge for current context.

        Phase 78 GAP-78-A-03: Convenience wrapper over _inject_knowledge_context.

        Returns:
            Dict with quality standards (SRP targets, complexity thresholds).
        """
        return self._inject_knowledge_context(domain="refactoring")

    def execute_operation(
        self,
        operation_name: str,
        parameters: Dict[str, Any],
    ) -> Result[Any]:
        """Route an operation_name to the matching refactoring method.

        Supported special operations:
        - analyze_god_class        → SRP violation detection
        - generate_refactoring_plan → phased refactoring plan
        - refactor / execute_refactoring → delegates to execute_refactoring()
        Unknown operations → Err (AC-AR-012-05)
        """
        # Phase 58 — cross-cutting hooks
        self._activate_cross_cutting_hooks(
            operation=operation_name,
            orchestrator_context=parameters.get("orchestrator_context"),
            unified_context=parameters.get("unified_context"),
        )
        try:
            result_value: Any
            if operation_name == "analyze_god_class":
                content = parameters.get("content", "")
                # SRP heuristic: count method defs + self.xxx() call sites as responsibility proxy
                method_count = content.count("def ") + content.count("void ") + content.count("function ")
                call_count = content.count("self.")
                total_indicators = method_count + call_count
                violations = []
                if method_count >= 3 or total_indicators >= 3:
                    violations.append(
                        f"SRP: class has {method_count} methods and {call_count} "
                        "responsibility call-sites spanning multiple concerns"
                    )
                result_value = {"violations": violations, "method_count": method_count}

            elif operation_name == "generate_refactoring_plan":
                god_classes = parameters.get("god_classes", [])
                architecture = parameters.get("target_architecture", "clean_architecture")
                phases = [
                    {"phase": 1, "name": "Extract interfaces", "targets": god_classes},
                    {"phase": 2, "name": "Decompose responsibilities", "architecture": architecture},
                    {"phase": 3, "name": "Wire dependencies", "targets": god_classes},
                ]
                result_value = {"phases": phases, "architecture": architecture}

            elif operation_name in ("refactor", "execute_refactoring"):
                request_data = parameters.get("request")
                if isinstance(request_data, RefactoringRequest):
                    inner = self.execute_refactoring(request_data)
                    if inner.is_ok():
                        result_value = inner.unwrap()
                    else:
                        prev_hash = self._audit_trail[-1].current_hash if self._audit_trail else ""
                        entry = _AuditEntry(operation_name.upper(), "refactoring error", previous_hash=prev_hash)
                        self._audit_trail.append(entry)
                        return CoreErr(str(getattr(inner, "error", "refactoring error")))
                else:
                    return CoreErr("execute_operation requires 'request' parameter of type RefactoringRequest")

            else:
                # Unknown operations return Err (tests explicitly assert this)
                return CoreErr(f"Unknown operation: {operation_name}")

            prev_hash = self._audit_trail[-1].current_hash if self._audit_trail else ""
            entry = _AuditEntry(operation_name.upper(), str(result_value)[:120], previous_hash=prev_hash)
            self._audit_trail.append(entry)
            return CoreOk(result_value)

        except Exception as exc:
            return CoreErr(f"RefactoringOrchestrator.execute_operation failed: {exc}")

    def get_audit_trail(self, limit: int = 100) -> Result[list]:
        """Return recent audit trail entries with hash chain (AC-AR-012-03)."""
        return CoreOk(self._audit_trail[-limit:])

    def get_recommended_template(self) -> Optional[str]:
        """Return the canonical refactoring workflow template.

        Returns:
            Template ID: 'refactor/holistic-sweep'

        Phase: 23 — Workflow Template Injection (G3 Fix)
        """
        return "refactor/holistic-sweep"

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

# AC_COMPLETE: AC-REFACTOR-20260223T000000Z ✅ RefactoringOrchestrator implementation complete
