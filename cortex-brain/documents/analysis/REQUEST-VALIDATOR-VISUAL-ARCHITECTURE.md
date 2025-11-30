# Request Validator & Enhancer - Visual Architecture

## 🎯 Overall Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER REQUEST                                │
│                    "Add PDF export feature"                         │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      REQUEST PARSER                                 │
│                  (Existing - No Changes)                            │
│  Extracts: intent, files, context, priority                        │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  ★ NEW: REQUEST VALIDATOR ★                         │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │              THREE PARALLEL ANALYSES                        │  │
│  │                                                             │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐ │  │
│  │  │  Viability   │  │  Historical  │  │  Enhancement    │ │  │
│  │  │   Analyzer   │  │   Analyzer   │  │    Analyzer     │ │  │
│  │  │              │  │              │  │                 │ │  │
│  │  │ Can this     │  │ Have we done │  │ How can we     │ │  │
│  │  │ work?        │  │ this before? │  │ improve it?    │ │  │
│  │  │              │  │              │  │                 │ │  │
│  │  │ ├─Scope     │  │ ├─Patterns   │  │ ├─Completeness │ │  │
│  │  │ ├─Technical │  │ ├─Success    │  │ ├─Best Practic │ │  │
│  │  │ ├─Risks     │  │ ├─Workflows  │  │ ├─Quality      │ │  │
│  │  │ └─DoR       │  │ └─Anti-ptns  │  │ └─UX           │ │  │
│  │  └──────┬───────┘  └──────┬───────┘  └────────┬────────┘ │  │
│  │         │                  │                    │          │  │
│  │         └──────────────────┼────────────────────┘          │  │
│  │                            ▼                                │  │
│  │                   ┌─────────────────┐                      │  │
│  │                   │ SYNTHESIS ENGINE│                      │  │
│  │                   │  Combine Results│                      │  │
│  │                   └────────┬────────┘                      │  │
│  └─────────────────────────────┼──────────────────────────────┘  │
│                                ▼                                  │
│         Decision: APPROVE / CHALLENGE / ENHANCE / ADVISE          │
└──────────────────────────────┬────────────────────────────────────┘
                               │
                               ▼
         ┌─────────────────────┴─────────────────────┐
         │                                            │
         │   Requires User Input?                    │
         │                                            │
         └─────────┬──────────────────────┬───────────┘
                   │                      │
                YES│                      │NO
                   ▼                      │
    ┌──────────────────────────┐         │
    │  VALIDATION PRESENTER    │         │
    │  (Format for User)       │         │
    │                          │         │
    │  ┌────────────────────┐  │         │
    │  │   CHALLENGE        │  │         │
    │  │   - Issues found   │  │         │
    │  │   - Alternatives   │  │         │
    │  │   - Recommendation │  │         │
    │  └────────────────────┘  │         │
    │          OR               │         │
    │  ┌────────────────────┐  │         │
    │  │   ENHANCEMENT      │  │         │
    │  │   - Suggestions    │  │         │
    │  │   - Est. value     │  │         │
    │  │   - Options        │  │         │
    │  └────────────────────┘  │         │
    └───────────┬──────────────┘         │
                │                        │
                ▼                        │
    ┌──────────────────────┐             │
    │   USER DECISION      │             │
    │                      │             │
    │ 1. Accept            │             │
    │ 2. Modify            │             │
    │ 3. Override          │             │
    │ 4. Abort             │             │
    └───────────┬──────────┘             │
                │                        │
                │  (Accept/Modify)       │
                └────────────┬───────────┘
                             │
                             ▼
              ┌──────────────────────────┐
              │  APPLY ENHANCEMENTS      │
              │  (Update request)        │
              └──────────────┬───────────┘
                             │
                             ▼
              ┌──────────────────────────┐
              │  INTENT ROUTER           │
              │  (Existing Flow)         │
              └──────────────┬───────────┘
                             │
                             ▼
              ┌──────────────────────────┐
              │  SPECIALIST AGENTS       │
              │  (Execute Work)          │
              └──────────────────────────┘
```

## 🔍 Data Flow Details

```
┌─────────────────────────────────────────────────────────────┐
│                      DATA SOURCES                           │
│                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────┐ │
│  │ Tier 0   │    │ Tier 1   │    │ Tier 2   │    │Tier 3│ │
│  │  Rules   │    │  Recent  │    │ Pattern  │    │  Dev │ │
│  │          │    │  Context │    │ Library  │    │ Ctxt │ │
│  │ ├─TDD    │    │├─Last 20 │    │├─Success │    │├─File│ │
│  │ ├─DoR    │    ││ Convs   │    ││ History │    ││ Churn│ │
│  │ ├─DoD    │    │├─Recent  │    │├─Similar │    │├─Comm│ │
│  │ └─SOLID  │    ││ Msgs    │    ││ Patterns│    ││ Rate │ │
│  └────┬─────┘    └────┬─────┘    └────┬─────┘    └───┬──┘ │
│       │               │               │              │    │
└───────┼───────────────┼───────────────┼──────────────┼────┘
        │               │               │              │
        │               │               │              │
        └───────────────┴───────────────┴──────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │   VALIDATION COMPONENTS       │
        │                               │
        │  ViabilityAnalyzer            │
        │  - Queries Tier 0 & Tier 3    │
        │  - <100ms                     │
        │                               │
        │  HistoricalAnalyzer           │
        │  - Queries Tier 1 & Tier 2    │
        │  - <150ms (FTS5 search)       │
        │                               │
        │  EnhancementAnalyzer          │
        │  - Queries Tier 0 & Tier 2    │
        │  - <50ms (rule-based)         │
        │                               │
        └───────────────┬───────────────┘
                        │
                        ▼
                 Analysis Results
