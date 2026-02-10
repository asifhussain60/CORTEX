# Context Consumption Governance (ENH-046)

**Authority:** ENH-046 | **Status:** Phase 1 Complete (4 phases total)  
**Priority:** P1 (Critical Governance Violation)

---

## 🎯 Problem Statement

**CRITICAL:** CORTEX loads massive context without pre-synthesis, causing GitHub Copilot token exhaustion.

**Evidence (chat01.md):**
- 1,002 lines triggered **5 "Summarized conversation history" events** (1 per 200 lines)
- **13 large file references** loaded without caching or compression
- Estimated **65KB context per turn** (3x over 20KB budget)
- **Target:** ≤1 summarization per 1000 lines (80% reduction needed)

---

## 📊 Metrics System (Phase 1 - COMPLETE)

### Components

| Component | Status | Tests | Purpose |
|-----------|--------|-------|---------|
| `context_metrics_collector.py` | ✅ | 12/12 | Prometheus metrics + session tracking |
| `test_context_metrics_collector.py` | ✅ | 12/12 | Test coverage |
| `grafana-dashboards/context-consumption-governance.json` | ✅ | N/A | Real-time visualization |

### Prometheus Metrics

```python
# Context size tracking
cortex_context_size_before_bytes   # Histogram: context before synthesis
cortex_context_size_after_bytes    # Histogram: context after synthesis

# Efficiency metrics
cortex_context_compression_ratio    # Gauge: 0.0-1.0 (target: 0.6)
cortex_context_synthesis_time_ms    # Histogram: latency (target: <100ms)

# Cache metrics
cortex_context_cache_hit_rate       # Gauge: percentage (target: ≥70%)

# Governance metrics (CRITICAL)
cortex_copilot_summarization_total  # Counter: "Summarized conversation history" events
cortex_copilot_reference_total      # Counter: file references by type (agent, yaml, source)

# Compliance
cortex_token_budget_violations_total  # Counter: turns exceeding budget
cortex_token_budget_usage_tokens      # Histogram: token usage distribution
```

### Usage Example

```python
from cortex.interaction.context_metrics_collector import get_context_metrics_collector

collector = get_context_metrics_collector()

# Start tracking
collector.start_synthesis("session-123")

# ... perform context synthesis ...

# End tracking + publish metrics
metrics = collector.end_synthesis(
    session_id="session-123",
    size_before=65000,  # 65KB raw context
    size_after=18000,   # 18KB after synthesis
    cache_hits=5,
    cache_misses=2,
    token_budget=20000,
    tokens_used=12000,
    references_loaded=13,
    reference_types={"agent": 6, "yaml": 5, "source": 2}
)

# Check results
assert metrics.compression_ratio >= 0.6  # 72% compression achieved
assert metrics.tokens_used <= 20000      # Within budget
```

### Grafana Dashboard

**Location:** `deployment/grafana-dashboards/context-consumption-governance.json`

**Panels:**
1. **Context Size Trends** - Before/after line chart with 50KB alert threshold
2. **Compression Ratio** - Gauge (red <40%, yellow 40-60%, green ≥60%)
3. **Cache Hit Rate** - Gauge (red <50%, yellow 50-70%, green ≥70%)
4. **Copilot Summarization Events** - CRITICAL governance metric (alert >5/hour)
5. **Token Budget Violations** - Counter (target: 0)
6. **Synthesis Latency P99** - Histogram (red >250ms, yellow 100-250ms, green <100ms)
7. **Reference Types Distribution** - Pie chart breakdown
8. **Token Budget Usage Distribution** - Heatmap

**Access:** http://localhost:3000/d/cortex-context

---

## 🔍 AUDIT Mode Integration (COMPLETE)

### P1 Infrastructure Check

Added to `.github/prompts/cortex-architect.prompt.md` (line 369):

```markdown
| **Context Consumption Governance (ENH-046)** | **CRITICAL: Measure context efficiency metrics, detect Copilot token exhaustion patterns, enforce synthesis before handoff** | **ContextMetricsCollector + chat log analysis** |
```

