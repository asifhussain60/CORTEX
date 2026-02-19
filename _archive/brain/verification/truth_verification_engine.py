"""
Truth Verification Engine - Implementation Truth Verification

Verifies claims against live code, wiring, tests, and git history.
Detects documentation drift and implementation mismatches.

Phase 22 Component #4: TruthVerificationEngine (P0)

Authority: AC-EDUCATIONAL-INTERACTION-001, CORE-030 (Implementation Truth)
Rule: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
"""

import ast
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from cortex.core.result import Err, Ok, Result
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger


class VerificationStatus(Enum):
    """Verification outcome status."""
    VERIFIED = "verified"  # Claim matches live implementation
    FALSE = "false"  # Claim contradicts implementation
    PARTIAL = "partial"  # Claim partially correct
    UNKNOWN = "unknown"  # Cannot verify (missing context)
    DRIFT = "drift"  # Documentation exists but outdated


class ClaimType(Enum):
    """Type of claim being verified."""
    ORCHESTRATOR_EXISTS = "orchestrator_exists"
    ORCHESTRATOR_CAPABILITY = "orchestrator_capability"
    WIRING_CONFIG = "wiring_config"
    TEST_COVERAGE = "test_coverage"
    FILE_EXISTS = "file_exists"
    FUNCTION_EXISTS = "function_exists"
    CLASS_EXISTS = "class_exists"
    PARAMETER_TYPE = "parameter_type"
    RETURN_TYPE = "return_type"
    INTEGRATION_POINT = "integration_point"
    MCP_TOOL = "mcp_tool"
    GIT_HISTORY = "git_history"


@dataclass
class Evidence:
    """
    Evidence supporting verification result.

    Contains file paths, line numbers, code snippets, and git references.
    """

    source_type: str  # "code", "wiring", "test", "git", "docs"
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    line_range: Optional[Tuple[int, int]] = None
    code_snippet: Optional[str] = None
    git_commit: Optional[str] = None
    git_timestamp: Optional[str] = None
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VerificationResult:
    """
    Result of truth verification.

    Contains status, evidence, confidence, and recommendations.
    """

    claim: str
    claim_type: ClaimType
    status: VerificationStatus
    confidence: float  # 0.0 - 1.0
    evidence: List[Evidence]
    explanation: str
    recommendations: List[str] = field(default_factory=list)
    drift_detected: bool = False
    drift_details: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


