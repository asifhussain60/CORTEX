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

# Phase 4 exports - Narrative Generation (safe imports)
try:
    from .narrative_engine import (
        StoryTemplateSystem, 
        ContextWeavingEngine, 
        DecisionRationaleExtractor,
        enhance_narrative_intelligence_with_track_b
    )
except ImportError as e:
    import logging
    logging.warning(f"Could not import narrative_engine components: {e}")
    StoryTemplateSystem = None
    ContextWeavingEngine = None
    DecisionRationaleExtractor = None
    enhance_narrative_intelligence_with_track_b = None

try:
    from .mock_data import DualChannelMockData, create_track_b_mock_data
except ImportError as e:
    import logging
    logging.warning(f"Could not import mock_data components: {e}")
    DualChannelMockData = None
    create_track_b_mock_data = None

try:
    from .integration_system import (
        MockDataIntegrationSystem,
        IntegrationTestResult, 
        DualChannelCompatibilityTester
    )
except ImportError as e:
    import logging
    logging.warning(f"Could not import integration_system components: {e}")
    MockDataIntegrationSystem = None
    IntegrationTestResult = None
    DualChannelCompatibilityTester = None

try:
    from .enhanced_continue_command import (
        EnhancedContinueCommand,
        ContinueContext,
        ContinuationSuggestion
    )
except ImportError as e:
    import logging
    logging.warning(f"Could not import enhanced_continue_command components: {e}")
    EnhancedContinueCommand = None
    ContinueContext = None
    ContinuationSuggestion = None

__all__ = [
    # Core narrative engine
    "StoryTemplateSystem",
    "ContextWeavingEngine", 
    "DecisionRationaleExtractor",
    "enhance_narrative_intelligence_with_track_b",
    
    # Mock data for development
    "DualChannelMockData",
    "create_track_b_mock_data",
    
    # Integration system
    "MockDataIntegrationSystem",
    "IntegrationTestResult", 
    "DualChannelCompatibilityTester",
    
    # Enhanced continue command
    "EnhancedContinueCommand",
    "ContinueContext",
    "ContinuationSuggestion",
]