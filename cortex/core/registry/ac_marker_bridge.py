"""ACMarkerBridge for canonical AC_START/AC_COMPLETE marker emission."""

from __future__ import annotations


class ACMarkerBridge:
    """Formats paired audit markers under canonical AC contract."""

    def __init__(self, domain: str) -> None:
        """Initialize with a marker domain.

        Args:
            domain: Marker domain (e.g., M21, DOCGEN).
        """
        self._domain = domain.upper().replace(" ", "-")

    def _marker_id(self, sequence: str) -> str:
        """Build canonical marker id.

        Args:
            sequence: Sequence identifier.

        Returns:
            Canonical AC marker id.
        """
        return f"AC-{self._domain}-{sequence}"

    def emit_start(self, sequence: str) -> str:
        """Emit AC_START marker line."""
        marker_id = self._marker_id(sequence)
        return f"AC_START: {marker_id}"

    def emit_complete(self, sequence: str) -> str:
        """Emit AC_COMPLETE marker line."""
        marker_id = self._marker_id(sequence)
        return f"AC_COMPLETE: {marker_id}"
