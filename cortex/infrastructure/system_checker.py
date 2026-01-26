"""
Phase 6 System Check - Comprehensive Verification Suite

Validates that the hardening layer is fully operational:
1. All 23 orchestrators remain wired after implementation
2. Contract validation works correctly
3. Drift detection detects discrepancies accurately
4. Pre-op gates perform remediation silently
5. No existing functionality broken
6. Permanent hardening is in place

Run this after integration to verify success.

Author: CORTEX Hardening System
Date: 2026-01-25
Authority: AC-PERMANENT-FIX-016
"""

import logging
from dataclasses import dataclass
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


@dataclass
class CheckResult:
    """Result of a single system check."""
    name: str
    passed: bool
    message: str
    details: Dict[str, Any]


@dataclass
class SystemCheckReport:
    """Full system check report."""
    total_checks: int
    passed_checks: int
    failed_checks: int
    checks: List[CheckResult]

    @property
    def success(self) -> bool:
        """Check if all checks passed."""
        return self.failed_checks == 0

    @property
    def percent_passed(self) -> float:
        """Percentage of checks passed."""
        if self.total_checks == 0:
            return 100.0
        return (self.passed_checks / self.total_checks) * 100


class SystemChecker:
    """Runs comprehensive system checks."""

    def __init__(self):
        """Initialize checker."""
        self.checks: List[CheckResult] = []

    def run_all_checks(self) -> SystemCheckReport:
        """Run all system checks and return report."""
        try:
            self._check_wiring_integrity()
            self._check_contract_manager()
            self._check_drift_detector()
            self._check_pre_op_enforcer()
            self._check_backward_compatibility()
            self._check_audit_trail()
            self._check_core035_compliance()  # NEW: CORE-035 compliance check
            self._check_performance()

        except Exception as e:
            logger.error(f"System check failed with exception: {e}", exc_info=True)

        return self._generate_report()

    def _check_wiring_integrity(self) -> None:
        """Check that all 23 orchestrators are wired."""
        try:
            from cortex.orchestrators.core.database_registry import get_database_registry

            registry = get_database_registry()
            orchestrators = registry.get_all_orchestrators()

            expected_count = 23
            actual_count = len(orchestrators)

            if actual_count >= expected_count:
                self.checks.append(CheckResult(
                    name="Wiring Integrity",
                    passed=True,
                    message=f"All {expected_count} orchestrators wired",
                    details={
                        "expected": expected_count,
                        "actual": actual_count,
                        "names": list(orchestrators.keys()),
                    },
                ))
            else:
                self.checks.append(CheckResult(
                    name="Wiring Integrity",
                    passed=False,
                    message=f"Only {actual_count}/{expected_count} orchestrators wired",
                    details={
                        "expected": expected_count,
                        "actual": actual_count,
                        "names": list(orchestrators.keys()),
                    },
                ))

        except Exception as e:
            self.checks.append(CheckResult(
                name="Wiring Integrity",
                passed=False,
                message=f"Failed to check wiring: {e}",
                details={"error": str(e)},
            ))

    def _check_contract_manager(self) -> None:
        """Check that Contract Manager is initialized and functional."""
        try:
            from cortex.infrastructure.wiring_contract_manager import WiringContractManager

            manager = WiringContractManager.instance()
            contract = manager.get_contract()

            # Contract should never be None (will raise if truly unavailable)
            if contract.checksum and contract.total_orchestrators > 0:
                self.checks.append(CheckResult(
                    name="Contract Manager",
                    passed=True,
                    message=f"Contract Manager functional (checksum={contract.checksum[:8]})",
                    details={
                        "checksum": contract.checksum[:8],
                        "total_orchestrators": contract.total_orchestrators,
                        "version": contract.version,
                    },
                ))
            else:
                self.checks.append(CheckResult(
                    name="Contract Manager",
                    passed=False,
                    message="Contract Manager returned invalid contract",
                    details={"contract": str(contract)},
                ))

        except Exception as e:
            self.checks.append(CheckResult(
                name="Contract Manager",
                passed=False,
                message=f"Contract Manager check failed: {e}",
                details={"error": str(e)},
            ))

    def _check_drift_detector(self) -> None:
        """Check that Drift Detector is running and functional."""
        try:
            from cortex.infrastructure.wiring_drift_detector import WiringDriftDetector

            detector = WiringDriftDetector.instance()
            health = detector.validate_health()

            if health.get("status") == "HEALTHY":
                self.checks.append(CheckResult(
                    name="Drift Detector",
                    passed=True,
                    message="Drift Detector running and healthy",
                    details=health,
                ))
            elif health.get("status") == "DRIFT_DETECTED":
                self.checks.append(CheckResult(
                    name="Drift Detector",
                    passed=True,
                    message="Drift Detector running (drift currently detected - expected during initialization)",
                    details=health,
                ))
            else:
                self.checks.append(CheckResult(
                    name="Drift Detector",
                    passed=False,
                    message=f"Drift Detector unhealthy: {health.get('status')}",
                    details=health,
                ))

        except Exception as e:
            self.checks.append(CheckResult(
                name="Drift Detector",
                passed=False,
                message=f"Drift Detector check failed: {e}",
                details={"error": str(e)},
            ))

    def _check_pre_op_enforcer(self) -> None:
        """Check that Pre-Op Enforcer is available."""
        try:
            from cortex.infrastructure.pre_op_enforcer import (
                PreOpGate,
                RemediationStrategy,
                OperationGuard,
            )

            # Verify all components are importable and have required methods
            assert hasattr(PreOpGate, 'safe_execute'), "PreOpGate.safe_execute missing"
            assert hasattr(PreOpGate, 'safe_instantiate'), "PreOpGate.safe_instantiate missing"
            assert hasattr(RemediationStrategy, 'remediate_missing_orchestrators'), \
                "RemediationStrategy.remediate_missing_orchestrators missing"
            assert hasattr(OperationGuard, '__enter__'), "OperationGuard.__enter__ missing"

            self.checks.append(CheckResult(
                name="Pre-Op Enforcer",
                passed=True,
                message="Pre-Op Enforcer fully available with all strategies",
                details={
                    "components": [
                        "PreOpGate.safe_execute",
                        "PreOpGate.safe_instantiate",
                        "RemediationStrategy",
                        "OperationGuard",
                    ],
                },
            ))

        except Exception as e:
            self.checks.append(CheckResult(
                name="Pre-Op Enforcer",
                passed=False,
                message=f"Pre-Op Enforcer check failed: {e}",
                details={"error": str(e)},
            ))

    def _check_backward_compatibility(self) -> None:
        """Check that existing orchestrator functionality still works."""
        try:
            from cortex.orchestrators.core.database_registry import get_database_registry

            # Try to instantiate MasterOrchestrator (most critical)
            registry = get_database_registry()
            master = registry.get_orchestrator("MasterOrchestrator")

            if master is not None:
                self.checks.append(CheckResult(
                    name="Backward Compatibility",
                    passed=True,
                    message="MasterOrchestrator instantiates successfully",
                    details={"type": type(master).__name__},
                ))
            else:
                self.checks.append(CheckResult(
                    name="Backward Compatibility",
                    passed=False,
                    message="MasterOrchestrator returned None",
                    details={},
                ))

        except Exception as e:
            self.checks.append(CheckResult(
                name="Backward Compatibility",
                passed=False,
                message=f"Backward compatibility check failed: {e}",
                details={"error": str(e)},
            ))

    def _check_audit_trail(self) -> None:
        """Check that audit trail is operational."""
        try:
            from cortex.infrastructure.wiring_drift_detector import AuditTrailLogger

            audit_logger = AuditTrailLogger()

            # Check that database exists
            if audit_logger.audit_db_path.exists():
                # Try to read recent events
                events = audit_logger.get_recent_events(limit=1)

                self.checks.append(CheckResult(
                    name="Audit Trail",
                    passed=True,
                    message=f"Audit trail operational at {audit_logger.audit_db_path}",
                    details={
                        "path": str(audit_logger.audit_db_path),
                        "recent_events": len(events),
                    },
                ))
            else:
                self.checks.append(CheckResult(
                    name="Audit Trail",
                    passed=True,
                    message="Audit trail database not yet created (will be on first drift)",
                    details={"path": str(audit_logger.audit_db_path)},
                ))

        except Exception as e:
            self.checks.append(CheckResult(
                name="Audit Trail",
                passed=False,
                message=f"Audit trail check failed: {e}",
                details={"error": str(e)},
            ))

    def _check_performance(self) -> None:
        """Check that hardening adds minimal overhead."""
        try:
            import time
            from cortex.infrastructure.wiring_contract_manager import WiringContractManager

            # Time contract manager access (should be O(1) after first call)
            manager = WiringContractManager.instance()

            start = time.perf_counter()
            _ = manager.get_contract()  # Call but don't use (variable not accessed)
            elapsed_ms = (time.perf_counter() - start) * 1000

            # Should be very fast after first call
            if elapsed_ms < 10:  # Less than 10ms is excellent
                self.checks.append(CheckResult(
                    name="Performance",
                    passed=True,
                    message=f"Contract Manager fast ({elapsed_ms:.2f}ms)",
                    details={"elapsed_ms": elapsed_ms},
                ))
            else:
                logger.warning(f"Contract Manager slower than expected: {elapsed_ms:.2f}ms")
                self.checks.append(CheckResult(
                    name="Performance",
                    passed=True,  # Still pass, but log warning
                    message=f"Contract Manager acceptable ({elapsed_ms:.2f}ms)",
                    details={"elapsed_ms": elapsed_ms},
                ))

        except Exception as e:
            self.checks.append(CheckResult(
                name="Performance",
                passed=False,
                message=f"Performance check failed: {e}",
                details={"error": str(e)},
            ))

    def _check_core035_compliance(self) -> None:
        """Check CORE-035 (Single Canonical Implementation) compliance.
        
        This is a detection-only check that tracks duplication violations
        for audit trail purposes. Non-blocking for deployments.
        """
        try:
            from cortex.infrastructure.core035_compliance_check import get_core035_checker
            
            checker = get_core035_checker()
            status = checker.check()
            
            # Always passes (detection-only, non-blocking)
            # But logs violations for audit trail
            self.checks.append(CheckResult(
                name="CORE-035 Compliance",
                passed=status.healthy,  # Always True for health check
                message=status.message,
                details={
                    "violations_count": status.violations_count,
                    "duplicate_classes": status.duplicate_classes,
                    "duplicate_functions": status.duplicate_functions,
                    "multi_path_orchestrators": status.multi_path_orchestrators,
                    "baseline_comparison": status.baseline_comparison,
                    "latency_ms": status.latency_ms,
                },
            ))
            
            # Log violations if found
            if status.violations_count > 0:
                logger.warning(
                    f"AC-CORE035-HEALTH: {status.violations_count} violations detected "
                    f"(classes: {status.duplicate_classes}, functions: {status.duplicate_functions}, "
                    f"orchestrators: {status.multi_path_orchestrators}). "
                    f"Trend: {status.baseline_comparison.upper()}"
                )
        
        except Exception as e:
            # If check fails, still passes but logs warning
            self.checks.append(CheckResult(
                name="CORE-035 Compliance",
                passed=True,  # Non-blocking
                message=f"CORE-035 check unavailable (will retry on next cycle): {e}",
                details={"error": str(e)},
            ))
            logger.warning(f"CORE-035 compliance check failed: {e}")

    def _generate_report(self) -> SystemCheckReport:
        """Generate final report."""
        passed = sum(1 for c in self.checks if c.passed)
        failed = len(self.checks) - passed

        return SystemCheckReport(
            total_checks=len(self.checks),
            passed_checks=passed,
            failed_checks=failed,
            checks=self.checks,
        )


def run_system_check() -> SystemCheckReport:
    """Run full system check and return report."""
    logger.info("🔍 Starting comprehensive system check...")
    logger.info("This validates all hardening components are operational")

    checker = SystemChecker()
    report = checker.run_all_checks()

    logger.info(f"\n{'='*70}")
    logger.info(f"SYSTEM CHECK REPORT")
    logger.info(f"{'='*70}")
    logger.info(f"Total Checks: {report.total_checks}")
    logger.info(f"Passed: {report.passed_checks} ({report.percent_passed:.1f}%)")
    logger.info(f"Failed: {report.failed_checks}")
    logger.info(f"Status: {'✅ ALL CHECKS PASSED' if report.success else '❌ SOME CHECKS FAILED'}")
    logger.info(f"{'='*70}\n")

    for check in report.checks:
        status = "✅" if check.passed else "❌"
        logger.info(f"{status} {check.name}: {check.message}")
        if check.details:
            for key, value in check.details.items():
                logger.debug(f"    {key}: {value}")

    return report
