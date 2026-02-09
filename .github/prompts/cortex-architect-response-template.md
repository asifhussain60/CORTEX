# CORTEX Architect Response Template Guide
**Version:** 1.0 | **Updated:** 2026-02-09 | **Purpose:** Visual enhancement standards for Copilot Chat

---

## 🎨 Visual Enhancement Standards

### Header Structure (MANDATORY)

**Single Response Header** (appears once at top of response):
```markdown
## 🏛️ CORTEX Architect {MODE}
**Author:** Asif Hussain | **Orchestrator:** {OrchestratorName} ✅

---
```

**Section Headers** (use h2 ## for main sections):
```markdown
## 📊 Architecture Review

## 🔍 Analysis Results

## 🚀 Recommendations

## ✅ Implementation Plan
```

**Sub-sections** (use h3 ### and h4 ####):
```markdown
### Current State Analysis

#### Strengths
#### Weaknesses

### Proposed Solution

#### Design Approach
#### Implementation Steps
```

---

## 📋 Problem/Solution Pattern

### Two-Column Comparison Table

**Use for architectural issues:**

| 🔴 **Problem** | 🟢 **Solution** |
|----------------|-----------------|
| • **Static intent classification**<br>• Pattern matching only<br>• No semantic understanding<br>• Cannot handle compound intents | • **Semantic NLP classification**<br>• Multi-label support<br>• Confidence scoring<br>• Learning from corrections |
| • **Stub examination phase**<br>• Hardcoded feature lists<br>• No real codebase analysis<br>• Ignores context parameter | • **Real AST/Git integration**<br>• Dynamic feature extraction<br>• Call graph generation<br>• Import dependency analysis |
| • **Empty knowledge retrieval**<br>• 45+ YAML files unused<br>• Static cache keys<br>• No domain integration | • **Dynamic knowledge loader**<br>• Semantic YAML search<br>• Intent-based retrieval<br>• Multi-source knowledge |

---

## 🎯 Status Icons (Semantic Colors)

### Progress Status
- 🟢 **Complete/Good** — Feature working as designed
- 🔵 **In Progress** — Currently being implemented
- 🟡 **Warning/Medium** — Needs attention, not critical
- 🔴 **Critical/Blocked** — Must be fixed before proceeding
- ⚪ **Planned/Pending** — Not started yet
- ⚠️ **Attention Required** — Review recommended
- ✅ **Passed/Validated** — Tests passing, criteria met
- ❌ **Failed/Violation** — Tests failing, requirements not met

### Priority Indicators
- 🔴 **P0** — Critical blocker, production breaking
- 🟡 **P1** — High priority, impacts user experience
- 🟢 **P2** — Medium priority, enhancement
- 🔵 **P3** — Low priority, nice to have

---

## 📊 Data Tables

### Comparison Tables (Before/After)

| Metric | Baseline | Target | Status |
|--------|----------|--------|--------|
| Intent Accuracy | 60% | 95% | 🔴 Gap |
| Codebase Understanding | 0% | 90% | 🔴 Critical |
| Knowledge Retrieval | 0% | 100% | 🔴 Critical |
| Routing Accuracy | 70% | 95% | 🟡 Improve |
| Latency P95 | <10ms | <50ms | 🟢 Excellent |

### Architecture Matrix

| Component | Implementation | Intelligence | Priority |
|-----------|---------------|--------------|----------|
| Phase 1: Language | Pattern matching | ⚠️ Basic | 🟡 P1 |
| Phase 2: Examination | Stub data | 🔴 None | 🔴 P0 |
| Phase 3: Synthesis | Static mapping | ⚠️ Basic | 🟡 P1 |
| Phase 4: Knowledge | Empty cache | 🔴 None | 🔴 P0 |

---

## 🔍 Code Comparison Blocks

### Side-by-Side (Problem → Solution)

**❌ Current (Problem):**
```python
# Static pattern matching - no semantic understanding
self._intent_patterns: Dict[str, List[str]] = {
    "IMPLEMENT": ["create", "add", "implement"],
    "FIX": ["fix", "bug", "error"],
}
```

**✅ Proposed (Solution):**
```python
# Semantic classification with confidence scoring
def classify_intent(self, query: str) -> IntentClassification:
    embedding = self.model.encode(query)
    similarities = cosine_similarity(embedding, self.intent_embeddings)
    return IntentClassification(
        primary=max(similarities),
        confidence=similarities.max(),
        secondary=[s for s in similarities if s > 0.5]
    )
```

---

## 📈 Progress Visualization

### ASCII Progress Bars (for execution updates)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Phase 53: LENS Intelligence Upgrade
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[████████░░] 80% S5: Semantic Classification
├─ ✅ S1: Phase 2 Integration (12 tests)
├─ ✅ S2: Knowledge Loader (10 tests)  
├─ ✅ S3: Intent Embeddings (8 tests)
├─ ✅ S4: Confidence Scoring (14 tests)
├─ 🔵 S5: Semantic Classifier (6/10 tests)
├─ ⚪ S6: Performance Optimization (pending)
└─ ⚪ S7: Cleanup & Migration (pending)

Tests: 50/60 | Coverage: 89% | Duration: 12m 34s
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Stage Checklist

```
## ✅ Implementation Progress

- [x] S1: Foundation fixes (Phase 2 integration)
- [x] S2: Knowledge base integration
- [x] S3: Semantic classification
- [ ] S4: Dynamic confidence scoring
- [ ] S5: Multi-orchestrator routing
- [ ] S6: Performance optimization
- [ ] S7: Cleanup & migration
```

---

## 🗂️ Collapsible Sections

### For Long Technical Details

<details>
<summary><strong>📋 Technical Implementation Details (Click to expand)</strong></summary>

```python
# Detailed implementation code
class SemanticIntentClassifier:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.intent_embeddings = self._load_embeddings()
    
    def classify(self, query: str) -> ClassificationResult:
        # ... implementation
        pass
```

**Key Design Decisions:**
- Used lightweight sentence-transformers (no API calls)
- Pre-computed embeddings for 100+ examples per intent
- SQLite storage for fast lookup (<5ms)
- Multi-label support with confidence thresholds

</details>

---

## 🎯 Recommendations Format

### Numbered Priority List

**Use for action items:**

#### Priority 1: Critical Blockers (P0)

1. **Integrate Phase 2 with LENSOrchestrator**
   - **Problem:** Examination returns stub data
   - **Impact:** 🔴 Zero codebase understanding
   - **Effort:** 2 days
   - **Files:** `cortex/brain/lens/pipeline.py`, `cortex/brain/lens/orchestrator_adapter.py`

2. **Connect Phase 4 to knowledge YAMLs**
   - **Problem:** 45+ YAML files unused
   - **Impact:** 🔴 No best practices integration
   - **Effort:** 2 days
   - **Files:** `cortex/brain/lens/knowledge_loader.py`, `cortex/brain/lens/pipeline.py`

#### Priority 2: Intelligence Improvements (P1)

3. **Implement semantic intent classification**
   - **Problem:** Pattern matching only (60% accuracy)
   - **Impact:** 🟡 Misses compound intents
   - **Effort:** 3 days
   - **Files:** `cortex/brain/lens/semantic_classifier.py`

---

## 📊 Metrics Dashboard

### Summary Cards

```
┌─────────────────────────────────────────────────────────────┐
│ 📊 LENS Intelligence Score                                   │
├─────────────────────────────────────────────────────────────┤
│ Current:  5.0/10  ⚠️  Not production-ready                   │
│ Target:   9.0/10  🎯  Production-grade intelligence          │
│ Gap:      4.0     🔴  Critical improvements needed           │
├─────────────────────────────────────────────────────────────┤
│ Blockers: 2 P0 issues (Phase 2 + Phase 4)                   │
│ Timeline: 21 days (7 stages)                                 │
│ Impact:   +35% accuracy, +90% understanding                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚨 Alert Boxes

### Critical Issues

> **🔴 CRITICAL: Phase 2 Examination Returns Stub Data**
> 
> **Impact:** Zero real codebase analysis, all examination results are hardcoded
> **Files Affected:** `cortex/brain/lens/pipeline.py` (ExaminationPhase)
> **Resolution:** Connect to LENSOrchestrator for real AST/Git analysis
> **Priority:** P0 — Must fix before production

### Warnings

> **⚠️ WARNING: Knowledge Retrieval Returns Empty List**
> 
> **Impact:** 45+ YAML knowledge files unused by pipeline
> **Workaround:** Manual knowledge injection via context
> **Resolution:** Implement knowledge_loader.py with semantic search
> **Priority:** P0 — Blocking intelligent recommendations

### Success Messages

> **✅ SUCCESS: Performance Targets Met**
> 
> **Latency P95:** 8ms (target: <50ms) — Excellent!
> **Cache Hit Rate:** 85% (target: 70%) — Exceeding expectations
> **Memory Usage:** 45MB (target: <100MB) — Efficient
> **Status:** 🟢 Production-ready performance

---

## 🔗 File Links

### Linkified File References

**Use clickable file links:**
- [cortex/brain/lens/pipeline.py](cortex/brain/lens/pipeline.py) — Main LENS implementation
- [cortex/orchestrators/core/lens_synthesis.py](cortex/orchestrators/core/lens_synthesis.py) — Orchestrator-level synthesis
- [tests/unit/brain/lens/test_pipeline.py](tests/unit/brain/lens/test_pipeline.py) — Test suite

**Line-specific references:**
- [pipeline.py#L261](cortex/brain/lens/pipeline.py#L261) — Stub relationships
- [pipeline.py#L396](cortex/brain/lens/pipeline.py#L396) — Empty knowledge cache

---

## 📋 Decision Matrix

### For architectural choices:

| Option | Pros | Cons | Recommendation |
|--------|------|------|----------------|
| **A: Semantic Classification** | • 95% accuracy<br>• Multi-label support<br>• Learning capability | • 3 days implementation<br>• Requires embedding DB | ✅ **Recommended** |
| **B: Pattern Matching+** | • Fast implementation<br>• No dependencies | • 70% accuracy ceiling<br>• No compound intents | ❌ Insufficient |
| **C: LLM API** | • Highest accuracy<br>• Zero implementation | • API costs<br>• Latency penalty<br>• External dependency | ❌ Not suitable |

---

## 🎯 Visual Summary (End of Response)

### Verdict Section

```markdown
## ✅ Verdict: Architecture Assessment

| Dimension | Score | Status |
|-----------|-------|--------|
| **Structural Design** | 8/10 | ✅ Clean separation |
| **Intelligence** | 3/10 | 🔴 Rule-based only |
| **Performance** | 9/10 | 🟢 Excellent |
| **Context Awareness** | 2/10 | 🔴 Disconnected |
| **Knowledge Integration** | 1/10 | 🔴 Unused YAMLs |
| **Extensibility** | 7/10 | 🟢 Easy to extend |

**Overall:** 5.0/10 — **⚠️ Not production-ready**

**Blockers:**
1. 🔴 Phase 2 examination returns stub data
2. 🔴 Phase 4 knowledge retrieval empty
3. 🟡 Phase 3 routing static (no adaptation)
```

---

## 🚀 Next Steps Section

**Always end architectural reviews with clear action items:**

```markdown
## 🚀 Next Steps

**Immediate Actions (This Session):**
1. Run pre-flight audit: `python scripts/audit_lens_migration.py`
2. Review Phase 53 plan: [phase-53-lens-intelligence-upgrade.yaml](cortex-registry/_cortex-master/phases/active/phase-53-lens-intelligence-upgrade.yaml)
3. Choose implementation approach

**Short-term (1 week):**
- ✅ Fix P0 blockers (Phase 2 + Phase 4 integration)
- ⚪ Implement semantic classification
- ⚪ Add confidence scoring

**Long-term (3 weeks):**
- Complete Phase 53 all 7 stages
- Validate 95% accuracy target
- Production deployment

**Decision Required:**
- [ ] Start Stage 1 implementation?
- [ ] Run audit first?
- [ ] Review dependencies?
```

---

## 📌 Key Principles

1. **Single header per response** — No repetition of "CORTEX Architect"
2. **Hierarchical sections** — h2 for main, h3/h4 for nested
3. **Problem/Solution tables** — Side-by-side comparisons
4. **Visual indicators** — Icons for status, priority, progress
5. **Collapsible details** — Hide verbose technical content
6. **Clear next steps** — Always provide actionable guidance

---

*This template ensures consistent, visually appealing, and actionable responses in CORTEX Architect mode.*