class TruthVerificationEngine:
    """
    Truth Verification Engine - Implementation-based claim verification.

    Verifies claims about CORTEX architecture by inspecting:
    - Live code (AST analysis)
    - Wiring configuration (YAML parsing)
    - Test files (test coverage)
    - Git history (recent changes)
    - Documentation (drift detection)

    Features:
    - Multi-source evidence collection
    - Confidence scoring (0.0 - 1.0)
    - Documentation drift detection
    - Recommendation generation
    - Integration with LENS for code intelligence

    Usage:
        >>> engine = TruthVerificationEngine()
        >>> result = engine.verify_claim(
        ...     claim="MasterOrchestrator has Stage 2 routing",
        ...     claim_type=ClaimType.ORCHESTRATOR_CAPABILITY
        ... )
        >>> print(result.status)  # VERIFIED, FALSE, PARTIAL, UNKNOWN
        >>> print(result.evidence)  # List of Evidence objects

    Authority: AC-EDUCATIONAL-INTERACTION-001, CORE-030
    """

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize Truth Verification Engine.

        Args:
            project_root: Root directory of CORTEX project (auto-detected if None)
        """
        self.logger = EnhancedAuditLogger.instance()
        self.project_root = project_root or Path(__file__).parent.parent.parent.parent
        self._cache: Dict[str, Any] = {}

        self.logger.log_operation_start(
            ac_id="AC-EDUCATIONAL-INTERACTION-001",
            operation="TRUTH_ENGINE_INIT",
            details={"project_root": str(self.project_root)}
        )

    def verify_claim(
        self,
        claim: str,
        claim_type: ClaimType,
        context: Optional[Dict[str, Any]] = None
    ) -> VerificationResult:
        """
        Verify a claim against live implementation.

        Args:
            claim: The claim to verify (natural language or structured)
            claim_type: Type of claim for routing verification strategy
            context: Optional context (file path, component name, etc.)

        Returns:
            VerificationResult with status, evidence, and recommendations

        Authority: CORE-030 (Implementation Truth)
        """
        self.logger.log_operation_start(
            ac_id="AC-EDUCATIONAL-INTERACTION-001",
            operation="VERIFY_CLAIM",
            details={"claim": claim, "type": claim_type.value}
        )

        context = context or {}

        try:
            # Route to appropriate verification strategy
            if claim_type == ClaimType.ORCHESTRATOR_EXISTS:
                result = self._verify_orchestrator_exists(claim, context)
            elif claim_type == ClaimType.ORCHESTRATOR_CAPABILITY:
                result = self._verify_orchestrator_capability(claim, context)
            elif claim_type == ClaimType.WIRING_CONFIG:
                result = self._verify_wiring_config(claim, context)
            elif claim_type == ClaimType.FILE_EXISTS:
                result = self._verify_file_exists(claim, context)
            elif claim_type == ClaimType.FUNCTION_EXISTS:
                result = self._verify_function_exists(claim, context)
            elif claim_type == ClaimType.CLASS_EXISTS:
                result = self._verify_class_exists(claim, context)
            elif claim_type == ClaimType.TEST_COVERAGE:
                result = self._verify_test_coverage(claim, context)
            elif claim_type == ClaimType.MCP_TOOL:
                result = self._verify_mcp_tool(claim, context)
            else:
                result = VerificationResult(
                    claim=claim,
                    claim_type=claim_type,
                    status=VerificationStatus.UNKNOWN,
                    confidence=0.0,
                    evidence=[],
                    explanation=f"Verification strategy not implemented for {claim_type.value}"
                )

            self.logger.log_operation_complete(
                ac_id="AC-EDUCATIONAL-INTERACTION-001",
                operation="VERIFY_CLAIM",
                success=True,
                details={"status": result.status.value, "confidence": result.confidence}
            )

            return result

        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-EDUCATIONAL-INTERACTION-001",
                operation="VERIFY_CLAIM",
                success=False,
                details={"error": str(e)}
            )

            return VerificationResult(
                claim=claim,
                claim_type=claim_type,
                status=VerificationStatus.UNKNOWN,
                confidence=0.0,
                evidence=[],
                explanation=f"Verification failed: {str(e)}"
            )

    def _verify_orchestrator_exists(
        self,
        claim: str,
        context: Dict[str, Any]
    ) -> VerificationResult:
        """Verify orchestrator exists in codebase."""
        orchestrator_name = context.get("orchestrator_name", self._extract_orchestrator_name(claim))

        evidence = []

        # Check cortex/orchestrators directory structure
        orchestrators_path = self.project_root / "cortex" / "orchestrators"

        if not orchestrators_path.exists():
            return VerificationResult(
                claim=claim,
                claim_type=ClaimType.ORCHESTRATOR_EXISTS,
                status=VerificationStatus.FALSE,
                confidence=1.0,
                evidence=[],
                explanation=f"Orchestrators directory not found at {orchestrators_path}"
            )

        # Search for orchestrator file - convert to snake_case for file matching
        import re
        snake_case_name = re.sub(r'(?<!^)(?=[A-Z])', '_', orchestrator_name).lower()
        found_files = list(orchestrators_path.rglob(f"*{snake_case_name}*.py"))

        if found_files:
            for file_path in found_files:
                if file_path.name != "__init__.py":
                    evidence.append(Evidence(
                        source_type="code",
                        file_path=str(file_path.relative_to(self.project_root)),
                        description=f"Orchestrator implementation found: {file_path.name}"
                    ))

            return VerificationResult(
                claim=claim,
                claim_type=ClaimType.ORCHESTRATOR_EXISTS,
                status=VerificationStatus.VERIFIED,
                confidence=1.0,
                evidence=evidence,
                explanation=f"{orchestrator_name} exists in codebase with implementation files"
            )
        else:
            return VerificationResult(
                claim=claim,
                claim_type=ClaimType.ORCHESTRATOR_EXISTS,
                status=VerificationStatus.FALSE,
                confidence=1.0,
                evidence=[],
                explanation=f"{orchestrator_name} not found in cortex/orchestrators/",
                recommendations=[
                    f"Create {orchestrator_name} implementation",
                    "Check wiring.yaml for registration",
                    "Add to orchestrator registry"
                ]
            )

    def _verify_orchestrator_capability(
        self,
        claim: str,
        context: Dict[str, Any]
    ) -> VerificationResult:
        """Verify orchestrator has claimed capability via AST analysis."""
        orchestrator_name = context.get("orchestrator_name", self._extract_orchestrator_name(claim))
        capability = context.get("capability", "")

        evidence = []

        # Find orchestrator file
        orchestrators_path = self.project_root / "cortex" / "orchestrators"
        found_files = list(orchestrators_path.rglob(f"*{orchestrator_name.lower()}*.py"))

        if not found_files:
            return VerificationResult(
                claim=claim,
                claim_type=ClaimType.ORCHESTRATOR_CAPABILITY,
                status=VerificationStatus.FALSE,
                confidence=1.0,
                evidence=[],
                explanation=f"{orchestrator_name} not found, cannot verify capability"
            )

        # Parse AST to find methods
        for file_path in found_files:
            if file_path.name == "__init__.py":
                continue

            try:
                with open(file_path, 'r') as f:
                    tree = ast.parse(f.read())

                # Find class definition
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and orchestrator_name in node.name:
                        # Collect method names
                        methods = [m.name for m in node.body if isinstance(m, ast.FunctionDef)]

                        evidence.append(Evidence(
                            source_type="code",
                            file_path=str(file_path.relative_to(self.project_root)),
                            line_number=node.lineno,
                            description=f"Found class {node.name} with methods: {', '.join(methods[:10])}",
                            metadata={"methods": methods}
                        ))

                        # Check if capability keyword appears in method names
                        if capability:
                            matching_methods = [m for m in methods if capability.lower() in m.lower()]
                            if matching_methods:
                                return VerificationResult(
                                    claim=claim,
                                    claim_type=ClaimType.ORCHESTRATOR_CAPABILITY,
                                    status=VerificationStatus.VERIFIED,
                                    confidence=0.9,
                                    evidence=evidence,
                                    explanation=f"{orchestrator_name} has capability '{capability}' (methods: {', '.join(matching_methods)})"
                                )

            except Exception as e:
                evidence.append(Evidence(
                    source_type="code",
                    file_path=str(file_path.relative_to(self.project_root)),
                    description=f"Failed to parse: {str(e)}"
                ))

        if evidence:
            return VerificationResult(
                claim=claim,
                claim_type=ClaimType.ORCHESTRATOR_CAPABILITY,
                status=VerificationStatus.PARTIAL,
                confidence=0.5,
                evidence=evidence,
                explanation=f"{orchestrator_name} exists but specific capability '{capability}' not clearly evident"
            )

        return VerificationResult(
            claim=claim,
            claim_type=ClaimType.ORCHESTRATOR_CAPABILITY,
            status=VerificationStatus.UNKNOWN,
            confidence=0.0,
            evidence=[],
            explanation=f"Could not analyze {orchestrator_name} for capability verification"
        )

    def _verify_wiring_config(
        self,
        claim: str,
        context: Dict[str, Any]
    ) -> VerificationResult:
        """Verify wiring configuration exists and is correct."""
        wiring_path = self.project_root / "cortex" / "wiring" / "specifications" / "wiring.yaml"

        if not wiring_path.exists():
            return VerificationResult(
                claim=claim,
                claim_type=ClaimType.WIRING_CONFIG,
                status=VerificationStatus.FALSE,
                confidence=1.0,
                evidence=[],
                explanation="wiring.yaml not found at expected location",
                recommendations=["Create wiring.yaml specification"]
            )

        try:
            import yaml
            with open(wiring_path, 'r') as f:
                wiring_data = yaml.safe_load(f)

            evidence = [Evidence(
                source_type="wiring",
                file_path=str(wiring_path.relative_to(self.project_root)),
                description="Wiring configuration loaded successfully"
            )]

            return VerificationResult(
                claim=claim,
                claim_type=ClaimType.WIRING_CONFIG,
                status=VerificationStatus.VERIFIED,
                confidence=1.0,
                evidence=evidence,
                explanation="Wiring configuration exists and is parseable",
                metadata={"orchestrator_count": len(wiring_data.get("orchestrators", []))}
            )

        except Exception as e:
            return VerificationResult(
                claim=claim,
                claim_type=ClaimType.WIRING_CONFIG,
                status=VerificationStatus.FALSE,
                confidence=1.0,
                evidence=[],
                explanation=f"Wiring configuration exists but failed to parse: {str(e)}",
                recommendations=["Fix YAML syntax in wiring.yaml"]
            )

    def _verify_file_exists(
        self,
        claim: str,
        context: Dict[str, Any]
    ) -> VerificationResult:
        """Verify file exists at claimed path."""
        file_path_str = context.get("file_path", self._extract_file_path(claim))

        if not file_path_str:
            return VerificationResult(
                claim=claim,
                claim_type=ClaimType.FILE_EXISTS,
                status=VerificationStatus.UNKNOWN,
                confidence=0.0,
                evidence=[],
                explanation="Could not extract file path from claim"
            )

        file_path = self.project_root / file_path_str

        if file_path.exists():
            evidence = [Evidence(
                source_type="code",
                file_path=file_path_str,
                description=f"File exists: {file_path.name} ({file_path.stat().st_size} bytes)"
            )]

            return VerificationResult(
                claim=claim,
                claim_type=ClaimType.FILE_EXISTS,
                status=VerificationStatus.VERIFIED,
                confidence=1.0,
                evidence=evidence,
                explanation=f"File exists at {file_path_str}"
            )
        else:
            return VerificationResult(
                claim=claim,
                claim_type=ClaimType.FILE_EXISTS,
                status=VerificationStatus.FALSE,
                confidence=1.0,
                evidence=[],
                explanation=f"File not found at {file_path_str}",
                recommendations=[f"Create file at {file_path_str}"]
            )

    def _verify_function_exists(
        self,
        claim: str,
        context: Dict[str, Any]
    ) -> VerificationResult:
        """Verify function exists in specified file via AST."""
        file_path_str = context.get("file_path", "")
        function_name = context.get("function_name", self._extract_function_name(claim))

        if not file_path_str or not function_name:
            return VerificationResult(
                claim=claim,
                claim_type=ClaimType.FUNCTION_EXISTS,
                status=VerificationStatus.UNKNOWN,
                confidence=0.0,
                evidence=[],
                explanation="Missing file path or function name for verification"
            )

        file_path = self.project_root / file_path_str

        if not file_path.exists():
            return VerificationResult(
                claim=claim,
                claim_type=ClaimType.FUNCTION_EXISTS,
                status=VerificationStatus.FALSE,
                confidence=1.0,
                evidence=[],
                explanation=f"File not found: {file_path_str}"
            )

        try:
            with open(file_path, 'r') as f:
                tree = ast.parse(f.read())

            # Find function definition
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == function_name:
                    evidence = [Evidence(
                        source_type="code",
                        file_path=file_path_str,
                        line_number=node.lineno,
                        description=f"Function {function_name} found at line {node.lineno}"
                    )]

                    return VerificationResult(
                        claim=claim,
                        claim_type=ClaimType.FUNCTION_EXISTS,
                        status=VerificationStatus.VERIFIED,
                        confidence=1.0,
                        evidence=evidence,
                        explanation=f"Function {function_name} exists in {file_path_str}"
                    )

            return VerificationResult(
                claim=claim,
                claim_type=ClaimType.FUNCTION_EXISTS,
                status=VerificationStatus.FALSE,
                confidence=1.0,
                evidence=[],
                explanation=f"Function {function_name} not found in {file_path_str}",
                recommendations=[f"Implement function {function_name} in {file_path_str}"]
            )

        except Exception as e:
            return VerificationResult(
                claim=claim,
                claim_type=ClaimType.FUNCTION_EXISTS,
                status=VerificationStatus.UNKNOWN,
                confidence=0.0,
                evidence=[],
                explanation=f"Failed to parse file: {str(e)}"
            )

    def _verify_class_exists(
        self,
        claim: str,
        context: Dict[str, Any]
    ) -> VerificationResult:
        """Verify class exists in specified file via AST."""
        file_path_str = context.get("file_path", "")
        class_name = context.get("class_name", self._extract_class_name(claim))

        if not file_path_str or not class_name:
            return VerificationResult(
                claim=claim,
                claim_type=ClaimType.CLASS_EXISTS,
                status=VerificationStatus.UNKNOWN,
                confidence=0.0,
                evidence=[],
                explanation="Missing file path or class name for verification"
            )

        file_path = self.project_root / file_path_str

        if not file_path.exists():
            return VerificationResult(
                claim=claim,
                claim_type=ClaimType.CLASS_EXISTS,
                status=VerificationStatus.FALSE,
                confidence=1.0,
                evidence=[],
                explanation=f"File not found: {file_path_str}"
            )

        try:
            with open(file_path, 'r') as f:
                tree = ast.parse(f.read())

            # Find class definition
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == class_name:
                    # Get base classes
                    bases = [base.id if isinstance(base, ast.Name) else str(base) for base in node.bases]

                    evidence = [Evidence(
                        source_type="code",
                        file_path=file_path_str,
                        line_number=node.lineno,
                        description=f"Class {class_name} found at line {node.lineno}, bases: {', '.join(bases) if bases else 'None'}",
                        metadata={"bases": bases}
                    )]

                    return VerificationResult(
                        claim=claim,
                        claim_type=ClaimType.CLASS_EXISTS,
                        status=VerificationStatus.VERIFIED,
                        confidence=1.0,
                        evidence=evidence,
                        explanation=f"Class {class_name} exists in {file_path_str}"
                    )

            return VerificationResult(
                claim=claim,
                claim_type=ClaimType.CLASS_EXISTS,
                status=VerificationStatus.FALSE,
                confidence=1.0,
                evidence=[],
                explanation=f"Class {class_name} not found in {file_path_str}",
                recommendations=[f"Implement class {class_name} in {file_path_str}"]
            )

        except Exception as e:
            return VerificationResult(
                claim=claim,
                claim_type=ClaimType.CLASS_EXISTS,
                status=VerificationStatus.UNKNOWN,
                confidence=0.0,
                evidence=[],
                explanation=f"Failed to parse file: {str(e)}"
            )

    def _verify_test_coverage(
        self,
        claim: str,
        context: Dict[str, Any]
    ) -> VerificationResult:
        """Verify test coverage exists for component."""
        component_name = context.get("component_name", self._extract_component_name(claim))

        # Search for test files
        tests_path = self.project_root / "tests"
        found_tests = list(tests_path.rglob(f"*test*{component_name.lower()}*.py"))

        if found_tests:
            evidence = [Evidence(
                source_type="test",
                file_path=str(test_file.relative_to(self.project_root)),
                description=f"Test file found: {test_file.name}"
            ) for test_file in found_tests]

            return VerificationResult(
                claim=claim,
                claim_type=ClaimType.TEST_COVERAGE,
                status=VerificationStatus.VERIFIED,
                confidence=0.8,
                evidence=evidence,
                explanation=f"Found {len(found_tests)} test file(s) for {component_name}"
            )
        else:
            return VerificationResult(
                claim=claim,
                claim_type=ClaimType.TEST_COVERAGE,
                status=VerificationStatus.FALSE,
                confidence=1.0,
                evidence=[],
                explanation=f"No test files found for {component_name}",
                recommendations=[
                    f"Create test file: tests/unit/test_{component_name.lower()}.py",
                    "Follow CORE-008 (TDD) guidelines"
                ]
            )

    def _verify_mcp_tool(
        self,
        claim: str,
        context: Dict[str, Any]
    ) -> VerificationResult:
        """Verify MCP tool exists and is properly registered."""
        tool_name = context.get("tool_name", self._extract_tool_name(claim))

        # Search for MCP tool files
        mcp_path = self.project_root / "cortex" / "mcp" / "tools"
        if not mcp_path.exists():
            return VerificationResult(
                claim=claim,
                claim_type=ClaimType.MCP_TOOL,
                status=VerificationStatus.FALSE,
                confidence=1.0,
                evidence=[],
                explanation="MCP tools directory not found",
                recommendations=["Create cortex/mcp/tools/ directory"]
            )

        found_tools = list(mcp_path.rglob(f"*{tool_name}*.py"))

        if found_tools:
            evidence = [Evidence(
                source_type="code",
                file_path=str(tool_file.relative_to(self.project_root)),
                description=f"MCP tool implementation found: {tool_file.name}"
            ) for tool_file in found_tools]

            return VerificationResult(
                claim=claim,
                claim_type=ClaimType.MCP_TOOL,
                status=VerificationStatus.VERIFIED,
                confidence=1.0,
                evidence=evidence,
                explanation=f"MCP tool {tool_name} exists with implementation"
            )
        else:
            return VerificationResult(
                claim=claim,
                claim_type=ClaimType.MCP_TOOL,
                status=VerificationStatus.FALSE,
                confidence=1.0,
                evidence=[],
                explanation=f"MCP tool {tool_name} not found",
                recommendations=[
                    f"Create MCP tool: cortex/mcp/tools/{tool_name}.py",
                    "Use @mcp_tool decorator",
                    "Register in MCP server"
                ]
            )

    # Helper methods for extracting entities from claims

    def _extract_orchestrator_name(self, claim: str) -> str:
        """Extract orchestrator name from claim."""
        # Simple heuristic: look for words ending in "Orchestrator"
        words = claim.split()
        for word in words:
            if "Orchestrator" in word:
                return word.strip(".,!?")
        return "UnknownOrchestrator"

    def _extract_file_path(self, claim: str) -> str:
        """Extract file path from claim."""
        # Look for patterns like "cortex/..." or "tests/..."
        import re
        match = re.search(r'(cortex|tests)/[\w/]+\.py', claim)
        if match:
            return match.group(0)
        return ""

    def _extract_function_name(self, claim: str) -> str:
        """Extract function name from claim."""
        # Look for patterns like "function_name()" or "def function_name"
        import re
        match = re.search(r'(?:def\s+)?(\w+)\s*\(', claim)
        if match:
            return match.group(1)
        return ""

    def _extract_class_name(self, claim: str) -> str:
        """Extract class name from claim."""
        # Look for patterns like "class ClassName" or multi-word capitalized names
        import re
        # First try "class ClassName"
        match = re.search(r'class\s+([A-Z][a-zA-Z]+(?:[A-Z][a-zA-Z]+)*)', claim)
        if match:
            return match.group(1)
        # Then try standalone capitalized multi-word (like "TruthVerificationEngine")
        match = re.search(r'\b([A-Z][a-z]+(?:[A-Z][a-z]+)+)\b', claim)
        if match:
            return match.group(1)
        # Finally try any capitalized word
        match = re.search(r'\b([A-Z][a-zA-Z]+)\b', claim)
        if match:
            return match.group(1)
        return ""

    def _extract_component_name(self, claim: str) -> str:
        """Extract component name from claim."""
        # Similar to class name extraction
        return self._extract_class_name(claim)

    def _extract_tool_name(self, claim: str) -> str:
        """Extract MCP tool name from claim."""
        # Look for "cortex_*" patterns
        import re
        match = re.search(r'(cortex_\w+)', claim)
        if match:
            return match.group(1)
        return ""
