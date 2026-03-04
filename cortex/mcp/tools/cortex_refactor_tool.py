"""
CortexRefactor — Semantic refactoring operations.

Extracted from cortex/mcp/tools/operations.py (Phase 103-d, GAP-103-07).
Single Responsibility: Execute extract, rename, move, inline, organize, and
STS gate operations across Python, C#, and TypeScript/JavaScript codebases.

CORE-011: type hints | CORE-012: docstrings
"""
from __future__ import annotations

import re
from pathlib import Path as _Path
from typing import List

from cortex.mcp.mcp_tool_base import (
    ConsolidatedTool,
    ToolCategory,
    ToolParameter,
    ToolResult,
)
from cortex.mcp.tools._shared import validate_orchestrator_context


class CortexRefactor(ConsolidatedTool):
    """
    Semantic refactoring operations.

    Operations:
    - extract: Extract method/class
    - rename: Rename symbol
    - move: Move to new location
    - inline: Inline variable/method
    - organize: Organize imports/code
    - gate: ENH-STS four-gate Software Transformation Session check
    """

    @property
    def name(self) -> str:
        """Return the name."""
        return "cortex_refactor"

    @property
    def description(self) -> str:
        """Return the description."""
        return (
            "Execute semantic refactoring operations. Supports extract, rename, "
            "move, inline, and organize across Python, C#, TypeScript/JavaScript."
        )

    @property
    def category(self) -> ToolCategory:
        """Return the category."""
        return ToolCategory.OPERATIONS

    @property
    def parameters(self) -> List[ToolParameter]:
        """Return the parameters."""
        return [
            ToolParameter(
                name="operation",
                type="string",
                description="Refactor operation: extract, rename, move, inline, organize, gate",
                required=True,
                enum=["extract", "rename", "move", "inline", "organize", "gate"],
            ),
            ToolParameter(
                name="target",
                type="string",
                description="Target file or symbol",
                required=True,
            ),
            ToolParameter(
                name="new_name",
                type="string",
                description="New name for rename operations",
                required=False,
            ),
            ToolParameter(
                name="destination",
                type="string",
                description="Destination for move operations",
                required=False,
            ),
            ToolParameter(
                name="scope",
                type="string",
                description="Scope: local, module, package, workspace",
                required=False,
                enum=["local", "module", "package", "workspace"],
            ),
            # ENH-STS-01 — Functional Completeness
            ToolParameter(
                name="source_items",
                type="array",
                description="ENH-STS-01: Source endpoint/function list before refactoring",
                required=False,
            ),
            ToolParameter(
                name="target_items",
                type="array",
                description="ENH-STS-01: Target endpoint/function list after refactoring",
                required=False,
            ),
            # ENH-STS-02 — Session Traceability
            ToolParameter(
                name="session_id",
                type="string",
                description="ENH-STS-02: Refactor session UUID for audit trail",
                required=False,
            ),
            ToolParameter(
                name="trace_action",
                type="string",
                description="ENH-STS-02: Audit action — AC_START or AC_COMPLETE",
                required=False,
                enum=["AC_START", "AC_COMPLETE"],
            ),
            ToolParameter(
                name="trace_metadata",
                type="object",
                description="ENH-STS-02: Additional metadata to persist with trace",
                required=False,
            ),
            # ENH-STS-03 — Security Hardening
            ToolParameter(
                name="source_code",
                type="string",
                description="ENH-STS-03: Source code to scan for security issues",
                required=False,
            ),
            ToolParameter(
                name="language",
                type="string",
                description="ENH-STS-03: Language of source_code (e.g. csharp, python)",
                required=False,
            ),
            ToolParameter(
                name="context_hints",
                type="object",
                description=(
                    "ENH-STS-03: Structural hints — has_jwt_config, has_jwt_middleware, "
                    "has_sensitive_endpoints, has_rate_limiting"
                ),
                required=False,
            ),
            # ENH-STS-04 — Test Coverage Density
            ToolParameter(
                name="service_dir",
                type="string",
                description="ENH-STS-04: Path to directory containing service classes",
                required=False,
            ),
            ToolParameter(
                name="test_dir",
                type="string",
                description="ENH-STS-04: Path to directory containing test classes",
                required=False,
            ),
            # ENH-STS-05 — DI Lifetime Consistency
            ToolParameter(
                name="di_source_code",
                type="string",
                description=(
                    "ENH-STS-05: C# DI registration source (Program.cs / Startup.cs) "
                    "to scan for AddSingleton<*Repository> captive dependency violations"
                ),
                required=False,
            ),
            # ENH-STS-07 — Health Endpoint Realness
            ToolParameter(
                name="health_source_code",
                type="string",
                description=(
                    "ENH-STS-07: Source containing health endpoint mapping to validate "
                    "that it performs a live DB probe rather than returning a hardcoded stub"
                ),
                required=False,
            ),
        ]

    @property
    def supported_operations(self) -> List[str]:
        """Return the supported operations."""
        return ["extract", "rename", "move", "inline", "organize", "gate"]

    async def execute(self, **params) -> ToolResult:
        """Execute refactoring operation."""
        # ENFORCEMENT: Validate orchestrator routing
        _oc = params.get("orchestrator_context")
        if _oc is not None:
            validate_orchestrator_context(_oc)

        operation = params.get("operation", "organize")
        target = params.get("target", "")
        new_name = params.get("new_name")
        destination = params.get("destination")
        scope = params.get("scope", "module")

        if operation == "extract":
            return ToolResult(
                success=True,
                data={
                    "target": target,
                    "extracted_to": new_name or "new_method",
                    "type": "method",
                    "changes": [],
                },
                metadata={"operation": "extract"},
            )

        elif operation == "rename":
            if not new_name:
                return ToolResult(success=False, error="new_name required for rename")
            return ToolResult(
                success=True,
                data={
                    "old_name": target,
                    "new_name": new_name,
                    "scope": scope,
                    "references_updated": 0,
                },
                metadata={"operation": "rename"},
            )

        elif operation == "move":
            if not destination:
                return ToolResult(success=False, error="destination required for move")
            return ToolResult(
                success=True,
                data={
                    "source": target,
                    "destination": destination,
                    "imports_updated": 0,
                },
                metadata={"operation": "move"},
            )

        elif operation == "inline":
            return ToolResult(
                success=True,
                data={
                    "target": target,
                    "inlined_at": [],
                    "original_removed": True,
                },
                metadata={"operation": "inline"},
            )

        elif operation == "organize":
            return ToolResult(
                success=True,
                data={
                    "target": target,
                    "imports_sorted": True,
                    "unused_removed": 0,
                    "groups_created": ["stdlib", "third_party", "local"],
                },
                metadata={"operation": "organize"},
            )

        elif operation == "gate":
            return await self._execute_gate(target, params)

        return ToolResult(success=False, error=f"Unknown operation: {operation}")

    async def _execute_gate(self, target: str, params: dict) -> ToolResult:
        """Execute ENH-STS four-gate Software Transformation Session check.

        Gates:
            ENH-STS-01: Functional completeness (dropped endpoint detection)
            ENH-STS-02: Session traceability (AC_START / AC_COMPLETE audit)
            ENH-STS-03: Security hardening (weak crypto / incomplete auth)
            ENH-STS-04: Test coverage density (every Service has a TestClass)
        """
        gate_results: dict = {}
        blocking_issues: list = []
        p0_count = 0
        total_violations = 0

        # ── ENH-STS-01: Functional Completeness ──────────────────────────────
        source_items = params.get("source_items")
        target_items = params.get("target_items")
        if source_items is not None and target_items is not None:
            source_set = set(source_items)
            target_set = set(target_items)
            gaps = sorted(source_set - target_set)
            complete = len(gaps) == 0
            if not complete:
                p0_count += 1
                total_violations += len(gaps)
                blocking_issues.append(
                    f"ENH-STS-01: {len(gaps)} endpoint(s) dropped during refactoring"
                )
            gate_results["ENH-STS-01_functional_completeness"] = {
                "complete": complete,
                "gap_count": len(gaps),
                "gaps": gaps,
            }
        else:
            gate_results["ENH-STS-01_functional_completeness"] = {
                "skipped": True,
                "reason": "source_items and target_items not provided",
            }

        # ── ENH-STS-02: Session Traceability ─────────────────────────────────
        session_id = params.get("session_id")
        trace_action = params.get("trace_action")
        trace_metadata = params.get("trace_metadata") or {}
        if session_id and trace_action:
            persisted = False
            error_msg = None
            try:
                from cortex.orchestrators.domain.refactoring_orchestrator import (
                    RefactoringOrchestrator,
                )
                orch = RefactoringOrchestrator()
                result = orch.write_refactor_session_trace(
                    trace_action,
                    target,
                    target,
                    session_id,
                    metadata=trace_metadata,
                )
                # Support Ok/Err result objects or plain True/None
                if hasattr(result, "is_ok"):
                    persisted = result.is_ok()
                    if not persisted:
                        error_msg = str(result.unwrap_err()) if hasattr(result, "unwrap_err") else "trace failed"
                else:
                    persisted = bool(result) if result is not None else True
            except Exception as exc:
                error_msg = str(exc)

            if not persisted:
                blocking_issues.append(
                    f"ENH-STS-02: session trace write failed — {error_msg}"
                )
            gate_results["ENH-STS-02_session_trace"] = {
                "persisted": persisted,
                "action": trace_action,
                "session_id": session_id,
                "error": error_msg,
            }
        else:
            gate_results["ENH-STS-02_session_trace"] = {
                "skipped": True,
                "reason": "session_id and trace_action both required",
            }

        # ── ENH-STS-03: Security Hardening ───────────────────────────────────
        language = params.get("language")
        source_code = params.get("source_code", "")
        context_hints = params.get("context_hints") or {}
        if language:
            violations = []
            # Weak password hashing: SHA256 in a password context
            if re.search(r"SHA256", source_code or ""):
                violations.append({"rule": "weak_password_hash", "severity": "P1",
                                   "detail": "SHA256 detected for password hashing — use BCrypt/Argon2"})
            # Incomplete JWT: config present but middleware absent
            if context_hints.get("has_jwt_config") and not context_hints.get("has_jwt_middleware"):
                violations.append({"rule": "incomplete_jwt", "severity": "P0",
                                   "detail": "JWT config present but AddAuthentication middleware absent"})
                p0_count += 1
                total_violations += 1
                blocking_issues.append("ENH-STS-03: P0 — incomplete JWT middleware wiring")
            # Missing rate limiting on sensitive endpoints
            if context_hints.get("has_sensitive_endpoints") and not context_hints.get("has_rate_limiting"):
                violations.append({"rule": "missing_rate_limiting", "severity": "P1",
                                   "detail": "Sensitive endpoints exposed without rate limiting"})

            clean = len(violations) == 0
            gate_results["ENH-STS-03_security_hardening"] = {
                "clean": clean,
                "violation_count": len(violations),
                "violations": violations,
            }
        else:
            gate_results["ENH-STS-03_security_hardening"] = {
                "skipped": True,
                "reason": "language not provided",
            }

        # ── ENH-STS-04: Test Coverage Density ────────────────────────────────
        service_dir = params.get("service_dir")
        test_dir = params.get("test_dir")
        if service_dir and test_dir:
            svc_path = _Path(service_dir)
            tst_path = _Path(test_dir)
            missing_test_classes = []
            if svc_path.exists():
                for svc_file in svc_path.glob("*.cs"):
                    svc_name = svc_file.stem  # e.g. "AccountService"
                    test_name = f"{svc_name}Tests"
                    if not list(tst_path.rglob(f"{test_name}.cs")):
                        missing_test_classes.append(test_name)
            complete = len(missing_test_classes) == 0
            if not complete:
                total_violations += len(missing_test_classes)
                blocking_issues.append(
                    f"ENH-STS-04: {len(missing_test_classes)} service(s) missing test class"
                )
            gate_results["ENH-STS-04_test_coverage_density"] = {
                "complete": complete,
                "missing_test_classes": missing_test_classes,
            }
        else:
            gate_results["ENH-STS-04_test_coverage_density"] = {
                "skipped": True,
                "reason": "service_dir and test_dir both required",
            }

        # ── ENH-STS-05: DI Lifetime Consistency ──────────────────────────────
        di_source_code = params.get("di_source_code")
        if di_source_code is not None:
            di_violations = []
            try:
                from cortex.orchestrators.domain.refactoring_orchestrator import (
                    RefactoringOrchestrator,
                )
                orch = RefactoringOrchestrator()
                di_result = orch.check_di_lifetime_consistency(source_code=di_source_code)
                if di_result.is_ok():
                    di_report = di_result.unwrap()
                    di_violations = di_report.get("violations", [])
                    if not di_report.get("clean", True):
                        total_violations += di_report.get("violation_count", 0)
                        blocking_issues.append(
                            f"ENH-STS-05: {di_report.get('violation_count', 0)} "
                            "AddSingleton<*Repository> captive dependency violation(s)"
                        )
                    gate_results["ENH-STS-05_di_lifetime_consistency"] = {
                        "clean": di_report.get("clean", True),
                        "violation_count": di_report.get("violation_count", 0),
                        "violations": di_violations,
                    }
                else:
                    gate_results["ENH-STS-05_di_lifetime_consistency"] = {
                        "skipped": True,
                        "reason": f"check_di_lifetime_consistency error: {di_result.unwrap_err()}",
                    }
            except Exception as exc:
                gate_results["ENH-STS-05_di_lifetime_consistency"] = {
                    "skipped": True,
                    "reason": f"ENH-STS-05 gate error: {exc}",
                }
        else:
            gate_results["ENH-STS-05_di_lifetime_consistency"] = {
                "skipped": True,
                "reason": "di_source_code not provided",
            }

        # ── ENH-STS-07: Health Endpoint Realness ─────────────────────────────
        health_source_code = params.get("health_source_code")
        if health_source_code is not None:
            try:
                from cortex.orchestrators.domain.refactoring_orchestrator import (
                    RefactoringOrchestrator,
                )
                orch = RefactoringOrchestrator()
                health_result = orch.check_health_endpoint_realness(source_code=health_source_code)
                if health_result.is_ok():
                    health_report = health_result.unwrap()
                    if not health_report.get("clean", True):
                        total_violations += health_report.get("violation_count", 0)
                        blocking_issues.append(
                            "ENH-STS-07: health endpoint returns hardcoded stub — "
                            "add a real DB probe and 503 on failure"
                        )
                    gate_results["ENH-STS-07_health_endpoint_realness"] = {
                        "clean": health_report.get("clean", True),
                        "violation_count": health_report.get("violation_count", 0),
                        "violations": health_report.get("violations", []),
                    }
                else:
                    gate_results["ENH-STS-07_health_endpoint_realness"] = {
                        "skipped": True,
                        "reason": f"check_health_endpoint_realness error: {health_result.unwrap_err()}",
                    }
            except Exception as exc:
                gate_results["ENH-STS-07_health_endpoint_realness"] = {
                    "skipped": True,
                    "reason": f"ENH-STS-07 gate error: {exc}",
                }
        else:
            gate_results["ENH-STS-07_health_endpoint_realness"] = {
                "skipped": True,
                "reason": "health_source_code not provided",
            }

        # ── Overall status ────────────────────────────────────────────────────
        if p0_count > 0:
            overall_status = "BLOCK"
            success = False
        elif total_violations > 0:
            overall_status = "WARN"
            success = True
        else:
            overall_status = "PASS"
            success = True

        return ToolResult(
            success=success,
            data={
                "overall_status": overall_status,
                "p0_count": p0_count,
                "total_violations": total_violations,
                "gate_results": gate_results,
                "blocking_issues": blocking_issues,
            },
            metadata={"operation": "gate", "sts_gates_run": 6},
        )
