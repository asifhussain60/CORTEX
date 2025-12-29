#!/usr/bin/env python3
"""
Repair HTML files using BeautifulSoup's auto-repair capabilities.
"""

import sys
from pathlib import Path
from bs4 import BeautifulSoup

def repair_html_file(file_path):
    """Repair HTML file using BeautifulSoup."""
    print(f"Repairing: {file_path}")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse with BeautifulSoup (auto-repairs unclosed tags)
    soup = BeautifulSoup(content, 'html.parser')
    
    # Write back the repaired HTML
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    
    print(f"✅ Repaired: {file_path}")

def main():
    files_to_repair = [
        "docs/technical/orchestrators/cortex-lens.html",
        "docs/technical/orchestrators/intelligent-dashboard.html",
        "docs/technical/orchestrators/planning-system.html"
    ]
    
    base_path = Path(__file__).parent.parent
    
    for file_path in files_to_repair:
        full_path = base_path / file_path
        if full_path.exists():
            repair_html_file(full_path)
        else:
            print(f"❌ File not found: {full_path}")
    
    print("\n✅ All files repaired!")

if __name__ == "__main__":
    main()
