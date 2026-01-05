#!/usr/bin/env python3
"""
CORTEX Level 1 Standardization Script
======================================

Purpose: Apply orchestrators/index.html glassmorphism pattern to all Level 1 views
         Enforces consistent 3-section color rotation: purple → emerald → amber

Author: Asif Hussain
Date: 2026-01-05
Version: 1.0.0

Approved Pattern:
- Section 1: glass-panel-purple (Master content)
- Section 2: glass-panel-emerald (Core capabilities)  
- Section 3: glass-panel-amber (Categories/Overview)

This script:
1. Identifies all glass-card-display sections (excluding hero)
2. Applies color rotation in order
3. Updates html-standardization-state.json
4. Creates git checkpoint before changes

CRITICAL: This is the ONLY way to standardize Level 1 views.
          Copilot must NEVER edit HTML directly.
"""

import re
import sys
from pathlib import Path
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import json
from datetime import datetime
import subprocess


class Level1Standardizer:
    """Applies orchestrators pattern to Level 1 HTML files"""
    
    # Approved 3-color rotation pattern
    COLOR_ROTATION = [
        'glass-panel-purple',
        'glass-panel-emerald',
        'glass-panel-amber'
    ]
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.docs_dir = project_root / 'docs'
        self.state_file = project_root / 'cortex-brain' / 'cache' / 'html-standardization-state.json'
        self.state = self.load_state()
    
    def load_state(self) -> Dict:
        """Load state tracking file"""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'version': '2.0',
            'last_updated': datetime.now().isoformat(),
            'pages': {},
            'global_state': {
                'total_pages_processed': 0,
                'css_registry_version': '2.0',
                'approved_panel_library_version': '1.1.0'
            }
        }
    
    def save_state(self):
        """Save state tracking file"""
        self.state['last_updated'] = datetime.now().isoformat()
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2)
    
    def create_git_checkpoint(self, page_name: str):
        """Create git checkpoint tag before changes"""
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        tag_name = f"checkpoint-{page_name}-{timestamp}"
        
        try:
            subprocess.run([
                'git', 'tag', '-a', tag_name, '-m',
                f'Pre-standardization checkpoint: {page_name}'
            ], check=True, capture_output=True)
            print(f"   📌 Git checkpoint created: {tag_name}")
            return tag_name
        except subprocess.CalledProcessError as e:
            print(f"   ⚠️  Warning: Could not create git tag: {e}")
            return None
    
    def standardize_html(self, html_path: Path) -> Dict:
        """Apply 3-color rotation to glass-card-display sections"""
        page_name = html_path.parent.name
        print(f"\n🎨 Standardizing: {html_path.relative_to(self.project_root)}")
        
        # Create git checkpoint
        checkpoint_tag = self.create_git_checkpoint(page_name)
        
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all sections with glass-card-display (exclude hero-introduction)
        sections = soup.find_all('section', class_='glass-card-display')
        content_sections = [s for s in sections if 'hero-introduction' not in s.get('class', [])]
        
        if not content_sections:
            print("   ⚠️  No content sections found to standardize")
            return {'sections_updated': 0}
        
        print(f"   📊 Found {len(content_sections)} content sections")
        
        # Apply color rotation
        updates = 0
        applied_patterns = []
        
        for i, section in enumerate(content_sections):
            color_class = self.COLOR_ROTATION[i % len(self.COLOR_ROTATION)]
            classes = section.get('class', [])
            
            # Remove any existing glass-panel-* classes
            classes_cleaned = [c for c in classes if not c.startswith('glass-panel-')]
            
            # Add new color class
            if color_class not in classes_cleaned:
                classes_cleaned.append(color_class)
                section['class'] = classes_cleaned
                updates += 1
                applied_patterns.append(color_class)
                print(f"   ✅ Section {i+1}: Applied {color_class}")
        
        # Write back to file
        if updates > 0:
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(str(soup.prettify()))
            print(f"   💾 Saved changes ({updates} sections updated)")
        else:
            print("   ℹ️  No changes needed (already standardized)")
        
        # Update state tracking
        page_key = str(html_path.relative_to(self.project_root)).replace('\\', '/')
        self.state['pages'][page_key] = {
            'last_modified': datetime.now().isoformat(),
            'git_checkpoint': checkpoint_tag,
            'applied_patterns': list(set(applied_patterns)),
            'sections_updated': updates,
            'complexity_score': len(content_sections),
            'status': 'standardized',
            'approved_tag': 'v5.0-glassmorphism-approved'
        }
        
        return {
            'sections_updated': updates,
            'patterns_applied': applied_patterns,
            'checkpoint': checkpoint_tag
        }
    
    def run(self, target_file: Optional[str] = None) -> Dict:
        """Execute standardization on one or all Level 1 pages"""
        print("=" * 70)
        print("🎨 CORTEX Level 1 Standardization")
        print("=" * 70)
        print(f"\nApproved pattern: {' → '.join(self.COLOR_ROTATION)}")
        print(f"Based on: orchestrators/index.html (v5.0-glassmorphism-approved)")
        
        if target_file:
            # Single file mode
            target_path = Path(target_file)
            if not target_path.is_absolute():
                target_path = self.project_root / target_path
            
            if not target_path.exists():
                print(f"\n❌ ERROR: File not found: {target_path}")
                return {'error': 'File not found'}
            
            result = self.standardize_html(target_path)
            total_updates = result['sections_updated']
        else:
            # Batch mode - all Level 1 views
            level1_dirs = [
                'architecture', 'features', 'getting-started', 'knowledge',
                'learning-paths', 'lens', 'security', 'story', 'sts',
                'token-optimization', 'toolkit-manager'
            ]
            
            total_updates = 0
            for dir_name in level1_dirs:
                html_path = self.docs_dir / dir_name / 'index.html'
                if html_path.exists():
                    result = self.standardize_html(html_path)
                    total_updates += result['sections_updated']
        
        # Save state
        self.save_state()
        
        print("\n" + "=" * 70)
        print(f"✅ Standardization Complete!")
        print(f"   Total sections updated: {total_updates}")
        print(f"   State saved: {self.state_file.relative_to(self.project_root)}")
        print("=" * 70)
        
        return {'total_updates': total_updates}


def main():
    """Main entry point"""
    project_root = Path(__file__).parent.parent
    standardizer = Level1Standardizer(project_root)
    
    # Check for target file argument
    target_file = sys.argv[1] if len(sys.argv) > 1 else None
    
    try:
        result = standardizer.run(target_file)
        
        if 'error' in result:
            sys.exit(1)
        
        if result['total_updates'] > 0:
            print("\n✅ Next steps:")
            print("   1. Review changes in git diff")
            print("   2. Test pages in browser")
            print("   3. Commit with: git commit -m 'feat(docs): Standardize Level 1 views to orchestrators pattern'")
        else:
            print("\n✅ All Level 1 views already standardized")
        
        sys.exit(0)
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
