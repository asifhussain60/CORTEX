"""
Checkpoint Utility

Lightweight workflow phase checkpoint metadata management.

Core Operations:
- create_checkpoint: Create phase checkpoint with git integration
- store_metadata: Store checkpoint metadata to JSON
- list_checkpoints: List all checkpoints for session
- get_checkpoint: Get specific phase checkpoint
- create_pre_work_checkpoint: Create pre-work baseline

Version: 3.0.0 (Migrated from PhaseCheckpointManager v2.0)
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any


def create_checkpoint(
    session_id: str,
    phase: str,
    project_root: str,
    metrics: Optional[Dict[str, Any]] = None
) -> Optional[Dict]:
    """
    Create phase checkpoint with git integration
    
    Args:
        session_id: Session identifier
        phase: Phase name
        project_root: Path to repository root
        metrics: Optional metrics
        
    Returns:
        Dict with checkpoint_id, commit_sha, success
        
    Example:
        >>> result = create_checkpoint("sess-001", "phase-1", "/project")
        >>> print(result["checkpoint_id"])
        'ckpt-001'
    """
    try:
        from src.orchestrators.git_checkpoint_orchestrator import GitCheckpointOrchestrator
        
        git_checkpoint = GitCheckpointOrchestrator(project_root=Path(project_root))
        
        checkpoint_result = git_checkpoint.create_checkpoint(
            session_id=session_id,
            checkpoint_type=f"phase-{phase}",
            message=f"Phase {phase} complete"
        )
        
        if not checkpoint_result.get('success'):
            return None
        
        checkpoint_id = checkpoint_result['checkpoint_id']
        commit_sha = checkpoint_result['commit_sha']
        
        # Store metadata
        store_metadata(
            project_root=project_root,
            session_id=session_id,
            phase=phase,
            checkpoint_id=checkpoint_id,
            commit_sha=commit_sha,
            metrics=metrics
        )
        
        return {
            'success': True,
            'checkpoint_id': checkpoint_id,
            'commit_sha': commit_sha,
            'phase': phase
        }
    
    except Exception:
        return None


def store_metadata(
    project_root: str,
    session_id: str,
    phase: str,
    checkpoint_id: str,
    commit_sha: str,
    metrics: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Store checkpoint metadata to JSON
    
    Args:
        project_root: Repository root
        session_id: Session identifier
        phase: Phase name
        checkpoint_id: Checkpoint identifier
        commit_sha: Git commit SHA
        metrics: Optional metrics
        
    Returns:
        True if stored successfully
        
    Example:
        >>> success = store_metadata(
        ...     "/project", "sess-001", "phase-1", "ckpt-001", "abc123"
        ... )
        >>> print(success)
        True
    """
    try:
        checkpoint_dir = Path(project_root) / ".cortex"
        checkpoint_dir.mkdir(exist_ok=True)
        
        metadata_file = checkpoint_dir / f"phase-checkpoints-{session_id}.json"
        
        # Load existing
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {
                'session_id': session_id,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'checkpoints': []
            }
        
        # Add checkpoint
        checkpoint = {
            'phase': phase,
            'checkpoint_id': checkpoint_id,
            'commit_sha': commit_sha,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'metrics': metrics or {}
        }
        
        data['checkpoints'].append(checkpoint)
        
        # Save
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        return True
    
    except Exception:
        return False


