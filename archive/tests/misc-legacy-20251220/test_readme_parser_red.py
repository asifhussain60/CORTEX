"""
Tests for README Deep Parser & Section Extractor

RED PHASE: Write failing tests first

Extracts structured information from README.md files for executive summaries.

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
import tempfile
from typing import Dict, List


# Import will fail until we create the module (RED phase)
try:
    from src.intelligence.readme_parser import (
        ReadmeParser,
        ReadmeSection,
        ReadmeAnalysis
    )
except ImportError:
    # Expected during RED phase - we'll create these classes in GREEN phase
    ReadmeParser = None
    ReadmeSection = None
    ReadmeAnalysis = None


@pytest.fixture
def temp_readme():
    """Create temporary README file for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        readme_path = Path(tmpdir) / "README.md"
        yield readme_path


class TestReadmeParserInitialization:
    """Test parser initialization."""
    
    @pytest.mark.skipif(ReadmeParser is None, reason="RED phase - module not created yet")
    def test_init_with_file(self, temp_readme):
        """Should initialize with README file path."""
        temp_readme.write_text("# Test README")
        parser = ReadmeParser(temp_readme)
        assert parser.file_path == temp_readme
    
    @pytest.mark.skipif(ReadmeParser is None, reason="RED phase - module not created yet")
    def test_init_with_text(self):
        """Should initialize with direct text content."""
        parser = ReadmeParser(content="# Test README\n\nThis is content.")
        assert parser.content is not None
    
    @pytest.mark.skipif(ReadmeParser is None, reason="RED phase - module not created yet")
    def test_missing_file_raises_error(self):
        """Should raise error for non-existent file."""
        with pytest.raises(FileNotFoundError):
            ReadmeParser(Path("nonexistent.md"))


class TestSectionExtraction:
    """Test markdown section extraction."""
    
    @pytest.mark.skipif(ReadmeParser is None, reason="RED phase - module not created yet")
    def test_extract_h2_sections(self, temp_readme):
        """Should extract all H2 (##) sections."""
        content = """
# Main Title

## Features
- Feature 1
- Feature 2

## Installation
Run pip install

## License
MIT License
"""
        temp_readme.write_text(content)
        parser = ReadmeParser(temp_readme)
        analysis = parser.analyze()
        
        section_titles = [s.title for s in analysis.sections]
        assert "Features" in section_titles
        assert "Installation" in section_titles
        assert "License" in section_titles
    
    @pytest.mark.skipif(ReadmeParser is None, reason="RED phase - module not created yet")
    def test_extract_h3_sections(self, temp_readme):
        """Should extract H3 (###) sections under H2."""
        content = """
## Features

### Core Features
- Authentication
- Dashboard

### Advanced Features
- Analytics
"""
        temp_readme.write_text(content)
        parser = ReadmeParser(temp_readme)
        analysis = parser.analyze()
        
        # Should find nested sections
        assert len(analysis.sections) >= 3
    
    @pytest.mark.skipif(ReadmeParser is None, reason="RED phase - module not created yet")
    def test_section_content_extraction(self, temp_readme):
        """Should extract content under each heading."""
        content = """
## Overview

This is a project management tool that helps teams collaborate.
It includes features for task tracking and reporting.

## Features
- Task management
- Team collaboration
"""
        temp_readme.write_text(content)
        parser = ReadmeParser(temp_readme)
        analysis = parser.analyze()
        
        overview = next((s for s in analysis.sections if s.title == "Overview"), None)
        assert overview is not None
        assert "project management tool" in overview.content
        assert len(overview.content) > 50


