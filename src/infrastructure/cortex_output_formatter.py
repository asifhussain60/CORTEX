#!/usr/bin/env python3
"""
CORTEX Global Response Formatter

Ensures ALL responses - error messages, status updates, and regular output -
go through the header/footer wrapping system.

This module provides a unified output interface that guarantees consistency.

Root cause fix: Direct print() calls bypass wrap_cortex_response().
Solution: Provide a global output interface that always wraps responses.
"""

import sys
from pathlib import Path
from typing import Optional, Literal
from datetime import datetime


class CORTEXOutputFormatter:
    """
    Unified output formatter for all CORTEX responses.
    
    Ensures that every piece of output - whether error, status, or regular response -
    includes the mandatory CORTEX header with brain icon and author info.
    
    Design: Singleton pattern to ensure consistent state across application.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.suppress_header = False  # Can be disabled for internal logging
        self.output_format = "markdown"
    
    def _get_brain_emoji(self) -> str:
        """Get brain emoji with fallback for encoding issues."""
        try:
            "🧠".encode(sys.stdout.encoding or 'utf-8')
            return "🧠"
        except (UnicodeEncodeError, AttributeError):
            return "⚙️"
    
    def format_output(
        self,
        content: str,
        operation_type: str = "Execution",
        format_type: str = "markdown",
        include_footer: bool = True,
        include_header: bool = True
    ) -> str:
        """
        Format content with CORTEX header and footer.
        
        This is the unified method that ALL responses should use.
        """
        if not content:
            content = "[No output]"
        
        if not include_header:
            return content
        
        try:
            # Import here to avoid circular imports
            from src.infrastructure.response_header_footer_manager import (
                wrap_cortex_response
            )
            return wrap_cortex_response(
                content,
                operation_type=operation_type,
                format=format_type,
                include_footer=include_footer
            )
        except ImportError:
            # Fallback: Simple header if manager unavailable
            brain = self._get_brain_emoji()
            iso_date = datetime.utcnow().isoformat() + "Z"
            return f"""## {brain} CORTEX {operation_type}

**Version:** 6.0.0 | **Date:** {iso_date}  
**Author:** Asif Hussain  
**Copyright © 2025-2026 Asif Hussain. All rights reserved.**

---

{content}"""
    
    def print(
        self,
        content: str,
        operation_type: str = "Execution",
        format_type: str = "markdown",
        include_header: bool = True,
        include_footer: bool = True
    ):
        """Print content with guaranteed CORTEX header."""
        formatted = self.format_output(
            content,
            operation_type=operation_type,
            format_type=format_type,
            include_header=include_header,
            include_footer=include_footer
        )
        print(formatted)
    
    def print_error(self, error_message: str, operation_type: str = "Error"):
        """Print error with CORTEX header."""
        formatted_error = f"❌ {error_message}"
        self.print(
            formatted_error,
            operation_type=operation_type,
            include_header=True,
            include_footer=False
        )
    
    def print_status(self, status_message: str, operation_type: str = "Status"):
        """Print status with CORTEX header."""
        formatted_status = f"ℹ️ {status_message}"
        self.print(
            formatted_status,
            operation_type=operation_type,
            include_header=True,
            include_footer=False
        )
    
    def print_success(self, success_message: str, operation_type: str = "Success"):
        """Print success with CORTEX header."""
        formatted_success = f"✅ {success_message}"
        self.print(
            formatted_success,
            operation_type=operation_type,
            include_header=True,
            include_footer=False
        )


# Global singleton instance
_formatter = None


def get_cortex_output_formatter() -> CORTEXOutputFormatter:
    """Get the global CORTEX output formatter instance."""
    global _formatter
    if _formatter is None:
        _formatter = CORTEXOutputFormatter()
    return _formatter


def cortex_print(
    content: str,
    operation_type: str = "Execution",
    format_type: str = "markdown",
    include_header: bool = True,
    include_footer: bool = True
):
    """
    Print CORTEX-formatted output.
    
    Usage:
        cortex_print("Task completed successfully")
        cortex_print(error_msg, operation_type="Error")
        cortex_print(status, include_footer=False)
    """
    formatter = get_cortex_output_formatter()
    formatter.print(
        content,
        operation_type=operation_type,
        format_type=format_type,
        include_header=include_header,
        include_footer=include_footer
    )


def cortex_format(
    content: str,
    operation_type: str = "Execution",
    format_type: str = "markdown",
    include_header: bool = True,
    include_footer: bool = True
) -> str:
    """
    Format content with CORTEX header without printing.
    
    Usage:
        formatted = cortex_format("Response content")
        print(formatted)
    """
    formatter = get_cortex_output_formatter()
    return formatter.format_output(
        content,
        operation_type=operation_type,
        format_type=format_type,
        include_header=include_header,
        include_footer=include_footer
    )
