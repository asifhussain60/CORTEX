# Root Cause Analysis: Duplicate Continuation Prompts & File Location Violations

**Date:** 2026-01-03  
**Issue:** Two continuation prompt files created in wrong locations  
**Impact:** Confusion, brittleness, SKULL rule violations

---

## 🔍 Problem Statement

**Observed Symptoms:**
1. ✅ `tracking/CONTINUATION-PROMPT.md` (CORRECT location)
2. ❌ `CONTINUATION-PROMPT-PHASE-6-3.md` (WRONG location - plan root instead of tracking/)

**User Question:** "why are there 2 continuation prompts? This is what causes problems. How do we enforce that files are created in their proper locations every single time."

---

## 🧪 Root Cause Analysis

### Root Cause #1: Code Implementation vs Manual Creation

**The Code (BaseOrchestratorV4.1):**
```python
# src/orchestrators/base/base_orchestrator_v4_1.py:533
prompt_path = plan_dir / "tracking" / "CONTINUATION-PROMPT.md"
prompt_path.parent.mkdir(parents=True, exist_ok=True)
prompt_path.write_text(prompt_content, encoding='utf-8')
```

**✅ Result:** Code CORRECTLY creates file in `tracking/` folder

**The Manual Creation:**
Someone (likely during manual planning work or token limit recovery) created:
```
CONTINUATION-PROMPT-PHASE-6-3.md
```

**❌ Result:** File created in plan root directory (violates FILE_ORGANIZATION_ENFORCEMENT)

**Evidence:**
- `tracking/CONTINUATION-PROMPT.md` last modified: 2026-01-02 (automated update)
- `CONTINUATION-PROMPT-PHASE-6-3.md` last modified: 2026-01-02 (manual creation during Phase 6.3 work)

### Root Cause #2: Missing SKULL Rule Enforcement

**Problem:** `FILE_ORGANIZATION_ENFORCEMENT` exists but NOT enforced programmatically

**Current State:**
```yaml
# cortex-brain/brain-protection-rules.yaml:5324
- rule_id: "FILE_ORGANIZATION_ENFORCEMENT"
  name: "File Organization Enforcement"
  severity: "blocked"
  description: "All documents MUST be created in cortex-brain/documents/{category}/ 
               with filename ≤20 characters. Root-level files PROHIBITED."
```

**Gap:** Rule defined in YAML, but no runtime enforcement mechanism

**Result:** 
- Copilot can create files in wrong locations
- Manual file creation bypasses rule
- No validation gate prevents violations

### Root Cause #3: Incomplete Rule Specification

**The Rule Says:**
> "All documents MUST be created in cortex-brain/documents/{category}/"

**The Reality:**
Planning files have different structure:
```
cortex-brain/documents/planning/active/{PLAN_NAME}/
├── 00-master-plan.md    # Plan root
├── tracking/            # Session state
│   ├── CONTINUATION-PROMPT.md
│   ├── progress.json
│   └── state-snapshot.json
├── context/             # Discovery artifacts
├── reports/             # Phase reports
└── artifacts/           # Supporting files
```

**Mismatch:** Rule doesn't account for planning folder structure with subfolders

---

## 💥 Impact Analysis

### Impact #1: Confusion & Brittleness
- Multiple continuation prompts confuse users ("which one is correct?")
- Stale files not updated when orchestrator updates tracking/ version
- Manual intervention required to clean up duplicates

### Impact #2: SKULL Rule Violations
- **FILE_ORGANIZATION_ENFORCEMENT** violated (root-level plan files)
- **DOCUMENT_ORGANIZATION_ENFORCEMENT** violated (no category folder)
- **HOLISTIC_DISCOVERY** bypassed (duplicate file created without checking existing)

### Impact #3: Cross-Session Context Breaks
- `CrossSessionContextMiddleware` reads `tracking/CONTINUATION-PROMPT.md`
- If manual file is newer, middleware may miss automated updates
- Session resumption uses stale context

---

## ✅ Solution Design

### Solution #1: Programmatic File Location Validation

**Add Brain Protector Agent Check:**

