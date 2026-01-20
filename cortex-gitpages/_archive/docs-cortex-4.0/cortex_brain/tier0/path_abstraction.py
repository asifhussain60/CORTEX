"""
PathAbstraction - Portable Path Abstraction Layer (AC-BRITTLE-002)

This module provides a unified, cross-platform path abstraction layer that replaces
os.path operations with a consistent interface across Windows, macOS, and Linux.

Key Features:
- Cross-platform path normalization (Windows/POSIX separators)
- Pathlib-compatible interface with additional utilities
- Thread-safe path operations
- Support for absolute and relative paths
- Package-aware path resolution
- Comprehensive error handling

Classes:
- PathAbstraction: Main facade for all path operations
- PathStrategy: Abstract base for platform-specific implementations
- PosixPathStrategy: Unix/Linux/macOS path handling
- WindowsPathStrategy: Windows path handling
- UniversalPathStrategy: Smart cross-platform handling

Design Patterns:
- Strategy Pattern: Platform-specific implementations
- Facade Pattern: Unified interface hiding complexity
- Builder Pattern: Fluent API for path operations
"""

from pathlib import Path, PureWindowsPath, PurePosixPath, PurePath
from typing import Optional, List, Union, Tuple, Any
from abc import ABC, abstractmethod
import os
import sys
from threading import RLock
import logging


# Configure logging
logger = logging.getLogger(__name__)


class PathStrategy(ABC):
    """Abstract base class for platform-specific path strategies."""

    @abstractmethod
    def normalize(self, path_str: str) -> str:
        """Normalize path for the platform.
        
        Args:
            path_str: Raw path string to normalize
            
        Returns:
            Normalized path string
        """
        pass

    @abstractmethod
    def join(self, *parts: str) -> str:
        """Join path parts correctly for the platform.
        
        Args:
            parts: Path components to join
            
        Returns:
            Joined path string
        """
        pass

    @abstractmethod
    def resolve(self, path_str: str) -> str:
        """Resolve path to absolute form.
        
        Args:
            path_str: Path to resolve
            
        Returns:
            Resolved absolute path
        """
        pass

    @abstractmethod
    def is_absolute(self, path_str: str) -> bool:
        """Check if path is absolute.
        
        Args:
            path_str: Path to check
            
        Returns:
            True if path is absolute
        """
        pass


class PosixPathStrategy(PathStrategy):
    """POSIX (Unix/Linux/macOS) path strategy implementation."""

    def normalize(self, path_str: str) -> str:
        """Normalize POSIX path.
        
        Args:
            path_str: Raw path string
            
        Returns:
            Normalized path with consistent separators and resolved . and ..
        """
        # Convert to PurePath for normalization
        pure_path = PurePosixPath(path_str)
        normalized = str(pure_path)
        # Remove trailing slash unless it's root
        if normalized != "/" and normalized.endswith("/"):
            normalized = normalized.rstrip("/")
        return normalized

    def join(self, *parts: str) -> str:
        """Join path parts using POSIX separators.
        
        Args:
            parts: Path components to join
            
        Returns:
            Joined path string
        """
        pure_path = PurePosixPath(parts[0]) if parts else PurePosixPath()
        for part in parts[1:]:
            pure_path = pure_path / part
        return str(pure_path)

    def resolve(self, path_str: str) -> str:
        """Resolve path to absolute form on POSIX system.
        
        Args:
            path_str: Path to resolve
            
        Returns:
            Absolute path string
        """
        path = Path(path_str)
        try:
            resolved = path.resolve()
            return str(resolved)
        except (OSError, RuntimeError):
            # If resolve fails, try absolute path conversion
            if path.is_absolute():
                return str(path)
            return str(Path.cwd() / path)

    def is_absolute(self, path_str: str) -> bool:
        """Check if path is absolute on POSIX system.
        
        Args:
            path_str: Path to check
            
        Returns:
            True if path starts with /
        """
        return path_str.startswith("/")


