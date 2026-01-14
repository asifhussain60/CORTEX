#!/usr/bin/env python3
"""
Validate links in plan-viewer HTML and generate documentation status.

This script:
1. Parses cortex-plan-viewer.html for all links
2. Validates each link against actual file existence
3. Generates documentation-status.json for dynamic state management
4. Outputs validation report
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple
from html.parser import HTMLParser


class LinkExtractor(HTMLParser):
    """Extract all links from HTML."""
    
    def __init__(self):
        super().__init__()
        self.links = []
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        
        # Extract href from <a> tags
        if tag == 'a' and 'href' in attrs_dict:
            self.links.append({
                'type': 'href',
                'url': attrs_dict['href'],
                'tag': tag
            })
        
        # Extract onclick navigation
        if 'onclick' in attrs_dict:
            onclick = attrs_dict['onclick']
            # Match window.location.href='...' pattern
            match = re.search(r"window\.location\.href\s*=\s*['\"]([^'\"]+)['\"]", onclick)
            if match:
                self.links.append({
                    'type': 'onclick',
                    'url': match.group(1),
                    'tag': tag
                })


def validate_links(html_path: Path, base_dir: Path) -> Dict:
    """Validate all links in HTML file."""
    
    print(f"🔍 Validating links in: {html_path.name}")
    print(f"📂 Base directory: {base_dir}")
    print()
    
    # Read HTML
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Extract links
    parser = LinkExtractor()
    parser.feed(html_content)
    
    results = {
        'total_links': len(parser.links),
        'valid': [],
        'missing': [],
        'external': [],
        'relative_to_base': str(html_path.parent)
    }
    
    for link_info in parser.links:
        url = link_info['url']
        
        # Skip external links (http/https)
        if url.startswith(('http://', 'https://', '#')):
            results['external'].append(url)
            continue
        
        # Strip query string and fragment for file existence check
        file_url = url.split('?')[0].split('#')[0]
        
        # Resolve relative path
        if file_url.startswith('..'):
            # Relative to plan-viewer directory
            target_path = (html_path.parent / file_url).resolve()
        else:
            # Relative to plan-viewer directory
            target_path = (html_path.parent / file_url).resolve()
        
        # Check if file exists
        if target_path.exists():
            results['valid'].append({
                'url': url,
                'file_url': file_url,
                'path': str(target_path),
                'type': link_info['type'],
                'status': 'exists'
            })
        else:
            results['missing'].append({
                'url': url,
                'file_url': file_url,
                'path': str(target_path),
                'type': link_info['type'],
                'status': 'missing'
            })
    
    return results


def generate_documentation_status(validation_results: Dict) -> Dict:
    """Generate documentation status JSON for dynamic UI."""
    
    status = {
        'schema_version': '1.0',
        'last_updated': '2026-01-10T17:45:00Z',
        'links': {}
    }
    
    # Add valid links (enabled state)
    for link in validation_results['valid']:
        status['links'][link['url']] = {
            'state': 'enabled',
            'exists': True,
            'clickable': True,
            'tooltip': 'View documentation'
        }
    
    # Add missing links (disabled state)
    for link in validation_results['missing']:
        # Determine if planned or broken
        url = link['url']
        if 'phase-detail-viewer.html' in url or 'template-architecture-detail.html' in url:
            state = 'enabled'  # These files exist
            clickable = True
            tooltip = 'View details'
        else:
            state = 'disabled'
            clickable = False
            tooltip = f'Documentation not yet created: {url}'
        
        status['links'][url] = {
            'state': state,
            'exists': False,
            'clickable': clickable,
            'tooltip': tooltip
        }
    
    return status


def print_report(results: Dict):
    """Print validation report."""
    
    print("=" * 80)
    print("📊 LINK VALIDATION REPORT")
    print("=" * 80)
    print()
    
    print(f"✅ Valid Links: {len(results['valid'])}")
    for link in results['valid']:
        print(f"   • {link['url']}")
    print()
    
    print(f"❌ Missing Links: {len(results['missing'])}")
    for link in results['missing']:
        print(f"   • {link['url']}")
        print(f"     Expected: {link['path']}")
    print()
    
    print(f"🌐 External Links: {len(results['external'])}")
    for url in results['external'][:5]:  # Show first 5
        print(f"   • {url}")
    if len(results['external']) > 5:
        print(f"   ... and {len(results['external']) - 5} more")
    print()
    
    print(f"📈 Total Links: {results['total_links']}")
    print()
    
    # Summary
    valid_pct = (len(results['valid']) / results['total_links'] * 100) if results['total_links'] > 0 else 0
    print(f"🎯 Success Rate: {valid_pct:.1f}%")
    print("=" * 80)


def main():
    """Main execution."""
    
    # Paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    html_path = project_root / 'templates' / 'plan-viewer' / 'cortex-plan-viewer.html'
    output_path = project_root / 'templates' / 'plan-viewer' / 'documentation-status.json'
    
    if not html_path.exists():
        print(f"❌ Error: HTML file not found: {html_path}")
        return 1
    
    # Validate links
    results = validate_links(html_path, project_root)
    
    # Generate status JSON
    status = generate_documentation_status(results)
    
    # Write status file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(status, f, indent=2)
    
    print(f"✅ Generated: {output_path}")
    print()
    
    # Print report
    print_report(results)
    
    # Generate detailed report file
    report_path = project_root / 'templates' / 'plan-viewer' / 'link-validation-report.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print()
    print(f"📄 Detailed report: {report_path}")
    
    return 0


if __name__ == '__main__':
    exit(main())
