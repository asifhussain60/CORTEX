"""
cortex/common/file_utils.py

Unified file operation utilities.

AC-REM-002-04: Centralizes file I/O patterns across codebase.
Phase 53: Cross-platform support (Windows, macOS, Linux)
"""

import json
import os
import platform
import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Union

import yaml

# Cross-platform detection
IS_WINDOWS = platform.system() == "Windows"
IS_MACOS = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"


class FileOperations:
    """Centralized file operations utility.

    Provides consistent file I/O across the codebase with
    proper error handling and format support.

    Example:
        config = FileOperations.read_yaml(Path("config.yaml"))
        FileOperations.write_json(Path("output.json"), {"key": "value"})
    """

    @staticmethod
    def read_text(path: Union[str, Path], encoding: str = "utf-8") -> str:
        """Read text file content.

        Args:
            path: Path to file
            encoding: File encoding

        Returns:
            File content as string
        """
        path = Path(path)
        return path.read_text(encoding=encoding)

    @staticmethod
    def read_yaml(path: Union[str, Path]) -> Any:
        """Read and parse YAML file.

        Args:
            path: Path to YAML file

        Returns:
            Parsed YAML content
        """
        path = Path(path)
        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    @staticmethod
    def read_json(path: Union[str, Path]) -> Any:
        """Read and parse JSON file.

        Args:
            path: Path to JSON file

        Returns:
            Parsed JSON content
        """
        path = Path(path)
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def write_text(
        path: Union[str, Path],
        content: str,
        encoding: str = "utf-8",
    ) -> None:
        """Write text content to file.

        Args:
            path: Path to file
            content: Text content to write
            encoding: File encoding
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding=encoding)

    @staticmethod
    def write_yaml(
        path: Union[str, Path],
        data: Any,
        default_flow_style: bool = False,
    ) -> None:
        """Write data to YAML file.

        Args:
            path: Path to YAML file
            data: Data to serialize
            default_flow_style: YAML flow style option
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=default_flow_style)

    @staticmethod
    def write_json(
        path: Union[str, Path],
        data: Any,
        indent: int = 2,
    ) -> None:
        """Write data to JSON file.

        Args:
            path: Path to JSON file
            data: Data to serialize
            indent: JSON indentation
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent)

    @staticmethod
    def exists(path: Union[str, Path]) -> bool:
        """Check if path exists.

        Args:
            path: Path to check

        Returns:
            True if path exists
        """
        return Path(path).exists()

    @staticmethod
    def ensure_dir(path: Union[str, Path]) -> Path:
        """Ensure directory exists.

        Args:
            path: Directory path

        Returns:
            Path object for directory
        """
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def safe_delete(path: Union[str, Path]) -> bool:
        """Safely delete file or directory.

        Args:
            path: Path to delete

        Returns:
            True if deleted, False if didn't exist
        """
        path = Path(path)
        if not path.exists():
            return False

        if path.is_file():
            path.unlink()
        else:
            shutil.rmtree(path)

        return True

    @staticmethod
    def read_lines(
        path: Union[str, Path],
        encoding: str = "utf-8",
        strip: bool = True,
    ) -> List[str]:
        """Read file content as list of lines.

        Args:
            path: Path to file
            encoding: File encoding
            strip: If True, strip trailing newlines

        Returns:
            List of lines
        """
        path = Path(path)
        content = path.read_text(encoding=encoding)
        lines = content.splitlines()
        return lines

    @staticmethod
    def backup(
        path: Union[str, Path],
        suffix: str = ".bak",
    ) -> Optional[Path]:
        """Create backup of file.

        Args:
            path: Path to file to backup
            suffix: Backup file suffix

        Returns:
            Path to backup file, or None if source doesn't exist
        """
        path = Path(path)
        if not path.exists():
            return None

        backup_path = path.with_suffix(path.suffix + suffix)
        shutil.copy2(path, backup_path)
        return backup_path


@contextmanager
def atomic_write(
    path: Union[str, Path],
    mode: str = "w",
    encoding: str = "utf-8",
) -> Generator[Any, None, None]:
    """Context manager for atomic file writes.

    Writes to a temp file then moves to target on success.
    Cleans up temp file on failure.

    Args:
        path: Target file path
        mode: File mode ('w' or 'wb')
        encoding: File encoding (for text mode)

    Yields:
        File object for writing

    Example:
        with atomic_write("config.yaml") as f:
            yaml.dump(config, f)
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Create temp file in same directory for atomic rename
    fd, temp_path = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.stem}_",
        suffix=path.suffix,
    )
    temp_path = Path(temp_path)

    try:
        os.close(fd)

        if "b" in mode:
            f = temp_path.open(mode)
        else:
            f = temp_path.open(mode, encoding=encoding)

        try:
            yield f
        finally:
            f.close()

        # Atomic rename (may need to remove target on Windows)
        if path.exists():
            path.unlink()
        temp_path.rename(path)

    except Exception:
        # Clean up temp file on failure
        if temp_path.exists():
            temp_path.unlink()
        raise


