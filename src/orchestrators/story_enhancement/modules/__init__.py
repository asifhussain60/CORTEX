"""
Story Enhancement Modules

Individual components for story enhancement orchestration.

Modules:
    1. feature_discovery - Extract CORTEX features
    2. voice_profile - Analyze narrative style
    3. content_generator - Create new chapters (Phase 2)
    4. humor_amplification - Enhance comedy (Phase 2)
    5. deduplication - Remove repetition (Phase 2)
    6. beat_detector - Find image anchors (Phase 3)
    7. image_prompt_generator - DALL-E prompts (Phase 3)
    8. story_validation - Auto-fix errors (Phase 3.5)
    9. dalle_integration - Prompt generation + injection (Phases 3-4)
"""

from .feature_discovery import FeatureDiscoveryModule, Feature, FeatureWeight
# from .voice_profile import VoiceProfileAnalyzer, VoiceProfile
# More modules imported as they're implemented

__all__ = [
    'FeatureDiscoveryModule',
    'Feature',
    'FeatureWeight',
    # 'VoiceProfileAnalyzer',
    # 'VoiceProfile',
]
