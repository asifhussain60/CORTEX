#!/usr/bin/env python3
"""
CORTEX Documentation Manifest Generator
Scans docs/ folder and creates comprehensive manifest files
Author: Asif Hussain
Date: 2026-01-05
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set
import yaml
from bs4 import BeautifulSoup

def scan_html_file(file_path: Path, docs_root: Path) -> Dict:
    """Extract metadata and links from HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        
        # Extract title
        title_tag = soup.find('title')
        title = title_tag.text.strip() if title_tag else file_path.stem
        
        # Extract description
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        description = desc_tag.get('content', '') if desc_tag else ''
        
        # Extract all links
        links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag.get('href')
            if href and not href.startswith(('http://', 'https://', '#', 'mailto:', 'javascript:')):
                links.append(href)
        
        # Determine level
        relative_path = file_path.relative_to(docs_root)
        depth = len(relative_path.parts) - 1
        
        if depth == 1 and file_path.name == 'index.html':
            level = 1
            category = relative_path.parts[0]
        elif depth > 1:
            level = 2
            category = relative_path.parts[0]
        else:
            level = 0  # Root level
            category = 'home'
        
        return {
            'file_path': str(relative_path).replace('\\', '/'),
            'absolute_path': str(file_path),
            'title': title,
            'description': description,
            'level': level,
            'category': category,
            'depth': depth,
            'links': list(set(links)),  # Remove duplicates
            'link_count': len(set(links))
        }
    except Exception as e:
        print(f"Error scanning {file_path}: {e}")
        return None

def generate_manifests(docs_path: str, output_dir: str):
    """Generate comprehensive manifest files"""
    docs_root = Path(docs_path)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Scan all HTML files
    all_pages = []
    level0_pages = []
    level1_pages = []
    level2_pages = []
    
    for html_file in docs_root.rglob('*.html'):
        page_data = scan_html_file(html_file, docs_root)
        if page_data:
            all_pages.append(page_data)
            
            if page_data['level'] == 0:
                level0_pages.append(page_data)
            elif page_data['level'] == 1:
                level1_pages.append(page_data)
            elif page_data['level'] == 2:
                level2_pages.append(page_data)
    
    # Generate site structure manifest
    site_structure = {
        'metadata': {
            'generated_at': '2026-01-05',
            'total_pages': len(all_pages),
            'level0_count': len(level0_pages),
            'level1_count': len(level1_pages),
            'level2_count': len(level2_pages)
        },
        'structure': {
            'level0': sorted([p['file_path'] for p in level0_pages]),
            'level1': sorted([p['file_path'] for p in level1_pages]),
            'level2': sorted([p['file_path'] for p in level2_pages])
        }
    }
    
    with open(output_path / 'site-structure-manifest.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(site_structure, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    # Generate Level 1 pages manifest
    level1_manifest = {
        'metadata': {
            'generated_at': '2026-01-05',
            'total_level1_pages': len(level1_pages),
            'description': 'Level 1 Hub Pages - Main category entry points'
        },
        'pages': sorted([{
            'file': p['file_path'],
            'title': p['title'],
            'description': p['description'],
            'category': p['category'],
            'outbound_links': p['link_count']
        } for p in level1_pages], key=lambda x: x['category'])
    }
    
    with open(output_path / 'level1-pages-manifest.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(level1_manifest, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    # Generate Level 2 pages manifest (grouped by category)
    level2_by_category = {}
    for page in level2_pages:
        cat = page['category']
        if cat not in level2_by_category:
            level2_by_category[cat] = []
        level2_by_category[cat].append({
            'file': page['file_path'],
            'title': page['title'],
            'description': page['description'][:100] + '...' if len(page['description']) > 100 else page['description'],
            'outbound_links': page['link_count']
        })
    
    level2_manifest = {
        'metadata': {
            'generated_at': '2026-01-05',
            'total_level2_pages': len(level2_pages),
            'categories': len(level2_by_category),
            'description': 'Level 2 Detail Pages - Child pages under Level 1 hubs'
        },
        'pages_by_category': {k: sorted(v, key=lambda x: x['file']) for k, v in sorted(level2_by_category.items())}
    }
    
    with open(output_path / 'level2-pages-manifest.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(level2_manifest, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    # Generate navigation links manifest
    navigation_links = []
    for page in all_pages:
        for link in page['links']:
            navigation_links.append({
                'source': page['file_path'],
                'target': link,
                'source_level': page['level'],
                'source_category': page['category']
            })
    
    navigation_manifest = {
        'metadata': {
            'generated_at': '2026-01-05',
            'total_links': len(navigation_links),
            'description': 'All navigation links across documentation'
        },
        'links': sorted(navigation_links, key=lambda x: (x['source'], x['target']))
    }
    
    with open(output_path / 'navigation-links-manifest.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(navigation_manifest, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"✅ Generated {len(all_pages)} pages across manifests")
    print(f"   - Level 0: {len(level0_pages)} pages")
    print(f"   - Level 1: {len(level1_pages)} pages")
    print(f"   - Level 2: {len(level2_pages)} pages")
    print(f"   - Total links: {len(navigation_links)}")
    print(f"   - Output: {output_path}")

if __name__ == "__main__":
    docs_path = "d:/PROJECTS/CORTEX/docs"
    output_dir = "d:/PROJECTS/CORTEX/cortex-brain/documents/planning/active/html-glassmorphism-alignment/manifests"
    generate_manifests(docs_path, output_dir)
