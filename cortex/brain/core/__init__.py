"""
CORTEX Core Module - Shared Utilities

Contains SOLID/DRY compliant shared utilities:
- interfaces.py: Abstract base classes
- result.py: Result[T] pattern for error handling
- config.py: Unified configuration loading
- path_resolver.py: Cross-platform path resolution
- yaml_loader.py: Single YAML loading implementation
- session_summary_generator.py: Session summary formatting (ENH-048)

All tools and orchestrators should use these utilities
to avoid duplication and ensure consistency.
"""

from cortex.brain.core.config import load_config
from cortex.brain.core.path_resolver import get_project_root, resolve_path
from cortex.brain.core.result import Err, Ok, Result
from cortex.brain.core.session_summary_generator import (
    SessionMetrics,
    StageResult,
    format_session_summary,
    generate_continuation_checkpoint,
    get_token_status,
)

__all__ = [
    "Result", "Ok", "Err",
    "get_project_root", "resolve_path",
    "load_config",
    "format_session_summary",
    "generate_continuation_checkpoint",
    "get_token_status",
    "SessionMetrics",
    "StageResult",
]