```python
# src/cortex_agents/brain_protector.py (NEW METHOD)

def validate_file_location(self, file_path: str, file_category: str) -> ValidationResult:
    """
    Validate file created in correct location per SKULL rules.
    
    Args:
        file_path: Proposed file path
        file_category: Type (report, analysis, planning, etc.)
    
    Returns:
        ValidationResult with pass/fail + corrected path
    """
    path = Path(file_path)
    
    # Rule 1: Planning files must be in plan subfolders
    if file_category == "planning":
        valid_subfolders = ["tracking", "context", "reports", "artifacts", "phases"]
        
        # Extract plan folder structure
        parts = path.parts
        if "planning" in parts and "active" in parts:
            plan_idx = parts.index("active") + 1
            if plan_idx + 1 < len(parts):  # Has subfolder
                subfolder = parts[plan_idx + 1]
                if subfolder not in valid_subfolders:
                    return ValidationResult(
                        passed=False,
                        severity="blocked",
                        rule_id="FILE_ORGANIZATION_ENFORCEMENT",
                        message=f"Planning file must be in valid subfolder: {valid_subfolders}",
                        corrected_path=str(path.parent / "tracking" / path.name)
                    )
            else:  # Root-level plan file
                # Only 00-master-plan.md allowed at root
                if path.name != "00-master-plan.md":
                    return ValidationResult(
                        passed=False,
                        severity="blocked",
                        rule_id="FILE_ORGANIZATION_ENFORCEMENT",
                        message="Only 00-master-plan.md allowed at plan root. Use tracking/ subfolder.",
                        corrected_path=str(path.parent / "tracking" / path.name)
                    )
    
    # Rule 2: Non-planning documents must be in category folders
    elif file_category in ["report", "analysis", "summary", "investigation", "implementation-guide"]:
        if not str(path).startswith(f"cortex-brain/documents/{file_category}"):
            return ValidationResult(
                passed=False,
                severity="blocked",
                rule_id="DOCUMENT_ORGANIZATION_ENFORCEMENT",
                message=f"Must be in cortex-brain/documents/{file_category}/",
                corrected_path=f"cortex-brain/documents/{file_category}/{path.name}"
            )
    
    # Rule 3: Filename length ≤20 characters (excluding extension)
    stem_length = len(path.stem)
    if stem_length > 20:
        return ValidationResult(
            passed=False,
            severity="warning",
            rule_id="FILE_ORGANIZATION_ENFORCEMENT",
            message=f"Filename too long ({stem_length} chars). Max 20 characters.",
            corrected_path=str(path.parent / f"{path.stem[:20]}{path.suffix}")
        )
    
    return ValidationResult(passed=True)
```

**Integration Point:**

```python
# src/orchestrators/base/base_orchestrator_v4_1.py

def write_artifact(self, file_path: str, content: str, category: str = "planning") -> Path:
    """
    Write artifact with location validation.
    
    Args:
        file_path: Target file path
        content: File content
        category: File category (planning, report, analysis, etc.)
    
    Returns:
        Path: Actual path written (may be corrected)
    """
    # VALIDATION GATE
    validation = self.brain_protector.validate_file_location(file_path, category)
    
    if not validation.passed:
        if validation.severity == "blocked":
            self.logger.error(
                f"FILE LOCATION VIOLATION: {validation.message}\n"
                f"Attempted: {file_path}\n"
                f"Corrected: {validation.corrected_path}"
            )
            # Use corrected path instead
            file_path = validation.corrected_path
        elif validation.severity == "warning":
            self.logger.warning(
                f"FILE LOCATION WARNING: {validation.message}\n"
                f"Using corrected path: {validation.corrected_path}"
            )
            file_path = validation.corrected_path
    
    # Proceed with write
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')
    
    self.logger.info(f"Artifact written: {path}")
    return path
```

### Solution #2: Update SKULL Rule Specification

**Expand FILE_ORGANIZATION_ENFORCEMENT to cover planning structure:**

```yaml
# cortex-brain/brain-protection-rules.yaml (UPDATE)

- rule_id: "FILE_ORGANIZATION_ENFORCEMENT"
  name: "File Organization Enforcement"
  severity: "blocked"
  description: "Files must be created in correct locations based on type"
  
  rules:
    planning_files:
      location: "cortex-brain/documents/planning/active/{PLAN_NAME}/"
      allowed_at_root:
        - "00-master-plan.md"
        - "README.md"
        - "MASTER-ORCHESTRATOR-INSTRUCTIONS.md"
      required_subfolders:
        - "tracking/"      # Session state (CONTINUATION-PROMPT.md, progress.json)
        - "context/"       # Discovery artifacts (AST analysis, semantic search)
        - "reports/"       # Phase completion reports
        - "artifacts/"     # Supporting files
        - "phases/"        # Child phase plans (optional)
      
      file_placement_rules:
        - "CONTINUATION-PROMPT.md → tracking/"
        - "progress.json → tracking/"
        - "state-snapshot.json → tracking/"
        - "*-completion.md → reports/"
        - "*-analysis.json → context/"
        - "phase-*-plan.md → phases/"
    
    document_files:
      location: "cortex-brain/documents/{category}/"
      categories:
        - "reports/"
        - "analysis/"
        - "summaries/"
        - "investigations/"
        - "planning/"
        - "implementation-guides/"
      
      file_placement_rules:
        - "test-*.md → reports/"
        - "*-analysis.md → analysis/"
        - "*-summary.md → summaries/"
        - "bug-*.md → investigations/"
        - "*-guide.md → implementation-guides/"
    
    filename_rules:
      max_length: 20  # Characters (excluding extension)
      format: "kebab-case"
      extension: ".md"
      
  validation:
    enforcement: "programmatic"
    agent: "BrainProtectorAgent.validate_file_location()"
    auto_correct: true
    severity: "blocked"
```

### Solution #3: Pre-Commit Hook for File Location

**Add git pre-commit validation:**

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Validate file locations before commit
python3 scripts/validate_file_locations.py --staged

