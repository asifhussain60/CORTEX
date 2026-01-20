"""
Canonicalization Engine for HP-001-01

Extended canonicalization with AC-ID, phase, and action type extraction.
Extends PHASE-07 IR-002-01 with production hardening.

Classes:
    IntentCanonicalForm: Data structure for canonicalized intent
    ACIDExtraction: AC-ID extraction utilities
    PhaseClassification: Phase identification utilities
    ActionTypeClassifier: Action type classification
    CanonicalIntentEngine: Main canonicalization engine

Governance: AC-HP-001-01
Tests: tests/unit/tier2/hallucination_prevention/test_hp_001_01_canonicalization.py
"""

import re
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict, field
from datetime import datetime


# =========================================================================
# DATA STRUCTURES
# =========================================================================

@dataclass
class IntentCanonicalForm:
    """Canonical representation of an intent"""
    
    ac_id: Optional[str] = None
    phase: Optional[str] = None
    action_type: Optional[str] = None
    original_text: Optional[str] = None
    normalized_text: Optional[str] = None
    confidence_score: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IntentCanonicalForm":
        """Create from dictionary"""
        return cls(**data)


# =========================================================================
# AC-ID EXTRACTION
# =========================================================================

class ACIDExtraction:
    """AC-ID extraction utilities"""
    
    # Regex patterns for AC-ID recognition
    STRICT_PATTERN = re.compile(r'^AC-[A-Z]{2,4}-\d{3}-\d{2}$')
    LOOSE_PATTERN = re.compile(r'[A-Z]{2,4}-\d{3}-\d{2}')
    IN_TEXT_PATTERN = re.compile(r'\bAC-[A-Z]{2,4}-\d{3}-\d{2}\b')
    
    @staticmethod
    def extract(text: str, validate: bool = False) -> Optional[str]:
        """
        Extract AC-ID from text
        
        Args:
            text: Input text to search
            validate: If True, validate format strictly
            
        Returns:
            Normalized AC-ID or None if not found
        """
        if not text or not isinstance(text, str):
            return None
        
        text = text.strip()
        
        # Normalize separators first
        text_normalized = text.upper().replace("_", "-")
        
        # Try strict format first
        if ACIDExtraction.STRICT_PATTERN.match(text_normalized):
            return text_normalized
        
        # Try to find in text
        match = ACIDExtraction.IN_TEXT_PATTERN.search(text_normalized)
        if match:
            return match.group(0)
        
        # Try loose format
        match = ACIDExtraction.LOOSE_PATTERN.search(text_normalized)
        if match:
            ac_id = match.group(0)
            normalized = f"AC-{ac_id}"
            
            if validate:
                if ACIDExtraction.STRICT_PATTERN.match(normalized):
                    return normalized
            else:
                return normalized
        
        return None
    
    @staticmethod
    def normalize(ac_id: str) -> str:
        """Normalize AC-ID format"""
        if not ac_id:
            return None
        
        ac_id = ac_id.upper().strip()
        
        # Remove common separators and normalize
        ac_id = ac_id.replace("_", "-")
        
        # Ensure AC- prefix
        if not ac_id.startswith("AC-"):
            ac_id = f"AC-{ac_id}"
        
        return ac_id


# =========================================================================
# PHASE CLASSIFICATION
# =========================================================================

class PhaseClassification:
    """Phase identification utilities"""
    
    PHASE_PATTERN = re.compile(r'PHASE-(\d{1,2})', re.IGNORECASE)
    PHASE_NUMBER_ONLY = re.compile(r'^(\d{1,2})$')
    
    # AC-ID to Phase mapping
    AC_ID_PHASE_MAP = {
        "HP": 11,  # Hallucination Prevention
        "IR": 7,   # Intent Router
        "KN": 12,  # Knowledge Ecosystem
        "OB": 13,  # Observability
        "BD": 13,  # Business Domain
    }
    
    @staticmethod
    def classify(text: str, infer_from_ac_id: bool = False, validate: bool = False) -> Optional[str]:
        """
        Classify phase from text
        
        Args:
            text: Input text
            infer_from_ac_id: If True, try to infer from AC-ID
            validate: If True, validate phase exists
            
        Returns:
            Normalized phase name or None
        """
        if not text or not isinstance(text, str):
            return None
        
        text = text.strip()
        
        # Try explicit phase pattern
        match = PhaseClassification.PHASE_PATTERN.search(text.upper())
        if match:
            phase_num = match.group(1).lstrip("0") or "0"
            return f"PHASE-{phase_num}"
        
        # Try phase number only
        match = PhaseClassification.PHASE_NUMBER_ONLY.match(text)
        if match:
            phase_num = match.group(1).lstrip("0") or "0"
            return f"PHASE-{phase_num}"
        
        # Try to infer from AC-ID
        if infer_from_ac_id:
            ac_id = ACIDExtraction.extract(text)
            if ac_id:
                # Extract domain from AC-ID (e.g., HP from AC-HP-001-01)
                parts = ac_id.split("-")
                if len(parts) >= 2:
                    domain = parts[1]
                    if domain in PhaseClassification.AC_ID_PHASE_MAP:
                        phase_num = PhaseClassification.AC_ID_PHASE_MAP[domain]
                        return f"PHASE-{phase_num}"
        
        return None


# =========================================================================
# ACTION TYPE CLASSIFICATION
# =========================================================================