class WindowsPathStrategy(PathStrategy):
    """Windows path strategy implementation."""

    def normalize(self, path_str: str) -> str:
        """Normalize Windows path.
        
        Args:
            path_str: Raw path string (may contain mixed separators)
            
        Returns:
            Normalized path with consistent Windows separators
        """
        # Convert to PureWindowsPath for normalization
        pure_path = PureWindowsPath(path_str)
        normalized = str(pure_path)
        # Remove trailing slash unless it's root or UNC root
        if len(normalized) > 3 and normalized.endswith("\\"):
            normalized = normalized.rstrip("\\")
        return normalized

    def join(self, *parts: str) -> str:
        """Join path parts using Windows separators.
        
        Args:
            parts: Path components to join
            
        Returns:
            Joined path string with Windows separators
        """
        pure_path = PureWindowsPath(parts[0]) if parts else PureWindowsPath()
        for part in parts[1:]:
            pure_path = pure_path / part
        return str(pure_path)

    def resolve(self, path_str: str) -> str:
        """Resolve path to absolute form on Windows system.
        
        Args:
            path_str: Path to resolve
            
        Returns:
            Absolute path string
        """
        path = Path(path_str)
        try:
            resolved = path.resolve()
            return str(resolved)
        except (OSError, RuntimeError):
            if path.is_absolute():
                return str(path)
            return str(Path.cwd() / path)

    def is_absolute(self, path_str: str) -> bool:
        """Check if path is absolute on Windows system.
        
        Args:
            path_str: Path to check
            
        Returns:
            True if path has drive letter or UNC root
        """
        pure_path = PureWindowsPath(path_str)
        return pure_path.is_absolute()


class UniversalPathStrategy(PathStrategy):
    """Universal cross-platform path strategy that adapts to the current OS."""

    def __init__(self) -> None:
        """Initialize with appropriate strategy for current OS."""
        if sys.platform == "win32":
            self._strategy: PathStrategy = WindowsPathStrategy()
        else:
            self._strategy = PosixPathStrategy()

    def normalize(self, path_str: str) -> str:
        """Normalize path using current OS strategy.
        
        Args:
            path_str: Raw path string
            
        Returns:
            Normalized path
        """
        return self._strategy.normalize(path_str)

    def join(self, *parts: str) -> str:
        """Join path parts using current OS strategy.
        
        Args:
            parts: Path components
            
        Returns:
            Joined path
        """
        return self._strategy.join(*parts)

    def resolve(self, path_str: str) -> str:
        """Resolve path using current OS strategy.
        
        Args:
            path_str: Path to resolve
            
        Returns:
            Absolute path
        """
        return self._strategy.resolve(path_str)

    def is_absolute(self, path_str: str) -> bool:
        """Check if path is absolute using current OS strategy.
        
        Args:
            path_str: Path to check
            
        Returns:
            True if path is absolute
        """
        return self._strategy.is_absolute(path_str)


