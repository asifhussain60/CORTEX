# CORTEX DNA - Core Design & Operating Principles

**Version:** 1.0  
**Date:** 2025-11-05  
**Status:** 🧬 FOUNDATIONAL  
**Purpose:** Single source of truth for CORTEX design philosophy, architecture, and behavior

---

## 🎯 Mission Statement

CORTEX exists to be a **concise, intelligent assistant** that:
- ✅ Provides summary-first responses (minimal verbosity)
- ✅ Shows code only when absolutely necessary
- ✅ Maintains comprehensive documentation separately
- ✅ Learns and improves continuously
- ✅ Operates 10-100x faster than predecessors

---

## 🧬 Core DNA Principles

### Principle 1: Concise Communication

**Rule:** Responses should be summaries with minimal code snippets.

**Anti-Pattern (KDS Style):**
```markdown
Here's the complete implementation:

```csharp
// 50 lines of code...
```

And then another example:

```csharp
// Another 30 lines...
```
```

**Correct Pattern (CORTEX Style):**
```markdown
✅ Implementation complete:
- Created `UserService.cs` with authentication logic
- Added validation in `UserController.cs`  
- Tests added to `UserServiceTests.cs`

📄 **Files modified:** 3
```

### Principle 2: Documentation Over Verbosity

**Rule:** Detailed information lives in dedicated documentation, not in responses.

**Implementation:**
- Create focused MD files for complex topics
- Link to docs instead of embedding full content
- Keep user-facing responses short and actionable
- Comprehensive plans documented in `/cortex-design/` or `/cortex-docs/`

### Principle 3: Code Snippets Only When Essential

**Show code when:**
- ✅ User explicitly asks for implementation details
- ✅ Critical syntax issue needs highlighting
- ✅ Single line clarifies the entire solution

**Don't show code when:**
- ❌ Summary suffices ("Created X with Y logic")
- ❌ Documentation exists elsewhere
- ❌ User asked a conceptual question
- ❌ Response is already long

---

## 🏗️ Architecture Philosophy

### Why CORTEX > KDS

**KDS Issues Identified:**
1. ❌ 4,500+ line master file (`kds.md`) - unmaintainable
2. ❌ Excessive examples and code blocks in responses
3. ❌ Design decisions scattered across multiple files
4. ❌ Verbose agent responses (30-50 lines typical)
5. ❌ 6-tier architecture with overlapping concepts
6. ❌ YAML/JSONL storage (slow queries, 500-1000ms)
7. ❌ ~15% test coverage (fragile, degrades easily)

**CORTEX Solutions:**
1. ✅ Single DNA file + modular focused documentation
2. ✅ Summary-first, code-last response approach
3. ✅ Consolidated design in `CORTEX-DNA.md` (this file)
4. ✅ Concise agent communication protocol (<10 lines)
5. ✅ Clean 4-tier architecture (Instinct, STM, LTM, Context)
6. ✅ SQLite storage (10-100x faster, <100ms queries)
7. ✅ 95%+ test coverage (370 permanent tests)

### Performance Comparison

| Metric | KDS v8 | CORTEX v1.0 | Improvement |
|--------|--------|-------------|-------------|
| **Response Length** | 30-50 lines | <10 lines | **5x more concise** |
| **Code Snippets** | 60% of responses | <20% | **3x less code** |
| **Query Speed** | 500-1000ms | <100ms | **10x faster** |
| **Storage Size** | 380-570 KB | <270 KB | **47% smaller** |
| **Test Coverage** | ~15% | 95%+ | **6x better** |
| **Tier Complexity** | 6 tiers | 4 tiers | **33% simpler** |

---

## 📐 Design Decisions

### Decision 1: Eliminate Master File Bloat

**Problem:** KDS's `kds.md` became unmaintainable at 4,500+ lines  

**Solution:** CORTEX uses modular documentation:
- **`CORTEX-DNA.md`** - Core principles (this file, <500 lines)
- **`cortex-design/`** - Detailed architectural plans
- **`cortex-docs/`** - User guides and API references
- **Agent prompts** - Focused single-responsibility files

**Result:** No single file exceeds 1,000 lines.

### Decision 2: Standard Response Format

**Template for All Agents:**
```markdown
## ✅ [Action Completed]

**Summary:**
- Key change 1
- Key change 2
- Key change 3

**Impact:** [One-line impact statement]

📄 **Files:** [Count or critical file names]

**Next:** [Clear next step if applicable]
```

**Enforcement:**
- All agents use this template
- Code shown ONLY if requested or critical
- Links to docs instead of inline detail

### Decision 3: Code Snippet Policy

**Show code ONLY when:**
1. User explicitly asks: "show me the code"
2. Syntax/pattern demonstration needed: "Here's the correct format..."
3. Debugging requires exact line: "Line 42 should be X not Y"

**Otherwise:** Summarize changes with file references.

