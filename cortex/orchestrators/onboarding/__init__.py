"""Onboarding orchestrators package for CORTEX.

This package provides automated setup and configuration orchestrators:
- SetupOrchestrator: Requirements validation and auto-installation
- VSCodeConfigurator: VSCode workspace configuration
- ToolchainValidator: Toolchain health checks
- MCPBootstrapper: MCP server bootstrap
- DependencyResolver: Multi-repo dependency resolution
"""

from cortex.orchestrators.onboarding.setup_orchestrator import (
    SetupOrchestrator,
    Requirement,
    InstallResult,
    SecurityScanResult,
)
from cortex.orchestrators.onboarding.vscode_configurator import (
    VSCodeConfigurator,
)
from cortex.orchestrators.onboarding.toolchain_validator import (
    ToolchainValidator,
    ToolValidationResult,
)
from cortex.orchestrators.onboarding.mcp_bootstrapper import (
    MCPBootstrapper,
    ServerStartResult,
    ServerStopResult,
    HealthCheckResult,
    ConfigUpdateResult,
)
from cortex.orchestrators.onboarding.dependency_resolver import (
    DependencyResolver,
    DependencyConflict,
    ResolutionStrategy,
)

__all__ = [
    # setup_orchestrator
    "SetupOrchestrator",
    "Requirement",
    "InstallResult",
    "SecurityScanResult",
    # vscode_configurator
    "VSCodeConfigurator",
    # toolchain_validator
    "ToolchainValidator",
    "ToolValidationResult",
    # mcp_bootstrapper
    "MCPBootstrapper",
    "ServerStartResult",
    "ServerStopResult",
    "HealthCheckResult",
    "ConfigUpdateResult",
    # dependency_resolver
    "DependencyResolver",
    "DependencyConflict",
    "ResolutionStrategy",
]
