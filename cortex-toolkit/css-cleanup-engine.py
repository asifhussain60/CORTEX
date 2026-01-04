#!/usr/bin/env python3
"""
🧹 CORTEX CSS Cleanup Engine
=============================

Removes unused CSS classes, eliminates duplicates, and optimizes CSS files.

**Author:** Asif Hussain
**Version:** 1.0.0
**Date:** January 4, 2026
**Copyright:** © 2026 Asif Hussain. All rights reserved.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict


class CSSCleanupEngine:
    """Intelligent CSS cleanup and optimization."""
    
    def __init__(self, docs_dir: Path, css_dir: Path):
        self.docs_dir = docs_dir
        self.css_dir = css_dir
        self.html_files = list(docs_dir.rglob('*.html'))
        self.css_files = list(css_dir.glob('*.css'))
        
        self.used_classes = set()
        self.defined_classes = {}  # class_name -> (file, line_number, rule)
        self.duplicate_rules = defaultdict(list)
    
    def extract_classes_from_html(self) -> Set[str]:
        """Extract all class attributes from HTML files."""
        classes = set()
        
        print(f"📄 Scanning {len(self.html_files)} HTML files for class usage...")
        
        for html_file in self.html_files:
            try:
                content = html_file.read_text(encoding='utf-8')
                
                # Find all class attributes
                class_matches = re.findall(r'class=["\']([\w\s\-_]+)["\']', content)
                
                for class_str in class_matches:
                    # Split multiple classes
                    for cls in class_str.split():
                        classes.add(cls.strip())
                
            except Exception as e:
                print(f"⚠️  Error reading {html_file}: {e}")
        
        print(f"✅ Found {len(classes)} unique classes in HTML")
        return classes
    
    def extract_classes_from_css(self) -> Dict[str, List[Dict]]:
        """Extract all class definitions from CSS files."""
        classes = defaultdict(list)
        
        print(f"🎨 Scanning {len(self.css_files)} CSS files for class definitions...")
        
        for css_file in self.css_files:
            try:
                content = css_file.read_text(encoding='utf-8')
                lines = content.split('\n')
                
                i = 0
                while i < len(lines):
                    line = lines[i].strip()
                    
                    # Match class selectors (simplified)
                    if line.startswith('.') and '{' in line:
                        # Extract class name
                        match = re.match(r'\.([\w\-_]+)', line)
                        if match:
                            class_name = match.group(1)
                            
                            # Extract full rule (multi-line)
                            rule_lines = [line]
                            if not line.endswith('}'):
                                i += 1
                                while i < len(lines) and '}' not in lines[i]:
                                    rule_lines.append(lines[i])
                                    i += 1
                                if i < len(lines):
                                    rule_lines.append(lines[i])
                            
                            rule = '\n'.join(rule_lines)
                            
                            classes[class_name].append({
                                'file': css_file.name,
                                'line': i + 1,
                                'rule': rule
                            })
                    
                    i += 1
                
            except Exception as e:
                print(f"⚠️  Error reading {css_file}: {e}")
        
        total_defs = sum(len(defs) for defs in classes.values())
        print(f"✅ Found {len(classes)} unique classes with {total_defs} definitions in CSS")
        return classes
    
    def find_duplicates(self, css_classes: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """Find duplicate class definitions."""
        duplicates = {}
        
        for class_name, definitions in css_classes.items():
            if len(definitions) > 1:
                # Check if rules are identical
                unique_rules = set(d['rule'] for d in definitions)
                if len(unique_rules) > 1:
                    # Different implementations - flag for review
                    duplicates[class_name] = {
                        'count': len(definitions),
                        'type': 'conflicting',
                        'definitions': definitions
                    }
                else:
                    # Exact duplicates - safe to remove
                    duplicates[class_name] = {
                        'count': len(definitions),
                        'type': 'exact',
                        'definitions': definitions
                    }
        
        print(f"🔍 Found {len(duplicates)} classes with duplicate definitions")
        return duplicates
    
    def find_unused_classes(self, used: Set[str], defined: Dict[str, List[Dict]]) -> Set[str]:
        """Find classes defined in CSS but never used in HTML."""
        unused = set(defined.keys()) - used
        print(f"🗑️  Found {len(unused)} unused CSS classes")
        return unused
    
    def generate_cleanup_plan(self) -> Dict:
        """Generate comprehensive cleanup plan."""
        
        # Step 1: Extract classes
        used_classes = self.extract_classes_from_html()
        defined_classes = self.extract_classes_from_css()
        
        # Step 2: Find issues
        duplicates = self.find_duplicates(defined_classes)
        unused = self.find_unused_classes(used_classes, defined_classes)
        
        # Step 3: Calculate stats
        total_defined = sum(len(defs) for defs in defined_classes.values())
        duplicate_count = sum(d['count'] - 1 for d in duplicates.values())  # Extra copies
        
        cleanup_plan = {
            'statistics': {
                'html_files_scanned': len(self.html_files),
                'css_files_scanned': len(self.css_files),
                'classes_used_in_html': len(used_classes),
                'classes_defined_in_css': len(defined_classes),
                'total_css_definitions': total_defined,
                'unused_classes': len(unused),
                'duplicate_classes': len(duplicates),
                'removable_definitions': len(unused) + duplicate_count
            },
            'unused_classes': sorted(list(unused)),
            'duplicate_classes': duplicates,
            'recommendations': []
        }
        
        # Generate recommendations
        if len(unused) > 0:
            cleanup_plan['recommendations'].append({
                'type': 'remove_unused',
                'priority': 'HIGH',
                'description': f'Remove {len(unused)} unused CSS classes',
                'impact': 'Reduces CSS file size, improves performance'
            })
        
        if len(duplicates) > 0:
            cleanup_plan['recommendations'].append({
                'type': 'eliminate_duplicates',
                'priority': 'HIGH',
                'description': f'Consolidate {len(duplicates)} duplicate class definitions',
                'impact': 'Prevents CSS conflicts, improves maintainability'
            })
        
        exact_duplicates = [k for k, v in duplicates.items() if v['type'] == 'exact']
        if exact_duplicates:
            cleanup_plan['recommendations'].append({
                'type': 'remove_exact_duplicates',
                'priority': 'CRITICAL',
                'description': f'Remove {len(exact_duplicates)} exact duplicate definitions (safe)',
                'impact': 'No risk - identical rules'
            })
        
        conflicting = [k for k, v in duplicates.items() if v['type'] == 'conflicting']
        if conflicting:
            cleanup_plan['recommendations'].append({
                'type': 'resolve_conflicts',
                'priority': 'MEDIUM',
                'description': f'Review {len(conflicting)} conflicting class definitions',
                'impact': 'May require manual decision on which implementation to keep'
            })
        
        return cleanup_plan
    
    def execute_cleanup(self, plan: Dict, dry_run: bool = True) -> Dict:
        """Execute the cleanup plan."""
        
        if dry_run:
            print("\n🔍 DRY RUN MODE - No files will be modified\n")
        else:
            print("\n⚠️  LIVE MODE - Files will be modified!\n")
        
        results = {
            'removed_classes': 0,
            'removed_duplicates': 0,
            'files_modified': set()
        }
        
        # Step 1: Remove unused classes
        unused = set(plan['unused_classes'])
        if unused:
            print(f"🗑️  Removing {len(unused)} unused classes...")
            
            for css_file in self.css_files:
                try:
                    content = css_file.read_text(encoding='utf-8')
                    original_content = content
                    
                    for class_name in unused:
                        # Remove class definition (simplified - may need improvement)
                        pattern = rf'\.{re.escape(class_name)}\s*\{{[^}}]*\}}'
                        content = re.sub(pattern, '', content, flags=re.MULTILINE)
                    
                    if content != original_content:
                        if not dry_run:
                            css_file.write_text(content, encoding='utf-8')
                        results['files_modified'].add(css_file.name)
                        results['removed_classes'] += len(unused)
                        print(f"  ✅ Cleaned {css_file.name}")
                
                except Exception as e:
                    print(f"  ❌ Error processing {css_file}: {e}")
        
        # Step 2: Remove exact duplicates
        duplicates = plan['duplicate_classes']
        exact_dups = {k: v for k, v in duplicates.items() if v['type'] == 'exact'}
        
        if exact_dups:
            print(f"\n🔄 Removing {len(exact_dups)} exact duplicates...")
            
            for class_name, dup_info in exact_dups.items():
                definitions = dup_info['definitions']
                
                # Keep first definition, remove others
                for i, defn in enumerate(definitions[1:], 1):
                    css_file = self.css_dir / defn['file']
                    
                    try:
                        content = css_file.read_text(encoding='utf-8')
                        
                        # Remove this specific occurrence
                        content = content.replace(defn['rule'], '', 1)
                        
                        if not dry_run:
                            css_file.write_text(content, encoding='utf-8')
                        
                        results['files_modified'].add(defn['file'])
                        results['removed_duplicates'] += 1
                        
                    except Exception as e:
                        print(f"  ❌ Error removing duplicate from {defn['file']}: {e}")
        
        print(f"\n✅ Cleanup {'plan generated' if dry_run else 'complete'}:")
        print(f"   Unused classes removed: {results['removed_classes']}")
        print(f"   Duplicate definitions removed: {results['removed_duplicates']}")
        print(f"   Files modified: {len(results['files_modified'])}")
        
        return results


if __name__ == '__main__':
    docs_dir = Path(__file__).parent.parent / 'docs'
    css_dir = docs_dir / 'assets' / 'css'
    
    engine = CSSCleanupEngine(docs_dir, css_dir)
    
    # Generate cleanup plan
    plan = engine.generate_cleanup_plan()
    
    # Save plan
    report_path = Path(__file__).parent.parent / 'reports' / 'css-cleanup-plan.json'
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(plan, indent=2))
    print(f"\n📊 Cleanup plan saved: {report_path}")
    
    # Execute dry run
    print("\n" + "="*60)
    results = engine.execute_cleanup(plan, dry_run=True)
    
    print("\n" + "="*60)
    print("ℹ️  To execute cleanup for real, run:")
    print("   python cortex-toolkit/css-cleanup-engine.py --execute")
