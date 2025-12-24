# CORTEX 4.0 Git Commit Policy

**Version:** 1.0  
**Author:** Asif Hussain  
**Created:** December 18, 2025  
**Status:** 🟢 MANDATORY - All Phase/Week Completions  
**Branch:** CORTEX-4.0  

---

## 📋 Overview

All CORTEX 4.0 migration phase and week completions MUST follow a standardized git commit workflow. This ensures clean history, rollback safety, and progress validation.

---

## 🔒 Mandatory Workflow

### Phase/Week Completion Sequence

**Every phase/week completion follows this exact sequence:**

```bash
# 1. Complete Phase Work
#    - All deliverables finished
#    - Validation scripts passing (if applicable)
#    - Tests passing

# 2. Git Commit Phase Work
git add .
git commit -m "✅ Phase [N] Week [X] Complete: [Brief Description]

- [Deliverable 1]
- [Deliverable 2]
- [Deliverable 3]
- [Validation status]"

# 3. Update Master Plan
#    - Edit MASTER-PLAN.md progress tracker
#    - Update progress bars: [████░░░░]
#    - Update percentages
#    - Update status: ✅ COMPLETE | ⏳ ACTIVE | ☐ PENDING

# 4. Git Commit Master Plan Update
git add cortex-brain/documents/planning/active/CORTEX-3.0-4.0/CORTEX4-STATUS.md
git commit -m "📊 Update MASTER-PLAN.md: Phase [N] Week [X] progress"

# 5. Push to CORTEX-4.0 Branch
git push origin CORTEX-4.0
```

---

## 📝 Commit Message Format

### Phase/Week Work Commit

**Format:**
```
✅ Phase [N] Week [X] Complete: [Brief Description]

- [Deliverable 1]
- [Deliverable 2]
- [Deliverable 3]
- [Validation status]
```

**Examples:**

```bash
# Phase 1, Week 1 Example
git commit -m "✅ Phase 1 Week 1 Complete: Base Orchestrator & Brain

- BaseOrchestrator framework with PhaseManager
- ErrorHandler with retry/fallback logic
- Brain interface with 4-tier architecture
- 22/22 brain tests passing"

# Phase 1, Week 2 Example
git commit -m "✅ Phase 1 Week 2 Complete: Infrastructure Layer

- Response Template System v4.0 (500 lines, 97% reduction)
- ConfigManager with multi-machine path resolution
- Testing infrastructure with 12 pytest fixtures
- 4/4 validation checks passing"

# Phase 1, Week 3 Example
git commit -m "✅ Phase 1 Week 3 Complete: Foundation Prerequisites

- Dependency injection container operational
- Logging system with rotating handlers
- Response templates v4.0 integrated
- 10/10 validation checks passing"

# Phase 2, Week 4-5 Example
git commit -m "✅ Phase 2 Weeks 4-5 Complete: Hybrid Centralization

- Shared templates in ~/.cortex/shared/
- Tier 2 namespace isolation implemented
- Privacy controls with explicit sharing
- Cross-repo pattern discovery operational"
```

### Master Plan Update Commit

**Format:**
```
📊 Update MASTER-PLAN.md: Phase [N] Week [X] progress
```

**Examples:**

```bash
git commit -m "📊 Update MASTER-PLAN.md: Phase 1 Week 1 progress"

git commit -m "📊 Update MASTER-PLAN.md: Phase 1 Week 3 progress"

git commit -m "📊 Update MASTER-PLAN.md: Phase 2 Weeks 4-5 progress"
```

---

## 🎯 Rationale

### Why This Policy?

**1. Rollback Safety**
- Clean checkpoint at end of each phase/week
- Can revert to last stable state with `git reset --hard <commit>`
- No need to cherry-pick individual files

**2. Progress Validation**
- Git commit proves work is actually complete
- Can't fake progress by just updating tracker
- Audit trail shows what changed in each phase

**3. Clear History**
- Easy to see phase-by-phase evolution
- Useful for future migrations/references
- Helps onboard new contributors

**4. Collaboration**
- Others can see exactly what was completed
- Can review phase work independently
- Easier to identify issues per phase

**5. Prevents Tracker Drift**
- Master plan updates tied to actual commits
- No "claimed complete but not committed" scenarios
- Progress tracker always reflects git reality

---

## ✅ Checklist Template

Use this checklist at the end of every phase/week:

