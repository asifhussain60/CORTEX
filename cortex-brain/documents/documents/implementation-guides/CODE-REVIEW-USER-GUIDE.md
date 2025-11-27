# Code Review Feature - User Guide

**Version:** 3.2.0  
**Author:** Asif Hussain  
**Last Updated:** 2025-11-26  

---

## 🎯 Overview

The CORTEX Code Review feature provides intelligent, automated analysis of Azure DevOps Pull Requests with dependency-driven context building and tiered analysis depths.

**Key Capabilities:**
- 🔍 **5 Specialized Analyzers:** Breaking changes, code smells, best practices, security, performance
- 🎯 **3 Depth Tiers:** Quick (30s), Standard (2min), Deep (5min)
- 📊 **Token Budget:** 5-10K tokens per review (83% reduction from naive approaches)
- ⚡ **Dependency-Driven:** Crawls import graph for relevant context
- 🛡️ **Two-Tier Response:** Findings report first, then optional auto-fix with Planning System 2.0

---

## 🚀 Getting Started

### Basic Usage

Simply mention "review" or "code review" in natural language:

```
Review this PR: https://dev.azure.com/myorg/MyProject/_git/MyApp/pullrequest/12345
```

CORTEX will:
1. Extract PR metadata from ADO
2. Build dependency graph for changed files
3. Execute analyzers based on depth tier
4. Generate comprehensive report with fix templates
5. Offer Planning System 2.0 integration for auto-fix

### Trigger Examples

**Simple review (default: Standard depth, all focus areas):**
```
review PR 12345
```

**With depth specification:**
```
quick review of PR 12345
deep review of https://dev.azure.com/.../pullrequest/12345
```

**With focus areas:**
```
review PR 12345 focusing on security
review PR 12345 for performance and security issues
```

**Combined:**
```
deep review of PR 12345 focusing on security and best practices
```

---

## 📊 Depth Tier Comparison

| Tier | Duration | Analyzers | Use Case |
|------|----------|-----------|----------|
| **Quick** | ~30s | Breaking Changes, Code Smells | Pre-commit check, rapid feedback |
| **Standard** | ~2min | Quick + Best Practices, Security | Regular PR reviews, balanced approach |
| **Deep** | ~5min | Standard + Performance | Critical PRs, production releases |

### Depth Tier Details

#### 🏃 Quick (30 seconds)
- **Analyzers:** Breaking Changes Detector, Code Smell Analyzer
- **Best for:** Quick feedback loops, multiple iterations
- **Coverage:** Critical issues and obvious smells
- **Example:** "quick review of PR 12345"

#### ⚖️ Standard (2 minutes) - **RECOMMENDED**
- **Analyzers:** Quick + Best Practices Validator, Security Scanner
- **Best for:** Regular development workflow
- **Coverage:** Most common issues across all categories
- **Example:** "review PR 12345" (default)

#### 🔬 Deep (5 minutes)
- **Analyzers:** Standard + Performance Analyzer
- **Best for:** Production releases, architectural changes
- **Coverage:** Comprehensive analysis including performance
- **Example:** "deep review of PR 12345"

---

## 🎯 Focus Areas

Narrow analysis to specific concern areas:

| Focus Area | Description | Example Issues |
|------------|-------------|----------------|
| **Security** | Vulnerabilities, hardcoded secrets | SQL injection, XSS, insecure functions |
| **Performance** | Efficiency issues | Nested loops, N+1 queries |
| **Tests** | Test coverage, test quality | Missing tests, brittle tests |
| **Maintainability** | Code readability, structure | Long methods, complex conditions |
| **Architecture** | Design patterns, dependencies | Circular dependencies, tight coupling |
| **All** (default) | Comprehensive analysis | Everything |

### Focus Area Examples

**Security-focused:**
```
review PR 12345 focusing on security
```

**Multiple areas:**
```
review PR 12345 for security and performance
```

---

## 📖 Reading Reports

Reports are saved to: `cortex-brain/documents/reports/code-review/PR-{id}-{timestamp}.md`

### Report Structure

#### 1. Executive Summary
3-sentence overview with risk assessment:
- What was analyzed
- What was found (count)
- Overall recommendation

#### 2. Risk Assessment
Visual risk score (0-100) with emoji indicator:
- 🟢 **0-39:** Low Risk (safe to merge)
- 🟡 **40-69:** Medium Risk (address warnings)
- 🔴 **70-100:** High Risk (must fix critical issues)

#### 3. Priority Matrix
Quick overview table:

| Priority | Count | Action Required |
|----------|-------|-----------------|
| 🔴 **Critical** | X | Must fix before merge |
| 🟡 **Warning** | Y | Should fix soon |
| 🔵 **Suggestion** | Z | Nice to have |

#### 4. Critical Issues
Detailed findings with:
- **File path** and line number
- **Description** of issue
- **Fix suggestion**
- **Copy-paste fix template** (collapsible)
- **Confidence score** (60-95%)

**Example:**
```markdown
### 1. SQL Injection Vulnerability

**File:** `src/auth.py` (Line 42)
**Description:** User input directly concatenated into SQL query
**Fix:** Use parameterized queries

<details>
<summary>💡 Click for copy-paste fix template</summary>

```python
# Before (problematic):
query = "SELECT * FROM users WHERE id = " + user_id
cursor.execute(query)

