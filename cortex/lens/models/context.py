"""
Canonical LENSContext model (Phase 65 S6).

Single source of truth for LENS operation context across all consumers.
Consolidates fields from multiple previous LENSContext implementations.

Authority: AC-PHASE65-S6-001
Purpose: CORE-035 compliance - eliminate duplicate LENSContext classes
"""

# AC_START: AC-PHASE65-S6-001
# Description: Phase 65 S6 - Canonical LENSContext implementation

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime


@dataclass
class LENSContext:
    """
    Canonical LENS operation context.
    
    Consolidates all fields from previous LENSContext implementations:
    - cortex/orchestrators/core/lens_synthesis.py::LENSContext
    - cortex/lens/context_provider.py::LENSContext (if existed)
    - Other scattered LENSContext definitions
    
    Fields:
        operation: LENS operation type ("analyze", "navigate", "synthesize")
        language_analysis: Language-specific analysis results
        code_examination: Code structure examination results
        domain_navigation: Domain entity navigation results
        synthesis_output: Final synthesis recommendations
        timestamp: Operation timestamp
        turn_number: Turn number in multi-turn session
    
    Authority: Phase 65 S6-T1
    """
    
    operation: str
    language_analysis: Dict[str, Any] = field(default_factory=dict)
    code_examination: Dict[str, Any] = field(default_factory=dict)
    domain_navigation: Dict[str, Any] = field(default_factory=dict)
    synthesis_output: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    turn_number: int = 1
    
    # Optional fields for extended use cases
    file_path: Optional[str] = None
    repo_path: Optional[str] = None
    intent: Optional[str] = None
    session_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'operation': self.operation,
            'language_analysis': self.language_analysis,
            'code_examination': self.code_examination,
            'domain_navigation': self.domain_navigation,
            'synthesis_output': self.synthesis_output,
            'timestamp': self.timestamp.isoformat(),
            'turn_number': self.turn_number,
            'file_path': self.file_path,
            'repo_path': self.repo_path,
            'intent': self.intent,
            'session_id': self.session_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LENSContext':
        """Create from dictionary representation."""
        # Parse timestamp
        timestamp_str = data.get('timestamp')
        if isinstance(timestamp_str, str):
            timestamp = datetime.fromisoformat(timestamp_str)
        else:
            timestamp = datetime.now()
        
        return cls(
            operation=data['operation'],
            language_analysis=data.get('language_analysis', {}),
            code_examination=data.get('code_examination', {}),
            domain_navigation=data.get('domain_navigation', {}),
            synthesis_output=data.get('synthesis_output', {}),
            timestamp=timestamp,
            turn_number=data.get('turn_number', 1),
            file_path=data.get('file_path'),
            repo_path=data.get('repo_path'),
            intent=data.get('intent'),
            session_id=data.get('session_id')
        )


__all__ = ["LENSContext"]

# AC_COMPLETE: AC-PHASE65-S6-001 ✅ Canonical LENSContext complete
