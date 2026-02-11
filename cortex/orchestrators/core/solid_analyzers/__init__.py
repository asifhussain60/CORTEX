"""
SOLID Principle Analyzers for CORTEX Challenge System.

Provides 5 pluggable analyzer plugins for detecting SOLID principle violations:
- SRPAnalyzer: Single Responsibility Principle
- DIPAnalyzer: Dependency Inversion Principle
- DRYAnalyzer: Don't Repeat Yourself
- ISPAnalyzer: Interface Segregation Principle
- OCPAnalyzer: Open/Closed Principle

Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
Phase: 8.0 - Challenge Orchestrator Foundation
"""

import ast
import hashlib
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from cortex.core.result import Err, Ok, Result
from cortex.orchestrators.core.challenge_engine_plugins import (
    DisagreementContext,
    DisagreementPlugin,
    DisagreementType,
)

logger = logging.getLogger(__name__)


class SolidViolationType(Enum):
    """Types of SOLID violations detected."""
    SRP_VIOLATION = "single_responsibility_principle"
    DIP_VIOLATION = "dependency_inversion_principle"
    DRY_VIOLATION = "dont_repeat_yourself"
    ISP_VIOLATION = "interface_segregation_principle"
    OCP_VIOLATION = "open_closed_principle"


@dataclass
class SolidViolation:
    """Represents a detected SOLID principle violation."""
    violation_type: SolidViolationType
    file_path: Path
    line_number: int
    severity: float  # 0.0-1.0 (1.0 = most severe)
    description: str
    affected_elements: List[str] = field(default_factory=list)
    suggested_fix: str = ""
    evidence: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# SRP ANALYZER: Single Responsibility Principle
# ============================================================================

@dataclass
class Responsibility:
    """Represents a distinct responsibility in code."""
    name: str
    methods: List[str] = field(default_factory=list)
    cohesion_score: float = 0.0


