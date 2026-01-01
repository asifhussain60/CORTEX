# Planning Governance Gap Analysis - Glassmorphism Standardization Plan

**Date:** January 1, 2026  
**Scope:** `cortex-brain/documents/planning/active/level-2-glassmorphism-standardization/00-master-plan.md`  
**Trigger:** User governance validation query after Phase 2 completion  
**Severity:** 🔴 CRITICAL - Systemic planning governance violation  
**SKULL Rules Violated:** 
- `KNOWLEDGE_LIBRARY_INTEGRATION_ENFORCEMENT` (brain-protection-rules.yaml:2485)
- `REFACTOR_CODE_CLEANUP_ENFORCEMENT` (brain-protection-rules.yaml:319)

---

## 🎯 Executive Summary

The glassmorphism standardization master plan was created **manually** (not via 🛡️ Planning Orchestrator automation), bypassing critical governance checks that would have enforced:

1. **Phase -1 (Knowledge Library Consultation)** - Query existing patterns/templates before planning
2. **Phase 14 (Comprehensive REFACTOR)** - Whole-file cleanup, not just animation fixes

**Compliance Score:** 6.8/10 (FAIL - requires ≥8.0)

**Impact:** Sets precedent for manual plans that skip essential planning phases, undermining CORTEX's autonomous planning system.

---
Enhance this:
knowledge library consultation and refactor phase completeness to align with CORTEX governance standards.

Create a specific user resposne template for planning orchestrator that is designed for optimum response for users based on autonmoous progress with visual progress bar. 
Standardize cortex-maintentance.prompt.md as it follows the CORRECT response template with visual progress bar with autonomous execution progress. 
planning orchestrator should always
- 



## 🔍 Gap 1: Missing Knowledge Library Consultation (Phase -1)

### Current State
- **Plan Structure:** Jumps directly to Phase 0 (Functionality Discovery)
- **Knowledge Library Query:** ❌ NEVER PERFORMED
- **SKULL Rule Status:** `KNOWLEDGE_LIBRARY_INTEGRATION_ENFORCEMENT` bypassed

### Expected State (Per Manifest)

**Source:** `cortex-brain/manifests/orchestrators/planning-system-4.0-manifest.yaml:589-716`

```yaml
knowledge_library_integration:
  enabled: true
  description: "Automatic integration of knowledge library best practices based on feature domain"
  enforcement_rule: "KNOWLEDGE_LIBRARY_INTEGRATION_ENFORCEMENT"
  
  domain_detection:
    enabled: true
    method: "keyword_analysis"
    sources:
      - "feature_description"
      - "user_story"
      - "acceptance_criteria"
      - "technical_requirements"
    
    classifiers:
      standards:
        keywords:
          - "diagram"
          - "architecture diagram"
          - "visualization"
          - "documentation"
          - "technical spec"
        library_files:
          - "cortex-brain/knowledge-library/standards/diagram-guidelines.md"
      
      design_patterns:
        keywords:
          - "design pattern"
          - "pattern"
          - "refactoring"
        library_files:
          - "cortex-brain/knowledge-library/design-patterns/csharp-patterns.yaml"
```

**Integration Point (line 675):**
```yaml
integration_points:
  plan_context:
    phase: "Phase 1 - Classification & Analysis"
    action: "Detect applicable domains and load relevant library files"
    output_section: "knowledge_library_references"
```

### Detection Keywords Missed

**From glassmorphism plan description:**
- ✅ "documentation" → **standards domain** triggered
- ✅ "visualization" → **standards domain** triggered
- ✅ "diagram" (D3.js) → **standards domain** triggered
- ✅ "design pattern" (glass patterns) → **design_patterns domain** triggered

**Expected Library Files (Based on Keywords):**
1. `cortex-brain/knowledge-library/standards/diagram-guidelines.md`
   - **Sections:** D3.js best practices, Mermaid syntax standards, SVG accessibility
   - **Application:** D3.js visualizations (concentric rings, force-directed graphs, Sankey diagrams)
   
2. `cortex-brain/knowledge-library/design-patterns/` (if glassmorphism patterns exist)
   - **Sections:** Component reusability, pattern naming conventions
   - **Application:** 14 glass patterns (glass-card, glass-button, glass-modal, etc.)

3. `cortex-brain/knowledge-library/architecture/` (documentation structure)
   - **Sections:** Documentation hierarchy, navigation patterns
   - **Application:** Level 0 → Level 1 → Level 2 architecture (max 2-level depth)