class PathAbstraction:
    """Unified path abstraction layer for cross-platform path operations.
    
    This class provides a consistent interface for path operations across
    Windows, macOS, and Linux platforms. It wraps pathlib.Path with
    additional utilities and ensures consistent behavior.
    
    Attributes:
        _path: Internal Path object
        _strategy: Platform-specific path strategy
        _lock: Thread-safety lock
    """

    _global_lock = RLock()

    def __init__(self, path: Union[str, Path, 'PathAbstraction']) -> None:
        """Initialize PathAbstraction with a path.
        
        Args:
            path: String path, pathlib.Path object, or another PathAbstraction
            
        Raises:
            ValueError: If path is None or empty
        """
        with self._global_lock:
            if isinstance(path, PathAbstraction):
                self._path = path._path
            elif isinstance(path, Path):
                self._path = path
            else:
                if not path:
                    raise ValueError("Path cannot be empty")
                self._path = Path(path)
            
            self._strategy = UniversalPathStrategy()
            logger.debug(f"Created PathAbstraction for: {self._path}")

    def __str__(self) -> str:
        """Return string representation of the path.
        
        Returns:
            Path as string
        """
        return str(self._path)

    def __repr__(self) -> str:
        """Return detailed representation.
        
        Returns:
            Detailed string representation
        """
        return f"PathAbstraction({str(self._path)!r})"

    def __eq__(self, other: Any) -> bool:
        """Check equality with another PathAbstraction or path-like object.
        
        Args:
            other: Object to compare
            
        Returns:
            True if paths are equal
        """
        if isinstance(other, PathAbstraction):
            return self._path == other._path
        elif isinstance(other, (Path, str)):
            return self._path == Path(other)
        return False

    def __truediv__(self, other: str) -> 'PathAbstraction':
        """Support / operator for path joining.
        
        Args:
            other: Path component to append
            
        Returns:
            New PathAbstraction with joined path
        """
        return self.join(other)

    def join(self, *parts: str) -> 'PathAbstraction':
        """Join path components.
        
        Args:
            parts: Path components to join
            
        Returns:
            New PathAbstraction with joined path
        """
        with self._global_lock:
            joined_str = self._strategy.join(str(self._path), *parts)
            return PathAbstraction(joined_str)

    def normalize(self) -> 'PathAbstraction':
        """Normalize the path by resolving . and .. components.
        
        Returns:
            New PathAbstraction with normalized path
        """
        with self._global_lock:
            normalized = self._strategy.normalize(str(self._path))
            return PathAbstraction(normalized)

    def resolve(self) -> 'PathAbstraction':
        """Resolve the path to absolute form.
        
        Returns:
            New PathAbstraction with absolute path
        """
        with self._global_lock:
            resolved = self._strategy.resolve(str(self._path))
            return PathAbstraction(resolved)

    def parent(self) -> 'PathAbstraction':
        """Get the parent directory.
        
        Returns:
            New PathAbstraction for parent directory
        """
        with self._global_lock:
            return PathAbstraction(self._path.parent)

    def name(self) -> str:
        """Get the filename component (last part of path).
        
        Returns:
            Filename as string
        """
        with self._global_lock:
            return self._path.name

    def stem(self) -> str:
        """Get filename without extension.
        
        Returns:
            Filename stem
        """
        with self._global_lock:
            return self._path.stem

    def suffix(self) -> str:
        """Get file extension.
        
        Returns:
            File extension including dot (e.g., '.py')
        """
        with self._global_lock:
            return self._path.suffix

    def suffixes(self) -> List[str]:
        """Get all file extensions.
        
        Returns:
            List of all extensions (e.g., ['.tar', '.gz'])
        """
        with self._global_lock:
            return self._path.suffixes

    def parts(self) -> Tuple[str, ...]:
        """Get all path components.
        
        Returns:
            Tuple of path parts
        """
        with self._global_lock:
            return self._path.parts

    def exists(self) -> bool:
        """Check if path exists in file system.
        
        Returns:
            True if path exists
        """
        with self._global_lock:
            try:
                return self._path.exists()
            except (OSError, ValueError):
                return False

    def is_file(self) -> bool:
        """Check if path points to a regular file.
        
        Returns:
            True if path is a file
        """
        with self._global_lock:
            try:
                return self._path.is_file()
            except (OSError, ValueError):
                return False

    def is_dir(self) -> bool:
        """Check if path points to a directory.
        
        Returns:
            True if path is a directory
        """
        with self._global_lock:
            try:
                return self._path.is_dir()
            except (OSError, ValueError):
                return False

    def is_symlink(self) -> bool:
        """Check if path points to a symbolic link.
        
        Returns:
            True if path is a symlink
        """
        with self._global_lock:
            try:
                return self._path.is_symlink()
            except (OSError, ValueError):
                return False

    def is_absolute(self) -> bool:
        """Check if path is absolute.
        
        Returns:
            True if path is absolute
        """
        with self._global_lock:
            return self._strategy.is_absolute(str(self._path))

    def relative_to(self, other: Union['PathAbstraction', Path, str]) -> 'PathAbstraction':
        """Compute the relative path from other to self.
        
        Args:
            other: Base path to compute relative path from
            
        Returns:
            New PathAbstraction with relative path
            
        Raises:
            ValueError: If paths are not relative to each other
        """
        with self._global_lock:
            if isinstance(other, PathAbstraction):
                other_path = other._path
            elif isinstance(other, Path):
                other_path = other
            else:
                other_path = Path(other)
            
            relative = self._path.relative_to(other_path)
            return PathAbstraction(relative)

    def with_name(self, name: str) -> 'PathAbstraction':
        """Return path with filename changed.
        
        Args:
            name: New filename
            
        Returns:
            New PathAbstraction with changed filename
        """
        with self._global_lock:
            return PathAbstraction(self._path.with_name(name))

    def with_stem(self, stem: str) -> 'PathAbstraction':
        """Return path with stem (filename without extension) changed.
        
        Args:
            stem: New stem
            
        Returns:
            New PathAbstraction with changed stem
        """
        with self._global_lock:
            return PathAbstraction(self._path.with_stem(stem))

    def with_suffix(self, suffix: str) -> 'PathAbstraction':
        """Return path with extension changed.
        
        Args:
            suffix: New extension (including dot, e.g., '.py')
            
        Returns:
            New PathAbstraction with changed suffix
        """
        with self._global_lock:
            return PathAbstraction(self._path.with_suffix(suffix))

    def iterdir(self) -> List['PathAbstraction']:
        """List directory contents.
        
        Returns:
            List of PathAbstraction objects for directory contents
            
        Raises:
            NotADirectoryError: If path is not a directory
        """
        with self._global_lock:
            if not self.is_dir():
                raise NotADirectoryError(f"{self._path} is not a directory")
            
            return [PathAbstraction(p) for p in self._path.iterdir()]

    def read_text(self, encoding: str = "utf-8") -> str:
        """Read text file contents.
        
        Args:
            encoding: File encoding (default: utf-8)
            
        Returns:
            File contents as string
        """
        with self._global_lock:
            return self._path.read_text(encoding=encoding)

    def write_text(self, data: str, encoding: str = "utf-8") -> int:
        """Write text to file.
        
        Args:
            data: Text content to write
            encoding: File encoding (default: utf-8)
            
        Returns:
            Number of characters written
        """
        with self._global_lock:
            return self._path.write_text(data, encoding=encoding)

    def mkdir(self, parents: bool = False, exist_ok: bool = False) -> None:
        """Create directory.
        
        Args:
            parents: If True, create parent directories as needed
            exist_ok: If True, don't raise error if directory exists
        """
        with self._global_lock:
            self._path.mkdir(parents=parents, exist_ok=exist_ok)

    def unlink(self, missing_ok: bool = False) -> None:
        """Delete file.
        
        Args:
            missing_ok: If True, don't raise error if file doesn't exist
        """
        with self._global_lock:
            self._path.unlink(missing_ok=missing_ok)

    def rmdir(self) -> None:
        """Remove empty directory.
        
        Raises:
            OSError: If directory is not empty
        """
        with self._global_lock:
            self._path.rmdir()

    def as_posix(self) -> str:
        """Return path with forward slashes (POSIX style).
        
        Returns:
            Path string with forward slashes
        """
        with self._global_lock:
            return self._path.as_posix()

    def as_uri(self) -> str:
        """Return path as a file URI.
        
        Returns:
            File URI representation
        """
        with self._global_lock:
            return self._path.as_uri()

    def stat(self) -> Any:
        """Get file statistics.
        
        Returns:
            os.stat_result object
        """
        with self._global_lock:
            return self._path.stat()

    def touch(self, exist_ok: bool = True) -> None:
        """Create an empty file or update its timestamp.
        
        Args:
            exist_ok: If True, don't raise error if file exists
        """
        with self._global_lock:
            self._path.touch(exist_ok=exist_ok)

    def glob(self, pattern: str) -> List['PathAbstraction']:
        """Match path components against pattern.
        
        Args:
            pattern: Glob pattern
            
        Returns:
            List of matching paths as PathAbstraction objects
        """
        with self._global_lock:
            return [PathAbstraction(p) for p in self._path.glob(pattern)]

    def rglob(self, pattern: str) -> List['PathAbstraction']:
        """Recursive glob pattern matching.
        
        Args:
            pattern: Glob pattern
            
        Returns:
            List of matching paths as PathAbstraction objects
        """
        with self._global_lock:
            return [PathAbstraction(p) for p in self._path.rglob(pattern)]
