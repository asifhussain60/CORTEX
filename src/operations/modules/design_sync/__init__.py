"""
Design Sync Module

Handles synchronization of CORTEX design documents with actual implementation.
Supports multi-track development with race metrics.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from .design_sync_orchestrator import DesignSyncOrchestrator
from .track_config import (
    MultiTrackConfig,
    MachineTrack,
    TrackMetrics,
    TrackNameGenerator,
    PhaseDistributor,
    TrackConfigManager
)
from .track_templates import TrackDocumentTemplates

__all__ = [
    'DesignSyncOrchestrator',
    'MultiTrackConfig',
    'MachineTrack',
    'TrackMetrics',
    'TrackNameGenerator',
    'PhaseDistributor',
    'TrackConfigManager',
    'TrackDocumentTemplates'
]
