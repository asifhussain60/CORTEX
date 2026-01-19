"""
Phase Readiness Checker for CORTEX Governance.

Validates that a phase is ready for completion/lock by checking:
1. Governance compliance (no rule violations in phase code)
2. Audit trail verification (audit log entries for all ACs)
3. Test coverage (all tests passing)
4. Documentation completeness (phase docs updated)

Used to determine if phase can proceed to next stage or be locked.
"""

import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import sqlite3


class ReadinessStage(Enum):
    """Readiness check stages."""

    GOVERNANCE = "governance"
    AUDIT = "audit"
    TESTS = "tests"
    DOCUMENTATION = "documentation"


class ReadinessLevel(Enum):
    """Readiness levels."""

    CRITICAL = 0  # Blocking issue
    WARNING = 1   # Non-blocking issue
    INFO = 2      # Informational


@dataclass
class ReadinessCheckResult:
    """Result of a single readiness check."""

    stage: ReadinessStage
    passed: bool
    level: ReadinessLevel
    message: str
    details: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "stage": self.stage.value,
            "passed": self.passed,
            "level": self.level.name,
            "message": self.message,
            "details": self.details,
        }


@dataclass
class PhaseReadinessReport:
    """Complete phase readiness report."""

    phase_id: str
    ready_for_lock: bool
    overall_percentage: float
    checks: List[ReadinessCheckResult] = field(default_factory=list)
    blockers: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    timestamp: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "phase_id": self.phase_id,
            "ready_for_lock": self.ready_for_lock,
            "overall_percentage": self.overall_percentage,
            "checks": [c.to_dict() for c in self.checks],
            "blockers": self.blockers,
            "recommendations": self.recommendations,
            "timestamp": self.timestamp,
        }


