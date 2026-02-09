"""
Phase Context Resolver - Multi-Session Continuity System

Enables users to pick up where they left off across chat sessions by:
1. Scanning previous session chat files for phase references
2. Extracting last completed phase and queued phases
3. Building a canonical phase map from SDLC plans
4. Resolving ambiguous phase references (e.g., "phase C" → Phase 7)

Authority: ENH-017 (cortex-architect enhancement)
Status: Core infrastructure for multi-session continuity
"""

import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import json


@dataclass
class PhaseContext:
    """Represents extracted phase context from a session or SDLC plan."""
    session_file: str  # Path to chat session (e.g., chat01.md)
    last_completed_phase: Optional[str] = None  # Phase ID (e.g., "phase-21-1")
    last_completed_title: Optional[str] = None  # Phase title
    queued_phases: List[str] = None  # Next phases in order
    all_phases_map: Dict[str, Dict[str, Any]] = None  # All known phases
    phase_numbering: str = "unknown"  # "numeric" (0-6), "letter" (A-C), "mixed"
    extracted_at: str = None
    confidence: float = 1.0  # 0.0-1.0
    
    def __post_init__(self):
        if self.queued_phases is None:
            self.queued_phases = []
        if self.all_phases_map is None:
            self.all_phases_map = {}
        if self.extracted_at is None:
            self.extracted_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Export context as dictionary (JSON-serializable)."""
        return asdict(self)
    
    @staticmethod
    def from_dict(data: Dict) -> "PhaseContext":
        """Import context from dictionary."""
        return PhaseContext(**data)


class PhaseContextResolver:
    """
    Resolves phase references across sessions and SDLC plans.
    
    Usage:
        resolver = PhaseContextResolver(chat_file="/path/to/chat01.md")
        context = resolver.extract_context()
        
        # Later, in a new session:
        resolver2 = PhaseContextResolver(chat_file="/path/to/chat02.md")
        next_phase = resolver2.resolve_phase_reference("phase C")
        # → "phase-21-7" with title "Prompt & Agent Updates"
    """
    
    # Regex patterns for phase detection
    PHASE_PATTERNS = [
        (r"##\s+🚀\s+(?:Next\s+)?Phase\s+(?:Preview)?:?\s+Phase\s+(\d+)[:\s]+(.+?)(?:\n|$)", "numbered_section"),
        (r"##\s+(?:Phase|PHASE))\s+(\d+)(?:/[A-Z])?:\s+(.+?)(?:\n|$)", "phase_header"),
        (r"\*\*Phase\s+(\d+)\*\*\s+\|\s+([^|]+)\s+\|", "table_row"),
        (r"\|\s+\*\*(\d+)\*\*\s+\|\s+(.+?)\s+\|", "alt_table_row"),
        (r"Phase\s+([A-Z])(?:\s|:|$)\s*(.+?)(?:\n|$)", "letter_phase"),
    ]
    
    def __init__(self, chat_file: str, sdlc_plan: Optional[str] = None):
        """
        Initialize resolver.
        
        Args:
            chat_file: Path to previous session chat (e.g., chat01.md)
            sdlc_plan: Path to SDLC plan YAML (auto-detected if None)
        """
        self.chat_file = Path(chat_file)
        self.sdlc_plan = Path(sdlc_plan) if sdlc_plan else self._find_sdlc_plan()
        self._context_cache = None
    
    @staticmethod
    def _find_sdlc_plan() -> Path:
        """Auto-detect SDLC plan in workspace."""
        candidates = [
            # Primary: cortex-registry (canonical location post-migration)
            Path("/Users/asifhussain/PROJECTS/CORTEX/cortex-registry/_cortex-master/phases/active/phase-21-json-first-rewrite.yaml"),
            Path("/Users/asifhussain/PROJECTS/CORTEX/cortex-registry/_cortex-master/meta/cortex-self-improvement-sdlc.yaml"),
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        raise FileNotFoundError("Cannot auto-detect SDLC plan. Provide explicit path.")
    
    def extract_context(self, use_cache: bool = True) -> PhaseContext:
        """
        Extract phase context from chat file.
        
        Returns:
            PhaseContext with last completed phase and queued phases
        """
        if use_cache and self._context_cache:
            return self._context_cache
        
        # Read chat file
        if not self.chat_file.exists():
            return PhaseContext(session_file=str(self.chat_file), confidence=0.0)
        
        chat_content = self.chat_file.read_text()
        
        # Extract phases in order of appearance
        phases_found = self._extract_phases_from_chat(chat_content)
        last_completed = self._find_last_completed_phase(chat_content, phases_found)
        queued = self._find_queued_phases(chat_content, phases_found)
        numbering = self._detect_numbering_system(phases_found)
        
        # Load all phases from SDLC plan for reference
        all_phases_map = self._load_sdlc_phases()
        
        context = PhaseContext(
            session_file=str(self.chat_file),
            last_completed_phase=last_completed.get("id") if last_completed else None,
            last_completed_title=last_completed.get("title") if last_completed else None,
            queued_phases=queued,
            all_phases_map=all_phases_map,
            phase_numbering=numbering,
        )
        
        self._context_cache = context
        return context
    
    def _extract_phases_from_chat(self, content: str) -> List[Dict[str, str]]:
        """Extract all phase references from chat content."""
        phases = []
        
        for pattern, pattern_type in self.PHASE_PATTERNS:
            for match in re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE):
                if pattern_type == "letter_phase":
                    phase_id = f"phase-{match.group(1).upper()}"
                    title = match.group(2).strip()
                else:
                    phase_id = f"phase-{match.group(1)}"
                    title = match.group(2).strip()
                
                phases.append({
                    "id": phase_id,
                    "title": title,
                    "pattern_type": pattern_type,
                })
        
        return phases
    
    def _find_last_completed_phase(self, content: str, phases: List[Dict]) -> Optional[Dict]:
        """
        Find last completed phase by looking for completion markers.
        
        Markers:
        - "✅ Phase X GREEN"
        - "all X tests passing"
        - "Phase X: ... (GREEN ✅)"
        """
        completion_patterns = [
            r"✅\s+Phase\s+(\d+)\s+GREEN",
            r"Phase\s+(\d+).*?✅.*?(?:passing|complete))",
            r"Phase\s+([A-Z])\s+.*?✅",
        ]
        
        last_completed_num = None
        for pattern in completion_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                # Get the highest phase number found
                nums = []
                for m in matches:
                    try:
                        nums.append(int(m))
                    except ValueError:
                        pass
                if nums:
                    last_completed_num = max(nums)
                    break
        
        if last_completed_num is not None:
            for phase in phases:
                if str(last_completed_num) in phase["id"]:
                    return phase
        
        return None
    
    def _find_queued_phases(self, content: str, phases: List[Dict]) -> List[str]:
        """Extract phases marked as queued/pending."""
        queued = []
        
        # Look for "Remaining Phases" or "Queued" sections
        queued_section = re.search(
            r"(?:Remaining|Queued)|Next)\s+Phases.*?\n(.*?)(?:\n\n|\n###|\Z)",
            content,
            re.IGNORECASE | re.DOTALL
        )
        
        if queued_section:
            section = queued_section.group(1)
            # Extract phase numbers/letters from table or list
            phase_matches = re.findall(r"\*\*Phase\s+(\d+|[A-Z])\*\*", section, re.IGNORECASE)
            
            for match in phase_matches:
                if match.isdigit():
                    queued.append(f"phase-{int(match)}")
                else:
                    queued.append(f"phase-{match.upper()}")
        
        return queued
    
    def _detect_numbering_system(self, phases: List[Dict]) -> str:
        """Detect if phases use numeric (0-6), letter (A-C), or mixed naming."""
        has_numeric = any(re.search(r"\d", p["id"]) for p in phases)
        has_letter = any(re.search(r"[A-Z]", p["id"]) for p in phases)
        
        if has_numeric and has_letter:
            return "mixed"
        elif has_letter:
            return "letter"
        else:
            return "numeric"
    
    def _load_sdlc_phases(self) -> Dict[str, Dict[str, Any]]:
        """Load all phases from SDLC plan YAML."""
        if not self.sdlc_plan.exists():
            return {}
        
        try:
            with open(self.sdlc_plan) as f:
                sdlc_data = yaml.safe_load(f)
            
            phases_map = {}
            if "implementation_phases" in sdlc_data:
                for phase_key, phase_data in sdlc_data["implementation_phases"].items():
                    phase_id = phase_key.replace("_", "-")
                    phases_map[phase_id] = {
                        "title": phase_data.get("title", ""),
                        "duration": phase_data.get("duration", ""),
                        "effort": phase_data.get("duration", ""),
                    }
            
            return phases_map
        except Exception as e:
            print(f"Warning: Could not load SDLC phases: {e}")
            return {}
    
    def resolve_phase_reference(self, user_input: str, context: Optional[PhaseContext] = None) -> Tuple[str, str, float]:
        """
        Resolve ambiguous phase reference to canonical phase ID.
        
        Args:
            user_input: User's phase reference (e.g., "phase C", "phase 7", "next phase")
            context: Optional pre-extracted context
        
        Returns:
            Tuple of (phase_id, title, confidence)
            Example: ("phase-7", "Prompt & Agent Updates", 0.95)
        
        Raises:
            ValueError: If phase cannot be resolved
        """
        if context is None:
            context = self.extract_context()
        
        user_input = user_input.strip().lower()
        
        # Handle "next phase" / "continue" 
        if "next" in user_input or "continue" in user_input:
            if context.queued_phases:
                next_phase_id = context.queued_phases[0]
                title = context.all_phases_map.get(next_phase_id, {}).get("title", "Unknown")
                return (next_phase_id, title, 0.99)
            else:
                raise ValueError(f"No queued phases found in context. Last completed: {context.last_completed_phase}")
        
        # Handle explicit phase references
        # "phase 7", "phase-7", "phase C", "C"
        explicit_match = re.search(r"phase\s*[\-]?\s*([0-9a-z])", user_input, re.IGNORECASE)
        if explicit_match:
            phase_ref = explicit_match.group(1)
            
            # Try numeric lookup first
            if phase_ref.isdigit():
                phase_id = f"phase-{int(phase_ref)}"
                if phase_id in context.all_phases_map:
                    title = context.all_phases_map[phase_id].get("title", "Unknown")
                    return (phase_id, title, 0.95)
            
            # Try letter lookup
            phase_id = f"phase-{phase_ref.upper()}"
            if phase_id in context.all_phases_map:
                title = context.all_phases_map[phase_id].get("title", "Unknown")
                return (phase_id, title, 0.90)
            
            # Letter might map to letter-based phases (A=1, B=2, etc)
            letter_num = ord(phase_ref.upper()) - ord("A")
            numeric_phase = f"phase-{letter_num}"
            if numeric_phase in context.all_phases_map:
                title = context.all_phases_map[numeric_phase].get("title", "Unknown")
                return (numeric_phase, title, 0.85)
        
        raise ValueError(
            f"Cannot resolve phase reference: '{user_input}'. "
            f"Queued phases: {context.queued_phases}. "
            f"Last completed: {context.last_completed_phase}"
        )
    
    def build_continuation_context(self) -> Dict[str, Any]:
        """
        Build a comprehensive context for session continuation.
        
        Used by cortex-architect to understand where we are in the SDLC.
        
        Returns:
            Dictionary with all context needed to continue seamlessly
        """
        context = self.extract_context()
        
        return {
            "session_file": context.session_file,
            "last_completed": {
                "phase_id": context.last_completed_phase,
                "title": context.last_completed_title,
            },
            "queued": context.queued_phases,
            "next_recommended": context.queued_phases[0] if context.queued_phases else None,
            "numbering_system": context.phase_numbering,
            "all_phases": context.all_phases_map,
            "extraction_confidence": context.confidence,
            "extracted_at": context.extracted_at,
        }


# Convenience functions for CLI / MCP exposure
def extract_session_context(chat_file: str) -> Dict[str, Any]:
    """Quick extraction (for MCP tool)."""
    resolver = PhaseContextResolver(chat_file)
    return resolver.build_continuation_context()


def resolve_phase(user_input: str, chat_file: str) -> Tuple[str, str]:
    """Quick phase resolution (for MCP tool)."""
    resolver = PhaseContextResolver(chat_file)
    phase_id, title, confidence = resolver.resolve_phase_reference(user_input)
    return (phase_id, title)
