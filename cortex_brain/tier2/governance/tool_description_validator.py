"""Tier2 Governance: Tool Description Validator

STUB IMPLEMENTATION - To be completed in Phase E.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass


@dataclass
class ToolDescription:
    """Tool description."""
    tool_id: str
    name: str
    description: str
    parameters: list = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = []


@dataclass
class ToolDescriptionValidator:
    """Validate tool descriptions."""
    strict_mode: bool = True
    
    def validate(self, description: str) -> bool:
        return True


__all__ = ["ToolDescription", "ToolDescriptionValidator"]
