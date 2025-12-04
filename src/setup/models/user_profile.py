"""
User Profile Model

Pydantic schema for CORTEX user profiles with multilingual support.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from typing import Literal
from pydantic import BaseModel, Field, field_validator


# Supported languages with native names (12 languages)
SUPPORTED_LANGUAGES = {
    "en": {"name": "English", "native": "English"},
    "es": {"name": "Spanish", "native": "Español"},
    "fr": {"name": "French", "native": "Français"},
    "de": {"name": "German", "native": "Deutsch"},
    "pt": {"name": "Portuguese", "native": "Português"},
    "zh": {"name": "Chinese", "native": "中文"},
    "ja": {"name": "Japanese", "native": "日本語"},
    "ko": {"name": "Korean", "native": "한국어"},
    "hi": {"name": "Hindi", "native": "हिन्दी"},
    "ar": {"name": "Arabic", "native": "العربية"},
    "ru": {"name": "Russian", "native": "Русский"},
    "it": {"name": "Italian", "native": "Italiano"},
}


class UserProfile(BaseModel):
    """
    User profile with personalization preferences.
    
    Attributes:
        name: User's name (for personalized greetings)
        preference: Response style (concise/balanced/verbose)
        role: Technical level (beginner/intermediate/expert)
        work_area: Primary work domain
        language: Preferred language (ISO 639-1 code)
    """
    
    name: str = Field(..., min_length=1, max_length=100, description="User's name")
    
    preference: Literal["concise", "balanced", "verbose"] = Field(
        default="verbose",
        description="Response style preference"
    )
    
    role: Literal["beginner", "intermediate", "expert"] = Field(
        default="intermediate",
        description="Technical expertise level"
    )
    
    work_area: Literal[
        "general", "web_dev", "data_science", "ai_ml", 
        "devops", "mobile", "backend", "frontend", "fullstack"
    ] = Field(
        default="general",
        description="Primary work domain"
    )
    
    language: str = Field(
        default="en",
        description="Preferred language (ISO 639-1 code)"
    )
    
    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        """Validate language code against supported languages."""
        if v not in SUPPORTED_LANGUAGES:
            supported = ", ".join(SUPPORTED_LANGUAGES.keys())
            raise ValueError(
                f"Language '{v}' not supported. Supported languages: {supported}"
            )
        return v
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "name": "Asif Hussain",
                "preference": "concise",
                "role": "expert",
                "work_area": "ai_ml",
                "language": "en"
            }
        }
