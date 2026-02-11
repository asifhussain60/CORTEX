"""
RoleResolver: Infer user roles from context signals
Authority: Phase 37 S2, CORE-008 (TDD-first)

Detects user roles based on:
- Explicit keywords ("engineer", "product owner", etc.)
- Context signals (interest in code, metrics, process, architecture)
- Inference memory (previous role detections for user)
- Optional context dict (job title, department, etc.)
"""

import re
from enum import Enum
from typing import Any, Dict, Optional, Tuple

from cortex.orchestrators.persona.models import PersonaId
from cortex.orchestrators.persona.persona_loader import PersonaLoader


class RoleResolver:
    """
    Infer user roles from context signals with memory and confidence scoring.

    Attributes:
        loader: PersonaLoader instance for accessing persona configurations
        inference_history: Dict mapping user_id to their detected PersonaId
    """

    # Role detection keywords and their associated PersonaId
    ROLE_KEYWORDS = {
        PersonaId.ENGINEER: [
            "engineer",
            "developer",
            "programmer",
            "coder",
            "dev",
            "software engineer",
            "senior engineer",
            "junior engineer",
        ],
        PersonaId.PRODUCT_OWNER: [
            "product owner",
            "product manager",
            "pm",
            "product lead",
            "feature owner",
        ],
        PersonaId.SCRUM_MASTER: [
            "scrum master",
            "scrum",
            "agile coach",
            "agile master",
            "process lead",
        ],
        PersonaId.TECH_LEAD: [
            "tech lead",
            "engineering manager",
            "team lead",
            "technical leader",
            "engineering leader",
            "architect",
        ],
        PersonaId.BUSINESS_LEADER: [
            "cto",
            "ceo",
            "cfo",
            "vp",
            "director",
            "executive",
            "c-suite",
            "business leader",
            "business executive",
        ],
    }

    # Context signals that indicate role preferences
    CONTEXT_SIGNALS = {
        PersonaId.ENGINEER: [
            "code",
            "refactor",
            "implementation",
            "test",
            "coverage",
            "algorithm",
            "function",
            "class",
            "method",
            "debug",
            "error",
            "bug",
            "compile",
            "runtime",
        ],
        PersonaId.PRODUCT_OWNER: [
            "feature",
            "roadmap",
            "user",
            "requirement",
            "specification",
            "velocity",
            "user story",
            "epic",
        ],
        PersonaId.SCRUM_MASTER: [
            "sprint",
            "velocity",
            "blocker",
            "standup",
            "retrospective",
            "planning",
            "process",
            "ceremony",
            "agile",
            "scrum",
        ],
        PersonaId.TECH_LEAD: [
            "architecture",
            "tech debt",
            "health metrics",
            "complexity",
            "design",
            "system design",
            "api",
            "scalability",
        ],
        PersonaId.BUSINESS_LEADER: [
            "roi",
            "rois",
            "kpi",
            "kpis",
            "business",
            "revenue",
            "stakeholder",
            "stakeholders",
            "quarterly",
            "metrics",
        ],
    }

    def __init__(self, loader: PersonaLoader) -> None:
        """
        Initialize RoleResolver with PersonaLoader.

        Args:
            loader: PersonaLoader instance
        """
        self.loader = loader
        self.inference_history: Dict[str, PersonaId] = {}

    def infer_role(
        self,
        message: str,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        use_memory: bool = True,
    ) -> Tuple[PersonaId, float]:
        """
        Infer user role from message with optional context.

        Args:
            message: User message text
            user_id: Optional user identifier for memory tracking
            context: Optional context dict with signals (job_title, etc.)
            use_memory: Whether to use inference history for ambiguous messages

        Returns:
            Tuple of (PersonaId, confidence_score 0.0-1.0)
        """
        # Handle empty message
        if not message or not message.strip():
            return PersonaId.ENGINEER, 0.0

        # Normalize message
        message_lower = message.lower()

        # Infer from message first (most reliable signal)
        message_persona, message_confidence = self._infer_from_message(
            message_lower
        )

        # If message gave strong signal, use it
        if message_confidence >= 0.8:
            if user_id:
                self.inference_history[user_id] = message_persona
            return message_persona, message_confidence

        # Try context for weak message signals
        if context:
            context_persona, context_confidence = self._infer_from_context(
                context
            )
            if context_confidence >= 0.6 and message_confidence < 0.5:
                # Use context if message was weak
                if user_id:
                    self.inference_history[user_id] = context_persona
                return context_persona, context_confidence
            elif context_confidence > message_confidence and message_confidence < 0.5:
                # Context is better and message was weak
                if user_id:
                    self.inference_history[user_id] = context_persona
                return context_persona, context_confidence

        # Use message inference
        if message_confidence >= 0.5 and user_id:
            self.inference_history[user_id] = message_persona

        # If low confidence and memory available, use memory
        if message_confidence < 0.5 and use_memory and user_id:
            if user_id in self.inference_history:
                return self.inference_history[user_id], message_confidence

        return message_persona, message_confidence

    def _infer_from_message(self, message_lower: str) -> Tuple[PersonaId, float]:
        """
        Infer role from message keywords and context signals.

        Args:
            message_lower: Lowercase message text

        Returns:
            Tuple of (PersonaId, confidence_score)
        """
        persona_scores: Dict[PersonaId, float] = {
            persona: 0.0 for persona in PersonaId
        }

        # Score based on keywords (high weight - specific and deliberate)
        # Use word boundaries to avoid substring matches (e.g., "cto" in "refactor")
        keyword_found = False
        for persona, keywords in self.ROLE_KEYWORDS.items():
            for keyword in keywords:
                # Use word boundary regex to match whole words only
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, message_lower):
                    persona_scores[persona] += 1.0
                    keyword_found = True

        # If any keyword matched, use only keyword scores
        if keyword_found:
            best_persona = PersonaId.ENGINEER
            best_score = 0.0

            for persona, score in persona_scores.items():
                if score > best_score:
                    best_score = score
                    best_persona = persona

            confidence = min(best_score, 1.0)
            return best_persona, confidence

        # Score based on context signals only if no keywords matched
        for persona, signals in self.CONTEXT_SIGNALS.items():
            signal_matches = sum(
                1 for signal in signals
                if re.search(r'\b' + re.escape(signal) + r'\b', message_lower)
            )
            if signal_matches > 0:
                # Multiple signals increase confidence
                persona_scores[persona] += 0.3 * min(signal_matches, 3)

        # Find persona with highest score
        best_persona = PersonaId.ENGINEER
        best_score = 0.0

        for persona, score in persona_scores.items():
            if score > best_score:
                best_score = score
                best_persona = persona

        # Normalize to 0.0-1.0 range
        confidence = min(best_score / 1.0, 1.0)

        # Default to engineer if confidence is too low
        if confidence < 0.5:
            return PersonaId.ENGINEER, confidence

        return best_persona, confidence

    def _infer_from_context(
        self, context: Dict[str, Any]
    ) -> Tuple[PersonaId, float]:
        """
        Infer role from context dict (job_title, department, etc).

        Args:
            context: Context dict with optional keys:
                - job_title: str
                - department: str
                - current_role: PersonaId
                - experience_level: str

        Returns:
            Tuple of (PersonaId, confidence_score)
        """
        confidence = 0.0
        best_persona = PersonaId.ENGINEER

        # Check current_role
        if "current_role" in context:
            current_role = context["current_role"]
            if isinstance(current_role, PersonaId):
                return current_role, 0.6

        # Check job_title
        if "job_title" in context:
            job_title = context["job_title"].lower()

            if any(kw in job_title for kw in self.ROLE_KEYWORDS[PersonaId.ENGINEER]):
                best_persona = PersonaId.ENGINEER
                confidence = 0.7
            elif any(kw in job_title for kw in self.ROLE_KEYWORDS[PersonaId.TECH_LEAD]):
                best_persona = PersonaId.TECH_LEAD
                confidence = 0.75
            elif any(kw in job_title for kw in self.ROLE_KEYWORDS[PersonaId.PRODUCT_OWNER]):
                best_persona = PersonaId.PRODUCT_OWNER
                confidence = 0.7
            elif any(kw in job_title for kw in self.ROLE_KEYWORDS[PersonaId.BUSINESS_LEADER]):
                best_persona = PersonaId.BUSINESS_LEADER
                confidence = 0.8

        # Check department
        if "department" in context and confidence < 0.7:
            department = context["department"].lower()

            if "engineering" in department:
                best_persona = PersonaId.ENGINEER
                confidence = max(confidence, 0.6)
            elif "product" in department:
                best_persona = PersonaId.PRODUCT_OWNER
                confidence = max(confidence, 0.6)
            elif "executive" in department or "leadership" in department:
                best_persona = PersonaId.BUSINESS_LEADER
                confidence = max(confidence, 0.6)

        return best_persona, confidence
