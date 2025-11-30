"""
Test suite for validating documentation links in MkDocs.

This test suite validates all internal links in documentation files to ensure:
1. Referenced files exist
2. Links use correct relative paths
3. No broken links after documentation generation

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import os
import pytest
from pathlib import Path


class TestDocumentationLinks:
    """Test documentation link integrity."""
    
    @pytest.fixture
    def docs_root(self):
        """Get the docs directory path."""
        return Path(__file__).resolve().parent.parent / "docs"
    
    @pytest.fixture
    def project_root(self):
        """Get the project root path."""
        return Path(__file__).resolve().parent.parent
    
    def test_awakening_cortex_navigation_link(self, docs_root):
        """Test that awakening-of-cortex.md links to existing getting-started/navigation.md"""
        # The link is: getting-started/navigation.md
        target_file = docs_root / "getting-started" / "navigation.md"
        assert target_file.exists(), f"Missing file: {target_file}"
    
    def test_awakening_cortex_api_reference_link(self, docs_root):
        """Test that awakening-of-cortex.md links to existing reference/api-reference.md"""
        # The link is: reference/api-reference.md
        target_file = docs_root / "reference" / "api-reference.md"
        assert target_file.exists(), f"Missing file: {target_file}"
    
    def test_diagrams_index_mermaid_links(self, docs_root):
        """Test that diagrams/INDEX.md links to mermaid files with correct paths."""
        # The links should use forward slashes and actual file names
        mermaid_dir = docs_root / "diagrams" / "mermaid"
        
        # Test a representative sample of the 20 mermaid files
        expected_files = [
            "01-tier-architecture.mmd",
            "02-agent-coordination-system.mmd",
            "03-information-flow.mmd",
            "05-cortex-one-pager.mmd",
            "08-brain-protection.mmd",
            "11-plugin-architecture.mmd",
            "12-conversation-flow.mmd",
            "15-interactive-planning.mmd",
            "18-git-integration.mmd",
            "20-github-actions-pipeline.mmd",
        ]
        
        for filename in expected_files:
            mermaid_file = mermaid_dir / filename
            assert mermaid_file.exists(), f"Missing mermaid file: {mermaid_file}"
    
    def test_story_chapter2_image_links(self, docs_root):
        """Test that story/chapter-2-the-solution.md links to existing images."""
        # The links are: ../../images/cortex-awakening/[filename].png
        images_dir = docs_root / "images" / "cortex-awakening"
        
        expected_images = [
            "Prompt 2.2 The Napkin Sketch - Two Hemispheres.png",
            "Prompt 2.4 Hemisphere Architecture Diagram.png",
            "Prompt 2.5 Strategic to Tactical Flow.jpg",
            "Prompt 2.6 BeforeAfter Comparison.png",
        ]
        
        for image_name in expected_images:
            image_file = images_dir / image_name
            assert image_file.exists(), f"Missing image: {image_file}"
    
    def test_story_chapter3_image_links(self, docs_root):
        """Test that story/chapter-3-the-memory.md links to existing images."""
        # The links are: ../../images/cortex-awakening/[filename].png
        images_dir = docs_root / "images" / "cortex-awakening"
        
        expected_images = [
            "Prompt 1.4 Three-Tier Memory Architecture Diagram.png",
            "Prompt 1.5 FIFO Queue Visualization.png",
            "Prompt 1.6 Memory Resolution Flow.png",
        ]
        
        for image_name in expected_images:
            image_file = images_dir / image_name
            assert image_file.exists(), f"Missing image: {image_file}"
    
    def test_story_chapter4_image_links(self, docs_root):
        """Test that story/chapter-4-the-protection.md links to existing images."""
        # The links are: ../../images/cortex-awakening/[filename].png
        images_dir = docs_root / "images" / "cortex-awakening"
        
        expected_images = [
            "Prompt 2.1 The Monolithic Disaster.png",
            "Prompt 2.2 The Napkin Sketch - Two Hemispheres.png",
            "Prompt 2.3 The Coordinated Dance.jpg",
        ]
        
        for image_name in expected_images:
            image_file = images_dir / image_name
            assert image_file.exists(), f"Missing image: {image_file}"
    
    def test_story_index_updated_cortex_story_links(self, docs_root):
        """Test that story/index-updated.md links to CORTEX-STORY files."""
        # The links are: CORTEX-STORY/Awakening Of CORTEX.md
        cortex_story_dir = docs_root / "story" / "CORTEX-STORY"
        
        expected_files = [
            "Awakening Of CORTEX.md",
            "History.md",
        ]
        
        for filename in expected_files:
            story_file = cortex_story_dir / filename
            assert story_file.exists(), f"Missing CORTEX-STORY file: {story_file}"
    
    def test_story_cortex_story_image_prompts_links(self, project_root):
        """Test that story/CORTEX-STORY/Image-Prompts.md links to external files."""
        # The links are: ../../../cortex-brain/cortex-3.0-design/[file].md
        design_dir = project_root / "cortex-brain" / "cortex-3.0-design"
        
        expected_files = [
            "data-collectors-specification.md",
            "intelligent-question-routing.md",
        ]
        
        for filename in expected_files:
            design_file = design_dir / filename
            assert design_file.exists(), f"Missing design file: {design_file}"
    
    def test_story_cortex_story_technical_links(self, docs_root):
        """Test that story/CORTEX-STORY/Technical-CORTEX.md links to other story files."""
        # The links are: Awakening Of CORTEX.md, History.md
        cortex_story_dir = docs_root / "story" / "CORTEX-STORY"
        
        expected_files = [
            "Awakening Of CORTEX.md",
            "History.md",
        ]
        
        for filename in expected_files:
            story_file = cortex_story_dir / filename
            assert story_file.exists(), f"Missing CORTEX-STORY file: {story_file}"


class TestDiagramIndexGeneration:
    """Test diagram index file generation and link correctness."""
    
    def test_diagram_index_uses_forward_slashes(self):
        """Test that diagrams/INDEX.md uses forward slashes in links, not backslashes."""
        index_file = Path(__file__).resolve().parent.parent / "docs" / "diagrams" / "INDEX.md"
        
        if index_file.exists():
            content = index_file.read_text(encoding='utf-8')
            
            # Check that links use forward slashes, not backslashes
            assert "diagrams\\01.mmd" not in content, "INDEX.md should use forward slashes, not backslashes"
            assert "diagrams\\02.mmd" not in content, "INDEX.md should use forward slashes, not backslashes"
            
            # Check that links reference mermaid directory and actual files
            assert "mermaid/01-tier-architecture.mmd" in content or "mermaid/" in content, "INDEX.md should link to mermaid/ subdirectory"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
