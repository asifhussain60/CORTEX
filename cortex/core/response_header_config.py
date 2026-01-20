"""Response Header Configuration Manager.

Manages configuration for response headers including formatting, inclusion rules,
and domain-specific header mappings.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class HeaderFormat(Enum):
    """Header format types."""

    JSON = "json"
    XML = "xml"
    PLAIN = "plain"
    CUSTOM = "custom"


@dataclass
class HeaderConfiguration:
    """Configuration for response headers.

    Attributes:
        format: Header format type.
        include_timestamp: Whether to include timestamp.
        include_execution_time: Whether to include execution time.
        include_version: Whether to include version.
        include_trace_id: Whether to include trace ID.
        custom_headers: Custom header configurations.
        domain_mappings: Domain-specific header mappings.
    """

    format: HeaderFormat = HeaderFormat.JSON
    include_timestamp: bool = True
    include_execution_time: bool = True
    include_version: bool = True
    include_trace_id: bool = True
    custom_headers: Dict[str, str] = field(default_factory=dict)
    domain_mappings: Dict[str, Dict[str, Any]] = field(default_factory=dict)


class HeaderConfigurationManager:
    """Manages response header configuration."""

    def __init__(self) -> None:
        """Initialize configuration manager."""
        self.default_config = HeaderConfiguration()
        self.domain_configs: Dict[str, HeaderConfiguration] = {}

    def get_configuration(self, domain: Optional[str] = None) -> HeaderConfiguration:
        """Get configuration for a domain.

        Args:
            domain: Domain name (uses default if None).

        Returns:
            HeaderConfiguration for the domain.
        """
        if domain and domain in self.domain_configs:
            return self.domain_configs[domain]
        return self.default_config

    def set_configuration(
        self, config: HeaderConfiguration, domain: Optional[str] = None
    ) -> None:
        """Set configuration for a domain.

        Args:
            config: HeaderConfiguration to set.
            domain: Domain name (uses default if None).
        """
        if domain:
            self.domain_configs[domain] = config
        else:
            self.default_config = config

    def update_configuration(
        self, updates: Dict[str, Any], domain: Optional[str] = None
    ) -> None:
        """Update configuration with partial changes.

        Args:
            updates: Dictionary of updates.
            domain: Domain name (uses default if None).
        """
        config = self.get_configuration(domain)

        for key, value in updates.items():
            if hasattr(config, key):
                setattr(config, key, value)

    def add_custom_header(
        self, header_name: str, header_value: str, domain: Optional[str] = None
    ) -> None:
        """Add a custom header.

        Args:
            header_name: Header name.
            header_value: Header value.
            domain: Domain name (uses default if None).
        """
        config = self.get_configuration(domain)
        config.custom_headers[header_name] = header_value

    def add_domain_mapping(
        self, domain: str, mapping_key: str, mapping_value: Any
    ) -> None:
        """Add a domain-specific mapping.

        Args:
            domain: Domain name.
            mapping_key: Mapping key.
            mapping_value: Mapping value.
        """
        config = self.get_configuration(domain)
        config.domain_mappings[mapping_key] = mapping_value

    def format_headers(
        self, headers: Dict[str, Any], domain: Optional[str] = None
    ) -> str:
        """Format headers according to configuration.

        Args:
            headers: Headers dictionary.
            domain: Domain name (uses default if None).

        Returns:
            Formatted headers string.
        """
        config = self.get_configuration(domain)

        if config.format == HeaderFormat.JSON:
            import json
            return json.dumps(headers, indent=2)
        elif config.format == HeaderFormat.PLAIN:
            lines = [f"{k}: {v}" for k, v in headers.items()]
            return "\n".join(lines)
        else:
            return str(headers)


# Global instance
_global_config_manager: Optional[HeaderConfigurationManager] = None


def get_header_config_manager() -> HeaderConfigurationManager:
    """Get global header configuration manager.

    Returns:
        HeaderConfigurationManager singleton.
    """
    global _global_config_manager
    if _global_config_manager is None:
        _global_config_manager = HeaderConfigurationManager()
    return _global_config_manager


__all__ = [
    "HeaderConfigurationManager",
    "HeaderConfiguration",
    "HeaderFormat",
    "get_header_config_manager",
    "HeaderConfigLoader",
]

# Stub for test compatibility
class HeaderConfigLoader:
    """Load header configurations."""
    def __init__(self):
        self.configs = {}
    
    def load(self, config_path):
        return {}