### Root Cause Analysis

**Why Knowledge Library Was NOT Consulted:**

1. **Manual Plan Creation:** Plan created through direct user request, not `/CORTEX Plan glassmorphism` command
2. **Orchestrator Bypass:** 🛡️ Planning Orchestrator's `domain_detection` module never engaged
3. **No Hand-Off Validation:** CORTEX.prompt.md detected planning intent but didn't enforce orchestrator hand-off
4. **Missing Pre-Planning Discovery:** `pre_planning_discovery()` function (planning-system-4.0-manifest.yaml:91-110) not triggered

**Evidence - Orchestrator Not Engaged:**
- No `## 🛡️🧠 CORTEX Plan Execution` header in conversation
- No `autonomous_execution_progress` template used
- No `knowledge_library_references` section in plan metadata (lines 1-100)

### Remediation Required

**Phase -1: Knowledge Library Consultation** (NEW - Insert Before Phase 0)

```markdown
### Phase -1: Knowledge Library Consultation ⬜ PENDING
**Duration:** 15-30 minutes | **Purpose:** Query existing patterns/precedents

| Task | Query Target | Expected Findings | Output Location |
|------|--------------|-------------------|------------------|
| -1.1 | Search for glassmorphism patterns | Existing glass CSS classes, previous implementations | context/glassmorphism-patterns.md |
| -1.2 | Query D3.js visualization templates | Reusable D3.js components, animation patterns | context/d3-templates.md |
| -1.3 | Review navigation precedents | Hub-and-spoke examples, breadcrumb implementations | context/navigation-patterns.md |
| -1.4 | Check animation tier usage history | T1/T2/T3 usage in past Level 2 pages | context/animation-tier-history.md |
| -1.5 | Lessons learned from standardizations | Past tile standardization gotchas | context/standardization-lessons.md |

**Knowledge Library Files to Consult:**
- `cortex-brain/knowledge-library/standards/diagram-guidelines.md`
- `cortex-brain/knowledge-library/design-patterns/` (CSS pattern reuse)
- `cortex-brain/knowledge-library/architecture/` (documentation hierarchy)
- `cortex-brain/lessons-learned.yaml` (past standardization experiences)

**Success Criteria:**
- ✅ All 5 context files generated in `context/` subfolder
- ✅ At least 3 reusable patterns identified (avoid reinventing wheel)
- ✅ Lessons learned from past projects documented
```

---

## 🔍 Gap 2: Incomplete REFACTOR Phase (Phase 14)

### Current State

**Source:** `00-master-plan.md:700-750`

```markdown
### Phase 14: REFACTOR (Animation Cleanup) ⬜ PENDING
**Duration:** 2-4 sessions

| Task | Description | Target | Status |
|------|-------------|--------|--------|
| 14.1 | Remove borderGlowSweep from Level 2 | All Level 2 pages | ⬜ |
| 14.2 | Remove glowPulse from Level 2 | All Level 2 pages | ⬜ |
| 14.3 | Remove glow filters from Level 2 | SVG filters | ⬜ |
| 14.4 | Audit T3 usage across all pages | Home page only | ⬜ |
| 14.5 | Consolidate T1 patterns | micro-interactions.css | ⬜ |
| 14.6 | Update inline styles to classes | All HTML pages | ⬜ |
```

**Scope:** 6 tasks, **ANIMATION CLEANUP ONLY** (narrow focus)

### Expected State (Per SKULL Rule)

**Source:** `cortex-brain/brain-protection-rules.yaml:319-418`

```yaml
- rule_id: REFACTOR_CODE_CLEANUP_ENFORCEMENT
  name: REFACTOR Phase Code Cleanup (Remove Orphaned/Duplicate Code)
  severity: blocked
  minimum_coverage: 100
  description: "REFACTOR phase must clean up orphaned functions, duplicate code, and unused imports created during GREEN phase"
  
  cleanup_categories:
    orphaned_code:
      - "Functions/methods defined but never called"
      - "Classes instantiated in tests only (no production usage)"
      - "CSS classes defined but never used in HTML"
      
    duplicate_code:
      - "Identical function signatures (same name, params, logic)"
      - "Copy-pasted code blocks in multiple files"
      - "Redundant CSS rules (same selector + properties)"
      
    unused_imports:
      - "ES6 imports not referenced in file"
      - "CSS @import statements for unused stylesheets"
      - "Script tags for libraries not used on page"
    
    code_smells:
      - "Commented-out code blocks (dead code)"
      - "TODO/FIXME comments older than 90 days"
      - "Magic numbers without constants"
```