# After (fixed):
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))
```
</details>

**Confidence:** 95%
```

#### 5. Warnings & Suggestions
Collapsible sections (click to expand) for non-blocking issues.

#### 6. Developer Disclaimer
⚠️ **Critical reminder:**
- False positives expected (~15-20%)
- Always verify findings
- Test fixes in isolation
- Use engineering judgment

#### 7. Next Steps
Context-aware recommendations:
- **Critical issues present:** Fix → Test → Re-review
- **Only warnings:** Address if time permits
- **No issues:** Ready to merge

---

## 🔄 Two-Tier Workflow

CORTEX uses a **two-tier response pattern** to balance automation with developer control:

### Tier 1: Findings Report (Always Provided)
1. Natural language trigger: "review PR 12345"
2. CORTEX analyzes and generates report
3. Report lists all findings with confidence scores
4. Developer reviews findings (verifies accuracy)

### Tier 2: Auto-Fix (Optional, User Choice)
After reviewing findings, developer chooses:

**Option A:** Fix manually (full control)
```
I'll handle the SQL injection fix myself
```

**Option B:** Use Planning System 2.0 for orchestrated fix
```
Create a plan to fix the SQL injection issue
```

**Option C:** Get more context before deciding
```
Show me examples of similar fixes in the codebase
```

### Why Two-Tier?

**Challenge:** Analysis must run BEFORE response template executes (timing conflict)

**Solution:** 
1. First, provide findings (async, takes 30s-5min)
2. Then, offer fix options (sync, based on findings)

**Benefits:**
- Developer validates findings before committing to fixes
- False positives caught early (before code changes)
- Flexibility: Manual fix vs. automated orchestration
- Aligns with TDD: Verify test failures before fixing

---

## 🔧 Common Scenarios

### Scenario 1: Pre-merge Safety Check
```
quick review of PR 12345
```
**Result:** 30-second scan, critical issues flagged, merge decision made

### Scenario 2: Security-Focused Review
```
review PR 12345 focusing on security
```
**Result:** Deep security scan, hardcoded secrets detected, SQL injection found

### Scenario 3: Production Release
```
deep review of PR 12345
```
**Result:** 5-minute comprehensive analysis, performance issues identified, all categories covered

### Scenario 4: Iterative Development
```
quick review of PR 12345 focusing on tests
```
**Result:** Fast feedback on test coverage, missing test files identified

### Scenario 5: Code Quality Improvement
```
review PR 12345 for maintainability
```
**Result:** Long methods, complex conditions, magic numbers flagged

---

## 🎓 Best Practices

### 1. Start with Standard Depth
Default depth (Standard) provides best balance:
- Covers 80% of common issues
- Completes in ~2 minutes
- Suitable for daily workflow

### 2. Use Focus Areas Strategically
When you know the risk area:
- Authentication PR → Focus on **security**
- Database queries → Focus on **performance**
- New feature → Use **all** (comprehensive)

### 3. Verify High-Confidence Findings First
Prioritize issues with 85%+ confidence:
- SQL injection: 95% confidence → Likely accurate
- Complex condition: 65% confidence → May be false positive

### 4. Use Fix Templates as Starting Points
Copy-paste templates are **guidelines**, not gospel:
- Adapt to your codebase style
- Consider context (not visible to analyzer)
- Test thoroughly before committing

### 5. Treat Warnings as Learning Opportunities
Even false positives have value:
- Why did analyzer flag this?
- Could naming be clearer?
- Is there a pattern to improve?

### 6. Re-review After Fixes
Quick second pass validates resolution:
```
quick review of PR 12345
```
**Expected:** Risk score drops, critical issues resolved

---

## 🚨 Troubleshooting

### Issue: "Token budget exceeded"
**Cause:** PR changes 100+ files or very large files
**Solution:** 
- Use focus areas to narrow scope
- Split PR into smaller chunks
- Contact team if legitimate large refactor

### Issue: "No issues found" (but code has obvious problems)
**Cause:** Analyzer limitations, language not supported
**Solution:**
- Check file extensions (only Python, JS, TS, C#, Java, Go supported)
- Report issue with feedback system
- Use manual review as fallback

### Issue: "Confidence score seems wrong"
**Cause:** Heuristic-based detection, context limitations
**Solution:**
- Always verify findings manually
- Remember: AI guidance, not final word
- Report persistent issues

### Issue: "Report missing expected sections"
**Cause:** No issues found in that category
**Solution:**
- This is expected behavior (collapsible sections only appear if issues exist)
- Low risk score (0-39) means safe to merge

---

## 📞 Support & Feedback

### Report Issues
Use the feedback system:
```
feedback
```
Structured template with auto-context capture.

### Request Features
Describe desired capability:
```
feedback: Would like Java language support for code review
```

### Get Help
```
help with code review
```
Shows this guide and common commands.

---

## 📚 Related Documentation

- **Planning System 2.0:** `.github/prompts/modules/planning-system-guide.md`
- **TDD Mastery:** `.github/prompts/modules/tdd-mastery-guide.md`
- **Response Format:** `.github/prompts/modules/response-format.md`
- **Brain Protection:** `cortex-brain/brain-protection-rules.yaml`

---

**Last Updated:** 2025-11-26  
**Feature Version:** 3.2.0  
**Completion:** Phase 4+5 (Enhanced Reports + E2E Testing)
