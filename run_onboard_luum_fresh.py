#!/usr/bin/env python3
"""
Run onboarding for Luum-Fresh project (MVC web app with SQL database)
Collects comprehensive data including UI details for dashboard visualization
"""
import sys
from pathlib import Path

# Add CORTEX to path
cortex_root = Path(__file__).parent
sys.path.insert(0, str(cortex_root))

from src.operations.onboarding_orchestrator import OnboardingOrchestrator

def main():
    # Configuration
    cortex_root_path = Path(r"C:\PROJECTS\CORTEX")
    luum_fresh_path = Path(r"C:\PROJECTS\luum-fresh")
    project_name = "luum-fresh"
    
    print("="*70)
    print("[CORTEX] Application Onboarding - Enhanced Dashboard Data Collection")
    print("="*70)
    print(f"\nTarget Project: {luum_fresh_path}")
    print(f"Project Name: {project_name}")
    print(f"Project Type: MVC Web Application with SQL Database")
    print(f"\nExpected Outputs:")
    print("  - Code quality metrics")
    print("  - Security vulnerability scan")
    print("  - Architecture analysis")
    print("  - Technology stack detection")
    print("  - UI components discovery (Views, Controllers, Models)")
    print("  - Database schema analysis")
    print("  - Performance metrics")
    print("  - Interactive dashboard data files")
    print("\nStarting comprehensive analysis...\n")
    
    try:
        # Validate paths
        if not luum_fresh_path.exists():
            print(f"\n[ERROR] Project path not found: {luum_fresh_path}")
            return 1
        
        if not cortex_root_path.exists():
            print(f"\n[ERROR] CORTEX root not found: {cortex_root_path}")
            return 1
        
        # Initialize orchestrator in TEST MODE
        # This is CORTEX testing an external repo, not embedded deployment
        orchestrator = OnboardingOrchestrator(
            cortex_root_path, 
            test_mode=True  # Outputs to cortex-brain/dashboards/luum-fresh/
        )
        
        print("[Step 1/10] Initializing orchestrator...")
        print(f"  ✓ Test mode enabled")
        print(f"  ✓ Output directory: cortex-brain/dashboards/luum-fresh/")
        
        # Run onboarding with full analysis
        print("\n[Step 2/10] Running comprehensive analysis...")
        result = orchestrator.onboard_application(
            project_path=luum_fresh_path,
            project_name=project_name
        )
        
        # Display results
        print("\n" + "="*70)
        if result.success:
            print("[SUCCESS] ONBOARDING COMPLETE - DATA COLLECTION FINISHED")
        else:
            print("[PARTIAL SUCCESS] ONBOARDING COMPLETED WITH WARNINGS")
        print("="*70)
        
        print(f"\n📊 Analysis Results:")
        print(f"   Project Name: {result.project_name}")
        print(f"   Timestamp: {result.analysis_timestamp}")
        print(f"   Quality Score: {result.quality_score:.1f}/100")
        print(f"   Security Issues: {result.security_issues}")
        print(f"   Performance Metrics: {result.performance_metrics}")
        
        if result.output_path:
            print(f"\n📁 Output Location:")
            print(f"   {result.output_path}")
            print(f"\n   Generated Files:")
            if result.output_path.exists():
                for file in sorted(result.output_path.glob('*.json')):
                    size_kb = file.stat().st_size / 1024
                    print(f"      ✓ {file.name} ({size_kb:.1f} KB)")
        
        print(f"\n🌐 Dashboard URL:")
        print(f"   {result.dashboard_url}")
        
        if result.errors:
            print(f"\n⚠️  Issues Detected:")
            for error in result.errors:
                print(f"      - {error}")
        
        print("\n" + "="*70)
        print("Next Steps:")
        print("="*70)
        print(f"   1. Open dashboard: {result.dashboard_url}")
        print(f"   2. Review UI components in architecture view")
        print(f"   3. Check database schema analysis")
        print(f"   4. Review security vulnerabilities")
        print(f"   5. Analyze performance bottlenecks")
        print(f"   6. Use CORTEX for development:")
        print(f"      - 'start tdd' - Begin test-driven development")
        print(f"      - 'plan feature [name]' - Plan new features")
        print(f"      - 'analyze [file]' - Deep code analysis")
        print(f"   7. Data files ready for dashboard visualization")
        
        print("\n" + "="*70)
        print(f"[CORTEX] Data collection complete for {project_name}")
        print("="*70 + "\n")
        
        return 0 if result.success else 1
        
    except KeyboardInterrupt:
        print("\n\n[WARNING] Onboarding interrupted by user")
        print("Partial results may be available in output directory")
        return 130
    except Exception as e:
        print(f"\n[ERROR] Onboarding failed: {e}")
        print("\nTroubleshooting:")
        print("  1. Check if project path exists and is accessible")
        print("  2. Verify CORTEX installation: python -m src.main --version")
        print("  3. Check Python dependencies: pip install -r requirements.txt")
        print("  4. Review logs in cortex-brain/logs/ for details")
        print("\nStack trace:")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
