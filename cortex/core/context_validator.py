"""Context validation utilities for phase-m2 consolidation."""

from pathlib import Path
from typing import Any, Optional


class ContextValidator:
    """Validate assembled context payloads before orchestration.

    The validator enforces minimal structure and detects stale file references.
    """

    REQUIRED_KEYS: tuple[str, ...] = ("intent", "files")

    def __init__(self, workspace_root: Optional[Path] = None) -> None:
        """Initialize validator.

        Args:
            workspace_root: Optional workspace root path override.
        """
        self._workspace_root = workspace_root or Path(__file__).resolve().parents[2]

    def get_missing_keys(self, context: dict[str, Any]) -> list[str]:
        """Return required keys that are missing from context.

        Args:
            context: Context dictionary.

        Returns:
            Missing required key names.
        """
        return [key for key in self.REQUIRED_KEYS if key not in context]

    def validate(self, context: Any) -> tuple[bool, list[str]]:
        """Validate context payload.

        Args:
            context: Candidate context payload.

        Returns:
            Tuple of validation status and list of error messages.
        """
        if not isinstance(context, dict):
            return False, ["Context must be a dictionary"]

        errors: list[str] = []
        missing = self.get_missing_keys(context)
        if missing:
            errors.append(f"Missing required keys: {', '.join(missing)}")
            return False, errors

        files = context.get("files")
        if not isinstance(files, list):
            errors.append("Context key 'files' must be a list")
            return False, errors

        stale_refs = self._get_stale_file_references(files)
        if stale_refs:
            errors.append(f"Stale file references: {', '.join(stale_refs)}")

        return len(errors) == 0, errors

    def is_valid(self, context: Any) -> bool:
        """Return whether context is valid.

        Args:
            context: Candidate context payload.

        Returns:
            True when context validates, otherwise False.
        """
        is_valid, _ = self.validate(context)
        return is_valid

    def _get_stale_file_references(self, files: list[Any]) -> list[str]:
        """Collect non-existent file references from context.

        Args:
            files: File reference list from context.

        Returns:
            Relative paths that do not exist.
        """
        stale_refs: list[str] = []
        for file_ref in files:
            if not isinstance(file_ref, str) or not file_ref.strip():
                stale_refs.append(str(file_ref))
                continue
            target_path = (self._workspace_root / file_ref).resolve()
            if not target_path.exists():
                stale_refs.append(file_ref)
        return stale_refs
