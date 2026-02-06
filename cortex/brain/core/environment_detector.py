"""
Environment Detection Layer.

Detects execution environment (MCP Server, Copilot, Development) and configures
appropriate tool adapters for dual-mode architecture.

Authority: Phase 33 - Architecture Alignment & Mandatory Governance Enforcement
CORE-008: TDD-first architecture
CORE-011: Type hints mandatory
CORE-012: Google-style docstrings

Implements graceful degradation: MCP (primary) → Copilot (fallback) → Development
"""

import os
import sys
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any
from pathlib import Path

import logging

logger = logging.getLogger(__name__)


class EnvironmentType(Enum):
    """Enumeration of supported execution environments."""

    MCP_SERVER = "mcp_server"          # Production: MCP server mode
    COPILOT = "copilot"                # Development: VS Code Copilot
    DEVELOPMENT = "development"        # Local: Python scripts/CLI


@dataclass
class EnvironmentConfig:
    """Runtime configuration for detected environment."""

    environment_type: EnvironmentType
    is_mcp_available: bool
    is_copilot_available: bool
    is_development: bool
    cortex_root: Path
    tool_adapter_class: str  # Qualified class name (e.g., 'cortex.brain.core.tool_adapter.MCPToolAdapter')
    
    def __str__(self) -> str:
        """Return human-readable environment description."""
        env_names = {
            EnvironmentType.MCP_SERVER: "MCP Server (Production)",
            EnvironmentType.COPILOT: "VS Code Copilot (Development)",
            EnvironmentType.DEVELOPMENT: "Local Development",
        }
        return env_names.get(self.environment_type, "Unknown")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Dict representation suitable for JSON serialization
        """
        return {
            "environment_type": self.environment_type.value,
            "mcp_available": self.is_mcp_available,
            "copilot_available": self.is_copilot_available,
            "is_development": self.is_development,
            "cortex_root": str(self.cortex_root),
            "adapter_type": self.tool_adapter_class.split(".")[-1]  # Class name only
        }


class EnvironmentDetector:
    """
    Detects execution environment and configures tool adapters.

    Strategy:
    1. Check if running as MCP server (environment variables + module availability)
    2. Check if VS Code Copilot is available (VS Code extension context)
    3. Fall back to local development mode

    Precedence: MCP_SERVER > COPILOT > DEVELOPMENT
    """

    def __init__(self) -> None:
        """Initialize environment detector."""
        self.cortex_root = self._find_cortex_root()
        self._cached_environment: Optional[EnvironmentConfig] = None

    @staticmethod
    def _find_cortex_root() -> Path:
        """
        Locate CORTEX project root directory.

        Searches up from current file until finding cortex/__init__.py

        Returns:
            Path to CORTEX root directory

        Raises:
            RuntimeError: If CORTEX root not found
        """
        current = Path(__file__).resolve()
        for parent in current.parents:
            if (parent / "cortex" / "__init__.py").exists():
                return parent

        raise RuntimeError(
            "Could not find CORTEX root directory. "
            f"Started from: {current}"
        )

    def detect_environment(self) -> EnvironmentType:
        """
        Detect current execution environment.

        Uses cached result if available (don't re-detect on every call).

        Returns:
            EnvironmentType enum value
        """
        if self._cached_environment is not None:
            return self._cached_environment.environment_type

        # Check MCP server first (highest priority)
        if self._is_mcp_server():
            logger.info("🔍 Environment: MCP Server (production)")
            return EnvironmentType.MCP_SERVER

        # Check Copilot second
        if self._is_copilot():
            logger.info("🔍 Environment: VS Code Copilot (development)")
            return EnvironmentType.COPILOT

        # Default to development
        logger.info("🔍 Environment: Local Development")
        return EnvironmentType.DEVELOPMENT

    def _is_mcp_server(self) -> bool:
        """
        Check if running as MCP server.

        Indicators:
        - CORTEX_MCP_SERVER env var set
        - cortex/mcp/server.py importable
        - stdio available for IPC
        """
        # Check environment variable
        if os.getenv("CORTEX_MCP_SERVER") == "true":
            logger.debug("MCP detected: CORTEX_MCP_SERVER=true")
            return True

        # Check if MCP server module is available
        try:
            from cortex.mcp import server as _  # noqa: F401
            logger.debug("MCP detected: cortex.mcp.server importable")
            return True
        except ImportError:
            pass

        return False

    def _is_copilot(self) -> bool:
        """
        Check if running in VS Code Copilot environment.

        Indicators:
        - VS_CODE_COPILOT env var set
        - VS Code IPC mechanism available
        - Copilot extension context variables present
        """
        # Check environment variable
        if os.getenv("VS_CODE_COPILOT") == "true":
            logger.debug("Copilot detected: VS_CODE_COPILOT=true")
            return True

        # Check for VS Code environment
        if os.getenv("TERM_PROGRAM") == "vscode":
            logger.debug("Copilot detected: VS Code environment")
            return True

        # Check VS Code API availability (would be set by extension)
        if os.getenv("VSCODE_IPC") is not None:
            logger.debug("Copilot detected: VSCODE_IPC available")
            return True

        return False

    def get_environment_config(self) -> EnvironmentConfig:
        """
        Get complete environment configuration.

        Caches result after first call.

        Returns:
            EnvironmentConfig with all detection results
        """
        if self._cached_environment is not None:
            return self._cached_environment

        # Detect components
        is_mcp = self._is_mcp_server()
        is_copilot = self._is_copilot()
        is_dev = not (is_mcp or is_copilot)

        # Select environment type
        if is_mcp:
            env_type = EnvironmentType.MCP_SERVER
            adapter_class = "cortex.brain.core.tool_adapter.MCPToolAdapter"
        elif is_copilot:
            env_type = EnvironmentType.COPILOT
            adapter_class = "cortex.brain.core.tool_adapter.CopilotToolAdapter"
        else:
            env_type = EnvironmentType.DEVELOPMENT
            adapter_class = "cortex.brain.core.tool_adapter.DevelopmentToolAdapter"

        config = EnvironmentConfig(
            environment_type=env_type,
            is_mcp_available=is_mcp,
            is_copilot_available=is_copilot,
            is_development=is_dev,
            cortex_root=self.cortex_root,
            tool_adapter_class=adapter_class,
        )

        self._cached_environment = config
        logger.info(
            f"Environment configured: {config} "
            f"(adapter: {adapter_class})"
        )

        return config

    def get_tool_adapter(self) -> "ToolAdapter":  # noqa: F821
        """
        Get configured tool adapter for current environment.

        Returns:
            ToolAdapter instance (MCPToolAdapter, CopilotToolAdapter, or DevelopmentToolAdapter)

        Raises:
            RuntimeError: If tool adapter cannot be imported
        """
        config = self.get_environment_config()

        # Import adapter class dynamically
        try:
            module_path, class_name = config.tool_adapter_class.rsplit(".", 1)
            module = __import__(module_path, fromlist=[class_name])
            adapter_class = getattr(module, class_name)
            adapter = adapter_class()
            logger.debug(f"Initialized tool adapter: {class_name}")
            return adapter
        except (ImportError, AttributeError) as e:
            logger.error(
                f"Failed to import tool adapter {config.tool_adapter_class}: {e}"
            )
            raise RuntimeError(
                f"Cannot instantiate tool adapter: {config.tool_adapter_class}"
            ) from e

    def is_production(self) -> bool:
        """
        Check if running in production environment (MCP server).

        Returns:
            True if MCP server, False otherwise
        """
        config = self.get_environment_config()
        return config.environment_type == EnvironmentType.MCP_SERVER
    
    def is_mcp_available(self) -> bool:
        """
        Public wrapper to check if MCP tools are available.
        
        Returns:
            True if MCP server environment detected
        """
        return self._is_mcp_server()
    
    def is_copilot_available(self) -> bool:
        """
        Public wrapper to check if Copilot tools are available.
        
        Returns:
            True if Copilot environment detected
        """
        return self._is_copilot()

    def is_development(self) -> bool:
        """
        Check if running in development environment (Copilot or local).

        Returns:
            True if development-mode environment, False if production
        """
        config = self.get_environment_config()
        return config.environment_type in (
            EnvironmentType.COPILOT,
            EnvironmentType.DEVELOPMENT,
        )


# Singleton instance
_detector: Optional[EnvironmentDetector] = None


def get_environment_detector() -> EnvironmentDetector:
    """
    Get singleton EnvironmentDetector instance.

    Returns:
        Global EnvironmentDetector instance
    """
    global _detector
    if _detector is None:
        _detector = EnvironmentDetector()
    return _detector


def detect_environment() -> EnvironmentType:
    """
    Convenience function to detect environment.

    Returns:
        EnvironmentType enum value
    """
    detector = get_environment_detector()
    return detector.detect_environment()


def get_tool_adapter() -> "ToolAdapter":  # noqa: F821
    """
    Convenience function to get tool adapter.

    Returns:
        ToolAdapter instance configured for current environment
    """
    detector = get_environment_detector()
    return detector.get_tool_adapter()
