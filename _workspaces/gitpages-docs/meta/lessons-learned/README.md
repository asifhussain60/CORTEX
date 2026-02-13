# Learning Artifacts

**Purpose:** Capture organizational knowledge from production incidents and successful implementations  
**Owner:** CORTEX Architect  
**Updated:** Automatically after each DESIGN/EXEC completion

---

## Overview

This directory contains structured learning artifacts extracted from real implementation work. Every lesson learned document represents actual production experience, following the Implementation Truth principle (CORE-030).

## Directory Structure

```
docs/
├── meta/
│   └── lessons-learned/        # ← You are here
│       ├── README.md
│       ├── CHAT01-2026-02-03.yaml
│       └── {INCIDENT_ID}.yaml
├── patterns/                    # Reusable solution patterns
│   ├── README.md
│   ├── deferred-renderer-pattern.md
│   └── {pattern-name}.md
└── anti-patterns/              # Mistakes to avoid
    ├── README.md
    ├── frontend-anti-patterns.md
    └── {anti-pattern-name}.md
```

## File Naming Convention

```
{CHAT_ID}-{YYYY-MM-DD}.yaml

Examples:
- CHAT01-2026-02-03.yaml (Chat01 dashboard incident)
- CHAT15-2026-02-10.yaml (Future incident)
- EXEC042-2026-03-15.yaml (EXEC mode implementation)
```

## Schema Structure

Each lessons learned file follows this schema:

```yaml
incident_id: "CHAT01-2026-02-03"
severity: P0|P1|P2|P3
category: "Domain category"
domain: "Specific area"

problem:
  summary: "Brief description"
  root_cause: "Technical root cause"
  affected_components: ["list"]
  impact: "User-facing impact"
  detection: "How it was discovered"

solution:
  pattern_name: "Name if reusable"
  approach: "Strategy used"
  key_insight: "Main learning"
  implementation_file: "path/to/file"
  test_coverage: "X% (Y tests)"
  performance_improvement: "X% (before → after)"

technical_details:
  root_cause_analysis: ["detailed analysis"]
  solution_architecture:
    pattern: "Pattern name"
    components: ["list of components"]
  implementation_strategy: ["RED → GREEN → REFACTOR steps"]

lessons:
  critical: ["Key lessons that prevent similar issues"]
  testing: ["Test-related learnings"]
  documentation: ["Doc-related learnings"]
  process: ["Process improvements"]

anti_patterns:
  - pattern: "What NOT to do"
    why_bad: "Explanation"
    better_approach: "Correct way"

reusability:
  applicability: "HIGH|MEDIUM|LOW"
  similar_scenarios: ["List of similar use cases"]
  pattern_extraction:
    pattern_name: "Name"
    documentation: "path/to/pattern/doc"

metrics:
  test_coverage: "X%"
  tests_created: N
  tests_passing: N
  documentation_artifacts: N

outcomes:
  immediate: ["Short-term results"]
  long_term: ["Long-term benefits"]

recommendations:
  immediate: ["P0 actions"]
  short_term: ["P1 actions"]
  long_term: ["P2+ actions"]

related_files:
  implementation: "path/to/file"
  tests: ["list of test files"]
  documentation: ["list of docs"]

governance:
  core_rules_followed: ["CORE-XXX: Description"]
  audit_trail: "Status"
  best_practices_applied: ["Security", "Performance", etc.]

meta:
  captured_by: "GitHub Copilot (CORTEX Architect)"
  capture_method: "Automated extraction"
  capture_date: "YYYY-MM-DD"
  review_status: "Approved|Pending"
  tags: ["keyword", "tags"]
```

## Usage

### For Developers

**Before tackling a new problem:**

1. Search lessons-learned/ for similar incidents
2. Check patterns/ for reusable solutions
3. Review anti-patterns/ to avoid known mistakes

```bash
# Search for specific topic
grep -r "rendering" docs/meta/lessons-learned/
grep -r "tab system" docs/patterns/
grep -r "getElementById" docs/anti-patterns/
```

### For Architects

**When planning new features:**

1. Review reusability scores in lessons
2. Check if pattern exists before creating new solution
3. Verify anti-patterns aren't being repeated

### For CORTEX Architect

**After DESIGN/EXEC completion:**

1. Extract lessons using template
2. Create reusable pattern if applicability is HIGH
3. Document anti-patterns if discovered
4. Update enhancement-history.yaml

