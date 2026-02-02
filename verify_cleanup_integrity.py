#!/usr/bin/env python
"""
Verify that cleanup did not break MAJOR functionality.

Tests:
1. Core orchestrator imports
2. MCP tool exposure
3. CLI command availability
4. Dashboard infrastructure
5. Company/dashboards preservation
"""

import sys
from pathlib import Path

# Add workspace to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test critical import paths."""
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Import core orchestrators
    try:
        from cortex.orchestrators.support.repository_onboarding_orchestrator import (
            RepositoryOnboardingOrchestrator,
            get_repository_onboarding_orchestrator,
        )
        print("✅ repository_onboarding_orchestrator imports OK")
        tests_passed += 1
    except Exception as e:
        print(f"❌ repository_onboarding_orchestrator import failed: {e}")
        tests_failed += 1

    # Test 2: Import lens orchestrator
    try:
        from cortex.orchestrators.support.lens_orchestrator import LENSOrchestrator
        print("✅ lens_orchestrator imports OK")
        tests_passed += 1
    except Exception as e:
        print(f"❌ lens_orchestrator import failed: {e}")
        tests_failed += 1

    # Test 3: Import context assembly
    try:
        from cortex.orchestrators.support.context_assembly_orchestrator import (
            ContextAssemblyOrchestrator,
        )
        print("✅ context_assembly_orchestrator imports OK")
        tests_passed += 1
    except Exception as e:
        print(f"❌ context_assembly_orchestrator import failed: {e}")
        tests_failed += 1

    # Test 4: Import MCP onboarding tools
    try:
        from cortex.mcp.tools.onboarding_tools import cortex_onboard_repository
        print("✅ MCP onboarding_tools imports OK")
        tests_passed += 1
    except Exception as e:
        print(f"❌ MCP onboarding_tools import failed: {e}")
        tests_failed += 1

    # Test 5: Import CLI onboard command
    try:
        from cortex.cli.commands.onboard import onboard_repo
        print("✅ CLI onboard command imports OK")
        tests_passed += 1
    except Exception as e:
        print(f"❌ CLI onboard command import failed: {e}")
        tests_failed += 1

    return tests_passed, tests_failed


def verify_preserved_assets():
    """Verify critical assets are preserved."""
    preserved = []
    missing = []
    
    critical_files = [
        "company/dashboards/kashkole/dashboard.html",
        "company/dashboards/kashkole/enhance_dashboard.py",
        "company/dashboards/kashkole/generate_dashboard_suite.py",
        "cortex/orchestrators/support/repository_onboarding_orchestrator.py",
        "cortex/orchestrators/support/lens_orchestrator.py",
        "cortex/orchestrators/support/context_assembly_orchestrator.py",
        "cortex/mcp/tools/onboarding_tools.py",
        "cortex/cli/commands/onboard.py",
    ]
    
    base_path = Path(__file__).parent
    for file_path in critical_files:
        full_path = base_path / file_path
        if full_path.exists():
            preserved.append(file_path)
        else:
            missing.append(file_path)
    
    for f in preserved:
        print(f"✅ Preserved: {f}")
    
    for f in missing:
        print(f"❌ MISSING: {f}")
    
    return len(preserved), len(missing)


def check_deleted_files():
    """Verify old files are actually deleted."""
    deleted_correctly = []
    not_deleted = []
    
    deleted_files = [
        "cortex/orchestrators/support/universal_dashboard_generator.py",
        "cortex/orchestrators/support/domain_dashboard_generator.py",
        "cortex/orchestrators/support/dashboard_asset_manager.py",
        "cortex/orchestrators/support/landing_page_generator.py",
        "company/dashboards/generate_modern_kashkole.py",
        "company/dashboards/quick_generate_dashboard.py",
    ]
    
    base_path = Path(__file__).parent
    for file_path in deleted_files:
        full_path = base_path / file_path
        if not full_path.exists():
            deleted_correctly.append(file_path)
        else:
            not_deleted.append(file_path)
    
    for f in deleted_correctly:
        print(f"✅ Deleted: {f}")
    
    for f in not_deleted:
        print(f"⚠️  NOT DELETED: {f}")
    
    return len(deleted_correctly), len(not_deleted)


if __name__ == "__main__":
    print("=" * 60)
    print("🏗️ CORTEX Cleanup Integrity Verification")
    print("=" * 60)
    
    print("\n📋 Testing Critical Import Paths...")
    print("-" * 60)
    passed, failed = test_imports()
    
    print(f"\n📊 Preserved Critical Assets...")
    print("-" * 60)
    preserved_count, missing_count = verify_preserved_assets()
    
    print(f"\n🗑️  Verification of Deleted Files...")
    print("-" * 60)
    deleted_count, not_deleted_count = check_deleted_files()
    
    print("\n" + "=" * 60)
    print("✅ VERIFICATION SUMMARY")
    print("=" * 60)
    print(f"✅ Imports passing: {passed}/{passed + failed}")
    print(f"✅ Critical assets preserved: {preserved_count}")
    print(f"✅ Old files deleted: {deleted_count}")
    
    if failed == 0 and missing_count == 0 and not_deleted_count == 0:
        print("\n🎯 RESULT: ✅ CLEANUP VERIFICATION PASSED")
        print("   → No major functionality was deleted")
        print("   → All critical infrastructure remains intact")
        print("   → Old deprecated code successfully removed")
        sys.exit(0)
    else:
        print("\n⚠️  RESULT: Issues detected during verification")
        if failed > 0:
            print(f"   → {failed} import path(s) broken")
        if missing_count > 0:
            print(f"   → {missing_count} critical asset(s) missing")
        if not_deleted_count > 0:
            print(f"   → {not_deleted_count} old file(s) not deleted")
        sys.exit(1)
