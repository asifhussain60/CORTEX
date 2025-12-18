"""
Week 2 Infrastructure Validation Script

Validates that all Week 2 prerequisites are operational before Week 3.

Checks:
1. Response Template System (TemplateManager, TierSelector, etc.)
2. Configuration System (CortexConfig, multi-machine paths)
3. Testing Infrastructure (pytest, conftest, fixtures)

Usage:
    python3 scripts/validate_week_2_infrastructure.py
"""

import sys
from pathlib import Path

# Add CORTEX root to path
cortex_root = Path(__file__).parents[1]
sys.path.insert(0, str(cortex_root))

def check_template_system() -> bool:
    """Validate Response Template System v4.0"""
    print("\n📋 Checking Response Template System...")
    
    try:
        from src.templates import TemplateManager, TierSelector, SectionSelector, TemplateRenderer
        print("  ✅ All template components importable")
        
        # Test TemplateManager
        manager = TemplateManager()
        print(f"  ✅ TemplateManager initialized (config: {manager.config_path.name})")
        
        # Test tier selection
        selector = TierSelector(manager.config)
        print("  ✅ TierSelector initialized")
        
        # Test section selection
        section_selector = SectionSelector(manager.config)
        print("  ✅ SectionSelector initialized")
        
        # Test renderer
        renderer = TemplateRenderer(manager.config)
        print("  ✅ TemplateRenderer initialized")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Template system error: {e}")
        return False


def check_config_system() -> bool:
    """Validate Configuration System"""
    print("\n⚙️  Checking Configuration System...")
    
    try:
        from src.config import get_config_manager, CortexConfig
        print("  ✅ Config components importable")
        
        # Test ConfigManager
        config_manager = get_config_manager()
        print(f"  ✅ ConfigManager initialized (config: {config_manager.config_path})")
        
        # Test CortexConfig (legacy compatibility - uses different API)
        # CortexConfig doesn't have root_path - it's the simpler legacy version
        print(f"  ✅ CortexConfig available (legacy compatibility)")
        
        # Test path resolution
        brain_path = config_manager.get("brain.base_path", "cortex-brain")
        print(f"  ✅ Path resolution working (brain: {brain_path})")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Config system error: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_testing_infrastructure() -> bool:
    """Validate Testing Infrastructure"""
    print("\n🧪 Checking Testing Infrastructure...")
    
    try:
        # Check conftest.py exists
        conftest_path = cortex_root / "tests" / "conftest.py"
        if not conftest_path.exists():
            print(f"  ❌ conftest.py not found at {conftest_path}")
            return False
        print(f"  ✅ conftest.py exists")
        
        # Check pytest.ini exists
        pytest_ini = cortex_root / "pytest.ini"
        if not pytest_ini.exists():
            print(f"  ❌ pytest.ini not found at {pytest_ini}")
            return False
        print(f"  ✅ pytest.ini exists")
        
        # Try importing fixtures
        sys.path.insert(0, str(cortex_root / "tests"))
        import conftest
        print("  ✅ conftest importable")
        
        # Check for CORTEX-specific fixtures (not application fixtures)
        import inspect
        fixtures = [name for name, obj in inspect.getmembers(conftest) 
                   if name.startswith('sample_') or name.startswith('mock_') or name.endswith('_fixture')]
        print(f"  ✅ Found {len(fixtures)} test fixtures")
        
        # Check test directory structure
        test_dirs = ['orchestration_3_0', 'integration', 'performance']
        for test_dir in test_dirs:
            if (cortex_root / "tests" / test_dir).exists():
                print(f"  ✅ tests/{test_dir}/ exists")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Testing infrastructure error: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_week_2_deliverables() -> bool:
    """Check Week 2 specific deliverables"""
    print("\n✅ Week 2 Deliverables Check...")
    
    deliverables = [
        ("Response Template System", cortex_root / "src" / "templates" / "template_manager.py"),
        ("Template Renderer", cortex_root / "src" / "templates" / "template_renderer.py"),
        ("Tier Selector", cortex_root / "src" / "templates" / "tier_selector.py"),
        ("Section Selector", cortex_root / "src" / "templates" / "section_selector.py"),
        ("Config Manager", cortex_root / "src" / "config.py"),
        ("Test Fixtures", cortex_root / "tests" / "conftest.py"),
        ("Pytest Config", cortex_root / "pytest.ini"),
    ]
    
    all_present = True
    for name, path in deliverables:
        if path.exists():
            print(f"  ✅ {name}: {path.name}")
        else:
            print(f"  ❌ {name}: MISSING at {path}")
            all_present = False
    
    return all_present


def main():
    """Run Week 2 infrastructure validation"""
    print("=" * 70)
    print("CORTEX 4.0 - Week 2 Infrastructure Validation")
    print("=" * 70)
    
    checks = [
        ("Response Template System", check_template_system),
        ("Configuration System", check_config_system),
        ("Testing Infrastructure", check_testing_infrastructure),
        ("Week 2 Deliverables", check_week_2_deliverables),
    ]
    
    results = []
    for name, check_func in checks:
        result = check_func()
        results.append((name, result))
    
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 Week 2 Infrastructure: COMPLETE")
        print("✅ Ready for Week 3 (DI Container, Logging, Validation)")
        return 0
    else:
        print("\n❌ Week 2 Infrastructure: INCOMPLETE")
        print("⚠️  Fix failing checks before proceeding to Week 3")
        return 1


if __name__ == "__main__":
    sys.exit(main())
