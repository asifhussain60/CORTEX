"""
Regenerate Plan Viewers for C150 and POC Plans
Holistic Review Action - 2026-01-05
"""

from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.orchestrators.planning.dual_mode_integration import DualModePlanningOrchestrator

def regenerate_plan_viewer(plan_path: Path, plan_name: str):
    """Regenerate plan viewer HTML for a given plan."""
    print(f"\n{'='*60}")
    print(f"Regenerating plan viewer: {plan_name}")
    print(f"Path: {plan_path}")
    print(f"{'='*60}\n")
    
    try:
        # Create orchestrator instance
        orchestrator = DualModePlanningOrchestrator(plan_path=plan_path)
        
        # Generate HTML viewer
        viewer_path = orchestrator.generate_html_viewer()
        
        print(f"✅ SUCCESS: Plan viewer generated")
        print(f"   Location: {viewer_path}")
        print(f"   Size: {viewer_path.stat().st_size:,} bytes")
        
        # Verify launch script exists
        launch_script = plan_path / "launch_plan_viewer.py"
        if launch_script.exists():
            print(f"✅ Launch script exists: {launch_script}")
        else:
            print(f"⚠️  Launch script missing: {launch_script}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Regenerate plan viewers for C150 and POC plans."""
    
    base_path = Path("cortex-brain/documents/planning/active")
    
    plans = [
        {
            "path": base_path / "c150-remediation-plan",
            "name": "C150 Remediation Plan"
        },
        {
            "path": base_path / "poc-python-execution",
            "name": "POC Python Execution Plan"
        }
    ]
    
    results = []
    
    for plan in plans:
        if not plan["path"].exists():
            print(f"⚠️  WARNING: Plan path does not exist: {plan['path']}")
            results.append(False)
            continue
        
        success = regenerate_plan_viewer(plan["path"], plan["name"])
        results.append(success)
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}\n")
    
    for i, plan in enumerate(plans):
        status = "✅ SUCCESS" if results[i] else "❌ FAILED"
        print(f"{status}: {plan['name']}")
    
    total_success = sum(results)
    print(f"\nTotal: {total_success}/{len(plans)} plan viewers regenerated successfully")
    
    if total_success == len(plans):
        print("\n🎉 All plan viewers regenerated successfully!")
        return 0
    else:
        print("\n⚠️  Some plan viewers failed to regenerate. Check errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
