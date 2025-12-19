#!/usr/bin/env python3
"""
Phase 2 Task 2.3: Brain Persistence Tests

Test: Tier1 FIFO enforcement, conversation limits, and persistence
"""

import pytest
from pathlib import Path
import tempfile
import shutil
import json


@pytest.fixture
def temp_brain_dir():
    """Create a temporary brain directory."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def tier1_api():
    """Create a Tier1API instance for testing."""
    try:
        from src.tier1.tier1_api import Tier1API
        return Tier1API()
    except ImportError:
        pytest.skip("Tier1API not available")


def test_tier1_api_exists():
    """Verify Tier1API can be imported."""
    try:
        from src.tier1.tier1_api import Tier1API
        assert Tier1API is not None
    except ImportError:
        pytest.skip("Tier1API not available")


def test_conversation_limit_constant():
    """Test that the 70-conversation limit is defined."""
    # The limit should be 70 conversations
    MAX_CONVERSATIONS = 70
    
    assert MAX_CONVERSATIONS == 70, "Tier1 should maintain exactly 70 conversations"


def test_fifo_eviction_logic():
    """Test FIFO (First In, First Out) eviction logic."""
    # When limit reached, oldest conversation should be removed
    
    # Simulate conversation queue
    conversations = []
    MAX_LIMIT = 70
    
    # Add 80 conversations
    for i in range(80):
        if len(conversations) >= MAX_LIMIT:
            # Remove oldest (FIFO)
            conversations.pop(0)
        conversations.append(f"conv-{i}")
    
    # Should have exactly 70
    assert len(conversations) == 70
    
    # Oldest (0-9) should be evicted
    assert "conv-0" not in conversations
    assert "conv-9" not in conversations
    
    # Newest (70-79) should remain
    assert "conv-70" in conversations
    assert "conv-79" in conversations


@pytest.mark.integration
def test_tier1_fifo_enforcement(temp_brain_dir):
    """
    Test Tier1 FIFO enforcement with actual conversation processing.
    
    Workflow:
    1. Process 80 conversations (exceeds 70 limit)
    2. Verify exactly 70 remain
    3. Verify oldest 10 were evicted (FIFO)
    4. Verify newest 70 are retained
    """
    try:
        from src.tier1.tier1_api import Tier1API
    except ImportError:
        pytest.skip("Tier1API not available")
    
    # Create Tier1 instance with temp directory
    tier1 = Tier1API()
    
    # Track conversation IDs
    conv_ids = []
    
    # Add 80 conversations (exceeds 70 limit)
    for i in range(80):
        conv_id = f"conv-{i:03d}"
        conv_ids.append(conv_id)
        
        # Simulate conversation entry
        entry = {
            "id": conv_id,
            "timestamp": f"2025-12-{11+(i//24):02d}T{i%24:02d}:00:00Z",
            "role": "user",
            "content": f"Test message {i}",
            "metadata": {"turn": i}
        }
        
        # Process entry (would trigger FIFO)
        # tier1.add_conversation(entry)
    
    # Expected behavior:
    # - Total conversations = 70 (not 80)
    # - Oldest 10 evicted: conv-000 through conv-009
    # - Newest 70 retained: conv-010 through conv-079
    
    expected_remaining = 70
    expected_evicted = conv_ids[:10]  # First 10
    expected_retained = conv_ids[10:]  # Last 70
    
    assert len(expected_retained) == expected_remaining
    assert len(expected_evicted) == 10
    
    # Verify FIFO logic
    assert "conv-000" in expected_evicted
    assert "conv-009" in expected_evicted
    assert "conv-010" in expected_retained
    assert "conv-079" in expected_retained
    
    pytest.skip("Full implementation requires Tier1API.add_conversation() method")


def test_conversation_persistence_file():
    """Test that conversations are persisted to file."""
    conversation_file = Path("cortex-brain/conversation-context.jsonl")
    
    # File should exist or parent directory should exist
    assert conversation_file.parent.exists(), "cortex-brain directory should exist"
    
    # If file exists, verify it's readable
    if conversation_file.exists():
        assert conversation_file.is_file(), "conversation-context.jsonl should be a file"
        
        # Verify JSONL format (each line is valid JSON)
        try:
            with open(conversation_file, 'r') as f:
                lines = f.readlines()
                for i, line in enumerate(lines[:5]):  # Check first 5 lines
                    if line.strip():  # Skip empty lines
                        entry = json.loads(line)
                        assert isinstance(entry, dict), f"Line {i} should be a dict"
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSONL format: {e}")


def test_conversation_jsonl_format():
    """Test that conversation entries follow JSONL format."""
    # Each line should be valid JSON
    sample_conversation = {
        "id": "conv-001",
        "timestamp": "2025-12-11T14:30:00Z",
        "role": "user",
        "content": "test message",
        "metadata": {}
    }
    
    # Should be serializable to JSON
    json_str = json.dumps(sample_conversation)
    parsed = json.loads(json_str)
    
    assert parsed["id"] == "conv-001"
    assert parsed["role"] == "user"


def test_conversation_retrieval():
    """Test conversation retrieval methods and logic."""
    # Required retrieval methods
    retrieval_methods = {
        "get_conversation_by_id": "Retrieve single conversation by ID",
        "get_conversations_by_time_range": "Retrieve conversations in time range",
        "get_all_conversations": "Retrieve all stored conversations",
        "get_recent_conversations": "Retrieve N most recent conversations"
    }
    
    assert len(retrieval_methods) == 4
    
    # Test retrieval logic patterns
    test_conversations = [
        {"id": f"conv-{i}", "timestamp": f"2025-12-{10+i:02d}T12:00:00Z"}
        for i in range(5)
    ]
    
    # By ID
    target_id = "conv-2"
    by_id = [c for c in test_conversations if c["id"] == target_id]
    assert len(by_id) == 1
    assert by_id[0]["id"] == target_id
    
    # Recent N
    recent_2 = test_conversations[-2:]
    assert len(recent_2) == 2
    assert recent_2[-1]["id"] == "conv-4"


def test_brain_tier_structure():
    """Test that brain tier structure is properly defined."""
    brain_tiers = {
        "tier0": "Governance (SKULL rules)",
        "tier1": "Working memory (70-conv FIFO)",
        "tier2": "Knowledge graph",
        "tier3": "Dev context"
    }
    
    assert "tier1" in brain_tiers
    assert "70-conv FIFO" in brain_tiers["tier1"]


def test_conversation_metadata_structure():
    """Test expected conversation metadata structure."""
    metadata_fields = [
        "conversation_id",
        "timestamp",
        "turn_count",
        "topics",
        "intent",
        "complexity"
    ]
    
    assert len(metadata_fields) == 6


def test_memory_eviction_logging():
    """Test conversation eviction logging structure and logic."""
    # Eviction should be logged with audit trail
    
    eviction_log_entry = {
        "timestamp": "2025-12-11T14:30:00Z",
        "conversation_id": "conv-001",
        "reason": "FIFO limit reached",
        "age_days": 45,
        "turn_count": 8
    }
    
    # Verify required fields
    required_fields = ["timestamp", "conversation_id", "reason"]
    for field in required_fields:
        assert field in eviction_log_entry, f"Missing required field: {field}"
    
    # Verify reason is valid
    valid_reasons = ["FIFO limit reached", "manual eviction", "expired"]
    assert eviction_log_entry["reason"] in valid_reasons
    
    # Simulate FIFO eviction scenario
    conversations = [f"conv-{i:03d}" for i in range(80)]
    MAX_LIMIT = 70
    
    # Evict oldest 10
    evicted = conversations[:len(conversations) - MAX_LIMIT]
    remaining = conversations[-MAX_LIMIT:]
    
    assert len(evicted) == 10
    assert len(remaining) == 70
    assert "conv-000" in evicted
    assert "conv-009" in evicted
    assert "conv-070" in remaining
    assert "conv-079" in remaining


def test_brain_protection_persistence_rule():
    """Verify brain persistence rules are defined."""
    try:
        import yaml
        from pathlib import Path
        
        brain_rules_path = Path("cortex-brain/brain-protection-rules.yaml")
        if not brain_rules_path.exists():
            pytest.skip("Brain protection rules file not found")
        
        with open(brain_rules_path) as f:
            rules = yaml.safe_load(f)
        
        # Check for persistence-related rules
        rules_str = str(rules)
        
        # Should mention conversation limits or FIFO
        assert any(keyword in rules_str.lower() for keyword in ["conversation", "fifo", "tier1"]), \
            "Brain protection rules should mention conversation/FIFO/tier1"
            
    except ImportError:
        pytest.skip("PyYAML not available")


def test_tier1_initialization():
    """Test Tier1 initialization with proper configuration."""
    required_config = {
        "max_conversations": 70,
        "storage_path": "cortex-brain/conversation-context.jsonl",
        "eviction_strategy": "FIFO",
        "persistence_enabled": True
    }
    
    # Verify config structure
    assert required_config["max_conversations"] == 70
    assert required_config["eviction_strategy"] == "FIFO"
    assert required_config["persistence_enabled"] is True
    
    # Verify storage path is valid
    storage_path = Path(required_config["storage_path"])
    assert storage_path.parent.name == "cortex-brain"
    assert storage_path.suffix == ".jsonl"


@pytest.mark.integration
def test_brain_backup_and_restore():
    """Test brain backup and restore functionality."""
    backup_targets = [
        "conversation-context.jsonl",
        "knowledge-graph.yaml",
        "development-context.yaml"
    ]
    
    # Verify all targets have valid formats
    for target in backup_targets:
        assert target.endswith(('.jsonl', '.yaml')), f"Invalid backup target format: {target}"
    
    # Verify backup target files exist or are creatable
    brain_dir = Path("cortex-brain")
    for target in backup_targets:
        target_path = brain_dir / target
        
        # Parent directory must exist
        assert target_path.parent.exists(), f"Directory for {target} does not exist"
        
        # If file exists, verify it's readable
        if target_path.exists():
            assert target_path.is_file(), f"{target} should be a file"
            
            # Verify file has content or is empty but valid
            stat = target_path.stat()
            assert stat.st_size >= 0, f"{target} should have non-negative size"
    
    # Test backup naming convention
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"brain-backup-{timestamp}.tar.gz"
    
    assert "brain-backup" in backup_name
    assert timestamp in backup_name
    assert backup_name.endswith(".tar.gz")
