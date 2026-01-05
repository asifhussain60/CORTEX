#!/usr/bin/env python3
"""
CORTEX Level 1 Theme Cleanup Script
====================================

Purpose: Remove all non-standard glassmorphism color classes from Level 1 HTML files
         Prepares files for standardization to orchestrators/index.html pattern

Author: Asif Hussain
Date: 2026-01-05
Version: 1.0.0

Approved Pattern (from orchestrators/index.html):
- Section 1: glass-panel-purple
- Section 2: glass-panel-emerald  
- Section 3: glass-panel-amber
- Cards: card-variant-primary, card-variant-info, card-variant-success, card-variant-warning

This script ONLY removes old color classes, does NOT apply new ones.
"""

import re
import sys
from pathlib import Path
from typing import List, Dict, Set
from bs4 import BeautifulSoup
import json
from datetime import datetime


class Level1ThemeCleanup:
    """Removes non-standard glassmorphism classes from Level 1 views"""
    
    # Approved classes (orchestrators pattern)
    APPROVED_PANEL_CLASSES = {
        'glass-panel-purple',
        'glass-panel-emerald',
        'glass-panel-amber'
    }
    
    APPROVED_CARD_CLASSES = {
        'card-variant-primary',
        'card-variant-info',
        'card-variant-success',
        'card-variant-warning'
    }
    
    # All possible glass-panel colors (to detect and remove unapproved ones)
    ALL_GLASS_PANEL_COLORS = {
        'glass-panel-cyan',
        'glass-panel-purple',
        'glass-panel-teal',
        'glass-panel-indigo',
        'glass-panel-pink',
        'glass-panel-emerald',
        'glass-panel-amber'
    }
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.docs_dir = project_root / 'docs'
        self.report = {
            'timestamp': datetime.now().isoformat(),
            'files_processed': [],
            'total_removals': 0
        }
    
    def get_level1_pages(self) -> List[Path]:
        """Get all Level 1 HTML index files (excluding orchestrators)"""
        manifest_path = self.project_root / 'cortex-brain' / 'documents' / 'planning' / 'active' / \
                        'html-glassmorphism-alignment' / 'manifests' / 'level1-pages-manifest.yaml'
        
        # Hardcoded list (manifest parsing requires PyYAML)
        level1_dirs = [
            'architecture',
            'features',
            'getting-started',
            'knowledge',
            'learning-paths',
            'lens',
            # 'orchestrators',  # SKIP - this is the approved template
            'security',
            'story',
            'sts',
            'token-optimization',
            'toolkit-manager'
        ]
        
        return [self.docs_dir / dir_name / 'index.html' for dir_name in level1_dirs 
                if (self.docs_dir / dir_name / 'index.html').exists()]
    
    def find_unapproved_classes(self, soup: BeautifulSoup) -> Dict[str, Set[str]]:
        """Find all glass-panel classes that are NOT in approved list"""
        unapproved = {
            'panel': set(),
            'card': set()
        }
        
        for element in soup.find_all(class_=True):
            classes = element.get('class', [])
            
            for cls in classes:
                # Check panel classes
                if cls in self.ALL_GLASS_PANEL_COLORS:
                    if cls not in self.APPROVED_PANEL_CLASSES:
                        unapproved['panel'].add(cls)
                
                # Check card variant classes (currently all are approved, but for future)
                if cls.startswith('card-variant-'):
                    if cls not in self.APPROVED_CARD_CLASSES:
                        unapproved['card'].add(cls)
        
        return unapproved
    
    def remove_unapproved_classes(self, html_path: Path) -> Dict:
        """Remove all non-approved glassmorphism classes from HTML file"""
        print(f"\n🔍 Processing: {html_path.relative_to(self.project_root)}")
        
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find unapproved classes
        unapproved = self.find_unapproved_classes(soup)
        
        if not any(unapproved.values()):
            print("   ✅ No unapproved classes found")
            return {'file': str(html_path), 'removals': 0, 'classes_removed': []}
        
        # Remove unapproved classes
        removals = 0
        classes_removed = []
        
        for element in soup.find_all(class_=True):
            classes = element.get('class', [])
            original_classes = classes.copy()
            
            # Remove unapproved panel classes
            for cls in unapproved['panel']:
                if cls in classes:
                    classes.remove(cls)
                    removals += 1
                    classes_removed.append(cls)
                    print(f"   🗑️  Removed: {cls} from <{element.name}>")
            
            # Remove unapproved card classes
            for cls in unapproved['card']:
                if cls in classes:
                    classes.remove(cls)
                    removals += 1
                    classes_removed.append(cls)
                    print(f"   🗑️  Removed: {cls} from <{element.name}>")
            
            # Update element if classes changed
            if classes != original_classes:
                if classes:
                    element['class'] = classes
                else:
                    del element['class']  # Remove empty class attribute
        
        # Write back to file
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify()))
        
        print(f"   ✅ Removed {removals} unapproved classes")
        
        return {
            'file': str(html_path.relative_to(self.project_root)),
            'removals': removals,
            'classes_removed': list(set(classes_removed))
        }
    
    def run(self) -> Dict:
        """Execute cleanup on all Level 1 pages"""
        print("=" * 70)
        print("🧹 CORTEX Level 1 Theme Cleanup")
        print("=" * 70)
        print(f"\nApproved panel classes: {', '.join(sorted(self.APPROVED_PANEL_CLASSES))}")
        print(f"Approved card classes: {', '.join(sorted(self.APPROVED_CARD_CLASSES))}")
        
        level1_pages = self.get_level1_pages()
        print(f"\n📄 Found {len(level1_pages)} Level 1 pages to process")
        
        for page in level1_pages:
            result = self.remove_unapproved_classes(page)
            self.report['files_processed'].append(result)
            self.report['total_removals'] += result['removals']
        
        # Save report
        report_path = self.project_root / 'cortex-brain' / 'cleanup-reports' / \
                      f'level1-theme-cleanup-{datetime.now().strftime("%Y%m%d-%H%M%S")}.json'
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2)
        
        print("\n" + "=" * 70)
        print(f"✅ Cleanup Complete!")
        print(f"   Total files processed: {len(level1_pages)}")
        print(f"   Total classes removed: {self.report['total_removals']}")
        print(f"   Report saved: {report_path.relative_to(self.project_root)}")
        print("=" * 70)
        
        return self.report


def main():
    """Main entry point"""
    project_root = Path(__file__).parent.parent
    cleanup = Level1ThemeCleanup(project_root)
    
    try:
        report = cleanup.run()
        
        # Exit with status code based on removals
        if report['total_removals'] > 0:
            print(f"\n⚠️  {report['total_removals']} unapproved classes were removed")
            print("   Next step: Run standardize_level1_views.py to apply approved pattern")
            sys.exit(0)  # Success - cleanup completed
        else:
            print("\n✅ All Level 1 views already clean (no unapproved classes found)")
            sys.exit(0)
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
