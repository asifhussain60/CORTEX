#!/usr/bin/env python3
"""Pre-Push Hook - Comprehensive Health Report

WARNING hook that runs full health check and shows report before push.
Does not block push, but provides visibility.

Author: CORTEX Framework
Phase: PHASE-95
"""

import sys
from pathlib import Path

# Add cortex to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator
from cortex.orchestrators.health.agents import (
    DuplicateDetectionAgent,
    StubDetectionAgent,
    PathIntegrityAgent,
    VersionCleanupAgent,
    TestCoverageAgent,
    RegistryConsistencyAgent,
)


def main() -> int:
    """Run pre-push health check.
    
    Returns:
        Always returns 0 (non-blocking)
    """
    workspace_root = Path(__file__).parent.parent
    
    print("\n" + "="*60)
    print("🔍 CORTEX Pre-Push Health Report")
    print("="*60 + "\n")
    
    # Initialize orchestrator
    orchestrator = HealthOrchestrator(workspace_root)
    
    # Register all agents
    orchestrator.register_agent(DuplicateDetectionAgent())
    orchestrator.register_agent(StubDetectionAgent())
    orchestrator.register_agent(PathIntegrityAgent())
    orchestrator.register_agent(VersionCleanupAgent())
    orchestrator.register_agent(TestCoverageAgent())
    orchestrator.register_agent(RegistryConsistencyAgent())
    
    # Run health check
    try:
        report = orchestrator.run_health_check()
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}\n")
        print("⚠️  Continuing with push (check non-blocking)\n")
        return 0
    
    # Display summary
    print(f"Health Score: {report.metrics.health_score:.1f}/100")
    print(f"Total Issues: {report.metrics.total_issues}")
    print(f"  - Critical: {report.metrics.critical_issues}")
    print(f"  - High: {report.metrics.high_issues}")
    print(f"  - Medium: {report.metrics.medium_issues}")
    print(f"  - Low: {report.metrics.low_issues}\n")
    
    # Show recommendations
    if report.recommendations:
        print("Recommendations:")
        for rec in report.recommendations:
            print(f"  {rec}")
        print()
    
    # Warning for critical issues
    if report.metrics.critical_issues > 0:
        print("⚠️  WARNING: Critical issues detected!")
        print("   Pushing anyway (pre-push is non-blocking)")
        print(f"   Run: python -m cortex.orchestrators.health.cli")
        print()
    
    # Show agent summary
    print("Agent Results:")
    for result in report.agent_results:
        status = "✅" if result.issue_count == 0 else f"⚠️  ({result.issue_count})"
        print(f"  {status} {result.agent_name}")
    
    print("\n" + "="*60)
    print("Push continuing...")
    print("="*60 + "\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