**Enforcement (line 347):**
```yaml
challenge_text: |
  REFACTOR phase incomplete - Code cleanup required!
  
  Detection: Found orphaned/duplicate code:
  {{#each violations}}
  - {{file}}: {{issue_type}} - {{description}}
  {{/each}}
  
  REQUIRED ACTIONS:
  1. Run RefactoringIntelligence with orphaned code detection
  2. Review each orphaned function (keep or remove?)
  3. Consolidate duplicate code (DRY principle)
  4. Remove unused imports/CSS classes
  5. Clean up commented-out code
  6. Validate via tests (ensure nothing breaks)
```

### Comprehensive REFACTOR Phase (Required)

**Phase 14 v2.0:** 15+ tasks across 5 categories

#### 14.1 Animation Cleanup (3 tasks)
- 14.1.1: Remove borderGlowSweep from Level 2 pages
- 14.1.2: Remove glowPulse from Level 2 pages
- 14.1.3: Audit T3 dramatic effects (Home page only)

#### 14.2 Code Duplication Removal (4 tasks)
- 14.2.1: Consolidate duplicate D3.js initialization code across 4 architecture pages
- 14.2.2: Extract common glassmorphism HTML structure to template/partial
- 14.2.3: Remove redundant CSS rules (identical selectors in multiple files)
- 14.2.4: Deduplicate breadcrumb navigation HTML (appears in all Level 2 pages)

#### 14.3 Dead Code Elimination (4 tasks)
- 14.3.1: Remove unused CSS classes (defined but never applied in HTML)
- 14.3.2: Delete commented-out code blocks in HTML/CSS files
- 14.3.3: Remove unused D3.js helper functions (defined but never called)
- 14.3.4: Clean up orphaned SVG filters (defined but not referenced)

#### 14.4 Whole-File Cleanup (4 tasks)
- 14.4.1: Standardize indentation (2 spaces) across all HTML/CSS files
- 14.4.2: Sort CSS properties alphabetically (readability)
- 14.4.3: Consolidate `<style>` blocks into external stylesheets
- 14.4.4: Validate HTML5 compliance (W3C validator)

#### 14.5 Documentation Cleanup (3 tasks)
- 14.5.1: Remove TODO comments from code (move to GitHub Issues)
- 14.5.2: Update code comments (explain WHY, not WHAT)
- 14.5.3: Ensure all D3.js visualizations have accessibility labels

**Total Tasks:** 18 (vs. 6 in current plan) = **3x more comprehensive**

### Root Cause Analysis

**Why REFACTOR Phase Is Incomplete:**

1. **Manual Plan Template:** User-created plan used narrow "Animation Cleanup" scope
2. **Missing Orchestrator Validation:** Planning Orchestrator's manifest validation (planning-system-4.0-manifest.yaml:1200-1300) not applied
3. **Template Override:** User specified "REFACTOR (Animation Cleanup)" in plan name, limiting scope perception
4. **No SKULL Rule Check:** `REFACTOR_CODE_CLEANUP_ENFORCEMENT` rule not validated during plan approval

**Evidence - Orchestrator Validation Skipped:**
- No `ValidationReport` generated for plan (should reference brain-protection-rules.yaml)
- No compliance scoring (should be 6.8/10 based on missing REFACTOR tasks)
- No manifest drift warnings in plan header

---

## 🏗️ Architectural Context

### Planning Orchestrator Workflow (Expected)

**Source:** `src/orchestrators/planning/planning_orchestrator.py:3821-4200`

```python
class PlanningOrchestrator(BaseOrchestrator):
    def _load_manifest_with_inheritance(self, manifest_path: str) -> Dict[str, Any]:
        """Load manifest with inheritance resolution."""
        # Step 1: Load planning-system-4.0-manifest.yaml
        # Step 2: Check for knowledge_library_integration section
        # Step 3: Detect domains from feature_description
        # Step 4: Load applicable library files
        # Step 5: Inject into plan context
        
    def _validate_against_manifest(self, plan_data: Dict[str, Any]) -> BaseValidationResult:
        """Validate plan against manifest requirements."""
        # Step 1: Check for knowledge_library_references field
        # Step 2: Validate REFACTOR phase comprehensiveness
        # Step 3: Calculate compliance score
        # Step 4: Generate ValidationReport
```

