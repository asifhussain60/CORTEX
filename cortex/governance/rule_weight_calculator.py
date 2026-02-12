"""
Rule Weight Calculator for Context-Aware Governance.

AC-PHASE38-007: Dynamic CORE rule severity adjustment

Calculates rule weights based on:
- Operation domain (security, performance, etc.)
- Operation mode (production, prototype, etc.)
- Rule category (critical, recommended, optional)
"""

from typing import Any, Dict


class RuleWeightCalculator:
    """
    Calculator for dynamic rule weights.

    Adjusts CORE rule weights based on operational context.
    """

    def __init__(self):
        """Initialize calculator with rule categorization."""
        self._rule_categories = self._categorize_rules()

    def _categorize_rules(self) -> Dict[str, str]:
        """Categorize CORE rules by primary domain."""
        return {
            # Critical rules (always enforced)
            'CORE-008': 'critical',  # TDD
            'CORE-027': 'critical',  # Audit trail
            'CORE-035': 'critical',  # Single implementation

            # Security rules
            'CORE-025': 'security',  # Git discipline
            'CORE-026': 'security',  # Git checkpoint

            # Code quality rules
            'CORE-011': 'quality',  # Type hints
            'CORE-012': 'quality',  # Docstrings
            'CORE-013': 'quality',  # No bare except

            # Documentation rules
            'CORE-029': 'documentation',  # Response header
            'CORE-030': 'documentation',  # Implementation truth
        }

    def calculate_weight(self, rule_id: str, context: Dict[str, Any]) -> float:
        """
        Calculate weight for a rule in given context.

        Args:
            rule_id: CORE rule ID
            context: Operation context

        Returns:
            Weight multiplier (0.1 - 2.0)
        """
        base_weight = 1.0
        category = self._rule_categories.get(rule_id, 'quality')

        # Critical rules always have high weight
        if category == 'critical':
            base_weight = 1.5

        # Domain-specific adjustments
        domain = context.get('domain', '')

        if domain == 'security':
            if category == 'security':
                base_weight = 1.8  # Elevate security rules
            else:
                base_weight = 1.2  # Slightly elevate all rules
        elif domain and domain not in ['security', 'performance', 'quality']:
            # Unknown domains: use default weight (graceful handling)
            base_weight = 1.0

        # Operation type adjustments
        operation = context.get('operation', '')

        if operation == 'IMPLEMENT':
            if rule_id == 'CORE-008':  # TDD rule
                base_weight = 2.0  # Maximum weight for TDD in IMPLEMENT
            elif category in ['security', 'critical']:
                base_weight = min(base_weight * 1.3, 2.0)
        elif operation == 'ANALYZE':
            if rule_id == 'CORE-008':  # TDD rule
                base_weight = 0.3  # Relaxed for analysis
            elif category == 'documentation':
                base_weight = 0.5  # Less strict documentation

        # Mode-specific adjustments
        mode = context.get('mode', '')

        if mode == 'prototype':
            if category == 'documentation':
                base_weight = 0.5  # Relax documentation
            elif category == 'quality':
                base_weight = 0.7  # Relax quality checks

        elif mode == 'production':
            if category in ['security', 'critical']:
                base_weight = min(base_weight * 1.2, 2.0)  # Elevate critical rules

        # Bounds check (weight ceiling at 2.0, floor at 0.1)
        return max(0.1, min(2.0, base_weight))

    def calculate(self, rule_id: str, context: Dict[str, Any]) -> float:
        """
        Convenience method that wraps calculate_weight().

        Args:
            rule_id: CORE rule ID
            context: Operation context

        Returns:
            Weight multiplier (0.1 - 2.0)
        """
        return self.calculate_weight(rule_id, context)

    def calculate_severity_adjustment(
        self,
        rule_id: str,
        base_severity: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Adjust rule severity based on context.

        Args:
            rule_id: CORE rule ID
            base_severity: Base severity (ERROR, WARNING, INFO)
            context: Operation context

        Returns:
            Adjusted severity
        """
        category = self._rule_categories.get(rule_id, 'quality')

        # Critical rules never downgrade
        if category == 'critical':
            return base_severity

        mode = context.get('mode', '')

        # Prototype mode: downgrade non-critical
        if mode == 'prototype':
            if base_severity == 'ERROR':
                return 'WARNING'
            elif base_severity == 'WARNING':
                return 'INFO'

        # Production mode: upgrade security/critical
        elif mode == 'production':
            if category == 'security' and base_severity == 'WARNING':
                return 'ERROR'

        return base_severity


# AC-PHASE38-007 ✅ Implementation complete
