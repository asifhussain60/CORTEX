"""
Tests for README Deep-Parser

RED PHASE: Write failing tests first

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
from pathlib import Path
from src.intelligence.readme_parser import (
    ReadmeParser,
    ReadmeMetadata,
    ReadmeSection,
    find_readme
)


@pytest.fixture
def sample_readme_content():
    """Sample README content for testing."""
    return """# Awesome Project

A comprehensive solution for managing data workflows.

![Build Status](https://img.shields.io/badge/build-passing-green)
![License](https://img.shields.io/badge/license-MIT-blue)

## Purpose

This project provides a robust framework for building and managing complex data workflows. 
It simplifies the process of data transformation and enables seamless integration with various data sources.

## Features

- **Real-time Processing**: Process data streams in real-time
- **Scalable Architecture**: Handles millions of records per second
- **Easy Integration**: Connect to 100+ data sources
- Multi-cloud support (AWS, Azure, GCP)
- Built-in monitoring and alerting

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure settings in `config.yaml`
4. Run setup: `python setup.py install`

## Usage

Basic example:

```python
from workflow import Pipeline

pipeline = Pipeline()
pipeline.add_source('database')
pipeline.run()
```

Advanced usage:

```python
pipeline = Pipeline(config='advanced.yaml')
pipeline.add_transform(lambda x: x * 2)
pipeline.execute()
```

## Technology Stack

- Python 3.9+
- Apache Kafka
- PostgreSQL
- Redis
- Docker

## Contributing

See [CONTRIBUTING.md](https://github.com/example/CONTRIBUTING.md) for details.

## License

MIT License - see [LICENSE](https://github.com/example/LICENSE) file.
"""


class TestReadmeParserInitialization:
    """Test parser initialization."""
    
    def test_parser_creation(self):
        """Should create parser instance."""
        parser = ReadmeParser()
        assert parser is not None


class TestTitleExtraction:
    """Test title extraction."""
    
    def test_extract_title_from_h1(self, sample_readme_content):
        """Should extract title from # heading."""
        parser = ReadmeParser()
        metadata = parser.parse_content(sample_readme_content)
        
        assert metadata.title == "Awesome Project"
    
    def test_no_title_returns_none(self):
        """Should return None when no heading found."""
        parser = ReadmeParser()
        content = "Just plain text without headings."
        metadata = parser.parse_content(content)
        
        assert metadata.title is None


class TestDescriptionExtraction:
    """Test description extraction."""
    
    def test_extract_description(self, sample_readme_content):
        """Should extract first paragraph as description."""
        parser = ReadmeParser()
        metadata = parser.parse_content(sample_readme_content)
        
        assert metadata.description is not None
        assert "comprehensive solution" in metadata.description.lower()
    
    def test_description_skips_badges(self):
        """Should skip badge lines when extracting description."""
        parser = ReadmeParser()
        content = """# Title
![Badge](url)
**Version**: 1.0
This is the actual description.
"""
        metadata = parser.parse_content(content)
        
        assert "This is the actual description" in metadata.description


class TestSectionParsing:
    """Test section structure parsing."""
    
    def test_parse_sections(self, sample_readme_content):
        """Should parse all sections with headings."""
        parser = ReadmeParser()
        metadata = parser.parse_content(sample_readme_content)
        
        assert len(metadata.sections) > 0
        section_titles = [s.title for s in metadata.sections]
        assert "Purpose" in section_titles
        assert "Features" in section_titles
        assert "Installation" in section_titles
    
    def test_section_levels(self, sample_readme_content):
        """Should correctly identify heading levels."""
        parser = ReadmeParser()
        metadata = parser.parse_content(sample_readme_content)
        
        # "Purpose" is ## (level 2)
        purpose_section = next(s for s in metadata.sections if s.title == "Purpose")
        assert purpose_section.level == 2
    
    def test_section_content(self, sample_readme_content):
        """Should capture section content."""
        parser = ReadmeParser()
        metadata = parser.parse_content(sample_readme_content)
        
        purpose_section = next(s for s in metadata.sections if s.title == "Purpose")
        assert len(purpose_section.content) > 0
        assert "framework" in purpose_section.content.lower()


class TestPurposeExtraction:
    """Test purpose statement extraction."""
    
    def test_extract_purpose_from_section(self, sample_readme_content):
        """Should extract purpose from Purpose/About section."""
        parser = ReadmeParser()
        metadata = parser.parse_content(sample_readme_content)
        
        assert metadata.purpose is not None
        assert "framework" in metadata.purpose.lower()


class TestFeatureExtraction:
    """Test feature list extraction."""
    
    def test_extract_features_list(self, sample_readme_content):
        """Should extract features as list items."""
        parser = ReadmeParser()
        metadata = parser.parse_content(sample_readme_content)
        
        assert len(metadata.features) >= 4
        assert any("real-time" in f.lower() for f in metadata.features)
        assert any("scalable" in f.lower() for f in metadata.features)
    
    def test_features_remove_markdown(self):
        """Should remove markdown formatting from features."""
        parser = ReadmeParser()
        content = """# Project
## Features
- **Bold feature**: Description
- *Italic feature*
- [Linked feature](http://example.com)
"""
        metadata = parser.parse_content(content)
        
        # Should have extracted features without markdown
        assert len(metadata.features) == 3
        assert "Bold feature" in metadata.features[0]
        assert "*" not in metadata.features[1]


class TestInstallationExtraction:
    """Test installation steps extraction."""
    
    def test_extract_installation_steps(self, sample_readme_content):
        """Should extract installation steps as ordered list."""
        parser = ReadmeParser()
        metadata = parser.parse_content(sample_readme_content)
        
        assert len(metadata.installation_steps) >= 3
        assert any("clone" in step.lower() for step in metadata.installation_steps)
        assert any("dependencies" in step.lower() for step in metadata.installation_steps)


class TestUsageExtraction:
    """Test usage example extraction."""
    
    def test_extract_code_examples(self, sample_readme_content):
        """Should extract code blocks from usage section."""
        parser = ReadmeParser()
        metadata = parser.parse_content(sample_readme_content)
        
        assert len(metadata.usage_examples) >= 2
        assert any("Pipeline" in example for example in metadata.usage_examples)


class TestTechnologyExtraction:
    """Test technology stack extraction."""
    
    def test_extract_technologies(self, sample_readme_content):
        """Should extract technology list."""
        parser = ReadmeParser()
        metadata = parser.parse_content(sample_readme_content)
        
        assert len(metadata.technologies) >= 4
        assert any("python" in tech.lower() for tech in metadata.technologies)
        assert any("kafka" in tech.lower() for tech in metadata.technologies)


class TestBadgeExtraction:
    """Test badge extraction."""
    
    def test_extract_badge_urls(self, sample_readme_content):
        """Should extract badge image URLs."""
        parser = ReadmeParser()
        metadata = parser.parse_content(sample_readme_content)
        
        assert len(metadata.badges) >= 2
        assert any("build" in badge.lower() for badge in metadata.badges)


class TestLinkExtraction:
    """Test hyperlink extraction."""
    
    def test_extract_markdown_links(self, sample_readme_content):
        """Should extract markdown links."""
        parser = ReadmeParser()
        metadata = parser.parse_content(sample_readme_content)
        
        assert len(metadata.links) >= 2
        assert "CONTRIBUTING.md" in metadata.links
        assert "LICENSE" in metadata.links


class TestSerialization:
    """Test metadata serialization."""
    
    def test_to_dict_conversion(self, sample_readme_content):
        """Should convert metadata to dictionary."""
        parser = ReadmeParser()
        metadata = parser.parse_content(sample_readme_content)
        result = parser.to_dict(metadata)
        
        assert isinstance(result, dict)
        assert 'title' in result
        assert 'features' in result
        assert 'sections' in result
    
    def test_to_json_conversion(self, sample_readme_content):
        """Should convert metadata to JSON string."""
        parser = ReadmeParser()
        metadata = parser.parse_content(sample_readme_content)
        json_str = parser.to_json(metadata)
        
        assert isinstance(json_str, str)
        assert '"title"' in json_str
        assert '"features"' in json_str


class TestFileOperations:
    """Test file reading operations."""
    
    def test_parse_file(self, sample_readme_content):
        """Should parse README from file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            readme_path = Path(tmpdir) / 'README.md'
            readme_path.write_text(sample_readme_content)
            
            parser = ReadmeParser()
            metadata = parser.parse_file(readme_path)
            
            assert metadata.title == "Awesome Project"
            assert len(metadata.features) >= 4
    
    def test_file_not_found_raises_error(self):
        """Should raise FileNotFoundError for missing file."""
        parser = ReadmeParser()
        
        with pytest.raises(FileNotFoundError):
            parser.parse_file(Path('/nonexistent/README.md'))


class TestFindReadme:
    """Test README file discovery."""
    
    def test_find_readme_standard_name(self):
        """Should find README.md in directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            readme = tmpdir / 'README.md'
            readme.write_text('# Test')
            
            found = find_readme(tmpdir)
            assert found == readme
    
    def test_find_readme_case_insensitive(self):
        """Should find readme with different case."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            readme = tmpdir / 'readme.md'
            readme.write_text('# Test')
            
            found = find_readme(tmpdir)
            assert found == readme
    
    def test_find_readme_returns_none_if_missing(self):
        """Should return None if no README found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            found = find_readme(Path(tmpdir))
            assert found is None


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_content(self):
        """Should handle empty content gracefully."""
        parser = ReadmeParser()
        metadata = parser.parse_content("")
        
        assert metadata.title is None
        assert metadata.description is None
        assert len(metadata.sections) == 0
    
    def test_content_without_sections(self):
        """Should handle README without section headings."""
        parser = ReadmeParser()
        content = "Just plain text without any headings or structure."
        metadata = parser.parse_content(content)
        
        assert metadata.title is None
        assert len(metadata.sections) == 0
    
    def test_malformed_markdown(self):
        """Should handle malformed markdown gracefully."""
        parser = ReadmeParser()
        content = """# Title
## Features
- Unclosed **bold
- Unclosed [link(incomplete
"""
        metadata = parser.parse_content(content)
        
        # Should not crash, even with malformed markdown
        assert metadata.title == "Title"
        assert len(metadata.sections) > 0


class TestKnowledgeGraphIntegration:
    """Test knowledge graph updates."""
    
    def test_knowledge_graph_update_attempt(self, sample_readme_content):
        """Should attempt to update knowledge graph without failing."""
        parser = ReadmeParser()
        
        # Should not raise exception even if knowledge graph unavailable
        metadata = parser.parse_content(sample_readme_content)
        assert metadata is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
