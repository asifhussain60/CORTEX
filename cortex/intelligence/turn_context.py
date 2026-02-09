"""
Turn-Over-Turn Intelligence Accumulation.

Session-scoped storage for accumulated intelligence across multiple turns.
Each turn's discoveries (entities, patterns, standards, files, violations) 
persist in-memory for subsequent turn reference.

Authority: AC-PHASE65-S5-001
"""

# AC_START: AC-PHASE65-S5-001
# Description: Phase 65 S5 - Turn-Over-Turn Intelligence Accumulation

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional
from datetime import datetime
from collections import deque
import logging

logger = logging.getLogger(__name__)


@dataclass
class TurnEntry:
    """Single turn's intelligence accumulation."""
    
    turn_number: int
    timestamp: datetime = field(default_factory=datetime.now)
    entities_discovered: List[str] = field(default_factory=list)
    patterns_detected: List[str] = field(default_factory=list)
    standards_applied: List[str] = field(default_factory=list)
    files_analyzed: List[str] = field(default_factory=list)
    violations: List[str] = field(default_factory=list)


class TurnContext:
    """
    Session-scoped intelligence accumulator.
    
    Stores discovered entities, patterns, standards, files, and violations
    across multiple turns. Memory-bounded with LRU eviction.
    
    Attributes:
        session_id: Unique session identifier
        max_turns: Maximum turns to store (default 100)
        turns: Deque of TurnEntry objects (LRU eviction)
    """
    
    def __init__(self, session_id: str, max_turns: int = 100):
        """
        Initialize turn context.
        
        Args:
            session_id: Unique session identifier
            max_turns: Maximum turns to store before LRU eviction
        """
        self.session_id = session_id
        self.max_turns = max_turns
        self.turns: deque[TurnEntry] = deque(maxlen=max_turns)
        logger.info(f"TurnContext initialized: session={session_id}, max_turns={max_turns}")
    
    def add_turn_entry(
        self,
        turn_number: int,
        entities_discovered: Optional[List[str]] = None,
        patterns_detected: Optional[List[str]] = None,
        standards_applied: Optional[List[str]] = None,
        files_analyzed: Optional[List[str]] = None,
        violations: Optional[List[str]] = None
    ) -> None:
        """
        Add intelligence from a single turn.
        
        Args:
            turn_number: Turn sequence number
            entities_discovered: Entities found this turn (classes, functions, etc.)
            patterns_detected: Design patterns detected
            standards_applied: CORE rules or standards referenced
            files_analyzed: Files analyzed this turn
            violations: Rule violations detected
        """
        entry = TurnEntry(
            turn_number=turn_number,
            entities_discovered=entities_discovered or [],
            patterns_detected=patterns_detected or [],
            standards_applied=standards_applied or [],
            files_analyzed=files_analyzed or [],
            violations=violations or []
        )
        
        self.turns.append(entry)
        
        # Log if LRU eviction occurred
        if len(self.turns) == self.max_turns:
            logger.debug(f"TurnContext LRU: evicted oldest turn (session={self.session_id})")
    
    def get_accumulated_entities(self) -> List[str]:
        """
        Get all entities discovered across all turns.
        
        Returns:
            List of unique entity names
        """
        entities = set()
        for turn in self.turns:
            entities.update(turn.entities_discovered)
        return list(entities)
    
    def get_accumulated_patterns(self) -> List[str]:
        """
        Get all patterns detected across all turns.
        
        Returns:
            List of unique pattern names
        """
        patterns = set()
        for turn in self.turns:
            patterns.update(turn.patterns_detected)
        return list(patterns)
    
    def get_accumulated_standards(self) -> List[str]:
        """
        Get all standards applied across all turns.
        
        Returns:
            List of unique standard references
        """
        standards = set()
        for turn in self.turns:
            standards.update(turn.standards_applied)
        return list(standards)
    
    def get_analyzed_files(self) -> List[str]:
        """
        Get all files analyzed across all turns.
        
        Returns:
            List of unique file paths
        """
        files = set()
        for turn in self.turns:
            files.update(turn.files_analyzed)
        return list(files)
    
    def get_accumulated_violations(self) -> List[str]:
        """
        Get all violations detected across all turns.
        
        Returns:
            List of all violations (not deduplicated - track frequency)
        """
        violations = []
        for turn in self.turns:
            violations.extend(turn.violations)
        return violations
    
    def needs_analysis(self, file_path: str) -> bool:
        """
        Check if file needs analysis.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file not yet analyzed, False otherwise
        """
        analyzed = set(self.get_analyzed_files())
        return file_path not in analyzed
    
    def get_entities_from_turn(self, turn_number: int) -> List[str]:
        """
        Get entities discovered in specific turn.
        
        Args:
            turn_number: Turn to query
            
        Returns:
            List of entities from that turn, empty if not found
        """
        for turn in self.turns:
            if turn.turn_number == turn_number:
                return turn.entities_discovered
        return []
    
    def get_turn_count(self) -> int:
        """
        Get current number of stored turns.
        
        Returns:
            Number of turns in memory
        """
        return len(self.turns)
    
    def get_accumulated_context(self) -> Dict[str, List[str]]:
        """
        Get complete accumulated context for session.
        
        Returns:
            Dictionary with entities, patterns, standards, files, violations
        """
        return {
            'entities': self.get_accumulated_entities(),
            'patterns': self.get_accumulated_patterns(),
            'standards': self.get_accumulated_standards(),
            'files': self.get_analyzed_files(),
            'violations': self.get_accumulated_violations()
        }
    
    def clear(self) -> None:
        """Clear all accumulated context for session."""
        self.turns.clear()
        logger.info(f"TurnContext cleared: session={self.session_id}")


# Global turn context registry
_turn_contexts: Dict[str, TurnContext] = {}


def get_turn_context(session_id: str, max_turns: int = 100) -> TurnContext:
    """
    Get or create turn context for session.
    
    Args:
        session_id: Session identifier
        max_turns: Maximum turns to store
        
    Returns:
        TurnContext for session
    """
    if session_id not in _turn_contexts:
        _turn_contexts[session_id] = TurnContext(session_id, max_turns)
    return _turn_contexts[session_id]


def clear_turn_context(session_id: str) -> None:
    """
    Clear turn context for session.
    
    Args:
        session_id: Session to clear
    """
    if session_id in _turn_contexts:
        _turn_contexts[session_id].clear()
        del _turn_contexts[session_id]
        logger.info(f"TurnContext removed: session={session_id}")


# AC_COMPLETE: AC-PHASE65-S5-001 ✅ TurnContext implementation complete