class ActionTypeClassifier:
    """Action type classification utilities"""
    
    ACTION_KEYWORDS = {
        "DELETE": ["delete", "remove", "drop", "eliminate"],
        "MODIFY": ["modify", "change", "update", "edit", "alter"],
        "CREATE": ["create", "new", "generate", "make", "build", "write"],
        "VERIFY": ["verify", "test", "check", "validate", "confirm", "assert"],
        "IMPLEMENT": ["implement", "code", "develop"],
        "EXECUTE": ["execute", "run", "perform", "do", "carry out"],
        "ANALYZE": ["analyze", "review", "examine", "inspect", "audit"],
        "PLAN": ["plan", "design", "architect", "organize"],
    }
    
    @staticmethod
    def classify(text: str) -> Optional[str]:
        """
        Classify action type from text
        
        Args:
            text: Input text
            
        Returns:
            Action type or "UNKNOWN"
        """
        if not text or not isinstance(text, str):
            return "UNKNOWN"
        
        text_lower = text.lower()
        
        # Use ordered matching for priority (more specific actions first)
        for action in ["DELETE", "MODIFY", "CREATE", "VERIFY", "IMPLEMENT", "EXECUTE", "ANALYZE", "PLAN"]:
            keywords = ActionTypeClassifier.ACTION_KEYWORDS[action]
            if any(kw in text_lower for kw in keywords):
                return action
        
        return "UNKNOWN"


# =========================================================================
# CANONICAL INTENT ENGINE
# =========================================================================

class CanonicalIntentEngine:
    """
    Main canonicalization engine for intents
    
    Extends PHASE-07 IR-002-01 with production hardening:
    - AC-ID extraction from varied formats
    - Phase classification from context
    - Action type recognition
    - Confidence scoring
    - Audit trail integration
    """
    
    def __init__(self):
        """Initialize engine with governance integration"""
        # TODO: Integrate with AuditLogger and GovernanceRegistry
        # self.audit_logger = AuditLogger()
        # self.registry = GovernanceRegistry()
        self._audit_cache = {}  # Cache for audit entries
    
    def extract_ac_id(self, text: str, validate: bool = False) -> Optional[str]:
        """Extract AC-ID from text"""
        return ACIDExtraction.extract(text, validate=validate)
    
    def classify_phase(self, text: str, infer_from_ac_id: bool = False, validate: bool = False) -> Optional[str]:
        """Classify phase from text"""
        return PhaseClassification.classify(text, infer_from_ac_id=infer_from_ac_id, validate=validate)
    
    def classify_action(self, text: str) -> str:
        """Classify action type from text"""
        return ActionTypeClassifier.classify(text)
    
    def canonicalize(self, intent: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[IntentCanonicalForm]:
        """
        Canonicalize an intent
        
        Args:
            intent: Raw intent text
            metadata: Additional metadata to preserve
            
        Returns:
            IntentCanonicalForm or None if intent cannot be canonicalized
        """
        if not intent:
            return None
        
        # Extract components
        ac_id = self.extract_ac_id(intent, validate=True)
        phase = self.classify_phase(intent, infer_from_ac_id=True)
        action_type = self.classify_action(intent)
        
        # Skip if no AC-ID found
        if not ac_id:
            return None
        
        # Normalize text
        normalized_text = intent.lower().strip()
        
        # Calculate confidence
        confidence = self._calculate_confidence(ac_id, phase, action_type, intent)
        
        # Create canonical form
        form = IntentCanonicalForm(
            ac_id=ac_id,
            phase=phase,
            action_type=action_type,
            original_text=intent,
            normalized_text=normalized_text,
            confidence_score=confidence,
            metadata=metadata or {}
        )
        
        # Log to audit trail
        self._log_to_audit(form)
        
        return form
    
    def canonicalize_batch(self, intents: List[str]) -> List[IntentCanonicalForm]:
        """
        Canonicalize multiple intents
        
        Args:
            intents: List of intent texts
            
        Returns:
            List of IntentCanonicalForm objects
        """
        results = []
        for intent in intents:
            result = self.canonicalize(intent)
            if result:
                results.append(result)
        return results
    
    def _calculate_confidence(self, ac_id: str, phase: Optional[str], action_type: str, original: str) -> float:
        """
        Calculate confidence score for canonicalization
        
        Returns:
            Score between 0.0 and 1.0
        """
        score = 0.0
        
        # AC-ID found (0.5 points)
        if ac_id:
            score += 0.5
        
        # Phase found (0.25 points)
        if phase:
            score += 0.25
        
        # Action type found (0.15 points)
        if action_type and action_type != "UNKNOWN":
            score += 0.15
        
        # Text length (0.1 points if reasonable)
        if 10 <= len(original) <= 500:
            score += 0.1
        
        return min(score, 1.0)
    
    def _log_to_audit(self, form: IntentCanonicalForm):
        """Log canonicalization to audit trail"""
        if not form.ac_id:
            return
        
        # Create audit entry
        audit_entry = {
            "operation": "CANONICALIZE",
            "ac_id": form.ac_id,
            "phase": form.phase,
            "action_type": form.action_type,
            "confidence": form.confidence_score,
            "timestamp": datetime.now().isoformat(),
        }
        
        # Cache for retrieval
        if form.ac_id not in self._audit_cache:
            self._audit_cache[form.ac_id] = []
        self._audit_cache[form.ac_id].append(audit_entry)
    
    def get_audit_entries(self, ac_id: str) -> List[Dict[str, Any]]:
        """Retrieve audit entries for AC-ID"""
        return self._audit_cache.get(ac_id, [])


# =========================================================================
# MODULE-LEVEL EXPORTS
# =========================================================================

__all__ = [
    "IntentCanonicalForm",
    "ACIDExtraction",
    "PhaseClassification",
    "ActionTypeClassifier",
    "CanonicalIntentEngine",
]
