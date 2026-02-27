# STS (Sharpen The Saw) — Before/After Architecture
# Live demonstration of CORTEX's refactoring capabilities

```
 ═══════════════════════════════════════════════════════════════════════════════
  SHARPEN THE SAW — BEFORE vs AFTER
 ═══════════════════════════════════════════════════════════════════════════════

  cortex-sts/CortexLabs/

  ┌─────────────────────────────────────┐     ┌─────────────────────────────────────┐
  │         BadMonolith (BEFORE)        │     │          Refactored (AFTER)          │
  │                                     │     │                                     │
  │  ✗ God classes (500+ lines)         │     │  ✓ SRP-compliant classes (<200 LOC) │
  │  ✗ No tests at all                  │     │  ✓ TDD coverage (CORE-008)          │
  │  ✗ Hardcoded credentials            │     │  ✓ Secrets in environment vars      │
  │  ✗ Circular imports                 │     │  ✓ Clean dependency graph           │
  │  ✗ Mixed naming conventions         │     │  ✓ snake_case everywhere (CORE-028) │
  │  ✗ No type hints                    │     │  ✓ Full type annotations (CORE-011) │
  │  ✗ No docstrings                    │     │  ✓ Docstrings on all public APIs    │
  │  ✗ Duplicated logic                 │     │  ✓ Single canonical (CORE-035)      │
  │                                     │     │                                     │
  │  backend/                           │     │  backend/                           │
  │  └── (over-engineered monolith)     │     │  └── (clean architecture)           │
  │  frontend/                          │     │  frontend/                          │
  │  └── (tightly coupled UI)           │     │  └── (component-based, tested)      │
  └─────────────────────────────────────┘     └─────────────────────────────────────┘
           │                                            ▲
           │                                            │
           └────────────── CORTEX PIPELINE ─────────────┘


 ═══════════════════════════════════════════════════════════════════════════════
  THE TRANSFORMATION PIPELINE
 ═══════════════════════════════════════════════════════════════════════════════

  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
  │   LENS   │───▶│CHALLENGE │───▶│   TDD    │───▶│  SWEEP   │───▶│GOVERNANCE│
  │ ANALYSIS │    │   GATE   │    │  CYCLE   │    │COMPLETE  │    │  GATE    │
  │          │    │(CORE-048)│    │(CORE-008)│    │(CORE-064)│    │(38 rules)│
  └──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
       │               │               │               │               │
  Detect all      Present          Write tests     Fix every       Validate
  anti-patterns   alternatives     before each     instance       all rules
  with scores     with ROI         fix             across repo    pass


 ═══════════════════════════════════════════════════════════════════════════════
  STS USAGE — Three Demo Scenarios
 ═══════════════════════════════════════════════════════════════════════════════

  Scenario 1: Team Onboarding
  ┌──────────────────────────────────────────────────────────┐
  │  /onboard cortex-sts/CortexLabs/BadMonolith             │
  │                                                          │
  │  → LENS analysis with confidence scores                  │
  │  → Security assessment (P0/P1/P2)                        │
  │  → SQLite dashboard with anti-pattern map                │
  └──────────────────────────────────────────────────────────┘

  Scenario 2: Before/After Digest
  ┌──────────────────────────────────────────────────────────┐
  │  /digest cortex-sts/CortexLabs/BadMonolith              │
  │  /digest cortex-sts/CortexLabs/Refactored               │
  │                                                          │
  │  → Side-by-side quality metrics comparison               │
  │  → Pattern detection (before: 0 patterns → after: 5+)   │
  └──────────────────────────────────────────────────────────┘

  Scenario 3: Live Refactoring
  ┌──────────────────────────────────────────────────────────┐
  │  /audit fix (on BadMonolith)                             │
  │                                                          │
  │  → 9-stage pipeline runs against bad code                │
  │  → Watch real-time fix convergence loop                  │
  │  → Compare output with Refactored/ golden state          │
  └──────────────────────────────────────────────────────────┘


 ═══════════════════════════════════════════════════════════════════════════════
  PLAYBOOK REFERENCE
 ═══════════════════════════════════════════════════════════════════════════════

  ┌────────────────────────────────────────────────────────────────────┐
  │  PB-STS-001                                                       │
  │  cortex-registry/playbooks/sharpen-the-saw/                       │
  │    pb-sts-001-badmonolith-refactoring.yaml  ← full playbook      │
  │    mcp-compatibility-gaps.yaml              ← MCP gap analysis   │
  └────────────────────────────────────────────────────────────────────┘

  Note: STS repos are intentionally exempt from CORE-008, CORE-011, CORE-028
  They exist to showcase what CORTEX fixes, not to be production-ready
```

**Source:** `cortex-sts/` · `cortex-registry/playbooks/sharpen-the-saw/`
