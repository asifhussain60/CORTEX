"""
Test Executive Summary Integration with MkDocs

Verifies that the Executive Summary Generator produces output
in the format similar to EXECUTIVE-SUMMARY.md and is picked up by MkDocs.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import sys
from pathlib import Path

# Add cortex-brain admin documentation to path
sys.path.insert(0, str(Path(__file__).parent.parent / "cortex-brain" / "admin" / "documentation"))

import pytest
from generators.executive_summary_generator import ExecutiveSummaryGenerator
from generators.base_generator import GenerationConfig, GeneratorType, GenerationProfile


def test_executive_summary_generation():
    """Test that executive summary generator creates expected file"""
    workspace_root = Path(__file__).parent.parent
    docs_path = workspace_root / "docs"
    
    config = GenerationConfig(
        generator_type=GeneratorType.EXECUTIVE_SUMMARY,
        profile=GenerationProfile.STANDARD,
        output_path=docs_path
    )
    
    generator = ExecutiveSummaryGenerator(config, workspace_root)
    result = generator.generate()
    
    assert result.success, f"Generation failed: {result.errors}"
    assert len(result.files_generated) > 0, "No files generated"
    
    # Verify the file was created
    exec_summary = docs_path / "EXECUTIVE-SUMMARY.md"
    assert exec_summary.exists(), "EXECUTIVE-SUMMARY.md not found"
    
    # Verify content structure
    content = exec_summary.read_text(encoding='utf-8')
    
    required_sections = [
        "# CORTEX Executive Summary",
        "## Overview",
        "## Key Metrics",
        "## Core Features",
        "## Architecture Highlights",
        "## Intelligent Safety & Risk Mitigation",
        "## Performance",
        "## Documentation",
        "## Status"
    ]
    
    for section in required_sections:
        assert section in content, f"Missing section: {section}"
    
    # Verify key metrics are present
    assert "Token Reduction:" in content
    assert "Cost Reduction:" in content
    assert "Agent Count:" in content
    assert "Memory Tiers:" in content
    
    # Verify safety features are documented
    assert "Auto .gitignore Management" in content
    assert "Automatic Checkpoints" in content
    assert "Local Backups" in content
    assert "Brain Protection Rules" in content
    
    # Verify performance metrics
    assert "Setup Time:" in content
    assert "Response Time:" in content


def test_executive_summary_format_matches_original():
    """Test that generated content matches the format of original EXECUTIVE-SUMMARY.md"""
    workspace_root = Path(__file__).parent.parent
    docs_path = workspace_root / "docs"
    exec_summary = docs_path / "EXECUTIVE-SUMMARY.md"
    
    if not exec_summary.exists():
        pytest.skip("EXECUTIVE-SUMMARY.md not generated yet")
    
    content = exec_summary.read_text(encoding='utf-8')
    
    # Check header format
    assert content.startswith("# CORTEX Executive Summary"), "Wrong header format"
    assert "**Version:**" in content[:200], "Version not in header"
    assert "**Last Updated:**" in content[:200], "Last Updated not in header"
    assert "**Status:**" in content[:200], "Status not in header"
    
    # Check feature list format (numbered list with "(feature)" suffix)
    assert "1. **" in content, "Features not formatted as numbered list"
    assert "(feature)" in content, "Feature entries don't have (feature) suffix"
    
    # Check architecture sections
    assert "### Memory System (Tier 0-3)" in content
    assert "### Agent System" in content
    assert "### Protection & Governance" in content
    
    # Check footer
    assert "**Author:**" in content
    assert "**Copyright:**" in content
    assert "**License:**" in content
    assert "**Repository:**" in content


def test_mkdocs_navigation_includes_executive_summary():
    """Test that mkdocs.yml includes executive summary in navigation"""
    workspace_root = Path(__file__).parent.parent
    mkdocs_config = workspace_root / "mkdocs.yml"
    
    assert mkdocs_config.exists(), "mkdocs.yml not found"
    
    content = mkdocs_config.read_text(encoding='utf-8')
    
    # Verify executive summary is in navigation
    assert "Executive Summary: EXECUTIVE-SUMMARY.md" in content, \
        "Executive Summary not in mkdocs.yml navigation"
    
    # Verify it's under Technical Docs section
    technical_docs_section = False
    for line in content.split('\n'):
        if "Technical Docs:" in line:
            technical_docs_section = True
        if technical_docs_section and "Executive Summary" in line:
            # Found it in the right section
            return
    
    pytest.fail("Executive Summary not found in Technical Docs section")


def test_mkdocs_build_includes_executive_summary():
    """Test that mkdocs build generates the executive summary page"""
    import subprocess
    
    workspace_root = Path(__file__).parent.parent
    site_dir = workspace_root / "site"
    exec_summary_page = site_dir / "EXECUTIVE-SUMMARY" / "index.html"
    
    # Build MkDocs (clean build to ensure fresh output)
    result = subprocess.run(
        ["mkdocs", "build", "--clean"],
        cwd=workspace_root,
        capture_output=True,
        text=True,
        timeout=60
    )
    
    assert result.returncode == 0, f"MkDocs build failed: {result.stderr}"
    
    # Verify the page was generated
    assert exec_summary_page.exists(), \
        "Executive summary page not generated in site/"
    
    # Verify the page contains expected content
    page_content = exec_summary_page.read_text(encoding='utf-8')
    
    assert "CORTEX Executive Summary" in page_content, \
        "Page doesn't contain executive summary title"
    assert "Token Reduction" in page_content, \
        "Page doesn't contain key metrics"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
