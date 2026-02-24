"""
Conversational Reflector for Phase 101 Stage 2.

Transforms DoR data into natural language reflections (2 sentences, ≤60 tokens).
Mirrors user vocabulary, avoids technical jargon.

AC_START: AC-CIG-S2-001
AC_COMPLETE: AC-CIG-S2-001 ✅
AC_START: AC-CIG-S2-002
AC_COMPLETE: AC-CIG-S2-002 ✅
AC_START: AC-CIG-S2-003
AC_COMPLETE: AC-CIG-S2-003 ✅
AC_START: AC-CIG-S2-004
AC_COMPLETE: AC-CIG-S2-004 ✅
AC_START: AC-CIG-S2-005
AC_COMPLETE: AC-CIG-S2-005 ✅
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class ConversationalReflection:
    """Natural language reflection of user intent."""
    
    summary: str  # 1-2 sentence summary mirroring user vocabulary
    context: str  # Contextual details (scope, impact)
    confidence: str  # "High confidence (92%)" format
    confidence_score: float  # Raw score (0-1)
    validation_data: Dict[str, Any]  # Background data for orchestrator


class ConversationalReflector:
    """
    Generate natural language reflections from DoR data.
    
    Transforms technical DoR data into conversational 2-sentence summaries
    that mirror user vocabulary and avoid jargon.
    
    Target: ≤60 tokens, 4-second scan time, 85%+ vocabulary match.
    
    Examples:
        >>> reflector = ConversationalReflector()
        >>> dor = {
        ...     "intent_type": "IMPLEMENT",
        ...     "confidence": 0.92,
        ...     "canonical_keywords": ["implement", "authentication", "login"],
        ...     "scope": "module",
        ...     "impact": "medium",
        ...     "user_text": "implement user authentication for login"
        ... }
        >>> reflection = reflector.reflect(dor)
        >>> print(reflection.summary)
        You want to implement user authentication for login to add new functionality.
        >>> print(reflection.confidence)
        High confidence (92%)
    """
    
    def __init__(self) -> None:
        """Initialize conversational reflector."""
        # Intent templates (natural language)
        self.intent_templates = {
            "IMPLEMENT": "implement {target}",
            "FIX": "fix {target}",
            "REFACTOR": "refactor {target}",
            "ANALYZE": "analyze {target}",
            "AUDIT": "audit {target}",
            "UNKNOWN": "work on {target}",
        }
        
        # Rationale templates
        self.rationale_templates = {
            "IMPLEMENT": "to add new functionality",
            "FIX": "to resolve an issue",
            "REFACTOR": "to improve code quality",
            "ANALYZE": "to understand the current state",
            "AUDIT": "to verify compliance",
            "UNKNOWN": "to make changes",
        }
        
        # Scope/impact descriptions
        self.scope_descriptions = {
            "function": "function-level",
            "component": "component-level",
            "module": "module-level",
            "system": "system-level",
            "unclear": "unclear scope",
        }
        
        self.impact_descriptions = {
            "low": "low impact",
            "medium": "medium impact",
            "high": "high impact",
        }
    
    def reflect(self, dor_data: Dict[str, Any]) -> ConversationalReflection:
        """
        Generate conversational reflection from DoR data.
        
        Args:
            dor_data: DoR dictionary with intent_type, confidence, canonical_keywords,
                     scope, impact, user_text
        
        Returns:
            ConversationalReflection with summary, context, confidence, validation_data
        
        Examples:
            >>> reflector = ConversationalReflector()
            >>> dor = {"intent_type": "FIX", "confidence": 0.88, 
            ...        "canonical_keywords": ["fix", "bug"], "scope": "component",
            ...        "impact": "high", "user_text": "fix the login bug"}
            >>> reflection = reflector.reflect(dor)
            >>> "fix" in reflection.summary.lower()
            True
            >>> reflection.confidence_score
            0.88
        """
        intent_type = dor_data.get("intent_type", "UNKNOWN")
        confidence_score = dor_data.get("confidence", 0.5)
        user_text = dor_data.get("user_text", "")
        scope = dor_data.get("scope", "unclear")
        impact = dor_data.get("impact", "medium")
        
        # Extract target from user text or keywords
        target = self._extract_target(user_text, dor_data.get("canonical_keywords", []))
        
        # Generate summary (sentence 1)
        summary = self._generate_summary(intent_type, target)
        
        # Generate context (sentence 2)
        context = self._generate_context(scope, impact)
        
        # Format confidence
        confidence_str = self.format_confidence(confidence_score)
        
        # Store validation data
        validation_data = {
            "intent_type": intent_type,
            "confidence": confidence_score,
            "canonical_keywords": dor_data.get("canonical_keywords", []),
            "scope": scope,
            "impact": impact,
            "urgency": dor_data.get("urgency"),
            "original_dor": dor_data,
        }
        
        return ConversationalReflection(
            summary=summary,
            context=context,
            confidence=confidence_str,
            confidence_score=confidence_score,
            validation_data=validation_data,
        )
    
    def _extract_target(self, user_text: str, keywords: list) -> str:
        """
        Extract target from user text or keywords.
        
        Args:
            user_text: Original user text
            keywords: Canonical keywords
        
        Returns:
            Target phrase (e.g., "user authentication", "the login bug")
        """
        # Remove intent verb from user text
        text_lower = user_text.lower()
        for intent_verb in ["implement", "fix", "refactor", "analyze", "audit"]:
            if text_lower.startswith(intent_verb):
                text_lower = text_lower[len(intent_verb):].strip()
                break
        
        # Remove articles and clean up
        text_lower = text_lower.strip()
        if not text_lower:
            # Fallback to keywords
            non_intent_keywords = [k for k in keywords if k not in ["implement", "fix", "refactor", "analyze", "audit"]]
            return " ".join(non_intent_keywords[:3]) if non_intent_keywords else "the codebase"
        
        # Return cleaned target
        return text_lower if text_lower else "the codebase"
    
    def _generate_summary(self, intent_type: str, target: str) -> str:
        """
        Generate natural language summary sentence.
        
        Args:
            intent_type: IMPLEMENT, FIX, REFACTOR, ANALYZE, AUDIT, UNKNOWN
            target: Target phrase
        
        Returns:
            Natural language sentence (e.g., "You want to implement user authentication to add new functionality.")
        """
        template = self.intent_templates.get(intent_type, self.intent_templates["UNKNOWN"])
        action = template.format(target=target)
        rationale = self.generate_rationale(intent_type)
        
        return f"You want to {action} {rationale}."
    
    def _generate_context(self, scope: str, impact: str) -> str:
        """
        Generate contextual sentence (scope + impact).
        
        Args:
            scope: function, component, module, system, unclear
            impact: low, medium, high
        
        Returns:
            Context sentence (e.g., "This involves module-level changes with medium impact.")
        """
        scope_desc = self.scope_descriptions.get(scope, "unclear scope")
        impact_desc = self.impact_descriptions.get(impact, "medium impact")
        
        return f"This involves {scope_desc} changes with {impact_desc}."
    
    def generate_rationale(self, intent_type: str) -> str:
        """
        Generate rationale phrase for intent type.
        
        Args:
            intent_type: IMPLEMENT, FIX, REFACTOR, ANALYZE, AUDIT, UNKNOWN
        
        Returns:
            Rationale phrase (e.g., "to add new functionality")
        
        Examples:
            >>> reflector = ConversationalReflector()
            >>> reflector.generate_rationale("IMPLEMENT")
            'to add new functionality'
            >>> reflector.generate_rationale("FIX")
            'to resolve an issue'
        """
        return self.rationale_templates.get(intent_type, self.rationale_templates["UNKNOWN"])
    
    def format_confidence(self, score: float) -> str:
        """
        Format confidence score as natural language.
        
        Args:
            score: Confidence score (0-1)
        
        Returns:
            Formatted string (e.g., "High confidence (92%)")
        
        Examples:
            >>> reflector = ConversationalReflector()
            >>> reflector.format_confidence(0.92)
            'High confidence (92%)'
            >>> reflector.format_confidence(0.70)
            'Medium confidence (70%)'
            >>> reflector.format_confidence(0.45)
            'Low confidence (45%)'
        """
        percentage = int(score * 100)
        
        if score >= 0.90:
            level = "High confidence"
        elif score >= 0.60:
            level = "Medium confidence"
        else:
            level = "Low confidence"
        
        return f"{level} ({percentage}%)"
