# Anti-Patterns Catalog

**Purpose:** Document mistakes to avoid based on real production incidents  
**Owner:** CORTEX Architect  
**Status:** Active ✅

---

## Overview

This catalog documents anti-patterns discovered through actual production issues in CORTEX. Each anti-pattern includes the mistake, why it's problematic, real-world impact, and the correct approach.

**Philosophy:** Learn from mistakes without repeating them.

## Current Anti-Patterns

| Anti-Pattern | Category | Severity | Source | Correct Pattern |
|--------------|----------|----------|--------|-----------------|
| [Hidden Element Rendering](frontend-anti-patterns.md#1-hidden-element-rendering) | Frontend | 🔴 HIGH | Chat01 | [DeferredRenderer](../patterns/deferred-renderer-pattern.md) |
| [Silent DOM API Failures](frontend-anti-patterns.md#2-silent-dom-api-failures) | Frontend | 🔴 HIGH | Chat01 | Explicit null checks |
| [Ad-Hoc Testing](frontend-anti-patterns.md#3-ad-hoc-testing) | Testing | 🟡 MEDIUM | Chat01 | Standard test framework |
| [Manual Test Execution](frontend-anti-patterns.md#4-manual-test-execution) | Testing | 🟡 MEDIUM | Chat01 | CI/CD automation |
| [Premature Success Declaration](#premature-success-declaration) | Governance | 🔴 HIGH | Chat01 | Autonomous fixing + completion gate |

---

## Anti-Pattern Categories

### Frontend Anti-Patterns
- Hidden Element Rendering
- Silent DOM API Failures

### Testing Anti-Patterns
- Ad-Hoc Testing
- Manual Test Execution

### Governance Anti-Patterns
- Premature Success Declaration

### Backend Anti-Patterns
*(To be added)*

### Architecture Anti-Patterns
*(To be added)*

### Security Anti-Patterns
*(To be added)*

---

## How to Use This Catalog

### For Developers

**Before implementing code:**

1. Search catalog for similar patterns
2. Check if your approach matches an anti-pattern
3. Use "Correct Approach" section as guidance
4. Run detection strategy if available

**Example Workflow:**

```bash
# Search by keyword
grep -r "getElementById" docs/anti-patterns/
grep -r "testing" docs/anti-patterns/

# Check severity
grep -r "🔴 HIGH" docs/anti-patterns/
```

### For Code Reviewers

**During code review:**

1. Check for known anti-patterns
2. Reference this catalog in review comments
3. Link to correct pattern documentation
4. Suggest detection tooling (ESLint, TypeScript)

### For Architects

**When setting standards:**

1. Review anti-patterns for your domain
2. Add detection rules to CI/CD
3. Create team training materials
4. Update style guides

---

## Anti-Pattern Documentation Standard

Each anti-pattern entry includes:

### 1. Anti-Pattern Description
- Clear name
- Code example showing the mistake
- Why it seems reasonable (temptation)

### 2. Why It's Bad
- Specific problems it causes
- Impact table (severity, symptoms)
- Real-world consequences

### 3. Real-World Impact
- Actual production incident
- Metrics (downtime, errors, user impact)
- Detection challenges

### 4. Correct Approach
- Proper implementation
- Code example showing the fix
- Benefits table

### 5. Detection Strategy
- Static analysis rules
- Testing approaches
- Code review checklist

---

## Severity Levels

| Severity | Criteria | Example |
|----------|----------|---------|
| 🔴 **HIGH** | Production breaks, data loss, security issue | Hidden Element Rendering |
| 🟡 **MEDIUM** | Degraded UX, technical debt, maintenance burden | Ad-Hoc Testing |
| 🟢 **LOW** | Minor inefficiency, cosmetic issue | *(future)* |

---

## Anti-Pattern Lifecycle

### 1. Discovery (Source: Incident)

Anti-pattern discovered through production issue:
- Problem occurs in production
- Root cause identified in lessons-learned/
- Marked as anti-pattern

### 2. Documentation

Full anti-pattern entry created:
- Copy template
- Fill in all sections
- Add to appropriate category file
- Update this README

### 3. Detection Automation

Tooling added to catch anti-pattern:
- ESLint rule created
- TypeScript strict check
- CI/CD gate added
- Code review checklist updated

### 4. Training

Team education materials created:
- Internal training session
- Wiki/docs updated
- Onboarding materials
- Lunch & learn presentation

### 5. Monitoring

Track occurrences over time:
- Count instances in codebase
- Monitor PR rejections
- Measure reduction rate
- Celebrate zero occurrences

---

## Detection & Prevention Matrix

| Anti-Pattern | Detection Method | Prevention Strategy | Tooling |
|--------------|------------------|---------------------|---------|
| **Hidden Element Rendering** | ESLint rules | DeferredRenderer pattern | Custom ESLint plugin |
| **Silent DOM Failures** | TypeScript strict null checks | Explicit null guards | TypeScript, JSDoc |
| **Ad-Hoc Testing** | Code review | Standard test framework | Vitest, Jest |
| **Manual Testing** | No CI/CD | GitHub Actions workflow | GitHub Actions |

---

## Anti-Pattern Template

```markdown
## {Number}. {Anti-Pattern Name}

**Source:** {Incident ID} ({Date})

### ❌ Anti-Pattern

```{language}
// BAD: {What's wrong}
```

### Why It's Bad

| Issue | Impact |
|-------|--------|
| {Issue 1} | {Impact description} |
| {Issue 2} | {Impact description} |

### Real-World Impact

**{Incident Name}:**
- {Impact metric 1}
- {Impact metric 2}
- {Detection challenge}

### ✅ Correct Approach

```{language}
// GOOD: {Proper implementation}
```

**Benefits:**
- ✅ {Benefit 1}
- ✅ {Benefit 2}

### Detection Strategy

**Static Analysis:**
```json
// ESLint/TypeScript rule
```

**Testing:**
```{language}
// Test to catch anti-pattern
```

---
```

---

## Quick Reference Checklist

**Before committing code, verify:**

### Frontend Code
- [ ] All `getElementById()` calls have null checks
- [ ] Hidden element scenarios tested
- [ ] No assumptions about element visibility
- [ ] TypeScript strict mode enabled (if applicable)

### Testing Code
- [ ] Tests use standard framework (Vitest/Jest/Playwright)
- [ ] Tests run in CI/CD pipeline
- [ ] Coverage meets threshold (>80%)
- [ ] No manual-only tests

### Backend Code
*(To be added)*

### Security Code
*(To be added)*

---

## Metrics

### Current Catalog Stats

| Metric | Value |
|--------|-------|
| **Total Anti-Patterns** | 4 |
| **🔴 HIGH Severity** | 2 (50%) |
| **🟡 MEDIUM Severity** | 2 (50%) |
| **🟢 LOW Severity** | 0 (0%) |
| **Categories Covered** | 2 (Frontend, Testing) |
| **Detection Rules Created** | 4 |
| **Correct Patterns Linked** | 1 |

### Reduction Targets

- **Q1 2026:** Zero HIGH severity anti-patterns in new code
- **Q2 2026:** 50% reduction in MEDIUM severity occurrences
- **Q3 2026:** Full automation of detection

---

## Contributing

### When to Document an Anti-Pattern

✅ **Document when:**
- Pattern caused production issue
- Mistake is easy to make (looks reasonable)
- Detection can be automated
- Correct approach is known

❌ **Don't document:**
- Obvious mistakes (syntax errors)
- One-off bizarre issues
- Undocumented edge cases
- Theoretical problems (no real occurrence)

### Anti-Pattern Submission Checklist

- [ ] Anti-pattern caused real production issue
- [ ] Documented in lessons-learned/ first
- [ ] Severity level assigned (HIGH/MEDIUM/LOW)
- [ ] Code example shows the mistake
- [ ] "Why It's Bad" section explains impact
- [ ] Real-world incident cited with metrics
- [ ] Correct approach provided with code
- [ ] Detection strategy documented
- [ ] Prevention tooling suggested
- [ ] README updated with entry

---

## Integration with CORTEX

### Prompt Enhancements

Anti-patterns feed into:
- **Challenge Template:** Warn if approach matches anti-pattern
- **Code Review Agent:** Auto-detect in PRs
- **TDD Enforcement:** Test for anti-pattern avoidance

### MCP Tools (Future)

Planned MCP tools:
- `cortex_check_anti_patterns` - Scan code for known mistakes
- `cortex_anti_pattern_stats` - Track occurrence metrics
- `cortex_prevention_rules` - Generate ESLint/TSConfig rules

---

## Related Documentation

- [Lessons Learned](../meta/lessons-learned/README.md) - Source of anti-patterns
- [Patterns Library](../patterns/README.md) - Correct approaches
- [Enhancement History](../meta/enhancement-history.yaml) - Tracking improvements

---

## Training Materials

### Internal Training Sessions

1. **Frontend Anti-Patterns 101** (1 hour)
   - Hidden Element Rendering deep-dive
   - Silent DOM Failures case study
   - Hands-on exercises

2. **Testing Anti-Patterns Workshop** (2 hours)
   - Ad-Hoc Testing refactoring
   - CI/CD integration tutorial
   - Test framework migration

3. **Governance Anti-Patterns Workshop** (1 hour)
   - Premature Success Declaration prevention
   - Autonomous fixing workflows
   - Completion gate enforcement

### Onboarding Materials

- [ ] Add anti-patterns section to onboarding docs
- [ ] Create quiz for new developers
- [ ] Include in code review guidelines
- [ ] Reference in style guide

---

## Governance Anti-Patterns

### Premature Success Declaration

**Anti-Pattern ID:** ANTI-GOV-001  
**Created:** 2026-02-04  
**Source:** chat01.md DIGEST analysis  
**Severity:** 🔴 HIGH

#### The Mistake

Reporting "Production-Ready" or "Success" status when:
- P0/P1/P2 issues still exist
- Manual action items await user intervention
- Fixes proposed but not executed
- Tests not yet written/passing
- Code not yet deployed

**Example (Bad):**
```markdown
## ✅ CORTEX Audit Complete

**Status:** Production-Ready with Minor P3 Cleanup ✅

### 🎯 P0 Actions Required
| # | Issue | Action |
|---|-------|--------|
| 1 | Security: Hardcoded secret | Remove from config |
| 2 | Broken code: Import error | Fix import path |

**For User:**
1. Review P0 actions above
2. Implement fixes manually
3. Re-run audit to verify
```

**Why This is Wrong:**
- User sees "Production-Ready ✅" header
- 2 P0 issues still exist (security + broken code)
- Autonomous fixing not executed
- Success declared before work complete

#### Real-World Impact

**Incident:** chat01.md (2026-02-04)

**Timeline:**
1. AUDIT mode completed analysis
2. Found P0 security issues + P2 code quality gaps
3. Reported "Production-Ready with Minor P3 Cleanup"
4. User believed system was ready for production
5. P0 issues discovered during deployment

**Consequences:**
- ❌ False confidence in code quality
- ❌ Security vulnerabilities unaddressed
- ❌ Wasted deployment effort
- ❌ Trust erosion in CORTEX governance

#### Root Causes

1. **Ambiguous Completion Criteria**
   - Prompt allowed "report issues OR fix them"
   - No explicit definition of "production-ready"

2. **Weak Autonomous Execution**
   - Fixing was implied, not enforced
   - AUDIT mode could emit action lists without execution

3. **Lenient Severity Interpretation**
   - P0 issues treated as "minor" if count was low
   - "Minor cleanup" language minimized severity

#### Correct Approach

**Autonomous Fixing + Strict Completion Gate:**

```markdown
## 🔍 CORTEX Audit

**Status:** Analysis Complete, Fixing in Progress...

### 📋 Issues Detected
| Priority | Count | Status |
|----------|-------|--------|
| P0 | 2 | 🔄 Auto-fixing... |
| P1 | 1 | 🔄 Auto-fixing... |
| P2 | 5 | 🔄 Auto-fixing... |
| P3 | 3 | 🔄 Auto-fixing... |

---

[Autonomous fixing cycle: detect → fix → verify → repeat]

---

## ✅ CORTEX 100% Production-Ready

**All Issues Resolved:**
- P0: 0 remaining (2 fixed)
- P1: 0 remaining (1 fixed)
- P2: 0 remaining (5 fixed)
- P3: 0 remaining (3 auto-fixed)

**Verification:**
- ✅ Security scan passed
- ✅ All tests passing
- ✅ Code quality gates passed
- ✅ Duplicates removed
```

#### Implementation (ENH-016)

**Files Modified:**
- `.github/prompts/cortex-architect.prompt.md` (completion criteria)
- `.github/agents/core/cortex-auditor.md` (autonomous fixing workflow)
- `.github/agents/core/CORTEX.md` (governance checklist)
- `.github/copilot-instructions.md` (before every operation)

**Key Changes:**
1. **Strict Completion Criteria:**
   - Success = 0 P0, 0 P1, 0 P2 remaining
   - P3 must be auto-fixed (no manual actions)

2. **Autonomous Fixing Workflow:**
   ```
   Detect Issues → Fix → Verify → (Repeat if issues found) → Report Success
   ```

3. **Mandatory Tools:**
   - P2 checks REQUIRE `cortex_lens_analyze` execution
   - No "Not analyzed" allowed

4. **Clear Language:**
   - "100% Production-Ready" = zero issues
   - No ambiguous terms like "Minor cleanup"

#### Detection & Prevention

**How to Detect in Code Reviews:**
```bash
# Flag premature success declarations
grep -r "Production-Ready" docs/*.md | grep -v "100%" | grep -v "0 P0"
```

**Pre-Commit Hook:**
```python
def validate_audit_completion(report: str) -> bool:
    """Ensure success only declared when issues = 0"""
    if "Production-Ready" in report or "Success" in report:
        if "P0: 0" not in report or "P1: 0" not in report or "P2: 0" not in report:
            raise ValueError("Cannot declare success with pending P0/P1/P2 issues")
    return True
```

#### Success Criteria

✅ **Report success ONLY when:**
- P0 issues = 0
- P1 issues = 0
- P2 issues = 0
- P3 issues auto-fixed (or documented as intentional)
- All tests passing
- Code deployed (if applicable)

❌ **Never report success when:**
- Manual action items remain
- "For User" sections exist
- Fixes proposed but not executed
- Test failures present
- Severity minimized ("minor", "small", "trivial")

#### Related Patterns

- [Autonomous Fixing Workflow](../patterns/autonomous-fixing.md) (TODO)
- [Completion Gate Pattern](../patterns/completion-gate.md) (TODO)
- [Evidence-Based Governance](../patterns/evidence-based-governance.md) (TODO)

---

**Last Updated:** 2026-02-04  
**Maintainer:** CORTEX Architect  
**Next Review:** 2026-03-04

