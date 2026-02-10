"""
Phase 67: .NET Roslyn Deep Intelligence

Semantic analysis layer for .NET codebases using Microsoft Roslyn.

AC_START: AC-PHASE67-S1-INIT-001
"""

from pathlib import Path
from typing import Optional

__version__ = "0.1.0"
__phase__ = "phase-67"
__stage__ = "S1"

# Module-level configuration
DEFAULT_ROSLYN_CLI_PATH: Optional[Path] = None


def configure_roslyn_cli(cli_path: Path) -> None:
    """
    Configure path to Roslyn CLI analyzer tool.
    
    Args:
        cli_path: Path to RoslynAnalyzerCLI.exe or dotnet DLL
    """
    global DEFAULT_ROSLYN_CLI_PATH
    DEFAULT_ROSLYN_CLI_PATH = cli_path


# AC_COMPLETE: AC-PHASE67-S1-INIT-001 ✅ Module initialized