## Searchability

### By Category

| Category | Description | Example Files |
|----------|-------------|---------------|
| Frontend Rendering | UI/DOM issues | CHAT01-2026-02-03.yaml |
| Backend Architecture | Server-side patterns | (future) |
| Testing | Test strategies | (future) |
| Performance | Optimization | (future) |
| Security | Hardening | (future) |

### By Severity

| Severity | Impact | Example |
|----------|--------|---------|
| P0 | Production broken | (future) |
| P1 | Major feature broken | CHAT01-2026-02-03.yaml |
| P2 | Minor issue | (future) |
| P3 | Cosmetic | (future) |

### By Reusability

| Score | Applicability | Example |
|-------|---------------|---------|
| HIGH | 10+ similar use cases | CHAT01 (DeferredRenderer) |
| MEDIUM | 3-10 use cases | (future) |
| LOW | 1-2 use cases | (future) |

## Quality Standards

### Every Lesson Must Include

- ✅ **Root Cause:** Technical explanation (not symptoms)
- ✅ **Solution:** Specific approach taken (with code references)
- ✅ **Tests:** Coverage numbers and test file references
- ✅ **Lessons:** Actionable insights (not vague statements)
- ✅ **Reusability:** Clear score with justification

### Anti-Patterns to Avoid

- ❌ Vague lessons ("Be more careful")
- ❌ Missing test coverage info
- ❌ No code references
- ❌ Symptoms instead of root cause
- ❌ No reusability assessment

## Metrics

### Current Statistics

| Metric | Value |
|--------|-------|
| **Total Lessons** | 1 |
| **HIGH Reusability** | 1 (100%) |
| **MEDIUM Reusability** | 0 (0%) |
| **LOW Reusability** | 0 (0%) |
| **Patterns Extracted** | 1 |
| **Anti-Patterns Documented** | 4 |
| **Average Tests per Lesson** | 20 |

### Growth Over Time

*Updated automatically as new lessons are added*

## Integration with CORTEX

### Prompt Enhancements

Lessons learned feed into:
- **Challenge Template:** Similarity scoring against past failures
- **Recommendation Gate:** Avoid repeating rejected patterns
- **TDD Enforcement:** Test coverage requirements validated

### MCP Tools (Future)

Planned MCP tools for lessons management:
- `cortex_search_lessons` - Search by keyword/category
- `cortex_extract_lessons` - Auto-extract from chat transcripts
- `cortex_lessons_stats` - Metrics dashboard
- `cortex_pattern_recommend` - Suggest patterns for current problem

## Examples

### Example 1: Chat01 Dashboard Incident

**Problem:** 5 containers failed to render in hidden tabs  
**Root Cause:** `getElementById()` returns null for `aria-hidden="true"` elements  
**Solution:** DeferredRenderer pattern (queue-based deferred execution)  
**Outcome:** 100% fix, 86% performance improvement, reusable pattern  
**Reusability:** HIGH - applies to all tab-based SPAs

**See:** [CHAT01-2026-02-03.yaml](CHAT01-2026-02-03.yaml)

---

## Contributing

### When to Create a Lesson

✅ **Create lesson when:**
- Implementation solved a non-trivial problem
- Tests were written (TDD followed)
- Solution is reusable
- Incident had user impact
- Pattern emerged naturally

❌ **Don't create lesson for:**
- Trivial fixes (typos, formatting)
- Work without tests
- Temporary workarounds
- Configuration-only changes

### Lesson Quality Checklist

- [ ] Root cause is technical (not vague)
- [ ] Solution references actual code
- [ ] Test coverage specified with file paths
- [ ] At least 3 actionable lessons
- [ ] Reusability score justified
- [ ] Related pattern documented (if HIGH reusability)
- [ ] Anti-patterns identified (if discovered)
- [ ] Enhancement history updated (if from recommendation)

---

## Related Documentation

- [Patterns Library](../../patterns/README.md)
- [Anti-Patterns Catalog](../../anti-patterns/README.md)
- [Enhancement History](../enhancement-history.yaml)
- [CORTEX Architect Prompt](../../../.github/prompts/cortex-architect.prompt.md)

---

**Last Updated:** 2026-02-03  
**Maintainer:** CORTEX Architect  
**Status:** Active ✅