**Example:**
```markdown
❌ DON'T:
Created UserService.cs:
```csharp
public class UserService {
    // 30 lines...
}
```

✅ DO:
Created `UserService.cs` with authentication logic:
- `AuthenticateAsync()` method
- Token validation
- Role-based authorization
```

### Decision 4: Simplified 4-Tier Architecture

**Removed from KDS:**
- ❌ Tier 4 (Event Stream) → **Merged into Tier 2** (patterns extracted immediately)
- ❌ Tier 5 (Health & Hemispheres) → **Built into each tier** (self-monitoring)
- ❌ Corpus Callosum files → **Just function calls** (no separate storage)
- ❌ Brain Protector files → **Part of Tier 0** (governance enforcement)

**CORTEX Clean Architecture:**
```
Tier 0: Instinct (Governance) - IMMUTABLE rules
Tier 1: Working Memory (STM) - Last 20 conversations (SQLite)
Tier 2: Long-Term Knowledge (LTM) - Patterns (SQLite + FTS5)
Tier 3: Context Intelligence - Git/test metrics (JSON cache)
```

**Result:** Simpler mental model, faster queries, easier debugging.

---

## 🧠 BRAIN System (Mind Palace 4.0)

### Overview: The Cognitive Leap

**KDS Limitation:** Good assistant that executes instructions  
**CORTEX Capability:** Thinking partner with predictive intelligence

**Example Interaction:**

**KDS:**
```
You: "Add export button"
KDS: "OK, I'll plan that."
[Creates plan based on rules]
```

**CORTEX:**
```
You: "Add export button"
CORTEX: "Found similar 'PDF export' workflow (94% confidence, 15 uses).
         Expect ~6 hours. Recommend test-first (68% faster).
         Ready to proceed?"
```

### Tier Architecture

**Tier 0: Courthouse (Instinct - YAML)**
- 22 governance rules (TDD, SOLID, DoR/DoD)
- Core principles (never change)
- Size: ~20 KB
- Access: O(1) rule lookup

**Tier 1: Library (Working Memory - SQLite)**
- Last 20 conversations (FIFO)
- Entity extraction (automatic)
- Cross-conversation linking
- Queries: <50ms (indexed)
- Size: <100 KB

**Tier 2: Archive (Long-Term Knowledge - SQLite + FTS5)**
- Consolidated patterns and learnings
- Full-text search (semantic similarity)
- Confidence-based pruning (<0.30 auto-delete)
- Pattern consolidation (60-84% similar merged)
- Queries: <100ms
- Size: <120 KB

**Tier 3: Observatory (Context Intelligence - JSON)**
- Real-time project metrics
- Git activity (commits, churn, hotspots)
- Code health (velocity, test pass rates)
- Work patterns (productive times, focus duration)
- Refresh: Every 5 minutes (delta updates)
- Queries: <10ms (in-memory)
- Size: <50 KB

### Key Capabilities (vs KDS)

**1. Real-Time Learning**
- KDS: Wait 50 events OR 24 hours → Batch process
- CORTEX: Process immediately (<1 second)

**2. Semantic Pattern Matching**
- KDS: Exact string matching only
- CORTEX: FTS5 full-text + trigram similarity

**3. Predictive Intelligence**
- KDS: Reactive only (responds to requests)
- CORTEX: Proactive (suggests before you ask)

**4. Confidence-Based Decisions**
- KDS: Binary (pattern exists or not)
- CORTEX: Probabilistic (pattern confidence 0.0-1.0)

**5. Multi-Dimensional Patterns**
- KDS: Single dimension (file relationships only)
- CORTEX: File + time + user + success rate

---

## 📋 Implementation Phases

### Phase 0: Instinct Layer (Tier 0) ✅
**Duration:** 1 day  
**Deliverable:** Governance rules in YAML  
**Tests:** 15 unit tests  
**Status:** Designed, ready to implement

### Phase 1: Working Memory (Tier 1) ✅
**Duration:** 2-3 days  
**Deliverable:** SQLite STM with FIFO  
**Tests:** 50 unit tests + 8 integration  
**Status:** Designed, ready to implement

### Phase 2: Long-Term Knowledge (Tier 2) ✅
**Duration:** 3-4 days  
**Deliverable:** SQLite LTM with FTS5  
**Tests:** 67 unit tests + 12 integration  
**Status:** Designed, ready to implement

### Phase 3: Context Intelligence (Tier 3) ✅
**Duration:** 2-3 days  
**Deliverable:** JSON metrics cache  
**Tests:** 38 unit tests + 6 integration  
**Status:** Designed, ready to implement

### Phase 4: Specialist Agents ✅
**Duration:** 4-5 days  
**Deliverable:** 10 agents refactored for CORTEX  
**Tests:** 125 unit tests  
**Status:** Designed, ready to implement

### Phase 5: Entry Point & Workflows ✅
**Duration:** 2-3 days  
**Deliverable:** `cortex.md` universal entry  
**Tests:** 45 workflow tests  
**Status:** Designed, ready to implement

