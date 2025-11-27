# CORTEX Code Review Feature - Implementation Guide

**Purpose:** Comprehensive code review system for Azure DevOps Pull Requests with dependency-driven context building and tiered analysis  
**Version:** 1.0 (MVP - Conservative Approach)  
**Status:** ⏳ PLANNED  
**Author:** Asif Hussain

---

## 🎯 Overview

The Code Review feature provides intelligent PR analysis with:
- **Dependency-Driven Crawling** - Only scans files directly referenced by PR changes (5-10K tokens vs 45K+ with percentage-based)
- **Tiered Analysis** - User chooses depth: Quick (30s) / Standard (2 min) / Deep (5 min)
- **Actionable Reporting** - Priority matrix with copy-paste fix templates
- **Token Efficiency** - 83% reduction vs percentage-based crawling (45K → 8K tokens)

---

## 🚀 User Workflow

### Step 1: Initiate Code Review

**Natural Language Triggers:**
- "code review"
- "review pr"
- "pr review"
- "review pull request"
- "ado pr review"

**Response Template:** `code_review_planning` from `response-templates.yaml`

### Step 2: Interactive Intake

**CORTEX Asks:**
1. **PR Information** - ADO link, work item ID, or paste diff directly
2. **Review Depth** - Quick / Standard / Deep
3. **Focus Areas** (optional) - Security / Performance / Maintainability / Tests / Architecture / All

**Example User Input:**
```
PR: https://dev.azure.com/org/project/_git/repo/pullrequest/1234
Depth: Standard
Focus: Security + Performance
```

Or simplified:
```
Review PR 1234 with standard depth
```

### Step 3: Context Building (Dependency-Driven)

**Phase 1: Scan PR Changes**
- Extract changed files from PR diff
- Identify file types (source code, tests, configs)
- Count lines changed (additions, deletions, modifications)

**Phase 2: Crawl Dependencies**
```python
dependency_graph = {
    "changed_files": [],       # Always included
    "direct_imports": [],      # Always included
    "test_files": [],          # If exists
    "indirect_deps": []        # Only if total <50 files
}
```

**Crawl Strategy:**
- **Level 1 (Always):** Changed files + direct imports (typically 5-15 files)
- **Level 2 (Conditional):** Test files if they exist
- **Level 3 (Capped):** Indirect dependencies only if total <50 files

**Token Budget:** 5-10K tokens (vs 45K+ with percentage-based)

### Step 4: Analysis Execution

**Quick Review (30 seconds):**
- Breaking changes detector
- Critical code smells (complexity >15, duplicate code >50 lines)
- Immediate blockers

**Standard Review (2 minutes):**
- All Quick Review checks
- Best practices validator
- Edge case analyzer
- Missing error handling

**Deep Review (5 minutes):**
- All Standard Review checks
- TDD pattern matcher
- Security scanner (OWASP checklist)
- Performance profiler
- Architecture pattern analysis

### Step 5: Report Generation

**Report Structure:**

```markdown
# Code Review Report - PR #1234

## Executive Summary
[3 sentence summary of findings]

## Risk Score: 65/100 (Medium Risk)
[Explanation of score calculation]

## Critical Issues (Must Fix Before Merge)
1. **SQL Injection Vulnerability** - Line 45, UserController.cs
   - Issue: User input concatenated into SQL query
   - Risk: HIGH (Security)
   - Fix Template:
     ```csharp
     // Replace this:
     var query = $"SELECT * FROM Users WHERE id = {userId}";
     
     // With this:
     var query = "SELECT * FROM Users WHERE id = @userId";
     cmd.Parameters.AddWithValue("@userId", userId);
     ```

## Warnings (Should Fix Soon)
[Non-blocking but important issues]

## Suggestions (Nice to Have)
[Optimization opportunities]

## Next Steps
1. Fix critical issues
2. Re-run tests
3. Request re-review
```

---

## 🏗️ Technical Architecture

### Component Breakdown

**1. CodeReviewOrchestrator**
- Entry point for code review workflow
- Manages phases (intake → crawl → analyze → report)
- Handles user interaction and confirmations

**2. PRContextBuilder**
- Parses PR information (ADO link, diff, work item)
- Builds dependency graph
- Implements crawl strategy (dependency-driven)
- Token budget enforcement

**3. AnalysisTierEngine**
- Executes selected analysis tier (quick/standard/deep)
- Runs code smell detectors
- Performs security scans (OWASP)
- Checks best practices

**4. ReportGenerator**
- Creates priority matrix
- Generates fix templates
- Calculates risk scores
- Formats executive summary

### Data Flow

```
User: "review pr 1234 with standard depth"
   ↓
IntentRouter → code_review_planning template
   ↓
CodeReviewOrchestrator.initiate()
   ↓
1. Interactive Intake
   - Collect PR info, depth, focus areas
   ↓
2. PRContextBuilder.build()
   - Fetch PR diff from ADO
   - Extract changed files
   - Crawl dependencies (level 1 + level 2)
   - Build context (5-10K tokens)
   ↓
3. AnalysisTierEngine.analyze(tier="standard")
   - Breaking changes check
   - Critical smells
   - Best practices validation
   - Edge case analysis
   ↓
4. ReportGenerator.create()
   - Executive summary
   - Risk score calculation
   - Priority matrix (critical/warning/suggestion)
   - Fix templates generation
   ↓
5. Present Report to User
   - Markdown formatted
   - Copy-paste ready fixes
   - Next steps guidance
```

---

## 📊 Implementation Phases

