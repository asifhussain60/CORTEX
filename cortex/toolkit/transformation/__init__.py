"""Content transformation — sanitization, safe renaming, transactional changes.

Components:
    ContentSanitizer:   Rule-based text transformation with configurable morphs
    SafeRename:         File rename with referential integrity
    CollisionDetector:  Duplicate prevention across rename operations
    RollbackManager:    Transaction + snapshot support

CORE-011: Type hints on all functions
CORE-012: Docstrings on all public APIs
"""

__all__ = [
    "ContentSanitizer",
    "SafeRename",
    "CollisionDetector",
    "RollbackManager",
]
