"""
Phase 67: .NET Roslyn Deep Intelligence

Semantic analysis layer for .NET codebases using Microsoft Roslyn.

AC_START: AC-PHASE67-S1-INIT-001
"""

from pathlib import Path
from typing import Optional
import os

__version__ = "0.1.0"
__phase__ = "phase-67"
__stage__ = "S1"

# Module-level configuration - auto-detect Roslyn CLI path
def _get_default_roslyn_cli_path() -> Path:
    """Auto-detect Roslyn CLI project path."""
    module_dir = Path(__file__).parent
    roslyn_cli_project = module_dir / "roslyn_cli" / "RoslynAnalyzerCLI.csproj"
    return roslyn_cli_project

DEFAULT_ROSLYN_CLI_PATH: Path = _get_default_roslyn_cli_path()


def configure_roslyn_cli(cli_path: Path) -> None:
    """
    Configure path to Roslyn CLI analyzer tool.
    
    Args:
        cli_path: Path to RoslynAnalyzerCLI.exe or dotnet DLL
    """
    global DEFAULT_ROSLYN_CLI_PATH
    DEFAULT_ROSLYN_CLI_PATH = cli_path


# AC_COMPLETE: AC-PHASE67-S1-INIT-001 ✅ Module initialized
