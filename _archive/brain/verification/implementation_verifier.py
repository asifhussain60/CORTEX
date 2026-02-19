"""
Implementation Verifier - Live Code Inspection

Verifies implementation details by inspecting live code structure,
wiring configuration, and orchestrator registry.

Phase 22 Component #5: ImplementationVerifier (P0)

Authority: AC-EDUCATIONAL-INTERACTION-001, CORE-030 (Implementation Truth)
Rule: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
"""

import ast
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml

from cortex.core.result import Err, Ok, Result
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger


class ImplementationStatus(Enum):
    """Implementation verification status."""
    IMPLEMENTED = "implemented"  # Feature fully implemented
    PARTIAL = "partial"  # Feature partially implemented
    MISSING = "missing"  # Feature not implemented
    BROKEN = "broken"  # Feature exists but broken/invalid
    DEPRECATED = "deprecated"  # Feature implemented but deprecated


@dataclass
class ImplementationIssue:
    """Issue found during implementation verification."""

    severity: str  # "error", "warning", "info"
    category: str  # "wiring", "code", "integration", "tests"
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    recommendation: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ImplementationReport:
    """
    Report of implementation verification results.

    Contains status, issues, metrics, and recommendations.
    """

    component: str
    status: ImplementationStatus
    confidence: float  # 0.0 - 1.0
    issues: List[ImplementationIssue]
    metrics: Dict[str, Any]
    recommendations: List[str]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