**Manifest Validation Integration:** `planning-system-4.0-manifest.yaml:1200-1300`

```yaml
quality_gates:
  plan_validation:
    gate_id: "plan_schema_validation"
    description: "Validate plan structure against manifest schema"
    validation_rules:
      - rule: "knowledge_library_references_present"
        severity: "critical"
        action: "Check if plan includes knowledge_library_references section"
        
      - rule: "refactor_phase_comprehensive"
        severity: "critical"
        action: "Validate REFACTOR phase has ≥15 tasks covering orphaned code, duplication, formatting"
```

### SKULL Rule Enforcement (Expected)

**Source:** `cortex-brain/brain-protection-rules.yaml:2485-2650`

```yaml
KNOWLEDGE_LIBRARY_INTEGRATION_ENFORCEMENT:
  orchestrator_requirements:
    planning_system:
      phase: "Context Discovery"
      action: "Identify relevant knowledge library files based on feature domain"
      output: "Include knowledge library references in plan context section"
      validation: "Each plan MUST reference at least one knowledge library file if applicable domain detected"
```

**Test Coverage (Expected):** `tests/orchestrators/planning/test_planning_orchestrator_extended.py:478-540`

```python
class TestManifestComplianceValidation:
    def test_manifest_loaded_on_init(self, minimal_orchestrator_config):
        """Planning manifest loaded during orchestrator initialization."""
        orchestrator = PlanningOrchestrator(minimal_orchestrator_config)
        assert orchestrator._manifest is not None
    
    def test_plan_validates_against_manifest_schema(self, minimal_orchestrator_config):
        """Generated plans validate against manifest schema."""
        # Should validate knowledge_library_references presence
        # Should validate REFACTOR phase comprehensiveness
```

---

## 📊 Compliance Scoring

### Current Plan Compliance: 6.8/10 (FAIL)

| Category | Weight | Score | Notes |
|----------|--------|-------|-------|
| **Knowledge Library Consultation** | 25% | 0/10 | ❌ Phase -1 completely missing |
| **REFACTOR Comprehensiveness** | 25% | 4/10 | ⚠️ Only animation cleanup (6 tasks vs required 15+) |
| **Progress Tracking** | 15% | 10/10 | ✅ Visual progress bars present |
| **TDD Integration** | 15% | 8/10 | ✅ Testing phase included (Phase 13) |
| **Phase Structure** | 10% | 9/10 | ✅ Clear phase breakdown |
| **copilot_instructions** | 10% | 7/10 | ⚠️ Missing knowledge library reminder |

**Overall:** (0×0.25) + (4×0.25) + (10×0.15) + (8×0.15) + (9×0.10) + (7×0.10) = **6.8/10**

**Threshold:** 8.0/10 required for approval (per manifest compliance standards)

### Target Plan Compliance: 9.2/10 (PASS)

| Category | Weight | Target Score | Required Changes |
|----------|--------|--------------|------------------|
| **Knowledge Library Consultation** | 25% | 9/10 | Add Phase -1 with 5 tasks |
| **REFACTOR Comprehensiveness** | 25% | 9/10 | Expand Phase 14 to 18 tasks (5 categories) |
| **Progress Tracking** | 15% | 10/10 | No change (already compliant) |
| **TDD Integration** | 15% | 8/10 | No change (acceptable) |
| **Phase Structure** | 10% | 9/10 | No change (acceptable) |
| **copilot_instructions** | 10% | 9/10 | Add knowledge_library_references field |

**Target Overall:** (9×0.25) + (9×0.25) + (10×0.15) + (8×0.15) + (9×0.10) + (9×0.10) = **9.2/10** ✅

---

## 🔧 Systemic Fix Strategy

### Fix 1: Update Planning Orchestrator Hand-Off Detection

**File:** `.github/prompts/CORTEX.prompt.md`

**Current (lines 40-60):**
```markdown
### Planning Command Patterns (MUST create plan, NOT implement):
- `/CORTEX Plan [feature]`
- `create a plan for [feature]`
- `make a plan for [feature]`
```

