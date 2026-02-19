#!/usr/bin/env python3
"""Pre-Commit Hook - Health Check

BLOCKING hook that runs health check and fails if critical issues detected.
Integrated with CORTEX health agent architecture.

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
    """Run pre-commit health check with DoD gate.
    
    Returns:
        0 if passed, 1 if critical issues found or DoD failed
    """
    workspace_root = Path(__file__).parent.parent
    
    print("🔍 Running CORTEX health check...")
    
    # Initialize orchestrator
    orchestrator = HealthOrchestrator(workspace_root)
    
    # Register all agents
    orchestrator.register_agent(DuplicateDetectionAgent())
    orchestrator.register_agent(StubDetectionAgent())
    orchestrator.register_agent(PathIntegrityAgent())
    orchestrator.register_agent(VersionCleanupAgent())
    orchestrator.register_agent(TestCoverageAgent())
    orchestrator.register_agent(RegistryConsistencyAgent())
    
    # Run Definition of Done (DoD) gate check
    try:
        dod_result = orchestrator.check_definition_of_done(min_score=80.0)
    except Exception as e:
        print(f"❌ DoD check failed: {str(e)}")
        return 1
    
    # Check DoD gate
    if not dod_result["passed"]:
        print(f"\n❌ COMMIT BLOCKED: Definition of Done (DoD) gate failed")
        print(f"   {dod_result['recommendation']}")
        print(f"   Health Score: {dod_result['health_score']:.1f}/{dod_result['min_score_required']:.1f}")
        print(f"   Total Issues: {dod_result['total_issues']}")
        print(f"   Critical Issues: {dod_result['critical_issues']}")
        
        if dod_result['blocking_failures']:
            print(f"\n   Blocking Failures:")
            for failure in dod_result['blocking_failures']:
                print(f"     🔴 {failure}")
        
        print("\n   Fix issues before committing.")
        print(f"   Run: python -m cortex.orchestrators.health.cli\n")
        return 1
    
    # DoD passed
    print(f"✅ DoD gate passed (Score: {dod_result['health_score']:.1f}/100)")
    if dod_result['total_issues'] > 0:
        print(f"   Found {dod_result['total_issues']} non-blocking issues")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
