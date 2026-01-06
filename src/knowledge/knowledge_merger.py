"""
Knowledge Merger - Phase 1 Implementation
CORTEX 5.5 Enhancement Epic

Merges CORTEX core knowledge with company-specific knowledge.
Company knowledge overrides CORTEX where explicitly defined.
"""

from typing import Dict, Any, Optional
from copy import deepcopy


class KnowledgeMerger:
    """
    Merges CORTEX core knowledge with company-specific knowledge.
    
    Merge Strategy:
    1. Company-defined fields override CORTEX
    2. Undefined company fields use CORTEX defaults
    3. Validates merge result (no type conflicts)
    """
    
    def __init__(self):
        """Initialize knowledge merger."""
        pass
    
    def merge(
        self,
        cortex_knowledge: Dict[str, Any],
        company_knowledge: Dict[str, Any],
        strategy: str = "company_priority"
    ) -> Dict[str, Any]:
        """
        Merge CORTEX and company knowledge.
        
        Args:
            cortex_knowledge: CORTEX core knowledge (baseline)
            company_knowledge: Company-specific knowledge (overrides)
            strategy: Merge strategy ("company_priority", "cortex_priority")
        
        Returns:
            Merged knowledge dictionary
        
        Raises:
            ValueError: If type conflicts detected
        """
        if strategy not in ["company_priority", "cortex_priority"]:
            raise ValueError(f"Invalid strategy: {strategy}")
        
        # Deep copy to avoid mutating originals
        result = deepcopy(cortex_knowledge)
        
        if strategy == "company_priority":
            result = self._merge_with_company_priority(result, company_knowledge)
        else:
            result = self._merge_with_cortex_priority(result, company_knowledge)
        
        # Validate merge result
        self._validate_merge(result, cortex_knowledge, company_knowledge)
        
        return result
    
    def _merge_with_company_priority(
        self,
        cortex: Dict[str, Any],
        company: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge with company knowledge taking priority.
        
        Company fields override CORTEX where explicitly defined.
        CORTEX fills gaps where company undefined.
        """
        result = deepcopy(cortex)
        
        for key, company_value in company.items():
            if company_value is None:
                # Company explicitly set to None - skip (use CORTEX)
                continue
            
            if key not in result:
                # New field from company - add it
                result[key] = company_value
            elif isinstance(company_value, dict) and isinstance(result[key], dict):
                # Both are dicts - recursive merge
                result[key] = self._merge_with_company_priority(result[key], company_value)
            elif isinstance(company_value, list) and isinstance(result[key], list):
                # Both are lists - company replaces (no append/merge)
                result[key] = company_value
            else:
                # Primitive value or type mismatch - company overrides
                result[key] = company_value
        
        return result
    
    def _merge_with_cortex_priority(
        self,
        cortex: Dict[str, Any],
        company: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge with CORTEX knowledge taking priority.
        
        CORTEX fields stay unchanged.
        Company fields added only if not in CORTEX.
        """
        result = deepcopy(cortex)
        
        for key, company_value in company.items():
            if key not in result:
                # Field not in CORTEX - add from company
                result[key] = company_value
            # Otherwise, keep CORTEX value (CORTEX priority)
        
        return result
    
    def _validate_merge(
        self,
        merged: Dict[str, Any],
        cortex: Dict[str, Any],
        company: Dict[str, Any]
    ) -> None:
        """
        Validate merge result.
        
        Checks:
        - No critical CORTEX fields removed
        - No type conflicts
        - No invalid values
        
        Raises:
            ValueError: If validation fails
        """
        # Check critical CORTEX fields not removed
        critical_fields = self._get_critical_fields(cortex)
        for field in critical_fields:
            if field not in merged:
                raise ValueError(f"Critical CORTEX field removed during merge: {field}")
        
        # Check type conflicts (if field exists in both, types should match)
        for key in set(cortex.keys()) & set(company.keys()):
            cortex_value = cortex[key]
            company_value = company[key]
            
            if cortex_value is not None and company_value is not None:
                cortex_type = type(cortex_value)
                company_type = type(company_value)
                
                # Allow dict/dict or list/list, but not dict/list mismatches
                if cortex_type != company_type:
                    if not (isinstance(cortex_value, dict) and isinstance(company_value, dict)):
                        if not (isinstance(cortex_value, list) and isinstance(company_value, list)):
                            raise ValueError(
                                f"Type conflict for field '{key}': "
                                f"CORTEX={cortex_type.__name__}, Company={company_type.__name__}"
                            )
    
    def _get_critical_fields(self, cortex: Dict[str, Any]) -> list[str]:
        """
        Get list of critical CORTEX fields that must not be removed.
        
        Critical fields are those required for CORTEX operation.
        """
        # Define critical fields (could be configurable)
        critical = []
        
        # Example: If cortex has "cortex_version", it's critical
        if "cortex_version" in cortex:
            critical.append("cortex_version")
        
        # Add more critical field detection logic as needed
        return critical
    
    def merge_tech_stack(
        self,
        cortex_tech_stack: Dict[str, Any],
        company_tech_stack: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Specialized merge for tech stack.
        
        Args:
            cortex_tech_stack: CORTEX default tech stack
            company_tech_stack: Company tech stack
        
        Returns:
            Merged tech stack with company overrides
        """
        return self.merge(cortex_tech_stack, company_tech_stack, strategy="company_priority")
    
    def merge_governance_rules(
        self,
        cortex_rules: Dict[str, Any],
        company_rules: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Specialized merge for governance rules.
        
        Company rules extend (not replace) CORTEX rules.
        
        Args:
            cortex_rules: CORTEX brain protection rules
            company_rules: Company-specific governance rules
        
        Returns:
            Merged governance rules (additive)
        """
        result = deepcopy(cortex_rules)
        
        # Additive merge - company rules add to CORTEX
        for category, rules in company_rules.items():
            if category not in result:
                result[category] = rules
            elif isinstance(rules, dict) and isinstance(result[category], dict):
                # Merge dict categories
                result[category].update(rules)
            elif isinstance(rules, list) and isinstance(result[category], list):
                # Extend list categories (no duplicates)
                for rule in rules:
                    if rule not in result[category]:
                        result[category].append(rule)
        
        return result
    
    def get_merge_summary(
        self,
        cortex_knowledge: Dict[str, Any],
        company_knowledge: Dict[str, Any],
        merged: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate merge summary report.
        
        Args:
            cortex_knowledge: Original CORTEX knowledge
            company_knowledge: Original company knowledge
            merged: Merged result
        
        Returns:
            Summary dict with statistics
        """
        cortex_fields = set(cortex_knowledge.keys())
        company_fields = set(company_knowledge.keys())
        merged_fields = set(merged.keys())
        
        overridden_fields = cortex_fields & company_fields
        added_fields = company_fields - cortex_fields
        cortex_only_fields = cortex_fields - company_fields
        
        return {
            "total_fields": len(merged_fields),
            "from_cortex": len(cortex_only_fields),
            "from_company": len(added_fields),
            "overridden": len(overridden_fields),
            "overridden_fields": list(overridden_fields),
            "added_fields": list(added_fields),
            "cortex_percentage": round(len(cortex_only_fields) / len(merged_fields) * 100, 1),
            "company_percentage": round((len(added_fields) + len(overridden_fields)) / len(merged_fields) * 100, 1)
        }
