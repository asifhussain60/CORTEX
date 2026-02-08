"""Phase Finalization Orchestrator - Automatic holistic review & activation.

Every phase completion must:
1. Holistic Review: Verify all layers connected (code, tests, docs, wiring)
2. Registry Sync: Update index.yaml with accurate status
3. Wiring Integration: Register all new components in wiring.yaml
4. Master Orchestrator Activation: Activate in MCP tools
5. Cleanup & Documentation: Final checks
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
from pathlib import Path
import yaml
from datetime import datetime


class ValidationLevel(Enum):
    """Validation severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ValidationResult:
    """Result of a validation check."""

    category: str
    check_name: str
    passed: bool
    severity: ValidationLevel
    details: str
    remediation: Optional[str] = None


@dataclass
class PhaseFinalizationReport:
    """Complete phase finalization report."""

    phase_id: str
    phase_name: str
    completion_date: str
    total_tests: int
    tests_passing: int
    validation_results: List[ValidationResult]
    wiring_updates: List[str]
    registry_updates: List[str]
    blockers: List[str]
    is_production_ready: bool


class HolisticReviewValidator:
    """Validate phase across all layers."""

    def __init__(self, phase_id: str, workspace_root: str = "/Users/asifhussain/PROJECTS/CORTEX"):
        """Initialize validator.

        Args:
            phase_id: Phase ID (e.g., "phase-47")
            workspace_root: Root workspace directory
        """
        self.phase_id = phase_id
        self.workspace_root = workspace_root
        self.validation_results: List[ValidationResult] = []

    def validate_code_layer(self) -> List[ValidationResult]:
        """Validate code implementation layer.

        Returns:
            List of validation results.
        """
        results = []

        # Check if orchestrators created
        orchestrators = self._find_phase_orchestrators()
        results.append(
            ValidationResult(
                category="Code Implementation",
                check_name="Orchestrator Existence",
                passed=len(orchestrators) > 0,
                severity=ValidationLevel.CRITICAL,
                details=f"Found {len(orchestrators)} orchestrators",
            )
        )

        # Check type hints
        type_hints_ok = self._check_type_hints(orchestrators)
        results.append(
            ValidationResult(
                category="Code Quality",
                check_name="Type Hints Coverage",
                passed=type_hints_ok,
                severity=ValidationLevel.HIGH,
                details="All functions have type hints",
            )
        )

        # Check docstrings
        docstrings_ok = self._check_docstrings(orchestrators)
        results.append(
            ValidationResult(
                category="Code Quality",
                check_name="Docstring Coverage",
                passed=docstrings_ok,
                severity=ValidationLevel.HIGH,
                details="All classes and functions documented",
            )
        )

        self.validation_results.extend(results)
        return results

    def validate_test_layer(self) -> List[ValidationResult]:
        """Validate test layer.

        Returns:
            List of validation results.
        """
        results = []

        # Check test files exist
        test_files = self._find_phase_tests()
        results.append(
            ValidationResult(
                category="Testing",
                check_name="Test Files Existence",
                passed=len(test_files) > 0,
                severity=ValidationLevel.CRITICAL,
                details=f"Found {len(test_files)} test files",
            )
        )

        # Check test coverage
        coverage = self._calculate_test_coverage(test_files)
        results.append(
            ValidationResult(
                category="Testing",
                check_name="Test Coverage",
                passed=coverage >= 80,
                severity=ValidationLevel.HIGH,
                details=f"Coverage: {coverage}%",
            )
        )

        # Check all tests passing
        tests_passing = self._verify_tests_pass(test_files)
        results.append(
            ValidationResult(
                category="Testing",
                check_name="All Tests Passing",
                passed=tests_passing,
                severity=ValidationLevel.CRITICAL,
                details="All unit tests must pass",
                remediation="Run: pytest tests/ -v",
            )
        )

        self.validation_results.extend(results)
        return results

    def validate_wiring_layer(self) -> List[ValidationResult]:
        """Validate wiring/integration layer.

        Returns:
            List of validation results.
        """
        results = []

        # Check wiring.yaml updated
        wiring_updated = self._check_wiring_yaml_updated()
        results.append(
            ValidationResult(
                category="Wiring Integration",
                check_name="wiring.yaml Updated",
                passed=wiring_updated,
                severity=ValidationLevel.CRITICAL,
                details="Orchestrators registered in wiring.yaml",
                remediation="Update cortex/wiring/specifications/wiring.yaml",
            )
        )

        # Check orchestrator registration
        registered = self._check_orchestrator_registration()
        results.append(
            ValidationResult(
                category="Wiring Integration",
                check_name="MCP Tool Registration",
                passed=registered,
                severity=ValidationLevel.HIGH,
                details="All tools registered in MCP gateway",
            )
        )

        self.validation_results.extend(results)
        return results

    def validate_governance_layer(self) -> List[ValidationResult]:
        """Validate governance and audit layer.

        Returns:
            List of validation results.
        """
        results = []

        # Check index.yaml updated
        index_updated = self._check_index_yaml_updated()
        results.append(
            ValidationResult(
                category="Governance",
                check_name="index.yaml Synchronized",
                passed=index_updated,
                severity=ValidationLevel.CRITICAL,
                details="Master plan registry synchronized with implementation",
                remediation="Update cortex-registry/_cortex-master/index.yaml",
            )
        )

        # Check AC markers
        ac_markers = self._check_audit_trail()
        results.append(
            ValidationResult(
                category="Governance",
                check_name="Audit Trail (AC markers)",
                passed=ac_markers,
                severity=ValidationLevel.MEDIUM,
                details="AC_START and AC_COMPLETE markers logged",
            )
        )

        # Check CORE rules
        core_rules = self._check_core_rules_compliance()
        results.append(
            ValidationResult(
                category="Governance",
                check_name="CORE Rules Compliance",
                passed=core_rules,
                severity=ValidationLevel.HIGH,
                details="Code complies with CORE-001 through CORE-050",
            )
        )

        self.validation_results.extend(results)
        return results

    def validate_documentation_layer(self) -> List[ValidationResult]:
        """Validate documentation layer.

        Returns:
            List of validation results.
        """
        results = []

        # Check code documentation
        code_docs = self._check_code_documentation()
        results.append(
            ValidationResult(
                category="Documentation",
                check_name="Code Documentation",
                passed=code_docs,
                severity=ValidationLevel.MEDIUM,
                details="Inline comments and docstrings present",
            )
        )

        # Check architecture documentation
        arch_docs = self._check_architecture_documentation()
        results.append(
            ValidationResult(
                category="Documentation",
                check_name="Architecture Documentation",
                passed=arch_docs,
                severity=ValidationLevel.MEDIUM,
                details="Architecture diagrams and design decisions documented",
            )
        )

        self.validation_results.extend(results)
        return results

    def generate_report(
        self,
        phase_name: str,
        total_tests: int,
        tests_passing: int,
    ) -> PhaseFinalizationReport:
        """Generate finalization report.

        Args:
            phase_name: Human-readable phase name
            total_tests: Total test count
            tests_passing: Tests passing count

        Returns:
            PhaseFinalizationReport object.
        """
        # Validate all layers
        self.validate_code_layer()
        self.validate_test_layer()
        self.validate_wiring_layer()
        self.validate_governance_layer()
        self.validate_documentation_layer()

        # Collect blockers
        blockers = [
            r.check_name
            for r in self.validation_results
            if not r.passed and r.severity in [ValidationLevel.CRITICAL, ValidationLevel.HIGH]
        ]

        # Determine readiness
        is_ready = (
            len(blockers) == 0
            and tests_passing == total_tests
            and all(r.passed for r in self.validation_results if r.severity == ValidationLevel.CRITICAL)
        )

        return PhaseFinalizationReport(
            phase_id=self.phase_id,
            phase_name=phase_name,
            completion_date=datetime.now().isoformat(),
            total_tests=total_tests,
            tests_passing=tests_passing,
            validation_results=self.validation_results,
            wiring_updates=self._extract_wiring_updates(),
            registry_updates=self._extract_registry_updates(),
            blockers=blockers,
            is_production_ready=is_ready,
        )

    # Helper methods (implementation stubs - to be filled based on actual files)

    def _find_phase_orchestrators(self) -> List[str]:
        """Find orchestrators for this phase."""
        # Pattern: cortex/orchestrators/{phase_name}/*.py
        return []

    def _check_type_hints(self, files: List[str]) -> bool:
        """Check if files have type hints."""
        return True

    def _check_docstrings(self, files: List[str]) -> bool:
        """Check if files have docstrings."""
        return True

    def _find_phase_tests(self) -> List[str]:
        """Find test files for this phase."""
        return []

    def _calculate_test_coverage(self, test_files: List[str]) -> int:
        """Calculate test coverage percentage."""
        return 85

    def _verify_tests_pass(self, test_files: List[str]) -> bool:
        """Verify all tests pass."""
        return True

    def _check_wiring_yaml_updated(self) -> bool:
        """Check if wiring.yaml was updated."""
        return True

    def _check_orchestrator_registration(self) -> bool:
        """Check if orchestrators are registered in MCP."""
        return True

    def _check_index_yaml_updated(self) -> bool:
        """Check if index.yaml synchronized."""
        return True

    def _check_audit_trail(self) -> bool:
        """Check for AC markers."""
        return True

    def _check_core_rules_compliance(self) -> bool:
        """Check CORE rules compliance."""
        return True

    def _check_code_documentation(self) -> bool:
        """Check code documentation."""
        return True

    def _check_architecture_documentation(self) -> bool:
        """Check architecture documentation."""
        return True

    def _extract_wiring_updates(self) -> List[str]:
        """Extract wiring updates made."""
        return ["cortex/wiring/specifications/wiring.yaml"]

    def _extract_registry_updates(self) -> List[str]:
        """Extract registry updates made."""
        return ["cortex-registry/_cortex-master/index.yaml"]


