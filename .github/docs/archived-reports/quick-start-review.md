# CORTEX Review System - Quick Start Guide

## 📖 Overview

You now have a comprehensive **5-agent review system** that can critically analyze CORTEX for gaps, weaknesses, brittleness, hallucinations, and other risks. The system is evidence-based and designed to catch issues before they surface in production.

---

## 🚀 How to Use

### Running a Full Review

Copy this prompt to any Claude conversation:

```
/review full

(In a Claude conversation, use this to trigger the full 5-agent review system
as defined in .github/prompts/cortex-review.prompt.md)
```

This will execute all 5 review agents and generate findings in:
- `.github/roadmap/issues/review-YYYY-MM-DD.yaml` (structured data)
- `.github/roadmap/issues/review-YYYY-MM-DD.json` (machine-readable)
- `.github/roadmap/issues/REVIEW-YYYY-MM-DD.md` (human-readable)

### Running Targeted Reviews

Review only specific concern areas:

```
/review brittleness         # Find structural weaknesses
/review hallucination       # Find AI hallucination risks
/review governance          # Verify CORE rule compliance
/review assumptions         # Find hidden assumptions
/review debt                # Identify technical debt
```

### Finding Quick Wins

```
/review quick-wins          # List all findings fixable in < 4 hours
```

### Deep Audit Analysis

```
/review audit-health        # Analyze governance.db audit trail
```

---

## 📊 Initial Review Results (2026-01-16)

### Overall Score: 78/100

| Category | Score | Status |
|----------|-------|--------|
| Brittleness | 72/100 | ⚠️ Needs attention |
| Hallucination | 85/100 | ✅ Good |
| Governance | 88/100 | ✅ Good |
| Assumptions | 70/100 | ⚠️ Needs attention |
| Debt | 75/100 | ⚠️ Moderate |

### Critical Findings (Must Fix)

| Finding | Issue | Effort | Impact |
|---------|-------|--------|--------|
| FINDING-001 | 3 bare `except:` clauses (CORE-013) | 2h | Silent error swallowing |
| FINDING-002 | 18 hardcoded paths in tests (CORE-005) | 4h | CI/CD fails, non-portable |

### Quick Wins (< 4h each)

1. Fix CORE-013 violations (2h)
2. Fix CORE-005 violations (4h)
3. Resolve failed AC audit entries (2h)
4. Clean TODO/FIXME comments (2h)
5. Platform compatibility audit (4h)
6. Generate test coverage report (8h)

---

## 🏗️ System Architecture

### The 5 Review Agents

1. **Brittleness Agent** (`cortex-review-brittleness.md`)
   - Finds single points of failure
   - Detects error handling gaps
   - Identifies resource leaks
   - Analyzes concurrency issues
   
2. **Hallucination Agent** (`cortex-review-hallucination.md`)
   - Finds prompt injection vectors
   - Detects ungrounded AI responses
   - Identifies code generation risks
   - Verifies human-in-the-loop gates

3. **Governance Agent** (`cortex-review-governance.md`)
   - Validates CORE rule compliance
   - Verifies audit trail integrity
   - Checks type hints and docstrings
   - Ensures naming conventions

4. **Assumptions Agent** (`cortex-review-assumptions.md`)
   - Finds platform-specific code
   - Detects Python version assumptions
   - Identifies environment dependencies
   - Locates hardcoded assumptions

5. **Technical Debt Agent** (`cortex-review-debt.md`)
   - Finds duplicated code
   - Identifies missing abstractions
   - Spots deprecated patterns
   - Analyzes test coverage gaps

### Master Orchestration

**`.github/prompts/cortex-review.prompt.md`** coordinates all 5 agents and:
- Defines review protocol (Preparation → Analysis → Audit → Patterns)
- Manages output formatting (YAML, JSON, Markdown)
- Integrates historical patterns from CORTEX 4.0/5.0/5.5
- Ensures findings are evidence-based
- Prioritizes recommendations

