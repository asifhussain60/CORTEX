#!/usr/bin/env python3
"""
CORTEX MCP Setup — Redirect to canonical setup script.

CORE-035: Single canonical implementation.
The canonical MCP setup script lives at: .cortex/setup-mcp.py

This file exists for backward compatibility. It delegates to the
canonical script to avoid duplication.

Usage:
    python scripts/setup-mcp.py          → Runs .cortex/setup-mcp.py
    python .cortex/setup-mcp.py          → Canonical (preferred)
    python .cortex/setup-mcp.py --cleanup → Remove competing MCP servers
"""

import os
import sys
import subprocess
from pathlib import Path


def main():
    """Redirect to canonical .cortex/setup-mcp.py."""
    # Find workspace root (this script is in scripts/)
    script_dir = Path(__file__).resolve().parent
    workspace_root = script_dir.parent
    canonical = workspace_root / ".cortex" / "setup-mcp.py"

    if not canonical.exists():
        print(f"❌ Canonical setup script not found: {canonical}")
        print("   Expected at: .cortex/setup-mcp.py")
        sys.exit(1)

    print(f"ℹ️  Redirecting to canonical: .cortex/setup-mcp.py")
    print(f"   (CORE-035: Single canonical implementation)\n")

    # Forward all arguments
    result = subprocess.run(
        [sys.executable, str(canonical)] + sys.argv[1:],
        cwd=str(workspace_root)
    )
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()