### Detailed Audit Procedure (lines 503-587)

**Metrics Collection:**

| Metric | Target | Red Flag | Measurement |
|--------|--------|----------|-------------|
| Context size per turn | ≤20KB | >50KB | Estimate refs × avg file size |
| Copilot summarization frequency | ≤1 per 1000 lines | >3 per 1000 | Grep pattern count |
| Reference count per turn | ≤5 synthesized | >10 raw | Count "Read [file]" |
| Compression ratio | ≥60% | <40% | (Before - After) / Before |
| Cache hit rate | ≥70% | <50% | Hits / Total |
| Token budget violations | 0 | >0 | Prometheus counter |

**Baseline Measurement (chat01.md):**

```markdown
| Metric | Value | Status |
|--------|-------|--------|
| Copilot Summarizations | 5 | 🔴 CRITICAL |
| File References | 13+ | 🔴 CRITICAL |
| Lines per Summarization | 200 | 🔴 Below target (1000) |
| Estimated Context Size | ~65KB | 🔴 3x over budget |
```

**Target Metrics (After ENH-046):**

```markdown
| Metric | Current | Target | Improvement |
|--------|---------|--------|-------------|
| Summarizations | 5 per 1000 | ≤1 per 1000 | 80% reduction |
| Context Size | 65KB | ≤20KB | 69% reduction |
| Reference Count | 13 raw | ≤5 synthesized | 62% reduction |
| Cache Hit Rate | 0% | ≥70% | +70pp |
```

---

## 🚀 Next Phases

### Phase 2: Context Budget Manager (Week 2)

**Deliverable:** `cortex/interaction/context_budget_manager.py`

**Features:**
- Token allocation and enforcement (default 20K budget)
- Overflow prevention (block operation if budget exceeded)
- Estimation using tiktoken library (accurate GPT tokenizer)

**Tests:** 15 unit tests

### Phase 3: Context Synthesizer (Week 3)

**Deliverable:** `cortex/interaction/context_synthesizer.py`

**Features:**
- Agent file summarization (e.g., 1903 lines → 3 lines = 99.8% reduction)
- YAML rule filtering by intent_type (500 rules → 15 applicable = 97% reduction)
- AST-based file content compression (250 lines → 5 lines = 98% reduction)

**Tests:** 25 unit tests

### Phase 4: Context Synthesis Gateway + Integration (Week 4)

**Deliverables:**
- `cortex/interaction/context_synthesis_gateway.py`
- `cortex/interaction/context_cache_layer.py`
- Enhancement to `InteractionOrchestrator`

**Features:**
- Main gateway orchestrating all components
- LRU cache with TTL (10 minutes)
- Auto-integration with InteractionOrchestrator

**Tests:** 50 unit tests (30 gateway + 20 cache)

---

## ✅ Success Criteria

| Metric | Baseline | Target | Status |
|--------|----------|--------|--------|
| Context size per turn | 65KB | ≤20KB | Phase 3 |
| Copilot summarizations | 5 per 1000 | ≤1 per 1000 | Phase 4 |
| Compression ratio | 0% | ≥60% | Phase 3 |
| Cache hit rate | N/A | ≥70% | Phase 4 |
| Synthesis latency | N/A | <100ms | Phase 3 |
| Token budget compliance | Unknown | 100% | Phase 2 |

---

## 📚 Documentation

- **AUDIT Procedure:** `.github/prompts/cortex-architect.prompt.md` (lines 503-587)
- **Enhancement History:** `docs/meta/enhancement-history.yaml` (ENH-046 entry)
- **Grafana Dashboard:** `deployment/grafana-dashboards/context-consumption-governance.json`
- **This README:** `cortex/interaction/README-context-governance.md`

---

## 🔗 Related Enhancements

- **ENH-023:** LENS Context Caching (subsumed into Phase 3)
- **ENH-017:** LENS Performance Optimization

---

**Phase 1 Complete:** ✅ Metrics system operational with 12/12 tests passing
