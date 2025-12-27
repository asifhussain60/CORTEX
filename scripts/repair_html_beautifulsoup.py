#!/usr/bin/env python3
"""Intelligent HTML repair using BeautifulSoup."""

import sys
from pathlib import Path
from bs4 import BeautifulSoup
import argparse

def repair_html_file(file_path: Path, dry_run: bool = False) -> dict:
    """Repair a single HTML file using BeautifulSoup.
    
    Returns:
        dict with repair statistics
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Parse with BeautifulSoup - it auto-fixes most structural issues
        soup = BeautifulSoup(original_content, 'html.parser')
        
        # Ensure html tag exists
        if not soup.html:
            # Wrap everything in html tag
            html_tag = soup.new_tag('html')
            html_tag.attrs['lang'] = 'en'
            for element in list(soup.children):
                html_tag.append(element.extract())
            soup.append(html_tag)
        
        # Ensure head exists
        if not soup.head:
            head_tag = soup.new_tag('head')
            soup.html.insert(0, head_tag)
        
        # Ensure body exists
        if not soup.body:
            body_tag = soup.new_tag('body')
            # Move non-head content to body
            for element in list(soup.html.children):
                if element.name != 'head':
                    body_tag.append(element.extract())
            soup.html.append(body_tag)
        
        # Get prettified output
        repaired_content = str(soup)
        
        # Calculate changes
        original_lines = original_content.splitlines()
        repaired_lines = repaired_content.splitlines()
        
        changes = {
            'file': file_path,
            'original_size': len(original_content),
            'repaired_size': len(repaired_content),
            'line_diff': len(repaired_lines) - len(original_lines),
            'modified': original_content != repaired_content
        }
        
        if not dry_run and changes['modified']:
            # Write repaired content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(repaired_content)
        
        return changes
        
    except Exception as e:
        return {
            'file': file_path,
            'error': str(e)
        }

def main():
    """Repair all HTML files in docs/."""
    parser = argparse.ArgumentParser(description='Repair HTML files using BeautifulSoup')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be fixed without modifying files')
    parser.add_argument('--file', type=str, help='Repair single file instead of all')
    parser.add_argument('--tier', type=int, choices=[1, 2, 3, 4], help='Repair specific tier only')
    args = parser.parse_args()
    
    docs_dir = Path('/Users/asifhussain/PROJECTS/CORTEX/docs')
    
    # Define tiers
    tier1_patterns = [
        'index.html',
        'features/index.html',
        'architecture/index.html',
        'technical/index.html',
        'governance/skull-rulebook.html',
        'features/planning-system.html',
        'features/tdd-mastery.html'
    ]
    
    if args.file:
        # Single file mode
        file_path = Path(args.file)
        if not file_path.is_absolute():
            file_path = docs_dir / file_path
        files_to_repair = [file_path]
    elif args.tier:
        # Tier-specific mode
        all_files = list(docs_dir.rglob('*.html'))
        
        if args.tier == 1:
            files_to_repair = [f for f in all_files if any(str(f).endswith(p) for p in tier1_patterns)]
        elif args.tier == 2:
            tier1_files = [f for f in all_files if any(str(f).endswith(p) for p in tier1_patterns)]
            files_to_repair = [f for f in all_files if 'features/' in str(f) and f not in tier1_files]
        elif args.tier == 3:
            files_to_repair = [f for f in all_files if 'technical/' in str(f) or 'orchestration/' in str(f)]
        else:  # tier 4
            tier1_files = [f for f in all_files if any(str(f).endswith(p) for p in tier1_patterns)]
            feature_files = [f for f in all_files if 'features/' in str(f)]
            tech_files = [f for f in all_files if 'technical/' in str(f) or 'orchestration/' in str(f)]
            files_to_repair = [f for f in all_files if f not in tier1_files and f not in feature_files and f not in tech_files]
    else:
        # All files mode
        files_to_repair = list(docs_dir.rglob('*.html'))
    
    mode = "DRY RUN" if args.dry_run else "REPAIR"
    print(f"🔧 HTML {mode} - BeautifulSoup Auto-Repair")
    print("=" * 60)
    print(f"Files to process: {len(files_to_repair)}\n")
    
    modified_count = 0
    error_count = 0
    
    for file_path in sorted(files_to_repair):
        result = repair_html_file(file_path, dry_run=args.dry_run)
        
        if 'error' in result:
            print(f"❌ {file_path.relative_to(docs_dir)}")
            print(f"   Error: {result['error']}\n")
            error_count += 1
        elif result['modified']:
            print(f"✅ {file_path.relative_to(docs_dir)}")
            if result['line_diff'] != 0:
                sign = '+' if result['line_diff'] > 0 else ''
                print(f"   Lines: {sign}{result['line_diff']}")
            modified_count += 1
        else:
            print(f"⚪ {file_path.relative_to(docs_dir)} (no changes needed)")
    
    print("\n" + "=" * 60)
    if args.dry_run:
        print(f"📊 Would modify: {modified_count} files")
    else:
        print(f"✅ Repaired: {modified_count} files")
    
    if error_count > 0:
        print(f"❌ Errors: {error_count} files")
    
    print("\n💡 Next: Run validation script to verify repairs")
    
    return 0 if error_count == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