```

## 🎭 Example Scenarios

### Scenario A: Blocking Challenge

```
User Request: "Skip TDD for this feature"
                    ↓
┌──────────────────────────────────────────────┐
│ VIABILITY ANALYZER                           │
│ ✗ CRITICAL: Tier 0 violation detected       │
│ ✗ Rule #4 (TDD) cannot be skipped           │
│ ✗ Security: No test coverage = risk         │
└──────────────────┬───────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│ HISTORICAL ANALYZER                          │
│ ✓ Data: Test-first = 94% success            │
│ ✓ Data: Test-skip = 67% success (2.3x slow) │
│ ✓ Pattern: Skipping always costs more       │
└──────────────────┬───────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│ SYNTHESIS                                    │
│ Decision: CHALLENGE (BLOCKING)               │
│ Confidence: 98%                              │
│ Message: "This violates Tier 0 rules..."    │
│ Alternative 1: Minimal test-first (15 min)  │
│ Alternative 2: Spike branch                 │
└──────────────────┬───────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│ PRESENTER                                    │
│ ═══════════════════════════════════════════  │
│ ⚠️  REQUEST VALIDATION CHALLENGE             │
│                                              │
│ CRITICAL ISSUE: Tier 0 Rule Violation       │
│ - Proposes skipping TDD (Rule #4)           │
│ - Historical: 2.3x slower, 68% more rework  │
│                                              │
│ SAFE ALTERNATIVES:                           │
│ 1. Minimal test-first ✅ RECOMMENDED         │
│ 2. Spike branch (throwaway)                 │
│                                              │
│ Your choice [1/2/Override]:                 │
│ ═══════════════════════════════════════════  │
└──────────────────────────────────────────────┘
```

### Scenario B: Enhancement Suggestions

```
User Request: "Add share button"
                    ↓
┌──────────────────────────────────────────────┐
│ VIABILITY ANALYZER                           │
│ ✓ Scope: Clear, bounded                     │
│ ✓ Technical: Feasible                       │
│ ✓ DoR: Meets criteria                       │
└──────────────────┬───────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│ HISTORICAL ANALYZER                          │
│ ✓ Similar: "Export button" (2 weeks ago)    │
│ ✓ Success rate: 100%                        │
│ ✓ Avg time: 18 minutes                      │
│ ✓ Workflow: Service→API→UI pattern          │
└──────────────────┬───────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│ ENHANCEMENT ANALYZER                         │
│ ✓ Suggest: Copy link to clipboard           │
│ ✓ Suggest: Element ID for testing           │
│ ✓ Suggest: Accessibility labels              │
│ ✓ Value: 3x quality improvement              │
└──────────────────┬───────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│ SYNTHESIS                                    │
│ Decision: ENHANCE                            │
│ Confidence: 92%                              │
│ Enhancements: 3 suggestions                  │
│ Estimated value: 14 minutes of quality      │
└──────────────────┬───────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│ PRESENTER                                    │
│ ═══════════════════════════════════════════  │
│ 💡 ENHANCEMENT SUGGESTIONS                   │
│                                              │
│ Your request is viable ✅                    │
│                                              │
│ Historical Context:                          │
│ - Similar: "Export button" - Success!       │
│ - Proven workflow available                 │
│                                              │
│ Suggested Enhancements:                      │
│ 1. Copy link (+3 min) ⭐⭐⭐                   │
│ 2. Element ID (+1 min, required) ⭐⭐⭐       │
│ 3. Accessibility (+2 min) ⭐⭐               │
│                                              │
│ Accept all? [Y/Select/Skip]:                │
│ ═══════════════════════════════════════════  │
└──────────────────────────────────────────────┘
```

## 📊 Performance Profile

```
┌─────────────────────────────────────────────────────────┐
│              VALIDATION TIMING                          │
│                                                         │
│  Request Received                                       │
│  ├─ Parser (existing)           [████] 12ms             │
│  │                                                      │
│  ├─ Validator (NEW)              [█████████] 287ms     │
│  │  ├─ Viability Analysis        [███] 89ms            │
│  │  │  └─ Tier 3 queries          45ms                 │
│  │  │  └─ Rule checks              44ms                 │
│  │  │                                                   │
│  │  ├─ Historical Analysis       [████] 143ms          │
│  │  │  └─ Tier 2 FTS5 search      98ms                 │
│  │  │  └─ Pattern matching         45ms                 │
│  │  │                                                   │
│  │  ├─ Enhancement Analysis      [██] 48ms             │
│  │  │  └─ Rule-based checks        48ms                 │
│  │  │                                                   │
│  │  └─ Synthesis                  [█] 7ms              │
│  │                                                      │
│  ├─ User Decision (interactive)   [?] Variable         │
│  │                                                      │
│  └─ Router (existing)             [██] 24ms            │
│                                                         │
│  Total Overhead: 287ms (< 300ms target) ✅             │
│                                                         │
└─────────────────────────────────────────────────────────┘

Efficiency Notes:
- Analyses run in parallel where possible
- Tier queries cached within request
- Fail-fast on critical issues (abort remaining checks)
- <300ms overhead acceptable for value gained
```

## 🔄 Learning Feedback Loop

```
┌─────────────────────────────────────────────────────────┐
│                 VALIDATION LIFECYCLE                    │
│                                                         │
│  ┌───────────┐                                          │
│  │ Validator │                                          │
│  │  Issues   │                                          │
│  │ Challenge │                                          │
│  └─────┬─────┘                                          │
│        │                                                │
│        ▼                                                │
│  ┌───────────┐                                          │
│  │   User    │                                          │
│  │  Decision │                                          │
│  └─────┬─────┘                                          │
│        │                                                │
│        ├──► Accept Alternative → Continue               │
│        ├──► Modify Request → Re-validate                │
│        ├──► Override → Log + Continue                   │
│        └──► Abort → End                                 │
│        │                                                │
│        ▼                                                │
│  ┌───────────┐                                          │
│  │  Tracker  │                                          │
│  │   Logs    │                                          │
│  │ Decision  │                                          │
│  └─────┬─────┘                                          │
│        │                                                │
│        ▼                                                │
│  ┌───────────┐                                          │
│  │  Execute  │                                          │
│  │   Work    │                                          │
│  └─────┬─────┘                                          │
│        │                                                │
│        ▼                                                │
│  ┌───────────┐                                          │
│  │  Outcome  │                                          │
│  │ Success / │                                          │
│  │  Failure  │                                          │
│  └─────┬─────┘                                          │
│        │                                                │
│        ▼                                                │
│  ┌───────────────────┐                                  │
│  │ LEARNING ENGINE   │                                  │
│  │                   │                                  │
│  │ If: Override + Success                               │
│  │ → Reduce false positive rate                         │
│  │                                                      │
│  │ If: Accept + Success                                 │
│  │ → Reinforce pattern                                  │
│  │                                                      │
│  │ If: Override + Failure                               │
│  │ → Strengthen challenge message                       │
│  │                                                      │
│  │ Update: Tier 2 pattern confidence                    │
│  └───────────────────┘                                  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## 🎯 Decision Matrix

```
┌─────────────────────────────────────────────────────────────────┐
│              VALIDATION DECISION LOGIC                          │
│                                                                 │
│  Input: Viability + Historical + Enhancement Results           │
│                                                                 │
│  ┌─────────────────────────────────────────────────────┐       │
│  │ Critical Viability Issues?                          │       │
│  │ (Tier 0 violation, scope too large, etc.)          │       │
│  └──────────────┬──────────────────────────────────────┘       │
│                 │                                              │
│           YES   │   NO                                         │
│       ┌─────────┴─────────┐                                    │
│       ▼                   ▼                                    │
│  ┌─────────┐         ┌─────────────┐                          │
│  │CHALLENGE│         │ High Issues │                          │
│  │(BLOCK)  │         │+ Good Alts? │                          │
│  └─────────┘         └──────┬──────┘                          │
│                             │                                 │
│                       YES   │   NO                            │
│                   ┌─────────┴──────┐                          │
│                   ▼                ▼                          │
│              ┌─────────┐      ┌────────────┐                 │
│              │CHALLENGE│      │Historical  │                 │
│              │(ADVISE) │      │Success?    │                 │
│              └─────────┘      └──────┬─────┘                 │
│                                      │                        │
│                                YES   │   NO                   │
│                            ┌─────────┴──────┐                 │
│                            ▼                ▼                 │
│                       ┌─────────┐      ┌────────┐            │
│                       │ENHANCE  │      │APPROVE │            │
│                       │(SUGGEST)│      │(NO-OP) │            │
│                       └─────────┘      └────────┘            │
│                                                               │
└───────────────────────────────────────────────────────────────┘

Examples:
- Critical Issue → CHALLENGE (BLOCK)
- High Issue + Alternative → CHALLENGE (ADVISE)
- Historical Pattern Found → ENHANCE (SUGGEST)
- No Issues → APPROVE (PROCEED)
```

---

**Created:** 2025-11-07  
**Purpose:** Visual reference for Request Validator & Enhancer architecture  
**Status:** Design documentation  
**Related:** `22-request-validator-enhancer.md`, `REQUEST-VALIDATOR-IMPLEMENTATION-SUMMARY.md`
