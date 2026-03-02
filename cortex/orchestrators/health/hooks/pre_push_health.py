"""Pre-push Hook - Health Warning System

Warns about health issues before push:
- Duplicates detected
- Weak implementations present
- Low health score

Does not block push, only warns.

Author: CORTEX Framework
Phase: PHASE-95 S4
CORE Rules: CORE-008 (TDD)
"""

import sys
from pathlib import Path

from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator
from cortex.orchestrators.health.agents.duplicate_detection_agent import DuplicateDetectionAgent
from cortex.orchestrators.health.agents.stub_detection_agent import StubDetectionAgent


def check_health_score(workspace_root: Path) -> None:
    """Check repository health and warn if low.
    
    Args:
        workspace_root: Repository root path
    """
    print("🔍 CORTEX Pre-Push Health Check...")
    
    orchestrator = HealthOrchestrator(workspace_root)
    
    # Register quick agents
    orchestrator.register_agent(DuplicateDetectionAgent())
    orchestrator.register_agent(StubDetectionAgent())
    
    # Run health check
    report = orchestrator.run_health_check()
    
    # Check for critical issues
    warnings = []
    
    if report.metrics.critical_issues > 0:
        warnings.append(f"🔴 {report.metrics.critical_issues} CRITICAL issues detected")
    
    if report.metrics.high_issues > 0:
        warnings.append(f"🟡 {report.metrics.high_issues} HIGH priority issues detected")
    
    if report.metrics.health_score < 80:
        warnings.append(f"⚠️  Health score: {report.metrics.health_score:.0f}/100 (below 80 threshold)")
    
    # Display warnings
    if warnings:
        print("\n⚠️  HEALTH WARNINGS (push allowed, fix recommended):\n")
        for warning in warnings:
            print(f"  {warning}")
        print(f"\nRun 'cortex health' for detailed report.")
    else:
        print(f"✅ Health check passed (score: {report.metrics.health_score:.0f}/100)")


def main() -> int:
    """Run pre-push health warnings.
    
    Returns:
        Exit code (always 0 - warnings only)
    """
    try:
        workspace_root = Path.cwd()
        check_health_score(workspace_root)
    except Exception as e:
        print(f"⚠️  Health check failed: {e}")
    
    # Always allow push
    return 0


if __name__ == "__main__":
    sys.exit(main())