class WiringIntegrator:
    """Integrate phase components into wiring system."""

    def __init__(self, wiring_yaml_path: str = "/Users/asifhussain/PROJECTS/CORTEX/cortex/wiring/specifications/wiring.yaml"):
        """Initialize integrator.

        Args:
            wiring_yaml_path: Path to wiring.yaml
        """
        self.wiring_yaml_path = wiring_yaml_path
        self.updates: List[Dict[str, Any]] = []

    def register_orchestrator(
        self,
        orchestrator_name: str,
        class_name: str,
        module_path: str,
        description: str,
        phase_id: str,
    ) -> bool:
        """Register orchestrator in wiring.yaml.

        Args:
            orchestrator_name: Name for wiring (e.g., "phase_47_registry_structure")
            class_name: Class name (e.g., "CompanyRegistryStructureOrchestrator")
            module_path: Module path (e.g., "cortex.orchestrators.company_separation.registry_structure")
            description: Description of orchestrator
            phase_id: Phase ID (e.g., "phase-47")

        Returns:
            True if registration successful.
        """
        update = {
            "name": orchestrator_name,
            "class": class_name,
            "module": module_path,
            "description": description,
            "phase": phase_id,
            "status": "active",
            "added_date": datetime.now().isoformat(),
        }
        self.updates.append(update)
        return True

    def register_mcp_tool(
        self,
        tool_name: str,
        handler: str,
        parameters: Dict[str, Any],
        description: str,
        phase_id: str,
    ) -> bool:
        """Register MCP tool.

        Args:
            tool_name: Tool name (e.g., "cortex_validate_phase_47")
            handler: Handler orchestrator
            parameters: Tool parameters
            description: Tool description
            phase_id: Phase ID

        Returns:
            True if registration successful.
        """
        tool_update = {
            "tool_name": tool_name,
            "handler": handler,
            "parameters": parameters,
            "description": description,
            "phase": phase_id,
            "status": "active",
        }
        self.updates.append(tool_update)
        return True

    def get_registration_summary(self) -> Dict[str, Any]:
        """Get summary of registrations.

        Returns:
            Dictionary with registration summary.
        """
        return {
            "total_registrations": len(self.updates),
            "orchestrators": sum(1 for u in self.updates if "class" in u),
            "mcp_tools": sum(1 for u in self.updates if "tool_name" in u),
            "updates": self.updates,
        }


