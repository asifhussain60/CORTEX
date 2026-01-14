"""
CORTEX Core Module - Shared Utilities

Contains SOLID/DRY compliant shared utilities:
- interfaces.py: Abstract base classes
- result.py: Result[T] pattern for error handling
- config.py: Unified configuration loading
- path_resolver.py: Cross-platform path resolution
- yaml_loader.py: Single YAML loading implementation

All tools and orchestrators should use these utilities
to avoid duplication and ensure consistency.
"""

from src.core.result import Result, Ok, Err
from src.core.path_resolver import get_project_root, resolve_path
from src.core.config import load_config

__all__ = [
    "Result", "Ok", "Err",
    "get_project_root", "resolve_path",
    "load_config"
]
