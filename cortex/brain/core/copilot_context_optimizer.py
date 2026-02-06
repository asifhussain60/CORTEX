"""
Copilot Context Optimizer (ENH-046 Phase 2)

Purpose: Extends Token Optimizer for Copilot-bound context compression
Architecture: EXIT GATE in MasterOrchestrator.execute_operation()

This module optimizes context handed to GitHub Copilot Chat by:
1. Accurate token estimation using tiktoken
2. Budget enforcement before handoff
3. Per-orchestrator compression strategies
4. Session cumulative tracking

Author: CORTEX AI | TDD: RED→GREEN→REFACTOR
"""

import json
from typing import Dict, Any, Optional
from dataclasses import dataclass
from collections import defaultdict


# ═══════════════════════════════════════════════════════════════════════════════
# EXCEPTION CLASSES
# ═══════════════════════════════════════════════════════════════════════════════

class TokenBudgetExceededError(Exception):
    """Raised when context exceeds Copilot token budget"""
    
    def __init__(self, actual_tokens: int, budget: int, message: str = ""):
        self.actual_tokens = actual_tokens
        self.budget = budget
        self.overflow = actual_tokens - budget
        super().__init__(message or f"Context exceeded budget: {actual_tokens}/{budget} tokens (+{self.overflow})")


# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class OptimizedContext:
    """Result of context optimization"""
    content: Dict[str, Any]
    tokens: int
    compression_ratio: float
    warnings: list[str]


# ═══════════════════════════════════════════════════════════════════════════════
# COPILOT CONTEXT OPTIMIZER
# ═══════════════════════════════════════════════════════════════════════════════

