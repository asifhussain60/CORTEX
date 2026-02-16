"""
Test suite for CORTEX Documentation JSON Extractor

Tests:
- Frontmatter parsing
- Role determination
- Excerpt generation
- Category discovery
- JSON schema validation
"""

import pytest
import json
from pathlib import Path
import tempfile
import shutil


# Import after adding to path
import sys
pipeline_dir = Path(__file__).parent.parent / "cortex-docs" / "pipeline"
sys.path.insert(0, str(pipeline_dir))

# Import module
import importlib.util
spec = importlib.util.spec_from_file_location(
    "extract_json",
    pipeline_dir / "extract-json.py"
)
extract_json = importlib.util.module_from_spec(spec)
spec.loader.exec_module(extract_json)
ContentExtractor = extract_json.ContentExtractor


class TestContentExtractor:
    """Test ContentExtractor functionality."""
    
    @pytest.fixture
    def temp_content_dir(self):
        """Create temporary content directory structure."""
        temp_dir = Path(tempfile.mkdtemp())
        content_src = temp_dir / "content" / "src"
        content_src.mkdir(parents=True)
        
        # Create sample category
        capabilities = content_src / "capabilities"
        capabilities.mkdir()
        
        # Create sample markdown file
        sample_md = capabilities / "test-capability.md"
        sample_md.write_text("""---
title: Test Capability
type: explanation
audience: [Software Developers, Product Owners]
word_count: 100
last_verified: 2026-02-16
---

# Test Capability

This is a test capability document with **markdown** formatting.

Organizations using CORTEX benefit from this feature [Business Leaders].

## Technical Details

```python
def example():
    return "test"
```

Software developers can implement this feature [Software Developers].
""")
        
        yield content_src
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def extractor(self, temp_content_dir):
        """Create ContentExtractor instance."""
        output_path = temp_content_dir.parent / "assets" / "data" / "content.json"
        return ContentExtractor(temp_content_dir, output_path)
    
    def test_parse_frontmatter(self, extractor, temp_content_dir):
        """Test YAML frontmatter parsing."""
        md_file = temp_content_dir / "capabilities" / "test-capability.md"
        content = md_file.read_text()
        
        frontmatter = extractor._parse_frontmatter(content)
        
        assert frontmatter["title"] == "Test Capability"
        assert frontmatter["type"] == "explanation"
        assert "Software Developers" in frontmatter["audience"]
        assert frontmatter["word_count"] == 100
    
    def test_generate_excerpt(self, extractor):
        """Test excerpt generation."""
        body = """# Heading

This is a **test** paragraph with [links](http://example.com).

## Subheading

More content here."""
        
        excerpt = extractor._generate_excerpt(body, max_length=50)
        
        assert len(excerpt) <= 53  # max_length + '...'
        assert "**" not in excerpt  # Markdown removed
        assert "[" not in excerpt  # Links removed
        assert excerpt.endswith("...")
    
    def test_determine_roles_from_audience(self, extractor, temp_content_dir):
        """Test role determination from frontmatter audience."""
        md_file = temp_content_dir / "capabilities" / "test-capability.md"
        content = md_file.read_text()
        
        frontmatter = extractor._parse_frontmatter(content)
        roles = extractor._determine_roles(frontmatter, content, "capabilities")
        
        assert "product-owner" in roles
        assert "software-engineer" in roles
    
    def test_determine_roles_from_keywords(self, extractor):
        """Test role determination from content keywords."""
        frontmatter = {}
        content = "This document discusses governance and compliance requirements."
        
        roles = extractor._determine_roles(frontmatter, content, "capabilities")
        
        assert "business-leader" in roles  # "governance" keyword
    
    def test_discover_categories(self, extractor, temp_content_dir):
        """Test category directory discovery."""
        # Add another category
        (temp_content_dir / "mcp").mkdir()
        
        categories = extractor._discover_categories()
        
        assert len(categories) == 2
        assert any(cat.name == "capabilities" for cat in categories)
        assert any(cat.name == "mcp" for cat in categories)
    
    def test_extract_file(self, extractor, temp_content_dir):
        """Test single file extraction."""
        md_file = temp_content_dir / "capabilities" / "test-capability.md"
        
        file_data = extractor._extract_file(md_file, "capabilities")
        
        assert file_data["slug"] == "test-capability"
        assert file_data["title"] == "Test Capability"
        assert file_data["category"] == "capabilities"
        assert "software-engineer" in file_data["roles"]
        assert len(file_data["excerpt"]) > 0
        # Check HTML contains h1 tag (may have attributes like id)
        assert "<h1" in file_data["content_html"]
        assert "Test Capability" in file_data["content_html"]
    
    def test_slugify_title(self, extractor):
        """Test slug to title conversion."""
        assert extractor._slugify_title("test-capability") == "Test Capability"
        assert extractor._slugify_title("mcp-overview") == "Mcp Overview"
    
    def test_full_extraction_pipeline(self, extractor, temp_content_dir):
        """Test complete extraction workflow."""
        result = extractor.run()
        
        assert "generated_at" in result
        assert "version" in result
        assert "categories" in result
        assert "roles" in result
        
        # Verify categories
        assert len(result["categories"]) > 0
        cap_cat = next(cat for cat in result["categories"] if cat["id"] == "capabilities")
        assert cap_cat["file_count"] == 1
        assert len(cap_cat["files"]) == 1
        
        # Verify roles definition
        assert "business-leader" in result["roles"]
        assert "product-owner" in result["roles"]
        assert "software-engineer" in result["roles"]
    
    def test_json_output_schema(self, extractor):
        """Test JSON output conforms to expected schema."""
        result = extractor.run()
        
        # Schema validation
        assert isinstance(result["categories"], list)
        assert isinstance(result["roles"], dict)
        
        for category in result["categories"]:
            assert "id" in category
            assert "title" in category
            assert "file_count" in category
            assert "files" in category
            assert isinstance(category["files"], list)
        
        for role_id, role_config in result["roles"].items():
            assert "id" in role_config
            assert "label" in role_config
            assert "icon" in role_config
            assert "focus" in role_config
            assert "categories" in role_config
            assert isinstance(role_config["categories"], list)
    
    def test_json_file_written(self, extractor):
        """Test JSON file is written to disk."""
        extractor.run()
        
        assert extractor.output_path.exists()
        
        # Verify valid JSON
        with open(extractor.output_path) as f:
            data = json.load(f)
        
        assert "categories" in data
        assert "roles" in data


class TestRoleConfiguration:
    """Test role configuration logic."""
    
    def test_business_leader_categories(self):
        """Test business leader sees correct categories."""
        extractor = ContentExtractor(Path("."), Path("."))
        bl_config = extractor.content_data["roles"]["business-leader"]
        
        assert "capabilities" in bl_config["categories"]
        assert "governance" in bl_config["categories"]
        assert "infrastructure" in bl_config["categories"]
        assert "toolkit" not in bl_config["categories"]  # Too technical
    
    def test_product_owner_categories(self):
        """Test product owner sees correct categories."""
        extractor = ContentExtractor(Path("."), Path("."))
        po_config = extractor.content_data["roles"]["product-owner"]
        
        assert "orchestration" in po_config["categories"]
        assert "mcp" in po_config["categories"]
        assert "capabilities" in po_config["categories"]
    
    def test_software_engineer_sees_all(self):
        """Test software engineer sees all technical categories."""
        extractor = ContentExtractor(Path("."), Path("."))
        se_config = extractor.content_data["roles"]["software-engineer"]
        
        assert "lens" in se_config["categories"]
        assert "toolkit" in se_config["categories"]
        assert "diagrams" in se_config["categories"]
        assert "learning" in se_config["categories"]
