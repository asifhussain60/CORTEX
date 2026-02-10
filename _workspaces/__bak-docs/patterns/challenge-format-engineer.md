# Engineer-Focused Challenge Format Pattern

**Pattern ID:** PATTERN-CHALLENGE-001  
**Created:** 2026-02-04  
**Source:** chat01.md DIGEST analysis  
**Status:** ✅ Active  
**Audience:** Software Engineers (Primary CORTEX users)

---

## Context

CORTEX Architect generates challenges for every DESIGN mode request. Original format was verbose (150+ lines, 3 separate tables, multi-role analysis), optimized for executive/PM audiences. However, **software engineers are the primary CORTEX users** and need faster comprehension.

---

## Problem

**Verbose Challenge Format Issues:**
- 150+ lines to scan (cognitive overload)
- 3 separate tables (Extensibility, Tradeoffs, Weaknesses) with redundant information
- Multi-role analysis (engineers, architects, PMs, researchers) adds noise for engineer-only tasks
- Evidence buried in separate "Implementation Truth" rows (context switching)
- Slow comprehension (30+ seconds to parse)

**Evidence:**
- chat01.md: User feedback "too verbose"
- Analysis: 3 tables repeating similar information
- Comparison: 150 lines original vs 15 lines condensed

---

## Solution

**Condensed Engineer-Focused Format (15-20 lines):**

```markdown
## ⚠️ ENGINEERING ANALYSIS

**Problem:** {1-sentence problem statement}

### Critical Issues (High Confidence ✅)
1. **{Issue 1}** — {evidence: grep/line numbers} | Impact: {specific}
2. **{Issue 2}** — {evidence: concrete proof} | Impact: {specific}
3. **{Issue 3}** — {evidence: test/implementation gap} | Impact: {specific}
4. **{Issue 4}** — {evidence: pattern detected} | Impact: {specific}
5. **{Issue 5}** — {evidence: technical debt count} | Impact: {specific}

### Recommended Fix (Effort: {S/M/L})
**Strategy:** {1-2 sentences describing approach}  
**Why:** {extensibility + scalability benefits in 1 sentence}  
**Tradeoff:** {cost} → {benefit} ({acceptable/not acceptable})  
**Evidence:** {Implementation Truth: what exists, what's missing, line numbers}

### Alternative Considered
{Brief alternative} → Rejected ({reason})

⏳ Type "proceed" to implement with TDD
```

---

## Key Improvements

| Change | Benefit |
|--------|---------|
| **Single List Format** | No table switching, linear reading |
| **Inline Evidence** | No context switching, evidence with issue |
| **Condensed Sections** | Merged 3 tables → 1 Critical Issues list |
| **Technical Language** | No business jargon, engineer-optimized |
| **10x Reduction** | 150 lines → 15 lines (90% reduction) |
| **5-Issue Standard** | Consistent structure, easy to scan |

---

## When to Use

| Use Engineer-Focused | Use Comprehensive |
|---------------------|-------------------|
| ✅ Primary audience = software engineer | ❌ Multi-stakeholder decision |
| ✅ Technical implementation task | ❌ Architecture review with executives |
| ✅ Code-level changes | ❌ Strategic planning with PMs |
| ✅ Fast comprehension needed | ❌ Full documentation required |
| ✅ **DEFAULT for all DESIGN mode** | ⚠️ Only on explicit request |

---

## Implementation

**Files:**
- `.github/prompts/cortex-architect.prompt.md` (v13.0)
- `.github/agents/core/cortex-architect.md` (v13.0)

**Audience Detection Logic:**
```python
def detect_audience(request: str, explicit_format: str = None) -> str:
    """
    Returns: 'engineer' (default) | 'comprehensive' (on request)
    """
    if explicit_format:
        return explicit_format
    
    # Keywords triggering comprehensive format
    comprehensive_keywords = [
        "full analysis for all roles",
        "show to executives",
        "stakeholder review",
        "comprehensive format"
    ]
    
    if any(kw in request.lower() for kw in comprehensive_keywords):
        return "comprehensive"
    
    return "engineer"  # Default
```

---

## Examples