---

## 📋 Review Output Files

After running a review, expect these artifacts:

### Structured Data (YAML)
```yaml
# .github/roadmap/issues/review-YYYY-MM-DD.yaml
findings:
  - id: "FINDING-001"
    severity: "CRITICAL"
    title: "[description]"
    evidence: {...}
    remediation: {...}
```

### Machine-Readable (JSON)
```json
{
  "review_id": "REVIEW-2026-01-16",
  "score": {"overall": 78, "brittleness": 72, ...},
  "findings": {...}
}
```

### Human-Readable (Markdown)
```markdown
# CORTEX Architecture Review

## Executive Summary
...

## Critical Findings
...

## Quick Wins
...
```

---

## 🔍 How to Interpret Findings

### Finding Structure

Each finding contains:

```yaml
finding:
  id: "FINDING-XXX"              # Unique identifier
  severity: "CRITICAL|HIGH|MEDIUM|LOW"
  category: "brittleness|hallucination|governance|assumption|debt"
  
  title: "[Clear description]"   # What was found
  
  evidence:
    detection_method: "grep_search|audit_query|code_analysis"
    command: "[Exact command used]"
    result: "[What it found]"
  
  impact:
    production_risk: "What could go wrong"
    debugging_difficulty: "How hard to fix"
  
  remediation:
    effort: "2h|4h|1d|1w"         # Time to fix
    approach: "[Step-by-step fix]"
    ac_id_suggested: "AC-FIX-XXX-XX"  # If creating new AC
```

### Severity Levels

| Level | Definition | Action |
|-------|-----------|--------|
| CRITICAL | System-breaking | Block next phase |
| HIGH | Major impact | Fix within 48h |
| MEDIUM | Workarounds exist | Fix within 1 week |
| LOW | Edge cases only | Track opportunistically |

### Evidence-Based Claims

Every finding includes:
- **Detection command** (so you can verify independently)
- **Affected files** (specific locations)
- **Root cause** (why this exists)
- **Failure scenario** (when/how it breaks)
- **Remediation approach** (step-by-step fix)

---

## 🛠️ Integration with Cortex Builder

After review findings are published:

1. **Builder reads findings** from `.github/roadmap/issues/review-YYYY-MM-DD.yaml`
2. **Builder prioritizes CRITICAL findings** before new phase work
3. **Builder creates fix ACs** for HIGH severity findings
4. **Builder updates phase_tracker** with blocking issues
5. **Builder documents remediation** in audit trail

### Example: Finding → AC

```yaml
# From review findings
finding_id: "FINDING-001"
severity: "CRITICAL"
title: "Bare except clauses"

# Becomes
ac_id: "AC-FIX-001-01"
phase: "PHASE-REMEDIATION-01"
title: "Fix CORE-013 violations: Replace bare except clauses"
```

---

## 📈 Historical Context

The review system learned from brittleness issues in CORTEX 4.0/5.0/5.5:

### Issues That Were Resolved
- ✅ State management (now uses governance.db with transactions)
- ✅ Orchestrator control flow (now has OrchestratorBase pattern)
- ✅ Failure recovery (now has CORE-026 git checkpoints)
- ✅ Base class inconsistency (now has shared patterns)
- ✅ Configuration parsing (now uses pure data templates)

### Issues Still Partially Resolved
- ⚠️ Intent classification (LLM classifier exists, adoption partial)
- ⚠️ Testing gaps (3262 tests exist, coverage unknown)

**Overall historical debt resolution: 71%**

---

## 🔄 Recommended Review Cadence

- **Before each phase lock**: Quick governance compliance review (`/review governance`)
- **Weekly**: Brittleness scan (`/review brittleness`)
- **Every 2 weeks**: Full architecture review (`/review full`)
- **Monthly**: Historical pattern comparison to track improvement

---

## 📝 Example: How to Read Initial Review

### CRITICAL Finding Example

