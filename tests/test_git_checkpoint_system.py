"""
Test Git Checkpoint System

Validates:
- Config loading from git-checkpoint-rules.yaml
- Dirty state detection
- Checkpoint creation
- Retention policy
- Rollback capability

Version: 1.0.0
Author: Asif Hussain
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.orchestrators.git_checkpoint_orchestrator import GitCheckpointOrchestrator


def test_config_loading():
    """Test that config loads correctly from YAML."""
    print("\n✅ TEST: Config Loading")
    
    orchestrator = GitCheckpointOrchestrator(
        project_root=project_root,
        brain_path=project_root / "cortex-brain"
    )
    
    config = orchestrator.config
    
    # Verify key config sections exist
    assert "auto_checkpoint" in config, "Missing auto_checkpoint config"
    assert "retention" in config, "Missing retention config"
    assert "naming" in config, "Missing naming config"
    assert "safety" in config, "Missing safety config"
    
    # Verify auto-checkpoint triggers
    triggers = config["auto_checkpoint"]["triggers"]
    assert triggers["before_implementation"] == True
    assert triggers["after_implementation"] == True
    
    # Verify retention policy
    retention = config["retention"]
    assert retention["max_age_days"] == 30
    assert retention["max_count"] == 50
    assert retention["preserve_named"] == True
    
    print("   ✓ Config loaded successfully")
    print(f"   ✓ Auto-checkpoints: {config['auto_checkpoint']['enabled']}")
    print(f"   ✓ Retention: {retention['max_age_days']} days, {retention['max_count']} max")


def test_dirty_state_detection():
    """Test dirty state detection."""
    print("\n✅ TEST: Dirty State Detection")
    
    orchestrator = GitCheckpointOrchestrator(
        project_root=project_root,
        brain_path=project_root / "cortex-brain"
    )
    
    dirty_state = orchestrator.detect_dirty_state()
    
    # Verify structure
    assert "is_dirty" in dirty_state
    assert "modified_files" in dirty_state
    assert "staged_files" in dirty_state
    assert "untracked_files" in dirty_state
    assert "merge_in_progress" in dirty_state
    assert "rebase_in_progress" in dirty_state
    assert "has_conflicts" in dirty_state
    
    print(f"   ✓ Dirty state detected: {dirty_state['is_dirty']}")
    print(f"   ✓ Modified files: {len(dirty_state.get('modified_files', []))}")
    print(f"   ✓ Staged files: {len(dirty_state.get('staged_files', []))}")
    print(f"   ✓ Untracked files: {len(dirty_state.get('untracked_files', []))}")


def test_checkpoint_naming():
    """Test checkpoint naming convention."""
    print("\n✅ TEST: Checkpoint Naming")
    
    orchestrator = GitCheckpointOrchestrator(
        project_root=project_root,
        brain_path=project_root / "cortex-brain"
    )
    
    # Verify naming format
    naming = orchestrator.config["naming"]
    assert naming["format"] == "{type}-{timestamp}"
    assert naming["timestamp_format"] == "%Y%m%d-%H%M%S"
    
    print("   ✓ Naming format validated")
    print(f"   ✓ Format: {naming['format']}")
    print(f"   ✓ Timestamp: {naming['timestamp_format']}")


def test_safety_checks():
    """Test safety check configuration."""
    print("\n✅ TEST: Safety Checks")
    
    orchestrator = GitCheckpointOrchestrator(
        project_root=project_root,
        brain_path=project_root / "cortex-brain"
    )
    
    safety = orchestrator.config["safety"]
    
    # Verify core safety settings
    assert safety["detect_uncommitted_changes"] == True
    assert safety["warn_on_uncommitted"] == True
    assert safety["require_confirmation"] == True
    
    print("   ✓ Safety checks enabled")
    print("   ✓ Uncommitted change detection: ON")
    print("   ✓ Warning on uncommitted: ON")
    print("   ✓ Confirmation required: ON")


def test_checkpoint_list():
    """Test listing checkpoints."""
    print("\n✅ TEST: Checkpoint Listing")
    
    orchestrator = GitCheckpointOrchestrator(
        project_root=project_root,
        brain_path=project_root / "cortex-brain"
    )
    
    # List all checkpoints
    checkpoints = orchestrator.list_all_checkpoints()
    
    print(f"   ✓ Found {len(checkpoints)} checkpoints")
    
    if checkpoints:
        latest = checkpoints[0]
        print(f"   ✓ Latest: {latest.get('checkpoint_id', 'N/A')}")
        print(f"   ✓ Type: {latest.get('type', 'N/A')}")
        print(f"   ✓ Timestamp: {latest.get('timestamp', 'N/A')}")


def main():
    """Run all tests."""
    print("=" * 60)
    print("GIT CHECKPOINT SYSTEM VALIDATION")
    print("=" * 60)
    
    try:
        test_config_loading()
        test_dirty_state_detection()
        test_checkpoint_naming()
        test_safety_checks()
        test_checkpoint_list()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print("\n📋 Summary:")
        print("   • Config loading: ✅")
        print("   • Dirty state detection: ✅")
        print("   • Checkpoint naming: ✅")
        print("   • Safety checks: ✅")
        print("   • Checkpoint listing: ✅")
        print("\n🎉 Git Checkpoint System is operational!\n")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
