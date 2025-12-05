"""
Module Guide Validator

Validates all module guide references in CORTEX documentation.

Checks:
- Extract all guide references from markdown
- Check file existence in .github/prompts/modules/
- Report missing guides

Usage:
    python scripts/validate_module_guides.py

Author: Asif Hussain
"""

import re
from pathlib import Path
from typing import List, Dict

CORTEX_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = CORTEX_ROOT / ".github" / "prompts" / "modules"
DOCS_TO_CHECK = [
    CORTEX_ROOT / ".github" / "copilot-instructions.md",
    CORTEX_ROOT / ".github" / "prompts" / "CORTEX.prompt.md"
]


def extract_guide_references(content: str) -> List[str]:
    """Extract all module guide references."""
    guides = set()
    
    # Pattern 1: modules/guide-name.md
    for match in re.finditer(r'modules/([a-z0-9\-]+\.md)', content):
        guides.add(match.group(1))
    
    # Pattern 2: .github/prompts/modules/guide-name.md
    for match in re.finditer(r'\.github/prompts/modules/([a-z0-9\-]+\.md)', content):
        guides.add(match.group(1))
    
    # Pattern 3: **Guide:** `.github/prompts/modules/guide-name.md`
    for match in re.finditer(r'\*\*Guide:\*\*[^`]*`[^`]*modules/([a-z0-9\-]+\.md)`', content):
        guides.add(match.group(1))
    
    return sorted(guides)


def validate_guides() -> Dict[str, List]:
    """Validate all guide references."""
    results = {
        'found': [],
        'missing': [],
        'total': 0
    }
    
    all_guides = set()
    
    # Extract guides from all docs
    for doc_file in DOCS_TO_CHECK:
        if doc_file.exists():
            content = doc_file.read_text(encoding='utf-8')
            guides = extract_guide_references(content)
            all_guides.update(guides)
    
    results['total'] = len(all_guides)
    
    # Check existence
    for guide in all_guides:
        guide_path = MODULES_DIR / guide
        
        if guide_path.exists():
            results['found'].append(guide)
        else:
            results['missing'].append(guide)
    
    return results


def main():
    """Run module guide validation."""
    print("=" * 80)
    print("CORTEX Module Guide Validator")
    print("=" * 80)
    print()
    
    print(f"[*] Modules directory: {MODULES_DIR.relative_to(CORTEX_ROOT)}")
    print()
    
    results = validate_guides()
    
    print(f"[#] Total guides referenced: {results['total']}")
    print(f"[OK] Found: {len(results['found'])}")
    print(f"[X] Missing: {len(results['missing'])}")
    print()
    
    if results['missing']:
        print("Missing guides:")
        for guide in results['missing']:
            print(f"   [X] {guide}")
            print(f"      Expected at: {MODULES_DIR / guide}")
        print()
        print("[!] Create missing guides or update references")
        return 1
    else:
        print("[OK] All module guides exist!")
        
        if results['found']:
            print()
            print("Found guides:")
            for guide in results['found'][:10]:  # Show first 10
                print(f"   [OK] {guide}")
            if len(results['found']) > 10:
                print(f"   ... and {len(results['found']) - 10} more")
        
        return 0


if __name__ == "__main__":
    exit(main())
