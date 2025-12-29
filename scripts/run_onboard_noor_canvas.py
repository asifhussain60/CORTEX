#!/usr/bin/env python3
"""
Run onboarding for NOOR CANVAS project
"""
import sys
from pathlib import Path

# Add CORTEX to path
cortex_root = Path(__file__).parent
sys.path.insert(0, str(cortex_root))

from src.operations.onboarding_orchestrator import OnboardingOrchestrator

def main():
    # Configuration
    cortex_root_path = Path(r"D:\PROJECTS\CORTEX")
    noor_canvas_path = Path(r"D:\PROJECTS\NOOR CANVAS")
    project_name = "NOOR-CANVAS"
    
    print("[CORTEX] Application Onboarding")
    print(f"Target Project: {noor_canvas_path}")
    print(f"Project Name: {project_name}")
    print("Starting analysis...\n")
    
    try:
        # Initialize orchestrator in TEST MODE
        # This is CORTEX testing an external repo, not embedded deployment
        orchestrator = OnboardingOrchestrator(
            cortex_root_path, 
            test_mode=True  # Outputs to onboarded-apps/ for inspection
        )
        
        # Run onboarding
        result = orchestrator.onboard_application(
            project_path=noor_canvas_path,
            project_name=project_name
        )
        
        # Display results
        print("\n" + "="*70)
        print("[SUCCESS] ONBOARDING COMPLETE")
        print("="*70)
        print(f"\nProject: {result.project_name}")
        print(f"Quality Score: {result.quality_score:.1f}/100")
        print(f"Security Issues: {result.security_issues}")
        print(f"Performance Metrics Collected: {result.performance_metrics}")
        print(f"Dashboard: {result.dashboard_url}")
        
        if result.output_path:
            print(f"\nResults stored in: {result.output_path}")
        
        if result.errors:
            print(f"\n[WARNING] Issues detected:")
            for error in result.errors:
                print(f"   - {error}")
        
        print("\nNext Steps:")
        print(f"   1. Open dashboard: {result.dashboard_url}")
        print(f"   2. Review quality issues and security vulnerabilities")
        print(f"   3. Use CORTEX for development: 'start tdd', 'plan feature', etc.")
        
        return 0 if result.success else 1
        
    except KeyboardInterrupt:
        print("\n[WARNING] Onboarding interrupted by user")
        return 130
    except Exception as e:
        print(f"\n[ERROR] Onboarding failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