if [ $? -ne 0 ]; then
    echo "❌ FILE LOCATION VIOLATIONS DETECTED"
    echo "Run: python scripts/validate_file_locations.py --fix"
    exit 1
fi
```

```python
# scripts/validate_file_locations.py

def validate_staged_files():
    """Validate all staged files against SKULL rules."""
    staged_files = subprocess.check_output(
        ['git', 'diff', '--cached', '--name-only'],
        text=True
    ).strip().split('\n')
    
    violations = []
    brain_protector = BrainProtectorAgent()
    
    for file_path in staged_files:
        if not file_path.endswith('.md'):
            continue
        
        # Determine category
        category = infer_category(file_path)
        
        # Validate
        result = brain_protector.validate_file_location(file_path, category)
        
        if not result.passed:
            violations.append({
                'file': file_path,
                'rule': result.rule_id,
                'message': result.message,
                'correction': result.corrected_path
            })
    
    if violations:
        print("❌ FILE LOCATION VIOLATIONS:")
        for v in violations:
            print(f"\n  File: {v['file']}")
            print(f"  Rule: {v['rule']}")
            print(f"  Issue: {v['message']}")
            print(f"  Correct: {v['correction']}")
        return False
    
    return True
```

---

## 🎯 Implementation Plan

### Phase 1: Add Programmatic Validation (2 hours)
1. **Task 1.1:** Add `validate_file_location()` to `BrainProtectorAgent` (1h)
2. **Task 1.2:** Update `BaseOrchestratorV4.1.write_artifact()` with validation gate (30m)
3. **Task 1.3:** Test with continuation prompt generation (30m)

### Phase 2: Update SKULL Rule (1 hour)
1. **Task 2.1:** Expand `FILE_ORGANIZATION_ENFORCEMENT` rule in YAML (30m)
2. **Task 2.2:** Add planning folder structure specification (30m)

### Phase 3: Add Pre-Commit Hook (1 hour)
1. **Task 3.1:** Create `scripts/validate_file_locations.py` (45m)
2. **Task 3.2:** Install pre-commit hook (15m)

### Phase 4: Clean Up Existing Violations (30 minutes)
1. **Task 4.1:** Move `CONTINUATION-PROMPT-PHASE-6-3.md` → `tracking/` (5m)
2. **Task 4.2:** Run full workspace validation (10m)
3. **Task 4.3:** Fix any other violations found (15m)

**Total Time:** 4.5 hours

---

## 📋 Acceptance Criteria

### AC-1: Single Source of Truth
- ✅ Only ONE continuation prompt exists: `tracking/CONTINUATION-PROMPT.md`
- ✅ No duplicate continuation prompts in plan root
- ✅ Orchestrator updates tracking/ version automatically

### AC-2: Programmatic Enforcement
- ✅ `validate_file_location()` catches wrong locations at runtime
- ✅ Files auto-corrected to proper locations
- ✅ Violations logged with corrected path

### AC-3: SKULL Rule Compliance
- ✅ `FILE_ORGANIZATION_ENFORCEMENT` expanded with planning structure
- ✅ Rule specifies allowed root files (00-master-plan.md only)
- ✅ Rule specifies subfolder placement (tracking/, context/, etc.)

### AC-4: Pre-Commit Protection
- ✅ Git pre-commit hook validates file locations
- ✅ Invalid files blocked from commit
- ✅ Auto-fix script available

### AC-5: Documentation Updated
- ✅ CORTEX.prompt.md references file location validation
- ✅ Planning System manifest includes location rules
- ✅ Error messages explain correct locations

---

## 🔗 Related Issues

**Issue #1:** No runtime enforcement of SKULL rules
- **Impact:** Rules exist in YAML but not enforced programmatically
- **Solution:** Brain Protector Agent validation gates

**Issue #2:** Planning folder structure not documented
- **Impact:** Confusion about where files should go
- **Solution:** Explicit specification in SKULL rules + manifest

**Issue #3:** Manual file creation bypasses validation
- **Impact:** Humans create files in wrong locations
- **Solution:** Pre-commit hooks + IDE warnings

---

## 📌 Next Steps

1. **Immediate:** Delete duplicate `CONTINUATION-PROMPT-PHASE-6-3.md` (manual cleanup)
2. **Short-term:** Implement Phase 1 (programmatic validation) - 2 hours
3. **Medium-term:** Complete Phases 2-4 (SKULL rule + hooks) - 2.5 hours
4. **Long-term:** Add to master plan Phase 10 (REFACTOR) as validation task

**Priority:** HIGH - This prevents brittleness and confusion in all future work.

---

## 🎓 Lessons Learned

1. **YAML rules alone are insufficient** - Must be enforced programmatically
2. **Manual interventions bypass automation** - Need validation at every entry point
3. **Folder structures must be explicit** - Document allowed locations clearly
4. **Git hooks prevent violations** - Catch errors before they reach repo
5. **Auto-correction is better than blocking** - Fix the problem, log the issue, proceed

**Key Insight:** "Enforcement without implementation is just documentation."
