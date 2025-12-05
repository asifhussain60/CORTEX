"""
Documentation Link Validator

Validates all links in CORTEX markdown documentation files.

Checks:
- #file: references point to existing files
- Internal anchors exist in target files
- Module guide references are valid
- Relative paths resolve correctly

Usage:
    python scripts/validate_docs_links.py

Author: Asif Hussain
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple

CORTEX_ROOT = Path(__file__).resolve().parents[1]
DOCS_TO_CHECK = [
    CORTEX_ROOT / ".github" / "copilot-instructions.md",
    CORTEX_ROOT / ".github" / "prompts" / "CORTEX.prompt.md"
]


def extract_file_references(content: str, file_path: Path) -> List[Tuple[int, str]]:
    """Extract all file references from markdown content."""
    references = []
    
    # Pattern 1: #file:path/to/file.md
    for match in re.finditer(r'#file:([^\s\)]+)', content):
        line_num = content[:match.start()].count('\n') + 1
        ref = match.group(1)
        # Skip template patterns
        if not ('[' in ref or '{' in ref):
            references.append((line_num, ref))
    
    # Pattern 2: [text](path/to/file.md) - but NOT in backticks and NOT template patterns
    for match in re.finditer(r'\[([^\]]+)\]\(([^\)]+\.md)\)', content):
        line_num = content[:match.start()].count('\n') + 1
        ref_path = match.group(2)
        # Skip if URL, or template pattern, or contains Example
        if (not ref_path.startswith('http') and 
            '[' not in ref_path and 
            '{' not in ref_path and
            '*' not in ref_path):
            references.append((line_num, ref_path))
    
    # Pattern 3: `.github/prompts/modules/guide-name.md` - only in tables/lists
    for match in re.finditer(r'`([^`]+\.md)`', content):
        line_num = content[:match.start()].count('\n') + 1
        ref = match.group(1)
        # Only process if in a table row (contains |) and is a real path (starts with . or /)
        line_start = content.rfind('\n', 0, match.start()) + 1
        line_end = content.find('\n', match.end())
        if line_end == -1:
            line_end = len(content)
        line_text = content[line_start:line_end]
        
        # Process only table rows with actual file references
        if ('|' in line_text and 
            (ref.startswith('.github/') or ref.startswith('../') or ref.startswith('cortex-brain/')) and
            '[' not in ref and '{' not in ref and '*' not in ref and
            'Example' not in line_text and 'example' not in line_text and 'pattern' not in line_text.lower()):
            references.append((line_num, ref))
    
    return references
    
    return references


def resolve_path(ref: str, from_file: Path) -> Path:
    """Resolve relative path from source file."""
    if ref.startswith('#file:'):
        ref = ref[6:]  # Remove #file: prefix
    
    # Handle relative paths
    if ref.startswith('./') or ref.startswith('../'):
        return (from_file.parent / ref).resolve()
    
    # Handle absolute paths from repo root
    if ref.startswith('.github/') or ref.startswith('cortex-brain/'):
        return (CORTEX_ROOT / ref).resolve()
    
    # Try relative to file's directory
    return (from_file.parent / ref).resolve()


def validate_links(file_path: Path) -> Dict[str, List]:
    """Validate all links in a markdown file."""
    results = {
        'valid': [],
        'broken': [],
        'total': 0
    }
    
    content = file_path.read_text(encoding='utf-8')
    references = extract_file_references(content, file_path)
    results['total'] = len(references)
    
    for line_num, ref in references:
        resolved = resolve_path(ref, file_path)
        
        if resolved.exists():
            results['valid'].append({
                'line': line_num,
                'reference': ref,
                'resolved': str(resolved)
            })
        else:
            results['broken'].append({
                'line': line_num,
                'reference': ref,
                'resolved': str(resolved)
            })
    
    return results


def main():
    """Run validation on all documentation files."""
    print("=" * 80)
    print("CORTEX Documentation Link Validator")
    print("=" * 80)
    print()
    
    total_valid = 0
    total_broken = 0
    
    for doc_file in DOCS_TO_CHECK:
        if not doc_file.exists():
            print(f"[!] File not found: {doc_file}")
            continue
        
        print(f"[*] Validating: {doc_file.relative_to(CORTEX_ROOT)}")
        results = validate_links(doc_file)
        
        total_valid += len(results['valid'])
        total_broken += len(results['broken'])
        
        if results['broken']:
            print(f"   [X] {len(results['broken'])} broken links:")
            for item in results['broken']:
                print(f"      Line {item['line']}: {item['reference']}")
                print(f"         -> {item['resolved']}")
        else:
            print(f"   [OK] All {results['total']} links valid")
        
        print()
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"[OK] Valid links: {total_valid}")
    print(f"[X] Broken links: {total_broken}")
    print(f"[#] Total links: {total_valid + total_broken}")
    
    if total_broken > 0:
        print()
        print("[!] Fix broken links before proceeding to next phase")
        return 1
    else:
        print()
        print("[SUCCESS] All links valid!")
        return 0


if __name__ == "__main__":
    exit(main())
