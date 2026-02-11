"""
Fault Detection Reporter for CORTEX ASK Mode.

Intelligently detects implementation issues and provides actionable
recommendations for fixing faults in CORTEX components.

Features:
- Categorizes faults (WIRING, TESTING, DOCUMENTATION, INTERFACE, IMPLEMENTATION)
- Severity levels (ERROR, WARNING, INFO)
- Actionable recommendations
- File path references
- Prioritized fault lists

Authority: AC-EDUCATIONAL-INTERACTION-001, PHASE-22-ASK-MODE-SYSTEM.yaml
Rules: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class FaultSeverity(Enum):
    """Severity levels for detected faults."""
    ERROR = 3  # Critical issues that block functionality
    WARNING = 2  # Issues that should be addressed
    INFO = 1  # Informational notices


class FaultCategory(Enum):
    """Categories of detected faults."""
    WIRING = "wiring"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    INTERFACE = "interface"
    IMPLEMENTATION = "implementation"
    MCP = "mcp"


@dataclass
class Fault:
    """A single detected fault."""
    category: FaultCategory
    severity: FaultSeverity
    title: str
    description: str
    recommendation: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None


@dataclass
class FaultReport:
    """Complete fault detection report."""
    topic: str
    faults: List[Fault]
    summary: str
    total_errors: int
    total_warnings: int
    total_info: int


class FaultDetectionReporter:
    """
    Detects and reports implementation faults in CORTEX components.

    Strategy:
    1. Analyze verification results from TruthVerificationEngine
    2. Categorize issues by type (wiring, testing, docs, etc.)
    3. Assign severity levels
    4. Generate actionable recommendations
    5. Sort by priority (errors first)

    Use Cases:
    - Missing orchestrator files
    - Unregistered wiring
    - Missing test coverage
    - Poor documentation
    - Interface non-compliance
    - Missing MCP tools
    """

    def __init__(self):
        """Initialize FaultDetectionReporter."""
        pass

    def detect_faults(
        self,
        topic: str,
        verification_results: Dict[str, Any]
    ) -> FaultReport:
        """
        Detect faults from verification results.

        Args:
            topic: Component or topic being analyzed
            verification_results: Results from TruthVerificationEngine

        Returns:
            FaultReport with detected issues and recommendations
        """
        faults: List[Fault] = []

        # Check for missing orchestrator
        if not verification_results.get("orchestrator_exists", True):
            faults.append(Fault(
                category=FaultCategory.IMPLEMENTATION,
                severity=FaultSeverity.ERROR,
                title="Orchestrator not found",
                description=f"{topic} does not exist in the codebase",
                recommendation=(
                    f"Create {topic} by:\n"
                    f"1. Create file: cortex/orchestrators/[domain]/{topic.lower()}.py\n"
                    f"2. Implement IOrchestrator interface\n"
                    f"3. Add to wiring.yaml\n"
                    f"4. Write TDD tests"
                ),
                file_path=verification_results.get("file_path")
            ))

        # Check for missing wiring registration
        if verification_results.get("orchestrator_exists") and not verification_results.get("wiring_registered", True):
            faults.append(Fault(
                category=FaultCategory.WIRING,
                severity=FaultSeverity.ERROR,
                title="Not registered in wiring.yaml",
                description=f"{topic} exists but is not registered in wiring configuration",
                recommendation=(
                    "Register in wiring.yaml:\n"
                    "1. Open cortex/wiring/specifications/wiring.yaml\n"
                    "2. Add entry under appropriate category\n"
                    "3. Include correct file path and class name\n"
                    "4. Run wiring validation tests"
                ),
                file_path="cortex/wiring/specifications/wiring.yaml"
            ))

        # Check for missing test coverage
        test_coverage = verification_results.get("test_coverage", 100)
        if test_coverage == 0:
            faults.append(Fault(
                category=FaultCategory.TESTING,
                severity=FaultSeverity.ERROR,
                title="No test coverage",
                description=f"{topic} has no unit tests (violates CORE-008)",
                recommendation=(
                    "Add TDD tests:\n"
                    "1. Create tests/unit/orchestrators/[domain]/test_{topic.lower()}.py\n"
                    "2. Write tests BEFORE implementation (TDD)\n"
                    "3. Cover execute(), get_name(), get_description()\n"
                    "4. Aim for 80%+ coverage"
                ),
                file_path=f"tests/unit/orchestrators/test_{topic.lower()}.py"
            ))
        elif test_coverage < 70:
            faults.append(Fault(
                category=FaultCategory.TESTING,
                severity=FaultSeverity.WARNING,
                title="Low test coverage",
                description=f"{topic} has only {test_coverage}% test coverage",
                recommendation=(
                    f"Increase test coverage to 80%+:\n"
                    f"1. Review untested code paths\n"
                    f"2. Add tests for edge cases\n"
                    f"3. Test error handling\n"
                    f"4. Current: {test_coverage}%, Target: 80%"
                )
            ))

        # Check for missing documentation
        if verification_results.get("documentation") is None:
            faults.append(Fault(
                category=FaultCategory.DOCUMENTATION,
                severity=FaultSeverity.WARNING,
                title="Missing documentation",
                description=f"{topic} lacks proper docstrings (violates CORE-012)",
                recommendation=(
                    "Add Google-style docstrings:\n"
                    "1. Class docstring explaining purpose\n"
                    "2. Method docstrings with Args/Returns\n"
                    "3. Example usage in module docstring\n"
                    "4. Follow CORE-012 standard"
                ),
                file_path=verification_results.get("file_path")
            ))

        # Check for interface compliance
        if not verification_results.get("implements_interface", True):
            faults.append(Fault(
                category=FaultCategory.INTERFACE,
                severity=FaultSeverity.ERROR,
                title="Does not implement IOrchestrator",
                description=f"{topic} does not inherit from IOrchestrator interface",
                recommendation=(
                    "Implement IOrchestrator interface:\n"
                    "1. from cortex.brain.core.interfaces.i_orchestrator import IOrchestrator\n"
                    "2. class {topic}(IOrchestrator):\n"
                    "3. Implement required methods: execute(), get_name(), get_description()\n"
                    "4. Add type hints for all methods"
                )
            ))

        # Sort faults by severity (errors first)
        faults.sort(key=lambda f: f.severity.value, reverse=True)

        # Generate summary
        error_count = sum(1 for f in faults if f.severity == FaultSeverity.ERROR)
        warning_count = sum(1 for f in faults if f.severity == FaultSeverity.WARNING)
        info_count = sum(1 for f in faults if f.severity == FaultSeverity.INFO)

        if not faults:
            summary = f"✅ {topic} has no detected issues"
        else:
            summary = f"⚠️ {topic} has {len(faults)} issue(s): {error_count} errors, {warning_count} warnings"

        return FaultReport(
            topic=topic,
            faults=faults,
            summary=summary,
            total_errors=error_count,
            total_warnings=warning_count,
            total_info=info_count
        )

    def format_report(self, report: FaultReport) -> str:
        """
        Format fault report for user display.

        Args:
            report: FaultReport to format

        Returns:
            Formatted string ready for display
        """
        lines = [
            f"## 🔍 Fault Detection Report: {report.topic}",
            "",
            report.summary,
            ""
        ]

        if report.faults:
            lines.append("### Issues Detected\n")

            for i, fault in enumerate(report.faults, start=1):
                # Severity emoji
                severity_emoji = {
                    FaultSeverity.ERROR: "❌",
                    FaultSeverity.WARNING: "⚠️",
                    FaultSeverity.INFO: "ℹ️"
                }[fault.severity]

                lines.append(f"**{i}. {severity_emoji} {fault.title}** ({fault.category.value})")
                lines.append(f"   {fault.description}")
                lines.append("")
                lines.append("   **Fix:**")
                for line in fault.recommendation.split('\n'):
                    lines.append(f"   {line}")

                if fault.file_path:
                    lines.append(f"   **File:** `{fault.file_path}`")

                lines.append("")
        else:
            lines.append("No issues detected! ✅")

        return "\n".join(lines)

    def get_fault_priority(self, fault: Fault) -> int:
        """
        Get priority score for a fault (higher = more urgent).

        Args:
            fault: Fault to score

        Returns:
            Priority score (0-10)
        """
        base_score = fault.severity.value * 3

        # Critical categories get priority boost
        if fault.category == FaultCategory.IMPLEMENTATION:
            base_score += 2
        elif fault.category == FaultCategory.INTERFACE:
            base_score += 1

        return min(base_score, 10)


# Example usage for testing
if __name__ == "__main__":
    reporter = FaultDetectionReporter()

    # Test with missing orchestrator
    verification = {
        "orchestrator_exists": False,
        "file_path": None
    }

    report = reporter.detect_faults("NonExistentOrchestrator", verification)
    print(reporter.format_report(report))

    print("\n" + "="*60 + "\n")

    # Test with wiring issue
    verification2 = {
        "orchestrator_exists": True,
        "wiring_registered": False,
        "test_coverage": 0,
        "documentation": None
    }

    report2 = reporter.detect_faults("UnwiredOrchestrator", verification2)
    print(reporter.format_report(report2))
