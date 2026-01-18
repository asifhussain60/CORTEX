"""
Telemetry Provider Integration Module

Provides convenience functions for telemetry initialization and management.
"""

import logging
from typing import Optional, List
from cortex.infrastructure.metrics_exporter import (
    TelemetryProvider,
    MetricsExporter,
    ConsoleMetricsExporter,
    MemoryMetricsExporter,
)

logger = logging.getLogger(__name__)


class TelemetryConfiguration:
    """Configuration for telemetry setup."""
    
    def __init__(
        self,
        enable_console: bool = True,
        enable_memory: bool = True,
        batch_size: int = 10,
        use_async: bool = True
    ):
        self.enable_console = enable_console
        self.enable_memory = enable_memory
        self.batch_size = batch_size
        self.use_async = use_async


def create_telemetry_provider(
    config: Optional[TelemetryConfiguration] = None
) -> TelemetryProvider:
    """
    Create and configure a telemetry provider with standard exporters.
    
    Args:
        config: Optional telemetry configuration
    
    Returns:
        Configured TelemetryProvider instance
    """
    config = config or TelemetryConfiguration()
    
    exporters: List[MetricsExporter] = []
    
    if config.enable_console:
        exporters.append(ConsoleMetricsExporter())
    
    if config.enable_memory:
        exporters.append(MemoryMetricsExporter())
    
    provider = TelemetryProvider(
        exporters=exporters,
        batch_size=config.batch_size,
        use_async=config.use_async
    )
    
    logger.info(
        f"Telemetry provider created with {len(exporters)} exporters "
        f"(batch_size={config.batch_size}, async={config.use_async})"
    )
    
    return provider


def get_default_telemetry_provider() -> TelemetryProvider:
    """Get default telemetry provider instance."""
    config = TelemetryConfiguration(
        enable_console=False,  # Default to memory only for production
        enable_memory=True,
        batch_size=10,
        use_async=True
    )
    return create_telemetry_provider(config)
