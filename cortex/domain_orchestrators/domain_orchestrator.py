"""Domain Orchestrator

Author: CORTEX Framework
"""

from dataclasses import dataclass, field
from typing import Dict

@dataclass
class DomainRegistry:
    """Domain registry."""
    domains: Dict[str, str] = field(default_factory=dict)

__all__ = ["DomainRegistry"]
