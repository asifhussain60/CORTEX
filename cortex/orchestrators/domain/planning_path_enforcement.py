"""
AC-PERMANENT-FIX-011: Planning Output Path Enforcement

This module provides permanent enforcement for planning file placement.
All planning artifacts MUST be created in: cortex-registry/planning/{plan-id}/

Do NOT import directly - this is for reference and enforcement only.
The actual implementation is integrated into PlanningOrchestrator.

Authority: AC-PERMANENT-FIX-011
Type: TIER-0-IMMUTABLE (Permanent Fix)
"""

# ==============================================================================
# ENFORCEMENT RULES (TIER-0-IMMUTABLE)
# ==============================================================================

PLANNING_FILE_PLACEMENT_RULES = """
✅ AC-PERMANENT-FIX-011: Planning File Placement Rules

RULE 1: Output Location
--------
ALL planning artifacts MUST be created in:
  cortex-registry/planning/{plan-id}/{artifact-type}/{filename}

RULE 2: Plan ID Format
--------
Plan IDs MUST be kebab-case (lowercase, dashes only):
  ✅ Valid:   phase-4, ac-permanent-fix-011, feature-xyz-123
  ❌ Invalid: Phase4, AC_PERMANENT_FIX_011, Feature XYZ

RULE 3: Artifact Types
--------
Supported artifact types:
  • phase_spec        : Phase specification documents
  • phase_completion  : Phase completion reports
  • execution_plan    : Execution plans
  • roadmap          : Roadmap documents
  • strategy         : Strategy documents
  • analysis         : Analysis reports

RULE 4: Filenames
--------
All filenames MUST comply with CORE-028:
  - Use FilenameFactory.generate() for naming
  - Lowercase, kebab-case, descriptive
  - File extensions: .md (markdown), .yaml (specs), .json (data)

RULE 5: Zero Exceptions Policy
--------
NO planning files are permitted in:
  ❌ docs/
  ❌ docs/02-architecture/
  ❌ _workspaces/
  ❌ Any other location

RULE 6: Enforcement
--------
✅ PlanningOrchestrator validates all output paths
✅ Pre-commit hooks block invalid paths
✅ FilenameFactory validates all filenames
✅ Integration tests verify compliance

VIOLATION HANDLING:
  1. Pre-commit hook BLOCKS the commit
  2. Error message points to AC-PERMANENT-FIX-011
  3. Developer must move file to correct location
  4. No workarounds or exceptions permitted
"""

# ==============================================================================
# INTEGRATION GUIDE
# ==============================================================================

INTEGRATION_EXAMPLE = """
from cortex.orchestrators.domain.planning_orchestrator import PlanningOrchestrator

# Initialize orchestrator
planner = PlanningOrchestrator.instance()

# All files created via planner are automatically placed correctly:
# - cortex-registry/planning/{plan-id}/{artifact-type}/{filename}
# - Filenames via FilenameFactory
# - Paths validated automatically

# Create a phase completion report
result = planner.create_phase_completion(
    plan_id="phase-4",
    content=report_content,
    # File is automatically placed in:
    # cortex-registry/planning/phase-4/phase_completion/phase-4-completion.md
)

# Query planning artifacts
artifacts = planner.list_artifacts(plan_id="phase-4")
# Returns:
# {
#   "phase-spec": ["phase-4-refactoring-spec.md"],
#   "phase_completion": ["phase-4-completion.md"],
#   "analysis": ["ac-010-status-phase-4-ready.md"]
# }
"""

# ==============================================================================
# VERIFICATION CHECKLIST
# ==============================================================================

VERIFICATION_CHECKLIST = """
✅ Verify AC-PERMANENT-FIX-011 Implementation:

1. File Structure
   □ cortex-registry/planning/ exists
   □ Subdirectories follow pattern: {plan-id}/{artifact-type}/
   □ No .md files in docs/02-architecture/ related to planning
   □ All phase files migrated to registry

2. Plan IDs
   □ All plan IDs are kebab-case
   □ No underscores or mixed case
   □ Examples: phase-1, phase-4, ac-permanent-fix-010

3. Artifact Organization
   □ phase_spec/ contains specification files
   □ phase_completion/ contains completion reports
   □ analysis/ contains status/analysis files
   □ roadmap/ contains roadmap files

4. Filenames
   □ All filenames follow CORE-028 conventions
   □ No spaces in filenames
   □ Lowercase with dashes
   □ Descriptive and meaningful

5. Integration
   □ PlanningOrchestrator uses PlanningOutputPathManager
   □ FilenameFactory integrated for all new files
   □ Pre-commit hooks active
   □ Tests verify path compliance

6. Enforcement
   □ No files can be manually created outside registry
   □ Pre-commit hook blocks violations
   □ CI/CD pipeline validates structure
   □ Documentation references this fix
"""

print(__doc__)
print(PLANNING_FILE_PLACEMENT_RULES)
print(INTEGRATION_EXAMPLE)
print(VERIFICATION_CHECKLIST)
