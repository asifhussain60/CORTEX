"""Blue-Green Deployment

Author: CORTEX Framework
"""

from dataclasses import dataclass

@dataclass
class Deployment:
    """Deployment configuration."""
    deployment_id: str
    environment: str = "blue"
    status: str = "pending"

__all__ = ["Deployment"]
