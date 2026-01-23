"""Cleaners - Domain-specific data cleaners.

Provides cleaning orchestrators for different domains.

Author: CORTEX Framework
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional, List, Callable
from enum import Enum


class CleanerType(Enum):
    """Types of cleaners."""

    DATA = "data"
    FORMAT = "format"
    VALIDATION = "validation"
    NORMALIZATION = "normalization"
    DEDUPLICATION = "deduplication"


@dataclass
class CleaningRule:
    """Cleaning rule definition.

    Attributes:
        rule_id: Unique rule identifier.
        name: Rule name.
        cleaner_type: Type of cleaner.
        processor: Processing function.
    """

    rule_id: str
    name: str
    cleaner_type: CleanerType
    processor: Callable


class Cleaner:
    """Base cleaner interface."""

    def __init__(self, name: str = "Cleaner") -> None:
        """Initialize cleaner.

        Args:
            name: Cleaner name.
        """
        self.name = name
        self.rules: Dict[str, CleaningRule] = {}

    def register_rule(self, rule: CleaningRule) -> None:
        """Register a cleaning rule.

        Args:
            rule: CleaningRule to register.
        """
        self.rules[rule.rule_id] = rule

    def clean(self, data: Any) -> Any:
        """Clean data.

        Args:
            data: Data to clean.

        Returns:
            Cleaned data.
        """
        result = data
        for rule in self.rules.values():
            try:
                result = rule.processor(result)
            except Exception:
                pass
        return result

    def get_name(self) -> str:
        """Get cleaner name.

        Returns:
            Cleaner name.
        """
        return self.name


class DataCleaner(Cleaner):
    """Specialized data cleaner."""

    def __init__(self) -> None:
        """Initialize data cleaner."""
        super().__init__("DataCleaner")


class FormatCleaner(Cleaner):
    """Specialized format cleaner."""

    def __init__(self) -> None:
        """Initialize format cleaner."""
        super().__init__("FormatCleaner")


__all__ = [
    "Cleaner",
    "DataCleaner",
    "FormatCleaner",
    "CleaningRule",
    "CleanerType",
]
