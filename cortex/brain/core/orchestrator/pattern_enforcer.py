"""
Communication pattern enforcement for orchestrators.

Loads and enforces patterns from cortex-registry/interaction/
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from cortex.brain.core.result import Err, Ok, Result


class PatternEnforcer:
    """
    Enforces communication patterns from cortex-registry/interaction/.

    Validates orchestrator compliance with defined patterns and audits violations.
    """

    def __init__(self, registry_path: Optional[Path] = None):
        """
        Initialize pattern enforcer.

        Args:
            registry_path: Path to pattern registry
        """
        if registry_path is None:
            registry_path = (
                Path(__file__).parent.parent.parent.parent.parent
                / "cortex-registry"
                / "interaction"
            )

        self.registry_path = Path(registry_path)
        self.patterns: Dict[str, Dict[str, Any]] = {}
        self.violations: List[Dict[str, Any]] = []
        self._load_patterns()

    def _load_patterns(self) -> None:
        """Load all patterns from registry."""
        if not self.registry_path.exists():
            return

        for pattern_file in self.registry_path.glob("*.yaml"):
            try:
                with open(pattern_file) as f:
                    pattern = yaml.safe_load(f)
                    self.patterns[pattern["pattern_id"]] = pattern
            except Exception as e:
                print(f"[WARNING] Failed to load pattern {pattern_file}: {e}")

    def validate_request(
        self,
        pattern_id: str,
        request: Dict[str, Any]
    ) -> Result[None]:
        """
        Validate request against pattern.

        Args:
            pattern_id: ID of pattern to validate against
            request: Request data

        Returns:
            Ok if valid, Err with violation details
        """
        if pattern_id not in self.patterns:
            return Err(f"Pattern {pattern_id} not found")

        pattern = self.patterns[pattern_id]

        # Check required fields
        for field in pattern.get("required_fields", []):
            if field not in request:
                violation = f"Missing required field: {field}"
                self._log_violation(pattern_id, "request", violation)
                return Err(violation)

        return Ok(None)

    def validate_response(
        self,
        pattern_id: str,
        response: Dict[str, Any]
    ) -> Result[None]:
        """
        Validate response against pattern.

        Args:
            pattern_id: ID of pattern to validate against
            response: Response data

        Returns:
            Ok if valid, Err with violation details
        """
        if pattern_id not in self.patterns:
            return Err(f"Pattern {pattern_id} not found")

        pattern = self.patterns[pattern_id]

        # Check pattern type requirements
        pattern_type = pattern.get("pattern_type")

        if pattern_type == "request-response":
            if "response" not in response and "result" not in response:
                violation = "Request-response requires 'response' or 'result'"
                self._log_violation(pattern_id, "response", violation)
                return Err(violation)

        elif pattern_type == "event-driven":
            if "event_type" not in response:
                violation = "Event-driven requires 'event_type'"
                self._log_violation(pattern_id, "response", violation)
                return Err(violation)

        return Ok(None)

    def _log_violation(
        self,
        pattern_id: str,
        context: str,
        violation: str
    ) -> None:
        """
        Log a pattern violation.

        Args:
            pattern_id: Pattern that was violated
            context: Context (request/response)
            violation: Violation description
        """
        from datetime import datetime

        self.violations.append({
            "pattern_id": pattern_id,
            "context": context,
            "violation": violation,
            "timestamp": datetime.now().isoformat()
        })

    def get_violations(self) -> List[Dict[str, Any]]:
        """
        Get all logged violations.

        Returns:
            List of violations
        """
        return self.violations.copy()

    def clear_violations(self) -> None:
        """Clear all logged violations."""
        self.violations.clear()

    def get_pattern_count(self) -> int:
        """Get number of loaded patterns."""
        return len(self.patterns)
