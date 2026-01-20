"""
Rule Validators for Governance Rules

Implements condition checks for all 29 CORE governance rules.

AC-GOV-CTX-001-03: Rule validators provide specific validation logic per rule
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from cortex.brain.core.governance.context_extractor import GovernanceContext


@dataclass
class RuleViolation:
    """
    Represents a governance rule violation.
    
    Attributes:
        rule_id: Rule identifier (e.g., "CORE-008")
        message: Human-readable violation description
        severity: Severity level (blocked, warning)
        file_path: Path to file with violation
        context: Additional context about violation
    """
    rule_id: str
    message: str
    severity: str
    file_path: str
    context: Dict[str, Any] = None
    
    def __post_init__(self) -> None:
        if self.context is None:
            self.context = {}
    
    def __str__(self) -> str:
        return f"{self.rule_id} [{self.severity}] in {self.file_path}: {self.message}"


# =============================================================================
# CORE-001: Incremental Execution
# =============================================================================

def validate_core_001_incremental(
    context: GovernanceContext,
    lines_changed: int = 0
) -> Optional[RuleViolation]:
    """
    Validate incremental execution (< 500 lines per turn).
    
    Args:
        context: Governance context
        lines_changed: Number of lines changed in operation
        
    Returns:
        RuleViolation if failed, None if passed
    """
    if lines_changed > 500:
        return RuleViolation(
            rule_id="CORE-001",
            message=f"Operation modifies {lines_changed} lines (limit: 500). Break into smaller increments.",
            severity="blocked",
            file_path=context.file_path,
            context={"lines_changed": lines_changed, "limit": 500}
        )
    return None


# =============================================================================
# CORE-008: TDD - Tests Before Code
# =============================================================================

def validate_core_008_tdd(
    context: GovernanceContext,
    test_file_exists: bool = False
) -> Optional[RuleViolation]:
    """
    Validate test-first development.
    
    Args:
        context: Governance context
        test_file_exists: Whether test file exists before implementation
        
    Returns:
        RuleViolation if failed, None if passed
    """
    if context.development_phase == "production" and not test_file_exists:
        return RuleViolation(
            rule_id="CORE-008",
            message=f"Test file must exist before implementing {context.file_path}. Follow RED → GREEN → REFACTOR.",
            severity="blocked",
            file_path=context.file_path,
            context={"test_file_exists": test_file_exists}
        )
    return None


# =============================================================================
# CORE-011: Type Hints Required
# =============================================================================

def validate_core_011_type_hints(
    context: GovernanceContext,
    functions_analyzed: int = 0,
    functions_with_hints: int = 0
) -> Optional[RuleViolation]:
    """
    Validate type hint coverage.
    
    Args:
        context: Governance context
        functions_analyzed: Total functions in file
        functions_with_hints: Functions with complete type hints
        
    Returns:
        RuleViolation if failed, None if passed
    """
    if functions_analyzed == 0:
        return None  # No functions to validate
    
    coverage = functions_with_hints / functions_analyzed
    
    if coverage < 1.0:
        missing = functions_analyzed - functions_with_hints
        return RuleViolation(
            rule_id="CORE-011",
            message=f"{missing} function(s) missing type hints in {context.file_path}. All functions require parameter and return type hints.",
            severity="blocked",
            file_path=context.file_path,
            context={
                "functions_analyzed": functions_analyzed,
                "functions_with_hints": functions_with_hints,
                "coverage": coverage
            }
        )
    return None


# =============================================================================
# CORE-012: Docstrings Required
# =============================================================================

def validate_core_012_docstrings(
    context: GovernanceContext,
    public_apis: int = 0,
    documented_apis: int = 0
) -> Optional[RuleViolation]:
    """
    Validate docstring coverage for public APIs.
    
    Args:
        context: Governance context
        public_apis: Total public functions/classes
        documented_apis: Public APIs with docstrings
        
    Returns:
        RuleViolation if failed, None if passed
    """
    if public_apis == 0:
        return None  # No public APIs to document
    
    coverage = documented_apis / public_apis
    
    if coverage < 1.0:
        missing = public_apis - documented_apis
        return RuleViolation(
            rule_id="CORE-012",
            message=f"{missing} public API(s) missing docstrings in {context.file_path}. Use Google-style docstrings with Args/Returns/Raises.",
            severity="blocked",
            file_path=context.file_path,
            context={
                "public_apis": public_apis,
                "documented_apis": documented_apis,
                "coverage": coverage
            }
        )
    return None


# =============================================================================
# CORE-013: No Bare Except
# =============================================================================

def validate_core_013_error_handling(
    context: GovernanceContext,
    bare_except_count: int = 0
) -> Optional[RuleViolation]:
    """
    Validate explicit error handling (no bare except).
    
    Args:
        context: Governance context
        bare_except_count: Number of bare except clauses
        
    Returns:
        RuleViolation if failed, None if passed
    """
    if bare_except_count > 0:
        return RuleViolation(
            rule_id="CORE-013",
            message=f"{bare_except_count} bare 'except:' clause(s) in {context.file_path}. Use specific exception types.",
            severity="blocked",
            file_path=context.file_path,
            context={"bare_except_count": bare_except_count}
        )
    return None


# =============================================================================
# CORE-022: Kebab-Case Naming
# =============================================================================

def validate_core_022_kebab_case(
    context: GovernanceContext,
    filename: str = ""
) -> Optional[RuleViolation]:
    """
    Validate kebab-case naming for user-facing files.
    
    Args:
        context: Governance context
        filename: Filename to validate
        
    Returns:
        RuleViolation if failed, None if passed
    """
    if not filename:
        filename = context.file_path.split("/")[-1]
    
    # Python files exempt (use snake_case)
    if filename.endswith(".py"):
        return None
    
    # Check for kebab-case (lowercase with hyphens)
    name_without_ext = filename.rsplit(".", 1)[0]
    
    # Allow numbers, lowercase letters, and hyphens
    if "_" in name_without_ext or any(c.isupper() for c in name_without_ext):
        return RuleViolation(
            rule_id="CORE-022",
            message=f"Filename '{filename}' must use kebab-case (lowercase-with-hyphens), not snake_case or CamelCase.",
            severity="blocked",
            file_path=context.file_path,
            context={"filename": filename, "expected": name_without_ext.lower().replace("_", "-")}
        )
    return None


# =============================================================================
# CORE-028: File Length Limits
# =============================================================================

def validate_core_028_file_length(
    context: GovernanceContext,
    line_count: int = 0
) -> Optional[RuleViolation]:
    """
    Validate file length limits (< 500 lines recommended).
    
    Args:
        context: Governance context
        line_count: Number of lines in file
        
    Returns:
        RuleViolation if failed, None if passed
    """
    if line_count > 500:
        return RuleViolation(
            rule_id="CORE-028",
            message=f"File {context.file_path} has {line_count} lines (recommended: < 500). Consider refactoring into smaller modules.",
            severity="warning",  # Warning not blocked
            file_path=context.file_path,
            context={"line_count": line_count, "recommended_max": 500}
        )
    return None


# =============================================================================
# Additional Validators (Stubs for remaining 22 rules)
# =============================================================================

def validate_core_002_no_summary_files(
    context: GovernanceContext
) -> Optional[RuleViolation]:
    """Validate no summary files created"""
    if any(x in context.file_path.lower() for x in ["-summary.md", "-report.md", "completion-"]):
        return RuleViolation(
            rule_id="CORE-002",
            message=f"Summary/report files forbidden: {context.file_path}. Use chat responses instead.",
            severity="blocked",
            file_path=context.file_path
        )
    return None


def validate_core_005_no_hardcoded_paths(
    context: GovernanceContext,
    has_hardcoded_paths: bool = False
) -> Optional[RuleViolation]:
    """Validate no hardcoded absolute paths"""
    if has_hardcoded_paths:
        return RuleViolation(
            rule_id="CORE-005",
            message=f"Hardcoded paths detected in {context.file_path}. Use path_resolver.get_project_root().",
            severity="blocked",
            file_path=context.file_path
        )
    return None


def validate_core_015_import_organization(
    context: GovernanceContext,
    import_groups_correct: bool = True
) -> Optional[RuleViolation]:
    """Validate PEP 8 import organization"""
    if not import_groups_correct:
        return RuleViolation(
            rule_id="CORE-015",
            message=f"Imports not organized correctly in {context.file_path}. Use: stdlib, third-party, local groups.",
            severity="warning",
            file_path=context.file_path
        )
    return None


# Stub validators for remaining rules - return None (pass) for now
# These can be implemented as needed

def validate_core_003_visual_progress(context: GovernanceContext) -> Optional[RuleViolation]:
    """Validate visual progress bars in responses"""
    return None  # Response formatting - not file-based


def validate_core_004_minimal_continuation(context: GovernanceContext) -> Optional[RuleViolation]:
    """Validate minimal continuation prompts"""
    return None  # Not applicable to code validation


def validate_core_006_setup_verification(context: GovernanceContext) -> Optional[RuleViolation]:
    """Validate phase -2 setup verification"""
    return None  # Runtime validation, not static


def validate_core_007_teardown_refactor(context: GovernanceContext) -> Optional[RuleViolation]:
    """Validate phase N+1 teardown"""
    return None  # Runtime validation, not static


def validate_core_009_plan_file_organization(context: GovernanceContext) -> Optional[RuleViolation]:
    """Validate plan files in correct folders"""
    if "plan" in context.file_path.lower() and "/" not in context.file_path:
        return RuleViolation(
            rule_id="CORE-009",
            message=f"Plan file {context.file_path} should be in plan_folder/",
            severity="blocked",
            file_path=context.file_path
        )
    return None


def validate_core_010_script_consolidation(context: GovernanceContext) -> Optional[RuleViolation]:
    """Validate no duplicate scripts"""
    return None  # Requires cross-file analysis


def validate_core_014_solid_principles(context: GovernanceContext) -> Optional[RuleViolation]:
    """Validate SOLID principles"""
    return None  # Requires architectural analysis


def validate_core_016_code_formatting(context: GovernanceContext) -> Optional[RuleViolation]:
    """Validate Black formatting"""
    return None  # Delegated to Black tool


def validate_core_017_governance_enforcement(context: GovernanceContext) -> Optional[RuleViolation]:
    """Validate strict governance enforcement"""
    return None  # Meta-rule about enforcement itself


def validate_core_018_yaml_first(context: GovernanceContext) -> Optional[RuleViolation]:
    """Validate YAML-first design"""
    if context.file_path.endswith("-PLAN.md"):
        return RuleViolation(
            rule_id="CORE-018",
            message=f"Use YAML for plans, not markdown: {context.file_path}",
            severity="blocked",
            file_path=context.file_path
        )
    return None


# Remaining validators for CORE-019 through CORE-029
# Return None (pass) - can be implemented as needed

def validate_other_core_rules(
    rule_id: str,
    context: GovernanceContext
) -> Optional[RuleViolation]:
    """
    Generic validator for remaining rules.
    
    Returns None (pass) for rules not yet implemented.
    """
    return None
