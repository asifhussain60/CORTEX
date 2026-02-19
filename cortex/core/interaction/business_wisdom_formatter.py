# AC_START: AC-PHASE-06-S1-001
"""
Business Wisdom Formatter - Display governance rules with book references.

Purpose:
    Enhance user experience by displaying CORE governance rules with authoritative
    book citations. Transforms technical rule IDs into educational principles with
    citations from famous business/tech books.

Example Output:
    ### 📚 Business Wisdom
    - **Red-Green-Refactor Discipline** → CORE-008 (TDD by Kent Beck)
    - **Type Hints Mandatory** → CORE-011 (Clean Code by Robert Martin)
    - **Google Docstrings** → CORE-012 (Pragmatic Programmer by Hunt & Thomas)

Integration Points:
    - EnforcementOrchestrator: Governance violation messages
    - DoR displays: Definition of Ready approval gates
    - IntentRouter: Intent classification messages
    - Response formatters: BLUF templates

Authority:
    - business-wisdom-wiring.md (Stage 2)
    - phase-06-business-wisdom-display-enhancement.yaml
    - cortex-response-templates.md (Business Wisdom Panel Template)

Governance:
    - CORE-011: Type hints 100%
    - CORE-012: Google-style docstrings
    - CORE-035: Single canonical implementation

Author: Asif Hussain
Date: 2026-02-13
"""

from typing import Any, Dict, List, Optional

from cortex.tools.cortex_intelligence_integration import GovernanceRuleLoader


class BusinessWisdomFormatter:
    """
    Format governance rules with book references for user-facing displays.
    
    This formatter transforms technical CORE rule IDs into educational principles
    with authoritative book citations, enhancing user understanding of WHY rules
    exist and building trust through recognized sources.
    
    Features:
        - Arrow notation: **Principle** → RULE-ID (Book)
        - Max 5 principles per display (prevents overwhelming users)
        - 📚 icon in section header
        - Severity-based sorting (P0 → P1 → P2)
        - Graceful degradation (missing books still display principle)
    
    Example:
        >>> formatter = BusinessWisdomFormatter()
        >>> markdown = formatter.format_governance_with_books(
        ...     rule_ids=["CORE-008", "CORE-011", "CORE-012"]
        ... )
        >>> print(markdown)
        ### 📚 Business Wisdom
        - **Red-Green-Refactor Discipline** → CORE-008 (TDD by Kent Beck)
        - **Type Hints Mandatory** → CORE-011 (Clean Code by Robert Martin)
        - **Google Docstrings** → CORE-012 (Pragmatic Programmer by Hunt & Thomas)
    """
    
    def __init__(self, loader: Optional[GovernanceRuleLoader] = None) -> None:
        """
        Initialize formatter with governance rule loader.
        
        Args:
            loader: Optional governance rule loader. If None, creates default instance.
        """
        self.loader = loader or GovernanceRuleLoader()
    
    def format_governance_with_books(
        self,
        rule_ids: List[str],
        max_display: int = 5,
        include_icon: bool = True,
    ) -> str:
        """
        Format governance rules with book references.
        
        Transforms technical rule IDs into educational markdown with book citations.
        Enforces max display limit to prevent overwhelming users.
        
        Args:
            rule_ids: List of CORE rule IDs (e.g., ["CORE-008", "CORE-011"])
            max_display: Maximum principles to show (default 5)
            include_icon: Include 📚 icon in section header (default True)
        
        Returns:
            Markdown string with enriched principles. Empty string if no valid rules.
        
        Example:
            >>> formatter = BusinessWisdomFormatter()
            >>> markdown = formatter.format_governance_with_books(
            ...     rule_ids=["CORE-008"],
            ...     max_display=1,
            ...     include_icon=True
            ... )
            >>> "📚" in markdown
            True
            >>> "CORE-008" in markdown
            True
        """
        if not rule_ids:
            return ""
        
        # Load rules from governance registry
        rules = []
        for rule_id in rule_ids:
            rule = self.loader.get_rule_by_id(rule_id)
            if rule:
                rules.append(rule)
        
        if not rules:
            return ""
        
        # Sort by severity (P0 → P1 → P2)
        sorted_rules = self._sort_by_severity(rules)
        
        # Limit display
        display_rules = sorted_rules[:max_display]
        
        # Format header
        header = "### 📚 Business Wisdom\n" if include_icon else "### Business Wisdom\n"
        
        # Format rules
        lines = [header]
        for rule in display_rules:
            formatted = self._format_single_rule(rule)
            if formatted:
                lines.append(formatted)
        
        return "\n".join(lines) if len(lines) > 1 else ""
    
    def _format_single_rule(self, rule: Dict[str, Any]) -> str:
        """
        Format single rule with arrow notation.
        
        Format: **Principle** → RULE-ID (Book)
        Graceful degradation: If book missing, omit book reference
        
        Args:
            rule: Rule dictionary from governance registry
        
        Returns:
            Markdown list item with formatted rule. Empty string if missing required fields.
        
        Example:
            >>> formatter = BusinessWisdomFormatter()
            >>> rule = {
            ...     "rule_id": "CORE-008",
            ...     "principle": "Red-Green-Refactor Discipline",
            ...     "book_reference": "TDD by Kent Beck"
            ... }
            >>> formatter._format_single_rule(rule)
            '- **Red-Green-Refactor Discipline** → CORE-008 (TDD by Kent Beck)'
        """
        principle = rule.get("principle", "")
        rule_id = rule.get("rule_id", "")
        book_ref = rule.get("book_reference", "")
        
        if not principle or not rule_id:
            return ""
        
        if book_ref:
            # Full format with book reference
            return f"- **{principle}** → {rule_id} ({book_ref})"
        else:
            # Graceful degradation: no book reference
            return f"- **{principle}** → {rule_id}"
    
    def _sort_by_severity(self, rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sort rules by severity (P0 → P1 → P2).
        
        Ensures most critical rules displayed first when max_display limit applies.
        
        Severity mapping:
            - "blocked": P0 (highest priority)
            - "warning": P1 (medium priority)
            - Other: P2 (lowest priority)
        
        Args:
            rules: List of rule dictionaries
        
        Returns:
            Sorted list (most critical first)
        
        Example:
            >>> formatter = BusinessWisdomFormatter()
            >>> rules = [
            ...     {"severity": "warning", "rule_id": "CORE-001"},
            ...     {"severity": "blocked", "rule_id": "CORE-008"}
            ... ]
            >>> sorted_rules = formatter._sort_by_severity(rules)
            >>> sorted_rules[0]["rule_id"]
            'CORE-008'
        """
        severity_order = {
            "blocked": 0,  # P0
            "warning": 1,  # P1
        }
        
        return sorted(
            rules,
            key=lambda r: severity_order.get(r.get("severity", ""), 2)
        )


# AC_COMPLETE: AC-PHASE-06-S1-001 ✅
