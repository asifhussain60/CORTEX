# CORTEX 3.0 - Idea Capture & Planning Integration

**System Name:** Idea Capture System (formerly "Task Dump")  
**Version:** 3.0.0  
**Status:** 🎯 DESIGN APPROVED  
**Timeline:** Post CORTEX 2.1 (6 weeks implementation)  
**Author:** Asif Hussain  
**Date:** November 10, 2025

> **NOTE:** See CORTEX 3.1 EPMO Optimization Plan for health management guidance  
> **Link:** `cortex-brain/cortex-3.0-design/CORTEX-3.1-EPMO-OPTIMIZATION-PLAN.yaml`  
> **Evolution:** `cortex-brain/cortex-3.0-design/CORTEX-3.0-TO-3.1-EVOLUTION.md`

---

## 📋 Executive Summary

**Idea Capture System** is an interrupt-driven, zero-disruption mechanism for capturing fleeting ideas during active CORTEX sessions. Captured ideas automatically enrich and integrate with CORTEX 2.1's Interactive Planning for later refinement and execution.

**Core Innovation:** <5ms capture + async enrichment + seamless planning integration

---

## 🎯 Problem & Solution

### The Problem
```
CORTEX: Refactoring auth.py (line 47)...
YOU: 💡 "Oh! We should add rate limiting!"
PROBLEM: Can't capture without disrupting work
```

### The Solution
```
CORTEX: Refactoring auth.py (line 47)...
YOU: "idea: add rate limiting to login"
CORTEX: ✅ Captured (#a3f9). Continuing...
     → Resumes line 89 (zero disruption!)
```

---

## 🏗️ Architecture Overview

### Core Components

```
┌─────────────────────────────────────┐
│   INTERRUPT DETECTION (<1ms)        │
│   Patterns: "idea:", "task:", etc.  │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│   FAST CAPTURE QUEUE (<5ms)         │
│   SQLite append-only writes         │
│   Context snapshot included         │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│   ASYNC ENRICHMENT (Background)     │
│   • Smart priority detection        │
│   • Component categorization        │
│   • Related idea clustering         │
│   • Cross-repository routing        │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│   RETRIEVAL & PLANNING              │
│   • "show ideas" - view all         │
│   • "work on idea 2" - triggers     │
│   •   CORTEX 2.1 planning           │
└─────────────────────────────────────┘
```

### Why NOT Orchestrator?
- Orchestrator = 50-100ms (too slow for interrupts)
- Idea Capture = <5ms (independent lightweight system)
- **Decision:** Independent SQLite queue system

---

## ✨ Included Enhancements

### 1. Smart Priority Detection (Auto)
**What:** Automatically detect priority from keywords and context

```python
PRIORITY_KEYWORDS = {
    'high': ['urgent', 'critical', 'bug', 'security', 'broken'],
    'medium': ['should', 'improve', 'refactor', 'optimize'],
    'low': ['nice to have', 'consider', 'cleanup']
}

# Examples:
"idea: fix security vulnerability"  → HIGH priority
"idea: refactor auth module"        → MEDIUM priority  
"idea: update docs"                 → LOW priority
```

**Benefit:** No manual prioritization needed

---

### 2. Related Idea Clustering
**What:** Group similar ideas together automatically

```
YOU: "show idea 2"

CORTEX:
  💡 Idea #2: Add rate limiting
  
  Related Ideas:
  • #1: Fix security vulnerability (security cluster)
  • #4: Add JWT tokens (authentication cluster)
  
  Context: Captured during auth.py refactoring
  Pattern: "authentication-security" (seen 5x)
```

**Implementation:**
- Text similarity (TF-IDF)
- Component matching
- Context proximity (same file/session)
- Knowledge graph patterns

**Benefit:** See connections between ideas

---

### 3. CORTEX 2.1 Integration (Synergy)
**What:** Ideas feed directly into Interactive Planning

```
┌─────────────────────────────────────┐
│ CAPTURE: "idea: add websockets"    │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│ ENRICH: Component=backend           │
│         Priority=medium             │
│         Related=#3,#7               │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│ REVIEW: "work on idea 2"            │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│ PLAN (2.1): Interactive Questions   │
│ • "Which protocol?"                 │
│ • "Client or server-side?"          │
│ • "Authentication needed?"          │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│ EXECUTE: Refined implementation     │
└─────────────────────────────────────┘
```

**Synergy Benefits:**
- Context preserved (was working on server.py)
- Priority guides question complexity
- Related ideas referenced in planning
- Learning loop improves both systems

---

### 4. Cross-Repository Support
**What:** Manage ideas across multiple projects