def get_venv_python_path(use_vscode_variable: bool = True) -> str:
    """
    Get cross-platform Python executable path in virtual environment.
    
    Args:
        use_vscode_variable: If True, return VS Code-compatible path using 
            ${workspaceFolder} variable for portability. If False, return 
            relative path from current directory.
    
    Returns:
        str: Cross-platform Python path
    
    Examples:
        >>> get_venv_python_path(use_vscode_variable=True)  # Windows
        '${workspaceFolder}/.venv/Scripts/python.exe'
        >>> get_venv_python_path(use_vscode_variable=True)  # macOS/Linux
        '${workspaceFolder}/.venv/bin/python'
        >>> get_venv_python_path(use_vscode_variable=False)  # Windows
        '.venv/Scripts/python.exe'
    """
    if use_vscode_variable:
        base = "${workspaceFolder}"
    else:
        base = "."
    
    if IS_WINDOWS:
        return f"{base}/.venv/Scripts/python.exe"
    else:
        return f"{base}/.venv/bin/python"


def get_absolute_venv_python(workspace_folder: Union[str, Path] = ".") -> Path:
    """
    Get absolute path to Python executable in virtual environment.
    
    Args:
        workspace_folder: Workspace root directory (default: current directory)
    
    Returns:
        Path: Absolute path to Python executable
    
    Raises:
        FileNotFoundError: If virtual environment doesn't exist
        
    Examples:
        >>> get_absolute_venv_python()  # Windows
        WindowsPath('D:/PROJECTS/CORTEX/.venv/Scripts/python.exe')
    """
    workspace = Path(workspace_folder).resolve()
    
    if IS_WINDOWS:
        candidates = [
            workspace / ".venv" / "Scripts" / "python.exe",
            workspace / ".venv" / "Scripts" / "python",
        ]
    else:
        candidates = [
            workspace / ".venv" / "bin" / "python",
            workspace / ".venv" / "bin" / "python3",
        ]
    
    for candidate in candidates:
        if candidate.exists():
            return candidate
    
    raise FileNotFoundError(
        f"Virtual environment Python not found in {workspace}. "
        f"Tried: {[str(c) for c in candidates]}"
    )


def normalize_path_separators(path: str) -> str:
    """
    Normalize path separators for current platform.
    
    Args:
        path: Path with mixed separators
    
    Returns:
        str: Path with platform-appropriate separators
        
    Examples:
        >>> normalize_path_separators('path/to/file')  # Windows
        'path\\to\\file'
        >>> normalize_path_separators('path\\to\\file')  # macOS/Linux
        'path/to/file'
    """
    if IS_WINDOWS:
        return path.replace('/', '\\')
    else:
        return path.replace('\\', '/')
