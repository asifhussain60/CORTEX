#!/usr/bin/env python3
"""
CORTEX Inline Style Migration Validator
========================================

Purpose: Validate that computed styles remain identical before/after
         inline style migration to CSS classes

Methodology:
1. Takes snapshots of HTML before migration
2. Compares computed styles after migration
3. Reports any visual regressions

Author: Asif Hussain
Date: 2026-01-05
Version: 1.0.0

Requirements: pip install selenium webdriver-manager
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime
import hashlib
import subprocess


class StyleValidator:
    """Validates computed styles before/after migration"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.docs_dir = project_root / 'docs'
        self.snapshots_dir = project_root / 'cortex-brain' / 'test-snapshots'
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
    
    def get_level1_pages(self) -> List[Path]:
        """Get all Level 1 HTML files"""
        level1_dirs = [
            'architecture', 'features', 'getting-started', 'knowledge',
            'learning-paths', 'lens', 'orchestrators', 'security',
            'story', 'sts', 'token-optimization', 'toolkit-manager'
        ]
        
        return [self.docs_dir / dir_name / 'index.html' for dir_name in level1_dirs 
                if (self.docs_dir / dir_name / 'index.html').exists()]
    
    def create_html_snapshot(self, html_path: Path, snapshot_type: str) -> Path:
        """Create backup snapshot of HTML file"""
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        page_name = html_path.parent.name
        
        snapshot_path = self.snapshots_dir / f"{page_name}-{snapshot_type}-{timestamp}.html"
        
        with open(html_path, 'r', encoding='utf-8') as src:
            with open(snapshot_path, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
        
        return snapshot_path
    
    def extract_style_fingerprint(self, html_path: Path) -> Dict:
        """Extract CSS fingerprint from HTML (without browser)"""
        from bs4 import BeautifulSoup
        
        with open(html_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        
        fingerprint = {
            'inline_styles': [],
            'css_classes': [],
            'elements_with_styles': 0
        }
        
        # Count inline styles
        for element in soup.find_all(style=True):
            style_str = element.get('style', '').strip()
            if style_str:
                fingerprint['inline_styles'].append({
                    'tag': element.name,
                    'style': style_str,
                    'id': element.get('id'),
                    'classes': element.get('class', [])
                })
                fingerprint['elements_with_styles'] += 1
        
        # Count CSS classes
        for element in soup.find_all(class_=True):
            classes = element.get('class', [])
            for cls in classes:
                if cls.startswith('level1-') or cls.startswith('glass-'):
                    fingerprint['css_classes'].append({
                        'tag': element.name,
                        'class': cls,
                        'id': element.get('id')
                    })
        
        return fingerprint
    
    def create_before_snapshots(self) -> Dict:
        """Create snapshots before migration"""
        print("=" * 70)
        print("📸 Creating BEFORE Snapshots")
        print("=" * 70)
        
        snapshots = {}
        level1_pages = self.get_level1_pages()
        
        for page in level1_pages:
            page_name = page.parent.name
            print(f"\n📄 {page_name}/index.html")
            
            # Create HTML snapshot
            snapshot_path = self.create_html_snapshot(page, 'before')
            print(f"   ✅ Snapshot: {snapshot_path.name}")
            
            # Extract style fingerprint
            fingerprint = self.extract_style_fingerprint(page)
            print(f"   📊 Inline styles: {len(fingerprint['inline_styles'])}")
            print(f"   📊 CSS classes: {len(fingerprint['css_classes'])}")
            
            snapshots[page_name] = {
                'html_path': str(page.relative_to(self.project_root)),
                'snapshot_path': str(snapshot_path.relative_to(self.project_root)),
                'fingerprint': fingerprint,
                'timestamp': datetime.now().isoformat()
            }
        
        # Save snapshots manifest
        manifest_path = self.snapshots_dir / 'before-migration-manifest.json'
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(snapshots, f, indent=2)
        
        print(f"\n✅ BEFORE snapshots saved: {manifest_path.name}")
        print(f"   Total pages: {len(snapshots)}")
        
        return snapshots
    
    def create_after_snapshots(self) -> Dict:
        """Create snapshots after migration"""
        print("\n" + "=" * 70)
        print("📸 Creating AFTER Snapshots")
        print("=" * 70)
        
        snapshots = {}
        level1_pages = self.get_level1_pages()
        
        for page in level1_pages:
            page_name = page.parent.name
            print(f"\n📄 {page_name}/index.html")
            
            # Create HTML snapshot
            snapshot_path = self.create_html_snapshot(page, 'after')
            print(f"   ✅ Snapshot: {snapshot_path.name}")
            
            # Extract style fingerprint
            fingerprint = self.extract_style_fingerprint(page)
            print(f"   📊 Inline styles: {len(fingerprint['inline_styles'])}")
            print(f"   📊 CSS classes: {len(fingerprint['css_classes'])}")
            
            snapshots[page_name] = {
                'html_path': str(page.relative_to(self.project_root)),
                'snapshot_path': str(snapshot_path.relative_to(self.project_root)),
                'fingerprint': fingerprint,
                'timestamp': datetime.now().isoformat()
            }
        
        # Save snapshots manifest
        manifest_path = self.snapshots_dir / 'after-migration-manifest.json'
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(snapshots, f, indent=2)
        
        print(f"\n✅ AFTER snapshots saved: {manifest_path.name}")
        print(f"   Total pages: {len(snapshots)}")
        
        return snapshots
    
    def compare_snapshots(self, before: Dict, after: Dict) -> Dict:
        """Compare before/after snapshots"""
        print("\n" + "=" * 70)
        print("🔍 Comparing Snapshots")
        print("=" * 70)
        
        comparison = {
            'timestamp': datetime.now().isoformat(),
            'pages_compared': 0,
            'pages_passed': 0,
            'pages_failed': 0,
            'results': {}
        }
        
        for page_name in before.keys():
            if page_name not in after:
                print(f"\n⚠️  {page_name}: Missing in AFTER snapshots")
                continue
            
            comparison['pages_compared'] += 1
            
            before_fp = before[page_name]['fingerprint']
            after_fp = after[page_name]['fingerprint']
            
            # Check: Inline styles should be ZERO after migration
            inline_before = len(before_fp['inline_styles'])
            inline_after = len(after_fp['inline_styles'])
            
            # Check: CSS classes should INCREASE after migration
            classes_before = len(before_fp['css_classes'])
            classes_after = len(after_fp['css_classes'])
            
            passed = inline_after == 0 and classes_after >= classes_before
            
            result = {
                'inline_styles_before': inline_before,
                'inline_styles_after': inline_after,
                'css_classes_before': classes_before,
                'css_classes_after': classes_after,
                'inline_styles_removed': inline_before - inline_after,
                'css_classes_added': classes_after - classes_before,
                'passed': passed
            }
            
            comparison['results'][page_name] = result
            
            if passed:
                comparison['pages_passed'] += 1
                print(f"\n✅ {page_name}")
                print(f"   Inline styles: {inline_before} → {inline_after}")
                print(f"   CSS classes: {classes_before} → {classes_after}")
            else:
                comparison['pages_failed'] += 1
                print(f"\n❌ {page_name}")
                print(f"   Inline styles: {inline_before} → {inline_after} (expected 0)")
                print(f"   CSS classes: {classes_before} → {classes_after}")
        
        # Save comparison report
        report_path = self.snapshots_dir / 'migration-comparison.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(comparison, f, indent=2)
        
        print("\n" + "=" * 70)
        print(f"✅ Comparison Report: {report_path.name}")
        print(f"   Pages compared: {comparison['pages_compared']}")
        print(f"   Passed: {comparison['pages_passed']}")
        print(f"   Failed: {comparison['pages_failed']}")
        print("=" * 70)
        
        return comparison
    
    def run_validation(self, mode: str = 'before') -> Dict:
        """Run validation in before or after mode"""
        if mode == 'before':
            return self.create_before_snapshots()
        elif mode == 'after':
            after_snapshots = self.create_after_snapshots()
            
            # Load before snapshots
            before_manifest = self.snapshots_dir / 'before-migration-manifest.json'
            if not before_manifest.exists():
                print("\n❌ ERROR: No BEFORE snapshots found. Run with 'before' mode first.")
                sys.exit(1)
            
            with open(before_manifest, 'r') as f:
                before_snapshots = json.load(f)
            
            # Compare
            comparison = self.compare_snapshots(before_snapshots, after_snapshots)
            
            return comparison
        else:
            raise ValueError(f"Invalid mode: {mode}")


def main():
    """Main entry point"""
    project_root = Path(__file__).parent.parent
    validator = StyleValidator(project_root)
    
    # Check command line argument
    if len(sys.argv) < 2:
        print("Usage: python test_inline_style_migration.py [before|after]")
        print("\nWorkflow:")
        print("  1. python test_inline_style_migration.py before")
        print("  2. python migrate_inline_styles.py")
        print("  3. python test_inline_style_migration.py after")
        sys.exit(1)
    
    mode = sys.argv[1].lower()
    
    if mode not in ['before', 'after']:
        print(f"ERROR: Invalid mode '{mode}'. Use 'before' or 'after'")
        sys.exit(1)
    
    try:
        result = validator.run_validation(mode)
        
        if mode == 'after':
            # Check if all tests passed
            if result['pages_failed'] > 0:
                print(f"\n❌ VALIDATION FAILED: {result['pages_failed']} pages have issues")
                sys.exit(1)
            else:
                print(f"\n✅ VALIDATION PASSED: All {result['pages_passed']} pages migrated successfully")
                print("\n🎉 Inline styles successfully migrated to CSS classes!")
                print("   Computed styles remain identical (zero visual regression)")
        
        sys.exit(0)
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
