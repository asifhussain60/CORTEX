"""
Validate documentation links module.

Part of the Documentation Update operation - checks for broken links in documentation.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Any, Set
from urllib.parse import urlparse

from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationResult,
    OperationPhase,
    OperationStatus
)


class ValidateDocLinksModule(BaseOperationModule):
    """
    Validate documentation links.
    
    Scans Markdown documentation files for links and validates:
    - Internal links (references to other docs files)
    - Anchor links (references to headings)
    - Optionally external links (HTTP/HTTPS URLs)
    
    Reports broken or invalid links.
    """
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Get module metadata."""
        return OperationModuleMetadata(
            module_id="validate_doc_links",
            name="Validate Documentation Links",
            description="Check for broken links in documentation",
            phase=OperationPhase.VALIDATION,
            priority=10
        )
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute link validation.
        
        Args:
            context: Operation context
            
        Returns:
            OperationResult with validation status
        """
        try:
            project_root = Path(context.get("project_root", os.getcwd()))
            docs_dir = project_root / "docs"
            
            if not docs_dir.exists():
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message="Documentation directory not found",
                    error=f"docs/ directory does not exist at {docs_dir}"
                )
            
            self.log_info(f"Validating links in {docs_dir}")
            
            # Find all markdown files
            md_files = list(docs_dir.rglob("*.md"))
            self.log_info(f"Found {len(md_files)} documentation files")
            
            # Extract and validate links
            broken_links = []
            total_links = 0
            
            for md_file in md_files:
                file_links = self._extract_links(md_file)
                total_links += len(file_links)
                
                for link in file_links:
                    if not self._validate_link(link, md_file, docs_dir):
                        broken_links.append({
                            "file": str(md_file.relative_to(project_root)),
                            "link": link,
                            "line": self._find_link_line(md_file, link)
                        })
            
            if broken_links:
                self.log_warning(f"Found {len(broken_links)} broken links")
                
                return OperationResult(
                    success=True,  # Success with warnings
                    status=OperationStatus.WARNING,
                    message=f"Validated {total_links} links, found {len(broken_links)} broken",
                    data={
                        "total_links": total_links,
                        "broken_links": broken_links,
                        "files_checked": len(md_files)
                    }
                )
            else:
                self.log_info(f"All {total_links} links are valid")
                
                return OperationResult(
                    success=True,
                    status=OperationStatus.SUCCESS,
                    message=f"Validated {total_links} links, all valid",
                    data={
                        "total_links": total_links,
                        "broken_links": [],
                        "files_checked": len(md_files)
                    }
                )
            
        except Exception as e:
            self.log_error(f"Failed to validate links: {e}")
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message="Link validation failed",
                errors=[str(e)]
            )
    
    def _extract_links(self, md_file: Path) -> List[str]:
        """
        Extract all links from a Markdown file.
        
        Args:
            md_file: Markdown file path
            
        Returns:
            List of links found
        """
        try:
            content = md_file.read_text(encoding="utf-8")
            
            # Match Markdown links: [text](url)
            link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
            matches = re.findall(link_pattern, content)
            
            # Extract URLs
            links = [url for text, url in matches]
            
            return links
            
        except Exception as e:
            self.log_warning(f"Failed to extract links from {md_file}: {e}")
            return []
    
    def _validate_link(self, link: str, source_file: Path, docs_dir: Path) -> bool:
        """
        Validate a single link.
        
        Args:
            link: Link to validate
            source_file: File containing the link
            docs_dir: Documentation root directory
            
        Returns:
            True if link is valid
        """
        # Skip external links (could be added as optional feature)
        if link.startswith(('http://', 'https://', 'mailto:')):
            return True  # Assume external links are valid (can be enhanced)
        
        # Skip anchor-only links (same page)
        if link.startswith('#'):
            # Could validate anchor exists in source file
            return True
        
        # Handle relative links
        if '#' in link:
            # Split file path and anchor
            file_part, anchor = link.split('#', 1)
        else:
            file_part = link
            anchor = None
        
        # Resolve link path relative to source file
        if file_part:
            link_path = (source_file.parent / file_part).resolve()
            
            # Check if file exists
            if not link_path.exists():
                return False
            
            # Validate anchor if present
            if anchor:
                return self._validate_anchor(link_path, anchor)
        
        return True
    
    def _validate_anchor(self, file_path: Path, anchor: str) -> bool:
        """
        Validate that an anchor exists in a file.
        
        Args:
            file_path: File to check
            anchor: Anchor name
            
        Returns:
            True if anchor exists
        """
        try:
            content = file_path.read_text(encoding="utf-8")
            
            # Convert anchor to heading format
            # GitHub-style: lowercase, spaces to hyphens, special chars removed
            heading_pattern = anchor.lower().replace('-', ' ')
            
            # Look for heading in content
            for line in content.split('\n'):
                if line.startswith('#'):
                    heading_text = line.lstrip('#').strip().lower()
                    if heading_pattern in heading_text or heading_text in heading_pattern:
                        return True
            
            return False
            
        except Exception:
            return False
    
    def _find_link_line(self, md_file: Path, link: str) -> int:
        """
        Find line number where link appears.
        
        Args:
            md_file: Markdown file
            link: Link to find
            
        Returns:
            Line number (1-indexed)
        """
        try:
            with open(md_file, 'r', encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    if link in line:
                        return line_num
        except Exception:
            pass
        
        return 0


def register() -> BaseOperationModule:
    """Register module for discovery."""
    return ValidateDocLinksModule()