```yaml
# cortex.config.json
{
  "idea_capture": {
    "projects": [
      {
        "name": "CORTEX",
        "path": "D:/PROJECTS/CORTEX",
        "components": ["tier1", "tier2", "agents"]
      },
      {
        "name": "MyApp", 
        "path": "D:/PROJECTS/MyApp",
        "components": ["frontend", "backend", "api"]
      }
    ]
  }
}
```

```
YOU: "idea: add dark mode to frontend"
CORTEX: ✅ Captured (#e8f3) → MyApp project

YOU: "show CORTEX ideas"
CORTEX: 📋 7 ideas for CORTEX project

YOU: "show all ideas"
CORTEX: 
  📋 ALL PROJECTS (15 ideas)
  
  🗂️ CORTEX (7)
  1. [ ] Improve tier 1 performance
  2. [ ] Add voice capture
  ...
  
  🗂️ MyApp (8)
  3. [ ] Add dark mode to frontend
  4. [ ] Optimize API endpoints
  ...
```

**Benefit:** Context-aware routing per project

---

## 🎯 User Experience

### Capture During Work
```
USER: "Refactor authentication module"
CORTEX: 
  ✅ Step 1: Extracting AuthService...
     • Updating auth.py (line 47)...

USER: "idea: add rate limiting to login"

CORTEX: ✅ Captured (#a3f9). Continuing...
     • Updating auth.py (line 89)...
```

### Review Ideas Later
```
USER: "show ideas"

CORTEX:
  💡 IDEA CAPTURE (3 ideas)
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  
  🔴 HIGH PRIORITY (1)
  1. [ ] Fix security vulnerability
     Component: security, authentication
     Context: Refactoring auth.py
     Related: #2 (rate limiting)
  
  🟡 MEDIUM PRIORITY (2)
  2. [ ] Add rate limiting to login
     Component: authentication, api
     Context: Refactoring auth.py  
     Related: #1 (security)
  
  3. [ ] Update authentication docs
     Component: documentation
  
  Commands:
  • "work on idea 2" - Start planning
  • "complete idea 3" - Mark done
  • "show auth ideas" - Filter
```

### Planning Integration
```
USER: "work on idea 2"

CORTEX: 💡 Add rate limiting to login
  
  Let me ask a few questions:
  
  1️⃣ What rate limit?
     • 10 req/min (strict)
     • 30 req/min (moderate)
     • 100 req/min (lenient)
  
USER: "30"

CORTEX: 2️⃣ Per IP or per user?
USER: "per user"

CORTEX: 3️⃣ Exceeded limit action?
USER: "return 429"

CORTEX:
  ✅ Refined plan ready:
  [8-step implementation]
  
  Proceed? (yes/no)
```

---

## 📊 Performance Targets

| Operation | Target | Why |
|-----------|--------|-----|
| Interrupt Detection | <1ms | Pattern regex |
| Context Snapshot | <1ms | Already in memory |
| Queue Write | <5ms | SQLite append-only |
| **Total Interrupt** | **<10ms** | **User doesn't notice** |
| Enrichment | Async | No blocking |
| Retrieval | <50ms | Fast queries |

---

## 🧪 Key Test Scenarios

```python
# Test 1: Zero disruption
def test_capture_during_active_work():
    """Verify work continues after capture."""
    entry = CortexEntry(...)
    future = entry.process_async("refactor auth")
    
    result = entry.process("idea: add rate limiting")
    assert result['action'] == 'idea_captured'
    
    # Original work completes
    assert future.result()['success'] is True

# Test 2: Performance
def test_capture_performance():
    """Verify <5ms capture."""
    start = time.perf_counter()
    idea_id = queue.capture("test idea", context)
    duration_ms = (time.perf_counter() - start) * 1000
    
    assert duration_ms < 5.0

# Test 3: 2.1 Integration
def test_idea_to_planning():
    """Verify planning integration."""
    idea_id = queue.capture("add websockets", context)
    
    planner = InteractivePlannerAgent(tier1, tier2)
    questions = planner.generate_questions(
        idea_id=idea_id
    )
    
    assert len(questions) > 0
```

---

## 🚀 Implementation Plan

### Phase 3.1: Core Capture (2 weeks)
- Fast capture queue (<5ms)
- Interrupt detection (patterns)
- Context snapshot API
- Background enrichment worker
- Unit tests + performance benchmarks

### Phase 3.2: Enrichment Features (1 week)
- Smart priority detection
- Component categorization
- Related idea clustering
- Cross-repository routing

### Phase 3.3: CORTEX 2.1 Integration (1 week)
- Idea → Planning workflow
- Context passing to planner
- Plan linking
- Learning loop (patterns → KG)

