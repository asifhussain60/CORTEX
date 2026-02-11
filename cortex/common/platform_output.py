"""
Windows CP1252 Encoding Compatibility Layer (ENH-054 P0)

Provides ASCII-only output for Windows environments where CP1252 encoding
doesn't support emoji characters. Automatically detects platform and falls
back to ASCII equivalents.

Authority: Production Readiness | Windows-First Compatibility
Created: 2026-02-11
"""

import logging
import platform
import sys
from enum import Enum
from typing import Dict, Optional

# AC_START: AC-ENH054-001
# Description: Windows CP1252 encoding compatibility layer
# Requirements: ASCII fallback for emoji, platform detection, consistent logging


class OutputLevel(Enum):
    """Output severity levels with ASCII fallbacks"""
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    CRITICAL = "CRITICAL"
    FIX = "FIX"
    START = "START"
    COMPLETE = "COMPLETE"


class PlatformOutputFormatter:
    """
    Platform-aware output formatter with emoji/ASCII fallback.
    
    Automatically detects Windows CP1252 and uses ASCII-only output.
    On macOS/Linux with UTF-8, uses emoji for better readability.
    
    Usage:
        formatter = PlatformOutputFormatter()
        print(formatter.success("Operation completed"))
        print(formatter.error("Failed to process"))
    """
    
    # Emoji mappings for UTF-8 environments
    _EMOJI_MAP: Dict[OutputLevel, str] = {
        OutputLevel.SUCCESS: "✅",
        OutputLevel.ERROR: "❌",
        OutputLevel.WARNING: "⚠️",
        OutputLevel.INFO: "ℹ️",
        OutputLevel.CRITICAL: "🔴",
        OutputLevel.FIX: "🔧",
        OutputLevel.START: "🚀",
        OutputLevel.COMPLETE: "🎯",
    }
    
    # ASCII fallbacks for CP1252/restricted environments
    _ASCII_MAP: Dict[OutputLevel, str] = {
        OutputLevel.SUCCESS: "[OK]",
        OutputLevel.ERROR: "[FAIL]",
        OutputLevel.WARNING: "[WARN]",
        OutputLevel.INFO: "[INFO]",
        OutputLevel.CRITICAL: "[CRIT]",
        OutputLevel.FIX: "[FIX]",
        OutputLevel.START: "[START]",
        OutputLevel.COMPLETE: "[DONE]",
    }
    
    def __init__(self, force_ascii: Optional[bool] = None):
        """
        Initialize formatter with platform detection.
        
        Args:
            force_ascii: If True, always use ASCII. If False, always use emoji.
                        If None (default), auto-detect based on platform.
        """
        if force_ascii is None:
            self.use_ascii = self._should_use_ascii()
        else:
            self.use_ascii = force_ascii
        
        self.logger = logging.getLogger(__name__)
    
    def _should_use_ascii(self) -> bool:
        """
        Detect if ASCII-only output should be used.
        
        Returns:
            True if ASCII required (Windows CP1252), False otherwise
        """
        # Check platform
        if platform.system() == "Windows":
            # Windows typically uses CP1252 which doesn't support emoji
            try:
                # Check stdout encoding
                encoding = sys.stdout.encoding
                if encoding is None:
                    # Unknown encoding on Windows, use ASCII for safety
                    return True
                if "cp1252" in encoding.lower() or "windows" in encoding.lower():
                    return True
            except (AttributeError, TypeError):
                # If encoding detection fails on Windows, assume CP1252
                return True
        
        # macOS/Linux with UTF-8 support emoji
        return False
    
    def _format_with_icon(self, level: OutputLevel, message: str) -> str:
        """
        Format message with appropriate icon.
        
        Args:
            level: Output severity level
            message: Message text
            
        Returns:
            Formatted message with icon prefix
        """
        if self.use_ascii:
            icon = self._ASCII_MAP[level]
        else:
            icon = self._EMOJI_MAP[level]
        
        return f"{icon} {message}"
    
    def success(self, message: str) -> str:
        """Format success message"""
        return self._format_with_icon(OutputLevel.SUCCESS, message)
    
    def error(self, message: str) -> str:
        """Format error message"""
        return self._format_with_icon(OutputLevel.ERROR, message)
    
    def warning(self, message: str) -> str:
        """Format warning message"""
        return self._format_with_icon(OutputLevel.WARNING, message)
    
    def info(self, message: str) -> str:
        """Format info message"""
        return self._format_with_icon(OutputLevel.INFO, message)
    
    def critical(self, message: str) -> str:
        """Format critical message"""
        return self._format_with_icon(OutputLevel.CRITICAL, message)
    
    def fix(self, message: str) -> str:
        """Format fix/action message"""
        return self._format_with_icon(OutputLevel.FIX, message)
    
    def start(self, message: str) -> str:
        """Format start/launch message"""
        return self._format_with_icon(OutputLevel.START, message)
    
    def complete(self, message: str) -> str:
        """Format completion message"""
        return self._format_with_icon(OutputLevel.COMPLETE, message)
    
    def get_encoding_info(self) -> Dict[str, str]:
        """
        Get current encoding information for debugging.
        
        Returns:
            Dict with platform, encoding, and mode details
        """
        return {
            "platform": platform.system(),
            "stdout_encoding": sys.stdout.encoding or "unknown",
            "mode": "ASCII" if self.use_ascii else "UTF-8",
            "reason": "Windows CP1252 detected" if self.use_ascii else "UTF-8 support available"
        }


# Global singleton instance for convenience
_DEFAULT_FORMATTER = PlatformOutputFormatter()


def success(message: str) -> str:
    """Format success message (module-level convenience)"""
    return _DEFAULT_FORMATTER.success(message)


def error(message: str) -> str:
    """Format error message (module-level convenience)"""
    return _DEFAULT_FORMATTER.error(message)


def warning(message: str) -> str:
    """Format warning message (module-level convenience)"""
    return _DEFAULT_FORMATTER.warning(message)


def info(message: str) -> str:
    """Format info message (module-level convenience)"""
    return _DEFAULT_FORMATTER.info(message)


def critical(message: str) -> str:
    """Format critical message (module-level convenience)"""
    return _DEFAULT_FORMATTER.critical(message)


def fix(message: str) -> str:
    """Format fix message (module-level convenience)"""
    return _DEFAULT_FORMATTER.fix(message)


def start(message: str) -> str:
    """Format start message (module-level convenience)"""
    return _DEFAULT_FORMATTER.start(message)


def complete(message: str) -> str:
    """Format completion message (module-level convenience)"""
    return _DEFAULT_FORMATTER.complete(message)


def get_default_formatter() -> PlatformOutputFormatter:
    """Get the global default formatter instance"""
    return _DEFAULT_FORMATTER


# AC_COMPLETE: AC-ENH054-001 [OK] Platform-aware output formatting
# Windows CP1252: ASCII fallback [OK]
# UTF-8 environments: Emoji support [OK]
# Auto-detection: Platform-based [OK]
