#!/usr/bin/env python3
"""
Quick Inline Style Validator
Validates that CSS refactoring eliminated inline styles from documentation
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple


HUB_FILES = [
    "docs/index.html",  # Level 0
    "docs/future/index.html",
    "docs/orchestrators/index.html",
    "docs/sts/index.html",
    "docs/architecture/index.html",
    "docs/knowledge/index.html",
    "docs/features/index.html",
    "docs/validation/index.html",
    "docs/getting-started/index.html",
    "docs/lens/index.html",
]

# Acceptable inline style patterns (JS-generated dynamic content)
ACCEPTABLE_PATTERNS = [
    r'style="display:\s*none;?"',  # JS toggle functionality
    r'style="display:\s*block;?"',  # JS show functionality
    r'style="background:\s*\$\{[^}]+\}',  # JS template literal dynamic colors
    r'style="background:\s*#[0-9a-fA-F]{3,6};?"',  # JS-generated dynamic background colors
    r'style="color:\s*#[0-9a-fA-F]{3,6};?"',  # JS-generated dynamic text colors
    r'style="[^"]*\$\{[^}]+\}[^"]*"',  # Any JS template literal in style
    r'style="display:\s*grid;[^"]*"',  # JS-generated grid layouts for lazy-loaded content
]


def validate_file(file_path: Path) -> Tuple[int, List[str], List[str]]:
    """
    Validate a single HTML file for inline styles
    
    Returns:
        (total_count, unacceptable_styles, acceptable_styles)
    """
    if not file_path.exists():
        return -1, [f"FILE NOT FOUND: {file_path}"], []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all style attributes
    style_pattern = r'style="([^"]*)"'
    all_styles = re.findall(style_pattern, content)
    
    acceptable_styles = []
    unacceptable_styles = []
    
    for style in all_styles:
        full_attr = f'style="{style}"'
        is_acceptable = any(
            re.search(pattern, full_attr)
            for pattern in ACCEPTABLE_PATTERNS
        )
        
        if is_acceptable:
            acceptable_styles.append(style)
        else:
            unacceptable_styles.append(style)
    
    return len(all_styles), unacceptable_styles, acceptable_styles


def main():
    """Run validation on all hub files"""
    print("\n" + "="*80)
    print("INLINE STYLE VALIDATION REPORT")
    print("Phase 2: Level 1 Hub Files - CSS Refactoring")
    print("="*80 + "\n")
    
    total_files = len(HUB_FILES)
    passed = 0
    failed = 0
    
    results = []
    
    for hub_file in HUB_FILES:
        file_path = Path(hub_file)
        total_count, unacceptable, acceptable = validate_file(file_path)
        
        # File passes if: exists AND unacceptable_count <= 0
        file_passed = total_count >= 0 and len(unacceptable) == 0
        
        status_icon = "✅" if file_passed else "❌"
        
        results.append({
            'file': hub_file,
            'passed': file_passed,
            'total': total_count,
            'unacceptable': len(unacceptable),
            'acceptable': len(acceptable),
            'samples': unacceptable[:3] if unacceptable else []
        })
        
        if file_passed:
            passed += 1
        else:
            failed += 1
        
        # Print summary line
        if total_count == -1:
            print(f"{status_icon} {hub_file:40s} - FILE NOT FOUND")
        else:
            print(f"{status_icon} {hub_file:40s} - "
                  f"Total: {total_count:3d} | "
                  f"Unacceptable: {len(unacceptable):3d} | "
                  f"Acceptable: {len(acceptable):3d}")
    
    print("\n" + "="*80)
    print(f"SUMMARY: {passed}/{total_files} files passed")
    print("="*80 + "\n")
    
    # Print failures detail
    if failed > 0:
        print("FAILURES DETAIL:\n")
        for result in results:
            if not result['passed']:
                print(f"❌ {result['file']}")
                print(f"   Unacceptable inline styles: {result['unacceptable']}")
                if result['samples']:
                    print(f"   Samples:")
                    for i, sample in enumerate(result['samples'], 1):
                        print(f"      {i}. style=\"{sample[:80]}...\"" if len(sample) > 80 else f"      {i}. style=\"{sample}\"")
                print()
    
    # Exit code
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit(main())
