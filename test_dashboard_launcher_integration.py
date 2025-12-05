"""
Test Dashboard Launcher Integration

Quick test to verify dashboard launcher orchestrator and module work correctly.

Author: Asif Hussain
"""

import sys
from pathlib import Path

# Add src to path
cortex_root = Path(__file__).parent
sys.path.insert(0, str(cortex_root))

from src.orchestrators.dashboard_launcher import launch_dashboard
from src.operations.modules.dashboard_launcher_module import DashboardLauncherModule


def test_orchestrator_direct():
    """Test orchestrator directly."""
    print("=" * 80)
    print("TEST 1: Direct Orchestrator Call")
    print("=" * 80)
    
    result = launch_dashboard(
        port=8080,
        auto_open=False,  # Don't open browser in test
        source="mock"
    )
    
    print(f"\nSuccess: {result['success']}")
    print(f"Message: {result['message']}")
    
    if result['success']:
        print(f"Port: {result['port']}")
        print(f"URL: {result['url']}")
        print(f"Directory: {result['directory']}")
        
        # Stop server
        if 'server' in result:
            result['server'].stop()
            print("\n✅ Server stopped successfully")
    
    return result['success']


def test_module_wrapper():
    """Test module wrapper."""
    print("\n" + "=" * 80)
    print("TEST 2: Module Wrapper Call")
    print("=" * 80)
    
    module = DashboardLauncherModule()
    
    context = {
        "port": 8081,
        "auto_open": False,
        "source": "mock"
    }
    
    result = module.execute(context)
    
    print(f"\nSuccess: {result.success}")
    print(f"Status: {result.status}")
    print(f"Message:\n{result.message}")
    
    if result.success and result.data:
        print(f"\nData: {result.data}")
    
    return result.success


def test_yaml_registration():
    """Test YAML registration."""
    print("\n" + "=" * 80)
    print("TEST 3: YAML Registration Check")
    print("=" * 80)
    
    import yaml
    
    yaml_file = cortex_root / "cortex-operations.yaml"
    
    if not yaml_file.exists():
        print(f"❌ YAML file not found: {yaml_file}")
        return False
    
    with open(yaml_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    if 'operations' not in config:
        print("❌ No 'operations' section in YAML")
        return False
    
    if 'load_dashboard' not in config['operations']:
        print("❌ 'load_dashboard' operation not found in YAML")
        return False
    
    op = config['operations']['load_dashboard']
    
    print(f"✅ Operation found: {op['name']}")
    print(f"Description: {op['description']}")
    print(f"Deployment Tier: {op['deployment_tier']}")
    print(f"Category: {op['category']}")
    print(f"\nNatural Language Triggers:")
    for trigger in op['natural_language']:
        print(f"  - {trigger}")
    
    print(f"\nModules: {op['modules']}")
    print(f"Implementation Status: {op['implementation_status']['status']}")
    
    return True


def main():
    """Run all tests."""
    print("\n🧪 CORTEX Dashboard Launcher Integration Tests\n")
    
    results = {
        "Orchestrator Direct Call": test_orchestrator_direct(),
        "Module Wrapper Call": test_module_wrapper(),
        "YAML Registration": test_yaml_registration()
    }
    
    print("\n" + "=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 80 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
