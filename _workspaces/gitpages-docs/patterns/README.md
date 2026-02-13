# Patterns Library

**Purpose:** Document reusable solution patterns extracted from real implementations  
**Owner:** CORTEX Architect  
**Status:** Active ✅

---

## Overview

This library contains proven, production-ready patterns discovered through actual CORTEX implementations. Unlike theoretical design patterns, these emerged from solving real problems and are backed by tests, metrics, and lessons learned.

## Current Patterns

| Pattern | Category | Status | Reusability | Source |
|---------|----------|--------|-------------|--------|
| [DeferredRenderer](deferred-renderer-pattern.md) | Frontend | Production ✅ | HIGH | Chat01 (2026-02-03) |

---

## Pattern Categories

### Frontend Architecture
- **DeferredRenderer** - Queue-based rendering for hidden elements

### Backend Architecture
*(To be added)*

### Testing Patterns
*(To be added)*

### Performance Optimization
*(To be added)*

---

## How to Use This Library

### For Developers

**Before implementing a feature:**

1. **Search** for similar problems in this library
2. **Evaluate** if pattern fits your use case
3. **Adapt** pattern to your specific needs
4. **Test** using provided testing strategies

**Example Search Workflow:**

```bash
# Find patterns by keyword
grep -r "tab system" docs/patterns/
grep -r "hidden element" docs/patterns/
grep -r "deferred" docs/patterns/

# Browse by category
ls -la docs/patterns/*-pattern.md
```

### For Architects

**When designing new features:**

1. Check if pattern library has existing solution
2. Evaluate pattern fit vs. building custom
3. Consider combining multiple patterns
4. Document new patterns when discovered

---

## Pattern Documentation Standard

Each pattern document includes:

### 1. Problem Statement
- Real-world issue that pattern solves
- Example of broken code
- Impact of problem

### 2. Solution Architecture
- Core concept (1-sentence)
- Implementation code with comments
- Usage examples

### 3. Benefits
- Specific advantages
- Trade-offs (when NOT to use)

### 4. Testing Strategy
- Unit test examples
- Integration test examples
- Coverage requirements

### 5. Performance Characteristics
- Benchmarks from production
- Resource usage
- Scalability considerations

### 6. Variants & Extensions
- Alternative implementations
- Framework-specific adaptations
- Advanced features

### 7. Related Patterns
- Complementary patterns
- Alternative approaches
- Anti-patterns to avoid

### 8. Real-World Examples
- Production usage scenarios
- Code samples from CORTEX
- Success metrics

### 9. Migration Guide
- Before/after comparison
- Step-by-step migration
- Validation checklist

### 10. Metadata
- Pattern ID, author, date
- Status (Draft, Production, Deprecated)
- Reusability score
- Tags for searchability

---

## Pattern Reusability Scoring

| Score | Criteria | Example |
|-------|----------|---------|
| **HIGH** | 10+ similar use cases across domains | DeferredRenderer (all tab systems, accordions, modals) |
| **MEDIUM** | 3-10 similar use cases within domain | *(future)* |
| **LOW** | 1-2 specific use cases | *(future)* |

---

## Pattern Lifecycle

### 1. Discovery (Source: Lessons Learned)

Pattern emerges from solving real problem:
- Documented in lessons-learned/{ID}.yaml
- Reusability marked as HIGH or MEDIUM
- Pattern name assigned

### 2. Extraction

Full pattern documentation created:
- Copy template from existing pattern
- Fill in all 10 sections
- Add to this README

### 3. Validation

Pattern is tested in production:
- Tests confirm functionality
- Metrics validate performance
- Real usage demonstrates value

### 4. Promotion

Pattern becomes official recommendation:
- Added to prompt recommendations
- Mentioned in code reviews
- Taught to new developers

### 5. Evolution

Pattern is refined over time:
- Variants added for new use cases
- Performance optimizations
- Framework-specific adaptations

### 6. Deprecation (Rare)

Pattern becomes obsolete:
- Better pattern discovered
- Technology shift makes irrelevant
- Moved to deprecated/ folder

---

## Pattern Template

