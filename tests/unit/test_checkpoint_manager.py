import json
from pathlib import Path
import pytest

from src.orchestrators.core.checkpoint_manager import CheckpointManager


def test_create_checkpoint(tmp_path: Path):
    # Use temp directory to avoid polluting real checkpoints
    base_dir = tmp_path / "checkpoints"
    mgr = CheckpointManager(base_dir=base_dir)

    cid = "FEAT02-P3-T2.3.2"
    checkpoint_id = None

    # RED: This should fail until create_checkpoint is implemented
    checkpoint_id = mgr.create_checkpoint(correlation_id=cid)

    # After implementation, ensure file exists
    cp_file = base_dir / checkpoint_id
    assert cp_file.exists(), "Checkpoint file should be created"

    # Validate json structure
    data = json.loads(cp_file.read_text())
    assert data.get("version") == "1.0"
    assert "timestamp" in data
    assert isinstance(data.get("dag_snapshot"), dict)
    assert isinstance(data.get("state_snapshot"), dict)

    meta = data.get("metadata", {})
    for key in ["correlation_id", "executor", "tasks_completed", "tasks_remaining"]:
        assert key in meta
    assert meta["correlation_id"] == cid


def test_checkpoint_content(tmp_path: Path):
    base_dir = tmp_path / "checkpoints"
    mgr = CheckpointManager(base_dir=base_dir)

    cid = "FEAT02-P3-T2.3.2"
    checkpoint_id = mgr.create_checkpoint(correlation_id=cid)
    cp_file = base_dir / checkpoint_id

    data = json.loads(cp_file.read_text())

    # Ensure minimal content conforms to design spec
    assert data["version"] == "1.0"
    assert data["metadata"]["correlation_id"] == cid
    assert data["metadata"]["executor"] == "GitHub Copilot"
    assert isinstance(data["dag_snapshot"], dict)
    assert isinstance(data["state_snapshot"], dict)
    # timestamp should be ISO8601 (ends with Z)
    assert data["timestamp"].endswith("Z")


def test_recover_from_checkpoint(tmp_path: Path):
    # Create a checkpoint first
    base_dir = tmp_path / "checkpoints"
    mgr = CheckpointManager(base_dir=base_dir)

    cid = "FEAT02-P3-T2.3.3"
    checkpoint_id = mgr.create_checkpoint(correlation_id=cid)

    # RED: This should fail until recover_from_checkpoint is implemented
    result = mgr.recover_from_checkpoint(checkpoint_id)

    # After implementation, recovery should succeed
    assert result is True, "Recovery should succeed for valid checkpoint"


def test_partial_recovery(tmp_path: Path):
    # Test recovery validation with corrupted/partial checkpoint
    base_dir = tmp_path / "checkpoints"
    mgr = CheckpointManager(base_dir=base_dir)

    # Create a valid checkpoint
    cid = "FEAT02-P3-T2.3.3"
    checkpoint_id = mgr.create_checkpoint(correlation_id=cid)
    cp_file = base_dir / checkpoint_id

    # Corrupt the checkpoint (missing required field)
    data = json.loads(cp_file.read_text())
    del data["version"]
    cp_file.write_text(json.dumps(data))

    # Recovery should fail gracefully
    result = mgr.recover_from_checkpoint(checkpoint_id)
    assert result is False, "Recovery should fail for corrupted checkpoint"


def test_list_checkpoints(tmp_path: Path):
    base_dir = tmp_path / "checkpoints"
    mgr = CheckpointManager(base_dir=base_dir)

    # Create multiple checkpoints
    cp1 = mgr.create_checkpoint(correlation_id="FEAT02-P3-T1")
    cp2 = mgr.create_checkpoint(correlation_id="FEAT02-P3-T2")

    # List should return both
    checkpoints = mgr.list_checkpoints()
    assert len(checkpoints) >= 2, "Should list all checkpoints"
    assert cp1 in [cp["id"] for cp in checkpoints]
    assert cp2 in [cp["id"] for cp in checkpoints]


def test_get_latest_checkpoint(tmp_path: Path):
    base_dir = tmp_path / "checkpoints"
    mgr = CheckpointManager(base_dir=base_dir)

    # Create checkpoints in sequence
    cp1 = mgr.create_checkpoint(correlation_id="FEAT02-P3-T1")
    import time
    time.sleep(1.1)  # Ensure different timestamps (seconds precision)
    cp2 = mgr.create_checkpoint(correlation_id="FEAT02-P3-T2")

    # Latest should be the second one
    latest = mgr.get_latest_checkpoint()
    assert latest == cp2, f"Should return most recent checkpoint: {latest} vs {cp2}"


def test_rollback_to_checkpoint(tmp_path: Path):
    # Test basic rollback functionality
    base_dir = tmp_path / "checkpoints"
    mgr = CheckpointManager(base_dir=base_dir)

    cid = "FEAT02-P3-T2.3.4"
    checkpoint_id = mgr.create_checkpoint(correlation_id=cid)

    # RED: This should fail until rollback_to_checkpoint is implemented
    result = mgr.rollback_to_checkpoint(checkpoint_id)

    # After implementation, rollback should succeed
    assert result is True, "Rollback should succeed for valid checkpoint"


def test_rollback_cascade(tmp_path: Path):
    # Test rollback cascade for dependent tasks
    base_dir = tmp_path / "checkpoints"
    mgr = CheckpointManager(base_dir=base_dir)

    # Create checkpoint
    cid = "FEAT02-P3-T2.3.4-CASCADE"
    checkpoint_id = mgr.create_checkpoint(correlation_id=cid)

    # Rollback should handle cascade (minimal for now - expand when integrated)
    result = mgr.rollback_to_checkpoint(checkpoint_id)
    assert result is True, "Rollback with cascade should succeed"


def test_auto_checkpoint(tmp_path: Path):
    # Test automatic checkpoint configuration
    base_dir = tmp_path / "checkpoints"
    mgr = CheckpointManager(base_dir=base_dir)

    # RED: This should fail until configure_auto_checkpoint is implemented
    mgr.configure_auto_checkpoint(interval=5)

    # Verify configuration applied
    assert mgr._auto_checkpoint_interval == 5, "Auto-checkpoint interval should be set"


def test_checkpoint_cleanup(tmp_path: Path):
    # Test cleanup of old checkpoints
    base_dir = tmp_path / "checkpoints"
    mgr = CheckpointManager(base_dir=base_dir)

    # Configure to keep only 3 checkpoints
    mgr.configure_auto_checkpoint(interval=5)
    mgr._max_checkpoints = 3

    # Create 5 checkpoints
    for i in range(5):
        mgr.create_checkpoint(correlation_id=f"FEAT02-P3-T{i}")
        import time
        time.sleep(0.1)

    # Cleanup should remove oldest
    mgr._cleanup_old_checkpoints()

    # Should have only 3 remaining
    remaining = mgr.list_checkpoints()
    assert len(remaining) <= 3, f"Should keep max 3 checkpoints, found {len(remaining)}"


def test_should_checkpoint(tmp_path: Path):
    # Test checkpoint trigger logic
    base_dir = tmp_path / "checkpoints"
    mgr = CheckpointManager(base_dir=base_dir)

    mgr.configure_auto_checkpoint(interval=5)
    mgr._tasks_since_checkpoint = 0

    # Should not checkpoint yet
    assert mgr._should_checkpoint() is False, "Should not checkpoint at 0 tasks"

    # Simulate completing tasks
    mgr._tasks_since_checkpoint = 5

    # Should checkpoint now
    assert mgr._should_checkpoint() is True, "Should checkpoint at interval"