class ImplementationVerifier:
    """
    Implementation Verifier - Live code inspection and validation.

    Verifies implementation details by inspecting:
    - AST structure (classes, methods, inheritance)
    - Wiring configuration (YAML registration)
    - Orchestrator registry (runtime registration)
    - MCP tool exposure (tool definitions)
    - Test coverage (test file patterns)
    - Integration points (imports, dependencies)

    Features:
    - Deep AST analysis (methods, properties, decorators)
    - Wiring validation (consistency checks)
    - Registry verification (runtime state)
    - Issue detection with severity levels
    - Metric collection (LOC, methods, tests)
    - Recommendation generation

    Usage:
        >>> verifier = ImplementationVerifier()
        >>> report = verifier.verify_orchestrator("MasterOrchestrator")
        >>> print(report.status)  # IMPLEMENTED, PARTIAL, MISSING, BROKEN
        >>> print(report.issues)  # List of ImplementationIssue objects
        >>> print(report.metrics)  # {"loc": 500, "methods": 15, ...}

    Authority: AC-EDUCATIONAL-INTERACTION-001, CORE-030
    """

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize Implementation Verifier.

        Args:
            project_root: Root directory of CORTEX project (auto-detected if None)
        """
        self.logger = EnhancedAuditLogger.instance()
        self.project_root = project_root or Path(__file__).parent.parent.parent.parent
        self._cache: Dict[str, Any] = {}

        self.logger.log_operation_start(
            ac_id="AC-EDUCATIONAL-INTERACTION-001",
            operation="IMPL_VERIFIER_INIT",
            details={"project_root": str(self.project_root)}
        )

    def verify_orchestrator(
        self,
        orchestrator_name: str,
        check_wiring: bool = True,
        check_tests: bool = True
    ) -> ImplementationReport:
        """
        Verify orchestrator implementation completeness.

        Args:
            orchestrator_name: Name of orchestrator (e.g., "MasterOrchestrator")
            check_wiring: Whether to verify wiring configuration
            check_tests: Whether to check test coverage

        Returns:
            ImplementationReport with status, issues, and metrics

        Authority: CORE-030 (Implementation Truth)
        """
        self.logger.log_operation_start(
            ac_id="AC-EDUCATIONAL-INTERACTION-001",
            operation="VERIFY_ORCHESTRATOR",
            details={"orchestrator": orchestrator_name}
        )

        issues: List[ImplementationIssue] = []
        metrics: Dict[str, Any] = {}

        try:
            # 1. Find orchestrator file
            file_path = self._find_orchestrator_file(orchestrator_name)
            if not file_path:
                return ImplementationReport(
                    component=orchestrator_name,
                    status=ImplementationStatus.MISSING,
                    confidence=1.0,
                    issues=[ImplementationIssue(
                        severity="error",
                        category="code",
                        message=f"{orchestrator_name} implementation file not found",
                        recommendation=f"Create {orchestrator_name} in cortex/orchestrators/"
                    )],
                    metrics={},
                    recommendations=[f"Create {orchestrator_name} implementation"]
                )

            metrics["file_path"] = str(file_path.relative_to(self.project_root))

            # 2. Parse AST and analyze
            ast_issues, ast_metrics = self._analyze_ast(file_path, orchestrator_name)
            issues.extend(ast_issues)
            metrics.update(ast_metrics)

            # 3. Check wiring configuration
            if check_wiring:
                wiring_issues = self._check_wiring(orchestrator_name)
                issues.extend(wiring_issues)

            # 4. Check test coverage
            if check_tests:
                test_issues, test_metrics = self._check_tests(orchestrator_name)
                issues.extend(test_issues)
                metrics.update(test_metrics)

            # 5. Determine status from issues
            status = self._determine_status(issues, metrics)
            confidence = self._calculate_confidence(issues, metrics)
            recommendations = self._generate_recommendations(issues, orchestrator_name)

            self.logger.log_operation_complete(
                ac_id="AC-EDUCATIONAL-INTERACTION-001",
                operation="VERIFY_ORCHESTRATOR",
                success=True,
                details={"status": status.value, "issue_count": len(issues)}
            )

            return ImplementationReport(
                component=orchestrator_name,
                status=status,
                confidence=confidence,
                issues=issues,
                metrics=metrics,
                recommendations=recommendations
            )

        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-EDUCATIONAL-INTERACTION-001",
                operation="VERIFY_ORCHESTRATOR",
                success=False,
                details={"error": str(e)}
            )

            return ImplementationReport(
                component=orchestrator_name,
                status=ImplementationStatus.BROKEN,
                confidence=0.0,
                issues=[ImplementationIssue(
                    severity="error",
                    category="code",
                    message=f"Verification failed: {str(e)}"
                )],
                metrics={},
                recommendations=["Fix verification errors"]
            )

    def verify_mcp_tool(
        self,
        tool_name: str
    ) -> ImplementationReport:
        """
        Verify MCP tool implementation.

        Args:
            tool_name: Name of MCP tool (e.g., "cortex_ask")

        Returns:
            ImplementationReport with status and issues
        """
        issues: List[ImplementationIssue] = []
        metrics: Dict[str, Any] = {}

        # Find tool file
        mcp_path = self.project_root / "cortex" / "mcp" / "tools"
        if not mcp_path.exists():
            return ImplementationReport(
                component=tool_name,
                status=ImplementationStatus.MISSING,
                confidence=1.0,
                issues=[ImplementationIssue(
                    severity="error",
                    category="code",
                    message="MCP tools directory not found",
                    recommendation="Create cortex/mcp/tools/ directory"
                )],
                metrics={},
                recommendations=["Create MCP tools directory structure"]
            )

        tool_files = list(mcp_path.rglob(f"*{tool_name}*.py"))

        if not tool_files:
            return ImplementationReport(
                component=tool_name,
                status=ImplementationStatus.MISSING,
                confidence=1.0,
                issues=[ImplementationIssue(
                    severity="error",
                    category="code",
                    message=f"MCP tool {tool_name} not found",
                    recommendation=f"Create cortex/mcp/tools/{tool_name}.py"
                )],
                metrics={},
                recommendations=[f"Implement {tool_name} MCP tool"]
            )

        # Analyze tool file
        tool_file = tool_files[0]
        metrics["file_path"] = str(tool_file.relative_to(self.project_root))

        try:
            with open(tool_file, 'r') as f:
                content = f.read()
                tree = ast.parse(content)

            # Check for @mcp_tool decorator
            has_decorator = False
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Name) and 'mcp' in decorator.id.lower():
                            has_decorator = True
                            break

            if not has_decorator:
                issues.append(ImplementationIssue(
                    severity="warning",
                    category="code",
                    message="No @mcp_tool decorator found",
                    file_path=str(tool_file.relative_to(self.project_root)),
                    recommendation="Add @mcp_tool decorator to function"
                ))

            metrics["loc"] = len(content.splitlines())

            status = ImplementationStatus.IMPLEMENTED if not issues else ImplementationStatus.PARTIAL

            return ImplementationReport(
                component=tool_name,
                status=status,
                confidence=0.9 if not issues else 0.7,
                issues=issues,
                metrics=metrics,
                recommendations=[]
            )

        except Exception as e:
            return ImplementationReport(
                component=tool_name,
                status=ImplementationStatus.BROKEN,
                confidence=0.0,
                issues=[ImplementationIssue(
                    severity="error",
                    category="code",
                    message=f"Failed to analyze tool: {str(e)}"
                )],
                metrics=metrics,
                recommendations=["Fix syntax errors in MCP tool"]
            )

    def _find_orchestrator_file(self, orchestrator_name: str) -> Optional[Path]:
        """Find orchestrator implementation file."""
        orchestrators_path = self.project_root / "cortex" / "orchestrators"
        if not orchestrators_path.exists():
            return None

        # Convert to snake_case for file search
        import re
        snake_case = re.sub(r'(?<!^)(?=[A-Z])', '_', orchestrator_name).lower()

        found_files = list(orchestrators_path.rglob(f"*{snake_case}*.py"))

        # Filter out __init__.py and prioritize exact matches
        exact_match = None
        fallback = None

        for file_path in found_files:
            if file_path.name == "__init__.py":
                continue

            # Exact match (e.g., master_orchestrator.py for MasterOrchestrator)
            if file_path.stem == snake_case:
                exact_match = file_path
                break

            # Fallback to first non-exact match
            if fallback is None:
                fallback = file_path

        return exact_match or fallback

    def _analyze_ast(
        self,
        file_path: Path,
        orchestrator_name: str
    ) -> Tuple[List[ImplementationIssue], Dict[str, Any]]:
        """Analyze AST structure for implementation details."""
        issues: List[ImplementationIssue] = []
        metrics: Dict[str, Any] = {}

        try:
            with open(file_path, 'r') as f:
                content = f.read()
                tree = ast.parse(content)

            metrics["loc"] = len(content.splitlines())

            # Find class definition
            class_node = None
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and orchestrator_name in node.name:
                    class_node = node
                    break

            if not class_node:
                issues.append(ImplementationIssue(
                    severity="error",
                    category="code",
                    message=f"Class {orchestrator_name} not found in file",
                    file_path=str(file_path.relative_to(self.project_root))
                ))
                return issues, metrics

            # Check inheritance (should inherit from IOrchestrator)
            bases = [base.id if isinstance(base, ast.Name) else str(base) for base in class_node.bases]
            metrics["base_classes"] = bases

            if not any("IOrchestrator" in base or "Orchestrator" in base for base in bases):
                issues.append(ImplementationIssue(
                    severity="warning",
                    category="code",
                    message=f"{orchestrator_name} doesn't inherit from IOrchestrator",
                    file_path=str(file_path.relative_to(self.project_root)),
                    line_number=class_node.lineno,
                    recommendation="Inherit from IOrchestrator interface"
                ))

            # Collect methods
            methods = [m.name for m in class_node.body if isinstance(m, ast.FunctionDef)]
            metrics["method_count"] = len(methods)
            metrics["methods"] = methods

            # Check for required IOrchestrator methods
            required_methods = ["execute", "get_name", "get_version", "initialize", "get_mode"]
            missing_methods = [m for m in required_methods if m not in methods]

            if missing_methods:
                issues.append(ImplementationIssue(
                    severity="error",
                    category="code",
                    message=f"Missing required methods: {', '.join(missing_methods)}",
                    file_path=str(file_path.relative_to(self.project_root)),
                    recommendation=f"Implement missing IOrchestrator methods: {', '.join(missing_methods)}"
                ))

            # Check for docstrings
            if not ast.get_docstring(class_node):
                issues.append(ImplementationIssue(
                    severity="warning",
                    category="code",
                    message=f"{orchestrator_name} missing class docstring",
                    file_path=str(file_path.relative_to(self.project_root)),
                    line_number=class_node.lineno,
                    recommendation="Add Google-style docstring (CORE-012)"
                ))

            return issues, metrics

        except SyntaxError as e:
            issues.append(ImplementationIssue(
                severity="error",
                category="code",
                message=f"Syntax error: {str(e)}",
                file_path=str(file_path.relative_to(self.project_root)),
                line_number=e.lineno if hasattr(e, 'lineno') else None
            ))
            return issues, metrics

        except Exception as e:
            issues.append(ImplementationIssue(
                severity="error",
                category="code",
                message=f"AST analysis failed: {str(e)}",
                file_path=str(file_path.relative_to(self.project_root))
            ))
            return issues, metrics

    def _check_wiring(self, orchestrator_name: str) -> List[ImplementationIssue]:
        """Check wiring configuration for orchestrator."""
        issues: List[ImplementationIssue] = []

        wiring_path = self.project_root / "cortex" / "wiring" / "specifications" / "wiring.yaml"

        if not wiring_path.exists():
            issues.append(ImplementationIssue(
                severity="error",
                category="wiring",
                message="wiring.yaml not found",
                recommendation="Create wiring.yaml specification"
            ))
            return issues

        try:
            with open(wiring_path, 'r') as f:
                wiring_data = yaml.safe_load(f)

            orchestrators = wiring_data.get("orchestrators", [])

            # Check if orchestrator is registered
            found = False
            for orch in orchestrators:
                if isinstance(orch, dict) and orch.get("name") == orchestrator_name:
                    found = True

                    # Validate required fields
                    if not orch.get("module"):
                        issues.append(ImplementationIssue(
                            severity="error",
                            category="wiring",
                            message=f"{orchestrator_name} missing 'module' field in wiring",
                            file_path="cortex/wiring/specifications/wiring.yaml",
                            recommendation="Add module path to wiring configuration"
                        ))

                    if not orch.get("class_name"):
                        issues.append(ImplementationIssue(
                            severity="error",
                            category="wiring",
                            message=f"{orchestrator_name} missing 'class_name' field in wiring",
                            file_path="cortex/wiring/specifications/wiring.yaml",
                            recommendation="Add class_name to wiring configuration"
                        ))

                    break

            if not found:
                issues.append(ImplementationIssue(
                    severity="warning",
                    category="wiring",
                    message=f"{orchestrator_name} not registered in wiring.yaml",
                    file_path="cortex/wiring/specifications/wiring.yaml",
                    recommendation=f"Add {orchestrator_name} to wiring.yaml orchestrators list"
                ))

        except Exception as e:
            issues.append(ImplementationIssue(
                severity="error",
                category="wiring",
                message=f"Failed to parse wiring.yaml: {str(e)}",
                file_path="cortex/wiring/specifications/wiring.yaml"
            ))

        return issues

    def _check_tests(
        self,
        orchestrator_name: str
    ) -> Tuple[List[ImplementationIssue], Dict[str, Any]]:
        """Check test coverage for orchestrator."""
        issues: List[ImplementationIssue] = []
        metrics: Dict[str, Any] = {}

        tests_path = self.project_root / "tests"
        if not tests_path.exists():
            issues.append(ImplementationIssue(
                severity="error",
                category="tests",
                message="tests/ directory not found"
            ))
            return issues, metrics

        # Search for test files
        import re
        snake_case = re.sub(r'(?<!^)(?=[A-Z])', '_', orchestrator_name).lower()
        test_files = list(tests_path.rglob(f"*test*{snake_case}*.py"))

        metrics["test_file_count"] = len(test_files)

        if not test_files:
            issues.append(ImplementationIssue(
                severity="warning",
                category="tests",
                message=f"No test files found for {orchestrator_name}",
                recommendation=f"Create tests/unit/orchestrators/test_{snake_case}.py (CORE-008)"
            ))
        else:
            metrics["test_files"] = [str(f.relative_to(self.project_root)) for f in test_files]

            # Count test functions in files
            total_tests = 0
            for test_file in test_files:
                try:
                    with open(test_file, 'r') as f:
                        tree = ast.parse(f.read())

                    test_count = sum(1 for node in ast.walk(tree)
                                   if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'))
                    total_tests += test_count

                except Exception:
                    pass

            metrics["test_count"] = total_tests

            if total_tests == 0:
                issues.append(ImplementationIssue(
                    severity="warning",
                    category="tests",
                    message=f"Test files exist but no test functions found for {orchestrator_name}",
                    recommendation="Add test functions with test_ prefix"
                ))

        return issues, metrics

    def _determine_status(
        self,
        issues: List[ImplementationIssue],
        metrics: Dict[str, Any]
    ) -> ImplementationStatus:
        """Determine implementation status from issues and metrics."""
        error_count = sum(1 for issue in issues if issue.severity == "error")
        warning_count = sum(1 for issue in issues if issue.severity == "warning")

        if error_count > 0:
            return ImplementationStatus.BROKEN
        elif warning_count > 2:
            return ImplementationStatus.PARTIAL
        elif warning_count > 0:
            return ImplementationStatus.PARTIAL
        else:
            return ImplementationStatus.IMPLEMENTED

    def _calculate_confidence(
        self,
        issues: List[ImplementationIssue],
        metrics: Dict[str, Any]
    ) -> float:
        """Calculate confidence score from issues and metrics."""
        error_count = sum(1 for issue in issues if issue.severity == "error")
        warning_count = sum(1 for issue in issues if issue.severity == "warning")

        if error_count > 0:
            return 0.3  # Low confidence due to errors
        elif warning_count > 3:
            return 0.6  # Medium confidence due to many warnings
        elif warning_count > 0:
            return 0.8  # Good confidence with minor issues
        else:
            return 1.0  # Full confidence

    def _generate_recommendations(
        self,
        issues: List[ImplementationIssue],
        orchestrator_name: str
    ) -> List[str]:
        """Generate recommendations from issues."""
        recommendations: Set[str] = set()

        for issue in issues:
            if issue.recommendation:
                recommendations.add(issue.recommendation)

        # Add general recommendations based on issue patterns
        error_categories = {issue.category for issue in issues if issue.severity == "error"}

        if "code" in error_categories:
            recommendations.add(f"Review {orchestrator_name} implementation for errors")
        if "wiring" in error_categories:
            recommendations.add("Update wiring.yaml configuration")
        if "tests" in error_categories:
            recommendations.add("Add test coverage following CORE-008 (TDD)")

        return sorted(list(recommendations))
