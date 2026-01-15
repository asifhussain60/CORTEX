# © 2025-2026 Asif Hussain. All rights reserved.
# AC-ID: HP-001-01 - Intent Canonicalization Engine
"""
Extended Intent Canonicalization for Hallucination Prevention.

PHASE-11: Hallucination Prevention System
AC-ID: HP-001-01 - Intent Canonicalization Engine

Extends PHASE-07 IntentCanonicalizer with:
- AC-ID extraction (varied formats: AC-XX-YYY-ZZ, ACXXYYYZZZ, descriptions)
- Phase identification from AC-ID or explicit specification
- Action type classification (CREATE, MODIFY, DELETE, QUERY, EXECUTE, ROLLBACK)

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from src.core.intent.intent_canonicalizer import IntentCanonicalizer, CanonicalizedIntent


# =============================================================================
# ENUMS
# =============================================================================


class ActionType(Enum):
    """Action types for hallucination prevention."""
    CREATE = "CREATE"  # Implement new feature
    MODIFY = "MODIFY"  # Change existing feature
    DELETE = "DELETE"  # Remove feature or AC-ID
    QUERY = "QUERY"    # Information retrieval
    EXECUTE = "EXECUTE"  # Run/test/validate
    ROLLBACK = "ROLLBACK"  # Undo/restore state
    UNKNOWN = "UNKNOWN"


# =============================================================================
# DATA CLASSES
# =============================================================================


@dataclass
class ExtendedCanonicalIntent:
    """Extended canonical intent with AC-ID, phase, and action type.
    
    Attributes:
        base_intent: CanonicalizedIntent from PHASE-07
        ac_id: Extracted AC-ID (format: AC-DOMAIN-NNN-NN)
        phase: Identified phase (e.g., PHASE-11)
        action_type: Classified action type
        ac_id_format: Format of AC-ID (e.g., "standard", "compact", "description")
        phase_confidence: Confidence in phase identification (0.0-1.0)
        action_confidence: Confidence in action classification (0.0-1.0)
        overall_confidence: Combined confidence score (0.0-1.0)
    """
    base_intent: CanonicalizedIntent
    ac_id: Optional[str] = None
    phase: Optional[str] = None
    action_type: ActionType = ActionType.UNKNOWN
    ac_id_format: Optional[str] = None
    phase_confidence: float = 0.0
    action_confidence: float = 0.0
    overall_confidence: float = 0.0
    
    def __post_init__(self) -> None:
        """Validate extended canonical intent."""
        if not (0.0 <= self.phase_confidence <= 1.0):
            raise ValueError("phase_confidence must be between 0.0 and 1.0")
        if not (0.0 <= self.action_confidence <= 1.0):
            raise ValueError("action_confidence must be between 0.0 and 1.0")
        if not (0.0 <= self.overall_confidence <= 1.0):
            raise ValueError("overall_confidence must be between 0.0 and 1.0")


# =============================================================================
# PATTERNS
# =============================================================================


# AC-ID formats to match
AC_ID_FORMATS = {
    "standard": r"AC-([A-Z]{2,})-(\d{3})-(\d{2})",  # AC-XX-YYY-ZZ
    "compact": r"AC([A-Z]{2,})(\d{3})(\d{2})",  # ACXXYYYZZZ
    "description": r"AC-?(?:ID)?[-:\s]*([A-Z]{2,}[-_]?(?:\d{3}[-_]?\d{2}|\d{5}))",  # Description-like
}

# Action type keywords
ACTION_KEYWORDS = {
    ActionType.CREATE: ["implement", "create", "build", "develop", "code", "write", "add", "new"],
    ActionType.MODIFY: ["modify", "change", "update", "edit", "alter", "fix", "improve"],
    ActionType.DELETE: ["delete", "remove", "drop", "eliminate", "unimplement"],
    ActionType.QUERY: ["show", "get", "list", "display", "query", "check", "verify", "status"],
    ActionType.EXECUTE: ["run", "execute", "test", "validate", "deploy", "rollout"],
    ActionType.ROLLBACK: ["rollback", "revert", "undo", "restore", "recover"],
}

# Phase patterns
PHASE_PATTERNS = {
    r"PHASE-(\d{2})": "numbered",  # PHASE-01, PHASE-11
    r"PHASE-([A-Z\-]+)": "named",  # PHASE-PARALLEL, PHASE-ENHANCEMENT-01
}


# =============================================================================
# INTENT CANONICALIZER EXTENSION
# =============================================================================


class ExtendedIntentCanonicalizer:
    """Extended intent canonicalizer with AC-ID and phase extraction.
    
    Extends PHASE-07 IntentCanonicalizer to add:
    - AC-ID extraction and validation
    - Phase identification
    - Action type classification
    """
    
    def __init__(self, base_canonicalizer: Optional[IntentCanonicalizer] = None) -> None:
        """Initialize the extended canonicalizer.
        
        Args:
            base_canonicalizer: Base IntentCanonicalizer from PHASE-07.
                               If None, creates a new one.
        """
        self.base_canonicalizer = base_canonicalizer or IntentCanonicalizer()
        self._compile_patterns()
    
    def _compile_patterns(self) -> None:
        """Compile regex patterns for efficiency."""
        self.ac_id_patterns = {
            name: re.compile(pattern, re.IGNORECASE)
            for name, pattern in AC_ID_FORMATS.items()
        }
        self.phase_patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in PHASE_PATTERNS.keys()
        ]
    
    def canonicalize_extended(
        self, 
        text: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> ExtendedCanonicalIntent:
        """Canonicalize text with extended AC-ID and phase extraction.
        
        Args:
            text: Raw user request text
            context: Optional context (file, project, current phase, etc.)
        
        Returns:
            ExtendedCanonicalIntent with AC-ID, phase, and action type
        """
        # Get base canonicalization from PHASE-07
        base_intent = self.base_canonicalizer.canonicalize(text, context)
        
        # Extract AC-ID
        ac_id, ac_format = self._extract_ac_id(text)
        
        # Identify phase
        phase, phase_conf = self._identify_phase(ac_id, text, context)
        
        # Classify action
        action, action_conf = self._classify_action(text)
        
        # Calculate overall confidence
        overall_conf = self._calculate_overall_confidence(
            base_intent.confidence,
            phase_conf,
            action_conf,
            ac_id is not None
        )
        
        return ExtendedCanonicalIntent(
            base_intent=base_intent,
            ac_id=ac_id,
            phase=phase,
            action_type=action,
            ac_id_format=ac_format,
            phase_confidence=phase_conf,
            action_confidence=action_conf,
            overall_confidence=overall_conf
        )
    
    def extract_ac_id(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract AC-ID from text (public API).
        
        Args:
            text: Text to extract AC-ID from
        
        Returns:
            Tuple of (ac_id, format) or (None, None) if not found
        """
        return self._extract_ac_id(text)
    
    def _extract_ac_id(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract AC-ID from text in multiple formats.
        
        Tries to extract AC-ID in these formats:
        1. Standard: AC-XX-YYY-ZZ
        2. Compact: ACXXYYYZZZ
        3. Description: embedded in text
        
        Args:
            text: Text to search
        
        Returns:
            Tuple of (ac_id, format) or (None, None)
        """
        text_upper = text.upper()
        
        # Try standard format first (most reliable)
        match = self.ac_id_patterns["standard"].search(text_upper)
        if match:
            ac_id = f"AC-{match.group(1)}-{match.group(2)}-{match.group(3)}"
            return (ac_id, "standard")
        
        # Try compact format
        match = self.ac_id_patterns["compact"].search(text_upper)
        if match:
            ac_id = f"AC-{match.group(1)}-{match.group(2)}-{match.group(3)}"
            return (ac_id, "compact")
        
        # Try description format (lowest priority - highest false positive risk)
        match = self.ac_id_patterns["description"].search(text_upper)
        if match:
            ac_id_part = match.group(1).replace("_", "-").replace(" ", "-")
            # Ensure format is AC-XX-YYY-ZZ
            parts = ac_id_part.split("-")
            if len(parts) >= 2:
                # Reconstruct to standard format
                if len(parts) >= 4:
                    ac_id = f"AC-{parts[0]}-{parts[1]}-{parts[2]}"
                    return (ac_id, "description")
        
        return (None, None)
    
    def _identify_phase(
        self,
        ac_id: Optional[str],
        text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[Optional[str], float]:
        """Identify phase from AC-ID or explicit specification.
        
        Args:
            ac_id: Extracted AC-ID (if any)
            text: Raw text
            context: Optional context (current_phase, etc.)
        
        Returns:
            Tuple of (phase, confidence)
        """
        confidence = 0.0
        phase = None
        
        # 1. Check for explicit phase reference (highest priority)
        for pattern in self.phase_patterns:
            match = pattern.search(text)
            if match:
                phase = match.group(0).upper()
                confidence = 0.95  # Explicit reference is very reliable
                return (phase, confidence)
        
        # 2. Try to infer phase from AC-ID domain
        if ac_id:
            domain = ac_id.split("-")[1]  # AC-DOMAIN-NNN-ZZ
            phase, conf = self._infer_phase_from_domain(domain)
            confidence = conf
            if phase:
                return (phase, confidence)
        
        # 3. Use context if available
        if context and "current_phase" in context:
            phase = context["current_phase"]
            confidence = 0.7  # Context is moderately reliable
            return (phase, confidence)
        
        return (None, 0.0)
    
    def _infer_phase_from_domain(self, domain: str) -> Tuple[Optional[str], float]:
        """Infer phase from AC-ID domain.
        
        Maps domain codes to phases:
        - AR: Architecture (PHASE-01 through PHASE-06, PHASE-08)
        - FR: Framework (PHASE-01 through PHASE-06, PHASE-07)
        - NFR: Non-Functional (PHASE-01 through PHASE-06)
        - GV: Governance (PHASE-09)
        - HP: Hallucination Prevention (PHASE-11)
        - etc.
        
        Args:
            domain: Domain code (e.g., "AR", "HP", "GV")
        
        Returns:
            Tuple of (phase, confidence)
        """
        domain_phase_map = {
            "AR": ["PHASE-01", "PHASE-02", "PHASE-03", "PHASE-04", "PHASE-05", "PHASE-06", "PHASE-08"],
            "FR": ["PHASE-01", "PHASE-02", "PHASE-03", "PHASE-04", "PHASE-05", "PHASE-06", "PHASE-07"],
            "NFR": ["PHASE-01", "PHASE-02", "PHASE-03", "PHASE-04", "PHASE-05", "PHASE-06"],
            "IR": ["PHASE-07"],
            "EX": ["PHASE-10"],
            "GV": ["PHASE-09"],
            "HP": ["PHASE-11"],
            "KN": ["PHASE-12"],
            "OB": ["PHASE-13"],
            "PR": ["PHASE-14"],
            "NO": ["PHASE-15"],
        }
        
        phases = domain_phase_map.get(domain, [])
        if phases:
            # If only one possible phase, high confidence
            if len(phases) == 1:
                return (phases[0], 0.8)
            # Multiple phases, moderate confidence (caller should use context)
            else:
                return (phases[0], 0.5)  # Return first, but low confidence
        
        return (None, 0.0)
    
    def _classify_action(self, text: str) -> Tuple[ActionType, float]:
        """Classify action type from text.
        
        Args:
            text: Raw text
        
        Returns:
            Tuple of (action_type, confidence)
        """
        text_lower = text.lower()
        best_action = ActionType.UNKNOWN
        best_score = 0.0
        
        # Score each action type
        for action, keywords in ACTION_KEYWORDS.items():
            score = 0.0
            match_count = 0
            
            for keyword in keywords:
                # Exact word boundary match is more reliable
                if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
                    score += 2.0  # Strong match
                    match_count += 1
                elif keyword in text_lower:
                    score += 1.0  # Weak match (might be part of another word)
            
            # Normalize by keyword length (prioritize lists with more matches)
            # This helps prevent ambiguity
            if match_count > 0:
                score = score / len(keywords)  # Average per keyword
            
            if score > best_score:
                best_score = score
                best_action = action
        
        # Convert score to confidence (normalize)
        confidence = min(best_score, 1.0) if best_score > 0 else 0.0
        
        return (best_action, confidence)
    
    def _calculate_overall_confidence(
        self,
        base_confidence: float,
        phase_confidence: float,
        action_confidence: float,
        has_ac_id: bool
    ) -> float:
        """Calculate overall confidence score.
        
        Combines multiple confidence signals:
        - Base intent confidence (weight: 0.4)
        - Phase identification confidence (weight: 0.3)
        - Action classification confidence (weight: 0.2)
        - AC-ID presence (weight: 0.1)
        
        Args:
            base_confidence: Base intent confidence
            phase_confidence: Phase identification confidence
            action_confidence: Action classification confidence
            has_ac_id: Whether AC-ID was extracted
        
        Returns:
            Overall confidence (0.0-1.0)
        """
        ac_id_bonus = 0.1 if has_ac_id else 0.0
        
        overall = (
            base_confidence * 0.4 +
            phase_confidence * 0.3 +
            action_confidence * 0.2 +
            ac_id_bonus
        )
        
        return min(overall, 1.0)


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "ExtendedIntentCanonicalizer",
    "ExtendedCanonicalIntent",
    "ActionType",
]