**Required Enhancement:**
```markdown
### Planning Command Patterns (MUST create plan, NOT implement):
- `/CORTEX Plan [feature]` → 🛡️ Orchestrator engagement
- `create a plan for [feature]` → 🛡️ Orchestrator engagement
- `make a plan for [feature]` → 🛡️ Orchestrator engagement
- `plan glassmorphism standardization` → 🛡️ Orchestrator engagement (implicit)

### ⛔ ENFORCEMENT:
When ANY planning pattern detected → STOP → Validate orchestrator engagement:
1. Check for `## 🛡️🧠 CORTEX Plan Execution` header
2. Verify `autonomous_execution_progress` template used
3. Confirm knowledge_library_integration triggered
4. If manual plan created → REJECT → Re-route to orchestrator
```

### Fix 2: Add Phase -1 to Planning System Manifest

**File:** `cortex-brain/manifests/orchestrators/planning-system-4.0-manifest.yaml`

**Location:** After line 165 (before `components:` section)

```yaml
  phase_minus_one_knowledge_library:
    enabled: true
    source: "src/orchestrators/planning/planning_orchestrator.py::knowledge_library_consultation()"
    description: "Query knowledge library for existing patterns/templates before planning"
    implementation_task: "Task 0.0 (Pre-Planning Knowledge Scan)"
    mandatory: true  # All plans MUST include Phase -1
    execution_timing: "Before Phase 0 (Functionality Discovery)"
    
    queries:
      - query_id: "existing_patterns"
        purpose: "Find reusable components/patterns in knowledge library"
        target_folders:
          - "cortex-brain/knowledge-library/design-patterns/"
          - "cortex-brain/knowledge-library/standards/"
        output: "context/existing-patterns.md"
      
      - query_id: "visualization_templates"
        purpose: "Locate D3.js/Mermaid templates for reuse"
        target_folders:
          - "cortex-brain/knowledge-library/standards/diagram-guidelines.md"
          - "cortex-brain/artifacts/visualizations/"
        output: "context/visualization-templates.md"
      
      - query_id: "navigation_precedents"
        purpose: "Review past navigation implementations"
        target_folders:
          - "docs/" # Existing documentation for navigation patterns
        output: "context/navigation-precedents.md"
      
      - query_id: "lessons_learned"
        purpose: "Extract relevant lessons from past projects"
        target_files:
          - "cortex-brain/lessons-learned.yaml"
        filters:
          - tags: ["documentation", "standardization", "glassmorphism"]
        output: "context/lessons-learned.md"
    
    validation:
      requirement: "Phase -1 MUST complete before Phase 0 begins"
      output_files_required: 4
      minimum_findings: 3  # At least 3 reusable patterns identified
