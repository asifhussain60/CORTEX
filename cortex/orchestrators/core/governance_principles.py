"""
Business Principle Mappings for CORE Rules

Maps CORE-* rule IDs to human-readable business principles inspired by
management and engineering literature. These principles make governance
rules more intuitive and memorable without replacing the canonical CORE-* IDs.

Usage:
    from cortex.orchestrators.core.governance_principles import PRINCIPLE_NAMES
    
    principle = PRINCIPLE_NAMES["CORE-030"]  # "Confront Brutal Facts"
    display = f"{principle} (CORE-030)"  # "Confront Brutal Facts (CORE-030)"

Author: Asif Hussain
Authority: CORE-029 (Documentation as Code)
"""

from typing import Dict, Optional


# ============================================================================
# PRINCIPLE MAPPINGS (Dual Naming System)
# ============================================================================

PRINCIPLE_NAMES: Dict[str, str] = {
    # Orchestration & Lifecycle
    "CORE-001": "Flywheel Effect",  # Small consistent turns build momentum
    "CORE-006": "Trust But Verify",  # Validate assumptions before acting
    "CORE-032": "Hedgehog Concept",  # Know what you're best at
    
    # Response Formatting & Communication
    "CORE-002": "Signal vs Noise",  # Eliminate noise, amplify signal
    "CORE-004": "Clarity Through Brevity",  # Say more with less
    "CORE-029": "Documentation as Code",  # If not documented, doesn't exist
    
    # Portability & Reliability
    "CORE-005": "Write Once, Run Anywhere",  # Build for portability
    "CORE-026": "Always Have an Escape Route",  # Make reversibility a constraint
    
    # Development Workflow
    "CORE-008": "Red-Green-Refactor Discipline",  # Define success before building
    "CORE-019": "Right Tool for the Job",  # Specialization beats generalization
    
    # Quality Gates
    "CORE-011": "Make Invalid States Unrepresentable",  # Catch errors at design time
    "CORE-012": "Code Tells How, Docs Tell Why",  # Future you thanks present you
    "CORE-013": "Fail Fast, Fail Explicitly",  # Silent failures are time bombs
    "CORE-025": "Make Errors First-Class Citizens",  # Errors are expected outcomes
    "CORE-030": "Confront Brutal Facts",  # Face reality, code doesn't lie
    
    # Governance & Discipline
    "CORE-017": "Culture of Discipline",  # Consistency requires non-negotiable standards
    
    # Architecture & Structure
    "CORE-018": "Machine-Readable First, Human-Readable Second",  # Build for automation
    "CORE-020": "Separation of Concerns",  # Data structures separate from docs
    "CORE-024": "Convention Over Configuration",  # Standard patterns reduce cognitive load
    "CORE-028": "Self-Documenting Systems",  # Names should tell a story
    "CORE-035": "One Source of Truth",  # Duplication is waste
    "CORE-038": "A Place for Everything, Everything in its Place",  # Organization enables scale
    "CORE-039": "Prevention Over Cure",  # Stop problems at the source
    "CORE-040": "Design for Decay",  # Entropy is inevitable, design for self-maintenance
    "CORE-041": "Same Input, Same Output",  # Systems must tolerate replay
    
    # Auditability & Transparency
    "CORE-027": "Radical Transparency",  # Trust comes from verifiable history
    "CORE-034": "Measure What Matters",  # Can't improve what you don't measure
    
    # Architectural Enforcement
    "AC-PERMANENT-FIX-006": "Built-In Quality",  # Quality built in, not inspected in
    "AC-PERMANENT-FIX-007": "One Source of Truth",  # Same as CORE-035
}


# ============================================================================
# PRINCIPLE CATEGORIES
# ============================================================================

PRINCIPLE_CATEGORIES: Dict[str, list[str]] = {
    "Execution & Momentum": [
        "CORE-001",  # Flywheel Effect
    ],
    
    "Reality & Truth": [
        "CORE-006",  # Trust But Verify
        "CORE-030",  # Confront Brutal Facts
        "CORE-034",  # Measure What Matters
    ],
    
    "Simplicity & Clarity": [
        "CORE-002",  # Signal vs Noise
        "CORE-004",  # Clarity Through Brevity
        "CORE-028",  # Self-Documenting Systems
        "CORE-035",  # One Source of Truth
        "CORE-038",  # A Place for Everything
    ],
    
    "Quality & Discipline": [
        "CORE-008",  # Red-Green-Refactor
        "CORE-011",  # Make Invalid States Unrepresentable
        "CORE-012",  # Code Tells How, Docs Tell Why
        "CORE-013",  # Fail Fast, Fail Explicitly
        "CORE-017",  # Culture of Discipline
        "CORE-025",  # Make Errors First-Class Citizens
        "AC-PERMANENT-FIX-006",  # Built-In Quality
    ],
    
    "Prevention & Design": [
        "CORE-026",  # Always Have an Escape Route
        "CORE-039",  # Prevention Over Cure
        "CORE-040",  # Design for Decay
        "CORE-041",  # Same Input, Same Output
    ],
    
    "Structure & Architecture": [
        "CORE-018",  # Machine-Readable First
        "CORE-020",  # Separation of Concerns
        "CORE-024",  # Convention Over Configuration
    ],
    
    "Specialization & Focus": [
        "CORE-019",  # Right Tool for the Job
        "CORE-032",  # Hedgehog Concept
    ],
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_principle_name(rule_id: str) -> Optional[str]:
    """
    Get the business principle name for a CORE rule ID.
    
    Args:
        rule_id: CORE rule ID (e.g., "CORE-030")
    
    Returns:
        Business principle name or None if not found
    
    Example:
        >>> get_principle_name("CORE-030")
        "Confront Brutal Facts"
    """
    return PRINCIPLE_NAMES.get(rule_id)


def get_display_name(rule_id: str) -> str:
    """
    Get display name combining principle and rule ID.
    
    Args:
        rule_id: CORE rule ID (e.g., "CORE-030")
    
    Returns:
        Display name like "Confront Brutal Facts (CORE-030)"
    
    Example:
        >>> get_display_name("CORE-030")
        "Confront Brutal Facts (CORE-030)"
    """
    principle = PRINCIPLE_NAMES.get(rule_id)
    if principle:
        return f"{principle} ({rule_id})"
    return rule_id


def get_rules_by_category(category: str) -> list[str]:
    """
    Get all rule IDs in a principle category.
    
    Args:
        category: Category name (e.g., "Reality & Truth")
    
    Returns:
        List of rule IDs in that category
    
    Example:
        >>> get_rules_by_category("Reality & Truth")
        ["CORE-006", "CORE-030", "CORE-034"]
    """
    return PRINCIPLE_CATEGORIES.get(category, [])


def list_all_principles() -> Dict[str, str]:
    """
    Get all principle mappings.
    
    Returns:
        Dictionary of rule_id -> principle name
    """
    return PRINCIPLE_NAMES.copy()
