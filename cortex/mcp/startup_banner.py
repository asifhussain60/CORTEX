"""
CORTEX MCP Server Startup Banner.

Displays formatted server information on startup including:
- Version and build info
- Wiring system hash
- Orchestrator count
- Port and environment

CORE-011: All functions have type hints.
CORE-012: All public APIs have Google-style docstrings.
"""

from typing import Dict, Any


def get_banner(
    version: str = "2.1",
    wiring_hash: str = "unknown",
    orchestrator_count: int = 23,
    port: int = 8443,
    environment: str = "development"
) -> str:
    """
    Generate CORTEX MCP Server startup banner.
    
    Args:
        version: Server version.
        wiring_hash: Hash of wiring specification.
        orchestrator_count: Number of wired orchestrators.
        port: Server port.
        environment: Runtime environment (development/production).
    
    Returns:
        Formatted banner string.
    """
    banner = f"""
╔══════════════════════════════════════════════════════════╗
║                    CORTEX MCP Server                     ║
╠══════════════════════════════════════════════════════════╣
║  Version:       {version:<46} ║
║  Wiring Hash:   {wiring_hash:<46} ║
║  Orchestrators: {orchestrator_count}/23 wired{'':<41} ║
║  Port:          {port:<46} ║
║  Environment:   {environment:<46} ║
╚══════════════════════════════════════════════════════════╝
"""
    return banner


def print_banner(
    version: str = "2.1",
    wiring_hash: str = "unknown",
    orchestrator_count: int = 23,
    port: int = 8443,
    environment: str = "development"
) -> None:
    """
    Print CORTEX MCP Server startup banner to stdout.
    
    Args:
        version: Server version.
        wiring_hash: Hash of wiring specification.
        orchestrator_count: Number of wired orchestrators.
        port: Server port.
        environment: Runtime environment (development/production).
    """
    banner = get_banner(version, wiring_hash, orchestrator_count, port, environment)
    print(banner)


def get_banner_dict(
    version: str = "2.1",
    wiring_hash: str = "unknown",
    orchestrator_count: int = 23,
    port: int = 8443,
    environment: str = "development"
) -> Dict[str, Any]:
    """
    Get startup info as dictionary.
    
    Args:
        version: Server version.
        wiring_hash: Hash of wiring specification.
        orchestrator_count: Number of wired orchestrators.
        port: Server port.
        environment: Runtime environment.
    
    Returns:
        Dictionary with startup information.
    """
    return {
        "version": version,
        "wiring_hash": wiring_hash,
        "orchestrator_count": orchestrator_count,
        "orchestrators_total": 23,
        "port": port,
        "environment": environment,
        "service_name": "CORTEX MCP Server",
        "protocol": "MCP",
        "json_rpc_version": "2.0"
    }