### Phase 3.4: Polish & Testing (2 weeks)
- UI/UX refinement
- Comprehensive integration tests
- Documentation
- Beta testing

**Total:** 6 weeks

---

## 📚 Technical Reference

### Data Schema
```python
@dataclass
class IdeaCapture:
    idea_id: str                    # UUID
    raw_text: str                   # User's words
    timestamp: datetime
    
    # Context (instant capture)
    active_file: Optional[str]
    active_line: Optional[int]
    active_operation: Optional[str]
    conversation_id: str
    project: str                    # NEW: Cross-repo
    
    # Enrichment (async)
    component: Optional[str] = None
    priority: Optional[str] = None  # NEW: Smart detection
    related_ideas: List[str] = None # NEW: Clustering
    status: str = "pending"
```

### API Surface
```python
# Capture
idea_id = queue.capture(raw_text, context)

# Retrieval
ideas = queue.get_all_ideas()
auth_ideas = queue.filter_by_component('auth')
cortex_ideas = queue.filter_by_project('CORTEX')

# Management
queue.complete_idea(idea_id)
queue.update_priority(idea_id, 'high')

# 2.1 Integration
planner.plan_from_idea(idea_id)
```

---

## 🎯 Success Metrics

| Metric | Target |
|--------|--------|
| Capture Speed | <5ms |
| Zero Disruption | 100% (work continues) |
| Context Accuracy | >95% |
| Priority Detection | >85% accuracy |
| Component Detection | >90% accuracy |
| Clustering Quality | >80% relevant |
| User Adoption | >70% after 1 month |
| Completion Rate | >60% of captured ideas |

---

## 🔗 Integration Points

### With CORTEX 2.0
- Uses Tier 1 SQLite infrastructure
- Integrates with entry point interrupt detection
- Shares context snapshot system

### With CORTEX 2.1
- Ideas feed Interactive Planning
- Planning enriches idea details
- Completed plans link back to ideas
- Learning loop updates Knowledge Graph

### Future (Beyond 3.0)
- Voice capture: "Hey CORTEX, idea: add dark mode"
- AI breakdown: Auto-split big ideas into subtasks
- Proactive suggestions: CORTEX suggests related ideas
- Team sharing: Export/import (JIRA format)

---

## 📖 User Commands Reference

```bash
# Capture (during work)
idea: add rate limiting
task: refactor module
remember: fix bug
todo: update docs

# Review
show ideas              # All ideas
show ideas for auth    # Filter by component
show high priority     # Filter by priority
show idea 5            # Specific details
show CORTEX ideas      # Filter by project

# Manage
work on idea 5         # Trigger planning
complete idea 3        # Mark done
delete idea 7          # Remove
prioritize idea 2 high # Update priority

# Advanced
show related ideas 5   # Clustering
```

---

## 🎓 Learning Opportunities

The system learns patterns:

1. **Component Patterns:** "Add X to login" → auth component
2. **Priority Patterns:** Security keywords → high priority
3. **Cluster Patterns:** Auth ideas often batch together
4. **Template Recognition:** "Refactor X" → standard steps

Patterns stored in Tier 2 Knowledge Graph for continuous improvement.

---

## 📝 Documentation Files

```
cortex-brain/cortex-3.0-design/
├── IDEA-CAPTURE-SYSTEM.md (this file - compact reference)
└── TASK-DUMP-SYSTEM-DESIGN.md (full 28-page design)

docs/features/
└── idea-capture-user-guide.md (to be created)

src/tier1/
├── idea_queue.py (to be created)
└── idea_enrichment.py (to be created)
```

---

## ✅ Definition of Done

1. ✅ <5ms capture performance
2. ✅ Zero disruption (work continues)
3. ✅ Context accuracy >95%
4. ✅ Smart priority detection >85%
5. ✅ Related clustering >80%
6. ✅ Cross-repository routing works
7. ✅ 2.1 planning integration complete
8. ✅ All tests passing (unit + integration + performance)
9. ✅ Documentation complete
10. ✅ User adoption >70% after 1 month

---

## 🎯 Quick Summary

**Name:** Idea Capture System  
**Purpose:** Zero-disruption idea capture + planning integration  
**Performance:** <5ms interrupt, async enrichment  
**Enhancements:** Smart priority, clustering, 2.1 synergy, cross-repo  
**Timeline:** 6 weeks post-2.1  
**Status:** Design approved ✅

**Key Innovation:** Capture fast, refine later via Interactive Planning

---

*Design by: Asif Hussain*  
*Date: November 10, 2025*  
*Version: 3.0.0 (Approved)*  
*Reference: Full design in TASK-DUMP-SYSTEM-DESIGN.md*
