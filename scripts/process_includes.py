"""
Include Processor for CORTEX Documentation

Processes {{include: path}} directives in markdown files.

Usage:
    python scripts/process_includes.py <input_file> [output_file]
    
    If output_file is omitted, changes are made in-place.

Example:
    # In documentation file
    {{include: .github/prompts/includes/response-format-template.md}}
    
    # Process
    python scripts/process_includes.py .github/copilot-instructions.md

Author: Asif Hussain
"""

import re
import sys
from pathlib import Path
from typing import Tuple

CORTEX_ROOT = Path(__file__).resolve().parents[1]


def process_includes(content: str, source_file: Path) -> Tuple[str, int]:
    """
    Process {{include: path}} directives in content.
    
    Returns:
        Tuple of (processed_content, include_count)
    """
    include_pattern = r'\{\{include:\s*([^\}]+)\}\}'
    include_count = 0
    
    def replace_include(match):
        nonlocal include_count
        include_path = match.group(1).strip()
        
        # Resolve path relative to source file
        if include_path.startswith('.github/') or include_path.startswith('cortex-brain/'):
            full_path = CORTEX_ROOT / include_path
        else:
            full_path = (source_file.parent / include_path).resolve()
        
        if not full_path.exists():
            print(f"[!] Include not found: {include_path}")
            print(f"    Resolved to: {full_path}")
            return match.group(0)  # Return original if file not found
        
        # Read and return included content
        try:
            included_content = full_path.read_text(encoding='utf-8')
            # Strip leading/trailing whitespace but preserve internal formatting
            included_content = included_content.strip()
            include_count += 1
            print(f"[OK] Included: {include_path}")
            return included_content
        except Exception as e:
            print(f"[!] Error reading {include_path}: {e}")
            return match.group(0)
    
    processed = re.sub(include_pattern, replace_include, content)
    return processed, include_count


def main():
    """Process includes in a markdown file."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/process_includes.py <input_file> [output_file]")
        return 1
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else input_file
    
    if not input_file.exists():
        print(f"[!] Input file not found: {input_file}")
        return 1
    
    print("=" * 80)
    print("CORTEX Include Processor")
    print("=" * 80)
    print(f"[*] Input: {input_file}")
    print(f"[*] Output: {output_file}")
    print()
    
    # Read input
    content = input_file.read_text(encoding='utf-8')
    
    # Process includes
    processed, count = process_includes(content, input_file)
    
    if count == 0:
        print("[*] No includes found")
        return 0
    
    # Write output
    output_file.write_text(processed, encoding='utf-8')
    print()
    print(f"[OK] Processed {count} includes")
    print(f"[OK] Output written to: {output_file}")
    
    return 0


if __name__ == "__main__":
    exit(main())
