"""
Simple Plan Viewer Regenerator - Uses examples module
Holistic Review Action - 2026-01-05
"""

from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Use the examples module which has working viewer generation
from src.orchestrators.shared.examples import generate_all_plan_viewers_in_directory

def main():
    """Regenerate plan viewers for C150 and POC plans."""
    
    base_path = Path("cortex-brain/documents/planning/active")
    
    plans = [
        base_path / "c150-remediation-plan",
        base_path / "poc-python-execution"
    ]
    
    print("\n" + "="*60)
    print("REGENERATING PLAN VIEWERS")
    print("="*60 + "\n")
    
    success_count = 0
    
    for plan_path in plans:
        if not plan_path.exists():
            print(f"⚠️  SKIP: {plan_path.name} (path does not exist)")
            continue
        
        print(f"📁 Processing: {plan_path.name}")
        
        try:
            # Generate viewers for this directory
            generate_all_plan_viewers_in_directory(plan_path)
            
            # Check if viewer was created
            viewer_path = plan_path / "plan-viewer.html"
            if viewer_path.exists():
                print(f"✅ SUCCESS: plan-viewer.html ({viewer_path.stat().st_size:,} bytes)")
                success_count += 1
            else:
                print(f"⚠️  WARNING: plan-viewer.html was not created")
        
        except Exception as e:
            print(f"❌ ERROR: {type(e).__name__}: {e}")
    
    # Summary
    print(f"\n" + "="*60)
    print(f"SUMMARY: {success_count}/{len(plans)} plan viewers regenerated")
    print("="*60 + "\n")
    
    return 0 if success_count == len(plans) else 1

if __name__ == "__main__":
    sys.exit(main())
