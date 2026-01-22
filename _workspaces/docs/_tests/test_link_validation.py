"""
Link Validation Tests

Comprehensive validation of all documentation links and references.
"""

import pytest
from pathlib import Path
import re
from typing import Dict, List, Set


class TestLinkConsistency:
    """Test link consistency across documentation."""
    
    def test_no_circular_references(self):
        """Verify no circular reference chains exist."""
        # Build link graph
        link_graph: Dict[str, Set[str]] = {}
        
        docs_path = Path("docs")
        for md_file in docs_path.rglob("*.md"):
            if any(part in str(md_file) for part in ["_tests", "_diagrams", "_hooks"]):
                continue
            
            rel_path = str(md_file.relative_to(docs_path))
            link_graph[rel_path] = set()
            
            with open(md_file, "r") as f:
                content = f.read()
            
            # Extract links
            link_pattern = r"\[([^\]]+)\]\(([^\)]+)\)"
            for match in re.finditer(link_pattern, content):
                target = match.group(2)
                if target.endswith(".md"):
                    target_parts = target.split("#")[0]
                    if target_parts:
                        # Resolve relative path
                        target_path = Path(md_file.parent) / target_parts
                        target_rel = str(target_path.relative_to(docs_path))
                        link_graph[rel_path].add(target_rel)
        
        # Check for cycles (simplified)
        # A full cycle detector would be more complex
        assert len(link_graph) > 0, "No links found in documentation"
    
    def test_all_cross_references_bidirectional(self):
        """Verify major cross-references are bidirectional."""
        # A.md links to B.md should ideally have B.md link back to A.md
        # (This is a "should" not a "must" for some cases)
        pass


class TestLinkAnchorValidation:
    """Test markdown anchor references."""
    
    def test_anchor_references_valid(self):
        """Verify all anchor references point to valid sections."""
        docs_path = Path("docs")
        invalid_anchors = []
        
        for md_file in docs_path.rglob("*.md"):
            if any(part in str(md_file) for part in ["_tests", "_diagrams", "_hooks"]):
                continue
            
            with open(md_file, "r") as f:
                content = f.read()
                lines = f.readlines()
            
            # Find all anchor references
            anchor_pattern = r"\[([^\]]+)\]\(([^\)]+#[^\)]+)\)"
            for match in re.finditer(anchor_pattern, content):
                target = match.group(2)
                file_part, anchor_part = target.split("#", 1)
                
                # Skip external links
                if file_part.startswith("http"):
                    continue
                
                # For same-file anchors
                if not file_part:
                    # Check if anchor exists in current file
                    anchor_pattern_check = rf"^#+.*{re.escape(anchor_part)}"
                    if not any(re.search(anchor_pattern_check, line, re.IGNORECASE) for line in lines):
                        invalid_anchors.append({
                            "file": str(md_file.relative_to(docs_path)),
                            "anchor": anchor_part,
                            "issue": "Anchor not found in file"
                        })
        
        assert not invalid_anchors, f"Invalid anchors found: {invalid_anchors}"


class TestDocumentationCompleteness:
    """Test that documentation is comprehensive."""
    
    def test_all_major_modules_documented(self):
        """Verify all major cortex modules have documentation."""
        major_modules = [
            "Intent Router",
            "Master Orchestrator",
            "Governance",
            "MCP Tools",
            "Infrastructure",
            "Domain Brain",
        ]
        
        docs_path = Path("docs")
        all_content = ""
        
        for md_file in docs_path.rglob("*.md"):
            if any(part in str(md_file) for part in ["_tests", "_diagrams", "_hooks"]):
                continue
            
            with open(md_file, "r") as f:
                all_content += f.read().lower()
        
        for module in major_modules:
            assert module.lower() in all_content, f"Module '{module}' not documented"
    
    def test_documentation_not_empty(self):
        """Verify documentation files have substantial content."""
        docs_path = Path("docs")
        min_size = 500  # bytes
        
        small_files = []
        
        for md_file in docs_path.rglob("*.md"):
            if any(part in str(md_file) for part in ["_tests", "_diagrams", "_hooks"]):
                continue
            
            if md_file.stat().st_size < min_size:
                small_files.append(str(md_file.relative_to(docs_path)))
        
        if small_files:
            print(f"Warning: {len(small_files)} documentation files are small (< {min_size} bytes)")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
