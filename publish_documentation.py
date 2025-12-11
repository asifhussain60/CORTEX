"""
Publish Documentation to GitHub Pages

Final phase: Deploy all documentation including orchestration docs.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.operations.documentation_component_registry import create_default_registry

def publish_documentation(deploy=False):
    """
    Publish documentation to GitHub Pages.
    
    Args:
        deploy: If True, actually deploy to gh-pages branch. If False, dry-run only.
    """
    
    workspace_root = Path.cwd()
    registry = create_default_registry(workspace_root)
    
    print("\n🧠 Publishing Documentation to GitHub Pages")
    print("=" * 70)
    print(f"Mode: {'DEPLOY' if deploy else 'DRY-RUN'}")
    print("=" * 70)
    
    # Execute publish generator
    print("\n⚙️  Executing Publish Generator...")
    try:
        result = registry.execute(
            "publish",
            output_path=workspace_root / "docs",
            metadata={"deploy": deploy}
        )
        
        print("\n✅ Publish Results:")
        print(f"  Success: {result.get('success', False)}")
        print(f"  Build Status: {result.get('metadata', {}).get('build_status', 'Unknown')}")
        
        if deploy and result.get('success'):
            print(f"\n🌐 Documentation deployed to GitHub Pages!")
            print(f"  URL: https://asifhussain60.github.io/CORTEX/")
            print(f"  Orchestration Docs: https://asifhussain60.github.io/CORTEX/orchestration/")
        elif not deploy:
            print(f"\n📄 Dry-run complete. Site built locally in site/ directory.")
            print(f"  Run with deploy=True to publish to GitHub Pages.")
        
        if result.get('warnings'):
            print(f"\n⚠️  Warnings:")
            for warning in result['warnings']:
                print(f"  - {warning}")
        
        if result.get('errors'):
            print(f"\n❌ Errors:")
            for error in result['errors']:
                print(f"  - {error}")
        
        print("\n" + "=" * 70)
        print("✓ Publish Complete!")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Check if user wants to deploy or just test
    deploy_mode = len(sys.argv) > 1 and sys.argv[1] == "--deploy"
    
    if not deploy_mode:
        print("\n💡 Running in DRY-RUN mode (testing only)")
        print("   To actually deploy, run: python publish_documentation.py --deploy\n")
    
    success = publish_documentation(deploy=deploy_mode)
    sys.exit(0 if success else 1)
