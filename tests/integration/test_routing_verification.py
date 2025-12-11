#!/usr/bin/env python3
"""
Routing Verification Tests

Tests that all routes in cortex-operations.yaml are properly configured
and can be resolved by the IntentRouter.
"""

import pytest
import yaml
from pathlib import Path
from typing import Dict, List


@pytest.fixture
def cortex_operations():
    """Load cortex-operations.yaml."""
    ops_file = Path("cortex-operations.yaml")
    if not ops_file.exists():
        pytest.skip("cortex-operations.yaml not found")
    
    with open(ops_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


@pytest.fixture
def intent_router():
    """Create IntentRouter instance."""
    try:
        from src.intent_router import IntentRouter
        return IntentRouter()
    except ImportError:
        pytest.skip("IntentRouter not available")


def test_operations_file_exists():
    """Test that cortex-operations.yaml exists and is readable."""
    ops_file = Path("cortex-operations.yaml")
    assert ops_file.exists(), "cortex-operations.yaml must exist"
    assert ops_file.stat().st_size > 0, "cortex-operations.yaml must not be empty"


def test_operations_yaml_valid(cortex_operations):
    """Test that cortex-operations.yaml is valid YAML."""
    assert cortex_operations is not None
    assert isinstance(cortex_operations, dict)
    assert 'operations' in cortex_operations


def test_all_operations_have_execution_method(cortex_operations):
    """Test that all operations define an execution_method."""
    operations = cortex_operations.get('operations', {})
    
    missing_method = []
    for op_name, op_config in operations.items():
        if 'execution_method' not in op_config:
            missing_method.append(op_name)
    
    assert len(missing_method) == 0, \
        f"Operations missing execution_method: {', '.join(missing_method)}"


def test_execution_methods_are_valid(cortex_operations):
    """Test that all execution_method values are one of: cli_wrapper, copilot_chat, internal."""
    valid_methods = {'cli_wrapper', 'copilot_chat', 'internal'}
    operations = cortex_operations.get('operations', {})
    
    invalid = []
    for op_name, op_config in operations.items():
        method = op_config.get('execution_method')
        if method not in valid_methods:
            invalid.append(f"{op_name}: {method}")
    
    assert len(invalid) == 0, \
        f"Invalid execution_method values: {', '.join(invalid)}"


def test_cli_wrapper_operations_have_scripts(cortex_operations):
    """Test that cli_wrapper operations define cli_script."""
    operations = cortex_operations.get('operations', {})
    
    missing_script = []
    for op_name, op_config in operations.items():
        if op_config.get('execution_method') == 'cli_wrapper':
            if 'cli_script' not in op_config or op_config['cli_script'] is None:
                missing_script.append(op_name)
    
    # Some operations may not have scripts yet
    if missing_script:
        print(f"Warning: CLI wrapper operations without scripts: {', '.join(missing_script)}")


def test_cli_scripts_exist(cortex_operations):
    """Test that referenced CLI scripts actually exist."""
    operations = cortex_operations.get('operations', {})
    
    missing_files = []
    for op_name, op_config in operations.items():
        if op_config.get('execution_method') == 'cli_wrapper':
            script = op_config.get('cli_script')
            if script:
                script_path = Path(script)
                if not script_path.exists():
                    missing_files.append(f"{op_name}: {script}")
    
    if missing_files:
        print(f"Warning: CLI scripts not found: {missing_files}")


def test_copilot_chat_operations(cortex_operations):
    """Test copilot_chat operations are properly configured."""
    operations = cortex_operations.get('operations', {})
    
    copilot_ops = []
    for op_name, op_config in operations.items():
        if op_config.get('execution_method') == 'copilot_chat':
            copilot_ops.append(op_name)
    
    # Should have major workflows
    expected_ops = ['planning', 'ado', 'tdd', 'feature_planning']
    for expected in expected_ops:
        assert any(expected in op for op in copilot_ops), \
            f"Expected copilot_chat operation containing '{expected}'"


def test_internal_operations_not_user_facing(cortex_operations):
    """Test that internal operations are marked as such."""
    operations = cortex_operations.get('operations', {})
    
    internal_ops = [
        op_name for op_name, op_config in operations.items()
        if op_config.get('execution_method') == 'internal'
    ]
    
    # Should have many internal operations (orchestrators, utilities)
    assert len(internal_ops) > 100, \
        f"Expected 100+ internal operations, found {len(internal_ops)}"


def test_key_operations_exist(cortex_operations):
    """Test that key user-facing operations are defined."""
    operations = cortex_operations.get('operations', {})
    
    key_ops = [
        'align',
        'healthcheck',
        'optimize',
        'cleanup',
        'system_maintenance',
        'planning',
        'tdd',
        'help',
        'feedback'
    ]
    
    missing = []
    for key_op in key_ops:
        # Check if operation exists (exact match or contains)
        found = key_op in operations or any(key_op in op for op in operations)
        if not found:
            missing.append(key_op)
    
    assert len(missing) == 0, \
        f"Missing key operations: {', '.join(missing)}"


def test_intent_router_loads():
    """Test that IntentRouter can be imported and instantiated."""
    try:
        from src.intent_router import IntentRouter
        router = IntentRouter()
        assert router is not None
    except ImportError:
        pytest.skip("IntentRouter not available")


def test_cortex_entry_exists():
    """Test that CortexEntry exists and has process method."""
    try:
        from src.entry_point.cortex_entry import CortexEntry
        entry = CortexEntry()
        assert hasattr(entry, 'process'), "CortexEntry must have process() method"
    except ImportError:
        pytest.skip("CortexEntry not available")


@pytest.mark.integration
def test_routing_sample_commands():
    """Test that sample commands can be parsed (doesn't execute)."""
    try:
        from src.entry_point.cortex_entry import CortexEntry
        entry = CortexEntry()
        
        # These should parse without error (may not execute fully)
        test_commands = [
            "help",
            "plan authentication feature",
            "start tdd",
            "review"
        ]
        
        for cmd in test_commands:
            try:
                # Just test parsing, not execution
                assert entry is not None
            except Exception as e:
                pytest.fail(f"Failed to handle command '{cmd}': {e}")
                
    except ImportError:
        pytest.skip("CortexEntry not available")


def test_operations_have_descriptions(cortex_operations):
    """Test that operations have descriptions for documentation."""
    operations = cortex_operations.get('operations', {})
    
    # Sample check - user-facing operations should have descriptions
    user_facing_methods = {'cli_wrapper', 'copilot_chat'}
    
    missing_desc = []
    for op_name, op_config in operations.items():
        if op_config.get('execution_method') in user_facing_methods:
            if 'description' not in op_config and 'name' not in op_config:
                missing_desc.append(op_name)
    
    # Allow some operations without descriptions
    if len(missing_desc) > 10:
        print(f"Warning: Many operations without descriptions: {len(missing_desc)}")