class CopilotContextOptimizer:
    """
    Token Optimizer extension for Copilot-bound context.
    
    Responsibilities:
    - Estimate tokens for any content (text, dict, code)
    - Enforce exit budget (default 20K tokens)
    - Compress per-orchestrator output types
    - Track cumulative session tokens
    
    Usage:
        optimizer = CopilotContextOptimizer(exit_budget=20000)
        tokens = optimizer.estimate_copilot_tokens(context)
        result = optimizer.enforce_exit_budget(context)
        compressed = optimizer.compress_orchestrator_output(output, "InteractionOrchestrator")
    """
    
    def __init__(self, exit_budget: int = 20000, warn_threshold: float = 0.8):
        """
        Initialize optimizer.
        
        Args:
            exit_budget: Maximum tokens allowed before Copilot handoff (default: 20K)
            warn_threshold: Warn when usage exceeds this ratio (default: 0.8 = 80%)
        """
        self.exit_budget = exit_budget
        self.warn_threshold = warn_threshold
        self._session_tokens: Dict[str, int] = defaultdict(int)
        
        # Try to import tiktoken for accurate token counting
        try:
            import tiktoken
            self._tiktoken_encoder = tiktoken.get_encoding("cl100k_base")  # GPT-4 encoding
            self._has_tiktoken = True
        except ImportError:
            self._tiktoken_encoder = None
            self._has_tiktoken = False
    
    def estimate_copilot_tokens(self, content: Any) -> int:
        """
        Estimate token count for any content type.
        
        Uses tiktoken if available (accurate), otherwise word-based estimation.
        
        Args:
            content: Text, dict, or any serializable content
        
        Returns:
            Estimated token count
        """
        if content is None:
            return 0
        
        # Convert to string if dict/object
        if isinstance(content, dict):
            if not content:  # Empty dict
                return 0
            content_str = json.dumps(content, indent=2)
        elif isinstance(content, str):
            if not content:  # Empty string
                return 0
            content_str = content
        else:
            content_str = str(content)
        
        # Use tiktoken if available (accurate)
        if self._has_tiktoken and self._tiktoken_encoder:
            return len(self._tiktoken_encoder.encode(content_str))
        
        # Fallback: Word-based estimation (~0.75 tokens/word)
        # BUT: Add character-based adjustment for more accuracy
        word_count = len(content_str.split())
        char_count = len(content_str)
        
        # More accurate estimation: words + character overhead
        # Average word length is 5 chars, so extra chars add tokens
        base_tokens = word_count * 0.75
        char_tokens = char_count / 4  # ~4 chars per token
        estimated = int((base_tokens + char_tokens) / 2)  # Average both methods
        
        # Adjust for content type
        if isinstance(content, dict):
            # Dicts have JSON overhead (brackets, commas, quotes)
            return int(estimated * 1.2)
        elif "def " in content_str or "class " in content_str:
            # Code has more tokens (punctuation, operators)
            return int(estimated * 1.3)
        elif "#" in content_str or "**" in content_str or "*" in content_str:
            # Markdown has formatting tokens
            return int(estimated * 1.1)
        else:
            # Plain text
            return estimated
    
    def enforce_exit_budget(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enforce token budget before Copilot handoff.
        
        Raises TokenBudgetExceededError if context exceeds budget.
        Returns warning if approaching budget (>80%).
        
        Args:
            context: Context to validate
        
        Returns:
            Dict with status, tokens, usage_ratio, and optional warning
        
        Raises:
            TokenBudgetExceededError: When context exceeds budget
        """
        tokens = self.estimate_copilot_tokens(context)
        usage_ratio = tokens / self.exit_budget
        
        result = {
            "status": "PASS",
            "tokens": tokens,
            "usage_ratio": usage_ratio
        }
        
        # Check if exceeds budget
        if tokens > self.exit_budget:
            raise TokenBudgetExceededError(
                actual_tokens=tokens,
                budget=self.exit_budget
            )
        
        # Check if approaching budget
        if usage_ratio >= self.warn_threshold:
            result["status"] = "WARNING"
            result["warning"] = f"Approaching budget: {tokens}/{self.exit_budget} tokens ({usage_ratio:.1%})"
        
        return result
    
    def compress_orchestrator_output(
        self,
        output: Dict[str, Any],
        orchestrator_name: str
    ) -> Dict[str, Any]:
        """
        Compress orchestrator output using type-specific strategies.
        
        Strategies per orchestrator:
        - InteractionOrchestrator: LENS context → classification + confidence only
        - EnforcementOrchestrator: Pass/fail + violated rules only
        - ChallengeEngine: Verdict + top alternative only
        - TDDOrchestrator: Test count + phase, omit details
        - Unknown: Pass through unchanged
        
        Args:
            output: Orchestrator output dict
            orchestrator_name: Name of orchestrator
        
        Returns:
            Compressed output dict
        """
        # Unknown orchestrator: Pass through
        if orchestrator_name not in [
            "InteractionOrchestrator",
            "EnforcementOrchestrator",
            "ChallengeEngine",
            "TDDOrchestrator"
        ]:
            return output
        
        compressed = output.copy()
        
        # InteractionOrchestrator: Compress LENS context
        if orchestrator_name == "InteractionOrchestrator" and "lens_context" in output:
            lens = output["lens_context"]
            compressed["lens_context"] = {
                "language": lens.get("language", {}),  # Keep classification
                # Omit examination details (files, complexity)
                # Omit navigation details (git_history)
                # Omit synthesis details (DoR)
            }
        
        # EnforcementOrchestrator: Keep status + violations only
        elif orchestrator_name == "EnforcementOrchestrator" and "validation" in output:
            validation = output["validation"]
            compressed["validation"] = {
                "status": validation.get("status"),
                "agents": [
                    agent for agent in validation.get("agents", [])
                    if agent.get("status") == "BLOCKED"
                ]
            }
        
        # ChallengeEngine: Verdict + top alternative only
        elif orchestrator_name == "ChallengeEngine" and "challenge" in output:
            challenge = output["challenge"]
            alternatives = challenge.get("alternatives", [])
            compressed["challenge"] = {
                "verdict": challenge.get("verdict"),
                "alternatives": alternatives[:1] if alternatives else []  # Top alternative only
            }
        
        # TDDOrchestrator: Test count + phase, omit plans
        elif orchestrator_name == "TDDOrchestrator" and "tdd_cycle" in output:
            tdd = output["tdd_cycle"]
            test_plan = tdd.get("test_plan", {})
            compressed["tdd_cycle"] = {
                "phase": tdd.get("phase"),
                "test_plan": {
                    "test_count": test_plan.get("test_count", 0)
                }
                # Omit implementation_plan
            }
        
        return compressed
    
    def track_turn(self, session_id: str, context: Dict[str, Any]) -> int:
        """
        Track tokens for a turn and accumulate in session.
        
        Args:
            session_id: Session identifier
            context: Context sent this turn
        
        Returns:
            Cumulative tokens for session
        """
        tokens = self.estimate_copilot_tokens(context)
        self._session_tokens[session_id] += tokens
        return self._session_tokens[session_id]
    
    def get_session_tokens(self, session_id: str) -> int:
        """
        Get cumulative tokens for a session.
        
        Args:
            session_id: Session identifier
        
        Returns:
            Cumulative tokens sent in this session
        """
        return self._session_tokens.get(session_id, 0)
    
    def optimize_for_copilot(self, context: Dict[str, Any]) -> OptimizedContext:
        """
        Full optimization pipeline for Copilot-bound context.
        
        Steps:
        1. Estimate original tokens
        2. Compress based on orchestrator type
        3. Enforce budget
        4. Return optimized context
        
        Args:
            context: Raw context from orchestrator
        
        Returns:
            OptimizedContext with compressed content
        """
        original_tokens = self.estimate_copilot_tokens(context)
        
        # Compress if orchestrator identified
        orchestrator = context.get("orchestrator", "")
        if orchestrator:
            compressed = self.compress_orchestrator_output(context, orchestrator)
        else:
            compressed = context
        
        compressed_tokens = self.estimate_copilot_tokens(compressed)
        compression_ratio = 1.0 - (compressed_tokens / original_tokens) if original_tokens > 0 else 0.0
        
        # Collect warnings
        warnings = []
        try:
            budget_result = self.enforce_exit_budget(compressed)
            if budget_result["status"] == "WARNING":
                warnings.append(budget_result["warning"])
        except TokenBudgetExceededError as e:
            warnings.append(str(e))
        
        return OptimizedContext(
            content=compressed,
            tokens=compressed_tokens,
            compression_ratio=compression_ratio,
            warnings=warnings
        )
