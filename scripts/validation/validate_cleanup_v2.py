"""
End-to-End Validation: Cleanup v2 Master Orchestrator Routing

This script validates that:
1. Master Orchestrator routing patterns match user input correctly
2. Mode extraction works for all 5 cleanup modes
3. Cleanup Orchestrator v2 can be imported and initialized
4. All category cleaners are accessible
"""

import re
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_routing_pattern():
    """Test that Master Orchestrator routing pattern matches correctly."""
    pattern = r"^(cleanup|cleanup cache|cleanup logs|cleanup artifacts|cleanup full|cleanup git).*$"
    
    test_cases = [
        ("cleanup cache", True, "cache"),
        ("cleanup logs please", True, "logs"),
        ("cleanup artifacts", True, "artifacts"),
        ("cleanup full", True, "full"),
        ("cleanup git", True, "git"),
        ("cleanup", True, "full"),  # Default mode
        ("clear cache", False, None),  # Should NOT match (different verb)
        ("system maintenance", False, None),  # Should NOT match (different intent)
    ]
    
    print("=" * 80)
    print("ROUTING PATTERN VALIDATION")
    print("=" * 80)
    
    all_passed = True
    for user_input, should_match, expected_mode in test_cases:
        match = re.match(pattern, user_input, re.IGNORECASE)
        matched = match is not None
        
        if matched == should_match:
            print(f"✅ PASS: '{user_input}' -> Match={matched}")
        else:
            print(f"❌ FAIL: '{user_input}' -> Expected match={should_match}, Got={matched}")
            all_passed = False
    
    return all_passed


def test_mode_extraction():
    """Test that mode extraction regex works correctly."""
    mode_pattern = r"^cleanup\s+(cache|logs|artifacts|full|git).*$"
    default_mode = "full"
    
    test_cases = [
        ("cleanup cache", "cache"),
        ("cleanup logs please", "logs"),
        ("cleanup artifacts now", "artifacts"),
        ("cleanup full", "full"),
        ("cleanup git", "git"),
        ("cleanup", "full"),  # No mode specified -> default
        ("cleanup cache for me", "cache"),
    ]
    
    print("\n" + "=" * 80)
    print("MODE EXTRACTION VALIDATION")
    print("=" * 80)
    
    all_passed = True
    for user_input, expected_mode in test_cases:
        match = re.match(mode_pattern, user_input, re.IGNORECASE)
        extracted_mode = match.group(1) if match else default_mode
        
        if extracted_mode == expected_mode:
            print(f"✅ PASS: '{user_input}' -> Mode='{extracted_mode}'")
        else:
            print(f"❌ FAIL: '{user_input}' -> Expected='{expected_mode}', Got='{extracted_mode}'")
            all_passed = False
    
    return all_passed


def test_orchestrator_import():
    """Test that Cleanup Orchestrator v2 can be imported."""
    print("\n" + "=" * 80)
    print("ORCHESTRATOR IMPORT VALIDATION")
    print("=" * 80)
    
    try:
        from src.orchestrators.cleanup.cleanup_orchestrator_v2 import CleanupOrchestratorV2
        from src.database.planning_state_db import PlanningStateDB
        print("✅ PASS: CleanupOrchestratorV2 imported successfully")
        
        # Test initialization (without executing)
        # Note: BaseOrchestrator v4.1 requires config_path and state_db
        config_path = "cortex-brain/manifests/orchestrators/cleanup-orchestrator-v2.yaml"
        state_db = PlanningStateDB(db_path=":memory:")  # In-memory DB for testing
        
        orchestrator = CleanupOrchestratorV2(
            config_path=config_path,
            state_db=state_db
        )
        print(f"✅ PASS: CleanupOrchestratorV2 initialized successfully")
        
        # Verify execute method exists
        if hasattr(orchestrator, 'execute'):
            print(f"✅ PASS: CleanupOrchestratorV2.execute() method exists")
        else:
            print(f"❌ FAIL: CleanupOrchestratorV2.execute() method NOT FOUND")
            return False
        
        return True
    except ImportError as e:
        print(f"❌ FAIL: Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ FAIL: Initialization error: {e}")
        return False


def test_category_cleaners():
    """Test that all category cleaners can be imported."""
    print("\n" + "=" * 80)
    print("CATEGORY CLEANER IMPORT VALIDATION")
    print("=" * 80)
    
    cleaners = [
        "CacheCleaner",
        "LogManager",
        "ArtifactRemover",
        "GitOptimizer",
        "CleanupEngine",
    ]
    
    all_passed = True
    for cleaner_name in cleaners:
        try:
            module_path = f"src.orchestrators.cleanup.{cleaner_name.lower().replace('cleaner', '_cleaner').replace('manager', '_manager').replace('remover', '_remover').replace('optimizer', '_optimizer').replace('engine', '_engine')}"
            # Adjust module path for specific cleaners
            if cleaner_name == "CacheCleaner":
                module_path = "src.orchestrators.cleanup.cache_cleaner"
            elif cleaner_name == "LogManager":
                module_path = "src.orchestrators.cleanup.log_manager"
            elif cleaner_name == "ArtifactRemover":
                module_path = "src.orchestrators.cleanup.artifact_remover"
            elif cleaner_name == "GitOptimizer":
                module_path = "src.orchestrators.cleanup.git_optimizer"
            elif cleaner_name == "CleanupEngine":
                module_path = "src.orchestrators.cleanup.cleanup_engine"
            
            exec(f"from {module_path} import {cleaner_name}")
            print(f"✅ PASS: {cleaner_name} imported successfully")
        except ImportError as e:
            print(f"❌ FAIL: {cleaner_name} import error: {e}")
            all_passed = False
    
    return all_passed


def test_manifest_exists():
    """Test that manifest and templates exist."""
    print("\n" + "=" * 80)
    print("CONFIGURATION FILES VALIDATION")
    print("=" * 80)
    
    files_to_check = [
        "cortex-brain/manifests/orchestrators/cleanup-orchestrator-v2.yaml",
        "cortex-brain/templates/cleanup-report.jinja2",
        "cortex-brain/templates/log-rotation-report.jinja2",
        "cortex-brain/config/master-orchestrator.yaml",
    ]
    
    all_passed = True
    for file_path in files_to_check:
        full_path = Path(__file__).parent / file_path
        if full_path.exists():
            print(f"✅ PASS: {file_path} exists")
        else:
            print(f"❌ FAIL: {file_path} NOT FOUND")
            all_passed = False
    
    return all_passed


def main():
    """Run all validation tests."""
    print("\n" + "🔍 CLEANUP V2 END-TO-END VALIDATION")
    print("=" * 80)
    print("Testing Master Orchestrator routing, mode extraction, imports, and config\n")
    
    results = {
        "Routing Pattern": test_routing_pattern(),
        "Mode Extraction": test_mode_extraction(),
        "Orchestrator Import": test_orchestrator_import(),
        "Category Cleaners": test_category_cleaners(),
        "Configuration Files": test_manifest_exists(),
    }
    
    # Summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    
    all_passed = all(results.values())
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("=" * 80)
    if all_passed:
        print("🎉 ALL VALIDATIONS PASSED - Cleanup v2 is ready for production!")
    else:
        print("⚠️  SOME VALIDATIONS FAILED - Review errors above")
    print("=" * 80)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