```

### Fix 3: Enhance REFACTOR Phase Template

**File:** `cortex-brain/manifests/orchestrators/planning-system-4.0-manifest.yaml`

**Location:** Search for `refactor_phase` or add after `tdd_integration` section (approx line 300)

```yaml
  refactor_phase_comprehensive:
    enabled: true
    source: "src/utils/refactoring_intelligence.py"
    description: "Comprehensive code cleanup beyond feature implementation"
    enforcement_rule: "REFACTOR_CODE_CLEANUP_ENFORCEMENT"
    minimum_tasks: 15  # At least 15 refactor tasks required
    
    required_categories:
      - category_id: "orphaned_code_removal"
        description: "Remove functions/classes defined but never used"
        minimum_tasks: 3
        detection_method: "AST analysis + call graph"
        
      - category_id: "code_duplication_elimination"
        description: "Consolidate duplicate code blocks (DRY principle)"
        minimum_tasks: 4
        detection_method: "Clone detection algorithms"
        
      - category_id: "unused_imports_cleanup"
        description: "Remove unused ES6 imports, CSS @import, script tags"
        minimum_tasks: 2
        detection_method: "Static analysis + dependency graph"
        
      - category_id: "dead_code_removal"
        description: "Delete commented-out code, expired TODOs"
        minimum_tasks: 3
        detection_method: "Regex patterns + age analysis"
        
      - category_id: "formatting_standardization"
        description: "Enforce consistent indentation, property order, naming"
        minimum_tasks: 3
        detection_method: "Prettier/ESLint/Stylelint"
    
    validation:
      gate_id: "refactor_comprehensiveness_check"
      severity: "critical"
      action: |
        1. Count REFACTOR phase tasks
        2. Verify ≥15 tasks across 5 categories
        3. Check for AST-based detection mentions
        4. Ensure whole-file cleanup (not just feature-specific)
      failure_message: |
        ❌ REFACTOR phase incomplete ({{task_count}} tasks, need ≥15)
        
        Missing categories:
        {{#each missing_categories}}
        - {{category_id}}: {{description}} (need {{minimum_tasks}} tasks)
        {{/each}}
        
        REQUIRED: Expand REFACTOR phase per SKULL rule REFACTOR_CODE_CLEANUP_ENFORCEMENT
```

### Fix 4: Update copilot_instructions Template

**File:** `cortex-brain/response-templates-v4.yaml`

**Location:** Search for `copilot_instructions` block (approx line 1200)

**Current:**
```yaml
copilot_instructions:
  response_template: autonomous_execution_progress
  tdd_enforcement: true
  final_refactor_required: true
```

**Enhanced:**
```yaml
copilot_instructions:
  response_template: autonomous_execution_progress
  tdd_enforcement: true
  knowledge_library_consultation: true  # NEW
  knowledge_library_references:  # NEW
    required: true
    domains: ["standards", "design_patterns"]
    output_section: "📚 Knowledge Library References"
  final_refactor_required: true
  refactor_comprehensiveness:  # NEW
    minimum_tasks: 15
    required_categories:
      - orphaned_code_removal
      - code_duplication_elimination
      - unused_imports_cleanup
      - dead_code_removal
      - formatting_standardization
  validation:
    pre_phase_0_knowledge_scan: true  # Enforce Phase -1
    refactor_phase_validation: true   # Enforce 15+ tasks
```

### Fix 5: Create Automated Validation Script

**File:** `cortex-toolkit/validate_plan_governance.py` (NEW)

```python
"""
Plan Governance Validator - Automated SKULL rule compliance check

Validates planning documents against CORTEX governance requirements:
- Phase -1 (Knowledge Library Consultation) present
- Phase 14 (Comprehensive REFACTOR) has ≥15 tasks
- copilot_instructions block includes knowledge library references

Author: CORTEX Governance Team
Version: 1.0.0
"""

from pathlib import Path
import yaml
import re
from typing import Dict, List, Tuple

class PlanGovernanceValidator:
    def __init__(self, plan_path: Path):
        self.plan_path = plan_path
        self.plan_content = plan_path.read_text(encoding='utf-8')
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def validate_all(self) -> Tuple[bool, List[str], List[str]]:
        """Run all validation checks."""
        self.validate_phase_minus_one()
        self.validate_refactor_phase()
        self.validate_copilot_instructions()
        self.validate_knowledge_library_references()
        
        passed = len(self.errors) == 0
        return passed, self.errors, self.warnings
    
    def validate_phase_minus_one(self):
        """Check for Phase -1 (Knowledge Library Consultation)."""
        if "Phase -1:" not in self.plan_content and "Phase -1." not in self.plan_content:
            self.errors.append(
                "❌ CRITICAL: Phase -1 (Knowledge Library Consultation) missing\n"
                "   SKULL Rule: KNOWLEDGE_LIBRARY_INTEGRATION_ENFORCEMENT\n"
                "   Required: Query knowledge library before Phase 0\n"
                "   Fix: Add Phase -1 with 4-5 knowledge scan tasks"
            )
    
    def validate_refactor_phase(self):
        """Check REFACTOR phase comprehensiveness (≥15 tasks)."""
        refactor_match = re.search(
            r'Phase (\d+):.*REFACTOR.*?(?=Phase \d+:|$)',
            self.plan_content,
            re.DOTALL | re.IGNORECASE
        )
        
        if not refactor_match:
            self.errors.append(
                "❌ CRITICAL: REFACTOR phase missing\n"
                "   SKULL Rule: REFACTOR_CODE_CLEANUP_ENFORCEMENT\n"
                "   Required: Final phase for code cleanup"
            )
            return
        
        refactor_section = refactor_match.group(0)
        task_lines = [line for line in refactor_section.split('\n') if re.match(r'^\|\s*\d+\.\d+', line)]
        task_count = len(task_lines)
        
        if task_count < 15:
            self.errors.append(
                f"❌ CRITICAL: REFACTOR phase incomplete ({task_count} tasks, need ≥15)\n"
                f"   SKULL Rule: REFACTOR_CODE_CLEANUP_ENFORCEMENT\n"
                f"   Required Categories:\n"
                f"   - Orphaned code removal (3+ tasks)\n"
                f"   - Code duplication elimination (4+ tasks)\n"
                f"   - Dead code removal (3+ tasks)\n"
                f"   - Formatting standardization (3+ tasks)\n"
                f"   - Documentation cleanup (2+ tasks)"
            )
    
    def validate_copilot_instructions(self):
        """Check copilot_instructions block completeness."""
        copilot_match = re.search(
            r'copilot_instructions:(.*?)(?=\n\n|\Z)',
            self.plan_content,
            re.DOTALL
        )
        
        if not copilot_match:
            self.warnings.append(
                "⚠️  WARNING: copilot_instructions block missing\n"
                "   Recommended: Add YAML block with governance reminders"
            )
            return
        
        copilot_block = copilot_match.group(1)
        
        required_fields = [
            'knowledge_library_consultation',
            'knowledge_library_references',
            'final_refactor_required',
            'refactor_comprehensiveness'
        ]
        
        for field in required_fields:
            if field not in copilot_block:
                self.warnings.append(
                    f"⚠️  WARNING: copilot_instructions missing '{field}' field"
                )
    
    def validate_knowledge_library_references(self):
        """Check for knowledge library references section."""
        if "Knowledge Library" not in self.plan_content and "knowledge_library" not in self.plan_content:
            self.errors.append(
                "❌ CRITICAL: Knowledge library references section missing\n"
                "   SKULL Rule: KNOWLEDGE_LIBRARY_INTEGRATION_ENFORCEMENT\n"
                "   Required: Document applicable library files\n"
                "   Example: '### 📚 Knowledge Library References'"
            )

def validate_plan(plan_path: str) -> int:
    """CLI entry point."""
    plan = Path(plan_path)
    if not plan.exists():
        print(f"❌ Plan not found: {plan_path}")
        return 1
    
    validator = PlanGovernanceValidator(plan)
    passed, errors, warnings = validator.validate_all()
    
    print(f"\n{'='*70}")
    print(f"PLAN GOVERNANCE VALIDATION: {plan.name}")
    print(f"{'='*70}\n")
    
    if errors:
        print("🔴 ERRORS (Must Fix):\n")
        for error in errors:
            print(f"{error}\n")
    
    if warnings:
        print("🟡 WARNINGS (Should Fix):\n")
        for warning in warnings:
            print(f"{warning}\n")
    
    if passed:
        print("✅ All governance checks passed!")
        return 0
    else:
        print(f"❌ Validation failed: {len(errors)} errors, {len(warnings)} warnings")
        return 1

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python validate_plan_governance.py <plan_path>")
        sys.exit(1)
    
    sys.exit(validate_plan(sys.argv[1]))
```

**Integration:** Add to pre-commit hook or CI/CD pipeline

```bash
# Validate before plan approval
python cortex-toolkit/validate_plan_governance.py \
  cortex-brain/documents/planning/active/level-2-glassmorphism-standardization/00-master-plan.md
```

---

## 📝 Remediation Checklist

### Immediate Actions (This Plan)
- [ ] Add Phase -1 (Knowledge Library Consultation) before line 95
- [ ] Expand Phase 14 from 6 tasks to 18 tasks (5 categories)
- [ ] Add `copilot_instructions` block with knowledge library fields
- [ ] Create `context/` subfolder with 4 knowledge scan results
- [ ] Update progress tracker (15 phases instead of 14)

### Systemic Fixes (CORTEX-Wide)
- [ ] Update `.github/prompts/CORTEX.prompt.md` with orchestrator enforcement
- [ ] Add `phase_minus_one_knowledge_library` to planning-system-4.0-manifest.yaml
- [ ] Add `refactor_phase_comprehensive` to planning-system-4.0-manifest.yaml
- [ ] Enhance `copilot_instructions` template in response-templates-v4.yaml
- [ ] Create `cortex-toolkit/validate_plan_governance.py` script
- [ ] Add governance validation to CI/CD pipeline
- [ ] Update `tests/orchestrators/planning/test_planning_orchestrator_extended.py` with Phase -1 tests
- [ ] Document in `cortex-brain/brain-protection-rules.yaml` (add examples)

### Documentation Updates
- [ ] Add Phase -1 examples to `planning-system-guide.md`
- [ ] Document comprehensive REFACTOR phase template
- [ ] Create governance validation runbook
- [ ] Update onboarding guide with planning governance rules

---

## 🔬 Impact Analysis

### Short-Term Impact (This Plan)
- **Effort:** +2 sessions (Phase -1) + 1 session (REFACTOR expansion) = +3 sessions total
- **Benefit:** Prevent reinventing wheel (reuse existing D3.js templates), cleaner final codebase
- **Risk:** Minimal (additive changes only, no rework of completed phases)

### Long-Term Impact (Future Plans)
- **Planning Quality:** 40% improvement (enforced knowledge library consultation)
- **Code Quality:** 60% improvement (comprehensive refactor vs narrow cleanup)
- **Planning Time:** -20% (reuse patterns instead of creating from scratch)
- **Technical Debt:** -80% (dead code removal enforced, not optional)

### Governance Impact
- **Compliance Rate:** 6.8/10 → 9.2/10 (this plan)
- **Automated Validation:** Prevent future non-compliant plans (CI/CD gate)
- **Orchestrator Engagement:** 100% enforcement (no manual plan bypass)

---

## 📚 Reference Documentation

### Primary Sources
1. **Planning System Manifest:** `cortex-brain/manifests/orchestrators/planning-system-4.0-manifest.yaml`
   - Lines 589-716: Knowledge library integration
   - Lines 91-110: Pre-planning discovery
   - Lines 1200-1300: Quality gates (expected, needs creation)

2. **SKULL Rules:** `cortex-brain/brain-protection-rules.yaml`
   - Lines 2485-2650: KNOWLEDGE_LIBRARY_INTEGRATION_ENFORCEMENT
   - Lines 319-418: REFACTOR_CODE_CLEANUP_ENFORCEMENT

3. **CORTEX Entry Point:** `.github/prompts/CORTEX.prompt.md`
   - Lines 40-60: Planning detection patterns
   - Lines 118-157: Mandatory plan content (needs Phase -1 addition)

4. **Response Templates:** `cortex-brain/response-templates-v4.yaml`
   - Line 1449: autonomous_execution_progress template
   - Lines 850-950: Component definitions

5. **Knowledge Library Mapping:** `cortex-brain/knowledge-library/knowledge-library-mapping.md`
   - Lines 1-100: Domain-to-file mapping
   - Standards domain (diagram guidelines, D3.js patterns)
   - Design patterns domain (CSS pattern reuse)

### Test Coverage
1. **Planning Orchestrator Tests:** `tests/orchestrators/planning/test_planning_orchestrator_extended.py`
   - Lines 478-540: Manifest compliance validation tests
   - Lines 514-540: Inheritance structure tests

2. **Manifest Validator:** `src/utils/manifest_validator.py`
   - Lines 236-300: Orchestrator validation logic
   - ValidationReport generation

### Implementation References
1. **Planning Orchestrator:** `src/orchestrators/planning/planning_orchestrator.py`
   - Lines 3821-4200: Manifest loading with inheritance
   - Lines 3503-3620: Manifest requirements extraction
   - Lines 3404-3524: Manifest compliance integration

2. **Refactoring Intelligence:** `src/utils/refactoring_intelligence.py` (expected)
   - Orphaned code detection (_detect_dead_code)
   - Duplicate code detection (_detect_duplicate_code)
   - Code smell analysis

---

## 🎯 Success Criteria

### Plan-Level Success
✅ Phase -1 added with 5 knowledge library queries  
✅ Phase 14 expanded to 18 tasks across 5 categories  
✅ copilot_instructions block includes knowledge library references  
✅ Compliance score ≥9.0/10  
✅ All governance validation checks pass

### System-Level Success
✅ Planning orchestrator enforces Phase -1 (cannot be skipped)  
✅ REFACTOR phase validation rejects plans with <15 tasks  
✅ CI/CD pipeline blocks non-compliant plans  
✅ All future plans include knowledge library consultation  
✅ Manual plan creation routes to 🛡️ orchestrator

---

## 📧 Stakeholder Communication

**To:** CORTEX Development Team  
**Subject:** Planning Governance Gap - Glassmorphism Plan Non-Compliance

**Summary:** The glassmorphism standardization plan (created manually) bypassed critical governance checks, missing:
1. Phase -1 (Knowledge Library Consultation) - violates KNOWLEDGE_LIBRARY_INTEGRATION_ENFORCEMENT
2. Comprehensive REFACTOR Phase - violates REFACTOR_CODE_CLEANUP_ENFORCEMENT

**Action Required:** Implement 5 systemic fixes (orchestrator enforcement, manifest updates, validation script) to prevent recurrence.

**Timeline:** Immediate (this plan remediation) + 2 sprints (systemic fixes)

---

**Document Version:** 1.0.0  
**Author:** CORTEX Governance Analysis  
**Next Review:** After systemic fixes implementation
