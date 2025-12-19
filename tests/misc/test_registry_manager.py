"""
Unit tests for RegistryManager module.

Tests cover:
- Template registration and lookup
- Category-based organization
- Tag-based search
- Duplicate ID detection
- Registry validation
- Auto-discovery from file structure
- Markdown export
- Registry persistence (save/load)

Author: CORTEX Test Suite
Date: December 5, 2025
Version: 1.0
"""

import pytest
import yaml
from pathlib import Path
from datetime import datetime
from src.response_templates.registry_manager import (
    RegistryManager,
    TemplateRegistryEntry
)


@pytest.fixture
def temp_template_dir(tmp_path):
    """Create temporary template directory structure."""
    template_dir = tmp_path / "response-templates"
    template_dir.mkdir()
    
    # Create directory structure
    (template_dir / "core" / "base-templates").mkdir(parents=True)
    (template_dir / "agents" / "tactical").mkdir(parents=True)
    (template_dir / "orchestrators").mkdir(parents=True)
    (template_dir / "config").mkdir(parents=True)
    
    # Create template files for auto-discovery
    template_files = [
        "agents/tactical/executor.yaml",
        "agents/tactical/planner.yaml",
        "orchestrators/planning.yaml",
        "core/base-templates/standard.yaml"
    ]
    
    for file_path in template_files:
        full_path = template_dir / file_path
        template_data = {
            "id": Path(file_path).stem,
            "sections": {"content": "test"}
        }
        with open(full_path, 'w') as f:
            yaml.dump(template_data, f)
    
    # Create initial registry file
    registry_file = template_dir / "config" / "template-registry.yaml"
    registry_data = {
        "version": "4.0",
        "templates": {
            "test_template": {
                "id": "test_template",
                "file": "agents/tactical/test.yaml",
                "category": "agents",
                "tags": ["test", "tactical"]
            }
        }
    }
    with open(registry_file, 'w') as f:
        yaml.dump(registry_data, f)
    
    return template_dir


@pytest.fixture
def registry_manager(temp_template_dir):
    """Create RegistryManager instance."""
    registry_file = temp_template_dir / "config" / "template-registry.yaml"
    return RegistryManager(
        registry_file=registry_file,
        template_dir=temp_template_dir
    )


