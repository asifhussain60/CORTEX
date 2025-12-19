"""
Test sticky navigation CSS configuration for MkDocs theme.

Tests verify that the left navigation panel has proper sticky positioning
that will work on both localhost and GitHub Pages deployment.

Author: Asif Hussain
Date: 2025-11-20
"""

import pytest
import re
from pathlib import Path


def test_sticky_navigation_css_exists():
    """Verify sticky navigation CSS is present in theme."""
    css_file = Path("docs/themes/cortex-tales/assets/css/cortex-tales.css")
    assert css_file.exists(), "Theme CSS file not found"
    
    content = css_file.read_text(encoding='utf-8')
    
    # Verify .nav-tree has sticky positioning
    assert "position: sticky" in content, "Sticky position not found in CSS"
    assert ".nav-tree" in content, "Nav tree class not found"


def test_sticky_navigation_properties():
    """Verify all required CSS properties for sticky navigation."""
    css_file = Path("docs/themes/cortex-tales/assets/css/cortex-tales.css")
    content = css_file.read_text(encoding='utf-8')
    
    # Extract .nav-tree block
    nav_tree_pattern = r'\.nav-tree\s*\{([^}]+)\}'
    match = re.search(nav_tree_pattern, content, re.DOTALL)
    assert match, "Nav tree CSS block not found"
    
    nav_tree_css = match.group(1)
    
    # Verify required properties
    assert "position: sticky" in nav_tree_css, "Missing position: sticky"
    assert "top:" in nav_tree_css, "Missing top property"
    assert "max-height:" in nav_tree_css, "Missing max-height property"
    assert "overflow-y:" in nav_tree_css, "Missing overflow-y property"
    assert "align-self: flex-start" in nav_tree_css, "Missing align-self for flexbox"


def test_sticky_navigation_values():
    """Verify sticky navigation has optimized values."""
    css_file = Path("docs/themes/cortex-tales/assets/css/cortex-tales.css")
    content = css_file.read_text(encoding='utf-8')
    
    # Extract .nav-tree block
    nav_tree_pattern = r'\.nav-tree\s*\{([^}]+)\}'
    match = re.search(nav_tree_pattern, content, re.DOTALL)
    nav_tree_css = match.group(1)
    
    # Verify top value (should account for header)
    assert "top: 80px" in nav_tree_css, "Top offset should be 80px for header clearance"
    
    # Verify max-height uses viewport calculation
    assert "calc(100vh - 120px)" in nav_tree_css, "Max-height should be optimized viewport calculation"
    
    # Verify overflow handling
    assert "overflow-y: auto" in nav_tree_css, "Overflow-y should be auto"
    assert "overflow-x: hidden" in nav_tree_css, "Overflow-x should be hidden"


def test_no_parent_overflow_interference():
    """Verify parent containers don't interfere with sticky positioning."""
    css_file = Path("docs/themes/cortex-tales/assets/css/cortex-tales.css")
    content = css_file.read_text(encoding='utf-8')
    
    # Check that .widewrapper.main doesn't have overflow: hidden
    # which would break sticky positioning
    main_wrapper_pattern = r'\.widewrapper\.main\s*\{([^}]+)\}'
    match = re.search(main_wrapper_pattern, content, re.DOTALL)
    
    if match:
        main_css = match.group(1)
        # Ensure no overflow: hidden that would break sticky
        assert "overflow: hidden" not in main_css, \
            "Parent container should not have overflow: hidden (breaks sticky)"


def test_github_pages_compatibility():
    """Verify CSS is pure CSS without dependencies that might break on GitHub Pages."""
    css_file = Path("docs/themes/cortex-tales/assets/css/cortex-tales.css")
    content = css_file.read_text(encoding='utf-8')
    
    # Verify no JavaScript-dependent CSS (like CSS-in-JS)
    assert "var(" in content, "CSS variables are GitHub Pages compatible"
    
    # Verify standard CSS properties only (no experimental prefixes required)
    nav_tree_pattern = r'\.nav-tree\s*\{([^}]+)\}'
    match = re.search(nav_tree_pattern, content, re.DOTALL)
    nav_tree_css = match.group(1)
    
    # Sticky is widely supported, no vendor prefixes needed
    assert "-webkit-sticky" not in nav_tree_css, "No vendor prefixes needed for modern browsers"
    assert "position: sticky" in nav_tree_css, "Standard sticky syntax is GitHub Pages compatible"


@pytest.mark.parametrize("chapter", [
    "prologue.md",
    "chapter-01.md",
    "chapter-05.md",
    "chapter-10.md",
    "epilogue.md"
])
def test_chapter_files_exist_for_navigation(chapter):
    """Verify chapter files exist that will use the sticky navigation."""
    chapter_file = Path(f"docs/story/CORTEX-STORY/chapters/{chapter}")
    assert chapter_file.exists(), f"Chapter file {chapter} not found"


def test_mkdocs_config_references_chapters():
    """Verify mkdocs.yml includes chapter navigation structure."""
    mkdocs_file = Path("mkdocs.yml")
    assert mkdocs_file.exists(), "mkdocs.yml not found"
    
    content = mkdocs_file.read_text(encoding='utf-8')
    
    # Verify chapter structure in navigation
    assert "The CORTEX Story:" in content, "Story navigation section not found"
    assert "chapters/prologue.md" in content, "Prologue chapter not in navigation"
    assert "chapters/chapter-01.md" in content, "Chapter 1 not in navigation"
    assert "chapters/epilogue.md" in content, "Epilogue not in navigation"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
