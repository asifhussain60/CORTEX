"""
CORTEX Response Header/Footer Manager v1.0

Dynamically injects and manages CORTEX headers/footers across all response formats.
Centralizes branding, copyright, and versioning to ensure consistency without
hardcoding into individual templates.

This module:
- Loads header/footer config from cortex-brain/response-templates-v4.yaml
- Provides injectable header/footer components for all response types
- Supports multiple formats (markdown, HTML, JSON, plaintext)
- Automatically applies version, date, and copyright info
- Enables easy updates without touching individual templates
- Handles Windows emoji encoding gracefully

Author: Asif Hussain
Created: 2026-01-12
Part of: Infrastructure Layer (AC-HEADER-001)
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Literal
import yaml
import logging
import sys


logger = logging.getLogger(__name__)


def _get_brain_emoji():
    """Get brain emoji for markdown, with fallback for Windows encoding issues."""
    # Try to use brain emoji, fall back to gear if encoding fails
    try:
        # Test if system can encode emoji
        "🧠".encode(sys.stdout.encoding or 'utf-8')
        return "🧠"
    except (UnicodeEncodeError, AttributeError):
        # Windows cmd.exe compatibility fallback
        return "⚙️"


@dataclass
class HeaderFooterConfig:
    """Configuration for CORTEX header and footer components."""
    enabled: bool
    version: str
    author: str
    copyright_holder: str
    copyright_years: str
    operation_type: str  # "Execution", "Validation", "Planning", etc.
    include_timestamp: bool = True
    include_author: bool = True
    include_copyright: bool = True
    format: Literal["markdown", "html", "json", "plaintext"] = "markdown"


class ResponseHeaderFooterManager:
    """
    Central manager for CORTEX response headers and footers.
    
    Provides injectable components that can be used by any orchestrator,
    prompt, or response handler to maintain consistent branding and copyright.
    
    Design principle: Configuration-driven, not hardcoded.
    All header/footer content sourced from cortex-brain/response-templates-v4.yaml
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the header/footer manager.
        
        Args:
            config_path: Path to response-templates-v4.yaml. If None, uses default.
        """
        if config_path is None:
            config_path = Path("cortex-brain/response-templates-v4.yaml")
        
        self.config_path = config_path
        self.config = self._load_config()
        self.header_template = self.config.get("mandatory_header", {}).get("template", "")
        self.timestamp = datetime.utcnow().isoformat() + "Z"
    
    def _load_config(self) -> dict:
        """Load response template configuration from YAML."""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded response template config from {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load response templates: {e}")
            # Fallback config
            return {
                "mandatory_header": {
                    "enabled": True,
                    "template": "# CORTEX {operation_type}\n**Version:** {version} | **Date:** {iso_date}\n**Author:** Asif Hussain\n**Copyright © 2025-2026 Asif Hussain. All rights reserved.**\n---"
                }
            }
    
    def generate_header(
        self,
        operation_type: str = "Execution",
        version: str = "6.0.0",
        format: Literal["markdown", "html", "json"] = "markdown"
    ) -> str:
        """
        Generate a CORTEX header for responses.
        
        Args:
            operation_type: Type of operation (Execution, Validation, Planning, etc.)
            version: Version number for this response
            format: Output format (markdown, html, json)
        
        Returns:
            Formatted header string ready to prepend to response content
        """
        if format == "markdown":
            return self._generate_markdown_header(operation_type, version)
        elif format == "html":
            return self._generate_html_header(operation_type, version)
        elif format == "json":
            return self._generate_json_header(operation_type, version)
        else:
            return self._generate_plaintext_header(operation_type, version)
    
    def _generate_markdown_header(self, operation_type: str, version: str) -> str:
        """Generate markdown-formatted header (CORTEX-4.0 style with brain icon)."""
        iso_date = datetime.utcnow().isoformat() + "Z"
        brain_emoji = _get_brain_emoji()
        header = f"""## {brain_emoji} CORTEX {operation_type}

