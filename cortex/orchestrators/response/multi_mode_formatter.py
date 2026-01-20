"""Multi-Mode Formatter

Author: CORTEX Framework
"""

from dataclasses import dataclass

@dataclass
class FormattingProfile:
    """Formatting profile."""
    profile_id: str
    format_type: str = "markdown"

__all__ = ["FormattingProfile"]