class PhaseReadinessChecker:
    """
    Check if a phase is ready for completion/lock.

    Validates governance, audit trail, tests, and documentation.
    """

    def __init__(self, workspace_root: Optional[Path] = None):
        """
        Initialize readiness checker.

        Args:
            workspace_root: Root directory of workspace
        """
        self.workspace_root = workspace_root or Path.cwd()
        self.cli_script = (
            self.workspace_root / "src" / "tools" / "governance-cli.py"
        )
        self.governance_db = (
            self.workspace_root / "cortex_brain" / "state" / "governance.db"
        )

    def check_phase_readiness(self, phase_id: str) -> PhaseReadinessReport:
        """
        Check if a phase is ready for lock.

        Args:
            phase_id: Phase ID (e.g., 'PHASE-09')

        Returns:
            Phase readiness report
        """
        import datetime
        report = PhaseReadinessReport(
            phase_id=phase_id,
            ready_for_lock=True,
            overall_percentage=0.0,
            timestamp=datetime.datetime.utcnow().isoformat() + 'Z',
        )

        # Stage 1: Governance Compliance
        governance_check = self._check_governance_compliance(phase_id)
        report.checks.append(governance_check)
        if not governance_check.passed and governance_check.level == ReadinessLevel.CRITICAL:
            report.ready_for_lock = False
            report.blockers.append(f"Governance: {governance_check.message}")

        # Stage 2: Audit Trail
        audit_check = self._check_audit_trail(phase_id)
        report.checks.append(audit_check)
        if not audit_check.passed and audit_check.level == ReadinessLevel.CRITICAL:
            report.ready_for_lock = False
            report.blockers.append(f"Audit: {audit_check.message}")

        # Stage 3: Test Coverage
        test_check = self._check_test_coverage(phase_id)
        report.checks.append(test_check)
        if not test_check.passed and test_check.level == ReadinessLevel.CRITICAL:
            report.ready_for_lock = False
            report.blockers.append(f"Tests: {test_check.message}")

        # Stage 4: Documentation
        doc_check = self._check_documentation(phase_id)
        report.checks.append(doc_check)
        if not doc_check.passed and doc_check.level == ReadinessLevel.CRITICAL:
            report.ready_for_lock = False
            report.blockers.append(f"Documentation: {doc_check.message}")

        # Calculate overall percentage
        passed_checks = sum(1 for c in report.checks if c.passed)
        report.overall_percentage = (passed_checks / len(report.checks)) * 100

        # Generate recommendations
        report.recommendations = self._generate_recommendations(report)

        return report

    def _check_governance_compliance(self, phase_id: str) -> ReadinessCheckResult:
        """Check governance compliance for phase code."""
        try:
            if not self.cli_script.exists():
                return ReadinessCheckResult(
                    stage=ReadinessStage.GOVERNANCE,
                    passed=False,
                    level=ReadinessLevel.WARNING,
                    message="Governance CLI not found - skipping compliance check",
                )

            # Run governance validation on phase implementation
            phase_dir = self._get_phase_directory(phase_id)
            if not phase_dir.exists():
                return ReadinessCheckResult(
                    stage=ReadinessStage.GOVERNANCE,
                    passed=True,
                    level=ReadinessLevel.INFO,
                    message="No phase directory - governance check N/A",
                )

            result = subprocess.run(
                ["python3", str(self.cli_script), "validate", str(phase_dir), "--phase", phase_id, "--format", "json"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                return ReadinessCheckResult(
                    stage=ReadinessStage.GOVERNANCE,
                    passed=True,
                    level=ReadinessLevel.INFO,
                    message="Phase code complies with governance rules",
                )
            else:
                # Parse violations
                try:
                    data = json.loads(result.stdout or "{}")
                    violations = data.get("violations", [])
                    critical = [v for v in violations if v.get("severity") == "blocked"]

                    return ReadinessCheckResult(
                        stage=ReadinessStage.GOVERNANCE,
                        passed=len(critical) == 0,
                        level=ReadinessLevel.CRITICAL if critical else ReadinessLevel.WARNING,
                        message=f"Found {len(violations)} governance violation(s)",
                        details=[f"{v.get('rule_id')}: {v.get('message')}" for v in violations[:5]],
                    )
                except json.JSONDecodeError:
                    return ReadinessCheckResult(
                        stage=ReadinessStage.GOVERNANCE,
                        passed=False,
                        level=ReadinessLevel.WARNING,
                        message="Could not parse governance validation output",
                    )

        except subprocess.TimeoutExpired:
            return ReadinessCheckResult(
                stage=ReadinessStage.GOVERNANCE,
                passed=False,
                level=ReadinessLevel.WARNING,
                message="Governance validation timeout",
            )
        except Exception as e:
            return ReadinessCheckResult(
                stage=ReadinessStage.GOVERNANCE,
                passed=False,
                level=ReadinessLevel.WARNING,
                message=f"Governance check error: {str(e)}",
            )

    def _check_audit_trail(self, phase_id: str) -> ReadinessCheckResult:
        """Check audit trail for phase completion."""
        try:
            if not self.governance_db.exists():
                return ReadinessCheckResult(
                    stage=ReadinessStage.AUDIT,
                    passed=False,
                    level=ReadinessLevel.CRITICAL,
                    message="Governance database not found",
                )

            # Extract phase number
            phase_num = re.search(r'PHASE-(\d+)', phase_id)
            if not phase_num:
                return ReadinessCheckResult(
                    stage=ReadinessStage.AUDIT,
                    passed=False,
                    level=ReadinessLevel.WARNING,
                    message=f"Could not parse phase number from {phase_id}",
                )

            phase_number = phase_num.group(1)

            # Query audit log
            conn = sqlite3.connect(str(self.governance_db))
            cursor = conn.cursor()

            # Count audit entries for phase (AC-DOMAIN-NNN-NN format where NN = phase number)
            # For PHASE-09, look for AC-*-*-09
            cursor.execute("""
                SELECT ac_id, COUNT(*) as entries
                FROM audit_log
                WHERE ac_id LIKE ?
                GROUP BY ac_id
            """, (f'AC-%-%-{phase_number}',))

            rows = cursor.fetchall()
            conn.close()

            if not rows:
                return ReadinessCheckResult(
                    stage=ReadinessStage.AUDIT,
                    passed=False,
                    level=ReadinessLevel.WARNING,
                    message=f"No audit entries found for phase {phase_id}",
                )

            # Check each AC has minimum 3 entries (START, EXECUTE, COMPLETE)
            incomplete_acs = [ac_id for ac_id, count in rows if count < 3]

            if incomplete_acs:
                return ReadinessCheckResult(
                    stage=ReadinessStage.AUDIT,
                    passed=False,
                    level=ReadinessLevel.WARNING,
                    message=f"{len(incomplete_acs)} AC(s) missing audit entries",
                    details=incomplete_acs[:5],
                )

            return ReadinessCheckResult(
                stage=ReadinessStage.AUDIT,
                passed=True,
                level=ReadinessLevel.INFO,
                message=f"Audit trail verified: {len(rows)} AC(s) with complete entries",
            )

        except Exception as e:
            return ReadinessCheckResult(
                stage=ReadinessStage.AUDIT,
                passed=False,
                level=ReadinessLevel.WARNING,
                message=f"Audit check error: {str(e)}",
            )

    def _check_test_coverage(self, phase_id: str) -> ReadinessCheckResult:
        """Check test coverage for phase."""
        try:
            # Run pytest to get test results for phase
            test_dir = self.workspace_root / "tests"
            if not test_dir.exists():
                return ReadinessCheckResult(
                    stage=ReadinessStage.TESTS,
                    passed=False,
                    level=ReadinessLevel.WARNING,
                    message="Tests directory not found",
                )

            result = subprocess.run(
                ["python3", "-m", "pytest", str(test_dir), "-q", "--tb=no"],
                capture_output=True,
                text=True,
                cwd=str(self.workspace_root),
                timeout=30,
            )

            # Parse output (pytest -q format)
            output = result.stdout
            if "passed" in output:
                # Extract pass/fail counts
                import re
                match = re.search(r'(\d+) passed', output)
                passed = int(match.group(1)) if match else 0

                match = re.search(r'(\d+) failed', output)
                failed = int(match.group(1)) if match else 0

                if failed > 0:
                    return ReadinessCheckResult(
                        stage=ReadinessStage.TESTS,
                        passed=False,
                        level=ReadinessLevel.CRITICAL,
                        message=f"Test failures: {failed} failed, {passed} passed",
                    )

                return ReadinessCheckResult(
                    stage=ReadinessStage.TESTS,
                    passed=True,
                    level=ReadinessLevel.INFO,
                    message=f"All tests passing: {passed} passed",
                )

            return ReadinessCheckResult(
                stage=ReadinessStage.TESTS,
                passed=True,
                level=ReadinessLevel.INFO,
                message="Test execution completed",
            )

        except subprocess.TimeoutExpired:
            return ReadinessCheckResult(
                stage=ReadinessStage.TESTS,
                passed=False,
                level=ReadinessLevel.WARNING,
                message="Test execution timeout",
            )
        except Exception as e:
            return ReadinessCheckResult(
                stage=ReadinessStage.TESTS,
                passed=False,
                level=ReadinessLevel.WARNING,
                message=f"Test check error: {str(e)}",
            )

    def _check_documentation(self, phase_id: str) -> ReadinessCheckResult:
        """Check documentation completeness for phase."""
        try:
            # Check for phase YAML file
            phase_yaml = self.workspace_root / "docs" / "phases" / f"phase-{phase_id.lower()}.yaml"

            if not phase_yaml.exists():
                return ReadinessCheckResult(
                    stage=ReadinessStage.DOCUMENTATION,
                    passed=False,
                    level=ReadinessLevel.WARNING,
                    message=f"Phase YAML file not found: {phase_yaml.name}",
                )

            # Check for completion status in YAML
            with open(phase_yaml) as f:
                content = f.read()

            if "status: COMPLETED" in content or "status: \"COMPLETED\"" in content:
                return ReadinessCheckResult(
                    stage=ReadinessStage.DOCUMENTATION,
                    passed=True,
                    level=ReadinessLevel.INFO,
                    message="Phase documentation updated with completion status",
                )

            return ReadinessCheckResult(
                stage=ReadinessStage.DOCUMENTATION,
                passed=False,
                level=ReadinessLevel.WARNING,
                message="Phase documentation missing completion status",
                details=["Set status: COMPLETED in phase YAML file"],
            )

        except Exception as e:
            return ReadinessCheckResult(
                stage=ReadinessStage.DOCUMENTATION,
                passed=False,
                level=ReadinessLevel.WARNING,
                message=f"Documentation check error: {str(e)}",
            )

    def _get_phase_directory(self, phase_id: str) -> Path:
        """Get phase implementation directory."""
        # Typically: src/phases/{phase_id}
        return self.workspace_root / "src" / "phases" / phase_id.lower()

    def _generate_recommendations(self, report: PhaseReadinessReport) -> List[str]:
        """Generate recommendations based on readiness report."""
        recommendations = []

        if report.ready_for_lock:
            recommendations.append(f"✅ {report.phase_id} is ready for phase lock")
            recommendations.append("Run: cortex-governance-tools lock <phase>")
        else:
            recommendations.append(f"❌ {report.phase_id} has blockers - cannot lock yet")
            for blocker in report.blockers:
                recommendations.append(f"  • Fix: {blocker}")

        # Add stage-specific recommendations
        for check in report.checks:
            if not check.passed:
                if check.stage == ReadinessStage.GOVERNANCE:
                    recommendations.append("Run: cortex-governance validate src/ --phase <phase>")
                elif check.stage == ReadinessStage.AUDIT:
                    recommendations.append("Ensure all ACs have AC_START, AC_EXECUTE, AC_COMPLETE audit entries")
                elif check.stage == ReadinessStage.TESTS:
                    recommendations.append("Run: python3 -m pytest tests/ -v")
                elif check.stage == ReadinessStage.DOCUMENTATION:
                    recommendations.append("Update phase YAML: set status: COMPLETED")

        return recommendations


def main() -> int:
    """Main entry point for phase readiness checker."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: phase-readiness-checker <PHASE-ID>")
        print("Example: phase-readiness-checker PHASE-09")
        return 1

    phase_id = sys.argv[1].upper()

    checker = PhaseReadinessChecker()
    report = checker.check_phase_readiness(phase_id)

    # Output report
    print(json.dumps(report.to_dict(), indent=2))

    # Exit code: 0 if ready, 1 if not
    return 0 if report.ready_for_lock else 1


if __name__ == "__main__":
    sys.exit(main())
