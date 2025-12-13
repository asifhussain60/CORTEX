"""
Path translation utilities for cross-machine compatibility.

Handles conversion between Windows and Unix path formats.
"""

from pathlib import Path
from typing import Optional


class PathTranslator:
    """Utility for translating paths between Windows and Unix formats."""
    
    @staticmethod
    def is_windows_absolute(path: str) -> bool:
        """Check if path is Windows absolute (C:\\ format)."""
        return len(path) > 2 and path[1] == ":"
    
    @staticmethod
    def is_unix_absolute(path: str) -> bool:
        """Check if path is Unix absolute (/ format)."""
        return path.startswith("/")
    
    @staticmethod
    def is_unc_path(path: str) -> bool:
        """Check if path is UNC network path (\\\\server\\share)."""
        return path.startswith("\\\\\\\\")
    
    @staticmethod
    def translate(path: str, target_os: str) -> str:
        """
        Translate path between Windows and Unix formats.
        
        Args:
            path: Path to translate
            target_os: Target OS ("Windows" or "Unix")
            
        Returns:
            Translated path
        """
        is_windows_abs = PathTranslator.is_windows_absolute(path)
        is_unix_abs = PathTranslator.is_unix_absolute(path)
        is_relative = not is_windows_abs and not is_unix_abs and not path.startswith("~")
        
        # Handle relative paths - preserve them
        if is_relative:
            return PathTranslator._translate_relative(path, target_os)
        
        # Expand home directory
        if path.startswith("~"):
            path = str(Path(path).expanduser())
            is_windows_abs = PathTranslator.is_windows_absolute(path)
            is_unix_abs = PathTranslator.is_unix_absolute(path)
        
        # Handle UNC paths
        if PathTranslator.is_unc_path(path):
            return PathTranslator._translate_unc(path, target_os)
        
        # Windows to Unix
        if target_os == "Unix":
            return PathTranslator._windows_to_unix(path, is_windows_abs)
        
        # Unix to Windows
        if target_os == "Windows":
            return PathTranslator._unix_to_windows(path, is_unix_abs)
        
        return path
    
    @staticmethod
    def _translate_relative(path: str, target_os: str) -> str:
        """Translate relative path (separator conversion only)."""
        if target_os == "Windows":
            return path.replace("/", "\\")
        else:
            return path.replace("\\", "/")
    
    @staticmethod
    def _translate_unc(path: str, target_os: str) -> str:
        """Translate UNC network path."""
        if target_os == "Unix":
            parts = path.replace("\\", "/").split("/")
            return "/" + "/".join(p for p in parts if p)
        return path
    
    @staticmethod
    def _windows_to_unix(path: str, is_absolute: bool) -> str:
        """Convert Windows path to Unix format."""
        if is_absolute:
            drive = path[0].lower()
            rest = path[3:].replace("\\", "/")
            return f"/{drive}/{rest}"
        return path.replace("\\", "/")
    
    @staticmethod
    def _unix_to_windows(path: str, is_absolute: bool) -> str:
        """Convert Unix path to Windows format."""
        if is_absolute and len(path) > 2 and path[2] == "/":
            # /c/Projects -> C:\Projects
            drive = path[1].upper()
            rest = path[3:].replace("/", "\\")
            return f"{drive}:\\{rest}"
        # Generic Unix path - use C: as fallback
        return "C:\\" + path[1:].replace("/", "\\")