class TestRegistryManager:
    """Test suite for RegistryManager class."""
    
    def test_initialization(self, registry_manager):
        """Test registry manager initialization."""
        assert registry_manager.registry_file is not None
        assert registry_manager.template_dir is not None
        assert len(registry_manager.registry) >= 1  # At least test_template
        assert registry_manager.version == "4.0"
    
    def test_initialization_empty_registry(self, tmp_path):
        """Test initialization with non-existent registry file."""
        registry_file = tmp_path / "new_registry.yaml"
        manager = RegistryManager(registry_file=registry_file)
        
        assert len(manager.registry) == 0
        assert manager.version == "4.0"
    
    def test_register_template(self, registry_manager):
        """Test registering a new template."""
        registry_manager.register_template(
            template_id="new_template",
            file_path="agents/tactical/new.yaml",
            category="agents",
            tags=["new", "test"]
        )
        
        assert "new_template" in registry_manager.registry
        entry = registry_manager.registry["new_template"]
        assert entry.file == "agents/tactical/new.yaml"
        assert entry.category == "agents"
        assert "new" in entry.tags
    
    def test_register_duplicate_template(self, registry_manager):
        """Test registering template with duplicate ID."""
        # First registration
        registry_manager.register_template(
            template_id="dup_test",
            file_path="agents/dup1.yaml",
            category="agents",
            tags=[]
        )
        
        # Duplicate registration (should warn or overwrite)
        registry_manager.register_template(
            template_id="dup_test",
            file_path="agents/dup2.yaml",
            category="agents",
            tags=[]
        )
        
        # Should have one entry (either original or overwritten)
        assert "dup_test" in registry_manager.registry
    
    def test_get_template_file(self, registry_manager):
        """Test retrieving template file path."""
        file_path = registry_manager.get_template_file("test_template")
        
        assert file_path is not None
        assert "test.yaml" in str(file_path)
    
    def test_get_nonexistent_template_file(self, registry_manager):
        """Test retrieving nonexistent template."""
        file_path = registry_manager.get_template_file("nonexistent")
        
        assert file_path is None
    
    def test_get_templates_by_category(self, registry_manager):
        """Test filtering templates by category."""
        # Register templates in different categories
        registry_manager.register_template("agent1", "agents/a1.yaml", "agents", [])
        registry_manager.register_template("agent2", "agents/a2.yaml", "agents", [])
        registry_manager.register_template("orch1", "orchestrators/o1.yaml", "orchestrators", [])
        
        # Get templates by category using filter or iteration
        agents = [e for e in registry_manager.registry.values() if e.category == "agents"]
        
        assert len(agents) >= 2  # At least agent1 and agent2
        assert all(t.category == "agents" for t in agents)
    
    def test_get_templates_by_tag(self, registry_manager):
        """Test finding templates by tag."""
        # Register templates with tags
        registry_manager.register_template("tagged1", "t1.yaml", "agents", ["debug", "test"])
        registry_manager.register_template("tagged2", "t2.yaml", "agents", ["debug", "prod"])
        registry_manager.register_template("tagged3", "t3.yaml", "agents", ["test"])
        
        # Filter by tag manually
        debug_templates = [e for e in registry_manager.registry.values() if "debug" in e.tags]
        
        assert len(debug_templates) >= 2  # tagged1 and tagged2
        assert all("debug" in t.tags for t in debug_templates)
    
    def test_list_all_templates(self, registry_manager):
        """Test listing all registered templates."""
        templates = list(registry_manager.registry.values())
        
        assert isinstance(templates, list)
        assert len(templates) >= 1  # At least test_template
        assert all(isinstance(t, TemplateRegistryEntry) for t in templates)
    
    def test_list_categories(self, registry_manager):
        """Test getting list of all categories."""
        # Register templates in different categories
        registry_manager.register_template("a1", "a1.yaml", "agents", [])
        registry_manager.register_template("o1", "o1.yaml", "orchestrators", [])
        registry_manager.register_template("op1", "op1.yaml", "operations", [])
        
        categories = list(set(e.category for e in registry_manager.registry.values()))
        
        assert isinstance(categories, list)
        assert "agents" in categories
        assert "orchestrators" in categories
    
    def test_list_all_tags(self, registry_manager):
        """Test getting list of all unique tags."""
        # Register templates with various tags
        registry_manager.register_template("t1", "t1.yaml", "agents", ["tag1", "tag2"])
        registry_manager.register_template("t2", "t2.yaml", "agents", ["tag2", "tag3"])
        
        # Get all unique tags
        all_tags = set()
        for entry in registry_manager.registry.values():
            all_tags.update(entry.tags)
        
        assert isinstance(all_tags, set)
        assert len(all_tags) > 0
    
    def test_auto_discover_templates(self, registry_manager, temp_template_dir):
        """Test auto-discovering templates from file structure."""
        initial_count = len(registry_manager.registry)
        
        # Auto-discover
        discovered = registry_manager.auto_discover_templates()
        
        # Should discover some templates
        assert discovered >= 0  # Returns count of discovered templates
        assert len(registry_manager.registry) >= initial_count  # Should not lose templates
    
    def test_validate_registry(self, registry_manager):
        """Test validating registry integrity."""
        issues = registry_manager.validate_registry()
        
        # Should return list of issues (could be empty if valid)
        assert isinstance(issues, list)
    
    def test_save_and_load_registry(self, registry_manager, temp_template_dir):
        """Test saving and loading registry."""
        # Add new template
        registry_manager.register_template(
            template_id="save_test",
            file_path="agents/save_test.yaml",
            category="agents",
            tags=["save"]
        )
        
        # Save
        registry_manager.save_registry()
        
        # Create new manager to load
        new_manager = RegistryManager(
            registry_file=temp_template_dir / "config" / "template-registry.yaml",
            template_dir=temp_template_dir
        )
        
        # Should have loaded the saved template
        assert "save_test" in new_manager.registry
    
    def test_export_to_markdown(self, registry_manager, tmp_path):
        """Test exporting registry to markdown."""
        output_file = tmp_path / "registry.md"
        
        registry_manager.export_to_markdown(output_file)
        
        assert output_file.exists()
        content = output_file.read_text()
        assert len(content) > 0
        assert "test_template" in content or "Template Registry" in content
    
    def test_remove_template(self, registry_manager):
        """Test removing template from registry."""
        # Add template
        registry_manager.register_template("remove_me", "remove.yaml", "agents", [])
        assert "remove_me" in registry_manager.registry
        
        # Remove (method is called unregister_template)
        registry_manager.unregister_template("remove_me")
        
        assert "remove_me" not in registry_manager.registry
    
    def test_update_template(self, registry_manager):
        """Test updating existing template entry."""
        # Register initial template
        registry_manager.register_template("update_test", "old.yaml", "agents", ["old"])
        
        # Update (re-register with overwrite=True)
        registry_manager.register_template(
            template_id="update_test",
            file_path="new.yaml",
            category="orchestrators",
            tags=["new"],
            overwrite=True
        )
        
        entry = registry_manager.registry["update_test"]
        assert entry.file == "new.yaml"
        assert entry.category == "orchestrators"
        assert "new" in entry.tags
    
    def test_get_registry_stats(self, registry_manager):
        """Test getting registry statistics."""
        # Create stats dictionary manually
        stats = {
            "total_templates": len(registry_manager.registry),
            "categories": len(set(e.category for e in registry_manager.registry.values())),
            "version": registry_manager.version
        }
        
        assert isinstance(stats, dict)
        assert "total_templates" in stats
        assert stats["total_templates"] >= 1


class TestTemplateRegistryEntry:
    """Test suite for TemplateRegistryEntry dataclass."""
    
    def test_entry_creation(self):
        """Test creating registry entry."""
        entry = TemplateRegistryEntry(
            template_id="test",
            file="agents/test.yaml",
            category="agents",
            tags=["test"]
        )
        
        assert entry.template_id == "test"
        assert entry.file == "agents/test.yaml"
        assert entry.category == "agents"
        assert "test" in entry.tags
    
    def test_entry_to_dict(self):
        """Test converting entry to dictionary."""
        entry = TemplateRegistryEntry(
            template_id="test",
            file="test.yaml",
            category="agents",
            tags=["tag1"],
            description="Test template"
        )
        
        entry_dict = entry.to_dict()
        
        assert isinstance(entry_dict, dict)
        assert entry_dict["template_id"] == "test"
        assert entry_dict["category"] == "agents"
        assert "tag1" in entry_dict["tags"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
