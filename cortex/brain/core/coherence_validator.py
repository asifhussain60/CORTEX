"""
Coherence Validator - Cross-File Requirement Coherence

Hallucination prevention with:
- File-to-file requirement coherence validation
- AC-ID naming consistency checking
- Reference validity verification
- Contradiction detection
- Auto-fix suggestions

Satisfies: AC-COHERENCE-001 through AC-COHERENCE-004

Author: Asif Hussain
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from cortex.brain.core.result import Err, Ok, Result


@dataclass
class CoherenceIssue:
    """Single coherence issue found."""

    issue_type: str  # "CONFLICT", "INCONSISTENCY", "INVALID_REFERENCE", "CONTRADICTION"
    severity: str  # "ERROR", "WARNING"
    file_path: str
    line_number: Optional[int]
    ac_id: str
    description: str
    suggestion: Optional[str] = None

    def __hash__(self):
        return hash((self.issue_type, self.ac_id, self.file_path))


class CoherenceValidator:
    """
    Validate cross-file coherence of requirements.

    Ensures:
    - No conflicting requirements for same AC-ID
    - Consistent AC-ID naming across files
    - All references resolve to valid AC-IDs
    - No contradictory acceptance criteria
    """

    # AC-ID pattern: AC-{CATEGORY}-{PHASE}-{SEQUENCE}
    AC_ID_PATTERN = re.compile(r'^AC-([A-Z\-]+?)-(\d+)-(\d+)$')

    def __init__(self):
        """Initialize coherence validator."""
        self._ac_id_cache: Dict[str, Dict[str, Any]] = {}
        self._reference_cache: Dict[str, Set[str]] = {}

    @staticmethod
    def parse_ac_id(ac_id: str) -> Optional[Tuple[str, int, int]]:
        """
        Parse AC-ID into components.

        Args:
            ac_id: AC-ID string (e.g., "AC-NFR-003-01")

        Returns:
            Tuple of (category, phase, sequence) or None if invalid
        """
        match = CoherenceValidator.AC_ID_PATTERN.match(ac_id)
        if match:
            category = match.group(1)
            phase = int(match.group(2))
            sequence = int(match.group(3))
            return (category, phase, sequence)
        return None

    def validate_ac_id_format(self, ac_id: str) -> Result[bool]:
        """
        Validate AC-ID format.

        Args:
            ac_id: AC-ID to validate

        Returns:
            Result[bool] - True if valid format
        """
        if not ac_id:
            return Err("AC-ID cannot be empty")

        parsed = self.parse_ac_id(ac_id)
        if parsed is None:
            return Err(f"Invalid AC-ID format: {ac_id} (expected AC-CATEGORY-PHASE-SEQUENCE)")

        return Ok(True)

    def extract_ac_ids(self, content: str) -> Set[str]:
        """
        Extract all AC-IDs from text content.

        Args:
            content: Text content to search

        Returns:
            Set of AC-IDs found
        """
        pattern = r'\bAC-[A-Z\-]+?-\d+-\d+\b'
        matches = re.findall(pattern, content)
        return set(matches)

    def check_file_to_file_coherence(
        self,
        file_requirements: Dict[str, Dict[str, Any]],
    ) -> Result[List[CoherenceIssue]]:
        """
        Check for conflicting requirements for same AC-ID across files.

        Args:
            file_requirements: Dict mapping AC-ID to requirements from different files

        Returns:
            Result with list of coherence issues
        """
        issues = []

        for ac_id, requirements in file_requirements.items():
            if len(requirements) <= 1:
                continue

            # Extract requirement descriptions
            descriptions = [req.get('description', '') for req in requirements if isinstance(req, dict)]

            # Check for conflicting descriptions
            if len(set(descriptions)) > 1:
                # Descriptions differ - potential conflict
                issues.append(CoherenceIssue(
                    issue_type="CONFLICT",
                    severity="ERROR",
                    file_path="multiple",
                    line_number=None,
                    ac_id=ac_id,
                    description=f"Conflicting requirements for {ac_id} across files",
                    suggestion=f"Unify requirement description for {ac_id}",
                ))

        return Ok(issues)

    def check_ac_id_naming_consistency(
        self,
        ac_definitions: Dict[str, Dict[str, Any]],
    ) -> Result[List[CoherenceIssue]]:
        """
        Check AC-ID naming consistency (same AC-ID used consistently).

        Args:
            ac_definitions: Dict of AC-ID definitions

        Returns:
            Result with list of naming issues
        """
        issues = []

        for ac_id, definition in ac_definitions.items():
            # Validate AC-ID format
            if not self.parse_ac_id(ac_id):
                issues.append(CoherenceIssue(
                    issue_type="INCONSISTENCY",
                    severity="ERROR",
                    file_path=definition.get('file', 'unknown'),
                    line_number=definition.get('line'),
                    ac_id=ac_id,
                    description=f"Invalid AC-ID format: {ac_id}",
                    suggestion="Rename to AC-CATEGORY-PHASE-SEQUENCE format",
                ))

            # Check for typos (similar AC-IDs)
            for other_ac_id in ac_definitions:
                if ac_id != other_ac_id:
                    # Simple typo detection: differ by 1-2 characters
                    if self._is_likely_typo(ac_id, other_ac_id):
                        issues.append(CoherenceIssue(
                            issue_type="INCONSISTENCY",
                            severity="WARNING",
                            file_path=definition.get('file', 'unknown'),
                            line_number=definition.get('line'),
                            ac_id=ac_id,
                            description=f"AC-ID '{ac_id}' is similar to '{other_ac_id}' (possible typo)",
                            suggestion="Verify AC-ID spelling",
                        ))
                        break  # Only report once per AC-ID

        return Ok(issues)

    def check_reference_validity(
        self,
        references: Dict[str, List[str]],
        defined_ac_ids: Set[str],
    ) -> Result[List[CoherenceIssue]]:
        """
        Check that all references resolve to valid AC-IDs.

        Args:
            references: Dict mapping AC-ID to list of references it makes
            defined_ac_ids: Set of defined AC-IDs

        Returns:
            Result with list of invalid references
        """
        issues = []

        for ac_id, refs in references.items():
            for ref in refs:
                if ref not in defined_ac_ids:
                    issues.append(CoherenceIssue(
                        issue_type="INVALID_REFERENCE",
                        severity="ERROR",
                        file_path="unknown",
                        line_number=None,
                        ac_id=ac_id,
                        description=f"Reference to undefined AC-ID: {ref}",
                        suggestion=f"Define {ref} or fix the reference",
                    ))

        return Ok(issues)

    def check_contradiction_detection(
        self,
        ac_definitions: Dict[str, Dict[str, Any]],
    ) -> Result[List[CoherenceIssue]]:
        """
        Detect contradictory AC-IDs.

        Args:
            ac_definitions: Dict of AC-ID definitions with descriptions

        Returns:
            Result with list of contradictions
        """
        issues = []

        # Check for "MUST" vs "MUST NOT" contradictions
        must_not_keywords = {'must not', 'must_not', 'shall not', 'shall_not', 'cannot', 'cannot not'}
        must_keywords = {'must', 'shall', 'required'}

        for ac_id, definition in ac_definitions.items():
            description = (definition.get('description') or '').lower()

            has_must = any(keyword in description for keyword in must_keywords)
            has_must_not = any(keyword in description for keyword in must_not_keywords)

            # Check against other AC-IDs for contradictions
            for other_ac_id, other_def in ac_definitions.items():
                if ac_id == other_ac_id:
                    continue

                other_description = (other_def.get('description') or '').lower()

                # Simple contradiction check: same key term but conflicting directives
                if has_must and any(keyword in other_description for keyword in must_not_keywords):
                    # Check if they're about the same thing
                    if self._has_semantic_similarity(description, other_description):
                        issues.append(CoherenceIssue(
                            issue_type="CONTRADICTION",
                            severity="ERROR",
                            file_path=definition.get('file', 'unknown'),
                            line_number=definition.get('line'),
                            ac_id=ac_id,
                            description=f"Contradicts {other_ac_id}",
                            suggestion=f"Reconcile {ac_id} and {other_ac_id}",
                        ))

        return Ok(issues)

    def _is_likely_typo(self, ac_id1: str, ac_id2: str) -> bool:
        """
        Check if two AC-IDs are likely typos of each other.

        Args:
            ac_id1: First AC-ID
            ac_id2: Second AC-ID

        Returns:
            True if likely typo
        """
        # Simple check: Levenshtein distance
        if len(ac_id1) != len(ac_id2):
            return False

        differences = sum(c1 != c2 for c1, c2 in zip(ac_id1, ac_id2))
        return 1 <= differences <= 2

    def _has_semantic_similarity(self, text1: str, text2: str) -> bool:
        """
        Check if two texts have semantic similarity.

        Args:
            text1: First text
            text2: Second text

        Returns:
            True if similar
        """
        # Extract key words (excluding common words)
        stop_words = {'the', 'a', 'is', 'are', 'must', 'shall', 'be', 'not', 'and', 'or'}

        words1 = set(word.lower() for word in text1.split() if word.lower() not in stop_words)
        words2 = set(word.lower() for word in text2.split() if word.lower() not in stop_words)

        # Check overlap
        if not words1 or not words2:
            return False

        intersection = words1 & words2
        union = words1 | words2

        jaccard = len(intersection) / len(union) if union else 0
        return jaccard > 0.3

    def validate_consistency(
        self,
        file_ac_definitions: Dict[str, Dict[str, Any]],
    ) -> Result[List[CoherenceIssue]]:
        """
        Run all coherence validations.

        Args:
            file_ac_definitions: Dict of AC-ID definitions by file

        Returns:
            Result with combined list of all issues
        """
        all_issues = []

        # Flatten definitions for analysis
        flattened = {}
        for file_path, ac_ids in file_ac_definitions.items():
            for ac_id, definition in ac_ids.items():
                if ac_id not in flattened:
                    flattened[ac_id] = {}
                definition['file'] = file_path
                flattened[ac_id][file_path] = definition

        # Check file-to-file coherence
        result1 = self.check_file_to_file_coherence(flattened)
        if result1.is_ok():
            all_issues.extend(result1.unwrap())

        # Check AC-ID naming
        flat_defs = {ac_id: list(v.values())[0] for ac_id, v in flattened.items()}
        result2 = self.check_ac_id_naming_consistency(flat_defs)
        if result2.is_ok():
            all_issues.extend(result2.unwrap())

        # Check contradictions
        result3 = self.check_contradiction_detection(flat_defs)
        if result3.is_ok():
            all_issues.extend(result3.unwrap())

        return Ok(list(set(all_issues)))  # Deduplicate

    def generate_coherence_report(
        self,
        issues: List[CoherenceIssue],
    ) -> Dict[str, Any]:
        """
        Generate coherence validation report.

        Args:
            issues: List of detected issues

        Returns:
            Report dictionary
        """
        errors = [i for i in issues if i.severity == "ERROR"]
        warnings = [i for i in issues if i.severity == "WARNING"]

        issue_types = {}
        for issue in issues:
            if issue.issue_type not in issue_types:
                issue_types[issue.issue_type] = []
            issue_types[issue.issue_type].append(issue)

        return {
            'total_issues': len(issues),
            'errors': len(errors),
            'warnings': len(warnings),
            'error_details': [i.__dict__ for i in errors],
            'warning_details': [i.__dict__ for i in warnings],
            'by_type': {
                issue_type: len(items)
                for issue_type, items in issue_types.items()
            },
            'is_valid': len(errors) == 0,
        }
