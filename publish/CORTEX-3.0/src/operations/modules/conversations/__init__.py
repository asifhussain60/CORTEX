# Conversation Tracking & Capture Module
# 
# Purpose: Direct file-based conversation capture for CORTEX brain
# Version: CORTEX 3.0 Feature 5 (Streamlined - file parameter required)
# Author: Asif Hussain
# Copyright: © 2024-2025 Asif Hussain. All rights reserved.

# ConversationCaptureHandler removed - parameterless capture deprecated
# Only direct file import supported: capture conversation #file:path.md
from .import_handler import ConversationImportHandler
from .direct_import import DirectConversationImport
from .quality_monitor import QualityMonitor, create_monitor
from .smart_hint_generator import SmartHintGenerator, create_hint_generator
from .smart_auto_detection import SmartAutoDetection, create_smart_auto_detection
from .tier2_learning import Tier2LearningIntegration, create_tier2_learning

__all__ = [
    # 'ConversationCaptureHandler',  # REMOVED: parameterless capture deprecated
    'ConversationImportHandler',
    'DirectConversationImport',
    'QualityMonitor',
    'create_monitor',
    'SmartHintGenerator',
    'create_hint_generator',
    'SmartAutoDetection',
    'create_smart_auto_detection',
    'Tier2LearningIntegration',
    'create_tier2_learning'
]

