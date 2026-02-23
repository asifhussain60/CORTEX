"""
PreFlightRequestTransformer (PFRT) - Stage 0 Orchestration Layer.

Transforms verbose, repetitive user requests into crystallized single-paragraph
intents optimized for MasterOrchestrator processing.

AC_START: AC-CORE-PFRT-20260223T000000Z
Description: Pre-Flight Request Transformer - Stage 0 orchestration layer
"""

import re
from typing import Dict, Optional


class PreFlightRequestTransformer:
    """
    Stage 0 orchestrator for request clarity transformation.
    
    Responsibilities:
    - Remove redundant phrases and repetition
    - Synthesize multiple concerns into unified intent
    - Preserve technical terms and constraints
    - Convert uncertainty to decisive language
    - Flag anti-pattern directives
    - Inject classification hints for IntentRouter
    
    Pipeline Position: Stage 0 (before InteractionOrchestrator)
    """

    # Redundancy patterns to remove
    REDUNDANT_PATTERNS = [
        r"\b(but make sure|also check|just make sure|oh and|by the way)\b",
        r"\b(maybe|perhaps|not sure|I think|I was thinking)\b",
        r"\b(you know|kind of|sort of|like)\b",
        r"\b(thanks!?|please)\s*$",
    ]

    # Uncertainty markers to normalize
    UNCERTAINTY_MARKERS = {
        "maybe": "",
        "perhaps": "",
        "could": "should",
        "might": "will",
        "not sure": "",
    }

    # Anti-patterns that violate CORTEX principles
    ANTI_PATTERNS = {
        "skip tests": "implement with TDD validation",
        "ignore tests": "fix test failures",
        "no tests": "include test coverage",
        "quick fix": "implement properly",
        "just hack": "implement following CORE rules",
    }

    # Intent classification hints for Stage 2
    INTENT_VERBS = {
        "IMPLEMENT": ["add", "implement", "create", "build", "develop"],
        "FIX": ["fix", "resolve", "repair", "debug", "correct"],
        "REFACTOR": ["refactor", "improve", "optimize", "restructure"],
        "ANALYZE": ["analyze", "examine", "investigate", "review"],
        "ENHANCE": ["enhance", "extend", "augment"],
    }

    def __init__(self) -> None:
        """Initialize PFRT with transformation state."""
        self.last_intent_hint: Optional[str] = None
        self.last_token_reduction: float = 0.0

    def transform(
        self, 
        user_request: str, 
        include_hints: bool = False
    ) -> str:
        """
        Transform verbose user request into crystallized intent.

        Args:
            user_request: Raw user input (may be verbose/repetitive)
            include_hints: Whether to inject Stage 2 classification hints

        Returns:
            Crystallized single-paragraph request
        """
        if not user_request or user_request.strip() == "":
            return ""

        # Track original token count
        original_tokens = self._estimate_tokens(user_request)

        # Step 1: Normalize whitespace and paragraphs
        text = self._normalize_whitespace(user_request)

        # Step 2: Remove redundant patterns
        text = self._remove_redundancy(text)

        # Step 3: Replace uncertainty markers
        text = self._normalize_uncertainty(text)

        # Step 4: Convert anti-patterns
        text = self._handle_anti_patterns(text)

        # Step 5: Convert questions to statements
        text = self._questions_to_statements(text)

        # Step 6: Synthesize multi-concern requests
        text = self._synthesize_concerns(text)

        # Step 7: Extract and preserve constraints
        text = self._preserve_constraints(text)

        # Step 8: Ensure single-paragraph format
        text = self._ensure_single_paragraph(text)

        # Step 9: Classify intent for Stage 2 hint
        if include_hints:
            self.last_intent_hint = self._classify_intent(text)

        # Calculate token reduction
        final_tokens = self._estimate_tokens(text)
        self.last_token_reduction = (
            (original_tokens - final_tokens) / original_tokens
            if original_tokens > 0
            else 0.0
        )

        return text.strip()

    def _normalize_whitespace(self, text: str) -> str:
        """Convert multi-paragraph to single block, normalize spacing."""
        # Replace multiple newlines with single space
        text = re.sub(r"\n\s*\n+", " ", text)
        # Replace multiple spaces with single space
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _remove_redundancy(self, text: str) -> str:
        """Remove redundant conversational phrases."""
        for pattern in self.REDUNDANT_PATTERNS:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)
        # Clean up resulting double spaces
        text = re.sub(r"\s+", " ", text)
        return text

    def _normalize_uncertainty(self, text: str) -> str:
        """Convert uncertainty markers to decisive language."""
        for uncertain, decisive in self.UNCERTAINTY_MARKERS.items():
            # Case-insensitive replacement
            text = re.sub(
                rf"\b{uncertain}\b",
                decisive,
                text,
                flags=re.IGNORECASE,
            )
        # Clean up empty phrases
        text = re.sub(r"\s+", " ", text)
        return text

    def _handle_anti_patterns(self, text: str) -> str:
        """Replace anti-pattern directives with CORTEX-compliant alternatives."""
        for anti, correction in self.ANTI_PATTERNS.items():
            # Match multi-word patterns with flexible spacing
            pattern = r"\b" + r"\s+".join(re.escape(word) for word in anti.split()) + r"\b"
            if re.search(pattern, text, flags=re.IGNORECASE):
                text = re.sub(
                    pattern,
                    correction,
                    text,
                    flags=re.IGNORECASE,
                )
        return text

    def _questions_to_statements(self, text: str) -> str:
        """Convert interrogative sentences to declarative mode."""
        # Replace "Can we add X?" with "Add X"
        text = re.sub(
            r"(?:can|could|should) (?:we|I) (\w+)",
            r"\1",
            text,
            flags=re.IGNORECASE,
        )
        # Remove trailing question marks
        text = text.rstrip("?")
        # Ensure proper sentence case
        if text and text[0].islower():
            text = text[0].upper() + text[1:]
        return text

    def _synthesize_concerns(self, text: str) -> str:
        """Merge fragmented concerns into unified statement."""
        # Split on sentence boundaries
        sentences = re.split(r"[.!]\s+", text)
        
        if len(sentences) <= 2:
            return text  # Already concise
        
        # Extract core action (first meaningful sentence)
        core_action = sentences[0]
        
        # Extract constraints/requirements (remaining sentences)
        constraints = []
        for sentence in sentences[1:]:
            if any(
                keyword in sentence.lower()
                for keyword in ["ensure", "check", "verify", "validate", "without",
                                "mcp", "exposed", "must", "required", "tdd"]
            ):
                constraints.append(sentence.strip())
        
        # Synthesize: "Action with constraint1 and constraint2"
        if constraints:
            synthesized = f"{core_action} with {' and '.join(constraints[:2])}"
        else:
            synthesized = core_action
        
        return synthesized

    def _preserve_constraints(self, text: str) -> str:
        """Ensure requirements and constraints are retained."""
        # Identify constraint keywords
        constraint_keywords = [
            "mcp-exposed",
            "mcp",
            "exposed",
            "no regression",
            "tdd",
            "test coverage",
            "validation",
            "check existing",
        ]
        
        # If text lacks constraints but original likely had them, flag it
        has_constraint = any(kw in text.lower() for kw in constraint_keywords)
        
        if not has_constraint and any(
            marker in text.lower()
            for marker in ["ensure", "make sure", "don't break", "must be"]
        ):
            # Extract the requirement if mentioned
            if "must be mcp" in text.lower() or "mcp-exposed" in text.lower():
                if "mcp" not in text.lower():
                    text += " (MCP-exposed)"
            else:
                # Inject generic validation constraint
                text += " with validation against existing implementations"
        
        return text

    def _ensure_single_paragraph(self, text: str) -> str:
        """Guarantee output is single paragraph, suitable for inline display."""
        # Remove any remaining newlines
        text = text.replace("\n", " ")
        # Limit to 2 sentences max
        sentences = re.split(r"[.!]\s+", text)
        if len(sentences) > 2:
            text = ". ".join(sentences[:2]) + "."
        return text

    def _classify_intent(self, text: str) -> str:
        """
        Classify primary intent for IntentRouter hint.
        
        Returns:
            Intent classification (IMPLEMENT|FIX|REFACTOR|ANALYZE|ENHANCE)
        """
        text_lower = text.lower()
        
        # Score each intent based on verb presence
        scores: Dict[str, int] = {intent: 0 for intent in self.INTENT_VERBS}
        
        for intent, verbs in self.INTENT_VERBS.items():
            for verb in verbs:
                if rf"\b{verb}\b" in text_lower:
                    scores[intent] += 1
        
        # Return highest-scoring intent
        max_intent = max(scores.items(), key=lambda x: x[1])
        return max_intent[0] if max_intent[1] > 0 else "IMPLEMENT"

    def _estimate_tokens(self, text: str) -> float:
        """
        Estimate token count (approximation: words / 0.75).
        
        Args:
            text: Input text
            
        Returns:
            Estimated token count
        """
        words = len(text.split())
        return words / 0.75


# AC_COMPLETE: AC-CORE-PFRT-20260223T000000Z ✅ PFRT Engine implementation
