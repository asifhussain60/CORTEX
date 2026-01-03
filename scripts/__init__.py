"""
scripts package - CORTEX CLI utilities and orchestrators.

Provides import aliases for hyphenated script names.
"""

# Import alias for cortex-cli.py (hyphenated filename, importable as cortex_cli)
import importlib.util
import sys
from pathlib import Path

# Load cortex-cli.py as cortex_cli module
_cli_path = Path(__file__).parent / "cortex-cli.py"
_spec = importlib.util.spec_from_file_location("scripts.cortex_cli", _cli_path)
cortex_cli = importlib.util.module_from_spec(_spec)
sys.modules["scripts.cortex_cli"] = cortex_cli
_spec.loader.exec_module(cortex_cli)

__all__ = ["cortex_cli"]
