"""Conftest for vacuum enhancement tests - path configuration."""

import sys
from pathlib import Path

# Add cortex_brain to path
cortex_brain_path = Path(__file__).parent.parent.parent / "cortex_brain"
sys.path.insert(0, str(cortex_brain_path))
