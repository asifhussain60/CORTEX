"""
InteractionOrchestrator - Communication pattern enforcement wrapper.

Wraps ConversationProtocol to enforce communication patterns from
cortex-registry/interaction/ definitions.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path
import yaml

from cortex.brain.core.orchestrator.conversation_protocol import (
    ConversationProtocol,
    RoundContext,
)
from cortex.brain.core.orchestrator.continuation_decision import ContinuationDecision
from cortex.brain.core.result import Result, Ok, Err


@dataclass
class CommunicationPattern:
    """Definition of a communication pattern."""
    
    pattern_id: str
    name: str
    pattern_type: str  # "request-response", "event-driven", "pub-sub"
    required_fields: List[str]
    optional_fields: List[str]
    validation_rules: Dict[str, Any]


class PatternViolationError(Exception):
    """Raised when orchestrator violates communication pattern."""
    
    def __init__(self, pattern_id: str, violation: str):
        self.pattern_id = pattern_id
        self.violation = violation
        super().__init__(f"Pattern {pattern_id} violated: {violation}")


class InteractionOrchestrator:
    """
    Wraps ConversationProtocol to enforce communication patterns.
    
    Loads pattern definitions from cortex-registry/interaction/ and validates
    that orchestrators comply with specified patterns.
    
    Provides:
    - Pattern loading from registry
    - Per-turn pattern validation
    - Pattern violation logging and alerts
    - Full round-trip: user input → protocol → orchestrator → response
    """
    
    def __init__(
        self,
        conversation_protocol: ConversationProtocol,
        pattern_registry_path: Optional[Path] = None
    ):
        """
        Initialize InteractionOrchestrator.
        
        Args:
            conversation_protocol: ConversationProtocol instance to wrap
            pattern_registry_path: Path to pattern registry (defaults to cortex-registry/interaction/)
        """
        self.conversation_protocol = conversation_protocol
        
        if pattern_registry_path is None:
            pattern_registry_path = (
                Path(__file__).parent.parent.parent.parent.parent
                / "cortex-registry"
                / "interaction"
            )
        
        self.pattern_registry_path = Path(pattern_registry_path)
        self.patterns: Dict[str, CommunicationPattern] = {}
        self._load_patterns()
    
    def _load_patterns(self) -> None:
        """Load communication patterns from registry."""
        if not self.pattern_registry_path.exists():
            # Registry not yet populated, skip loading
            return
        
        for pattern_file in self.pattern_registry_path.glob("*.yaml"):
            try:
                with open(pattern_file) as f:
                    pattern_def = yaml.safe_load(f)
                
                pattern = CommunicationPattern(
                    pattern_id=pattern_def["pattern_id"],
                    name=pattern_def["name"],
                    pattern_type=pattern_def["pattern_type"],
                    required_fields=pattern_def.get("required_fields", []),
                    optional_fields=pattern_def.get("optional_fields", []),
                    validation_rules=pattern_def.get("validation_rules", {})
                )
                
                self.patterns[pattern.pattern_id] = pattern
            except Exception as e:
                print(f"[WARNING] Failed to load pattern from {pattern_file}: {e}")
    
    def execute_turn_with_pattern(
        self,
        round_context: RoundContext,
        pattern_id: str,
        validate_strict: bool = True
    ) -> Result[Dict[str, Any]]:
        """
        Execute a turn with pattern enforcement.
        
        Args:
            round_context: Context for this turn
            pattern_id: ID of the pattern to enforce
            validate_strict: If True, fail on violations; if False, log warnings
            
        Returns:
            Result with orchestrator output or error
        """
        # Check pattern exists
        if pattern_id not in self.patterns:
            return Err(f"Pattern {pattern_id} not found in registry")
        
        pattern = self.patterns[pattern_id]
        
        # Validate input against pattern (pre-execution)
        input_validation = self._validate_input(round_context, pattern)
        if not input_validation.is_ok() and validate_strict:
            return input_validation
        
        # Execute turn via ConversationProtocol
        result = self.conversation_protocol.execute_turn(round_context)
        
        if not result.is_ok():
            return result
        
        # Validate output against pattern (post-execution)
        output = result.unwrap()
        output_validation = self._validate_output(output, pattern)
        
        if not output_validation.is_ok() and validate_strict:
            return output_validation
        elif not output_validation.is_ok():
            # Log warning but allow execution
            print(f"[WARNING] Pattern violation (non-strict): {output_validation.unwrap_err()}")
        
        return Ok(output)
    
    def _validate_input(
        self,
        round_context: RoundContext,
        pattern: CommunicationPattern
    ) -> Result[None]:
        """
        Validate input against pattern requirements.
        
        Args:
            round_context: Turn context
            pattern: Pattern to validate against
            
        Returns:
            Ok if valid, Err with violation details
        """
        # Check required fields in context
        for field in pattern.required_fields:
            if field not in round_context.previous_context:
                return Err(
                    f"Required field '{field}' missing from context for pattern {pattern.pattern_id}"
                )
        
        # Apply validation rules
        for rule_name, rule_def in pattern.validation_rules.items():
            if rule_name == "min_length":
                if len(round_context.user_input) < rule_def:
                    return Err(
                        f"Input too short (min: {rule_def}) for pattern {pattern.pattern_id}"
                    )
        
        return Ok(None)
    
    def _validate_output(
        self,
        output: Dict[str, Any],
        pattern: CommunicationPattern
    ) -> Result[None]:
        """
        Validate output against pattern requirements.
        
        Args:
            output: Orchestrator output
            pattern: Pattern to validate against
            
        Returns:
            Ok if valid, Err with violation details
        """
        # For request-response pattern, ensure response structure
        if pattern.pattern_type == "request-response":
            if "response" not in output and "result" not in output:
                return Err(
                    f"Request-response pattern requires 'response' or 'result' field"
                )
        
        # For event-driven pattern, ensure event structure
        elif pattern.pattern_type == "event-driven":
            if "event_type" not in output:
                return Err(
                    f"Event-driven pattern requires 'event_type' field"
                )
        
        return Ok(None)
    
    def list_available_patterns(self) -> List[str]:
        """
        List all available pattern IDs.
        
        Returns:
            List of pattern IDs
        """
        return list(self.patterns.keys())
    
    def get_pattern(self, pattern_id: str) -> Optional[CommunicationPattern]:
        """
        Get pattern definition by ID.
        
        Args:
            pattern_id: Pattern ID
            
        Returns:
            CommunicationPattern if found, None otherwise
        """
        return self.patterns.get(pattern_id)