```markdown
- [ ] All deliverables completed
- [ ] Validation script passing (if applicable)
- [ ] All tests passing
- [ ] Code reviewed (self-review)
- [ ] **Git commit phase work** (✅ emoji, deliverables listed)
- [ ] Update MASTER-PLAN.md progress tracker
  - [ ] Progress bar updated
  - [ ] Percentage updated
  - [ ] Status updated
  - [ ] "Last Updated" timestamp updated
- [ ] **Git commit master plan update** (📊 emoji)
- [ ] **Git push to CORTEX-4.0 branch**
- [ ] Verify commits visible on GitHub
```

---

## 🚨 Common Mistakes to Avoid

### ❌ DON'T:

1. **Don't combine phase work and master plan in single commit**
   - Makes rollback ambiguous
   - Breaks clean separation

2. **Don't update master plan before phase work is committed**
   - Creates false progress
   - Breaks audit trail

3. **Don't skip validation before committing**
   - Commit should represent working state
   - Validation failures should block commit

4. **Don't use vague commit messages**
   - ❌ "Phase 1 done"
   - ✅ "✅ Phase 1 Week 3 Complete: Foundation Prerequisites"

5. **Don't forget to push**
   - Local commits aren't backed up
   - Others can't see your progress

### ✅ DO:

1. **Run validation scripts before committing**
   ```bash
   python scripts/validate_week_2_infrastructure.py
   python scripts/validate_cortex_4_foundation.py
   ```

2. **List actual deliverables in commit message**
   - Specific files/features completed
   - Validation results
   - Test coverage metrics

3. **Update master plan immediately after phase commit**
   - Don't let tracker drift
   - Commit master plan separately

4. **Push both commits together**
   ```bash
   git push origin CORTEX-4.0  # Pushes both commits
   ```

---

## 📊 Integration with Orchestrators

**Future Enhancement (Phase 4):**

Orchestrators will auto-commit phase work:

```python
# In BaseOrchestrator.complete_phase()
def complete_phase(self, phase_name, deliverables, validation_result):
    """Complete phase with automatic git commit."""
    
    # 1. Commit phase work
    commit_message = self._generate_phase_commit_message(
        phase_name=phase_name,
        deliverables=deliverables,
        validation=validation_result
    )
    self.git_manager.commit_all(commit_message)
    
    # 2. Update master plan
    self.progress_tracker.update_master_plan(
        phase=phase_name,
        status="COMPLETE"
    )
    
    # 3. Commit master plan
    self.git_manager.commit_file(
        "cortex-brain/documents/planning/active/CORTEX-3.0-4.0/MASTER-PLAN.md",
        f"📊 Update MASTER-PLAN.md: {phase_name} progress"
    )
    
    # 4. Push
    self.git_manager.push("CORTEX-4.0")
```

**Status:** Not yet implemented (manual process for now)

---

## 🔍 Verification

### How to Verify Policy Compliance

**Check recent commits:**
```bash
git log --oneline --graph -10
```

**Expected pattern:**
```
* abc1234 📊 Update MASTER-PLAN.md: Phase 1 Week 3 progress
* def5678 ✅ Phase 1 Week 3 Complete: Foundation Prerequisites
* ghi9012 📊 Update MASTER-PLAN.md: Phase 1 Week 2 progress
* jkl3456 ✅ Phase 1 Week 2 Complete: Infrastructure Layer
```

**Check commit details:**
```bash
git show <commit-hash>
```

**Verify deliverables match commit message:**
```bash
git diff <previous-commit> <current-commit> --stat
```

---

## 🎓 Training & Onboarding

### For New Contributors

1. **Read this policy first** - Before starting any phase work
2. **Use checklist template** - At end of each phase/week
3. **Review commit history** - See examples of proper commits
4. **Ask before committing** - If unsure about format

### For Code Reviews

When reviewing phase completion PRs, verify:
- ✅ Two commits (phase work + master plan)
- ✅ Commit messages follow format
- ✅ Deliverables listed in commit message
- ✅ Master plan progress matches commits
- ✅ Both commits pushed to CORTEX-4.0

---

## 📚 Related Documents

- **MASTER-PLAN.md** - Contains complete git commit policy section
- **PROGRESS-TRACKING-STANDARD.md** - Progress tracker format specification
- **IDE-DETECTION-IMPLEMENTATION-PLAN.md** - Example of policy applied to sub-plan

---

## 📝 Change History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | December 18, 2025 | Initial policy established |

---

**Status:** ✅ MANDATORY - All phase/week completions must follow this policy starting December 18, 2025.
