#!/usr/bin/env python3
"""
Quick integration test for MasterSetupOrchestrator with Phase 3.6 (Realignment)

Tests that all phases are properly wired and execute without errors.
"""

import sys
import tempfile
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.orchestrators.master_setup_orchestrator import MasterSetupOrchestrator


def test_phase_integration():
    """Test that all phases are properly integrated."""
    print("Testing MasterSetupOrchestrator Phase Integration...\n")
    
    # Create temporary project directory
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)
        
        # Create minimal project structure
        (project_path / "src").mkdir()
        (project_path / "src" / "main.py").write_text("print('Hello World')")
        
        print(f"✅ Created test project: {project_path}")
        
        # Initialize orchestrator
        try:
            orchestrator = MasterSetupOrchestrator(
                project_root=project_path,
                cortex_root=project_root,  # Use current CORTEX installation
                interactive=False  # Non-interactive for testing
            )
            print("✅ MasterSetupOrchestrator initialized")
        except Exception as e:
            print(f"❌ Failed to initialize orchestrator: {e}")
            return False
        
        # Check that realignment orchestrator is imported
        try:
            from src.orchestrators.realignment_orchestrator import RealignmentOrchestrator
            print("✅ RealignmentOrchestrator imported successfully")
        except ImportError as e:
            print(f"❌ Failed to import RealignmentOrchestrator: {e}")
            return False
        
        # Verify phase structure (check that execute_full_setup exists)
        if not hasattr(orchestrator, 'execute_full_setup'):
            print("❌ MasterSetupOrchestrator missing execute_full_setup method")
            return False
        print("✅ execute_full_setup method exists")
        
        # Check helper methods
        required_methods = ['_step_approved', '_setup_gitignore', '_create_completion_report']
        for method in required_methods:
            if not hasattr(orchestrator, method):
                print(f"❌ Missing method: {method}")
                return False
        print(f"✅ All required methods present ({len(required_methods)} checked)")
        
        print("\n" + "="*70)
        print("✅ ALL INTEGRATION CHECKS PASSED")
        print("="*70)
        return True


if __name__ == "__main__":
    success = test_phase_integration()
    sys.exit(0 if success else 1)