class SRPAnalyzer(DisagreementPlugin):
    """
    Detects Single Responsibility Principle violations.

    Indicators:
    - Large classes (>500 lines, >20 methods)
    - Multiple distinct responsibilities
    - Low cohesion (methods don't relate to each other)
    - God objects (touches too many domains)
    """

    @property
    def disagreement_type(self) -> DisagreementType:
        """Return BETTER_SOLUTION (SRP improvement is a better approach)."""
        return DisagreementType.BETTER_SOLUTION

    def detect(self, context: DisagreementContext) -> Optional[str]:
        """Detect SRP violations in context (plugin interface)."""
        # Used for plugin system, not direct analysis
        return None

    def generate_recommendation(self, context: DisagreementContext) -> str:
        """Generate recommendation for SRP violation."""
        return "Split this class into smaller, single-responsibility classes"

    def analyze(self, file_path: Path) -> Result[List[SolidViolation]]:
        """
        Analyze file for SRP violations.

        Args:
            file_path: Path to Python file to analyze

        Returns:
            Result containing list of SRPViolations or error
        """
        try:
            with open(file_path, 'r') as f:
                source = f.read()

            tree = ast.parse(source)
            violations: List[SolidViolation] = []

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_violations = self._analyze_class(file_path, node, source)
                    violations.extend(class_violations)

            logger.info(f"SRP analysis complete: {file_path} - {len(violations)} violations")
            return Ok(violations)

        except Exception as e:
            logger.error(f"SRP analysis failed for {file_path}: {e}")
            return Err(f"SRP analysis error: {e}")

    def _analyze_class(self, file_path: Path, class_node: ast.ClassDef, source: str) -> List[SolidViolation]:
        """Analyze single class for SRP violations."""
        violations: List[SolidViolation] = []

        methods = [n.name for n in class_node.body if isinstance(n, ast.FunctionDef)]
        source_lines = source.splitlines()

        # Indicator 1: Large class (>500 lines)
        # Calculate class size from node positions
        class_start = class_node.lineno - 1
        class_end = class_node.end_lineno if hasattr(class_node, 'end_lineno') and class_node.end_lineno else class_start
        class_size = class_end - class_start

        if class_size > 500:
            violations.append(SolidViolation(
                violation_type=SolidViolationType.SRP_VIOLATION,
                file_path=file_path,
                line_number=class_node.lineno,
                severity=0.7,
                description=f"Large class '{class_node.name}': {class_size} lines (>500)",
                affected_elements=[class_node.name],
                suggested_fix=f"Split '{class_node.name}' into smaller, single-responsibility classes",
                evidence={"class_size": class_size, "threshold": 500}
            ))

        # Indicator 2: Too many methods (>20)
        if len(methods) > 20:
            violations.append(SolidViolation(
                violation_type=SolidViolationType.SRP_VIOLATION,
                file_path=file_path,
                line_number=class_node.lineno,
                severity=0.6,
                description=f"Class '{class_node.name}' has {len(methods)} methods (>20)",
                affected_elements=methods[:5],  # Show first 5
                suggested_fix="Extract groups of related methods into separate classes",
                evidence={"method_count": len(methods), "threshold": 20}
            ))

        # Indicator 3: Detect multiple responsibilities via method name patterns
        responsibilities = self._detect_responsibilities(methods)
        if len(responsibilities) > 2:
            responsibility_names = [r.name for r in responsibilities]
            violations.append(SolidViolation(
                violation_type=SolidViolationType.SRP_VIOLATION,
                file_path=file_path,
                line_number=class_node.lineno,
                severity=0.5,
                description=f"Class '{class_node.name}' has {len(responsibilities)} distinct responsibilities: {', '.join(responsibility_names)}",
                affected_elements=responsibility_names,
                suggested_fix="Group related methods by responsibility and create separate classes",
                evidence={"responsibilities": responsibility_names}
            ))

        return violations

    def _detect_responsibilities(self, methods: List[str]) -> List[Responsibility]:
        """Detect distinct responsibilities via method naming patterns."""
        responsibilities: Dict[str, Responsibility] = {}

        # Common responsibility prefixes
        prefixes = {
            "get_": "Data Access",
            "set_": "Data Mutation",
            "validate_": "Validation",
            "parse_": "Parsing",
            "format_": "Formatting",
            "calculate_": "Calculation",
            "log_": "Logging",
            "send_": "Communication",
            "fetch_": "External Data",
            "save_": "Persistence"
        }

        for method in methods:
            responsibility = "Other"
            for prefix, resp_name in prefixes.items():
                if method.startswith(prefix):
                    responsibility = resp_name
                    break

            if responsibility not in responsibilities:
                responsibilities[responsibility] = Responsibility(
                    name=responsibility,
                    methods=[]
                )

            responsibilities[responsibility].methods.append(method)

        return list(responsibilities.values())


# ============================================================================
# DIP ANALYZER: Dependency Inversion Principle
# ============================================================================

class DIPAnalyzer(DisagreementPlugin):
    """
    Detects Dependency Inversion Principle violations.

    Indicators:
    - Direct instantiation of concrete classes (new ConcreteClass())
    - Circular imports
    - Tight coupling (high coupling score)
    - Service locators / hard-coded dependencies
    """

    @property
    def disagreement_type(self) -> DisagreementType:
        """Return ARCHITECTURAL_VIOLATION (DIP is architectural)."""
        return DisagreementType.ARCHITECTURAL_VIOLATION

    def detect(self, context: DisagreementContext) -> Optional[str]:
        """Detect DIP violations in context (plugin interface)."""
        return None

    def generate_recommendation(self, context: DisagreementContext) -> str:
        """Generate recommendation for DIP violation."""
        return "Use dependency injection and abstract interfaces instead of concrete classes"

    def analyze(self, file_path: Path) -> Result[List[SolidViolation]]:
        """
        Analyze file for DIP violations.

        Args:
            file_path: Path to Python file to analyze

        Returns:
            Result containing list of DIPViolations or error
        """
        try:
            with open(file_path, 'r') as f:
                source = f.read()

            tree = ast.parse(source)
            violations: List[SolidViolation] = []

            # Check for concrete class instantiations
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        # Direct instantiation: ClassName()
                        class_name = node.func.id
                        # Heuristic: class names should be abstract (start with Abstract, Base, Interface)
                        if not any(class_name.startswith(prefix) for prefix in ["Abstract", "Base", "Interface", "_"]):
                            if class_name[0].isupper():  # Is it a class name?
                                violations.append(SolidViolation(
                                    violation_type=SolidViolationType.DIP_VIOLATION,
                                    file_path=file_path,
                                    line_number=node.lineno,
                                    severity=0.6,
                                    description=f"Direct concrete class instantiation: {class_name}()",
                                    affected_elements=[class_name],
                                    suggested_fix=f"Inject {class_name} as dependency or use factory pattern",
                                    evidence={"instantiated_class": class_name}
                                ))

            logger.info(f"DIP analysis complete: {file_path} - {len(violations)} violations")
            return Ok(violations)

        except Exception as e:
            logger.error(f"DIP analysis failed for {file_path}: {e}")
            return Err(f"DIP analysis error: {e}")


