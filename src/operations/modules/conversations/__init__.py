# Conversation Tracking & Capture Module
# 
# Purpose: Manual and intelligent conversation capture for CORTEX brain
# Version: CORTEX 3.0 Feature 5
# Author: Asif Hussain
# Copyright: © 2024-2025 Asif Hussain. All rights reserved.

from .capture_handler import ConversationCaptureHandler
from .import_handler import ConversationImportHandler
from .quality_monitor import QualityMonitor, create_monitor
from .smart_hint_generator import SmartHintGenerator, create_hint_generator
from .smart_auto_detection import SmartAutoDetection, create_smart_auto_detection
from .tier2_learning import Tier2LearningIntegration, create_tier2_learning

__all__ = [
    'ConversationCaptureHandler',
    'ConversationImportHandler',
    'QualityMonitor',
    'create_monitor',
    'SmartHintGenerator',
    'create_hint_generator',
    'SmartAutoDetection',
    'create_smart_auto_detection',
    'Tier2LearningIntegration',
    'create_tier2_learning'
]

