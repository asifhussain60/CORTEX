"""
Regenerate Plan Viewers for C150 and POC Plans (Direct HTML Generator)
Holistic Review Action - 2026-01-05
"""

from pathlib import Path
import sys
import yaml

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.orchestrators.shared.html_viewer_generator import HTMLViewerGenerator, ViewerConfig, ViewerMode

def regenerate_yaml_plan_viewer(plan_path: Path, plan_name: str):
    """Regenerate plan viewer HTML for a YAML plan."""
    print(f"\n{'='*60}")
    print(f"Regenerating plan viewer: {plan_name}")
    print(f"Path: {plan_path}")
    print(f"{'='*60}\n")
    
    try:
        # Find YAML plan file
        yaml_files = list(plan_path.glob("00-*.yaml")) + list(plan_path.glob("00-*.yml"))
        if not yaml_files:
            print(f"❌ ERROR: No YAML plan file found in {plan_path}")
            return False
        
        yaml_file = yaml_files[0]
        print(f"📄 Found plan file: {yaml_file.name}")
        
        # Load YAML plan
        with open(yaml_file, 'r') as f:
            plan_data = yaml.safe_load(f)
        
        print(f"✅ Loaded plan data:")
        print(f"   Plan ID: {plan_data.get('plan_id', 'N/A')}")
        print(f"   Plan Name: {plan_data.get('plan_name', 'N/A')}")
        print(f"   Total Phases: {len(plan_data.get('phases', []))}")
        print(f"   Estimated Hours: {plan_data.get('estimated_total_hours', 'N/A')}")
        print(f"   Status: {plan_data.get('status', 'N/A')}")
        
        # Create viewer config
        config = ViewerConfig(
            title=plan_data.get('plan_name', plan_name),
            mode=ViewerMode.FEATURE,
            show_progress=True
        )
        
        # Initialize generator
        generator = HTMLViewerGenerator(config)
        
        # Generate HTML viewer
        output_path = plan_path / "plan-viewer.html"
        html_content = generator.generate_yaml_plan_viewer(plan_data)
        
        with open(output_path, 'w') as f:
            f.write(html_content)
        
        print(f"✅ SUCCESS: Plan viewer generated")
        print(f"   Location: {output_path}")
        print(f"   Size: {output_path.stat().st_size:,} bytes")
        
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
        
        success = regenerate_yaml_plan_viewer(plan["path"], plan["name"])
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