# ============================================================================
# DRY ANALYZER: Don't Repeat Yourself
# ============================================================================

class DRYAnalyzer(DisagreementPlugin):
    """
    Detects code duplication and DRY violations.

    Indicators:
    - Exact code duplication (copy-paste)
    - Similar patterns with minor differences
    - Repeated error handling
    - Repeated validation logic
    """

    @property
    def disagreement_type(self) -> DisagreementType:
        """Return REDUNDANT_WORK (duplication is unnecessary work)."""
        return DisagreementType.REDUNDANT_WORK

    def detect(self, context: DisagreementContext) -> Optional[str]:
        """Detect DRY violations in context (plugin interface)."""
        return None

    def generate_recommendation(self, context: DisagreementContext) -> str:
        """Generate recommendation for DRY violation."""
        return "Extract duplicated code into shared utility function"

    def analyze(self, file_paths: List[Path]) -> Result[List[SolidViolation]]:
        """
        Analyze files for DRY violations.

        Args:
            file_paths: List of Python files to analyze

        Returns:
            Result containing list of DRYViolations or error
        """
        try:
            violations: List[SolidViolation] = []
            code_hashes: Dict[str, List[tuple]] = {}  # hash -> [(file, line_num)]

            for file_path in file_paths:
                with open(file_path, 'r') as f:
                    lines = f.readlines()

                # Check for duplicated blocks (5+ line sequences)
                for i in range(len(lines) - 5):
                    block = ''.join(lines[i:i+5])
                    block_hash = hashlib.md5(block.encode()).hexdigest()

                    if block_hash not in code_hashes:
                        code_hashes[block_hash] = []

                    code_hashes[block_hash].append((file_path, i+1))

            # Find duplicate blocks
            for block_hash, occurrences in code_hashes.items():
                if len(occurrences) > 1:
                    # Found duplication
                    file_path, line_num = occurrences[0]
                    violations.append(SolidViolation(
                        violation_type=SolidViolationType.DRY_VIOLATION,
                        file_path=file_path,
                        line_number=line_num,
                        severity=0.5,
                        description=f"Code block duplicated {len(occurrences)} times across {len(set(f for f, _ in occurrences))} files",
                        affected_elements=[str(f) for f, _ in occurrences],
                        suggested_fix="Extract duplicated code into shared utility function",
                        evidence={"duplicate_count": len(occurrences), "locations": occurrences}
                    ))

            logger.info(f"DRY analysis complete: {len(violations)} duplication issues found")
            return Ok(violations)

        except Exception as e:
            logger.error(f"DRY analysis failed: {e}")
            return Err(f"DRY analysis error: {e}")


# ============================================================================
# ISP ANALYZER: Interface Segregation Principle
# ============================================================================

