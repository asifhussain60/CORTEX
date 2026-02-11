"""Conftest for vacuum enhancement tests - path configuration."""

import sys
from pathlib import Path

# Add cortex_brain to path
# Path: tests/unit/tier1/orchestrators/enhancements/conftest.py
# Need to go up 6 levels to project root: ../../../../../.. = /Users/asifhussain/PROJECTS/CORTEX
test_file = Path(__file__).resolve()
project_root = test_file.parent.parent.parent.parent.parent.parent
cortex_brain_path = project_root / "cortex_brain"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(cortex_brain_path.parent))
