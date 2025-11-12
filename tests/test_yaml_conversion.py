"""
YAML Conversion Tests - Phase 5.5.4

Tests for validating YAML conversion accuracy, performance, and token reduction.
Created: 2025-11-10
Machine: Mac (Asifs-MacBook-Pro.local)
"""

import pytest
import yaml
import time
from pathlib import Path
from typing import Dict, Any


class TestYAMLConversion:
    """Tests for Phase 5.5 YAML conversion validation."""
    
    @pytest.fixture
    def brain_path(self):
        """Get path to cortex-brain directory."""
        return Path(__file__).parent.parent / "cortex-brain"
    
    @pytest.fixture
    def root_path(self):
        """Get path to CORTEX root directory."""
        return Path(__file__).parent.parent
    
    @pytest.fixture
    def operations_config(self, brain_path):
        """Load operations-config.yaml"""
        yaml_path = brain_path / "operations-config.yaml"
        with open(yaml_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    @pytest.fixture
    def slash_commands_guide(self, brain_path):
        """Load slash-commands-guide.yaml"""
        yaml_path = brain_path / "slash-commands-guide.yaml"
        with open(yaml_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    @pytest.fixture
    def cortex_operations(self, root_path):
        """Load cortex-operations.yaml (in root directory)"""
        yaml_path = root_path / "cortex-operations.yaml"
        with open(yaml_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    # ============================================================
    # Task 5.5.4.1: Structure Validation
    # ============================================================
    
    def test_operations_config_structure(self, operations_config):
        """Verify operations-config.yaml has correct structure."""
        assert "metadata" in operations_config
        assert "operations" in operations_config
        assert "categories" in operations_config
        
        # Check metadata
        metadata = operations_config["metadata"]
        assert "version" in metadata
        assert "last_updated" in metadata
        assert "purpose" in metadata
        
        # Check operations list
        operations = operations_config["operations"]
        assert isinstance(operations, list)
        assert len(operations) > 0
        
        # Validate first operation structure
        first_op = operations[0]
        assert "id" in first_op
        assert "name" in first_op
        assert "status" in first_op
        assert "category" in first_op
    
    def test_slash_commands_structure(self, slash_commands_guide):
        """Verify slash-commands-guide.yaml has correct structure."""
        assert "metadata" in slash_commands_guide
        assert "commands" in slash_commands_guide
        assert "aliases" in slash_commands_guide
        
        commands = slash_commands_guide["commands"]
        assert isinstance(commands, list)
        assert len(commands) > 0
        
        # Validate command structure
        first_cmd = commands[0]
        assert "command" in first_cmd
        assert "natural_language" in first_cmd
        assert "category" in first_cmd
    
    def test_cortex_operations_structure(self, cortex_operations):
        """Verify cortex-operations.yaml has correct structure."""
        assert "metadata" in cortex_operations
        assert "operations" in cortex_operations
        
        operations = cortex_operations["operations"]
        assert isinstance(operations, dict)
        
        # Check at least one operation exists
        assert len(operations) > 0
        
        # Validate operation structure
        first_op_key = next(iter(operations))
        first_op = operations[first_op_key]
        assert "description" in first_op
        assert "modules" in first_op
    
    # ============================================================
    # Task 5.5.4.2: Data Integrity Validation
    # ============================================================
    
    def test_operations_config_data_integrity(self, operations_config):
        """Verify all operations have required fields."""
        operations = operations_config["operations"]
        
        required_fields = ["id", "name", "status", "category", "description"]
        
        for op in operations:
            for field in required_fields:
                assert field in op, f"Operation {op.get('id', 'unknown')} missing {field}"
            
            # Validate status values
            assert op["status"] in ["ready", "partial", "pending", "planned"]
            
            # Validate category
            assert op["category"] in operations_config["categories"]
    
    def test_no_duplicate_operation_ids(self, operations_config):
        """Ensure no duplicate operation IDs."""
        operations = operations_config["operations"]
        ids = [op["id"] for op in operations]
        
        assert len(ids) == len(set(ids)), "Duplicate operation IDs found"
    
    def test_no_duplicate_commands(self, slash_commands_guide):
        """Ensure no duplicate slash commands."""
        commands = slash_commands_guide["commands"]
        command_names = [cmd["command"] for cmd in commands]
        
        assert len(command_names) == len(set(command_names)), "Duplicate commands found"
    
    def test_aliases_reference_valid_commands(self, slash_commands_guide):
        """Verify aliases point to valid commands."""
        commands = slash_commands_guide["commands"]
        command_names = {cmd["command"] for cmd in commands}
        
        aliases = slash_commands_guide["aliases"]
        for alias, target in aliases.items():
            assert target in command_names, f"Alias '{alias}' points to non-existent command '{target}'"
    
    # ============================================================
    # Task 5.5.4.3: Performance Testing
    # ============================================================
    
    def test_operations_config_load_performance(self, brain_path):
        """Verify operations-config.yaml loads quickly (<100ms)."""
        yaml_path = brain_path / "operations-config.yaml"
        
        start = time.perf_counter()
        with open(yaml_path, 'r') as f:
            yaml.safe_load(f)
        duration = time.perf_counter() - start
        
        assert duration < 0.1, f"Load time {duration:.3f}s exceeds 100ms target"
    
    def test_slash_commands_load_performance(self, brain_path):
        """Verify slash-commands-guide.yaml loads quickly (<100ms)."""
        yaml_path = brain_path / "slash-commands-guide.yaml"
        
        start = time.perf_counter()
        with open(yaml_path, 'r') as f:
            yaml.safe_load(f)
        duration = time.perf_counter() - start
        
        assert duration < 0.1, f"Load time {duration:.3f}s exceeds 100ms target"
    
    def test_cortex_operations_load_performance(self, root_path):
        """Verify cortex-operations.yaml loads quickly (<100ms)."""
        yaml_path = root_path / "cortex-operations.yaml"
        
        start = time.perf_counter()
        with open(yaml_path, 'r') as f:
            yaml.safe_load(f)
        duration = time.perf_counter() - start
        
        assert duration < 0.1, f"Load time {duration:.3f}s exceeds 100ms target"
    
    def test_all_yaml_files_load_together(self, brain_path, root_path):
        """Verify all YAML files load together quickly (<500ms)."""
        yaml_files = {
            brain_path: [
                "operations-config.yaml",
                "slash-commands-guide.yaml",
                "brain-protection-rules.yaml",
                "response-templates.yaml"
            ],
            root_path: [
                "cortex-operations.yaml"
            ]
        }
        
        start = time.perf_counter()
        for base_path, files in yaml_files.items():
            for yaml_file in files:
                yaml_path = base_path / yaml_file
                if yaml_path.exists():
                    with open(yaml_path, 'r') as f:
                        yaml.safe_load(f)
        duration = time.perf_counter() - start
        
        assert duration < 0.5, f"Total load time {duration:.3f}s exceeds 500ms target"
    
    # ============================================================
    # Task 5.5.4.4: Cross-Reference Validation
    # ============================================================
    
    def test_operations_match_yaml_definitions(self, operations_config, cortex_operations):
        """Verify operations-config.yaml matches cortex-operations.yaml."""
        config_ops = {op["id"] for op in operations_config["operations"]}
        yaml_ops = set(cortex_operations["operations"].keys())
        
        # Some operations in config may not be in cortex-operations yet
        # But all operations in cortex-operations should be in config
        for yaml_op in yaml_ops:
            assert yaml_op in config_ops, f"Operation '{yaml_op}' in cortex-operations.yaml but not in operations-config.yaml"
    
    def test_commands_have_operation_mapping(self, slash_commands_guide, operations_config):
        """Verify slash commands map to operations."""
        commands = slash_commands_guide["commands"]
        operation_ids = {op["id"] for op in operations_config["operations"]}
        
        for cmd in commands:
            if "operation_id" in cmd:
                op_id = cmd["operation_id"]
                assert op_id in operation_ids, f"Command '{cmd['command']}' references non-existent operation '{op_id}'"
    
    # ============================================================
    # Task 5.5.4.5: Backward Compatibility
    # ============================================================
    
    def test_yaml_contains_all_legacy_operations(self, cortex_operations):
        """Ensure YAML includes all operations from legacy system."""
        expected_operations = [
            "refresh_cortex_story",
            "environment_setup",
            "workspace_cleanup",
            "update_documentation",
            "brain_protection_check",
            "run_tests"
        ]
        
        yaml_ops = cortex_operations["operations"].keys()
        
        for expected in expected_operations:
            assert expected in yaml_ops, f"Missing legacy operation: {expected}"
    
    # ============================================================
    # Task 5.5.4.6: Schema Validation
    # ============================================================
    
    def test_yaml_files_are_valid_yaml(self, brain_path, root_path):
        """Verify all YAML files parse without errors."""
        yaml_files = {
            brain_path: [
                "operations-config.yaml",
                "slash-commands-guide.yaml",
                "brain-protection-rules.yaml",
                "response-templates.yaml",
                "CORTEX-UNIFIED-ARCHITECTURE.yaml"
            ],
            root_path: [
                "cortex-operations.yaml"
            ]
        }
        
        for base_path, files in yaml_files.items():
            for yaml_file in files:
                yaml_path = base_path / yaml_file
                if yaml_path.exists():
                    try:
                        with open(yaml_path, 'r') as f:
                            yaml.safe_load(f)
                    except yaml.YAMLError as e:
                        pytest.fail(f"YAML parse error in {yaml_file}: {e}")
    
    def test_operations_have_module_structure(self, cortex_operations):
        """Verify operations define proper module structure."""
        operations = cortex_operations["operations"]
        
        for op_id, op_data in operations.items():
            assert "modules" in op_data, f"Operation '{op_id}' missing modules"
            
            modules = op_data["modules"]
            assert isinstance(modules, list), f"Operation '{op_id}' modules not a list"
            
            for module in modules:
                assert "id" in module, f"Module in '{op_id}' missing id"
                assert "name" in module, f"Module in '{op_id}' missing name"
                assert "status" in module, f"Module in '{op_id}' missing status"


class TestTokenReductionPreliminary:
    """Preliminary token reduction validation."""
    
    @pytest.fixture
    def brain_path(self):
        """Get path to cortex-brain directory."""
        return Path(__file__).parent.parent / "cortex-brain"
    
    @pytest.fixture
    def root_path(self):
        """Get path to CORTEX root directory."""
        return Path(__file__).parent.parent
    
    def test_yaml_files_exist(self, brain_path, root_path):
        """Verify new YAML files were created."""
        yaml_files = {
            brain_path: [
                "operations-config.yaml",
                "slash-commands-guide.yaml"
            ],
            root_path: [
                "cortex-operations.yaml"
            ]
        }
        
        for base_path, files in yaml_files.items():
            for yaml_file in files:
                yaml_path = base_path / yaml_file
                assert yaml_path.exists(), f"YAML file not found: {yaml_file} in {base_path}"
    
    def test_yaml_files_not_empty(self, brain_path, root_path):
        """Verify YAML files have content."""
        yaml_files = {
            brain_path: [
                "operations-config.yaml",
                "slash-commands-guide.yaml"
            ],
            root_path: [
                "cortex-operations.yaml"
            ]
        }
        
        for base_path, files in yaml_files.items():
            for yaml_file in files:
                yaml_path = base_path / yaml_file
                with open(yaml_path, 'r') as f:
                    content = f.read()
                
                assert len(content) > 100, f"YAML file {yaml_file} appears to be empty or too small"
                
                # Verify it's actually YAML content
                assert ":" in content, f"YAML file {yaml_file} doesn't contain YAML syntax"


# ============================================================
# Pytest Configuration
# ============================================================

def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "yaml: mark test as YAML conversion validation test"
    )