class ISPAnalyzer(DisagreementPlugin):
    """
    Detects Interface Segregation Principle violations.

    Indicators:
    - Large interfaces/protocols (>10 methods)
    - Unimplemented methods in implementations
    - Fat interface forcing implementations
    """

    @property
    def disagreement_type(self) -> DisagreementType:
        """Return BETTER_SOLUTION (ISP improvement is a better approach)."""
        return DisagreementType.BETTER_SOLUTION

    def detect(self, context: DisagreementContext) -> Optional[str]:
        """Detect ISP violations in context (plugin interface)."""
        return None

    def generate_recommendation(self, context: DisagreementContext) -> str:
        """Generate recommendation for ISP violation."""
        return "Split large interfaces into smaller, focused ones"

    def analyze(self, file_path: Path) -> Result[List[SolidViolation]]:
        """
        Analyze file for ISP violations.

        Args:
            file_path: Path to Python file to analyze

        Returns:
            Result containing list of ISPViolations or error
        """
        try:
            with open(file_path, 'r') as f:
                source = f.read()

            tree = ast.parse(source)
            violations: List[SolidViolation] = []

            for node in ast.walk(tree):
                # Check for abstract base classes or protocols
                if isinstance(node, ast.ClassDef):
                    methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]

                    # Indicator: Too many methods in interface (>10)
                    if len(methods) > 10 and any(d.id == "ABC" for d in node.decorator_list if isinstance(d, ast.Name)):
                        violations.append(SolidViolation(
                            violation_type=SolidViolationType.ISP_VIOLATION,
                            file_path=file_path,
                            line_number=node.lineno,
                            severity=0.5,
                            description=f"Interface '{node.name}' has {len(methods)} methods (>10)",
                            affected_elements=methods[:5],
                            suggested_fix=f"Split '{node.name}' into smaller, focused interfaces",
                            evidence={"method_count": len(methods), "threshold": 10}
                        ))

            logger.info(f"ISP analysis complete: {file_path} - {len(violations)} violations")
            return Ok(violations)

        except Exception as e:
            logger.error(f"ISP analysis failed for {file_path}: {e}")
            return Err(f"ISP analysis error: {e}")


# ============================================================================
# OCP ANALYZER: Open/Closed Principle
# ============================================================================

class OCPAnalyzer(DisagreementPlugin):
    """
    Detects Open/Closed Principle violations.

    Indicators:
    - Modifying base classes for extensions
    - Large if/else chains for type handling
    - Strategy pattern anti-patterns
    - Closed for extension (no inheritance points)
    """

    @property
    def disagreement_type(self) -> DisagreementType:
        """Return ARCHITECTURAL_VIOLATION (OCP is architectural)."""
        return DisagreementType.ARCHITECTURAL_VIOLATION

    def detect(self, context: DisagreementContext) -> Optional[str]:
        """Detect OCP violations in context (plugin interface)."""
        return None

    def generate_recommendation(self, context: DisagreementContext) -> str:
        """Generate recommendation for OCP violation."""
        return "Use polymorphism or strategy pattern instead of if/else chains"

    def analyze(self, file_path: Path) -> Result[List[SolidViolation]]:
        """
        Analyze file for OCP violations.

        Args:
            file_path: Path to Python file to analyze

        Returns:
            Result containing list of OCPViolations or error
        """
        try:
            with open(file_path, 'r') as f:
                source = f.read()

            tree = ast.parse(source)
            violations: List[SolidViolation] = []

            for node in ast.walk(tree):
                # Check for large if/else chains
                if isinstance(node, ast.If):
                    chain_length = self._count_if_chain(node)
                    if chain_length > 5:
                        violations.append(SolidViolation(
                            violation_type=SolidViolationType.OCP_VIOLATION,
                            file_path=file_path,
                            line_number=node.lineno,
                            severity=0.5,
                            description=f"Large if/else chain ({chain_length} branches) - consider polymorphism",
                            affected_elements=["if/elif/else chain"],
                            suggested_fix="Use polymorphism or strategy pattern instead of if/else chains",
                            evidence={"chain_length": chain_length}
                        ))

            logger.info(f"OCP analysis complete: {file_path} - {len(violations)} violations")
            return Ok(violations)

        except Exception as e:
            logger.error(f"OCP analysis failed for {file_path}: {e}")
            return Err(f"OCP analysis error: {e}")

    def _count_if_chain(self, node: ast.If) -> int:
        """Count the length of an if/elif/else chain."""
        count = 1
        for item in node.orelse:
            if isinstance(item, ast.If):
                count += self._count_if_chain(item)
            else:
                count += 1
        return count