### Phase 6: Feature Parity Validation ✅
**Duration:** 1-2 days  
**Deliverable:** 100% KDS feature coverage  
**Tests:** 30 regression tests  
**Status:** Designed, ready to implement

**Total:** 15-23 days (3-5 weeks)

---

## 🎯 Success Metrics

**CORTEX is successful when:**

### User Experience
- ✅ Average response length: <10 lines (vs KDS's 30-50)
- ✅ Code snippets: <20% of responses (vs KDS's 60%+)
- ✅ User feedback: "I got my answer quickly"
- ✅ Time to understand: <30 seconds per response

### Technical Performance
- ✅ Query latency: <100ms (vs KDS's 500-1000ms)
- ✅ Storage size: <270 KB (vs KDS's 380-570 KB)
- ✅ Learning cycle: <2 minutes (vs KDS's 5-10 min)
- ✅ Context refresh: <10 seconds (vs KDS's 2-5 min)

### Quality Assurance
- ✅ Test coverage: 95%+ (vs KDS's ~15%)
- ✅ All 370 tests passing
- ✅ Zero degradation (permanent regression suite)
- ✅ 100% feature parity with KDS

### Intelligence
- ✅ Pattern extraction rate: >80% of events
- ✅ Knowledge reuse rate: >50% of tasks
- ✅ False positive rate: <5%
- ✅ Confidence accuracy: >90%

---

## 📚 Related Documentation

### Design Documents (In `/cortex-design/`)
- **[WHY-CORTEX-IS-BETTER.md](WHY-CORTEX-IS-BETTER.md)** - Comprehensive comparison
- **[MIGRATION-STRATEGY.md](MIGRATION-STRATEGY.md)** - Git workflow & rollback plan
- **[CONVERSATION-LOG.md](CONVERSATION-LOG.md)** - Daily design decisions

### Implementation Plans (In `/cortex-design/phase-plans/`)
- **Phase 0:** Instinct layer specifications
- **Phase 1:** Working memory design
- **Phase 2:** Long-term knowledge architecture
- **Phase 3:** Context intelligence metrics
- **Phase 4:** Agent refactoring plans
- **Phase 5:** Entry point & workflows
- **Phase 6:** Feature parity test matrix

### Test Specifications (In `/cortex-design/test-specifications/`)
- **Unit tests:** Per-tier and per-agent
- **Integration tests:** Cross-tier coordination
- **Regression tests:** KDS feature parity
- **Performance tests:** Query benchmarks

---

## 🔄 Evolution & Maintenance

### This Document Evolves

**Change Protocol:**
1. Design decision made → Log in `CONVERSATION-LOG.md`
2. If fundamental → Update `CORTEX-DNA.md`
3. If implementation detail → Update phase-specific docs
4. All changes tracked in Git history

**Review Schedule:**
- **Weekly:** Quick scan for inconsistencies
- **Monthly:** Full review after major milestones
- **Quarterly:** Comprehensive audit and consolidation

### Long-Term Vision

**CORTEX 1.0** (Current)
- 4-tier architecture
- SQLite cognitive database
- 95%+ test coverage
- 100% KDS feature parity

**CORTEX 2.0** (Future)
- Mind Palace spatial memory extensions
- Advanced metric tracking (see Mind Palace placeholder in `kds.md`)
- Multi-repository learning
- Team collaboration features

---

## 🚀 Getting Started

### For Users
1. Read **[CORTEX Quick Start](../cortex-docs/quick-start.md)** (when created)
2. Use entry point: `#file:CORTEX/cortex-agents/user/cortex.md`
3. Get concise, intelligent responses
4. Benefit from continuous learning

### For Developers
1. Read **[Architecture Overview](../cortex-docs/architecture/overview.md)** (when created)
2. Review tier designs in `/cortex-design/`
3. Check test specifications
4. Follow phase-by-phase implementation plan

### For Contributors
1. Read **[CORTEX-DNA.md](CORTEX-DNA.md)** (this file)
2. Understand core principles
3. Follow concise communication guidelines
4. All PRs must include tests (95%+ coverage)

---

## 📊 Migration Status

**Current State:** KDS v8 preserved on `main` branch  
**Next Step:** Create feature inventory, then begin Phase 0  
**Timeline:** 3-5 weeks to CORTEX v1.0  
**Rollback:** KDS v8 available if migration fails

**See:** [MIGRATION-STRATEGY.md](MIGRATION-STRATEGY.md) for complete Git workflow

---

## ✨ The CORTEX Promise

**We promise:**
- 🎯 **Concise responses** - Get answers fast, not verbose essays
- 🧠 **Intelligent assistance** - Learn from your patterns, predict needs
- ⚡ **Instant performance** - Queries in milliseconds, not seconds
- 🛡️ **Permanent quality** - 370 tests ensure zero degradation
- 📖 **Complete documentation** - Details exist, but not forced on you

**CORTEX DNA = Concise, Intelligent, User-Focused** 🧬

---

**Last Updated:** 2025-11-05  
**Next Review:** After Phase 0 completion  
**Version:** 1.0 (Foundation)