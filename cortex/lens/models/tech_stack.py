"""
Tech Stack Models - Language and Framework Detection Types.

Authority: Phase 90 Stage 1 - Tech Stack Detection
Purpose: Data models for representing detected technology stacks

CORE Rules:
- CORE-011: Type hints required ✅
- CORE-012: Docstrings required ✅
- CORE-008: TDD mandatory ✅
"""
# CORE-035 — domain-scoped; class name is contextually appropriate here

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class TechCategory(Enum):
    """Technology category classification."""

    LANGUAGE = "language"
    FRAMEWORK = "framework"
    LIBRARY = "library"
    RUNTIME = "runtime"
    DATABASE = "database"
    CLOUD = "cloud"
    TESTING = "testing"
    BUILD_TOOL = "build_tool"


@dataclass
class TechStackItem:
    """Single technology stack item with metadata."""

    name: str
    category: TechCategory
    version: Optional[str] = None
    confidence: float = 1.0  # 0.0 to 1.0
    detection_method: str = "unknown"  # file_extension, ast_import, config_file, etc.

    def __post_init__(self) -> None:
        """Validate confidence score."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {self.confidence}")


@dataclass
class TechStack:
    """Complete technology stack detection result."""

    primary_language: Optional[str] = None
    languages: List[str] = field(default_factory=list)
    frameworks: List[str] = field(default_factory=list)
    libraries: List[str] = field(default_factory=list)
    databases: List[str] = field(default_factory=list)
    build_tools: List[str] = field(default_factory=list)
    test_frameworks: List[str] = field(default_factory=list)

    # Detailed items with metadata
    items: List[TechStackItem] = field(default_factory=list)

    # Detection metadata
    confidence_score: float = 0.0  # Overall confidence
    detection_methods: List[str] = field(default_factory=list)

    def add_item(self, item: TechStackItem) -> None:
        """Add technology item and update category lists."""
        self.items.append(item)

        # Update category-specific lists
        if item.category == TechCategory.LANGUAGE and item.name not in self.languages:
            self.languages.append(item.name)
        elif item.category == TechCategory.FRAMEWORK and item.name not in self.frameworks:
            self.frameworks.append(item.name)
        elif item.category == TechCategory.LIBRARY and item.name not in self.libraries:
            self.libraries.append(item.name)
        elif item.category == TechCategory.DATABASE and item.name not in self.databases:
            self.databases.append(item.name)
        elif item.category == TechCategory.BUILD_TOOL and item.name not in self.build_tools:
            self.build_tools.append(item.name)
        elif item.category == TechCategory.TESTING and item.name not in self.test_frameworks:
            self.test_frameworks.append(item.name)

    def get_primary_language(self) -> Optional[str]:
        """Get primary language (highest confidence language item)."""
        language_items = [
            item for item in self.items
            if item.category == TechCategory.LANGUAGE
        ]

        if not language_items:
            return None

        # Sort by confidence, return highest
        language_items.sort(key=lambda x: x.confidence, reverse=True)
        return language_items[0].name

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "primary_language": self.primary_language or self.get_primary_language(),
            "languages": self.languages,
            "frameworks": self.frameworks,
            "libraries": self.libraries,
            "databases": self.databases,
            "build_tools": self.build_tools,
            "test_frameworks": self.test_frameworks,
            "confidence_score": self.confidence_score,
            "detection_methods": self.detection_methods,
            "items": [
                {
                    "name": item.name,
                    "category": item.category.value,
                    "version": item.version,
                    "confidence": item.confidence,
                    "detection_method": item.detection_method
                }
                for item in self.items
            ]
        }


# AC_START: AC-PHASE90-S1-001
# Description: Tech stack data models for detection system
