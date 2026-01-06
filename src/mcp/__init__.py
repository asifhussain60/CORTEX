"""
CORTEX MCP (Master Control Program) Package.

Central orchestrator registry and dynamic loading system.

Phase 2 of CORTEX5 Enhancement Epic.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from .registry import OrchestratorRegistry
from .loader import OrchestratorLoader
from .metadata import OrchestratorMetadata

__all__ = [
    'OrchestratorRegistry',
    'OrchestratorLoader',
    'OrchestratorMetadata',
]