class TestContentPrioritization:
    """Test section informativeness scoring and prioritization."""
    
    @pytest.mark.skipif(ReadmeParser is None, reason="RED phase - module not created yet")
    def test_features_section_high_priority(self, temp_readme):
        """Features section should have high informativeness score."""
        content = """
## Features
- User authentication
- Real-time updates
- Data visualization

## License
MIT
"""
        temp_readme.write_text(content)
        parser = ReadmeParser(temp_readme)
        analysis = parser.analyze()
        
        features = next((s for s in analysis.sections if s.title == "Features"), None)
        license_sec = next((s for s in analysis.sections if s.title == "License"), None)
        
        assert features.informativeness_score > license_sec.informativeness_score
    
    @pytest.mark.skipif(ReadmeParser is None, reason="RED phase - module not created yet")
    def test_prioritization_order(self, temp_readme):
        """Sections should be prioritized: Features > Overview > Installation > License."""
        content = """
## License
MIT

## Features
- Feature 1

## Overview
This is a tool

## Installation
pip install
"""
        temp_readme.write_text(content)
        parser = ReadmeParser(temp_readme)
        analysis = parser.analyze()
        
        # Get prioritized sections
        prioritized = analysis.get_prioritized_sections()
        titles = [s.title for s in prioritized]
        
        # Features should come before License
        features_idx = titles.index("Features")
        license_idx = titles.index("License")
        assert features_idx < license_idx


class TestFallbackLogic:
    """Test fallback when structured sections missing."""
    
    @pytest.mark.skipif(ReadmeParser is None, reason="RED phase - module not created yet")
    def test_fallback_to_paragraphs(self, temp_readme):
        """Should fall back to first 3 paragraphs if no headings."""
        content = """
This is a simple README without headings.

It has multiple paragraphs describing the project.

This is the third paragraph with more information.

This is the fourth paragraph.
"""
        temp_readme.write_text(content)
        parser = ReadmeParser(temp_readme)
        analysis = parser.analyze()
        
        # Should extract content even without sections
        assert analysis.summary_text is not None
        assert len(analysis.summary_text) > 50
    
    @pytest.mark.skipif(ReadmeParser is None, reason="RED phase - module not created yet")
    def test_minimal_readme(self, temp_readme):
        """Should handle minimal README gracefully."""
        content = "# MyProject\n\nA simple project."
        temp_readme.write_text(content)
        parser = ReadmeParser(temp_readme)
        analysis = parser.analyze()
        
        assert analysis is not None
        assert analysis.project_name == "MyProject"


class TestMarkdownProcessing:
    """Test markdown formatting removal and content processing."""
    
    @pytest.mark.skipif(ReadmeParser is None, reason="RED phase - module not created yet")
    def test_remove_markdown_formatting(self):
        """Should remove markdown syntax (**, ##, `, etc.)."""
        parser = ReadmeParser(content="## Test\n\nThis is **bold** and `code`.")
        analysis = parser.analyze()
        
        # Content should have markdown removed
        assert "**" not in analysis.summary_text
        assert "##" not in analysis.summary_text
    
    @pytest.mark.skipif(ReadmeParser is None, reason="RED phase - module not created yet")
    def test_extract_bullet_points(self, temp_readme):
        """Should extract and parse bullet point lists."""
        content = """
## Features
- Feature A: Does something
- Feature B: Does another thing
- Feature C: Does more
"""
        temp_readme.write_text(content)
        parser = ReadmeParser(temp_readme)
        analysis = parser.analyze()
        
        features = next((s for s in analysis.sections if s.title == "Features"), None)
        assert features.bullet_points is not None
        assert len(features.bullet_points) == 3
        assert "Feature A" in features.bullet_points[0]


class TestBusinessPurposeExtraction:
    """Test extracting business purpose from Overview/About sections."""
    
    @pytest.mark.skipif(ReadmeParser is None, reason="RED phase - module not created yet")
    def test_extract_purpose_from_overview(self, temp_readme):
        """Should extract business purpose from Overview section."""
        content = """
## Overview

MyApp is a project management platform that helps distributed teams 
coordinate work efficiently. It provides real-time collaboration tools 
and automated reporting to improve productivity.
"""
        temp_readme.write_text(content)
        parser = ReadmeParser(temp_readme)
        analysis = parser.analyze()
        
        assert analysis.business_purpose is not None
        assert "project management" in analysis.business_purpose.lower()
        assert "distributed teams" in analysis.business_purpose.lower()
    
    @pytest.mark.skipif(ReadmeParser is None, reason="RED phase - module not created yet")
    def test_extract_capabilities_from_features(self, temp_readme):
        """Should identify key capabilities from feature lists."""
        content = """
## Features

- **User Management**: Create, update, and manage user accounts
- **Real-time Messaging**: Chat with team members instantly
- **Task Tracking**: Monitor progress on projects and tasks
- **Analytics Dashboard**: Visualize team performance metrics
"""
        temp_readme.write_text(content)
        parser = ReadmeParser(temp_readme)
        analysis = parser.analyze()
        
        capabilities = analysis.key_capabilities
        assert len(capabilities) >= 4
        assert any("user management" in c.lower() for c in capabilities)
        assert any("messaging" in c.lower() for c in capabilities)