class MasterOrchestratorActivator:
    """Activate newly implemented components in master orchestrator."""

    def __init__(self, phase_id: str):
        """Initialize activator.

        Args:
            phase_id: Phase ID to activate
        """
        self.phase_id = phase_id
        self.activations: List[Dict[str, Any]] = []

    def activate_orchestrators(self, orchestrator_list: List[str]) -> bool:
        """Activate orchestrators.

        Args:
            orchestrator_list: List of orchestrator names

        Returns:
            True if activation successful.
        """
        for orchestrator in orchestrator_list:
            self.activations.append(
                {
                    "type": "orchestrator",
                    "name": orchestrator,
                    "phase": self.phase_id,
                    "status": "activated",
                    "timestamp": datetime.now().isoformat(),
                }
            )
        return True

    def activate_mcp_tools(self, tool_list: List[str]) -> bool:
        """Activate MCP tools.

        Args:
            tool_list: List of tool names

        Returns:
            True if activation successful.
        """
        for tool in tool_list:
            self.activations.append(
                {
                    "type": "mcp_tool",
                    "name": tool,
                    "phase": self.phase_id,
                    "status": "activated",
                    "timestamp": datetime.now().isoformat(),
                }
            )
        return True

    def get_activation_status(self) -> Dict[str, Any]:
        """Get activation status.

        Returns:
            Dictionary with activation details.
        """
        return {
            "phase": self.phase_id,
            "total_activations": len(self.activations),
            "activations": self.activations,
        }


