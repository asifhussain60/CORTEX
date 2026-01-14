#!/usr/bin/env python3
"""
VS Code Cache Cleaner CLI Wrapper
Quick invocation: python3 clear-vscode-cache.py

Usage:
    python3 clear-vscode-cache.py              # Clean cache
    python3 clear-vscode-cache.py --dry-run   # Show what would be cleaned
    python3 clear-vscode-cache.py --json       # Output as JSON
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from tools.vscode_cache_cleaner import main

if __name__ == "__main__":
    main()