### Phase 1: Template & Orchestrator (2 hours)
**Status:** ✅ Template Created

**Tasks:**
- [x] Create `code_review_planning` template in response-templates.yaml
- [ ] Implement `CodeReviewOrchestrator` class
- [ ] Add natural language trigger routing
- [ ] Create interactive intake dialog

**Deliverables:**
- Template triggers code review workflow
- User can provide PR info and preferences
- Orchestrator initializes correctly

### Phase 2: Context Builder (2-3 hours)

**Tasks:**
- [ ] Implement `PRContextBuilder` class
- [ ] ADO API integration (fetch PR diff)
- [ ] Dependency graph builder
- [ ] Crawl strategy implementation (3 levels)
- [ ] Token budget enforcement

**Deliverables:**
- Fetches PR from ADO
- Builds dependency graph accurately
- Stays within 5-10K token budget
- Crawl depth adapts to PR size

### Phase 3: Analysis Engine (3-4 hours)

**Tasks:**
- [ ] Implement `AnalysisTierEngine` base class
- [ ] Quick review analyzers (breaking changes, critical smells)
- [ ] Standard review analyzers (+ best practices, edge cases)
- [ ] Deep review analyzers (+ TDD, security, performance)
- [ ] Integration with existing TDD/RefactoringIntelligence

**Deliverables:**
- All three tiers operational
- Reuses existing code smell detection (11 types)
- Security scanner uses OWASP checklist
- Performance analysis uses timing data if available

### Phase 4: Report Generation (1-2 hours)

**Tasks:**
- [ ] Implement `ReportGenerator` class
- [ ] Risk score calculation algorithm
- [ ] Priority matrix formatter
- [ ] Fix template generator (copy-paste ready)
- [ ] Executive summary creator

**Deliverables:**
- Professional markdown reports
- Risk scores accurate (0-100)
- Fix templates actionable
- Reports saved to `cortex-brain/documents/reports/code-review/`

### Phase 5: Testing & Validation (2 hours)

**Tasks:**
- [ ] Unit tests for each component (80% coverage)
- [ ] Integration test with sample PR
- [ ] Performance benchmarking (confirm 30s/2min/5min)
- [ ] Token usage validation (5-10K target)

**Deliverables:**
- All tests passing
- Performance targets met
- Token budget confirmed
- Ready for production use

---

## 🎯 Success Metrics

**Accuracy:**
- 95%+ dependency detection rate (captures all direct imports)
- 90%+ issue detection rate (finds real problems, not false positives)

**Performance:**
- Quick review: <30 seconds average
- Standard review: <2 minutes average
- Deep review: <5 minutes average

**Token Efficiency:**
- 5-10K tokens per review (83% reduction vs percentage-based)
- <$0.10 per review (GitHub Copilot pricing)

**User Satisfaction:**
- Actionable fix templates (copy-paste ready)
- Risk scores intuitive (0-100 scale)
- Reports concise (3 sentence executive summary)

---

## 🔧 Configuration Options

```yaml
code_review:
  crawl_strategy: dependency_driven
  max_files: 50  # Cap for indirect dependencies
  token_budget: 10000  # Maximum tokens per review
  
  analysis_tiers:
    quick:
      timeout: 30  # seconds
      checks:
        - breaking_changes
        - critical_smells
    standard:
      timeout: 120  # seconds
      checks:
        - breaking_changes
        - critical_smells
        - best_practices
        - edge_cases
    deep:
      timeout: 300  # seconds
      checks:
        - breaking_changes
        - critical_smells
        - best_practices
        - edge_cases
        - tdd_patterns
        - security_scan
        - performance_analysis
  
  report:
    format: markdown
    save_location: cortex-brain/documents/reports/code-review/
    include_fix_templates: true
    risk_score_enabled: true
```

---

## 🛡️ Integration Points

### ADO API Integration

**Authentication:**
- Use PAT (Personal Access Token) from `cortex.config.json`
- Store in `ado.personal_access_token` field

**Endpoints:**
- GET PR diff: `https://dev.azure.com/{org}/{project}/_apis/git/repositories/{repo}/pullRequests/{prId}?api-version=7.0`
- GET PR files: `https://dev.azure.com/{org}/{project}/_apis/git/pullRequests/{prId}/iterations/{iterationId}/changes?api-version=7.0`

### TDD Workflow Integration

**Auto-Test Generation:**
- If Deep Review detects uncovered edge cases → Offer to generate tests
- Use `ViewDiscoveryAgent` if UI changes detected
- Store tests in user repo (test location isolation)

**Test Execution:**
- If PR includes test files → Run and report results
- Use `TDDWorkflowOrchestrator` for execution

### Refactoring Intelligence Integration

**Code Smell Detection:**
- Reuse existing 11 smell types from `RefactoringIntelligence`
- Leverage AST-based analysis (Python, JS, TS, C#)
- Include performance smells if timing data available

---

## 📚 Related Documentation

- **Response Format Guide:** `.github/prompts/modules/response-format.md`
- **Template Guide:** `.github/prompts/modules/template-guide.md`
- **TDD Mastery Guide:** `.github/prompts/modules/tdd-mastery-guide.md`
- **Planning System Guide:** `.github/prompts/modules/planning-system-guide.md`

---

## 🎓 Copyright & Attribution

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)  
**Repository:** https://github.com/asifhussain60/CORTEX

---

**Version:** 1.0 (MVP - Conservative Approach)  
**Last Updated:** November 26, 2025  
**Estimated Implementation Time:** 10-12 hours  
**Risk Level:** Low (proven techniques, existing code reuse)
