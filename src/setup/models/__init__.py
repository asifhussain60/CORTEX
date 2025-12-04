"""
Setup Models Package

Pydantic models for CORTEX setup and configuration.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from .user_profile import UserProfile, SUPPORTED_LANGUAGES
from .user_path_config import UserPathConfig

__all__ = ["UserProfile", "SUPPORTED_LANGUAGES", "UserPathConfig"]
