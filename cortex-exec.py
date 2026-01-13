#!/usr/bin/env python3
"""
CORTEX Execution Agent CLI
Quick wrapper for cortex_execution_agent.py

Usage:
    python3 cortex-exec.py status       # Show current status
    python3 cortex-exec.py validate     # Validate evidence
    python3 cortex-exec.py sync         # Sync dashboard
    python3 cortex-exec.py continue     # Execute autonomous loop
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from agents.cortex_execution_agent import main

if __name__ == "__main__":
    main()
