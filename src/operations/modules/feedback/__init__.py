"""
Feedback Module Package

Enhanced feedback collection with comprehensive metrics and GitHub Gist integration.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from .enhanced_feedback_module import EnhancedFeedbackModule, register
from .privacy import PrivacySanitizer

__all__ = [
    'EnhancedFeedbackModule',
    'PrivacySanitizer',
    'register',
]
