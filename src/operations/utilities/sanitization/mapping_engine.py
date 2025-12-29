"""
Mapping Engine for Code Sanitization

Generates domain→generic terminology mappings with conflict detection
and resolution strategies.

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
"""

import logging
import re
from typing import Dict, List, Set, Any, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class MappingEngine:
    """Generates and manages transformation mappings."""

    def __init__(self, manifest: Dict[str, Any], overrides: Optional[Dict[str, str]] = None):
        self.manifest = manifest
        self.mapping_rules = manifest.get("mapping_rules", {})
        self.generic_replacements = self.mapping_rules.get("generic_replacements", {})
        self.overrides = overrides or {}
        
    def generate_mappings(
        self,
        domain_terms: Dict[str, Any],
        namespaces: Dict[str, List[str]]
    ) -> Dict[str, str]:
        """
        Generate comprehensive transformation mappings.

        Args:
            domain_terms: Extracted domain terminology
            namespaces: Detected namespaces by language

        Returns:
            Dict mapping original→sanitized terms
        """
        mappings = {}

        # 1. Apply manual overrides first
        mappings.update(self.overrides)

        # 2. Map domain-specific terms
        for term, info in domain_terms.items():
            if term not in mappings:
                generic_term = self._find_generic_replacement(term, info["category"])
                if generic_term:
                    mappings[term] = generic_term
                    # Add variations (PascalCase, camelCase, etc.)
                    mappings.update(self._generate_case_variations(term, generic_term))

        # 3. Map namespaces
        namespace_mappings = self._generate_namespace_mappings(namespaces)
        mappings.update(namespace_mappings)

        # 4. Handle compound terms (e.g., "RAFundingInvoice" → "PaymentInvoice")
        # Only add compound mappings for keys that don't already exist (preserve custom mappings)
        compound_mappings = self._generate_compound_mappings(mappings)
        for key, value in compound_mappings.items():
            if key not in mappings:
                mappings[key] = value

        logger.info(f"Generated {len(mappings)} transformation mappings")
        return mappings

    def detect_conflicts(self, mappings: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Detect naming conflicts in mappings.

        Args:
            mappings: Proposed transformation mappings

        Returns:
            List of conflicts with details
        """
        conflicts = []
        reverse_map = defaultdict(list)

        # Build reverse mapping to find collisions
        for original, generic in mappings.items():
            reverse_map[generic].append(original)

        # Identify many→one mappings (conflicts)
        for generic, originals in reverse_map.items():
            if len(originals) > 1:
                conflicts.append({
                    "generic_term": generic,
                    "original_terms": originals,
                    "type": "collision",
                    "severity": "high" if len(originals) > 2 else "medium",
                })

        if conflicts:
            logger.warning(f"Detected {len(conflicts)} naming conflicts")
        
        return conflicts

    def resolve_conflicts(
        self,
        mappings: Dict[str, str],
        conflicts: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """
        Resolve naming conflicts by adding disambiguators.

        Args:
            mappings: Original mappings
            conflicts: Detected conflicts

        Returns:
            Resolved mappings
        """
        resolved = mappings.copy()

        for conflict in conflicts:
            generic = conflict["generic_term"]
            originals = conflict["original_terms"]

            # Strategy: Add numeric suffixes to all but the first
            for i, original in enumerate(originals):
                if i > 0:
                    resolved[original] = f"{generic}_{i}"
                    logger.info(f"Resolved conflict: {original} → {generic}_{i}")

        return resolved

    def generate_preview(self, mappings: Dict[str, str]) -> Dict[str, str]:
        """
        Generate human-readable preview of transformations.

        Args:
            mappings: Transformation mappings

        Returns:
            Sorted dict for preview display
        """
        # Sort by original term length (longest first) for better readability
        sorted_mappings = dict(
            sorted(mappings.items(), key=lambda x: len(x[0]), reverse=True)
        )
        
        return sorted_mappings

    def _find_generic_replacement(self, term: str, category: str) -> Optional[str]:
        """Find generic replacement for a domain term."""
        term_lower = term.lower()

        # Check category-specific replacements
        if category in self.generic_replacements:
            category_map = self.generic_replacements[category]
            if term_lower in category_map:
                return category_map[term_lower]

        # Check all replacement categories
        for cat_name, cat_map in self.generic_replacements.items():
            if term_lower in cat_map:
                return cat_map[term_lower]

        # No replacement found
        return None

    def _generate_case_variations(self, original: str, generic: str) -> Dict[str, str]:
        """
        Generate case variations for a term.

        Examples:
            - reimbursement → payment
            - Reimbursement → Payment
            - REIMBURSEMENT → PAYMENT
            - ReimbursementAccount → PaymentAccount
        """
        variations = {}

        # Title Case
        if original.istitle():
            variations[original.title()] = generic.title()

        # UPPER CASE
        if original.isupper():
            variations[original.upper()] = generic.upper()

        # PascalCase (detect by capital letters)
        if self._is_pascal_case(original):
            variations[self._to_pascal_case(original)] = self._to_pascal_case(generic)

        # camelCase
        if self._is_camel_case(original):
            variations[self._to_camel_case(original)] = self._to_camel_case(generic)

        return variations

    def _generate_namespace_mappings(self, namespaces: Dict[str, List[str]]) -> Dict[str, str]:
        """Generate mappings for namespaces/packages."""
        mappings = {}

        for lang, ns_list in namespaces.items():
            for ns in ns_list:
                # Apply namespace pattern transformations
                for pattern_config in self.mapping_rules.get("namespace_patterns", []):
                    pattern = pattern_config.get("pattern", "")
                    replacement = pattern_config.get("replacement", "")
                    
                    # Simple pattern matching (enhanced version would use regex)
                    if "RA." in ns:
                        generic_ns = ns.replace("RA.", "PaymentProcessor.")
                        mappings[ns] = generic_ns

        return mappings

    def _generate_compound_mappings(self, base_mappings: Dict[str, str]) -> Dict[str, str]:
        """
        Generate mappings for compound terms.

        Example: If "RA" → "PaymentProcessor" and "Invoice" → "Invoice",
                then "RAInvoice" → "PaymentProcessorInvoice"
        """
        compound_mappings = {}

        # Get base terms sorted by length (longest first for greedy matching)
        sorted_terms = sorted(base_mappings.keys(), key=len, reverse=True)

        # Look for compounds in existing mappings
        for original, generic in base_mappings.items():
            for term in sorted_terms:
                if term in original and term != original:
                    # Found a compound
                    compound_generic = original.replace(term, base_mappings[term])
                    if compound_generic != original:
                        compound_mappings[original] = compound_generic

        return compound_mappings

    def _is_pascal_case(self, text: str) -> bool:
        """Check if text is in PascalCase."""
        return text and text[0].isupper() and not text.isupper() and '_' not in text

    def _is_camel_case(self, text: str) -> bool:
        """Check if text is in camelCase."""
        return text and text[0].islower() and any(c.isupper() for c in text) and '_' not in text

    def _to_pascal_case(self, text: str) -> str:
        """Convert text to PascalCase."""
        if not text:
            return text
        return text[0].upper() + text[1:]

    def _to_camel_case(self, text: str) -> str:
        """Convert text to camelCase."""
        if not text:
            return text
        return text[0].lower() + text[1:]
