#!/usr/bin/env python3
"""
CORTEX Documentation Link Analysis Tool
Recursively analyzes all HTML files in docs/ to map link structure
"""

import os
import json
import re
from pathlib import Path
from html.parser import HTMLParser
from typing import Dict, List, Set, Tuple
from urllib.parse import urljoin, urlparse

class LinkExtractor(HTMLParser):
    """Extract href and src attributes from HTML"""
    def __init__(self):
        super().__init__()
        self.links = []
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'a' and 'href' in attrs_dict:
            self.links.append(('href', attrs_dict['href']))
        elif tag in ['img', 'script'] and 'src' in attrs_dict:
            self.links.append(('src', attrs_dict['src']))
        elif tag == 'link' and 'href' in attrs_dict:
            self.links.append(('link', attrs_dict['href']))

def normalize_path(base_file: Path, link: str, docs_root: Path) -> str:
    """Normalize a link path relative to docs root"""
    # Skip external URLs, anchors, and special protocols
    if any([
        link.startswith(('http://', 'https://', '//', 'mailto:', 'tel:', 'javascript:')),
        link.startswith('#'),
        not link.strip()
    ]):
        return None
    
    # Remove query string and fragment
    link = link.split('?')[0].split('#')[0]
    if not link:
        return None
    
    # Handle absolute paths from root
    if link.startswith('/'):
        # Assume it's relative to docs root
        link = link.lstrip('/')
        target_path = docs_root / link
    else:
        # Relative to current file's directory
        base_dir = base_file.parent
        target_path = (base_dir / link).resolve()
    
    # Get path relative to docs root
    try:
        rel_path = target_path.relative_to(docs_root)
        return str(rel_path).replace('\\', '/')
    except ValueError:
        # Path is outside docs root
        return None