class TestSynthesisAndSummary:
    """Test summary synthesis from extracted sections."""
    
    @pytest.mark.skipif(ReadmeParser is None, reason="RED phase - module not created yet")
    def test_generate_coherent_summary(self, temp_readme):
        """Should generate 150-300 word coherent summary."""
        content = """
# ProjectX

## Overview
ProjectX is an advanced data analytics platform for enterprise teams.

## Features
- Real-time data processing
- Machine learning integration
- Customizable dashboards
- Multi-tenant architecture

## Installation
Run pip install projectx

## License
MIT License
"""
        temp_readme.write_text(content)
        parser = ReadmeParser(temp_readme)
        analysis = parser.analyze()
        
        summary = analysis.generate_summary()
        word_count = len(summary.split())
        
        assert 150 <= word_count <= 300
        assert "analytics" in summary.lower()
        assert any(word in summary.lower() for word in ["data", "machine learning", "dashboard"])
    
    @pytest.mark.skipif(ReadmeParser is None, reason="RED phase - module not created yet")
    def test_deduplication_across_sources(self):
        """Should deduplicate similar phrases across sections."""
        content = """
## Overview
ProjectX provides real-time analytics.

## Features
- Real-time analytics capabilities
- Live data monitoring
"""
        parser = ReadmeParser(content=content)
        analysis = parser.analyze()
        summary = analysis.generate_summary()
        
        # Should not repeat "real-time analytics" multiple times
        assert summary.lower().count("real-time analytics") <= 2


class TestPerformance:
    """Test parser performance."""
    
    @pytest.mark.skipif(ReadmeParser is None, reason="RED phase - module not created yet")
    def test_parse_large_readme_under_1_second(self, temp_readme):
        """Should parse large README (<10K lines) in <1 second."""
        import time
        
        # Generate large README
        content = "# Large Project\n\n"
        for i in range(100):
            content += f"## Section {i}\n\nContent for section {i}.\n\n"
        
        temp_readme.write_text(content)
        
        parser = ReadmeParser(temp_readme)
        start = time.time()
        analysis = parser.analyze()
        elapsed = time.time() - start
        
        assert elapsed < 1.0
        assert len(analysis.sections) >= 90  # Most sections extracted


class TestDiverseReadmeFormats:
    """Test with diverse real-world README formats."""
    
    @pytest.mark.skipif(ReadmeParser is None, reason="RED phase - module not created yet")
    def test_github_style_readme(self, temp_readme):
        """Should handle GitHub-style README with badges and links."""
        content = """
# MyProject

[![Build Status](https://travis-ci.org/user/repo.svg)](https://travis-ci.org/user/repo)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A simple description of my project.

## Installation

```bash
npm install myproject
```

## Usage

```javascript
const myproject = require('myproject');
myproject.run();
```
"""
        temp_readme.write_text(content)
        parser = ReadmeParser(temp_readme)
        analysis = parser.analyze()
        
        assert analysis.project_name == "MyProject"
        assert len(analysis.sections) >= 2
    
    @pytest.mark.skipif(ReadmeParser is None, reason="RED phase - module not created yet")
    def test_minimal_single_line_readme(self, temp_readme):
        """Should handle single-line README."""
        temp_readme.write_text("Simple project for testing.")
        parser = ReadmeParser(temp_readme)
        analysis = parser.analyze()
        
        assert analysis.summary_text == "Simple project for testing."


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