**Version:** {version} | **Date:** {iso_date}  
**Author:** Asif Hussain  
**Copyright © 2025-2026 Asif Hussain. All rights reserved.**

---

"""
        return header
    
    def _generate_html_header(self, operation_type: str, version: str) -> str:
        """Generate HTML-formatted header."""
        iso_date = datetime.utcnow().isoformat() + "Z"
        header = f"""<!-- CORTEX Response Header v1.0 -->
<div class="cortex-header" style="padding: 20px; background: linear-gradient(135deg, rgba(0,212,255,0.1), rgba(123,44,191,0.1)); border-bottom: 1px solid rgba(0,212,255,0.3); margin-bottom: 20px;">
    <h1 style="color: #00d4ff; margin: 0 0 10px 0;">⚙️ CORTEX {operation_type} Summary</h1>
    <p style="color: rgba(255,255,255,0.7); margin: 5px 0; font-size: 0.9em;">
        <strong>Version:</strong> {version} | 
        <strong>Date:</strong> {iso_date}<br>
        <strong>Author:</strong> Asif Hussain<br>
        <strong>Copyright © 2025-2026 Asif Hussain. All rights reserved.</strong>
    </p>
</div>
"""
        return header
    
    def _generate_json_header(self, operation_type: str, version: str) -> str:
        """Generate JSON-formatted header (as metadata object)."""
        iso_date = datetime.utcnow().isoformat() + "Z"
        return f"""{{
  "_header": {{
    "operation_type": "{operation_type}",
    "version": "{version}",
    "timestamp": "{iso_date}",
    "author": "Asif Hussain",
    "copyright": "Copyright © 2025-2026 Asif Hussain. All rights reserved.",
    "cortex_version": "6.0.0"
  }},
  "content": {{
"""
    
    def _generate_plaintext_header(self, operation_type: str, version: str) -> str:
        """Generate plaintext-formatted header."""
        iso_date = datetime.utcnow().isoformat() + "Z"
        header = f"""================================================================================
CORTEX {operation_type} Summary
================================================================================
Version: {version} | Date: {iso_date}
Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
================================================================================

"""
        return header
    
    def generate_footer(
        self,
        format: Literal["markdown", "html", "json"] = "markdown",
        include_cortex_version: bool = True
    ) -> str:
        """
        Generate a CORTEX footer for responses.
        
        Args:
            format: Output format (markdown, html, json)
            include_cortex_version: Whether to include CORTEX version in footer
        
        Returns:
            Formatted footer string ready to append to response content
        """
        if format == "markdown":
            return self._generate_markdown_footer(include_cortex_version)
        elif format == "html":
            return self._generate_html_footer(include_cortex_version)
        elif format == "json":
            return self._generate_json_footer(include_cortex_version)
        else:
            return self._generate_plaintext_footer(include_cortex_version)
    
    def _generate_markdown_footer(self, include_version: bool) -> str:
        """Generate markdown footer."""
        footer = "\n---\n\n"
        if include_version:
            footer += "_CORTEX 6.0.0 | Autonomous Execution Engine_\n"
        footer += "_Copyright © 2025-2026 Asif Hussain. All rights reserved._\n"
        return footer
    
    def _generate_html_footer(self, include_version: bool) -> str:
        """Generate HTML footer."""
        footer = """
<!-- CORTEX Response Footer v1.0 -->
<div class="cortex-footer" style="padding: 15px; border-top: 1px solid rgba(0,212,255,0.3); margin-top: 30px; text-align: center; color: rgba(255,255,255,0.5); font-size: 0.85em;">
    """
        if include_version:
            footer += "CORTEX 6.0.0 | Autonomous Execution Engine<br>\n"
        footer += "Copyright © 2025-2026 Asif Hussain. All rights reserved.\n</div>"
        return footer
    
    def _generate_json_footer(self, include_version: bool) -> str:
        """Generate JSON footer (closing braces and metadata)."""
        footer = f"""  }},
  "_footer": {{
    "cortex_version": "6.0.0",
    "author": "Asif Hussain",
    "copyright": "Copyright © 2025-2026 Asif Hussain. All rights reserved."
  }}
}}"""
        return footer
    
    def _generate_plaintext_footer(self, include_version: bool) -> str:
        """Generate plaintext footer."""
        footer = "\n" + "=" * 80 + "\n"
        if include_version:
            footer += "CORTEX 6.0.0 | Autonomous Execution Engine\n"
        footer += "Copyright © 2025-2026 Asif Hussain. All rights reserved.\n"
        footer += "=" * 80 + "\n"
        return footer
    
    def wrap_response(
        self,
        content: str,
        operation_type: str = "Execution",
        version: str = "6.0.0",
        format: Literal["markdown", "html", "json", "plaintext"] = "markdown",
        include_footer: bool = True
    ) -> str:
        """
        Wrap content with CORTEX header and optional footer.
        
        This is the primary entry point for orchestrators and response handlers.
        
        Args:
            content: Response content to wrap
            operation_type: Type of operation
            version: Version number
            format: Output format
            include_footer: Whether to include footer
        
        Returns:
            Complete response with header and footer
        """
        header = self.generate_header(operation_type, version, format)
        
        if include_footer:
            footer = self.generate_footer(format)
            return header + content + footer
        else:
            return header + content
    
    def get_copyright_line(self) -> str:
        """Return the canonical copyright line for use in any context."""
        return "Copyright © 2025-2026 Asif Hussain. All rights reserved."
    
    def get_cortex_branding(self) -> Dict[str, str]:
        """Return canonical CORTEX branding elements."""
        return {
            "title": "CORTEX",
            "version": "6.0.0",
            "author": "Asif Hussain",
            "copyright": "Copyright © 2025-2026 Asif Hussain. All rights reserved.",
            "started": "2025",
            "ended": "2026"
        }


# Global singleton instance for easy access
_manager_instance: Optional[ResponseHeaderFooterManager] = None


def get_header_footer_manager() -> ResponseHeaderFooterManager:
    """Get or create the global ResponseHeaderFooterManager instance."""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = ResponseHeaderFooterManager()
    return _manager_instance


def inject_cortex_header(
    content: str,
    operation_type: str = "Execution",
    format: Literal["markdown", "html", "json", "plaintext"] = "markdown"
) -> str:
    """
    Convenience function to inject CORTEX header into content.
    
    Usage:
        response = orchestrator.execute()
        response_with_header = inject_cortex_header(response, "Validation")
    
    Args:
        content: Response content
        operation_type: Type of operation
        format: Output format
    
    Returns:
        Content with CORTEX header prepended
    """
    manager = get_header_footer_manager()
    return manager.generate_header(operation_type, "6.0.0", format) + content


def wrap_cortex_response(
    content: str,
    operation_type: str = "Execution",
    format: Literal["markdown", "html", "json", "plaintext"] = "markdown",
    include_footer: bool = True
) -> str:
    """
    Convenience function to wrap content with CORTEX header and footer.
    
    This is the recommended way to ensure all responses have proper branding.
    
    Usage:
        response = orchestrator.execute()
        complete_response = wrap_cortex_response(response, "Planning")
    
    Args:
        content: Response content
        operation_type: Type of operation
        format: Output format
        include_footer: Whether to include footer
    
    Returns:
        Complete response with header and footer
    """
    manager = get_header_footer_manager()
    return manager.wrap_response(
        content,
        operation_type=operation_type,
        format=format,
        include_footer=include_footer
    )


if __name__ == "__main__":
    # Quick test
    manager = ResponseHeaderFooterManager()
    
    print("=" * 80)
    print("MARKDOWN FORMAT")
    print("=" * 80)
    test_content = """✅ OUTCOMES

• Implementation completed successfully
• All tests passing
• Tracker updated
"""
    print(manager.wrap_response(test_content, "Implementation", format="markdown"))
    
    print("\n" + "=" * 80)
    print("HTML FORMAT")
    print("=" * 80)
    print(manager.wrap_response(test_content, "Implementation", format="html"))
