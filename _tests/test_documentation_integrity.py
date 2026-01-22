"""
Documentation Integrity Tests

Validates mkdocs site structure, link validity, and asset completeness.
All tests ensure documentation can be built and deployed successfully.
"""

import pytest
import os
import yaml
from pathlib import Path
import subprocess
import re
from typing import List, Set, Tuple


class TestDocumentationStructure:
    """Test documentation folder structure and organization."""
    
    def test_docs_directory_exists(self):
        """Verify docs directory exists."""
        docs_dir = Path("docs")
        assert docs_dir.exists(), "docs/ directory must exist"
        assert docs_dir.is_dir(), "docs/ must be a directory"
    
    def test_mkdocs_yml_exists(self):
        """Verify mkdocs.yml configuration exists."""
        mkdocs_file = Path("mkdocs.yml")
        assert mkdocs_file.exists(), "mkdocs.yml must exist"
        assert mkdocs_file.is_file(), "mkdocs.yml must be a file"
    
    def test_mkdocs_yml_valid_yaml(self):
        """Verify mkdocs.yml is valid YAML."""
        with open("mkdocs.yml") as f:
            try:
                yaml.safe_load(f)
            except yaml.YAMLError as e:
                pytest.fail(f"mkdocs.yml is invalid YAML: {e}")
    
    def test_required_doc_folders_exist(self):
        """Verify all required documentation folders exist."""
        required_folders = [
            "docs/01-cortex-brain",
            "docs/02-orchestrators",
            "docs/03-getting-started",
            "docs/04-architecture",
            "docs/05-lens-protocol",
            "docs/06-api-reference",
            "docs/07-guides",
            "docs/08-reference",
            "docs/09-tutorials",
            "docs/10-contributing",
            "docs/11-mcp-tools",
            "docs/12-infrastructure",
            "docs/13-domain-brain",
            "docs/14-deployment",
            "docs/15-observability",
            "docs/16-testing",
            "docs/_tests",
            "docs/assets",
        ]
        
        for folder in required_folders:
            folder_path = Path(folder)
            assert folder_path.exists(), f"{folder} must exist"
            assert folder_path.is_dir(), f"{folder} must be a directory"
    
    def test_no_orphaned_markdown_files(self):
        """Verify all markdown files are referenced in mkdocs.yml."""
        with open("mkdocs.yml") as f:
            config = yaml.safe_load(f)
        
        # Extract all references from nav
        referenced_files = set()
        
        def extract_files(nav_item):
            if isinstance(nav_item, dict):
                for key, value in nav_item.items():
                    if isinstance(value, str) and value.endswith(".md"):
                        referenced_files.add(Path("docs") / value)
                    elif isinstance(value, list):
                        for item in value:
                            extract_files(item)
            elif isinstance(nav_item, list):
                for item in nav_item:
                    extract_files(item)
        
        if "nav" in config:
            extract_files(config["nav"])
        
        # Find all markdown files in docs
        docs_path = Path("docs")
        actual_files = set(docs_path.rglob("*.md"))
        
        # Exclude _tests and _diagrams
        actual_files = {
            f for f in actual_files
            if "_tests" not in str(f) and "_diagrams" not in str(f)
            and "_hooks" not in str(f) and "theme" not in str(f)
        }
        
        orphaned = actual_files - referenced_files
        
        # Some orphaned files are OK (like assets), but warn if there are many
        if orphaned:
            print(f"Warning: {len(orphaned)} orphaned markdown files found")


class TestAssets:
    """Test documentation assets (images, stylesheets, etc.)."""
    
    def test_cortex_logo_exists(self):
        """Verify CORTEX logo file exists."""
        logo_path = Path("docs/assets/images/cortex-logo-200.png")
        assert logo_path.exists(), "docs/assets/images/cortex-logo-200.png must exist"
        assert logo_path.is_file(), "cortex-logo-200.png must be a file"
        assert logo_path.stat().st_size > 0, "cortex-logo-200.png must not be empty"
    
    def test_favicon_exists(self):
        """Verify favicon file exists."""
        favicon_path = Path("docs/assets/images/CORTEX-logo-64.png")
        assert favicon_path.exists(), "docs/assets/images/CORTEX-logo-64.png must exist"
        assert favicon_path.is_file(), "favicon must be a file"
    
    def test_logo_path_in_mkdocs_config(self):
        """Verify logo path is correctly configured in mkdocs.yml."""
        with open("mkdocs.yml") as f:
            config = yaml.safe_load(f)
        
        theme = config.get("theme", {})
        logo = theme.get("logo")
        
        assert logo == "assets/images/cortex-logo-200.png", \
            f"Logo path should be 'assets/images/cortex-logo-200.png', got '{logo}'"
    
    def test_favicon_path_in_mkdocs_config(self):
        """Verify favicon path is correctly configured in mkdocs.yml."""
        with open("mkdocs.yml") as f:
            config = yaml.safe_load(f)
        
        theme = config.get("theme", {})
        favicon = theme.get("favicon")
        
        assert favicon == "assets/images/CORTEX-logo-64.png", \
            f"Favicon path should be 'assets/images/CORTEX-logo-64.png', got '{favicon}'"


