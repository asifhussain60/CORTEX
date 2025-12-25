#!/usr/bin/env python3
"""Check README completeness."""

import argparse
import sys
from pathlib import Path


def check_readme(readme_path: Path, required_sections: list) -> tuple[bool, str]:
    """Check if README contains required sections."""
    if not readme_path.exists():
        return False, f"❌ README not found: {readme_path}"
    
    with open(readme_path) as f:
        content = f.read()
    
    missing_sections = []
    for section in required_sections:
        # Check for section headers (case-insensitive)
        if f"## {section}" not in content and f"# {section}" not in content:
            missing_sections.append(section)
    
    messages = [
        f"📄 README Completeness Check:",
        f"  Required sections: {len(required_sections)}",
        f"  Missing sections: {len(missing_sections)}"
    ]
    
    if missing_sections:
        messages.append(f"\n⚠️  Missing sections:")
        for section in missing_sections:
            messages.append(f"    - {section}")
    
    passed = len(missing_sections) == 0
    
    if passed:
        messages.append(f"\n✅ README completeness: PASSED")
    else:
        messages.append(f"\n❌ README completeness: FAILED")
    
    return passed, "\n".join(messages)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--readme', type=Path, required=True)
    parser.add_argument('--required-sections', type=str, required=True,
                       help='Comma-separated list of required sections')
    args = parser.parse_args()
    
    sections = [s.strip() for s in args.required_sections.split(',')]
    passed, message = check_readme(args.readme, sections)
    print(message)
    sys.exit(0 if passed else 1)


if __name__ == '__main__':
    main()
