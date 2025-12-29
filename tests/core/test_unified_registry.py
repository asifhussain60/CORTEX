"""
Tests for UnifiedRegistry and Registry Adapters

Tests all functionality of unified registry system including:
- Core operations (register, get, list, unregister)
- Thread safety
- Validation
- Persistence
- Migration adapters

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

import pytest
import threading
import time
from pathlib import Path
from src.core.unified_registry import (
    UnifiedRegistry,
    RegistryItem,
    RegistryItemType,
    RegistryConflictError,
    RegistryValidationError,
    get_unified_registry
)
from src.core.registry_adapters import (
    CommandRegistryAdapter,
    ToolkitRegistryAdapter,
    WorkspaceRegistryAdapter,
    create_migration_report
)


@pytest.fixture
def registry():
    """Create fresh UnifiedRegistry for each test."""
    return UnifiedRegistry()


@pytest.fixture
def registry_with_storage(tmp_path):
    """Create UnifiedRegistry with temporary storage."""
    storage_path = tmp_path / "registry.yaml"
    return UnifiedRegistry(
        storage_path=storage_path,
        enable_persistence=True
    )


@pytest.fixture
def sample_command_metadata():
    """Sample command metadata for testing."""
    return {
        'natural_language_equivalent': 'switched to mac',
        'plugin_id': 'platform_switch',
        'description': 'Switch to macOS environment',
        'category': 'platform',
        'aliases': ['/macos', '/darwin']
    }


@pytest.fixture
def sample_tool_metadata():
    """Sample tool metadata for testing."""
    return {
        'name': 'align',
        'command': 'cortex align',
        'description': 'Align system with brain',
        'category': 'maintenance',
        'script': 'tools/system/align.py',
        'platforms': ['Windows', 'Linux', 'Darwin']
    }


class TestUnifiedRegistryCore:
    """Test core UnifiedRegistry functionality."""
    
    def test_registry_initialization(self, registry):
        """Test registry initializes correctly."""
        assert registry.count() == 0
        stats = registry.get_stats()
        assert stats['total_items'] == 0
        assert stats['total_registrations'] == 0
    
    def test_register_item(self, registry, sample_command_metadata):
        """Test registering an item."""
        success = registry.register(
            item_type=RegistryItemType.COMMAND,
            item_id='/mac',
            metadata=sample_command_metadata,
            registered_by='test'
        )
        
        assert success is True
        assert registry.count(RegistryItemType.COMMAND) == 1
        assert registry.exists(RegistryItemType.COMMAND, '/mac')
    
    def test_register_duplicate_raises_conflict(self, registry, sample_command_metadata):
        """Test registering duplicate ID raises error."""
        registry.register(
            item_type=RegistryItemType.COMMAND,
            item_id='/mac',
            metadata=sample_command_metadata
        )
        
        with pytest.raises(RegistryConflictError):
            registry.register(
                item_type=RegistryItemType.COMMAND,
                item_id='/mac',
                metadata=sample_command_metadata
            )
    
    def test_register_duplicate_with_override(self, registry, sample_command_metadata):
        """Test allowing override of existing items."""
        registry.register(
            item_type=RegistryItemType.COMMAND,
            item_id='/mac',
            metadata={'version': 1}
        )
        
        success = registry.register(
            item_type=RegistryItemType.COMMAND,
            item_id='/mac',
            metadata={'version': 2},
            allow_override=True
        )
        
        assert success is True
        item = registry.get(RegistryItemType.COMMAND, '/mac')
        assert item.metadata['version'] == 2
    
    def test_get_item(self, registry, sample_command_metadata):
        """Test retrieving an item."""
        registry.register(
            item_type=RegistryItemType.COMMAND,
            item_id='/mac',
            metadata=sample_command_metadata
        )
        
        item = registry.get(RegistryItemType.COMMAND, '/mac')
        assert item is not None
        assert item.item_id == '/mac'
        assert item.item_type == RegistryItemType.COMMAND
        assert item.metadata == sample_command_metadata
    
    def test_get_nonexistent_item(self, registry):
        """Test retrieving nonexistent item returns None."""
        item = registry.get(RegistryItemType.COMMAND, '/nonexistent')
        assert item is None
    
    def test_get_metadata(self, registry, sample_command_metadata):
        """Test getting item metadata."""
        registry.register(
            item_type=RegistryItemType.COMMAND,
            item_id='/mac',
            metadata=sample_command_metadata
        )
        
        metadata = registry.get_metadata(RegistryItemType.COMMAND, '/mac')
        assert metadata == sample_command_metadata
    
    def test_list_items(self, registry):
        """Test listing items of a type."""
        # Register multiple commands
        for i in range(5):
            registry.register(
                item_type=RegistryItemType.COMMAND,
                item_id=f'/cmd{i}',
                metadata={'index': i}
            )
        
        items = registry.list(RegistryItemType.COMMAND)
        assert len(items) == 5
        assert all(isinstance(item, RegistryItem) for item in items)
    
    def test_list_with_filter(self, registry):
        """Test listing items with filter function."""
        # Register items with different metadata
        for i in range(10):
            registry.register(
                item_type=RegistryItemType.COMMAND,
                item_id=f'/cmd{i}',
                metadata={'priority': 'high' if i < 5 else 'low'}
            )
        
        high_priority = registry.list(
            RegistryItemType.COMMAND,
            filter_fn=lambda item: item.metadata.get('priority') == 'high'
        )
        
        assert len(high_priority) == 5
    
    def test_list_ids(self, registry):
        """Test listing item IDs."""
        for i in range(3):
            registry.register(
                item_type=RegistryItemType.TOOL,
                item_id=f'tool{i}',
                metadata={}
            )
        
        ids = registry.list_ids(RegistryItemType.TOOL)
        assert len(ids) == 3
        assert 'tool0' in ids
        assert 'tool1' in ids
        assert 'tool2' in ids
    
    def test_unregister_item(self, registry, sample_command_metadata):
        """Test unregistering an item."""
        registry.register(
            item_type=RegistryItemType.COMMAND,
            item_id='/mac',
            metadata=sample_command_metadata
        )
        
        assert registry.exists(RegistryItemType.COMMAND, '/mac')
        
        success = registry.unregister(RegistryItemType.COMMAND, '/mac')
        assert success is True
        assert not registry.exists(RegistryItemType.COMMAND, '/mac')
    
    def test_unregister_nonexistent(self, registry):
        """Test unregistering nonexistent item returns False."""
        success = registry.unregister(RegistryItemType.COMMAND, '/nonexistent')
        assert success is False
    
    def test_exists(self, registry):
        """Test existence check."""
        assert not registry.exists(RegistryItemType.COMMAND, '/mac')
        
        registry.register(
            item_type=RegistryItemType.COMMAND,
            item_id='/mac',
            metadata={}
        )
        
        assert registry.exists(RegistryItemType.COMMAND, '/mac')
    
    def test_count(self, registry):
        """Test counting items."""
        assert registry.count() == 0
        assert registry.count(RegistryItemType.COMMAND) == 0
        
        # Register items of different types
        registry.register(RegistryItemType.COMMAND, '/cmd1', {})
        registry.register(RegistryItemType.COMMAND, '/cmd2', {})
        registry.register(RegistryItemType.TOOL, 'tool1', {})
        
        assert registry.count() == 3
        assert registry.count(RegistryItemType.COMMAND) == 2
        assert registry.count(RegistryItemType.TOOL) == 1
    
    def test_clear(self, registry):
        """Test clearing registry."""
        # Register items
        registry.register(RegistryItemType.COMMAND, '/cmd1', {})
        registry.register(RegistryItemType.TOOL, 'tool1', {})
        
        assert registry.count() == 2
        
        # Clear commands only
        registry.clear(RegistryItemType.COMMAND)
        assert registry.count(RegistryItemType.COMMAND) == 0
        assert registry.count(RegistryItemType.TOOL) == 1
        
        # Clear all
        registry.clear()
        assert registry.count() == 0
    
    def test_get_stats(self, registry):
        """Test getting registry statistics."""
        # Perform operations
        registry.register(RegistryItemType.COMMAND, '/cmd1', {})
        registry.register(RegistryItemType.COMMAND, '/cmd2', {})
        registry.unregister(RegistryItemType.COMMAND, '/cmd1')
        
        stats = registry.get_stats()
        assert stats['total_registrations'] == 2
        assert stats['total_unregistrations'] == 1
        assert stats['total_items'] == 1
        assert stats['items_by_type']['command'] == 1


class TestUnifiedRegistryValidation:
    """Test validation functionality."""
    
    def test_custom_validator(self):
        """Test custom validation function."""
        def validate_command(item: RegistryItem) -> bool:
            # Require 'description' in metadata
            return 'description' in item.metadata
        
        registry = UnifiedRegistry(
            validators={RegistryItemType.COMMAND: validate_command}
        )
        
        # Valid item
        success = registry.register(
            RegistryItemType.COMMAND,
            '/valid',
            {'description': 'Valid command'}
        )
        assert success is True
        
        # Invalid item
        with pytest.raises(RegistryValidationError):
            registry.register(
                RegistryItemType.COMMAND,
                '/invalid',
                {}
            )


class TestUnifiedRegistryThreadSafety:
    """Test thread safety of registry operations."""
    
    def test_concurrent_registration(self, registry):
        """Test concurrent registrations from multiple threads."""
        def register_items(thread_id, count):
            for i in range(count):
                registry.register(
                    RegistryItemType.COMMAND,
                    f'/thread{thread_id}_cmd{i}',
                    {'thread': thread_id}
                )
        
        threads = []
        for thread_id in range(10):
            thread = threading.Thread(target=register_items, args=(thread_id, 10))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Should have 100 items (10 threads × 10 items)
        assert registry.count(RegistryItemType.COMMAND) == 100
    
    def test_concurrent_read_write(self, registry):
        """Test concurrent reads and writes."""
        # Pre-populate
        for i in range(50):
            registry.register(RegistryItemType.COMMAND, f'/cmd{i}', {})
        
        results = {'reads': 0, 'writes': 0}
        lock = threading.Lock()
        
        def reader():
            for _ in range(100):
                registry.list(RegistryItemType.COMMAND)
                with lock:
                    results['reads'] += 1
        
        def writer(thread_id):
            # Each writer gets unique IDs to avoid conflicts
            for i in range(10):
                registry.register(
                    RegistryItemType.COMMAND,
                    f'/cmd{thread_id}_{i}',
                    {}
                )
                with lock:
                    results['writes'] += 1
        
        threads = []
        for i in range(5):
            threads.append(threading.Thread(target=reader))
            threads.append(threading.Thread(target=writer, args=(i,)))
        
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        # Verify no corruption (50 pre-populated + 5 writers × 10 writes = 100)
        assert registry.count(RegistryItemType.COMMAND) == 100
        assert results['reads'] == 500  # 5 reader threads × 100 reads
        assert results['writes'] == 50  # 5 writer threads × 10 writes


class TestUnifiedRegistryPersistence:
    """Test persistence functionality."""
    
    def test_save_and_load(self, registry_with_storage):
        """Test saving and loading registry."""
        # Register items
        registry_with_storage.register(
            RegistryItemType.COMMAND,
            '/mac',
            {'description': 'macOS command'}
        )
        registry_with_storage.register(
            RegistryItemType.TOOL,
            'align',
            {'category': 'maintenance'}
        )
        
        # Storage file should exist
        assert registry_with_storage._storage_path.exists()
        
        # Create new registry from same storage
        registry2 = UnifiedRegistry(
            storage_path=registry_with_storage._storage_path,
            enable_persistence=False
        )
        
        # Should load existing data
        assert registry2.count() == 2
        assert registry2.exists(RegistryItemType.COMMAND, '/mac')
        assert registry2.exists(RegistryItemType.TOOL, 'align')
    
    def test_auto_save_on_register(self, registry_with_storage):
        """Test auto-save on registration."""
        storage_path = registry_with_storage._storage_path
        
        # Register item
        registry_with_storage.register(
            RegistryItemType.COMMAND,
            '/test',
            {}
        )
        
        # File should be updated
        assert storage_path.exists()
        
        # Load in new registry
        registry2 = UnifiedRegistry(storage_path=storage_path)
        assert registry2.exists(RegistryItemType.COMMAND, '/test')


class TestCommandRegistryAdapter:
    """Test CommandRegistryAdapter."""
    
    def test_register_command(self, registry):
        """Test registering command via adapter."""
        adapter = CommandRegistryAdapter(registry)
        
        success = adapter.register_command({
            'command': '/mac',
            'natural_language_equivalent': 'switched to mac',
            'plugin_id': 'platform_switch',
            'description': 'Switch to macOS',
            'category': 'platform'
        })
        
        assert success is True
        assert adapter.is_command('/mac')
    
    def test_expand_command(self, registry):
        """Test expanding command to natural language."""
        adapter = CommandRegistryAdapter(registry)
        
        adapter.register_command({
            'command': '/mac',
            'natural_language_equivalent': 'switched to mac',
            'plugin_id': 'platform_switch',
            'description': 'Switch to macOS'
        })
        
        expanded = adapter.expand_command('/mac')
        assert expanded == 'switched to mac'
    
    def test_get_all_commands(self, registry):
        """Test getting all commands."""
        adapter = CommandRegistryAdapter(registry)
        
        for i in range(5):
            adapter.register_command({
                'command': f'/cmd{i}',
                'natural_language_equivalent': f'command {i}',
                'plugin_id': 'test',
                'description': f'Command {i}'
            })
        
        commands = adapter.get_all_commands()
        assert len(commands) == 5


class TestToolkitRegistryAdapter:
    """Test ToolkitRegistryAdapter."""
    
    def test_register_tool(self, registry, sample_tool_metadata):
        """Test registering tool via adapter."""
        adapter = ToolkitRegistryAdapter(registry)
        
        success = adapter.register_tool('align', sample_tool_metadata)
        assert success is True
    
    def test_get_tool(self, registry, sample_tool_metadata):
        """Test getting tool metadata."""
        adapter = ToolkitRegistryAdapter(registry)
        adapter.register_tool('align', sample_tool_metadata)
        
        tool = adapter.get_tool('align')
        assert tool == sample_tool_metadata
    
    def test_list_tools_by_category(self, registry):
        """Test listing tools filtered by category."""
        adapter = ToolkitRegistryAdapter(registry)
        
        adapter.register_tool('align', {'category': 'maintenance'})
        adapter.register_tool('test', {'category': 'testing'})
        adapter.register_tool('clean', {'category': 'maintenance'})
        
        maintenance_tools = adapter.list_tools(category='maintenance')
        assert len(maintenance_tools) == 2
    
    def test_list_categories(self, registry):
        """Test listing all categories."""
        adapter = ToolkitRegistryAdapter(registry)
        
        adapter.register_tool('tool1', {'category': 'maintenance'})
        adapter.register_tool('tool2', {'category': 'testing'})
        adapter.register_tool('tool3', {'category': 'docs'})
        
        categories = adapter.list_categories()
        assert len(categories) == 3
        assert 'maintenance' in categories


class TestWorkspaceRegistryAdapter:
    """Test WorkspaceRegistryAdapter."""
    
    def test_register_workspace(self, registry):
        """Test registering workspace."""
        adapter = WorkspaceRegistryAdapter(registry)
        
        success = adapter.register_workspace(
            workspace_id='ws-123',
            workspace_info={
                'path': '/path/to/workspace',
                'name': 'TestWorkspace',
                'status': 'active'
            }
        )
        
        assert success is True
    
    def test_get_workspace_by_path(self, registry):
        """Test getting workspace by path."""
        adapter = WorkspaceRegistryAdapter(registry)
        
        adapter.register_workspace(
            'ws-123',
            {
                'path': '/path/to/workspace',
                'name': 'TestWorkspace'
            }
        )
        
        workspace = adapter.get_workspace_by_path('/path/to/workspace')
        assert workspace is not None
        assert workspace['name'] == 'TestWorkspace'


class TestMigrationHelpers:
    """Test migration helper functions."""
    
    def test_create_migration_report(self, registry):
        """Test creating migration report."""
        # Populate registry
        registry.register(RegistryItemType.COMMAND, '/cmd1', {})
        registry.register(RegistryItemType.TOOL, 'tool1', {})
        registry.register(RegistryItemType.WORKSPACE, 'ws1', {})
        
        report = create_migration_report(registry)
        
        assert report['total_items'] == 3
        assert report['items_by_type']['command'] == 1
        assert report['items_by_type']['tool'] == 1
        assert report['items_by_type']['workspace'] == 1
        assert report['compatibility']['command_registry_compatible'] is True