```yaml
FINDING-002: Hardcoded Paths in Tests [CORE-005 violation]

Location: tests/unit/tier3/test_auto_indexing.py (17 instances)

Evidence:
  Command: grep -rn '/Users/' --include='*.py' tests/
  Result: 18 hardcoded absolute paths found

Impact:
  • Tests will fail on any other developer's machine
  • CI/CD systems will fail
  • Cross-platform (Windows/Linux) incompatible

Remediation:
  Step 1: Replace /Users/asifhussain/PROJECTS/CORTEX/... 
          with get_project_root() / "..."
  Step 2: Use pytest fixtures for common paths
  Step 3: Add CI check to prevent recurrence
  Effort: 4 hours
```

---

## 🚀 Next Actions

### Immediate (This Week)
1. Fix FINDING-001: Replace bare except clauses (2h)
2. Fix FINDING-002: Fix hardcoded test paths (4h)
3. Resolve failed AC audit entries (2h)

### Short-term (2 Weeks)
1. Platform compatibility audit (4h)
2. Clean TODO/FIXME comments (2h)
3. Generate test coverage report (8h)

### Long-term (Next Quarter)
1. Improve test coverage to 80%
2. Implement database migration framework

---

## 💡 Tips for Effective Reviews

### Best Practices

1. **Run before major changes**: Execute before implementing new phases
2. **Track improvements**: Compare scores across reviews to measure progress
3. **Focus on quick wins**: Fix < 4h items first for momentum
4. **Verify fixes independently**: Use detection commands to validate fixes
5. **Update assumptions**: As environment changes, re-run assumption checks

### When to Use Each Agent

| Scenario | Use Agent |
|----------|-----------|
| "Is the code robust?" | Brittleness |
| "Can the AI go wrong?" | Hallucination |
| "Are we following rules?" | Governance |
| "Will this break elsewhere?" | Assumptions |
| "Is code maintainable?" | Debt |

### Common False Positives to Ignore

- Bare except in code that intentionally swallows all errors (intentional, not a bug)
- TODO comments in test fixtures (expected)
- Hardcoded paths in test factories (acceptable if clearly marked)

---

## 📚 File Reference

| File | Purpose |
|------|---------|
| `.github/prompts/cortex-review.prompt.md` | Master orchestration (copy to Claude) |
| `.github/agents/cortex-review-brittleness.md` | Brittleness detection rules |
| `.github/agents/cortex-review-hallucination.md` | AI safety checks |
| `.github/agents/cortex-review-governance.md` | CORE rule validation |
| `.github/agents/cortex-review-assumptions.md` | Assumption analysis |
| `.github/agents/cortex-review-debt.md` | Technical debt catalog |
| `.github/roadmap/issues/review-YYYY-MM-DD.yaml` | Latest review findings |
| `.github/roadmap/issues/review-YYYY-MM-DD.json` | Machine-readable results |
| `.github/roadmap/issues/REVIEW-YYYY-MM-DD.md` | Executive summary |

---

## ❓ FAQ

**Q: How often should I run reviews?**
A: Full reviews weekly; targeted reviews (brittleness, governance) daily during active development.

**Q: What if I disagree with a finding?**
A: Check the evidence (detection command). If the command is wrong, the finding is wrong. File a PR to improve agent accuracy.

**Q: Can findings be false positives?**
A: Yes, occasionally. Always verify by running the detection command yourself.

**Q: How do I add new review rules?**
A: Edit the appropriate agent file (cortex-review-*.md) and add new detection patterns.

**Q: Who should review the findings?**
A: Builders/architects should review, but the system provides evidence so anyone can understand findings.

---

## 📞 Support

For questions about the review system, check:
1. The agent file for the category (cortex-review-*.md)
2. The master prompt (cortex-review.prompt.md)
3. Historical findings (review-2026-01-16.* files)

---

*CORTEX Review System v1.0*
*Copyright © 2025-2026 Asif Hussain. All rights reserved.*
