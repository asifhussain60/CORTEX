"""
KSE synthesizers — conflict resolution, citation, violation detection, guidance.

Phase 103-g: extracted from knowledge_synthesis_engine.py (1,567L) god-object.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def resolve_rule_conflicts(
    cortex_rules: Dict[str, Any],
    company_rules: Dict[str, Any],
) -> Dict[str, Any]:
    """Resolve conflicts — company rules have OVERRIDE precedence."""
    merged = cortex_rules.copy()
    for key, value in company_rules.items():
        if key in merged:
            logger.info(f"Company rule overrides CORTEX rule: {key}")
        merged[key] = value
    return merged


def generate_citations(merged_rules: Dict[str, Any], intent_type: str) -> List[str]:
    """Generate list of rule IDs to cite in routing decision."""
    citations = []
    for rule_id in ("CORE-008", "CORE-011", "CORE-012"):
        if rule_id in merged_rules:
            citations.append(rule_id)
    if intent_type == "IMPLEMENT" and "CORE-026" in merged_rules:
        citations.append("CORE-026")
    elif intent_type == "FIX" and "CORE-013" in merged_rules:
        citations.append("CORE-013")
    return citations


def detect_violations(
    merged_rules: Dict[str, Any],
    lens_intelligence: Any,
    company_knowledge: Any,
) -> List[str]:
    """Detect rule violations based on LENS intelligence."""
    violations: List[str] = []
    ast = lens_intelligence.ast_analysis

    # Complexity
    complexity_value = ast.get("complexity", 0)
    try:
        if isinstance(complexity_value, str):
            if complexity_value.lower() in ("very_high", "high", "critical"):
                violations.append("CORTEX: High complexity detected, refactoring recommended")
            elif complexity_value.isdigit() and int(complexity_value) > 20:
                violations.append("CORTEX: High complexity detected (>20), refactoring recommended")
        elif isinstance(complexity_value, (int, float)) and complexity_value > 20:
            violations.append("CORTEX: High complexity detected (>20), refactoring recommended")
    except (ValueError, TypeError):
        pass

    # Security issues
    for issue in ast.get("security_issues", []):
        if isinstance(issue, dict):
            violations.append(
                f"SECURITY: {issue.get('severity', 'MEDIUM')} - {issue.get('type', 'UNKNOWN')}: {issue.get('description', '')}"
            )
        else:
            violations.append(f"SECURITY: {issue}")

    # Method length
    try:
        ml = int(ast.get("method_length", 0))
        if ml > 15:
            violations.append(f"CORTEX: Method too long ({ml} lines > 15 line threshold)")
    except (ValueError, TypeError):
        pass

    # LENS violations
    for v in ast.get("violations", []):
        violations.append(f"LENS: {v}")

    # FIXME count
    try:
        fixmes = int(lens_intelligence.comment_analysis.get("fixmes", 0))
        if fixmes > 5:
            violations.append("CORTEX: Excessive FIXMEs detected (>5), technical debt accumulating")
    except (ValueError, TypeError):
        pass

    # Compliance
    if "PCI-DSS" in getattr(company_knowledge, "compliance_standards", []):
        if lens_intelligence.git_analysis.get("payment_related", False):
            violations.append("COMPANY: PCI-DSS compliance check required for payment data")

    return violations


def generate_guidance(
    intent_type: str,
    merged_rules: Dict[str, Any],
    violations: List[str],
    lens_intelligence: Any,
) -> List[str]:
    """Generate proactive guidance for engineer."""
    guidance: List[str] = []
    ast = lens_intelligence.ast_analysis

    # Company rule guidance
    for key, value in merged_rules.items():
        if key.startswith(("ERR-", "LOG-", "SEC-", "PERF-", "TEST-")):
            guidance.append(f"Follow company standard {key}: {value}")

    # Security guidance
    for issue in ast.get("security_issues", []):
        if isinstance(issue, dict):
            t = issue.get("type", "")
            if "SQL_INJECTION" in t:
                guidance.append("Use parameterized queries to prevent SQL injection")
            elif "XSS" in t:
                guidance.append("Escape all user-generated content before rendering in HTML")
            elif "PATH_TRAVERSAL" in t:
                guidance.append("Validate and sanitize file paths to prevent directory traversal")

    # Intent-specific guidance
    if intent_type == "IMPLEMENT":
        if "CORE-008" in merged_rules:
            guidance.append("Start with TDD: Write test first, then implement")
        if "CORE-011" in merged_rules:
            guidance.append("Add type hints to all function signatures")
    elif intent_type == "REFACTOR":
        responsibilities = ast.get("responsibilities", [])
        rc = len(responsibilities) if isinstance(responsibilities, list) else responsibilities
        if isinstance(rc, int) and rc > 3:
            guidance.append("Apply Single Responsibility Principle")
        for v in ast.get("violations", []):
            if "single responsibility" in v.lower():
                guidance.append("Follow SOLID principles: each class should have one reason to change")

    if violations:
        guidance.append(f"Address {len(violations)} violation(s) before proceeding")

    # Complexity guidance
    cv = ast.get("complexity", 0)
    try:
        if isinstance(cv, str):
            if cv.lower() in ("very_high", "high", "critical"):
                guidance.append("Consider refactoring to reduce complexity")
            elif cv.isdigit() and int(cv) > 15:
                guidance.append(f"Consider refactoring to reduce complexity (current: {cv})")
        elif isinstance(cv, (int, float)) and cv > 15:
            guidance.append(f"Consider refactoring to reduce complexity (current: {cv})")
    except (ValueError, TypeError):
        pass

    return guidance


def extract_applicable_patterns(intent_type: str, best_practices: Dict[str, Any]) -> List[str]:
    """Extract applicable patterns for intent type."""
    _map = {
        "IMPLEMENT": ["Repository Pattern", "Factory Pattern", "TDD Pattern"],
        "FIX": ["Root Cause Analysis", "Defensive Programming"],
        "REFACTOR": ["Extract Method", "Introduce Parameter Object", "Replace Conditional with Polymorphism"],
        "ANALYZE": ["Code Metrics", "Dependency Analysis", "Complexity Analysis"],
    }
    return _map.get(intent_type, [])


def extract_anti_patterns(best_practices: Dict[str, Any]) -> List[str]:
    """Extract anti-patterns to avoid."""
    return [
        "God Object",
        "Spaghetti Code",
        "Copy-Paste Programming",
        "Magic Numbers",
        "Premature Optimization",
    ]
