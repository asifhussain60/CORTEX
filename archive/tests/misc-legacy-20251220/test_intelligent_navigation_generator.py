"""
Tests for IntelligentNavigationGenerator

TDD RED Phase - Tests written BEFORE implementation
These tests MUST fail initially to prove they test real behavior.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file
"""

import pytest
from pathlib import Path
from typing import Dict, List, Any
import tempfile
import shutil
import yaml


class TestIntelligentNavigationGeneratorRED:
    """
    RED Phase Tests - Must fail before implementation
    
    Acceptance Criteria:
    1. Discovers all .md files in docs/ directory
    2. Respects frontmatter metadata (title, category, weight, hidden)
    3. Generates 3-level deep navigation hierarchy
    4. Preserves manual overrides in config
    5. Updates mkdocs.yml without breaking existing structure
    """
    
    @pytest.fixture
    def temp_docs_dir(self):
        """Create temporary docs directory with sample files"""
        temp_dir = tempfile.mkdtemp()
        docs_path = Path(temp_dir) / "docs"
        docs_path.mkdir()
        
        # Create sample markdown files with frontmatter
        self._create_md_file(
            docs_path / "index.md",
            title="Home",
            category="root",
            weight=1
        )
        
        self._create_md_file(
            docs_path / "getting-started.md",
            title="Getting Started",
            category="guides",
            weight=10
        )
        
        # Create nested structure
        guides_dir = docs_path / "guides"
        guides_dir.mkdir()
        
        self._create_md_file(
            guides_dir / "installation.md",
            title="Installation",
            category="guides",
            weight=20
        )
        
        self._create_md_file(
            guides_dir / "configuration.md",
            title="Configuration",
            category="guides",
            weight=30
        )
        
        # Create API docs
        api_dir = docs_path / "api"
        api_dir.mkdir()
        
        self._create_md_file(
            api_dir / "overview.md",
            title="API Overview",
            category="api",
            weight=100
        )
        
        # Create hidden file (should be excluded)
        self._create_md_file(
            api_dir / "internal.md",
            title="Internal API",
            category="api",
            weight=200,
            hidden=True
        )
        
        yield docs_path
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def _create_md_file(self, path: Path, title: str, category: str, weight: int, hidden: bool = False):
        """Helper to create markdown file with frontmatter"""
        frontmatter = {
            "title": title,
            "category": category,
            "weight": weight
        }
        if hidden:
            frontmatter["hidden"] = True
        
        content = "---\n"
        content += yaml.dump(frontmatter)
        content += "---\n\n"
        content += f"# {title}\n\nContent goes here."
        
        path.write_text(content)
    
    def test_class_exists(self):
        """AC1 Setup: IntelligentNavigationGenerator class must exist"""
        from documentation.generators.intelligent_navigation_generator import (
            IntelligentNavigationGenerator
        )
        
        assert IntelligentNavigationGenerator is not None
    
    def test_discovers_all_markdown_files(self, temp_docs_dir):
        """AC1: Discovers all .md files in docs/ directory"""
        from documentation.generators.intelligent_navigation_generator import (
            IntelligentNavigationGenerator
        )
        
        generator = IntelligentNavigationGenerator(temp_docs_dir)
        discovered_files = generator.discover_markdown_files()
        
        # Should find 5 non-hidden files
        assert len(discovered_files) == 5
        
        # Should include all non-hidden files
        file_names = [f.name for f in discovered_files]
        assert "index.md" in file_names
        assert "getting-started.md" in file_names
        assert "installation.md" in file_names
        assert "configuration.md" in file_names
        assert "overview.md" in file_names
        
        # Should NOT include hidden file
        assert "internal.md" not in file_names
    
    def test_extracts_frontmatter_metadata(self, temp_docs_dir):
        """AC2: Respects frontmatter metadata (title, category, weight, hidden)"""
        from documentation.generators.intelligent_navigation_generator import (
            IntelligentNavigationGenerator
        )
        
        generator = IntelligentNavigationGenerator(temp_docs_dir)
        file_path = temp_docs_dir / "getting-started.md"
        
        metadata = generator.extract_frontmatter(file_path)
        
        assert metadata["title"] == "Getting Started"
        assert metadata["category"] == "guides"
        assert metadata["weight"] == 10
        assert "hidden" not in metadata or metadata["hidden"] is False
    
    def test_categorizes_files_by_metadata(self, temp_docs_dir):
        """AC2: Categorizes files based on frontmatter category"""
        from documentation.generators.intelligent_navigation_generator import (
            IntelligentNavigationGenerator
        )
        
        generator = IntelligentNavigationGenerator(temp_docs_dir)
        files = generator.discover_markdown_files()
        categorized = generator.categorize_files(files)
        
        assert "root" in categorized
        assert "guides" in categorized
        assert "api" in categorized
        
        assert len(categorized["guides"]) == 3  # getting-started, installation, configuration
        assert len(categorized["api"]) == 1     # overview (internal is hidden)
    
    def test_generates_three_level_hierarchy(self, temp_docs_dir):
        """AC3: Generates 3-level deep navigation hierarchy"""
        from documentation.generators.intelligent_navigation_generator import (
            IntelligentNavigationGenerator
        )
        
        generator = IntelligentNavigationGenerator(temp_docs_dir)
        nav_structure = generator.generate_navigation_structure()
        
        # Level 1: Top-level categories
        assert len(nav_structure) >= 2  # At least root and guides
        
        # Level 2: Should have sections within categories
        guides_section = next((item for item in nav_structure if "Guides" in item), None)
        assert guides_section is not None
        
        # Level 3: Should have pages within sections
        guides_items = guides_section["Guides"]
        assert len(guides_items) >= 3
    
    def test_respects_weight_ordering(self, temp_docs_dir):
        """AC3: Orders items by weight metadata"""
        from documentation.generators.intelligent_navigation_generator import (
            IntelligentNavigationGenerator
        )
        
        generator = IntelligentNavigationGenerator(temp_docs_dir)
        nav_structure = generator.generate_navigation_structure()
        
        # Find guides section
        guides_section = next((item for item in nav_structure if "Guides" in item), None)
        guides_items = guides_section["Guides"]
        
        # Extract titles in order
        titles = []
        for item in guides_items:
            if isinstance(item, dict):
                titles.append(list(item.keys())[0])
            elif isinstance(item, str):
                titles.append(item)
        
        # Should be ordered by weight: Getting Started (10) -> Installation (20) -> Configuration (30)
        assert titles.index("Getting Started") < titles.index("Installation")
        assert titles.index("Installation") < titles.index("Configuration")
    
    def test_preserves_manual_overrides(self, temp_docs_dir):
        """AC4: Preserves manual overrides in config"""
        from documentation.generators.intelligent_navigation_generator import (
            IntelligentNavigationGenerator
        )
        
        # Create existing mkdocs.yml with manual overrides
        mkdocs_path = temp_docs_dir.parent / "mkdocs.yml"
        existing_config = {
            "site_name": "My Custom Site",
            "nav": [
                {"Manual Override": "custom-page.md"}
            ]
        }
        
        with open(mkdocs_path, "w") as f:
            yaml.dump(existing_config, f)
        
        generator = IntelligentNavigationGenerator(temp_docs_dir, mkdocs_path)
        generator.update_mkdocs_navigation()
        
        # Load updated config
        with open(mkdocs_path, "r") as f:
            updated_config = yaml.safe_load(f)
        
        # Manual override should still exist
        nav_items = updated_config["nav"]
        manual_override = next((item for item in nav_items if "Manual Override" in item), None)
        assert manual_override is not None
    
    def test_updates_mkdocs_yml_safely(self, temp_docs_dir):
        """AC5: Updates mkdocs.yml without breaking existing structure"""
        from documentation.generators.intelligent_navigation_generator import (
            IntelligentNavigationGenerator
        )
        
        # Create existing mkdocs.yml
        mkdocs_path = temp_docs_dir.parent / "mkdocs.yml"
        existing_config = {
            "site_name": "CORTEX Docs",
            "site_url": "https://example.com",
            "theme": {"name": "material"},
            "plugins": ["search"],
            "nav": []
        }
        
        with open(mkdocs_path, "w") as f:
            yaml.dump(existing_config, f)
        
        generator = IntelligentNavigationGenerator(temp_docs_dir, mkdocs_path)
        generator.update_mkdocs_navigation()
        
        # Load updated config
        with open(mkdocs_path, "r") as f:
            updated_config = yaml.safe_load(f)
        
        # Existing settings should be preserved
        assert updated_config["site_name"] == "CORTEX Docs"
        assert updated_config["site_url"] == "https://example.com"
        assert updated_config["theme"]["name"] == "material"
        assert "search" in updated_config["plugins"]
        
        # Navigation should be updated
        assert len(updated_config["nav"]) > 0
    
    def test_handles_missing_frontmatter_gracefully(self, temp_docs_dir):
        """Edge Case: Files without frontmatter should use sensible defaults"""
        from documentation.generators.intelligent_navigation_generator import (
            IntelligentNavigationGenerator
        )
        
        # Create file without frontmatter
        no_frontmatter_file = temp_docs_dir / "no-metadata.md"
        no_frontmatter_file.write_text("# Just Content\n\nNo metadata here.")
        
        generator = IntelligentNavigationGenerator(temp_docs_dir)
        metadata = generator.extract_frontmatter(no_frontmatter_file)
        
        # Should provide defaults
        assert "title" in metadata  # Derived from filename or heading
        assert "weight" in metadata  # Default weight
        assert metadata.get("hidden") is False
    
    def test_handles_malformed_yaml(self, temp_docs_dir):
        """Edge Case: Malformed YAML frontmatter should not crash"""
        from documentation.generators.intelligent_navigation_generator import (
            IntelligentNavigationGenerator
        )
        
        # Create file with malformed YAML
        malformed_file = temp_docs_dir / "malformed.md"
        malformed_file.write_text("---\ntitle: Unclosed quote\"\ncategory: test\n---\n# Content")
        
        generator = IntelligentNavigationGenerator(temp_docs_dir)
        
        # Should handle gracefully (not crash)
        try:
            metadata = generator.extract_frontmatter(malformed_file)
            assert metadata is not None  # Should return defaults or partial data
        except Exception as e:
            pytest.fail(f"Should handle malformed YAML gracefully, but raised: {e}")
    
    def test_handles_nonexistent_docs_directory(self):
        """Edge Case: Non-existent docs directory should return empty list"""
        from documentation.generators.intelligent_navigation_generator import (
            IntelligentNavigationGenerator
        )
        
        nonexistent_path = Path("/tmp/does_not_exist_12345")
        generator = IntelligentNavigationGenerator(nonexistent_path)
        
        files = generator.discover_markdown_files()
        assert files == []
    
    def test_generates_nav_without_explicit_discovery(self, temp_docs_dir):
        """Edge Case: Should auto-discover if generate_navigation_structure called directly"""
        from documentation.generators.intelligent_navigation_generator import (
            IntelligentNavigationGenerator
        )
        
        generator = IntelligentNavigationGenerator(temp_docs_dir)
        
        # Call generate_navigation_structure without calling discover_markdown_files first
        nav = generator.generate_navigation_structure()
        
        assert len(nav) > 0  # Should have discovered files automatically
    
    def test_updates_navigation_without_mkdocs_path(self, temp_docs_dir):
        """Edge Case: Should handle update_mkdocs_navigation with no mkdocs_path"""
        from documentation.generators.intelligent_navigation_generator import (
            IntelligentNavigationGenerator
        )
        
        generator = IntelligentNavigationGenerator(temp_docs_dir)
        
        # Should not crash, just log warning
        try:
            generator.update_mkdocs_navigation()
        except Exception as e:
            pytest.fail(f"Should handle missing mkdocs_path gracefully, but raised: {e}")
    
    def test_extracts_title_from_heading(self, temp_docs_dir):
        """Edge Case: Should extract title from # heading when no frontmatter"""
        from documentation.generators.intelligent_navigation_generator import (
            IntelligentNavigationGenerator
        )
        
        # Create file with heading but no frontmatter
        heading_file = temp_docs_dir / "heading-title.md"
        heading_file.write_text("# Awesome Title\n\nContent here.")
        
        generator = IntelligentNavigationGenerator(temp_docs_dir)
        metadata = generator.extract_frontmatter(heading_file)
        
        assert metadata["title"] == "Awesome Title"