def analyze_html_file(file_path: Path, docs_root: Path) -> List[str]:
    """Extract all local file links from an HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        parser = LinkExtractor()
        parser.feed(content)
        
        normalized_links = []
        for link_type, link in parser.links:
            normalized = normalize_path(file_path, link, docs_root)
            if normalized:
                normalized_links.append(normalized)
        
        return normalized_links
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []

def build_link_map(docs_root: Path) -> Dict:
    """Build complete map of all links in documentation"""
    
    # Find all HTML files
    html_files = list(docs_root.rglob('*.html'))
    
    # Build link graph
    link_graph = {}  # file -> [files it links to]
    all_linked_files = set()
    
    for html_file in html_files:
        rel_path = str(html_file.relative_to(docs_root)).replace('\\', '/')
        links = analyze_html_file(html_file, docs_root)
        link_graph[rel_path] = links
        all_linked_files.update(links)
    
    # Get all files in docs
    all_files = set()
    for file_path in docs_root.rglob('*'):
        if file_path.is_file():
            rel_path = str(file_path.relative_to(docs_root)).replace('\\', '/')
            all_files.add(rel_path)
    
    # Get root-level files only
    root_files = [f for f in all_files if '/' not in f]
    root_files_linked = [f for f in root_files if f in all_linked_files]
    root_files_unlinked = [f for f in root_files if f not in all_linked_files]
    
    # Build reverse link map (which files link TO each file)
    reverse_links = {}
    for source, targets in link_graph.items():
        for target in targets:
            if target not in reverse_links:
                reverse_links[target] = []
            reverse_links[target].append(source)
    
    # Analyze link tree from index.html
    def build_tree(file: str, visited: Set[str] = None, depth: int = 0) -> Dict:
        if visited is None:
            visited = set()
        
        if file in visited or depth > 10:  # Prevent infinite loops
            return {"file": file, "circular": True}
        
        visited.add(file)
        
        children = []
        if file in link_graph:
            for child in sorted(set(link_graph[file])):
                # Only include HTML files in tree for clarity
                if child.endswith('.html'):
                    children.append(build_tree(child, visited.copy(), depth + 1))
        
        return {
            "file": file,
            "children": children,
            "link_count": len(link_graph.get(file, []))
        }
    
    link_tree = build_tree('index.html')
    
    # Suggest moves for unlinked root files
    suggested_moves = []
    for unlinked in root_files_unlinked:
        # Skip special files
        if unlinked.startswith('.') or unlinked in ['README.md', '404.md', 'DEPLOYMENT.md', 'QUICK-LAUNCH.md']:
            continue
        
        # Suggest folder based on filename
        suggestions = {
            'test': 'testing/',
            'demo': 'prototypes/',
            'diagnostic': 'development/',
            'sitemap': 'assets/',
            'faq': 'getting-started/'
        }
        
        target = None
        for keyword, folder in suggestions.items():
            if keyword in unlinked.lower():
                target = folder + unlinked
                break
        
        if not target:
            target = 'development/' + unlinked
        
        suggested_moves.append({
            'current': unlinked,
            'suggested': target,
            'reason': 'Unlinked root-level file'
        })
    
    # Calculate statistics
    html_files_count = len([f for f in all_files if f.endswith('.html')])
    linked_html_count = len([f for f in all_linked_files if f.endswith('.html')])
    
    return {
        'statistics': {
            'total_files': len(all_files),
            'total_html_files': html_files_count,
            'linked_html_files': linked_html_count,
            'unlinked_html_files': html_files_count - linked_html_count,
            'root_level_files': len(root_files),
            'root_level_linked': len(root_files_linked),
            'root_level_unlinked': len(root_files_unlinked)
        },
        'link_graph': link_graph,
        'link_tree': link_tree,
        'reverse_links': reverse_links,
        'all_linked_files': sorted(list(all_linked_files)),
        'root_files': {
            'all': sorted(root_files),
            'linked': sorted(root_files_linked),
            'unlinked': sorted(root_files_unlinked)
        },
        'suggested_moves': suggested_moves,
        'orphaned_html_files': sorted([
            f for f in all_files 
            if f.endswith('.html') and f not in all_linked_files and '/' in f
        ])
    }

def main():
    docs_root = Path(__file__).parent / 'docs'
    
    print("🔍 Analyzing CORTEX documentation structure...")
    print(f"📁 Docs root: {docs_root}")
    print()
    
    result = build_link_map(docs_root)
    
    # Print summary
    print("=" * 80)
    print("📊 DOCUMENTATION LINK ANALYSIS REPORT")
    print("=" * 80)
    print()
    
    stats = result['statistics']
    print("📈 Statistics:")
    print(f"  • Total files: {stats['total_files']}")
    print(f"  • HTML files: {stats['total_html_files']}")
    print(f"  • Linked HTML files: {stats['linked_html_files']}")
    print(f"  • Unlinked HTML files: {stats['unlinked_html_files']}")
    print(f"  • Root-level files: {stats['root_level_files']}")
    print(f"  • Root-level linked: {stats['root_level_linked']}")
    print(f"  • Root-level unlinked: {stats['root_level_unlinked']}")
    print()
    
    print("🔗 Root-Level Files (LINKED):")
    for f in result['root_files']['linked']:
        link_count = len(result['reverse_links'].get(f, []))
        print(f"  ✓ {f} (linked from {link_count} file(s))")
    print()
    
    print("❌ Root-Level Files (UNLINKED - Candidates for Moving/Deletion):")
    for f in result['root_files']['unlinked']:
        print(f"  ✗ {f}")
    print()
    
    print("💡 Suggested Moves:")
    for move in result['suggested_moves']:
        print(f"  {move['current']} → {move['suggested']}")
        print(f"     Reason: {move['reason']}")
    print()
    
    print("🏝️ Orphaned HTML Files (in subfolders but not linked):")
    for f in result['orphaned_html_files'][:20]:  # Show first 20
        print(f"  • {f}")
    if len(result['orphaned_html_files']) > 20:
        print(f"  ... and {len(result['orphaned_html_files']) - 20} more")
    print()
    
    # Save full report
    output_file = Path(__file__).parent / 'docs-link-analysis-report.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
    
    print(f"💾 Full report saved to: {output_file}")
    print()
    print("=" * 80)

if __name__ == '__main__':
    main()
