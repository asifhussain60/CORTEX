"""CORTEX Telemetry API module for unified deployment architecture."""

__version__ = "1.0.0"

from .aggregator import TelemetryAggregator
from .ingest import TelemetryIngestEndpoint
from .schema import TelemetryEventSchema

__all__ = [
    "TelemetryIngestEndpoint",
    "TelemetryAggregator",
    "TelemetryEventSchema",
]
