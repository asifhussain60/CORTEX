"""
CORTEX Toolkit Installation Verification

Verifies toolkit installation and configuration.
"""
import sys
from pathlib import Path

# Add shared to path
toolkit_root = Path(__file__).parent.parent
sys.path.insert(0, str(toolkit_root / "shared"))

from toolkit_registry import ToolkitRegistry
from config import get_config
import platform as plat


def verify_installation() -> bool:
    """
    Verify toolkit installation.
    
    Returns:
        True if all checks pass, False otherwise.
    """
    print("=== CORTEX Toolkit Installation Verification ===\n")
    
    all_passed = True
    
    # 1. Check toolkit root
    print("[1/6] Checking toolkit root...")
    try:
        config = get_config()
        toolkit_root = config.get_toolkit_root()
        print(f"  ✓ Toolkit root: {toolkit_root}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
        all_passed = False
    
    # 2. Check manifest
    print("\n[2/6] Checking manifest...")
    try:
        registry = ToolkitRegistry()
        print(f"  ✓ Manifest loaded")
        print(f"  ✓ Version: {registry.version}")
        print(f"  ✓ Categories: {len(registry.list_categories())}")
        print(f"  ✓ Tools: {len(registry.list_tools())}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
        all_passed = False
    
    # 3. Check Python version
    print("\n[3/6] Checking Python version...")
    version_info = sys.version_info
    if version_info >= (3, 8):
        print(f"  ✓ Python {version_info.major}.{version_info.minor}.{version_info.micro}")
    else:
        print(f"  ✗ Python {version_info.major}.{version_info.minor} (requires 3.8+)")
        all_passed = False
    
    # 4. Check platform
    print("\n[4/6] Checking platform...")
    system = plat.system()
    print(f"  ✓ Platform: {system}")
    print(f"  ✓ Architecture: {plat.machine()}")
    
    # 5. Check dependencies
    print("\n[5/6] Checking dependencies...")
    dependencies = ["yaml", "json", "pathlib"]
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"  ✓ {dep}")
        except ImportError:
            print(f"  ✗ {dep} (not found)")
            all_passed = False
    
    # 6. Check sample tools
    print("\n[6/6] Checking sample tools...")
    sample_tools = ["align", "healthcheck", "plan"]
    for tool_name in sample_tools:
        tool = registry.get_tool(tool_name)
        if tool:
            supported = registry.is_platform_supported(tool_name)
            status = "✓" if supported else "⚠"
            print(f"  {status} {tool_name} (platform: {supported})")
        else:
            print(f"  ✗ {tool_name} (not found)")
            all_passed = False
    
    # Summary
    print("\n=== Summary ===")
    if all_passed:
        print("✓ All checks passed!")
        print("\nToolkit is ready to use.")
        print(f"Run: python {toolkit_root / 'shared' / 'toolkit_registry.py'} list")
        return True
    else:
        print("✗ Some checks failed.")
        print("\nPlease fix the errors and try again.")
        return False


if __name__ == "__main__":
    success = verify_installation()
    sys.exit(0 if success else 1)