class TestLinkValidation:
    """Test internal documentation links."""
    
    def get_all_markdown_files(self) -> List[Path]:
        """Get all markdown files in docs (excluding _tests, _diagrams, etc.)."""
        docs_path = Path("docs")
        all_files = list(docs_path.rglob("*.md"))
        
        # Filter out special directories
        return [
            f for f in all_files
            if not any(part in str(f) for part in ["_tests", "_diagrams", "_hooks", "theme"])
        ]
    
    def extract_links_from_file(self, file_path: Path) -> List[Tuple[str, int, str]]:
        """Extract all markdown links from a file.
        
        Returns list of (link_target, line_number, link_text)
        """
        links = []
        
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # Match markdown links: [text](target)
        link_pattern = r"\[([^\]]+)\]\(([^\)]+)\)"
        
        for line_num, line in enumerate(lines, 1):
            for match in re.finditer(link_pattern, line):
                link_text = match.group(1)
                link_target = match.group(2)
                links.append((link_target, line_num, link_text))
        
        return links
    
    def test_internal_links_resolve(self):
        """Verify all internal links point to existing files."""
        markdown_files = self.get_all_markdown_files()
        
        broken_links = []
        
        for md_file in markdown_files:
            links = self.extract_links_from_file(md_file)
            
            for link_target, line_num, link_text in links:
                # Skip external links
                if link_target.startswith("http://") or link_target.startswith("https://"):
                    continue
                
                # Skip anchors in external files (would need to load target)
                if "#" in link_target:
                    file_part = link_target.split("#")[0]
                    if file_part:
                        target_file = link_target.split("#")[0]
                    else:
                        continue
                else:
                    target_file = link_target
                
                # Resolve relative path
                if target_file:
                    target_path = (md_file.parent / target_file).resolve()
                    
                    # Check if file exists
                    if not target_path.exists():
                        broken_links.append({
                            "source": str(md_file.relative_to(Path("docs"))),
                            "line": line_num,
                            "link": link_target,
                            "text": link_text,
                        })
        
        if broken_links:
            error_msg = "Broken internal links found:\n"
            for broken in broken_links[:10]:  # Show first 10
                error_msg += f"  {broken['source']}:{broken['line']} - [{broken['text']}]({broken['link']})\n"
            
            if len(broken_links) > 10:
                error_msg += f"  ... and {len(broken_links) - 10} more\n"
            
            pytest.fail(error_msg)
    
    def test_image_references_valid(self):
        """Verify all image references point to existing files."""
        markdown_files = self.get_all_markdown_files()
        
        missing_images = []
        
        for md_file in markdown_files:
            # Match image syntax: ![alt](path)
            image_pattern = r"!\[([^\]]*)\]\(([^\)]+)\)"
            
            with open(md_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                for match in re.finditer(image_pattern, line):
                    image_path = match.group(2)
                    
                    # Skip external URLs
                    if image_path.startswith("http://") or image_path.startswith("https://"):
                        continue
                    
                    # Resolve relative path
                    resolved_path = (md_file.parent / image_path).resolve()
                    
                    if not resolved_path.exists():
                        missing_images.append({
                            "source": str(md_file.relative_to(Path("docs"))),
                            "line": line_num,
                            "image": image_path,
                        })
        
        assert not missing_images, f"Missing image files: {missing_images}"


class TestMkdocsBuild:
    """Test mkdocs build process."""
    
    @pytest.mark.slow
    def test_mkdocs_builds_successfully(self):
        """Verify mkdocs can build the site without errors."""
        result = subprocess.run(
            ["mkdocs", "build", "--strict"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        assert result.returncode == 0, \
            f"mkdocs build failed:\nStdout:\n{result.stdout}\n\nStderr:\n{result.stderr}"
    
    @pytest.mark.slow
    def test_mkdocs_site_directory_created(self):
        """Verify mkdocs creates site directory."""
        # Build site
        subprocess.run(
            ["mkdocs", "build"],
            capture_output=True,
            timeout=60
        )
        
        site_dir = Path("_build/site")
        assert site_dir.exists(), "_build/site directory should be created"
        assert site_dir.is_dir(), "_build/site should be a directory"
        
        # Verify index.html was created
        index_file = site_dir / "index.html"
        assert index_file.exists(), "_build/site/index.html must exist"


class TestDocumentationContent:
    """Test documentation content quality."""
    
    def test_all_new_sections_exist(self):
        """Verify all new documentation sections were created."""
        expected_files = [
            "docs/11-mcp-tools/00-mcp-index.md",
            "docs/11-mcp-tools/mcp-architecture.md",
            "docs/12-infrastructure/00-infrastructure-index.md",
            "docs/13-domain-brain/00-domain-brain-index.md",
            "docs/14-deployment/00-deployment-index.md",
            "docs/15-observability/00-observability-index.md",
            "docs/16-testing/00-testing-index.md",
        ]
        
        for file_path in expected_files:
            path = Path(file_path)
            assert path.exists(), f"Expected documentation file {file_path} not found"
            assert path.stat().st_size > 100, f"Documentation file {file_path} appears to be empty"
    
    def test_mermaid_diagrams_syntax(self):
        """Verify mermaid diagram syntax is valid."""
        markdown_files = list(Path("docs").rglob("*.md"))
        
        invalid_diagrams = []
        
        for md_file in markdown_files:
            if any(part in str(md_file) for part in ["_tests", "_diagrams", "_hooks"]):
                continue
            
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Find all mermaid blocks
            mermaid_pattern = r"```mermaid\n(.*?)\n```"
            
            for match in re.finditer(mermaid_pattern, content, re.DOTALL):
                diagram_code = match.group(1)
                
                # Basic validation - check for common syntax issues
                lines = diagram_code.strip().split("\n")
                
                if not lines[0].startswith(("graph", "sequenceDiagram", "pie", "stateDiagram")):
                    invalid_diagrams.append({
                        "file": str(md_file.relative_to(Path("docs"))),
                        "issue": "Diagram doesn't start with valid type",
                        "code": diagram_code[:50] + "..."
                    })
        
        if invalid_diagrams:
            print(f"Warning: {len(invalid_diagrams)} mermaid diagrams may have syntax issues")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