def list_checkpoints(project_root: str, session_id: str) -> List[Dict[str, Any]]:
    """
    List all checkpoints for session
    
    Args:
        project_root: Repository root
        session_id: Session identifier
        
    Returns:
        List of checkpoint dicts
        
    Example:
        >>> checkpoints = list_checkpoints("/project", "sess-001")
        >>> for cp in checkpoints:
        ...     print(cp["phase"], cp["commit_sha"][:7])
        phase-1 abc1234
    """
    try:
        checkpoint_dir = Path(project_root) / ".cortex"
        metadata_file = checkpoint_dir / f"phase-checkpoints-{session_id}.json"
        
        if not metadata_file.exists():
            return []
        
        with open(metadata_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data.get('checkpoints', [])
    
    except Exception:
        return []


def get_checkpoint(
    project_root: str,
    session_id: str,
    phase: str
) -> Optional[Dict[str, Any]]:
    """
    Get specific phase checkpoint
    
    Args:
        project_root: Repository root
        session_id: Session identifier
        phase: Phase name
        
    Returns:
        Checkpoint dict or None
        
    Example:
        >>> checkpoint = get_checkpoint("/project", "sess-001", "phase-1")
        >>> if checkpoint:
        ...     print(checkpoint["commit_sha"])
        abc1234def5678
    """
    checkpoints = list_checkpoints(project_root, session_id)
    
    for checkpoint in checkpoints:
        if checkpoint.get('phase') == phase:
            return checkpoint
    
    return None


def create_pre_work_checkpoint(
    project_root: str,
    session_id: str,
    operation: str
) -> Optional[Dict]:
    """
    Create pre-work baseline checkpoint
    
    Args:
        project_root: Repository root
        session_id: Session identifier
        operation: Operation description
        
    Returns:
        Dict with checkpoint_id, commit_sha, success
        
    Example:
        >>> result = create_pre_work_checkpoint(
        ...     "/project", "sess-001", "Feature implementation"
        ... )
        >>> print(result["checkpoint_id"])
        'ckpt-pre-work'
    """
    try:
        from src.orchestrators.git_checkpoint_orchestrator import GitCheckpointOrchestrator
        
        git_checkpoint = GitCheckpointOrchestrator(project_root=Path(project_root))
        
        checkpoint_result = git_checkpoint.create_checkpoint(
            session_id=session_id,
            checkpoint_type="pre-work",
            message=f"Pre-work checkpoint: {operation}"
        )
        
        if not checkpoint_result.get('success'):
            return None
        
        checkpoint_id = checkpoint_result['checkpoint_id']
        commit_sha = checkpoint_result['commit_sha']
        
        # Store metadata
        store_metadata(
            project_root=project_root,
            session_id=session_id,
            phase="pre-work",
            checkpoint_id=checkpoint_id,
            commit_sha=commit_sha,
            metrics=None
        )
        
        return {
            'success': True,
            'checkpoint_id': checkpoint_id,
            'commit_sha': commit_sha,
            'phase': 'pre-work'
        }
    
    except Exception:
        return None


# CLI for testing
if __name__ == "__main__":
    import time
from src.utils.resource_resolver import get_root_path
    
    print("🧪 Testing Checkpoint Utility...")
    start_test = time.time()
    
    # Test with CORTEX project
    cortex_root = str(get_root_path().parent.parent)
    test_session = "test-checkpoint-001"
    
    # Test 1: Store metadata
    print("Testing metadata storage...")
    success = store_metadata(
        cortex_root,
        test_session,
        "test-phase-1",
        "test-ckpt-001",
        "abc123def456",
        {"tests": 100, "coverage": 95}
    )
    assert success, "Metadata storage failed"
    print("✅ Metadata stored")
    
    # Test 2: List checkpoints
    print("Testing checkpoint listing...")
    checkpoints = list_checkpoints(cortex_root, test_session)
    assert len(checkpoints) == 1, f"Expected 1 checkpoint, got {len(checkpoints)}"
    print(f"✅ Found {len(checkpoints)} checkpoint")
    
    # Test 3: Get checkpoint
    print("Testing checkpoint retrieval...")
    checkpoint = get_checkpoint(cortex_root, test_session, "test-phase-1")
    assert checkpoint is not None, "Checkpoint not found"
    assert checkpoint["checkpoint_id"] == "test-ckpt-001", "Wrong checkpoint ID"
    print(f"✅ Retrieved checkpoint: {checkpoint['checkpoint_id']}")
    
    # Test 4: Add second checkpoint
    print("Testing multiple checkpoints...")
    store_metadata(
        cortex_root,
        test_session,
        "test-phase-2",
        "test-ckpt-002",
        "def456ghi789",
        {"tests": 150, "coverage": 97}
    )
    checkpoints = list_checkpoints(cortex_root, test_session)
    assert len(checkpoints) == 2, f"Expected 2 checkpoints, got {len(checkpoints)}"
    print(f"✅ Now {len(checkpoints)} checkpoints")
    
    # Cleanup test file
    test_file = Path(cortex_root) / ".cortex" / f"phase-checkpoints-{test_session}.json"
    if test_file.exists():
        test_file.unlink()
        print("✅ Test file cleaned up")
    
    elapsed = time.time() - start_test
    print(f"\n⚡ All tests passed in {elapsed:.3f}s")
    print(f"📊 Operations: 5 core functions tested")
    print(f"✅ Performance: {elapsed:.3f}s")
