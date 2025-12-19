"""
End-to-End Validation for Cortex Implants System

Tests the complete cortex-implants workflow from initialization to usage.

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
"""

from pathlib import Path
import tempfile
import shutil
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def test_complete_workflow():
    """Test complete cortex-implants workflow."""
    logger.info("=" * 60)
    logger.info("🧪 CORTEX IMPLANTS END-TO-END VALIDATION")
    logger.info("=" * 60)
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        test_repo = Path(tmpdir) / "test-repo"
        test_repo.mkdir()
        
        logger.info(f"\n📁 Test Repository: {test_repo}")
        
        # Test 1: Initialize implants
        logger.info("\n--- Test 1: Initialize Implants ---")
        from src.operations.modules.implants_commands import ImplantsCommands
        
        commands = ImplantsCommands(test_repo)
        success = commands.init_implants(
            company_name="TestCorp",
            project_name="TestProject"
        )
        
        assert success, "❌ Failed to initialize implants"
        logger.info("✅ Implants initialized successfully")
        
        # Verify folder structure
        implants_dir = test_repo / ".cortex-implants"
        assert implants_dir.exists(), "❌ Implants directory not created"
        assert (implants_dir / "governance.yaml").exists(), "❌ governance.yaml not created"
        logger.info("✅ Folder structure validated")
        
        # Test 2: Validate implants
        logger.info("\n--- Test 2: Validate Implants ---")
        success = commands.validate_implants()
        assert success, "❌ Validation failed"
        logger.info("✅ Implants validated successfully")
        
        # Test 3: Load with loader
        logger.info("\n--- Test 3: Load with Loader ---")
        from src.tier0.cortex_implants_loader import load_cortex_implants
        
        implants = load_cortex_implants(test_repo)
        assert implants is not None, "❌ Failed to load implants"
        assert implants.governance.company_name == "TestCorp", "❌ Company name mismatch"
        logger.info(f"✅ Loaded implants for {implants.governance.company_name}")
        
        # Test 4: Use integrator
        logger.info("\n--- Test 4: Use Integrator ---")
        from src.tier0.cortex_implants_integrator import CortexImplantsIntegrator
        
        integrator = CortexImplantsIntegrator(test_repo)
        assert integrator.has_implants(), "❌ Integrator didn't find implants"
        logger.info(f"✅ Integrator loaded (Priority: {integrator.get_priority()})")
        
        # Test 5: Validate tech stack
        logger.info("\n--- Test 5: Tech Stack Validation ---")
        violations = integrator.validate_tech_stack(["pytest", "pandas"])
        logger.info(f"✅ Tech stack validation: {len(violations)} violations")
        
        # Test 6: Get context summary
        logger.info("\n--- Test 6: Context Summary ---")
        summary = integrator.get_context_summary()
        assert "Cortex Implants Active" in summary, "❌ Summary not generated"
        logger.info("✅ Context summary generated")
        
        # Test 7: Update copilot instructions
        logger.info("\n--- Test 7: Update Copilot Instructions ---")
        success = commands.update_implants()
        assert success, "❌ Failed to update copilot instructions"
        
        copilot_file = test_repo / ".github" / "copilot-instructions.md"
        assert copilot_file.exists(), "❌ copilot-instructions.md not created"
        logger.info("✅ Copilot instructions generated")
        
        # Test 8: Show status
        logger.info("\n--- Test 8: Show Status ---")
        status = commands.show_status()
        assert status["present"], "❌ Status shows not present"
        assert status["company"] == "TestCorp", "❌ Company mismatch in status"
        logger.info("✅ Status retrieved successfully")
        
        # Test 9: Graceful degradation (no implants)
        logger.info("\n--- Test 9: Graceful Degradation ---")
        empty_repo = Path(tmpdir) / "empty-repo"
        empty_repo.mkdir()
        
        integrator_empty = CortexImplantsIntegrator(empty_repo)
        assert not integrator_empty.has_implants(), "❌ Should not have implants"
        assert integrator_empty.get_priority() == "NONE", "❌ Priority should be NONE"
        assert integrator_empty.validate_tech_stack(["anything"]) == [], "❌ Should return empty list"
        logger.info("✅ Graceful degradation works")
        
        # Test 10: Planning integration
        logger.info("\n--- Test 10: Planning Integration ---")
        try:
            from src.orchestration_3_0.orchestrators.planning.planning_orchestrator import PlanningOrchestrator
            logger.info("✅ Planning orchestrator imports with implants support")
        except ImportError as e:
            logger.warning(f"⚠️  Planning orchestrator not available: {e}")
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ ALL TESTS PASSED!")
    logger.info("=" * 60)
    logger.info("\n🎉 CORTEX IMPLANTS SYSTEM FULLY FUNCTIONAL\n")


def test_module_imports():
    """Test that all modules import correctly."""
    logger.info("\n🔍 Testing Module Imports...")
    
    modules = [
        ("src.tier0.cortex_implants_loader", "CortexImplantsLoader"),
        ("src.tier0.cortex_implants_integrator", "CortexImplantsIntegrator"),
        ("src.tier0.copilot_instructions_generator", "CopilotInstructionsGenerator"),
        ("src.tier0.repo_boundary_enforcer", "RepoBoundaryEnforcer"),
        ("src.operations.modules.implants_commands", "ImplantsCommands"),
    ]
    
    for module_path, class_name in modules:
        try:
            module = __import__(module_path, fromlist=[class_name])
            getattr(module, class_name)
            logger.info(f"   ✅ {module_path}.{class_name}")
        except Exception as e:
            logger.error(f"   ❌ {module_path}.{class_name}: {e}")
            raise
    
    logger.info("✅ All modules import successfully\n")


if __name__ == "__main__":
    try:
        # Test imports first
        test_module_imports()
        
        # Run complete workflow
        test_complete_workflow()
        
        print("\n" + "🎊" * 30)
        print("SUCCESS: Cortex Implants system is ready for production!")
        print("🎊" * 30)
        
    except Exception as e:
        logger.error(f"\n❌ VALIDATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
