"""
CORTEX 3.0 Track B (Enhanced Features) - Phase 4: Narrative Generation

Track B focuses on enhanced user-facing features:
- Phase 4: Narrative Generation (story templates, context weaving, enhanced continue)
- Phase 5: VS Code Manual Import Extension

This implementation follows the CORTEX 3.0 Parallel Track Plan and uses
mock dual-channel data during development phase (Weeks 8-15).

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
"""

__version__ = "3.0.0-phase-4"
__author__ = "Asif Hussain"

# Phase 4 exports - Narrative Generation (only what exists)
from .narrative_engine import (
    StoryTemplateSystem, 
    ContextWeavingEngine, 
    DecisionRationaleExtractor,
    enhance_narrative_intelligence_with_track_b
)
from .mock_data import DualChannelMockData, create_track_b_mock_data

__all__ = [
    # Core narrative engine
    "StoryTemplateSystem",
    "ContextWeavingEngine", 
    "DecisionRationaleExtractor",
    "enhance_narrative_intelligence_with_track_b",
    
    # Mock data for development
    "DualChannelMockData",
    "create_track_b_mock_data",
]