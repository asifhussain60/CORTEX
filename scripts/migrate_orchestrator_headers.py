#!/usr/bin/env python3
"""
AC-TEMPLATE-006: Orchestrator Header Migration
Migrate all orchestrator prompts to CORE-026 compliant headers
"""

from pathlib import Path
import re
from datetime import datetime

def migrate_header(prompt_file: Path) -> bool:
    """Add or fix CORE-026 header in prompt file."""
    content = prompt_file.read_text()
    
    # Check if already compliant
    has_all = all([
        re.search(r'^\*\*Purpose:\*\*', content, re.MULTILINE),
        re.search(r'^\*\*Version:\*\*', content, re.MULTILINE),
        re.search(r'^\*\*Date:\*\*', content, re.MULTILINE),
        re.search(r'^\*\*Governance:\*\*', content, re.MULTILINE),
        re.search(r'\*\*Copyright.*All rights reserved', content)
    ])
    
    if has_all:
        return False  # Already compliant
    
    # Extract existing header elements
    purpose_match = re.search(r'^\*\*Purpose:\*\* (.+)$', content, re.MULTILINE)
    version_match = re.search(r'^\*\*Version:\*\* (.+)$', content, re.MULTILINE)
    date_match = re.search(r'^\*\*Date:\*\* (.+)$', content, re.MULTILINE)
    governance_match = re.search(r'^\*\*Governance:\*\* (.+)$', content, re.MULTILINE)
    
    # Build compliant header
    header_lines = []
    
    if purpose_match:
        header_lines.append(f"**Purpose:** {purpose_match.group(1)}")
    else:
        header_lines.append(f"**Purpose:** {prompt_file.stem.replace('-', ' ').title()}")
    
    if version_match:
        header_lines.append(f"**Version:** {version_match.group(1)}")
    else:
        header_lines.append("**Version:** 1.0.0")
    
    if date_match:
        header_lines.append(f"**Date:** {date_match.group(1)}")
    else:
        header_lines.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}")
    
    if governance_match:
        header_lines.append(f"**Governance:** {governance_match.group(1)}")
    else:
        header_lines.append("**Governance:** CORE-002, CORE-009, CORE-017")
    
    header_lines.append("**Copyright © 2025-2026 Asif Hussain. All rights reserved.**")
    
    # Insert header at top of file (after title if present)
    lines = content.split('\n')
    insert_pos = 0
    
    # Skip title line if present
    if lines[0].startswith('#'):
        insert_pos = 1
        while insert_pos < len(lines) and not lines[insert_pos].strip():
            insert_pos += 1
    
    # Insert header
    new_content = '\n'.join(lines[:insert_pos] + [''] + header_lines + [''] + lines[insert_pos:])
    
    # Write back
    prompt_file.write_text(new_content)
    return True

def main():
    """Migrate all orchestrator prompts to CORE-026 headers."""
    prompt_dir = Path('.github/prompts')
    prompt_files = list(prompt_dir.glob('*.prompt.md'))
    
    migrated = []
    skipped = []
    
    for prompt_file in prompt_files:
        if migrate_header(prompt_file):
            migrated.append(prompt_file.name)
        else:
            skipped.append(prompt_file.name)
    
    print(f"✅ AC-TEMPLATE-006 Migration Complete")
    print(f"   Migrated: {len(migrated)} prompts")
    print(f"   Skipped (already compliant): {len(skipped)}")
    
    if migrated:
        print(f"\n📝 Migrated files:")
        for f in migrated:
            print(f"   • {f}")

if __name__ == "__main__":
    main()
