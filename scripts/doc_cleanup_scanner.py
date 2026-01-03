#!/usr/bin/env python3
"""
Documentation Cleanup Scanner
Scans CORTEX documentation structure to identify:
- Orphaned HTML files (not linked from index.html or sitemap)
- Broken links (href/src pointing to non-existent files)
- Duplicate content
- Unused assets (images, CSS, JS not referenced)
- Directory structure issues

Author: Asif Hussain
Version: 1.0.0
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
import json
from datetime import datetime
from bs4 import BeautifulSoup


class DocCleanupScanner:
    """Comprehensive documentation scanner for cleanup operations"""
    
    def __init__(self, docs_root: str = "docs"):
        self.docs_root = Path(docs_root)
        self.all_html_files: Set[Path] = set()
        self.all_asset_files: Set[Path] = set()
        self.referenced_files: Set[Path] = set()
        self.broken_links: List[Dict] = []
        self.orphaned_files: List[Path] = []
        self.duplicate_content: List[Tuple[Path, Path]] = []
        
    def scan(self) -> Dict:
        """Execute full documentation scan"""
        print("🔍 Starting documentation scan...")
        
        # Phase 1: Inventory
        print("  📂 Phase 1: Building file inventory...")
        self._build_inventory()
        
        # Phase 2: Link analysis
        print("  🔗 Phase 2: Analyzing links...")
        self._analyze_links()
        
        # Phase 3: Orphan detection
        print("  👻 Phase 3: Detecting orphaned files...")
        self._detect_orphans()
        
        # Phase 4: Asset usage
        print("  🖼️  Phase 4: Checking asset usage...")
        self._check_asset_usage()
        
        # Generate report
        return self._generate_report()
    
    def _build_inventory(self):
        """Build inventory of all documentation files"""
        for root, dirs, files in os.walk(self.docs_root):
            # Skip certain directories
            if any(skip in root for skip in ['node_modules', '.git', '__pycache__']):
                continue
                
            root_path = Path(root)
            
            for file in files:
                file_path = root_path / file
                
                if file.endswith('.html'):
                    self.all_html_files.add(file_path)
                elif file.endswith(('.png', '.jpg', '.jpeg', '.svg', '.gif')):
                    self.all_asset_files.add(file_path)
                elif file.endswith(('.css', '.js')):
                    self.all_asset_files.add(file_path)
        
        print(f"    ✅ Found {len(self.all_html_files)} HTML files")
        print(f"    ✅ Found {len(self.all_asset_files)} asset files")
    
    def _analyze_links(self):
        """Analyze all links in HTML files"""
        for html_file in self.all_html_files:
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f.read(), 'html.parser')
                
                # Find all links (href)
                for tag in soup.find_all(['a', 'link']):
                    href = tag.get('href', '')
                    if href and not href.startswith(('http:', 'https:', 'mailto:', '#')):
                        self._check_link(html_file, href)
                
                # Find all sources (src)
                for tag in soup.find_all(['img', 'script']):
                    src = tag.get('src', '')
                    if src and not src.startswith(('http:', 'https:', 'data:')):
                        self._check_link(html_file, src)
                        
            except Exception as e:
                print(f"    ⚠️  Error reading {html_file}: {e}")
    
    def _check_link(self, source_file: Path, link: str):
        """Check if a link is valid"""
        # Clean the link
        link = link.split('?')[0].split('#')[0]
        if not link:
            return
        
        # Resolve relative path
        source_dir = source_file.parent
        target_path = (source_dir / link).resolve()
        
        # Mark as referenced
        self.referenced_files.add(target_path)
        
        # Check if exists
        if not target_path.exists():
            self.broken_links.append({
                'source': str(source_file.relative_to(self.docs_root)),
                'link': link,
                'resolved': str(target_path.relative_to(self.docs_root) if target_path.is_relative_to(self.docs_root) else target_path)
            })
    
    def _detect_orphans(self):
        """Detect orphaned files not linked from anywhere"""
        # Start from index.html and sitemap.html as entry points
        entry_points = [
            self.docs_root / 'index.html',
            self.docs_root / 'sitemap.html'
        ]
        
        # Files not in referenced set are orphans (excluding entry points)
        for html_file in self.all_html_files:
            resolved = html_file.resolve()
            if resolved not in self.referenced_files:
                # Check if it's an entry point
                if not any(resolved == ep.resolve() for ep in entry_points if ep.exists()):
                    self.orphaned_files.append(html_file)
    
    def _check_asset_usage(self):
        """Check which assets are not referenced"""
        unused_assets = []
        for asset in self.all_asset_files:
            if asset.resolve() not in self.referenced_files:
                unused_assets.append(asset)
        
        self.unused_assets = unused_assets
        print(f"    ✅ Found {len(unused_assets)} unused assets")
    
    def _generate_report(self) -> Dict:
        """Generate comprehensive cleanup report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_html_files': len(self.all_html_files),
                'total_assets': len(self.all_asset_files),
                'orphaned_files': len(self.orphaned_files),
                'broken_links': len(self.broken_links),
                'unused_assets': len(self.unused_assets)
            },
            'orphaned_files': [str(f.relative_to(self.docs_root)) for f in self.orphaned_files],
            'broken_links': self.broken_links,
            'unused_assets': [str(f.relative_to(self.docs_root)) for f in self.unused_assets[:50]],  # Limit to 50
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate cleanup recommendations"""
        recommendations = []
        
        if len(self.orphaned_files) > 0:
            recommendations.append(f"Remove or link {len(self.orphaned_files)} orphaned HTML files")
        
        if len(self.broken_links) > 0:
            recommendations.append(f"Fix {len(self.broken_links)} broken links")
        
        if len(self.unused_assets) > 10:
            recommendations.append(f"Review and remove {len(self.unused_assets)} unused assets")
        
        if len(recommendations) == 0:
            recommendations.append("Documentation structure looks healthy!")
        
        return recommendations


def main():
    """Main execution"""
    print("\n" + "="*80)
    print("📋 CORTEX Documentation Cleanup Scanner")
    print("="*80 + "\n")
    
    scanner = DocCleanupScanner()
    report = scanner.scan()
    
    # Save report
    output_path = Path("docs/reports/doc-cleanup-scan.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    print("\n" + "="*80)
    print("📊 SCAN SUMMARY")
    print("="*80)
    print(f"Total HTML Files: {report['summary']['total_html_files']}")
    print(f"Total Assets: {report['summary']['total_assets']}")
    print(f"🔴 Orphaned Files: {report['summary']['orphaned_files']}")
    print(f"🔴 Broken Links: {report['summary']['broken_links']}")
    print(f"🟡 Unused Assets: {report['summary']['unused_assets']}")
    print("\n💡 Recommendations:")
    for rec in report['recommendations']:
        print(f"  • {rec}")
    
    print(f"\n📄 Full report saved to: {output_path}")
    print("="*80 + "\n")
    
    return 0 if report['summary']['orphaned_files'] == 0 else 1


if __name__ == "__main__":
    exit(main())