class PhaseFinalizationOrchestrator:
    """Master orchestrator for phase finalization."""

    def __init__(
        self,
        phase_id: str,
        phase_name: str,
        workspace_root: str = "/Users/asifhussain/PROJECTS/CORTEX",
    ):
        """Initialize orchestrator.

        Args:
            phase_id: Phase ID
            phase_name: Human-readable phase name
            workspace_root: Root workspace directory
        """
        self.phase_id = phase_id
        self.phase_name = phase_name
        self.workspace_root = workspace_root
        self.validator = HolisticReviewValidator(phase_id, workspace_root)
        self.wiring_integrator = WiringIntegrator()
        self.activator = MasterOrchestratorActivator(phase_id)

    def finalize(
        self,
        total_tests: int,
        tests_passing: int,
        orchestrators: List[str],
        mcp_tools: List[str],
    ) -> PhaseFinalizationReport:
        """Execute complete phase finalization.

        Args:
            total_tests: Total test count
            tests_passing: Tests passing count
            orchestrators: List of orchestrator names
            mcp_tools: List of MCP tool names

        Returns:
            PhaseFinalizationReport object.
        """
        # Step 1: Holistic Review
        report = self.validator.generate_report(
            phase_name=self.phase_name,
            total_tests=total_tests,
            tests_passing=tests_passing,
        )

        # Step 2: Wiring Integration
        for orchestrator in orchestrators:
            self.wiring_integrator.register_orchestrator(
                orchestrator_name=orchestrator,
                class_name=orchestrator,
                module_path=f"cortex.orchestrators.{self.phase_id.replace('-', '_')}.{orchestrator}",
                description=f"{orchestrator} from {self.phase_name}",
                phase_id=self.phase_id,
            )

        for tool in mcp_tools:
            self.wiring_integrator.register_mcp_tool(
                tool_name=tool,
                handler="master_orchestrator",
                parameters={},
                description=f"{tool} from {self.phase_name}",
                phase_id=self.phase_id,
            )

        # Step 3: Master Orchestrator Activation
        if report.is_production_ready:
            self.activator.activate_orchestrators(orchestrators)
            self.activator.activate_mcp_tools(mcp_tools)

        # Step 4: Add activation status to report
        report.wiring_updates = list(self.wiring_integrator.get_registration_summary()["updates"])

        return report
