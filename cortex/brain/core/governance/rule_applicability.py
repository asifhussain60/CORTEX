"""
Rule Applicability Engine

Determines if governance rules should apply based on context.

AC-GOV-CTX-001-02: Rule applicability determination with exemption patterns
"""

from typing import Dict, Any, Tuple
from cortex.brain.core.governance.context_extractor import GovernanceContext


class RuleApplicabilityEngine:
    """
    Determines if governance rules should apply to specific contexts.
    
    AC-GOV-CTX-001-02: Provides situational exemption logic
    """
    
    # Exemption patterns for each rule
    EXEMPTION_PATTERNS = {
        "CORE-008": {  # TDD: Tests before code
            "phases": ["exploration", "testing"],
            "code_types": ["generated", "test"],
            "reason": "TDD relaxed for exploration/testing phases and generated code"
        },
        "CORE-011": {  # Type hints required
            "code_types": ["generated"],
            "reason": "Generated code may have alternative type systems"
        },
        "CORE-012": {  # Google docstrings
            "code_types": ["generated", "test"],
            "phases": ["testing"],
            "reason": "Docstrings optional for generated code and test fixtures"
        },
        "CORE-013": {  # No bare except
            "code_types": [],  # Always enforced
            "reason": "Safety-critical rule - no exemptions"
        },
        "CORE-022": {  # Kebab-case naming
            "code_types": ["generated", "internal"],  # Internal code exempt
            "reason": "Kebab-case only for user-facing content, not internal/generated"
        },
        "CORE-028": {  # File length limits
            "code_types": ["generated"],
            "reason": "Generated code may exceed length limits"
        },
        "CORE-030": {  # Response headers
            "code_types": ["test", "generated"],
            "reason": "Headers for interactive responses, not test/generated code"
        },
        # Default for other rules - apply to production only
        "_default": {
            "phases": ["exploration"],
            "code_types": ["generated"],
            "reason": "Standard exemptions for exploration and generated code"
        }
    }
    
    def should_apply_rule(
        self,
        rule_id: str,
        context: GovernanceContext
    ) -> Tuple[bool, str]:
        """
        Determine if rule should apply to given context.
        
        Args:
            rule_id: Governance rule identifier (e.g., "CORE-008")
            context: Governance context with file/operation metadata
            
        Returns:
            Tuple of (applies: bool, reason: str)
        """
        # Check if context matches any exemption pattern
        is_exempt, exemption_reason = self.check_exemption(rule_id, context)
        
        if is_exempt:
            return (False, f"Exempt: {exemption_reason}")
        
        # Rule applies - provide reasoning
        reason = self._get_application_reason(rule_id, context)
        return (True, reason)
    
    def get_exemption_patterns(self, rule_id: str) -> Dict[str, Any]:
        """
        Get exemption patterns for a specific rule.
        
        Args:
            rule_id: Governance rule identifier
            
        Returns:
            Dict with exemption pattern configuration
        """
        return self.EXEMPTION_PATTERNS.get(
            rule_id,
            self.EXEMPTION_PATTERNS["_default"]
        )
    
    def check_exemption(
        self,
        rule_id: str,
        context: GovernanceContext
    ) -> Tuple[bool, str]:
        """
        Check if context matches any exemption pattern.
        
        Args:
            rule_id: Governance rule identifier
            context: Governance context
            
        Returns:
            Tuple of (is_exempt: bool, reason: str)
        """
        patterns = self.get_exemption_patterns(rule_id)
        
        # Check development phase exemptions
        if "phases" in patterns:
            if context.development_phase in patterns["phases"]:
                return (True, f"{context.development_phase} phase - {patterns['reason']}")
        
        # Check code type exemptions
        if "code_types" in patterns:
            if context.code_classification in patterns["code_types"]:
                return (True, f"{context.code_classification} code - {patterns['reason']}")
        
        # Check file type exemptions
        if "file_types" in patterns:
            # If file_types specified, only apply to those types
            if context.file_type not in patterns["file_types"]:
                return (True, f"Rule only applies to {patterns['file_types']}")
        
        # No exemption matched
        return (False, "No exemption applies - rule enforced")
    
    def _get_application_reason(
        self,
        rule_id: str,
        context: GovernanceContext
    ) -> str:
        """
        Generate reason why rule applies.
        
        Args:
            rule_id: Rule identifier
            context: Governance context
            
        Returns:
            Human-readable reason
        """
        reasons = []
        
        if context.development_phase == "production":
            reasons.append("production phase")
        
        if context.code_classification == "production":
            reasons.append("production code")
        
        if context.operation_type in ["implement", "fix", "refactor"]:
            reasons.append(f"{context.operation_type} operation")
        
        if not reasons:
            reasons.append("standard governance applies")
        
        return f"Rule applies: {', '.join(reasons)}"