```markdown
# {Pattern Name}

**Category:** {Frontend|Backend|Testing|Performance|Security}  
**Problem Domain:** {Specific area}  
**Complexity:** {Simple|Moderate|Complex}  
**Status:** {Draft|Production-Ready|Deprecated}

---

## Problem Statement

### The Issue
{Describe problem with code example}

**Impact:**
- {Impact 1}
- {Impact 2}

### Real-World Example
```{language}
// ❌ BAD: {What breaks}
```

---

## Solution: {Pattern Name}

### Core Concept
{1-sentence explanation}

### Implementation
```{language}
// ✅ GOOD: {Working code}
```

### Usage Pattern
```{language}
// Example usage
```

---

## Benefits

| Benefit | Description |
|---------|-------------|
| {Benefit 1} | {Explanation} |

---

## When to Use

✅ **Use when:**
- {Scenario 1}
- {Scenario 2}

❌ **Don't use when:**
- {Scenario 1}
- {Scenario 2}

---

## Testing Strategy

### Unit Tests
```{language}
// Test examples
```

### Integration Tests
```{language}
// Test examples
```

---

## Performance Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| {Metric 1} | {Value} | {Context} |

---

## Variants & Extensions

### Variant 1: {Name}
```{language}
// Code
```

---

## Related Patterns

| Pattern | Relationship | When to Use Instead |
|---------|--------------|---------------------|
| {Pattern} | {Complementary|Alternative} | {Scenario} |

---

## Real-World Examples

### Example 1: {Name}
{Description with code}

---

## Anti-Patterns (What NOT to Do)

### ❌ Anti-Pattern 1: {Name}
**Why Bad:** {Explanation}  
**Fix:** {Correct approach}

---

## Migration Guide

### From {Old Approach}
```{language}
// Before
```

```{language}
// After
```

### Migration Checklist
- [ ] {Step 1}
- [ ] {Step 2}

---

## Metadata

| Field | Value |
|-------|-------|
| **Pattern ID** | PTN-{XXX} |
| **Author** | {Name} |
| **Date Created** | YYYY-MM-DD |
| **Status** | {Status} |
| **Complexity** | {Level} |
| **Test Coverage** | {%} |
| **Reusability** | {HIGH|MEDIUM|LOW} |
| **Tags** | {tag1, tag2, tag3} |
```

---

## Quality Standards

### Every Pattern Must Have

- ✅ Real production example (not theoretical)
- ✅ Working code samples (copy-paste ready)
- ✅ Test examples (unit + integration)
- ✅ Performance metrics (benchmarks)
- ✅ Clear use cases (when to use / not use)
- ✅ Migration guide (before/after)
- ✅ Anti-patterns section (what to avoid)

### Common Mistakes to Avoid

- ❌ Theoretical patterns (no real usage)
- ❌ Missing code examples
- ❌ No test strategy
- ❌ Vague benefits ("better", "faster")
- ❌ No performance data
- ❌ Missing anti-patterns section

---

## Metrics

### Current Library Stats

| Metric | Value |
|--------|-------|
| **Total Patterns** | 1 |
| **Production-Ready** | 1 (100%) |
| **HIGH Reusability** | 1 (100%) |
| **MEDIUM Reusability** | 0 (0%) |
| **Categories Covered** | 1 (Frontend) |
| **Average Tests per Pattern** | 20 |
| **Avg Performance Improvement** | 86% |

### Growth Target

- **Q1 2026:** 10 patterns
- **Q2 2026:** 25 patterns
- **Q3 2026:** 50 patterns

---

## Contributing

### When to Add a Pattern

✅ **Add pattern when:**
- Pattern solved real problem in production
- Reusability score is HIGH or MEDIUM
- Tests exist with good coverage
- Performance metrics measured
- Use cases clearly identified

❌ **Don't add pattern for:**
- One-off solutions (LOW reusability)
- Unproven approaches (not in production)
- Framework-specific code (without abstraction)
- Trivial patterns (standard library usage)

### Pattern Submission Checklist

- [ ] Pattern emerged from real implementation
- [ ] Documented in lessons-learned/ first
- [ ] Reusability score HIGH or MEDIUM
- [ ] All 10 sections completed
- [ ] Code examples are copy-paste ready
- [ ] Tests provided (unit + integration)
- [ ] Performance metrics included
- [ ] Anti-patterns documented
- [ ] Migration guide provided
- [ ] Metadata complete

---

## Related Documentation

- [Lessons Learned](../meta/lessons-learned/README.md) - Source of patterns
- [Anti-Patterns](../anti-patterns/README.md) - What to avoid
- [Enhancement History](../meta/enhancement-history.yaml) - Tracking adoptions

---

**Last Updated:** 2026-02-03  
**Maintainer:** CORTEX Architect  
**Next Review:** 2026-03-03
