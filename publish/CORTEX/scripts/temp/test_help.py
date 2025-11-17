#!/usr/bin/env python
"""Test CORTEX help command."""

import sys
from pathlib import Path

# Add CORTEX to path
sys.path.insert(0, str(Path(__file__).parent))

from src.operations import show_help

def main():
    """Display CORTEX help."""
    # Test table format
    print("\n" + "="*50)
    print("TESTING: TABLE FORMAT")
    print("="*50)
    help_text = show_help('table')
    
    # Write to file to avoid encoding issues
    output_file = Path(__file__).parent / 'HELP_OUTPUT.txt'
    output_file.write_text(help_text, encoding='utf-8')
    print(f"\nHelp text written to: {output_file}")
    print(f"Length: {len(help_text)} characters")
    
    # Also print to console (may have encoding issues on Windows)
    try:
        print("\n" + help_text)
    except UnicodeEncodeError:
        print("\n[Console encoding issue - see HELP_OUTPUT.txt for full output]")

if __name__ == '__main__':
    main()
