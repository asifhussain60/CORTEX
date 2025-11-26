"""
Brain Ingestion Adapter Agent

Adapter pattern implementation that bridges interface differences between
the abstract BrainIngestionAgent interface and the concrete BrainIngestionAgentImpl.

This adapter enables the Feature Completion Orchestrator to work with the concrete
brain ingestion implementation without tight coupling.

Author: Asif Hussain
Created: November 26, 2025
Version: 1.0
"""

import logging
from .feature_completion_orchestrator import BrainIngestionAgent, BrainData
from .brain_ingestion_agent import BrainIngestionAgentImpl

logger = logging.getLogger(__name__)


class BrainIngestionAdapterAgent(BrainIngestionAgent):
    """
    Adapter to bridge interface differences between abstract BrainIngestionAgent
    and concrete BrainIngestionAgentImpl.
    
    This is a pure delegation pattern - no business logic or feature processing
    happens here. The adapter simply forwards calls to the concrete implementation.
    """
    
    def __init__(self, workspace_path: str):
        """
        Initialize adapter with workspace path.
        
        Args:
            workspace_path: Path to workspace/CORTEX root
        """
        self.workspace_path = workspace_path
        self.impl = BrainIngestionAgentImpl(workspace_path)
    
    async def ingest_feature(self, feature_description: str) -> BrainData:
        """
        Delegate feature ingestion to concrete implementation.
        
        Args:
            feature_description: Description of completed feature
            
        Returns:
            BrainData with extracted entities, patterns, and context updates
        """
        return await self.impl.ingest_feature(feature_description)
