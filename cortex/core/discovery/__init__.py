"""Discovery modules for service and version management."""

from cortex.core.discovery.mcp_discovery import (
    HealthCheck,
    PromptVersionConfig,
    ServiceDiscovery,
)

__all__ = ["HealthCheck", "ServiceDiscovery", "PromptVersionConfig"]