### Before (Comprehensive - 150+ lines)
```markdown
## ⚠️ CHALLENGE + RECOMMENDATION

**User's Request:** {describe}

### 🎯 Extensibility & Scalability Analysis
| Dimension | Current State | Gap | Future-Proofing |
|-----------|--------------|-----|-----------------|
| **Horizontal Scale** | {current} | {gap} | {path to 10x} |
| **Extension Points** | {current} | {gap} | {path for new roles/agents} |
| **Degradation Pattern** | {current} | {gap} | {priority when under stress} |
| **Distributed Ready** | {current} | {gap} | {federated/multi-region path} |

### ⚖️ Accuracy vs Efficiency Tradeoff
| Factor | Accuracy Cost | Speed Cost | Recommended |
|--------|--------------|-----------|-------------|
| {check 1} | {precision} | {latency} | {tradeoff choice + why} |
| {check 2} | {precision} | {latency} | {tradeoff choice + why} |

### 🔴 Identified Weaknesses
| # | Weakness | Category | Impact | Root Cause |
|---|----------|----------|--------|-----------|
| 1 | {specific} | {Ext/Scale/Accuracy/Efficiency/Architecture} | {impact} | {why} |
| 2 | {specific} | {category} | {impact} | {why} |
| 3 | {specific} | {category} | {impact} | {why} |

### 🟢 Evidence-Based Fix Plan
[150+ more lines...]
```

**Issues:**
- Too many tables (3 separate)
- Redundant information (weakness appears in 2-3 places)
- Executive language ("Future-Proofing", "Distributed Ready")
- Takes 30+ seconds to scan

---

### After (Engineer-Focused - 15 lines)
```markdown
## ⚠️ ENGINEERING ANALYSIS

**Problem:** Analyze existing CORTEX SPA dashboard, assess GPT enhancement recommendations (Phase 21)

### Critical Issues (High Confidence ✅)
1. **Missing SPA Framework** — evidence: `dashboard.html:1-1109` has 1,109 lines inline | Impact: Hard to scale to 100+ use cases
2. **No Build Tooling** — evidence: package.json lacks Vite/Webpack | Impact: Cannot tree-shake, lazy-load
3. **Incomplete Testing** — evidence: 15 spec files but no E2E | Impact: Regression risk
4. **Missing Diagrams** — evidence: Sankey, Heatmap, Box-and-Whisker absent | Impact: No risk visualization
5. **No Use Case Scalability** — evidence: Lacks Fuse.js integration | Impact: Can't find relevant scenarios

### Recommended Fix (Effort: L - 2-3 weeks)
**Strategy:** Incremental modularization with build tooling + diagram additions + test hardening  
**Why:** Preserves working components, enables 100+ use case support, component library pattern  
**Tradeoff:** 2-week effort → 10x maintainability + 40x faster data load  
**Evidence:** Phase 21 YAML lines 150-200: JSON 5ms vs SQLite 200ms

### Alternative Considered
React/Angular Full Rewrite → Rejected (violates CORE-035, discards working components, 4-week effort)

⏳ Type "proceed" to implement with TDD
```

**Benefits:**
- Single scan (15 lines)
- Evidence inline (no jumping between sections)
- Technical precision (line numbers, LOC counts)
- Clear action path (proceed command)

---

## Metrics

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Lines** | 150+ | 15-20 | 90% reduction |
| **Tables** | 3 | 0 | Linear reading |
| **Scan Time** | 30+ sec | 5-10 sec | 75% faster |
| **Context Switches** | 5+ | 0 | No jumping |
| **Comprehension** | Moderate | Fast | Qualitative |

---

## Related Patterns

- [Implementation Truth (CORE-030)](../05-reference/core-rules.md#core-030)
- [DoR Gate Pattern](dor-gate-pattern.md)
- [Evidence-Based Estimation](evidence-based-estimation.md)

---

## Anti-Patterns

**Don't:**
- ❌ Use comprehensive format by default (99% of requests are engineer-focused)
- ❌ Duplicate information across multiple tables
- ❌ Bury evidence in separate "Implementation Truth" rows
- ❌ Use business jargon when technical terms are clearer
- ❌ Omit evidence (all claims must cite code/docs/metrics)

---

## Success Criteria

✅ Challenge fits in single screen (no scrolling)  
✅ Evidence inline with each issue  
✅ Technical language optimized for engineers  
✅ Clear recommended fix with tradeoff  
✅ Alternative considered + rejection reason  
✅ Explicit proceed command  

---

**Status:** ✅ Active in production (cortex-architect v13.0)
