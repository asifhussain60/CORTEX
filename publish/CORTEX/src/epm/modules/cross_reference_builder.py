"""
CORTEX EPM - Cross-Reference Builder Module
Builds internal link index and updates navigation structure

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from pathlib import Path
from typing import Dict, List, Set
import re
import logging
import yaml

logger = logging.getLogger(__name__)

# Register constructor to handle Python tags in YAML (like in mkdocs.yml)
yaml.SafeLoader.add_multi_constructor('tag:yaml.org,2002:python/', 
                                      lambda loader, suffix, node: None)


class CrossReferenceBuilder:
    """Builds cross-reference index and navigation structure"""
    
    def __init__(self, root_path: Path, dry_run: bool = False):
        self.root_path = root_path
        self.docs_path = root_path / "docs"
        self.dry_run = dry_run
        
        # Internal link patterns
        self.link_pattern = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)')
        self.heading_pattern = re.compile(r'^#{1,6}\s+(.+)$', re.MULTILINE)
    
    def build_cross_references(self) -> Dict:
        """
        Build complete cross-reference index
        
        Returns:
            Dictionary with cross-reference statistics
        """
        # Scan all markdown files
        all_pages = self._scan_all_pages()
        
        # Build link index
        link_index = self._build_link_index(all_pages)
        
        # Detect broken links
        broken_links = self._detect_broken_links(link_index, all_pages)
        
        # Build heading index
        heading_index = self._build_heading_index(all_pages)
        
        # Generate navigation structure
        nav_structure = self._generate_navigation(all_pages, heading_index)
        
        # Update mkdocs.yml navigation
        if not self.dry_run:
            self._update_mkdocs_nav(nav_structure)
        
        return {
            "total_pages": len(all_pages),
            "total_links": len(link_index),
            "broken_links": len(broken_links),
            "total_headings": sum(len(h) for h in heading_index.values()),
            "navigation_entries": len(nav_structure)
        }
    
    def _scan_all_pages(self) -> List[Path]:
        """Scan docs/ for all markdown files"""
        pages = []
        
        for md_file in self.docs_path.rglob("*.md"):
            pages.append(md_file)
        
        logger.info(f"Found {len(pages)} markdown pages")
        return pages
    
    def _build_link_index(self, pages: List[Path]) -> Dict[str, List[Dict]]:
        """Build index of all internal links"""
        link_index = {}
        
        for page in pages:
            with open(page, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all markdown links
            links = self.link_pattern.findall(content)
            
            page_key = str(page.relative_to(self.docs_path))
            link_index[page_key] = []
            
            for link_text, link_url in links:
                # Skip external links
                if link_url.startswith('http://') or link_url.startswith('https://'):
                    continue
                
                link_index[page_key].append({
                    "text": link_text,
                    "url": link_url,
                    "type": "internal"
                })
        
        return link_index
    
    def _detect_broken_links(self, link_index: Dict, pages: List[Path]) -> List[Dict]:
        """Detect broken internal links"""
        broken_links = []
        
        # Build set of valid paths
        valid_paths = set(str(p.relative_to(self.docs_path)) for p in pages)
        
        for page_key, links in link_index.items():
            for link in links:
                link_url = link['url']
                
                # Remove anchor if present
                if '#' in link_url:
                    link_url = link_url.split('#')[0]
                
                # Skip empty links (anchor-only)
                if not link_url:
                    continue
                
                # Resolve relative path
                page_path = self.docs_path / Path(page_key).parent
                target_path = (page_path / link_url).resolve()
                
                # Check if target is within docs_path
                try:
                    target_relative = str(target_path.relative_to(self.docs_path))
                except ValueError:
                    # Path is outside docs/, skip validation
                    continue
                
                if target_relative not in valid_paths:
                    broken_links.append({
                        "source": page_key,
                        "link_text": link['text'],
                        "link_url": link['url'],
                        "target": target_relative
                    })
                    logger.warning(f"Broken link in {page_key}: {link['url']}")
        
        return broken_links
    
    def _build_heading_index(self, pages: List[Path]) -> Dict[str, List[Dict]]:
        """Build index of all headings in pages"""
        heading_index = {}
        
        for page in pages:
            with open(page, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all headings
            headings = []
            for match in self.heading_pattern.finditer(content):
                heading_text = match.group(1).strip()
                heading_level = match.group(0).count('#')
                
                # Generate anchor ID
                anchor = heading_text.lower()
                anchor = re.sub(r'[^\w\s-]', '', anchor)
                anchor = re.sub(r'[\s_]+', '-', anchor)
                
                headings.append({
                    "text": heading_text,
                    "level": heading_level,
                    "anchor": anchor
                })
            
            page_key = str(page.relative_to(self.docs_path))
            heading_index[page_key] = headings
        
        return heading_index
    
    def _generate_navigation(self, pages: List[Path], heading_index: Dict) -> List[Dict]:
        """Generate hierarchical navigation structure"""
        nav_structure = []
        
        # Group pages by directory
        by_directory = {}
        for page in pages:
            dir_name = page.parent.name if page.parent != self.docs_path else "root"
            
            if dir_name not in by_directory:
                by_directory[dir_name] = []
            
            by_directory[dir_name].append(page)
        
        # Build navigation hierarchy
        for dir_name, dir_pages in sorted(by_directory.items()):
            if dir_name == "root":
                # Add root pages directly
                for page in sorted(dir_pages):
                    nav_structure.append({
                        "title": page.stem.replace('-', ' ').title(),
                        "path": str(page.relative_to(self.docs_path))
                    })
            else:
                # Create section
                section = {
                    "title": dir_name.replace('-', ' ').title(),
                    "pages": []
                }
                
                for page in sorted(dir_pages):
                    section["pages"].append({
                        "title": page.stem.replace('-', ' ').title(),
                        "path": str(page.relative_to(self.docs_path))
                    })
                
                nav_structure.append(section)
        
        return nav_structure
    
    def _update_mkdocs_nav(self, nav_structure: List[Dict]):
        """Update mkdocs.yml with generated navigation"""
        mkdocs_file = self.root_path / "mkdocs.yml"
        
        if not mkdocs_file.exists():
            logger.warning("mkdocs.yml not found, skipping navigation update")
            return
        
        # Load existing config
        with open(mkdocs_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Update navigation
        config['nav'] = self._convert_nav_to_mkdocs_format(nav_structure)
        
        # Write back
        with open(mkdocs_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        
        logger.info("✓ Updated mkdocs.yml navigation")
    
    def _convert_nav_to_mkdocs_format(self, nav_structure: List[Dict]) -> List:
        """Convert navigation structure to MkDocs format"""
        mkdocs_nav = []
        
        for item in nav_structure:
            if "pages" in item:
                # Section with sub-pages
                section_dict = {}
                section_dict[item["title"]] = []
                
                for page in item["pages"]:
                    section_dict[item["title"]].append({
                        page["title"]: page["path"]
                    })
                
                mkdocs_nav.append(section_dict)
            else:
                # Single page
                mkdocs_nav.append({
                    item["title"]: item["path"]
                })
        
        return mkdocs_nav
